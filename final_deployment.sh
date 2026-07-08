#!/usr/bin/env bash
source .env 2>/dev/null || true
# Update Deployment for Private GitHub
set -e

export REGION="${REGION:-us-south}"

GITHUB_TOKEN="${GITHUB_TOKEN}"
REPO_URL="https://github.com/joshuaipock4-art/regional-retail-swarm"
NAMESPACE="online_retail_swarm"
IMAGE_NAME="retail-swarm"
REGISTRY_SERVER="us.icr.io"

echo "[1/4] Retrieving IAM Access Token..."
TOKEN_RESPONSE=$(curl -s -X POST "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  --data-urlencode "grant_type=urn:ibm:params:oauth:grant-type:apikey" \
  --data-urlencode "apikey=$IBMCLOUD_API_KEY")
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')

echo "[2/4] Re-creating Registry Secret..."
curl -s -X DELETE "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/secrets/retail-swarm-registry-secret" \
  -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null || true

curl -s -X POST "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/secrets" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"retail-swarm-registry-secret\",
    \"format\": \"registry\",
    \"data\": {
      \"server\": \"$REGISTRY_SERVER\",
      \"username\": \"iamapikey\",
      \"password\": \"$IBMCLOUD_API_KEY\"
    }
  }" | python3 -m json.tool || true

echo "[2.5/4] Re-creating Git Auth Secret..."
curl -s -X DELETE "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/secrets/retail-swarm-git-auth" \
  -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null || true

curl -s -X POST "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/secrets" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"retail-swarm-git-auth\",
    \"format\": \"basic_auth\",
    \"data\": {
      \"username\": \"joshuaipock4-art\",
      \"password\": \"$GITHUB_TOKEN\"
    }
  }" | python3 -m json.tool || true

echo "[3/4] Re-creating Build Configuration..."
# Delete old build
curl -s -X DELETE "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/builds/retail-swarm-github-build" \
  -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null || true

sleep 2

# Create new build with git_secret
curl -s -X POST "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/builds" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"retail-swarm-github-build\",
    \"source_type\": \"git\",
    \"source_url\": \"$REPO_URL\",
    \"source_revision\": \"shopify-integration-822303029735242017\",
    \"strategy_type\": \"dockerfile\",
    \"strategy_size\": \"medium\",
    \"output_image\": \"$REGISTRY_SERVER/$NAMESPACE/$IMAGE_NAME:latest\",
    \"source_secret\": \"retail-swarm-git-auth\",
    \"output_secret\": \"retail-swarm-registry-secret\"
  }" | python3 -m json.tool

echo "[4/4] Submitting Final BuildRun..."
RUN_NAME="retail-swarm-final-run-$(date +%s)"
curl -s -X POST "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/build_runs" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"$RUN_NAME\",
    \"build_name\": \"retail-swarm-github-build\"
  }" | python3 -m json.tool

echo "Expert DevOps: Authenticated Build Submitted!"
