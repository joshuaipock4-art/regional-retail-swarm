import time
import os
import sys

agent_id = os.environ.get("AGENT_ID", "unknown")
agent_role = os.environ.get("AGENT_ROLE", "worker")

print(f"[BOOT] {agent_role} ({agent_id}) initialized.")

try:
    while True:
        print(f"[RUN] {agent_role} is active. Processing regional data...")
        time.sleep(30)
except KeyboardInterrupt:
    print(f"[STOP] {agent_role} shutting down.")

