#!/usr/bin/env bash
export AGENT_ID="agent1"
export AGENT_ROLE="agent1_sourcing"
source /idm/system/env.sh
python3 -u /idm/agents/agent1_sourcing/main.py
