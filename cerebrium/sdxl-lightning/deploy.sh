#!/bin/bash

# Check if CEREBRIUM_SERVICE_ACCOUNT_TOKEN is set
if [ -z "$CEREBRIUM_SERVICE_ACCOUNT_TOKEN" ]; then
  echo "Error: CEREBRIUM_SERVICE_ACCOUNT_TOKEN environment variable is not set."
  exit 1
fi

# Deploy the model
cerebrium deploy --disable-confirmation
