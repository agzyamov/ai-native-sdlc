# Data Flow (Specification Automation)

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#0d1117','primaryTextColor':'#c9d1d9','primaryBorderColor':'#30363d','lineColor':'#58a6ff','secondaryColor':'#161b22','tertiaryColor':'#21262d','background':'#0d1117','mainBkg':'#161b22','secondBkg':'#21262d','tertiaryBorderColor':'#30363d','clusterBkg':'#161b22','clusterBorder':'#30363d','titleColor':'#58a6ff','edgeLabelBackground':'#161b22','nodeTextColor':'#c9d1d9'}}}%%
flowchart TB
    %% Trigger Phase
    WI[ADO Work Item<br/>Move to Spec] -->|webhook| Hook[Service Hook]
    Hook -->|POST| FW{IP Firewall}
    FW -.->|403| Deny[ ]
    FW -->|allow| Func[Azure Function]
    
    %% Azure Phase
    Func -->|validate| Func
    Func -->|secrets| KV[(Key Vault)]
    Func -->|details| WI
    Func -->|dispatch| GH[GitHub Actions]
    Func -.->|log| AI[App Insights]
    
    %% Generation Phase
    GH -->|run| Copilot[Copilot CLI]
    Copilot -->|output| Detect{Questions?}
    
    %% Question Path
    Detect -->|yes| Extract[Extract via<br/>GitHub Models API]
    Extract -->|create child| Issues[ADO Issues]
    Issues -->|link to| WI
    Extract -->|save| SpecQ["spec.md<br/>[NEEDS CLARIFICATION]"]
    SpecQ -->|commit| Repo[Git Repository]
    
    %% Normal Path
    Detect -->|no| SpecN[spec.md]
    SpecN -->|commit| Repo
    SpecN -->|update| WI
    
    %% Styling
    classDef critical fill:#da3633,stroke:#f85149,stroke-width:2px,color:#fff
    classDef azure fill:#0078d4,stroke:#005a9e,stroke-width:2px,color:#fff
    classDef secret fill:#f0ad4e,stroke:#ec971f,stroke-width:2px,color:#000
    classDef monitor fill:#28a745,stroke:#1e7e34,stroke-width:2px,color:#fff
    classDef llm fill:#9370db,stroke:#7b68ee,stroke-width:2px,color:#fff
    classDef hidden fill:none,stroke:none
    
    class FW critical
    class Func,Hook,GH,Copilot,Issues,Repo,WI,SpecN,SpecQ azure
    class KV secret
    class AI monitor
    class Detect,Extract llm
    class Deny hidden
```

## Flow Phases

### 1. Trigger Phase
- **User moves** work item to "Specification" column in ADO
- **Service Hook** fires `workitem.updated` webhook
- **IP Firewall** validates source IP (deny 403 if not allowlisted)
- **Azure Function** receives validated event

### 2. Azure Phase
- **Validate event**: Check work item type, assignment, column transition
- **Fetch secrets**: Get PATs from Key Vault (Managed Identity)
- **Fetch details**: Get full work item data from ADO API
- **Dispatch workflow**: Trigger GitHub Actions with parameters
- **Log telemetry**: Send metrics to Application Insights

### 3. Generation Phase
- **Copilot CLI** generates specification from feature description
- **LLM Detection**: GitHub Models API analyzes output for questions

### 4. Branching Logic

**If Copilot asked questions:**
1. Extract questions via GitHub Models API (GPT-4o)
2. Create **ADO Issue** work items as children of parent Feature
3. Link Issues to parent Feature work item
4. Save spec with `[NEEDS CLARIFICATION:]` markers
5. Commit to repository
6. **Skip** ADO Description update

**If no questions:**
1. Save clean `spec.md`
2. Commit to repository
3. **Update** ADO work item Description with spec

## Security Configuration

**IP Allowlist**: Function App uses Azure Firewall with:
- Azure DevOps webhook IP ranges (region-specific, from [Microsoft docs](https://learn.microsoft.com/en-us/azure/devops/organizations/security/allow-list-ip-url?view=azure-devops#inbound-connections))
- Deployment source IPs

**Critical Fix Applied (Oct 28, 2025)**: Changed from `AzureDevOps` service tag (outbound connections) to proper inbound IP ranges for Service Hooks. See Terraform `main.tf` for actual configuration.
