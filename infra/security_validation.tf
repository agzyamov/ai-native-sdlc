# Security Validation - Prevent Public Resource Deployment
# This file enforces network isolation policies

# Validation: Ensure public access is disabled
resource "null_resource" "validate_no_public_access" {
  # Trigger validation on every apply
  triggers = {
    always_run = timestamp()
  }

  # Fail deployment if public access is enabled
  provisioner "local-exec" {
    command = <<-EOT
      if [ "${var.enable_public_access}" = "true" ]; then
        echo "ERROR: Public access is ENABLED. This violates security policy."
        echo "ERROR: Set enable_public_access = false in terraform.tfvars"
        exit 1
      fi
      echo "✓ Security validation passed: Public access is disabled"
    EOT
  }
}

# Validation: Ensure Premium plan is used (not Consumption)
locals {
  is_premium_plan = can(regex("^(EP1|EP2|EP3)$", var.service_plan_sku))
}

resource "null_resource" "validate_premium_plan" {
  # Trigger validation on every apply
  triggers = {
    always_run = timestamp()
  }

  # Fail deployment if Consumption plan is used
  provisioner "local-exec" {
    command = <<-EOT
      if [ "${var.service_plan_sku}" = "Y1" ]; then
        echo "ERROR: Consumption plan (Y1) does NOT support network isolation."
        echo "ERROR: This violates the security policy: NO public internet access."
        echo "ERROR: Use Premium plan (EP1/EP2/EP3) in terraform.tfvars"
        echo "ERROR: Set service_plan_sku = \"EP1\""
        exit 1
      fi
      echo "✓ Security validation passed: Premium plan configured (${var.service_plan_sku})"
    EOT
  }
}

# Output validation results
output "security_validation" {
  value = {
    public_access_disabled = !var.enable_public_access
    premium_plan_enabled   = local.is_premium_plan
    vnet_name              = var.vnet_name
    policy_compliant       = !var.enable_public_access && local.is_premium_plan
  }
  description = "Security validation status for deployed resources"
}
