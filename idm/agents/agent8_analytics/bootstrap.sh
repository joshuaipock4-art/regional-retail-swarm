#!/usr/bin/env bash
export AGENT_ID="agent8"
export AGENT_ROLE="agent8_analytics"
source /idm/system/env.sh
python3 -u /idm/agents/agent8_analytics/main.py
