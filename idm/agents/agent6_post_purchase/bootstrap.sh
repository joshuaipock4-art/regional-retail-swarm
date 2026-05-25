#!/usr/bin/env bash
export AGENT_ID="agent6"
export AGENT_ROLE="agent6_post_purchase"
source /idm/system/env.sh
python3 -u /idm/agents/agent6_post_purchase/main.py
