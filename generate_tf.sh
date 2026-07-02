#!/usr/bin/env bash
# Generator for the Retail Swarm Terraform Deployment
cat << 'EOF' > retail_swarm_deployment.tf
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
EOF

# Now append the agent logic to the user_data in the TF file
# Using a temporary file to build the user_data block
cat << 'EOF' > user_data_agents.sh
AGENT_NAMES=(
    "agent0_trend_scout"
    "agent1_sourcing"
    "agent2_marketer"
    "agent3_support"
    "agent4_storefront"
    "agent5_fulfillment"
    "agent6_post_purchase"
    "agent7_inventory"
    "agent8_analytics"
    "agent10_competitor_analyst"
)

PYTHON_TEMPLATE='import time
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
'

for i in "${!AGENT_NAMES[@]}"; do
    NAME="${AGENT_NAMES[$i]}"
    IDX=$(echo "$NAME" | grep -o -E '[0-9]+')
    DIR="/idm/agents/$NAME"
    
    echo "mkdir -p $DIR"
    
    echo "cat << 'INNER_EOF' > $DIR/main.py"
    echo "$PYTHON_TEMPLATE"
    echo "INNER_EOF"
    
    echo "cat << 'INNER_EOF' > $DIR/bootstrap.sh"
    echo "#!/usr/bin/env bash"
    echo "export AGENT_ID=\"agent$IDX\""
    echo "export AGENT_ROLE=\"$NAME\""
    echo "source /idm/system/env.sh"
    echo "python3 -u $DIR/main.py"
    echo "INNER_EOF"
    echo "chmod +x $DIR/bootstrap.sh"
    
    echo "cat << 'INNER_EOF' > /idm/system/supervisor/agent$IDX.conf"
    echo "[program:agent$IDX]"
    echo "command=bash $DIR/bootstrap.sh"
    echo "directory=$DIR"
    echo "autostart=true"
    echo "autorestart=true"
    echo "stdout_logfile=/idm/system/logs/agent$IDX.log"
    echo "stderr_logfile=/idm/system/logs/agent$IDX_error.log"
    echo "INNER_EOF"
done

echo "ln -s /idm/system/supervisor/*.conf /etc/supervisor/conf.d/"
echo "systemctl restart supervisor"
EOF

# Execute the agent block generator and insert into TF
bash user_data_agents.sh > agents_block.txt
sed -i "/# (This part will be populated by the generator script)/r agents_block.txt" retail_swarm_deployment.tf

# Cleanup
rm user_data_agents.sh agents_block.txt
