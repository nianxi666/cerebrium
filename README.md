# LatentSync Cerebrium Deployment

This is a Cerebrium deployment for [LatentSync](https://github.com/nianxi666/LatentSync), an end-to-end lip-sync method based on audio-conditioned latent diffusion models.

## Overview

LatentSync performs audio-driven lip-sync on videos, allowing you to replace the audio of a video while synchronizing the lips of the person in the video to match the new audio.

## Hardware Requirements

This deployment is configured to use an **AMPERE_A100_80GB** GPU, which is required for the high-resolution (512x512) model variant. The model requires approximately 18GB of VRAM for inference.

## Deployment

### Prerequisites

1. A Cerebrium account
2. Cerebrium API key

### Steps

1. Export your Cerebrium API key:

```bash
export CEREBRIUM_API_KEY="your-api-key-here"
```

2. Deploy using the provided script:

```bash
./deploy.sh
```

Or manually:

```bash
pip install --upgrade cerebrium
cerebrium deploy
```

## Usage

Once deployed, you can make inference requests to the endpoint. The API accepts the following parameters:

### Input Parameters

- `video_url` (optional): URL to the input video (MP4 format)
- `video_base64` (optional): Base64-encoded video file
- `audio_url` (optional): URL to the input audio (WAV/MP3 format)
- `audio_base64` (optional): Base64-encoded audio file
- `guidance_scale` (optional, default: 1.5): Controls lip-sync accuracy (range: 1.0-3.0)
  - Higher values improve accuracy but may cause distortion
- `inference_steps` (optional, default: 20): Number of inference steps (range: 20-50)
  - Higher values improve quality but slow down generation
- `seed` (optional, default: 1247): Random seed for reproducibility

**Note:** You must provide either `video_url` or `video_base64`, and either `audio_url` or `audio_base64`.

### Example Request with URLs

```bash
curl -X POST <YOUR_ENDPOINT_URL> \
  -H "Authorization: Bearer $CEREBRIUM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://github.com/anotherjesse/LatentSync/raw/main/assets/yuxin.mp4",
    "audio_url": "https://github.com/anotherjesse/LatentSync/raw/main/assets/audio_yuxin.wav",
    "guidance_scale": 1.5,
    "inference_steps": 20,
    "seed": 1247
  }'
```

### Example Request with Base64

```bash
curl -X POST <YOUR_ENDPOINT_URL> \
  -H "Authorization: Bearer $CEREBRIUM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "video_base64": "<base64-encoded-video>",
    "audio_base64": "<base64-encoded-audio>",
    "guidance_scale": 2.0,
    "inference_steps": 25
  }'
```

### Response

The API returns a JSON response containing:

```json
{
  "video_base64": "<base64-encoded-output-video>",
  "details": {
    "guidance_scale": 1.5,
    "inference_steps": 20,
    "seed": 1247
  }
}
```

## Model Details

- **Model**: LatentSync 1.6
- **Resolution**: 512x512
- **Architecture**: U-Net 3D with cross-attention
- **Audio Encoder**: Whisper (tiny variant)
- **VAE**: Stable Diffusion VAE (stabilityai/sd-vae-ft-mse)

## Features

- Automatic model weight downloading from HuggingFace
- Support for both URL and base64-encoded inputs
- Configurable guidance scale and inference steps
- Face detection and affine transformation
- Video looping for longer audio tracks
- GPU-accelerated inference with FP16 support

## Tips for Best Results

1. **Input Quality**: Use high-quality videos with clear, front-facing faces
2. **Guidance Scale**: 
   - Use 1.5-2.0 for balanced results
   - Increase to 2.5-3.0 for better lip-sync at the cost of potential artifacts
3. **Inference Steps**: 
   - 20 steps is sufficient for most cases
   - Increase to 30-50 for higher quality output
4. **Video Length**: The model works best with videos that match the audio length, but will automatically loop videos if needed

## License

This project uses LatentSync, which is licensed under the Apache License 2.0. See LICENSE file for details.

## Credits

- Original LatentSync implementation: [ByteDance/LatentSync](https://github.com/ByteDance/LatentSync)
- Fork: [nianxi666/LatentSync](https://github.com/nianxi666/LatentSync)
- Paper: [LatentSync on arXiv](https://arxiv.org/abs/2412.09262)
