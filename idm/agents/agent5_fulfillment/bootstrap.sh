#!/usr/bin/env bash
export AGENT_ID="agent5"
export AGENT_ROLE="agent5_fulfillment"
source /idm/system/env.sh
python3 -u /idm/agents/agent5_fulfillment/main.py
