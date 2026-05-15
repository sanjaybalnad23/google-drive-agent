#!/bin/sh

# This is used for deployment, basically u have to store service-account.json file content in GOOGLE_SERVICE_ACCOUNT_JSON environment variable
# Do not execute in local environment 

mkdir -p backend/secrets

echo "$GOOGLE_SERVICE_ACCOUNT_JSON" > backend/secrets/service-account.json

uv run uvicorn backend.app:app --host 0.0.0.0 --port $PORT