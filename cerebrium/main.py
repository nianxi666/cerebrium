import base64
import os
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Optional

import requests
import torch
from diffusers import UniPCMultistepScheduler, DiffusionPipeline
from diffusers.utils import export_to_video, load_image
from pydantic import BaseModel, Field, field_validator

DEFAULT_MODEL_ID = os.getenv("WAN_MODEL_ID", "Wan-AI/Wan2.2-TI2V-5B-Diffusers")
DEFAULT_PROMPT = (
    "Two anthropomorphic cats in comfy boxing gear and bright gloves fight intensely on a spotlighted stage."
)
DEFAULT_NEGATIVE_PROMPT = (
    "low quality, worst quality, jpeg artifacts, static frame, blurry, deformed hands, distorted face"
)
WAN_ENABLE_CPU_OFFLOAD = os.getenv("WAN_ENABLE_CPU_OFFLOAD", "false").lower() in {"1", "true", "yes"}

PIPELINE: Optional[DiffusionPipeline] = None
CURRENT_MODEL_ID: Optional[str] = None
CURRENT_OFFLOAD_STATE: Optional[bool] = None
PIPELINE_DEVICE: Optional[torch.device] = None


class WanRequest(BaseModel):
    prompt: str = Field(default=DEFAULT_PROMPT, description="Text prompt used for generation.")
    negative_prompt: Optional[str] = Field(
        default=DEFAULT_NEGATIVE_PROMPT,
        description="Negative prompt that suppresses unwanted artifacts.",
    )
    height: int = Field(default=704, description="Output video height in pixels.")
    width: int = Field(default=1280, description="Output video width in pixels.")
    num_frames: int = Field(default=121, description="Number of frames to generate (must be 4n+1).")
    num_inference_steps: int = Field(default=50, description="Sampler diffusion steps.")
    guidance_scale: float = Field(default=5.0, description="Classifier-free guidance scale.")
    fps: int = Field(default=24, description="Frames per second for the exported video.")
    seed: Optional[int] = Field(default=None, description="Seed for reproducible results.")
    image_url: Optional[str] = Field(default=None, description="Optional reference image URL for TI2V.")
    image_base64: Optional[str] = Field(default=None, description="Optional base64 reference image for TI2V.")
    model_id: str = Field(default=DEFAULT_MODEL_ID, description="Hugging Face model identifier.")
    use_cpu_offload: Optional[bool] = Field(
        default=None,
        description="Enable Accelerate CPU offload to reduce GPU VRAM usage.",
    )

    @field_validator("height", "width", "fps")
    @classmethod
    def _positive_values(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("height/width/fps must be positive integers.")
        return value

    @field_validator("num_frames")
    @classmethod
    def _validate_num_frames(cls, value: int) -> int:
        if value <= 0 or (value - 1) % 4 != 0:
            raise ValueError("num_frames must be positive and satisfy num_frames = 4n + 1.")
        return value


def _load_image_from_inputs(item: WanRequest) -> Optional["Image.Image"]:
    if item.image_url:
        response = requests.get(item.image_url, timeout=600)
        response.raise_for_status()
        return load_image(BytesIO(response.content))
    if item.image_base64:
        return load_image(BytesIO(base64.b64decode(item.image_base64)))
    return None


def _encode_file_to_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def _resolve_dtype() -> torch.dtype:
    if not torch.cuda.is_available():
        raise RuntimeError("Wan deployment requires access to a CUDA-enabled GPU.")
    major, _ = torch.cuda.get_device_capability()
    return torch.bfloat16 if major >= 8 else torch.float16


def setup(model_id: str, use_cpu_offload: bool) -> None:
    global PIPELINE, CURRENT_MODEL_ID, CURRENT_OFFLOAD_STATE, PIPELINE_DEVICE

    if (
        PIPELINE is not None
        and CURRENT_MODEL_ID == model_id
        and CURRENT_OFFLOAD_STATE == use_cpu_offload
    ):
        return

    dtype = _resolve_dtype()

    pipeline = DiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
    )
    pipeline.scheduler = UniPCMultistepScheduler.from_config(pipeline.scheduler.config)
    pipeline.enable_attention_slicing()
    pipeline.enable_vae_slicing()

    if use_cpu_offload:
        pipeline.enable_model_cpu_offload()
        PIPELINE_DEVICE = torch.device("cuda")
    else:
        pipeline.to("cuda")
        PIPELINE_DEVICE = torch.device("cuda")

    PIPELINE = pipeline
    CURRENT_MODEL_ID = model_id
    CURRENT_OFFLOAD_STATE = use_cpu_offload


def predict(
    prompt: str = DEFAULT_PROMPT,
    negative_prompt: Optional[str] = DEFAULT_NEGATIVE_PROMPT,
    height: int = 704,
    width: int = 1280,
    num_frames: int = 121,
    num_inference_steps: int = 50,
    guidance_scale: float = 5.0,
    fps: int = 24,
    seed: Optional[int] = None,
    image_url: Optional[str] = None,
    image_base64: Optional[str] = None,
    model_id: str = DEFAULT_MODEL_ID,
    use_cpu_offload: Optional[bool] = None,
) -> dict:
    item = WanRequest(
        prompt=prompt,
        negative_prompt=negative_prompt,
        height=height,
        width=width,
        num_frames=num_frames,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        fps=fps,
        seed=seed,
        image_url=image_url,
        image_base64=image_base64,
        model_id=model_id,
        use_cpu_offload=use_cpu_offload,
    )

    offload = item.use_cpu_offload if item.use_cpu_offload is not None else WAN_ENABLE_CPU_OFFLOAD
    setup(item.model_id, offload)

    assert PIPELINE is not None and PIPELINE_DEVICE is not None

    generator: Optional[torch.Generator] = None
    if item.seed is not None:
        generator = torch.Generator(device=PIPELINE_DEVICE).manual_seed(item.seed)

    pil_image = _load_image_from_inputs(item)

    pipe_inputs = dict(
        prompt=item.prompt,
        negative_prompt=item.negative_prompt,
        height=item.height,
        width=item.width,
        num_frames=item.num_frames,
        num_inference_steps=item.num_inference_steps,
        guidance_scale=item.guidance_scale,
        generator=generator,
    )
    if pil_image is not None:
        pipe_inputs["image"] = pil_image

    output = PIPELINE(**pipe_inputs)
    frames = output.frames[0]

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "wan-output.mp4"
        export_to_video(frames, temp_path.as_posix(), fps=item.fps)
        video_base64 = _encode_file_to_base64(temp_path)

    return {
        "video_base64": video_base64,
        "details": {
            "prompt": item.prompt,
            "negative_prompt": item.negative_prompt,
            "height": item.height,
            "width": item.width,
            "num_frames": item.num_frames,
            "num_inference_steps": item.num_inference_steps,
            "guidance_scale": item.guidance_scale,
            "fps": item.fps,
            "seed": item.seed,
            "model_id": item.model_id,
            "cpu_offload": offload,
            "has_image_conditioning": pil_image is not None,
        },
    }
