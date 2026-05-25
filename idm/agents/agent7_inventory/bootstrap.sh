#!/usr/bin/env bash
export AGENT_ID="agent7"
export AGENT_ROLE="agent7_inventory"
source /idm/system/env.sh
python3 -u /idm/agents/agent7_inventory/main.py
