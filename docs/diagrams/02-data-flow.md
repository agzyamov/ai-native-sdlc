# Data Flow (Specification Automation)

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#0d1117','primaryTextColor':'#c9d1d9','primaryBorderColor':'#30363d','lineColor':'#58a6ff','secondaryColor':'#161b22','tertiaryColor':'#21262d','background':'#0d1117','mainBkg':'#161b22','secondBkg':'#21262d','tertiaryBorderColor':'#30363d','clusterBkg':'#161b22','clusterBorder':'#30363d','titleColor':'#58a6ff','edgeLabelBackground':'#161b22','nodeTextColor':'#c9d1d9'}}}%%
flowchart LR
    WI[ADO Work Item<br/>New → Spec<br/>Assigned to AI Teammate] -->|1. HTTP POST| Hook[Service<br/>Hook]
    Hook -->|2. JSON| FW{IP Firewall}
    FW -->|✓ Allow| Func[Azure Function<br/>spec-dispatch]
    FW -.->|✗ 403| Block[ ]
    
    Func -->|3. Validate| Func
    Func -->|4. Get Secrets| KV[(Key Vault)]
    Func -->|5. Fetch Details| WI
    Func -->|6. Dispatch| GH[GitHub Actions<br/>spec-kit]
    Func -.->|Log| AI[App Insights]
    
    GH -->|7. Generate| Spec[Specification]
    GH -->|8. Update| WI

    classDef critical fill:#da3633,stroke:#f85149,stroke-width:2px,color:#ffffff
    classDef azure fill:#0078d4,stroke:#005a9e,stroke-width:2px,color:#ffffff
    classDef secret fill:#f0ad4e,stroke:#ec971f,stroke-width:2px,color:#000000
    classDef monitor fill:#28a745,stroke:#1e7e34,stroke-width:2px,color:#ffffff
    classDef hidden fill:none,stroke:none,color:#c9d1d9
    
    class FW critical
    class Func,WI,Hook,GH,Spec azure
    class KV secret
    class AI monitor
    class Block hidden
```

## Data Flow Steps

1. **User Action**: Moves work item to "Specification" column in Azure DevOps and assigns it to AI Teammate
2. **Webhook Trigger**: ADO fires `workitem.updated` event with JSON payload
3. **IP Validation**: Azure Function firewall validates source IP against allowlist
4. **Event Validation**: Function validates:
   - Work item type = Feature
   - Assigned to AI Teammate
   - New column = Specification
5. **Secret Retrieval**: Fetches PATs from Key Vault via Managed Identity
6. **Work Item Fetch**: Gets full work item details from ADO API
7. **Workflow Dispatch**: Triggers GitHub Actions workflow with parameters
8. **Spec Generation**: GitHub Actions runs spec-kit to generate specification
9. **Update ADO**: Updates work item Description field with generated spec
10. **Logging**: All steps logged to Application Insights

## Security Configuration

**IP Allowlist**: Function App uses Azure Firewall with:
- Azure DevOps webhook IP ranges (region-specific, from [Microsoft docs](https://learn.microsoft.com/en-us/azure/devops/organizations/security/allow-list-ip-url?view=azure-devops#inbound-connections))
- Deployment source IPs

**Critical Fix Applied (Oct 28, 2025)**: Changed from `AzureDevOps` service tag (outbound connections) to proper inbound IP ranges for Service Hooks. See Terraform `main.tf` for actual configuration.
