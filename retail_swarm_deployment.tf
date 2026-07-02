terraform {
  required_providers {
    ibm = {
      source  = "IBM-Cloud/ibm"
      version = ">= 1.51.0"
    }
  }
}

provider "ibm" {
  region = "us-south"
}

variable "resource_group_id" {
  default = "1d3e7cf573f34830a5c1f86713f0ef78"
}

resource "ibm_is_vpc" "swarm_vpc" {
  name           = "online-retail-swarm-vpc"
  resource_group = var.resource_group_id
}

resource "ibm_is_subnet" "swarm_subnet" {
  name                     = "online-retail-swarm-subnet"
  vpc                      = ibm_is_vpc.swarm_vpc.id
  zone                     = "us-south-1"
  total_ipv4_address_count = 16
  resource_group           = var.resource_group_id
}

resource "ibm_is_ssh_key" "swarm_ssh_key" {
  name           = "online-retail-swarm-key"
  public_key     = file("vpc_key.pub")
  resource_group = var.resource_group_id
}

data "ibm_is_image" "ubuntu" {
  name = "ibm-ubuntu-22-04-4-minimal-amd64-1"
}

resource "ibm_is_instance" "swarm_instance" {
  name           = "online-retail-swarm-node"
  vpc            = ibm_is_vpc.swarm_vpc.id
  zone           = "us-south-1"
  keys           = [ibm_is_ssh_key.swarm_ssh_key.id]
  image          = data.ibm_is_image.ubuntu.id
  profile        = "cx2-2x4"
  resource_group = var.resource_group_id

  primary_network_interface {
    subnet = ibm_is_subnet.swarm_subnet.id
  }

  user_data = <<EOD
#!/bin/bash
echo "Initializing 9-State Retail Swarm Architecture..."

# Install dependencies
apt-get update
apt-get install -y supervisor python3-pip

# Reconstruct /idm structure
mkdir -p /idm/system/supervisor
mkdir -p /idm/system/logs
mkdir -p /idm/agents/agent{0..8}

# Write System Configs
cat << 'INNER_EOF' > /idm/system/env.sh
export SWARM_ENV="production"
export LOG_DIR="/idm/system/logs"
export GEMINI_MODEL="gemini-1.5-pro"
export REGION_COUNT=9
INNER_EOF

# Write Agents and Supervisor Configs
# (This part will be populated by the generator script)
mkdir -p /idm/agents/agent0_trend_scout
cat << 'INNER_EOF' > /idm/agents/agent0_trend_scout/main.py
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

INNER_EOF
cat << 'INNER_EOF' > /idm/agents/agent0_trend_scout/bootstrap.sh
#!/usr/bin/env bash
export AGENT_ID="agent0"
export AGENT_ROLE="agent0_trend_scout"
source /idm/system/env.sh
python3 -u /idm/agents/agent0_trend_scout/main.py
INNER_EOF
chmod +x /idm/agents/agent0_trend_scout/bootstrap.sh
cat << 'INNER_EOF' > /idm/system/supervisor/agent0.conf
[program:agent0]
command=bash /idm/agents/agent0_trend_scout/bootstrap.sh
directory=/idm/agents/agent0_trend_scout
autostart=true
autorestart=true
stdout_logfile=/idm/system/logs/agent0.log
stderr_logfile=/idm/system/logs/agent.log
INNER_EOF
mkdir -p /idm/agents/agent1_sourcing
cat << 'INNER_EOF' > /idm/agents/agent1_sourcing/main.py
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

INNER_EOF
cat << 'INNER_EOF' > /idm/agents/agent1_sourcing/bootstrap.sh
#!/usr/bin/env bash
export AGENT_ID="agent1"
export AGENT_ROLE="agent1_sourcing"
source /idm/system/env.sh
python3 -u /idm/agents/agent1_sourcing/main.py
INNER_EOF
chmod +x /idm/agents/agent1_sourcing/bootstrap.sh
cat << 'INNER_EOF' > /idm/system/supervisor/agent1.conf
[program:agent1]
command=bash /idm/agents/agent1_sourcing/bootstrap.sh
directory=/idm/agents/agent1_sourcing
autostart=true
autorestart=true
stdout_logfile=/idm/system/logs/agent1.log
stderr_logfile=/idm/system/logs/agent.log
INNER_EOF
mkdir -p /idm/agents/agent2_marketer
cat << 'INNER_EOF' > /idm/agents/agent2_marketer/main.py
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

INNER_EOF
cat << 'INNER_EOF' > /idm/agents/agent2_marketer/bootstrap.sh
#!/usr/bin/env bash
export AGENT_ID="agent2"
export AGENT_ROLE="agent2_marketer"
source /idm/system/env.sh
python3 -u /idm/agents/agent2_marketer/main.py
INNER_EOF
chmod +x /idm/agents/agent2_marketer/bootstrap.sh
cat << 'INNER_EOF' > /idm/system/supervisor/agent2.conf
[program:agent2]
command=bash /idm/agents/agent2_marketer/bootstrap.sh
directory=/idm/agents/agent2_marketer
autostart=true
autorestart=true
stdout_logfile=/idm/system/logs/agent2.log
stderr_logfile=/idm/system/logs/agent.log
INNER_EOF
mkdir -p /idm/agents/agent3_support
cat << 'INNER_EOF' > /idm/agents/agent3_support/main.py
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

INNER_EOF
cat << 'INNER_EOF' > /idm/agents/agent3_support/bootstrap.sh
#!/usr/bin/env bash
export AGENT_ID="agent3"
export AGENT_ROLE="agent3_support"
source /idm/system/env.sh
python3 -u /idm/agents/agent3_support/main.py
INNER_EOF
chmod +x /idm/agents/agent3_support/bootstrap.sh
cat << 'INNER_EOF' > /idm/system/supervisor/agent3.conf
[program:agent3]
command=bash /idm/agents/agent3_support/bootstrap.sh
directory=/idm/agents/agent3_support
autostart=true
autorestart=true
stdout_logfile=/idm/system/logs/agent3.log
stderr_logfile=/idm/system/logs/agent.log
INNER_EOF
mkdir -p /idm/agents/agent4_storefront
cat << 'INNER_EOF' > /idm/agents/agent4_storefront/main.py
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

INNER_EOF
cat << 'INNER_EOF' > /idm/agents/agent4_storefront/bootstrap.sh
#!/usr/bin/env bash
export AGENT_ID="agent4"
export AGENT_ROLE="agent4_storefront"
source /idm/system/env.sh
python3 -u /idm/agents/agent4_storefront/main.py
INNER_EOF
chmod +x /idm/agents/agent4_storefront/bootstrap.sh
cat << 'INNER_EOF' > /idm/system/supervisor/agent4.conf
[program:agent4]
command=bash /idm/agents/agent4_storefront/bootstrap.sh
directory=/idm/agents/agent4_storefront
autostart=true
autorestart=true
stdout_logfile=/idm/system/logs/agent4.log
stderr_logfile=/idm/system/logs/agent.log
INNER_EOF
mkdir -p /idm/agents/agent5_fulfillment
cat << 'INNER_EOF' > /idm/agents/agent5_fulfillment/main.py
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

INNER_EOF
cat << 'INNER_EOF' > /idm/agents/agent5_fulfillment/bootstrap.sh
#!/usr/bin/env bash
export AGENT_ID="agent5"
export AGENT_ROLE="agent5_fulfillment"
source /idm/system/env.sh
python3 -u /idm/agents/agent5_fulfillment/main.py
INNER_EOF
chmod +x /idm/agents/agent5_fulfillment/bootstrap.sh
cat << 'INNER_EOF' > /idm/system/supervisor/agent5.conf
[program:agent5]
command=bash /idm/agents/agent5_fulfillment/bootstrap.sh
directory=/idm/agents/agent5_fulfillment
autostart=true
autorestart=true
stdout_logfile=/idm/system/logs/agent5.log
stderr_logfile=/idm/system/logs/agent.log
INNER_EOF
mkdir -p /idm/agents/agent6_post_purchase
cat << 'INNER_EOF' > /idm/agents/agent6_post_purchase/main.py
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

INNER_EOF
cat << 'INNER_EOF' > /idm/agents/agent6_post_purchase/bootstrap.sh
#!/usr/bin/env bash
export AGENT_ID="agent6"
export AGENT_ROLE="agent6_post_purchase"
source /idm/system/env.sh
python3 -u /idm/agents/agent6_post_purchase/main.py
INNER_EOF
chmod +x /idm/agents/agent6_post_purchase/bootstrap.sh
cat << 'INNER_EOF' > /idm/system/supervisor/agent6.conf
[program:agent6]
command=bash /idm/agents/agent6_post_purchase/bootstrap.sh
directory=/idm/agents/agent6_post_purchase
autostart=true
autorestart=true
stdout_logfile=/idm/system/logs/agent6.log
stderr_logfile=/idm/system/logs/agent.log
INNER_EOF
mkdir -p /idm/agents/agent7_inventory
cat << 'INNER_EOF' > /idm/agents/agent7_inventory/main.py
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

INNER_EOF
cat << 'INNER_EOF' > /idm/agents/agent7_inventory/bootstrap.sh
#!/usr/bin/env bash
export AGENT_ID="agent7"
export AGENT_ROLE="agent7_inventory"
source /idm/system/env.sh
python3 -u /idm/agents/agent7_inventory/main.py
INNER_EOF
chmod +x /idm/agents/agent7_inventory/bootstrap.sh
cat << 'INNER_EOF' > /idm/system/supervisor/agent7.conf
[program:agent7]
command=bash /idm/agents/agent7_inventory/bootstrap.sh
directory=/idm/agents/agent7_inventory
autostart=true
autorestart=true
stdout_logfile=/idm/system/logs/agent7.log
stderr_logfile=/idm/system/logs/agent.log
INNER_EOF
mkdir -p /idm/agents/agent8_analytics
cat << 'INNER_EOF' > /idm/agents/agent8_analytics/main.py
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

INNER_EOF
cat << 'INNER_EOF' > /idm/agents/agent8_analytics/bootstrap.sh
#!/usr/bin/env bash
export AGENT_ID="agent8"
export AGENT_ROLE="agent8_analytics"
source /idm/system/env.sh
python3 -u /idm/agents/agent8_analytics/main.py
INNER_EOF
chmod +x /idm/agents/agent8_analytics/bootstrap.sh
cat << 'INNER_EOF' > /idm/system/supervisor/agent8.conf
[program:agent8]
command=bash /idm/agents/agent8_analytics/bootstrap.sh
directory=/idm/agents/agent8_analytics
autostart=true
autorestart=true
stdout_logfile=/idm/system/logs/agent8.log
stderr_logfile=/idm/system/logs/agent.log
INNER_EOF
mkdir -p /idm/agents/agent10_competitor_analyst
cat << 'INNER_EOF' > /idm/agents/agent10_competitor_analyst/main.py
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

INNER_EOF
cat << 'INNER_EOF' > /idm/agents/agent10_competitor_analyst/bootstrap.sh
#!/usr/bin/env bash
export AGENT_ID="agent10"
export AGENT_ROLE="agent10_competitor_analyst"
source /idm/system/env.sh
python3 -u /idm/agents/agent10_competitor_analyst/main.py
INNER_EOF
chmod +x /idm/agents/agent10_competitor_analyst/bootstrap.sh
cat << 'INNER_EOF' > /idm/system/supervisor/agent10.conf
[program:agent10]
command=bash /idm/agents/agent10_competitor_analyst/bootstrap.sh
directory=/idm/agents/agent10_competitor_analyst
autostart=true
autorestart=true
stdout_logfile=/idm/system/logs/agent10.log
stderr_logfile=/idm/system/logs/agent.log
INNER_EOF
ln -s /idm/system/supervisor/*.conf /etc/supervisor/conf.d/
systemctl restart supervisor
EOD
}

resource "ibm_is_floating_ip" "swarm_fip" {
  name   = "online-retail-swarm-fip"
  target = ibm_is_instance.swarm_instance.primary_network_interface[0].id
  resource_group = var.resource_group_id
}

output "swarm_public_ip" {
  value = ibm_is_floating_ip.swarm_fip.address
}
