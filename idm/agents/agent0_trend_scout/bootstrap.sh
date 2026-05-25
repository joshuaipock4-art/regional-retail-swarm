#!/usr/bin/env bash
export AGENT_ID="agent0"
export AGENT_ROLE="agent0_trend_scout"
source /idm/system/env.sh
python3 -u /idm/agents/agent0_trend_scout/main.py
