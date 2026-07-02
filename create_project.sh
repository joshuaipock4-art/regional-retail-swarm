#!/usr/bin/env bash
source .env 2>/dev/null || true
export REGION="${REGION:-us-south}"
RG_ID="dc975b952cbe4f69900ced1a364da99a"

# 1. Get Access Token
TOKEN_RESPONSE=$(curl -s -X POST "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  --data-urlencode "grant_type=urn:ibm:params:oauth:grant-type:apikey" \
  --data-urlencode "apikey=$IBMCLOUD_API_KEY")
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')

# 2. Create Project
echo "Creating Code Engine project: online-retail-swarm-project"
curl -s -X POST "https://api.${REGION}.codeengine.cloud.ibm.com/v2/projects" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"online-retail-swarm-project\",
    \"resource_group_id\": \"$RG_ID\"
  }" | python3 -m json.tool
