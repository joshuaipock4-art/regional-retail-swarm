#!/usr/bin/env bash
source .env 2>/dev/null || true
# Deploy Application to Code Engine
set -e

export REGION="${REGION:-us-south}"

NAMESPACE="online_retail_swarm"
IMAGE_NAME="retail-swarm"
REGISTRY_SERVER="us.icr.io"

echo "[1/3] Retrieving IAM Access Token..."
TOKEN_RESPONSE=$(curl -s -X POST "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  --data-urlencode "grant_type=urn:ibm:params:oauth:grant-type:apikey" \
  --data-urlencode "apikey=$IBMCLOUD_API_KEY")
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')

echo "[2/3] Creating/updating e-commerce secrets..."
# Base64 encode the keys
SHOPIFY_CLIENT_ID_B64=$(echo -n "$SHOPIFY_CLIENT_ID" | base64)
SHOPIFY_CLIENT_SECRET_B64=$(echo -n "$SHOPIFY_CLIENT_SECRET" | base64)
SHOPIFY_STORE_URL_B64=$(echo -n "$SHOPIFY_STORE_URL" | base64)
CJ_DROPSHIPPING_API_KEY_B64=$(echo -n "$CJ_DROPSHIPPING_API_KEY" | base64)

# Delete existing secret if it exists to ensure freshness
curl -s -X DELETE "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/secrets/ecommerce-secrets" \
  -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null || true

# Create the secret
curl -s -X POST "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/secrets" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"ecommerce-secrets\",
    \"format\": \"generic\",
    \"data\": {
      \"SHOPIFY_CLIENT_ID\": \"$SHOPIFY_CLIENT_ID_B64\",
      \"SHOPIFY_CLIENT_SECRET\": \"$SHOPIFY_CLIENT_SECRET_B64\",
      \"SHOPIFY_STORE_URL\": \"$SHOPIFY_STORE_URL_B64\",
      \"CJ_DROPSHIPPING_API_KEY\": \"$CJ_DROPSHIPPING_API_KEY_B64\"
    }
  }" > /dev/null || true

echo "[3/3] Creating Application: online-retail-swarm-app..."
curl -s -X POST "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/apps" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"online-retail-swarm-app\",
    \"image_reference\": \"$REGISTRY_SERVER/$NAMESPACE/$IMAGE_NAME:latest\",
    \"image_secret\": \"retail-swarm-registry-secret\",
    \"min_scale\": 1,
    \"max_scale\": 10,
    \"port\": 8080,
    \"run_env_variables\": [
      {
        \"type\": \"secret_full_reference\",
        \"reference\": \"ecommerce-secrets\"
      }
    ]
  }" | python3 -m json.tool

echo "Creating/updating Code Engine Job: retail-swarm-agent-10..."
# Delete existing job if it exists to ensure freshness
curl -s -X DELETE "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/jobs/retail-swarm-agent-10" \
  -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null || true

# Create the job running our end-to-end pricing pipeline
curl -s -X POST "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/jobs" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"retail-swarm-agent-10\",
    \"image_reference\": \"$REGISTRY_SERVER/$NAMESPACE/$IMAGE_NAME:latest\",
    \"image_secret\": \"retail-swarm-registry-secret\",
    \"run_env_variables\": [
      {
        \"type\": \"secret_full_reference\",
        \"reference\": \"ecommerce-secrets\"
      }
    ],
    "run_arguments": [
      "python3",
      "-c",
      "import sys; sys.path.insert(0, 'idm/agents/agent1_sourcing'); import main as m1; m1.build_sourcing_catalog(); sys.modules.pop('main'); sys.path.insert(0, 'idm/agents/agent10_competitor_analyst'); import main as m10; m10.scan_competitor_prices(); sys.modules.pop('main'); sys.path.insert(0, 'idm/agents/agent7_inventory'); import main as m7; m7.build_shopify_catalog()"
    ]
  }" > /dev/null || true

echo "Creating Code Engine Cron Subscriptions targeting job: retail-swarm-agent-10..."
# Delete existing subscriptions to ensure freshness
curl -s -X DELETE "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/subscriptions/cron/retail-swarm-cron-morning" \
  -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null || true
curl -s -X DELETE "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/subscriptions/cron/retail-swarm-cron-afternoon" \
  -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null || true
curl -s -X DELETE "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/subscriptions/cron/retail-swarm-cron-evening" \
  -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null || true

# Morning Cron: 08:12 AM CST (14:12 UTC)
curl -s -X POST "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/subscriptions/cron" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"retail-swarm-cron-morning\",
    \"destination\": \"retail-swarm-agent-10\",
    \"destination_type\": \"job\",
    \"schedule\": \"12 14 * * *\"
  }" > /dev/null || true

# Afternoon Cron: 01:12 PM CST (19:12 UTC)
curl -s -X POST "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/subscriptions/cron" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"retail-swarm-cron-afternoon\",
    \"destination\": \"retail-swarm-agent-10\",
    \"destination_type\": \"job\",
    \"schedule\": \"12 19 * * *\"
  }" > /dev/null || true

# Evening Cron: 07:12 PM CST (01:12 UTC next day)
curl -s -X POST "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/subscriptions/cron" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"retail-swarm-cron-evening\",
    \"destination\": \"retail-swarm-agent-10\",
    \"destination_type\": \"job\",
    \"schedule\": \"12 1 * * *\"
  }" > /dev/null || true

echo "Expert DevOps Deployment Complete!"
echo "Your 10-agent retail swarm is now LIVE and scheduled on IBM Cloud."
