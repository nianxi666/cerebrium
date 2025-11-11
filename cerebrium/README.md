# Wan2.2 TI2V Cerebrium Deployment

This project packages the [Wan 2.2 Text-Image-to-Video 5B](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B-Diffusers) diffusers pipeline so it can be deployed directly to [Cerebrium](https://www.cerebrium.ai/). Once deployed, the endpoint generates up to 5 seconds of 720p (1280×704) video at 24 FPS from either a pure text prompt or a text prompt plus an optional reference image.

## Hardware & Runtime

- **GPU**: `AMPERE_A10` (24 GB) or higher. Set `WAN_ENABLE_CPU_OFFLOAD=true` if you need additional VRAM headroom.
- **Python**: 3.11
- **Key dependencies**: PyTorch 2.2, Diffusers 0.32, Transformers 4.44, Accelerate 0.34.

## Deploying to Cerebrium

1. Export your Cerebrium credentials (service token preferred):
   ```bash
   export CEREBRIUM_SERVICE_ACCOUNT_TOKEN="<your-service-key>"
   ```
   Or use `CEREBRIUM_API_KEY` if you rely on a user token instead of a service account.
2. (Optional) Control VRAM usage:
   ```bash
   # Enable Accelerate CPU offload before running the service (lower VRAM, slower runtime)
   export WAN_ENABLE_CPU_OFFLOAD=true
   ```
3. Deploy:
   ```bash
   cd cerebrium
   ./deploy.sh
   ```

The deployment metadata (name, hardware, dependencies) lives in `cerebrium.toml`.

## Prediction API

The `predict` function in `main.py` exposes the following parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | example cinematic boxing prompt | Primary generation prompt. |
| `negative_prompt` | `str` | discourages low-quality artifacts | Optional negative guidance. |
| `height` / `width` | `int` | `704` / `1280` | Output resolution. Keep the product close to 720p for best results. |
| `num_frames` | `int` | `121` | Must follow `4n+1`. `121` → 5.0 s @ 24 FPS. |
| `num_inference_steps` | `int` | `50` | Diffusion steps (higher = better + slower). |
| `guidance_scale` | `float` | `5.0` | CFG scale. |
| `fps` | `int` | `24` | Playback framerate for the returned MP4. |
| `seed` | `int`/`null` | `null` | Reproducible run when set. |
| `image_url` / `image_base64` | `str` | `null` | Optional reference image for TI2V. Omit for pure T2V. |
| `model_id` | `str` | `Wan-AI/Wan2.2-TI2V-5B-Diffusers` | Alternate HF repo if needed. |
| `use_cpu_offload` | `bool`/`null` | `null` | Override `WAN_ENABLE_CPU_OFFLOAD` per-request. |

### Example Request

```bash
curl -X POST "$CEREBRIUM_ENDPOINT" \
  -H "Authorization: Bearer $CEREBRIUM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Two anthropomorphic cats in comfy boxing gear and bright gloves fight intensely on a spotlighted stage.",
    "negative_prompt": "saturated, overexposed, static frame, low quality",
    "height": 704,
    "width": 1280,
    "num_frames": 121,
    "num_inference_steps": 50,
    "guidance_scale": 5.0,
    "fps": 24,
    "seed": 2025
  }'
```

The response payload contains a base64-encoded MP4 plus the metadata echoed in the `details` key.

## Local Smoke Test

Ensure your machine has a CUDA GPU with ≥24 GB VRAM, install the requirements, and run an interactive Python session:

```bash
python -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python - <<'PY'
from main import predict
result = predict(num_inference_steps=30, num_frames=81, seed=1234)
print(result.keys(), result['details'])
PY
```

This downloads the model weights into your default Hugging Face cache (or `/persistent-storage` when running inside Cerebrium) and verifies that the pipeline can execute end-to-end.

## Tips

- Keep `num_frames` within `4n+1` (e.g., 65, 81, 97, 121) to match Wan's temporal lattice.
- Use `image_url` for character-consistent TI2V shots; omit it for pure text-to-video.
- Increase `guidance_scale` to tighten adherence to the prompt; reduce it if motion becomes unstable.
- If you hit CUDA OOM errors on A10 hardware, set `WAN_ENABLE_CPU_OFFLOAD=true` or lower the resolution (`width`/`height`) and/or frames.
