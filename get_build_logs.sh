#!/usr/bin/env bash
source .env 2>/dev/null || true
export REGION="${REGION:-us-south}"
RUN_NAME="retail-swarm-final-run-1779683030"

# 1. Get Access Token
TOKEN_RESPONSE=$(curl -s -X POST "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  --data-urlencode "grant_type=urn:ibm:params:oauth:grant-type:apikey" \
  --data-urlencode "apikey=$IBMCLOUD_API_KEY")
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')

# 2. Get Build Run Logs
echo "Build Run Logs for $RUN_NAME:"
curl -s -X GET "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/build_runs/${RUN_NAME}/logs" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
