#!/usr/bin/env bash
export AGENT_ID="agent3"
export AGENT_ROLE="agent3_support"
source /idm/system/env.sh
python3 -u /idm/agents/agent3_support/main.py
