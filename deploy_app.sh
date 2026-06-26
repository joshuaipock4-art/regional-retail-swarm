#!/usr/bin/env bash
source .env
# Deploy Application to Code Engine
set -e

NAMESPACE="online_retail_swarm"
IMAGE_NAME="retail-swarm"
REGISTRY_SERVER="jp.icr.io"

echo "[1/2] Retrieving IAM Access Token..."
TOKEN_RESPONSE=$(curl -s -X POST "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  --data-urlencode "grant_type=urn:ibm:params:oauth:grant-type:apikey" \
  --data-urlencode "apikey=$IBMCLOUD_API_KEY")
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')

echo "[2/2] Creating Application: online-retail-swarm-app..."
curl -s -X POST "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/apps" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"online-retail-swarm-app\",
    \"image_reference\": \"$REGISTRY_SERVER/$NAMESPACE/$IMAGE_NAME:latest\",
    \"image_secret\": \"retail-swarm-registry-secret\",
    \"min_scale\": 1,
    \"max_scale\": 10,
    \"port\": 8080
  }" | python3 -m json.tool

echo "Expert DevOps Deployment Complete!"
echo "Your autonomous Italian leather dropshipping retail swarm is now LIVE on IBM Cloud."
