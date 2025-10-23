import base64
import shutil
import tempfile
from pathlib import Path
from typing import Optional

import requests
import torch
from accelerate.utils import set_seed
from diffusers import AutoencoderKL, DDIMScheduler
from huggingface_hub import hf_hub_download
from omegaconf import OmegaConf
from pydantic import BaseModel

from latentsync.models.unet import UNet3DConditionModel
from latentsync.pipelines.lipsync_pipeline import LipsyncPipeline
from latentsync.whisper.audio2feature import Audio2Feature

CONFIG_PATH = Path("configs/unet/stage2_512.yaml")
CHECKPOINT_PATH = Path("checkpoints/latentsync_unet.pt")
WHISPER_PATH = Path("checkpoints/whisper/tiny.pt")
TORCH_HUB_CACHE = Path.home() / ".cache" / "torch" / "hub" / "checkpoints" / "vgg16-397923af.pth"

PIPELINE: Optional[LipsyncPipeline] = None
CONFIG: Optional[OmegaConf] = None

def _copy_from_cache(cache_path: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(cache_path, destination)


def _ensure_checkpoint(target_path: Path, repo_id: str, filename: str) -> None:
    if target_path.exists():
        return
    downloaded_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=target_path.parent.as_posix(),
        local_dir_use_symlinks=False,
    )
    # hf_hub_download already writes to local_dir when provided, but returns the resolved path.
    # Ensure the final file lives exactly at target_path.
    if Path(downloaded_path) != target_path:
        _copy_from_cache(downloaded_path, target_path)


def _ensure_torch_hub_weights() -> None:
    if TORCH_HUB_CACHE.exists():
        return
    TORCH_HUB_CACHE.parent.mkdir(parents=True, exist_ok=True)
    downloaded_path = hf_hub_download(
        repo_id="pytorch/vision",
        filename="vgg16-397923af.pth",
    )
    _copy_from_cache(downloaded_path, TORCH_HUB_CACHE)


def download_weights() -> None:
    """Download model weights required for inference."""
    _ensure_checkpoint(CHECKPOINT_PATH, "ByteDance/LatentSync-1.6", "latentsync_unet.pt")
    _ensure_checkpoint(WHISPER_PATH, "ByteDance/LatentSync-1.6", "whisper/tiny.pt")
    _ensure_torch_hub_weights()


def download_file(url: str, directory: Path) -> Path:
    """Download file from URL to the specified directory."""
    directory.mkdir(parents=True, exist_ok=True)
    local_path = directory / Path(url).name

    response = requests.get(url, stream=True, timeout=600)
    response.raise_for_status()

    with local_path.open("wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return local_path


def decode_base64_to_file(base64_str: str, directory: Path, extension: str) -> Path:
    output_path = directory / f"input{extension}"
    output_path.write_bytes(base64.b64decode(base64_str))
    return output_path


def encode_file_to_base64(file_path: Path) -> str:
    return base64.b64encode(file_path.read_bytes()).decode("utf-8")


class Item(BaseModel):
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    video_base64: Optional[str] = None
    audio_base64: Optional[str] = None
    guidance_scale: float = 1.5
    inference_steps: int = 20
    seed: int = 1247


def setup() -> None:
    global PIPELINE, CONFIG

    if PIPELINE is not None:
        return

    if not torch.cuda.is_available():
        raise RuntimeError("LatentSync deployment requires a CUDA-enabled GPU.")

    download_weights()

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Configuration file not found: {CONFIG_PATH}")
    if not CHECKPOINT_PATH.exists():
        raise FileNotFoundError(
            "Model checkpoint not found. Please verify download permissions for ByteDance/LatentSync-1.6."
        )

    CONFIG = OmegaConf.load(CONFIG_PATH)

    is_fp16_supported = torch.cuda.get_device_capability()[0] > 7
    weight_dtype = torch.float16 if is_fp16_supported else torch.float32

    scheduler = DDIMScheduler.from_pretrained("configs")

    cross_attention_dim = CONFIG.model.cross_attention_dim
    if cross_attention_dim == 768:
        whisper_path = CHECKPOINT_PATH.parent / "whisper" / "small.pt"
    elif cross_attention_dim == 384:
        whisper_path = WHISPER_PATH
    else:
        raise NotImplementedError("cross_attention_dim must be either 768 or 384")

    audio_encoder = Audio2Feature(
        model_path=whisper_path.as_posix(),
        device="cuda",
        num_frames=CONFIG.data.num_frames,
        audio_feat_length=CONFIG.data.audio_feat_length,
    )

    vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse", torch_dtype=weight_dtype)
    vae.config.scaling_factor = 0.18215
    vae.config.shift_factor = 0

    unet, _ = UNet3DConditionModel.from_pretrained(
        OmegaConf.to_container(CONFIG.model),
        CHECKPOINT_PATH.resolve().as_posix(),
        device="cpu",
    )
    unet = unet.to(dtype=weight_dtype)

    pipeline = LipsyncPipeline(
        vae=vae,
        audio_encoder=audio_encoder,
        unet=unet,
        scheduler=scheduler,
    )
    PIPELINE = pipeline.to("cuda")


def _resolve_input(
    *,
    url: Optional[str],
    encoded: Optional[str],
    temp_dir: Path,
    extension: str,
    description: str,
) -> Path:
    if url:
        return download_file(url, temp_dir)
    if encoded:
        return decode_base64_to_file(encoded, temp_dir, extension)
    raise ValueError(f"{description} must be provided via URL or base64 upload.")


def predict(item: Item, context) -> dict:
    setup()

    assert PIPELINE is not None and CONFIG is not None  # for type-checkers

    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        video_path = _resolve_input(
            url=item.video_url,
            encoded=item.video_base64,
            temp_dir=temp_dir,
            extension=".mp4",
            description="Video input",
        )
        audio_path = _resolve_input(
            url=item.audio_url,
            encoded=item.audio_base64,
            temp_dir=temp_dir,
            extension=".wav",
            description="Audio input",
        )

        if item.seed != -1:
            set_seed(item.seed)
        else:
            torch.seed()

        dtype = next(PIPELINE.unet.parameters()).dtype
        output_path = temp_dir / "output" / "output.mp4"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        CONFIG.run.update(
            {
                "guidance_scale": item.guidance_scale,
                "inference_steps": item.inference_steps,
            }
        )

        PIPELINE(
            video_path=video_path.as_posix(),
            audio_path=audio_path.as_posix(),
            video_out_path=output_path.as_posix(),
            num_frames=CONFIG.data.num_frames,
            num_inference_steps=item.inference_steps,
            guidance_scale=item.guidance_scale,
            weight_dtype=dtype,
            width=CONFIG.data.resolution,
            height=CONFIG.data.resolution,
            mask_image_path=CONFIG.data.mask_image_path,
            temp_dir=temp_dir.as_posix(),
        )

        return {
            "video_base64": encode_file_to_base64(output_path),
            "details": {
                "guidance_scale": item.guidance_scale,
                "inference_steps": item.inference_steps,
                "seed": item.seed,
            },
        }
