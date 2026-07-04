#!/usr/bin/env bash
source .env 2>/dev/null || true
# Update Application with ETag handling
set -e

export REGION="${REGION:-us-south}"

APP_NAME="online-retail-swarm-app"

echo "[1/3] Retrieving IAM Access Token..."
TOKEN_RESPONSE=$(curl -s -X POST "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  --data-urlencode "grant_type=urn:ibm:params:oauth:grant-type:apikey" \
  --data-urlencode "apikey=$IBMCLOUD_API_KEY")
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')

echo "[2/3] Fetching current ETag..."
APP_INFO=$(curl -s -X GET "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/apps/${APP_NAME}" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
ETAG=$(echo $APP_INFO | sed -n 's/.*"entity_tag":"\([^"]*\)".*/\1/p')

echo "Current ETag: $ETAG"

echo "[3/3] Patching Application..."
curl -s -X PATCH "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/apps/${APP_NAME}" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -H "If-Match: $ETAG" \
  -d "{
    \"image_reference\": \"us.icr.io/online_retail_swarm/retail-swarm:latest\"
  }" | python3 -m json.tool

echo "--------------------------------------------------------"
echo "Expert DevOps Deployment Successfully Updated!"
