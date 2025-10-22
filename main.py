import base64
import logging
import os
import secrets
from io import BytesIO
from typing import Optional

import torch
from diffusers import AutoPipelineForText2Image
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

logger = logging.getLogger("qwen_image_service")
logging.basicConfig(level=logging.INFO)

MODEL_ID = os.getenv("QWEN_IMAGE_MODEL_ID", "Qwen/Qwen2-Image")
MIN_RESOLUTION = int(os.getenv("QWEN_MIN_RESOLUTION", "512"))
MAX_RESOLUTION = int(os.getenv("QWEN_MAX_RESOLUTION", "1024"))
DEFAULT_INFERENCE_STEPS = int(os.getenv("QWEN_DEFAULT_STEPS", "30"))
DEFAULT_GUIDANCE_SCALE = float(os.getenv("QWEN_DEFAULT_GUIDANCE", "5.0"))
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN:
    os.environ.setdefault("HUGGINGFACE_HUB_TOKEN", HF_TOKEN)

app = FastAPI(title="Qwen Image Generation Service", version="1.0.0")

_pipeline: Optional[AutoPipelineForText2Image] = None
device: Optional[torch.device] = None
dtype: Optional[torch.dtype] = None


class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt to guide image generation", min_length=1)
    negative_prompt: Optional[str] = Field(
        None, description="Optional text prompt for attributes to avoid during generation"
    )
    seed: Optional[int] = Field(
        None,
        description="Random seed for reproducible outputs. Leave blank for randomness.",
        ge=0,
        le=2**32 - 1,
    )
    num_inference_steps: int = Field(
        DEFAULT_INFERENCE_STEPS,
        ge=5,
        le=75,
        description="Number of denoising steps. Higher values are slower but can yield more detailed images.",
    )
    guidance_scale: float = Field(
        DEFAULT_GUIDANCE_SCALE,
        ge=0.0,
        le=20.0,
        description="Classifier-free guidance scale. Higher values adhere more closely to the prompt.",
    )
    width: int = Field(
        MAX_RESOLUTION,
        ge=MIN_RESOLUTION,
        le=MAX_RESOLUTION,
        description="Width of the generated image. Must be divisible by 8.",
    )
    height: int = Field(
        MAX_RESOLUTION,
        ge=MIN_RESOLUTION,
        le=MAX_RESOLUTION,
        description="Height of the generated image. Must be divisible by 8.",
    )


class GenerateResponse(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded PNG image")
    seed: int = Field(..., description="Seed used for generation")
    model_id: str = Field(..., description="Model identifier used for inference")
    width: int = Field(..., description="Width of the generated image")
    height: int = Field(..., description="Height of the generated image")
    guidance_scale: float = Field(..., description="Guidance scale used for inference")
    num_inference_steps: int = Field(..., description="Number of inference steps used")


@app.on_event("startup")
def load_pipeline() -> None:
    """Load the Qwen image generation pipeline when the API starts."""
    global _pipeline, device, dtype

    if _pipeline is not None:
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.float16 if device.type == "cuda" else torch.float32

    logger.info("Loading Qwen image pipeline '%s' on %s", MODEL_ID, device)

    load_kwargs = {"torch_dtype": dtype}

    try:
        pipeline = AutoPipelineForText2Image.from_pretrained(MODEL_ID, **load_kwargs)
    except Exception as exc:  # pragma: no cover - startup failure should be surfaced clearly
        logger.exception("Failed to load pipeline for model '%s'", MODEL_ID)
        raise RuntimeError(f"Failed to load model {MODEL_ID}: {exc}") from exc

    pipeline.to(device)
    pipeline.set_progress_bar_config(disable=True)

    # Disable the safety checker if present to reduce overhead. Users should apply their own filters.
    if getattr(pipeline, "safety_checker", None) is not None:
        pipeline.safety_checker = None

    if device.type != "cuda" and hasattr(pipeline, "enable_attention_slicing"):
        pipeline.enable_attention_slicing()

    _pipeline = pipeline
    logger.info("Pipeline loaded successfully")


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint for Cerebrium runtime."""
    status = "ready" if _pipeline is not None else "loading"
    return {"status": status, "model_id": MODEL_ID}


def _validate_dimensions(width: int, height: int) -> None:
    if width % 8 != 0 or height % 8 != 0:
        raise HTTPException(status_code=422, detail="Width and height must be divisible by 8.")
    if width > MAX_RESOLUTION or height > MAX_RESOLUTION:
        raise HTTPException(
            status_code=422,
            detail=f"Width and height must be <= {MAX_RESOLUTION}.",
        )
    if width < MIN_RESOLUTION or height < MIN_RESOLUTION:
        raise HTTPException(
            status_code=422,
            detail=f"Width and height must be >= {MIN_RESOLUTION}.",
        )


def _generate_image(request: GenerateRequest, seed: int) -> str:
    assert _pipeline is not None, "Pipeline must be loaded before generating images"
    assert device is not None, "Device must be initialised before generating images"
    generator = torch.Generator(device=device)
    generator.manual_seed(seed)

    output = _pipeline(
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        guidance_scale=request.guidance_scale,
        num_inference_steps=request.num_inference_steps,
        width=request.width,
        height=request.height,
        generator=generator,
    )

    image = output.images[0]
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    """Generate an image using the Qwen image diffusion model."""
    if _pipeline is None:
        raise HTTPException(status_code=503, detail="Model is still loading. Please retry shortly.")

    _validate_dimensions(request.width, request.height)

    seed = request.seed or secrets.randbelow(2**32)

    try:
        image_base64 = await run_in_threadpool(_generate_image, request, seed)
    except Exception as exc:  # pragma: no cover - runtime errors reported to caller
        logger.exception("Image generation failed")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {exc}") from exc

    return GenerateResponse(
        image_base64=image_base64,
        seed=seed,
        model_id=MODEL_ID,
        width=request.width,
        height=request.height,
        guidance_scale=request.guidance_scale,
        num_inference_steps=request.num_inference_steps,
    )
