# Security Architecture - Network Isolation

## Overview

All Azure resources for the spec automation system are **network-isolated** and **NOT publicly accessible**. Access is only possible through the existing VPN gateway.

## Network Architecture

```
[Azure DevOps] 
     ↓ (Service Hook via VPN)
[VPN Gateway] ← [Your Client]
     ↓
[VNet: vnet-ai-agents-infra-dev]
     ├── [Private Endpoint: Storage Blob]
     ├── [Private Endpoint: Storage File]
     └── [Function App with VNet Integration]
           ↓ (outbound via VNet)
      [GitHub API]
```

## Security Controls

### 1. Storage Account
- **Public Access**: `DISABLED` (`public_network_access_enabled = false`)
- **Access Method**: Private Endpoints only (blob + file)
- **Network Rules**: Default deny, bypass for Azure Services only
- **DNS**: Private DNS zones for `privatelink.blob.core.windows.net` and `privatelink.file.core.windows.net`

### 2. Function App
- **Public Access**: `DISABLED` (`public_network_access_enabled = false`)
- **VNet Integration**: Connected to `subnet-ai-dev` in existing VNet
- **Outbound Traffic**: Routes through VNet (`vnet_route_all_enabled = true`)
- **Access Method**: VPN connection required

### 3. Private Endpoints
**Storage Blob Endpoint:**
- Name: `{storage_name}-blob-pe`
- Subnet: `subnet-ai-dev`
- Subresource: `blob`

**Storage File Endpoint:**
- Name: `{storage_name}-file-pe`
- Subnet: `subnet-ai-dev`
- Subresource: `file`

### 4. Private DNS
**Automatic resolution within VNet:**
- `privatelink.blob.core.windows.net` → Storage blob private IP
- `privatelink.file.core.windows.net` → Storage file private IP

Linked to VNet: `vnet-ai-agents-infra-dev`

## Access Patterns

### Administrative Access
1. Connect to VPN
2. Access Azure Portal (resources visible but only manageable via VPN)
3. Use Azure CLI from VPN-connected machine

### Function Invocation
1. ADO Service Hook must originate from VPN-accessible network
2. Function URL resolves to private IP within VNet
3. No public internet access possible

### Outbound Connectivity
- Function → GitHub API: Routes through VNet NAT/Gateway
- Function → Storage: Via private endpoints (internal VNet traffic)
- Function → ADO API: Routes through VNet

## Deployment Considerations

### Initial Deployment (One-Time)
**Option 1: From VPN-connected machine (Recommended)**
```bash
# Connect to VPN first
terraform init
terraform apply
```

**Option 2: Temporary public access (NOT recommended)**
```hcl
# In terraform.tfvars (TEMPORARY ONLY)
enable_public_access = true
```

After deployment, immediately set back to `false` and reapply:
```bash
terraform apply -var="enable_public_access=false"
```

### ADO Service Hook Configuration
**Important**: ADO must be able to reach the private function endpoint.

**Options:**
1. **Self-hosted ADO Agent** (Recommended): Deploy agent in same VNet
2. **Azure DevOps Service Hooks**: May require additional network configuration
3. **Hybrid Connection**: Use Azure Relay or other hybrid connectivity

**Validation**:
```bash
# From VPN-connected machine
curl -X POST "https://{function-private-url}/api/spec-dispatch" \
  -H "Content-Type: application/json" \
  -d @sample-payload.json
```

## Compliance Checklist

- ✅ No resources expose public endpoints (`public_network_access_enabled = false`)
- ✅ All compute resources have VNet integration configured
- ✅ Private endpoints configured for all storage services
- ✅ Private DNS zones linked to VNet
- ✅ Network ACLs configured (default deny)
- ✅ VPN gateway access documented
- ✅ Firewall rules documented (Azure Services bypass only)

## Incident Response

### If Public Access Accidentally Enabled

1. **Immediate Action**:
   ```bash
   az functionapp update \
     --name {function-name} \
     --resource-group {rg} \
     --set publicNetworkAccess=Disabled
   
   az storage account update \
     --name {storage-name} \
     --resource-group {rg} \
     --public-network-access Disabled
   ```

2. **Audit**:
   - Check Azure Activity Log for unauthorized access attempts
   - Review function execution logs for unexpected invocations
   - Rotate all PATs immediately

3. **Remediation**:
   ```bash
   # Correct Terraform state
   terraform plan
   terraform apply
   ```

### Network Troubleshooting

**Function cannot access storage:**
1. Verify private endpoint status: `az network private-endpoint show`
2. Check DNS resolution from function: Add diagnostic code to log DNS lookup
3. Verify subnet delegation: `Microsoft.Web/serverFarms`
4. Check NSG rules on subnet

**Cannot invoke function from ADO:**
1. Verify VPN connectivity
2. Test from VPN-connected machine first
3. Check ADO agent network configuration
4. Verify function app status in portal

## References

- **VNet**: `vnet-ai-agents-infra-dev` in `rg-ai-agents-infra-dev`
- **Subnets**: 
  - Function VNet Integration: `subnet-ai-dev` (10.0.1.0/24)
  - Private Endpoints: `subnet-ai-dev` (10.0.1.0/24)
- **Gateway Subnet**: `GatewaySubnet` (10.0.255.0/27)

## Cost Impact

Private endpoints add minimal cost:
- Private Endpoint: ~$7/month per endpoint (2 endpoints = ~$14/month)
- Private DNS Zone: ~$0.50/month per zone (2 zones = ~$1/month)
- **Total additional cost**: ~$15/month for network isolation

**Trade-off**: Security vs. $15/month → **Security wins**
