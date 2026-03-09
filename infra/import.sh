#!/bin/bash
set -e
cd /Users/Rustem_Agziamov/ai-native-sdlc/infra
export ARM_SUBSCRIPTION_ID=1313a7a3-30d8-4f42-adef-a730f6dc82fb
S=1313a7a3-30d8-4f42-adef-a730f6dc82fb
P="/subscriptions/$S"
RG="$P/resourceGroups/rg-func-dev"

echo "=== Importing existing Azure resources into Terraform state ==="

# azurerm_resource_group.main already imported - skip
echo "✓ resource group (already in state)"

terraform import -input=false azurerm_log_analytics_workspace.main "$RG/providers/Microsoft.OperationalInsights/workspaces/law-dev-func"
echo "✓ log analytics"

terraform import -input=false azurerm_application_insights.main "$RG/providers/Microsoft.Insights/components/ai-dev-func"
echo "✓ app insights"

terraform import -input=false azurerm_service_plan.main "$RG/providers/Microsoft.Web/serverFarms/asp-dev-spec"
echo "✓ service plan"

terraform import -input=false azurerm_virtual_network.main "$RG/providers/Microsoft.Network/virtualNetworks/vnet-dev"
echo "✓ vnet"

terraform import -input=false azurerm_subnet.function "$RG/providers/Microsoft.Network/virtualNetworks/vnet-dev/subnets/snet-func"
echo "✓ subnet function"

terraform import -input=false azurerm_subnet.private_endpoint "$RG/providers/Microsoft.Network/virtualNetworks/vnet-dev/subnets/snet-pe"
echo "✓ subnet pe"

terraform import -input=false azurerm_key_vault.main "$RG/providers/Microsoft.KeyVault/vaults/kv-dev-func"
echo "✓ key vault"

terraform import -input=false "azurerm_private_dns_zone.blob" "$RG/providers/Microsoft.Network/privateDnsZones/privatelink.blob.core.windows.net"
echo "✓ dns zone blob"

terraform import -input=false "azurerm_private_dns_zone.file" "$RG/providers/Microsoft.Network/privateDnsZones/privatelink.file.core.windows.net"
echo "✓ dns zone file"

terraform import -input=false "azurerm_private_dns_zone.keyvault" "$RG/providers/Microsoft.Network/privateDnsZones/privatelink.vaultcore.azure.net"
echo "✓ dns zone keyvault"

terraform import -input=false "azurerm_private_dns_zone_virtual_network_link.blob" "$RG/providers/Microsoft.Network/privateDnsZones/privatelink.blob.core.windows.net/virtualNetworkLinks/vnet-link-blob"
echo "✓ dns link blob"

terraform import -input=false "azurerm_private_dns_zone_virtual_network_link.file" "$RG/providers/Microsoft.Network/privateDnsZones/privatelink.file.core.windows.net/virtualNetworkLinks/vnet-link-file"
echo "✓ dns link file"

terraform import -input=false "azurerm_private_dns_zone_virtual_network_link.keyvault" "$RG/providers/Microsoft.Network/privateDnsZones/privatelink.vaultcore.azure.net/virtualNetworkLinks/vnet-link-keyvault"
echo "✓ dns link keyvault"

terraform import -input=false azurerm_private_endpoint.keyvault "$RG/providers/Microsoft.Network/privateEndpoints/kv-func-dev-pe"
echo "✓ pe keyvault"

terraform import -input=false azurerm_linux_function_app.main "$RG/providers/Microsoft.Web/sites/func-dev-dispatch"
echo "✓ function app"

echo "=== All imports done. Running plan ==="
terraform plan -out=tfplan 2>&1
echo "=== Plan done ==="
