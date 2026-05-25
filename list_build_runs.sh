#!/usr/bin/env bash
source .env

# 1. Get Access Token
TOKEN_RESPONSE=$(curl -s -X POST "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  --data-urlencode "grant_type=urn:ibm:params:oauth:grant-type:apikey" \
  --data-urlencode "apikey=$IBMCLOUD_API_KEY")
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')

# 2. List Build Runs
curl -s -X GET "https://api.jp-tok.codeengine.cloud.ibm.com/v2/projects/986156ac-6823-4b7c-ab64-50a6eae46452/build_runs" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
