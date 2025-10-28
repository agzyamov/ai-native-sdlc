#!/bin/bash
# Update deployment IP in terraform.tfvars for Azure Function deployment access
# Run this script whenever your IP changes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TFVARS_FILE="$SCRIPT_DIR/../infra/terraform.tfvars"

# Get current public IP
echo "🔍 Detecting your public IP..."
CURRENT_IP=$(curl -s https://api.ipify.org)

if [ -z "$CURRENT_IP" ]; then
  echo "❌ ERROR: Could not detect public IP"
  exit 1
fi

echo "✅ Detected IP: $CURRENT_IP"

# Format as CIDR
IP_CIDR="${CURRENT_IP}/32"

# Create or update terraform.tfvars
if [ -f "$TFVARS_FILE" ]; then
  # Update existing file
  if grep -q "^deployment_allowed_ip" "$TFVARS_FILE"; then
    # Replace existing line
    if [[ "$OSTYPE" == "darwin"* ]]; then
      sed -i '' "s|^deployment_allowed_ip.*|deployment_allowed_ip = \"$IP_CIDR\"|" "$TFVARS_FILE"
    else
      sed -i "s|^deployment_allowed_ip.*|deployment_allowed_ip = \"$IP_CIDR\"|" "$TFVARS_FILE"
    fi
    echo "✅ Updated deployment_allowed_ip in $TFVARS_FILE"
  else
    # Add new line
    echo "" >> "$TFVARS_FILE"
    echo "# Deployment access IP (auto-updated by scripts/update-deployment-ip.sh)" >> "$TFVARS_FILE"
    echo "deployment_allowed_ip = \"$IP_CIDR\"" >> "$TFVARS_FILE"
    echo "✅ Added deployment_allowed_ip to $TFVARS_FILE"
  fi
else
  # Create new file
  cat > "$TFVARS_FILE" << EOF
# Deployment access IP (auto-updated by scripts/update-deployment-ip.sh)
deployment_allowed_ip = "$IP_CIDR"
EOF
  echo "✅ Created $TFVARS_FILE with deployment_allowed_ip"
fi

echo ""
echo "📝 Current configuration:"
grep "deployment_allowed_ip" "$TFVARS_FILE"
echo ""
echo "🚀 Next steps:"
echo "   1. cd infra"
echo "   2. terraform apply"
echo "   3. Deploy your function"
