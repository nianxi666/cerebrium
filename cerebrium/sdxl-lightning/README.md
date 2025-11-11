# SDXL-Lightning Deployment

This directory contains an example of how to deploy the SDXL-Lightning model to Cerebrium.

## Deployment

To deploy the model, you will need to have the Cerebrium CLI installed and a Cerebrium account. You will also need to have your Cerebrium service account token set as the `CEREBRIUM_SERVICE_ACCOUNT_TOKEN` environment variable.

Once you have everything set up, you can deploy the model by running the following command from within this directory:

```bash
./deploy.sh
```

## Usage

Once deployed, you can send inference requests to the endpoint using a `curl` command like the following:

```bash
curl -X POST <YOUR_ENDPOINT_URL> \
-H "Authorization: Bearer $CEREBRIUM_SERVICE_ACCOUNT_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "prompt": "a beautiful landscape",
  "num_inference_steps": 4,
  "guidance_scale": 0
}'
```
