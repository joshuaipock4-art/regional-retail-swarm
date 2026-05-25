#!/usr/bin/env bash
export AGENT_ID="agent2"
export AGENT_ROLE="agent2_marketer"
source /idm/system/env.sh
python3 -u /idm/agents/agent2_marketer/main.py
