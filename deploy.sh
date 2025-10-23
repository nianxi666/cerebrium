#!/bin/bash

if [ -z "${CEREBRIUM_API_KEY}" ]; then
  echo "Error: CEREBRIUM_API_KEY is not set. Please export your API key before running this script." >&2
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
