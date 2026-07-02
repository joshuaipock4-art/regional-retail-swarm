#!/usr/bin/env bash
export AGENT_ID="agent10"
export AGENT_ROLE="agent10_competitor_analyst"
source /idm/system/env.sh
python3 -u /idm/agents/agent10_competitor_analyst/main.py
