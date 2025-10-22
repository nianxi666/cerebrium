# Qwen Image Deployment on Cerebrium

This repository packages a FastAPI application that wraps the standard Qwen image generation model (`Qwen/Qwen2-Image` by default) and is ready to deploy on [Cerebrium](https://www.cerebrium.ai/). It provides:

- A production-ready API (`main.py`) with `/health` and `/generate` endpoints.
- A `cerebrium.toml` configuration tuned for GPU-backed deployments.
- Dependency management via `requirements.txt`.
- Documentation for authenticating with a service account token and deploying without an interactive browser login.

## Repository structure

```
.
├── .gitignore
├── cerebrium.toml
├── main.py
├── README.md
└── requirements.txt
```

## Prerequisites

- Python 3.10 or newer.
- Access to a Cerebrium project with GPU capacity (for best performance).
- A Hugging Face account with access to the selected Qwen image model (accept the license on Hugging Face and set `HF_TOKEN`).

## 1. Local environment setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install --upgrade cerebrium
pip install -r requirements.txt
```

## 2. Configure credentials (non-interactive login)

Because the current terminal environment has no browser, use the Cerebrium service account token provided to you. **Never commit the raw token to version control.**

```bash
export CEREBRIUM_SERVICE_ACCOUNT_TOKEN="<paste-your-service-account-jwt>"
export CEREBRIUM_PROJECT_ID="p-xxxxxxxx"
```

- Replace `<paste-your-service-account-jwt>` with the JWT you generated.
- Replace `p-xxxxxxxx` with the actual project ID (for the shared token above it is `p-9de54108`).
- The Cerebrium CLI automatically picks up `CEREBRIUM_SERVICE_ACCOUNT_TOKEN`. If you are using an older CLI release, consult the [official docs](https://docs.cerebrium.ai) for the equivalent `cerebrium auth` sub-command to persist the token.

For convenience, you can place these values in a local `.env` file (listed in `.gitignore`) and source it before working:

```bash
cat > .env <<'EOF'
export CEREBRIUM_SERVICE_ACCOUNT_TOKEN="..."
export CEREBRIUM_PROJECT_ID="p-9de54108"
export HF_TOKEN="<required huggingface token if the model needs authentication>"
export QWEN_IMAGE_MODEL_ID="Qwen/Qwen2-Image"
EOF

source .env
```

## 3. Deploy to Cerebrium

Ensure you are in the repository root, then execute:

```bash
cerebrium project set "$CEREBRIUM_PROJECT_ID"
cerebrium deploy
```

The CLI reads the deployment metadata from `cerebrium.toml` and builds a container image that exposes the FastAPI service on port `8000`.

### Deployment tuning

- **Model selection:** Override `QWEN_IMAGE_MODEL_ID` to target other variants, e.g. the distilled `Qwen/Qwen2-Image-1.2B-Distilled` or AWQ quantized checkpoints.
- **Resolution limits:** Adjust `QWEN_MIN_RESOLUTION` / `QWEN_MAX_RESOLUTION` environment variables if you need different bounds.
- **Default settings:** Override `QWEN_DEFAULT_STEPS` and `QWEN_DEFAULT_GUIDANCE` to change the default inference parameters.

## 4. Run locally (optional)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Check the service:

```bash
curl http://127.0.0.1:8000/health
```

Generate an image (the response contains a Base64 encoded PNG):

```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
        "prompt": "A tranquil mountain lake at sunrise",
        "num_inference_steps": 40,
        "guidance_scale": 6.5,
        "width": 1024,
        "height": 1024
      }'
```

## 5. Calling the deployed endpoint

Once deployed, the service will be exposed at an endpoint similar to:

```
https://api.aws.us-east-1.cerebrium.ai/v4/<project-id>/<deployment-name>/generate
```

Use the same JSON payload as the local example. Include the bearer token (service account key) in the `Authorization` header:

```bash
curl -X POST "https://api.aws.us-east-1.cerebrium.ai/v4/p-9de54108/qwen-image-inference/generate" \
  -H "Authorization: Bearer $CEREBRIUM_SERVICE_ACCOUNT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A futuristic city skyline at dusk"}'
```

## Security notes

- Rotate the service account token periodically and store it securely (e.g. a secrets manager).
- Never hard-code secrets inside the codebase.
- If the Hugging Face model requires authentication, use the `HF_TOKEN` environment variable and configure it inside Cerebrium as a secret.

## Troubleshooting

| Issue | Suggested action |
|-------|------------------|
| `Model is still loading` | Wait for startup to complete or verify GPU availability. |
| `Image generation failed` | Check build logs for missing dependencies or Hugging Face permissions. |
| `Failed to load model Qwen/Qwen2-Image` | Make sure your Hugging Face account has accepted the model’s license and provide `HF_TOKEN` as an environment variable/secret. |
| `401 Unauthorized` | Ensure the `Authorization: Bearer` header contains a valid, non-expired service account token. |
| Slow inference | Reduce resolution or inference steps, or upgrade to a stronger GPU tier in `cerebrium.toml`. |

---

Need more customization? Review the detailed configuration options in the official [Cerebrium TOML reference](https://docs.cerebrium.ai/toml-reference/toml-reference).
