#!/bin/bash

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

if [ -z "${CEREBRIUM_SERVICE_ACCOUNT_TOKEN}" ] && [ -z "${CEREBRIUM_API_KEY}" ]; then
  echo "Error: CEREBRIUM_SERVICE_ACCOUNT_TOKEN or CEREBRIUM_API_KEY is not set." >&2
  echo "Please create a .env file with your CEREBRIUM_SERVICE_ACCOUNT_TOKEN or export it." >&2
  exit 1
fi

# Install Cerebrium CLI if not already installed
if ! command -v cerebrium &> /dev/null; then
  echo "Installing Cerebrium CLI..."
  pip install --upgrade cerebrium
fi

# Deploy to Cerebrium
echo "Deploying LatentSync to Cerebrium..."
cerebrium deploy
