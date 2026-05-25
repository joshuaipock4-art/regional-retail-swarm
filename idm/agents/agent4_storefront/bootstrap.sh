#!/usr/bin/env bash
export AGENT_ID="agent4"
export AGENT_ROLE="agent4_storefront"
source /idm/system/env.sh
python3 -m uvicorn main:app --host 0.0.0.0 --port 8080
