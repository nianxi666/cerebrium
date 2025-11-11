# ✅ Deployment Success Report

## Application Details
- **Application Name**: wan22-ti2v
- **Project ID**: p-194bc83f
- **Service**: Cerebrium AI
- **Status**: ✅ Live

## Endpoints
- **API Base URL**: `https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v`
- **Dashboard**: https://dashboard.cerebrium.ai/projects/p-194bc83f/apps/p-194bc83f-wan22-ti2v

## Deployment Configuration
- **Hardware**: AMPERE_A10 (24 GB GPU)
- **CPU**: 8 cores
- **Memory**: 32 GB
- **Python Version**: 3.11

## Key Dependencies
- PyTorch 2.3.1
- Diffusers 0.33.1
- Transformers 4.48.2
- CUDA 12.1

## Model Capabilities
- **Model**: Wan2.2 Text-Image-to-Video 5B
- **Output**: Up to 5 seconds of 720p (1280×704) video at 24 FPS
- **Input**: Text prompt + optional reference image
- **Features**:
  - Pure Text-to-Video (T2V)
  - Text-Image-to-Video (TI2V)
  - Customizable resolution, frames, and inference steps

## Usage Example
```bash
curl -X POST https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v/predict \
  -H "Authorization: Bearer <your-api-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cat dancing on a stage",
    "negative_prompt": "low quality, blurry",
    "num_frames": 121,
    "num_inference_steps": 50,
    "guidance_scale": 5.0
  }'
```

## Deployment Date
2024-11-11 02:06

## Notes
- Service account token authentication enabled
- Syntax checks disabled during deployment
- Model loading handled via DiffusionPipeline.from_pretrained()
