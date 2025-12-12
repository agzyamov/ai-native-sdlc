# Architecture Diagram: ADO Process Change Alert

## System Overview

:::mermaid
flowchart TB
    subgraph ADO["Azure DevOps (Production)"]
        AuditLog["📋 Audit Log<br/>Process.* Events"]
        AuditStream["📤 Audit Stream<br/>(Event Grid Target)"]
    end

    subgraph Azure["Azure (Minimal Bridge)"]
        EventGrid["⚡ Event Grid Topic<br/>ado-audit-events"]
        BridgeFunc["⚙️ Bridge Function<br/>(HTTP Trigger)"]
    end

    subgraph AWS["AWS Cloud"]
        subgraph EventProcessing["Event Processing Layer"]
            EventBridge["📨 EventBridge<br/>Custom Event Bus"]
            ProcessRule["📜 Event Rule<br/>Process.* Filter"]
        end

        subgraph Compute["Compute Layer"]
            MonitorLambda["λ ProcessChangeMonitor<br/>Python 3.11"]
            HistoryLambda["λ AlertHistoryAPI<br/>Python 3.11"]
        end

        subgraph Storage["Storage Layer"]
            DynamoDB[("🗄️ DynamoDB<br/>ProcessChangeAlerts")]
            ParamStore["🔐 Parameter Store<br/>Authorized Accounts"]
            SecretsManager["🔑 Secrets Manager<br/>API Keys"]
        end

        subgraph Messaging["Messaging Layer"]
            SES["📧 Amazon SES<br/>Email Service"]
            SQS["📬 SQS DLQ<br/>Failed Emails"]
        end

        subgraph API["API Layer"]
            APIGateway["🌐 API Gateway<br/>REST API"]
        end
    end

    subgraph External["External"]
        OpsTeam["👥 Operations Team<br/>Email Distribution"]
    end

    %% Flow connections
    AuditLog -->|"Process changes"| AuditStream
    AuditStream -->|"≤30 min batch"| EventGrid
    EventGrid -->|"HTTP webhook"| BridgeFunc
    BridgeFunc -->|"Forward events"| EventBridge
    EventBridge --> ProcessRule
    ProcessRule -->|"Trigger"| MonitorLambda

    %% Lambda connections
    MonitorLambda -->|"Read config"| ParamStore
    MonitorLambda -->|"Store alert"| DynamoDB
    MonitorLambda -->|"Send email"| SES
    MonitorLambda -->|"Failed emails"| SQS
    SQS -->|"Retry"| MonitorLambda

    SES -->|"Alert email"| OpsTeam

    %% API connections
    APIGateway --> HistoryLambda
    HistoryLambda -->|"Query"| DynamoDB
    HistoryLambda -->|"Auth"| SecretsManager

    OpsTeam -.->|"Query history"| APIGateway

    %% Styling
    classDef azure fill:#0078D4,color:#fff,stroke:#005A9E
    classDef aws fill:#FF9900,color:#000,stroke:#CC7A00
    classDef ado fill:#0078D4,color:#fff,stroke:#005A9E
    classDef external fill:#6B7280,color:#fff,stroke:#4B5563

    class AuditLog,AuditStream ado
    class EventGrid,BridgeFunc azure
    class EventBridge,ProcessRule,MonitorLambda,HistoryLambda,DynamoDB,ParamStore,SecretsManager,SES,SQS,APIGateway aws
    class OpsTeam external
:::

## Data Flow Sequence

:::mermaid
sequenceDiagram
    participant ADO as Azure DevOps
    participant EG as Event Grid
    participant Bridge as Bridge Function
    participant EB as EventBridge
    participant Lambda as ProcessChangeMonitor
    participant PS as Parameter Store
    participant DB as DynamoDB
    participant SES as Amazon SES
    participant Ops as Operations Team

    Note over ADO,Ops: Process Change Detection Flow

    ADO->>EG: Audit event (≤30 min batch)
    EG->>Bridge: HTTP webhook
    Bridge->>EB: Forward to custom bus
    EB->>Lambda: Trigger on Process.* events

    Lambda->>PS: Get authorized accounts
    PS-->>Lambda: Return account list

    alt Is CI/CD Account
        Lambda->>Lambda: Skip alerting
        Lambda->>DB: Store event (AlertSent=false)
    else Is Manual Change
        Lambda->>DB: Store event
        Lambda->>SES: Send alert email
        SES->>Ops: Deliver email
        Lambda->>DB: Update AlertSent=true
    end

    Note over ADO,Ops: Alert History Query Flow

    Ops->>Lambda: GET /alerts?startDate=...
    Lambda->>DB: Query by date range
    DB-->>Lambda: Return alerts
    Lambda-->>Ops: JSON response
:::

## Component Details

:::mermaid
flowchart LR
    subgraph Lambda1["ProcessChangeMonitor Lambda"]
        direction TB
        Handler["handler.py<br/>EventBridge trigger"]
        Filter["event_filter.py<br/>Process.* filtering"]
        CICD["cicd_filter.py<br/>Account exclusion"]
        Email["email_service.py<br/>SES integration"]
        History["history_service.py<br/>DynamoDB ops"]

        Handler --> Filter
        Filter --> CICD
        CICD --> Email
        CICD --> History
    end

    subgraph Lambda2["AlertHistoryAPI Lambda"]
        direction TB
        APIHandler["handler.py<br/>API Gateway trigger"]
        Query["query_service.py<br/>DynamoDB queries"]
        Export["export_service.py<br/>CSV/JSON export"]

        APIHandler --> Query
        APIHandler --> Export
    end

    subgraph Shared["Shared Module"]
        Config["config.py<br/>Parameter Store"]
        Utils["utils.py<br/>Common utilities"]
    end

    Lambda1 --> Shared
    Lambda2 --> Shared
:::

## Infrastructure (Terraform)

:::mermaid
flowchart TB
    subgraph TF["Terraform Modules"]
        direction LR
        Main["main.tf<br/>AWS Provider"]
        EB["eventbridge.tf<br/>Custom Bus + Rules"]
        LM["lambda.tf<br/>Functions + IAM"]
        DB["dynamodb.tf<br/>Table + GSI"]
        SE["ses.tf<br/>Domain + Templates"]
        AG["api_gateway.tf<br/>REST API"]
        IA["iam.tf<br/>Roles + Policies"]
    end

    subgraph Resources["AWS Resources Created"]
        R1["EventBridge Bus"]
        R2["EventBridge Rule"]
        R3["Lambda Functions (2)"]
        R4["DynamoDB Table"]
        R5["SES Domain"]
        R6["API Gateway"]
        R7["IAM Roles"]
        R8["Parameter Store"]
        R9["SQS Dead Letter Queue"]
    end

    Main --> EB & LM & DB & SE & AG & IA
    EB --> R1 & R2
    LM --> R3
    DB --> R4
    SE --> R5
    AG --> R6
    IA --> R7 & R8 & R9
:::

## Event Flow States

:::mermaid
stateDiagram-v2
    [*] --> EventReceived: ADO audit event

    EventReceived --> Filtering: Parse event
    
    Filtering --> Excluded: Not Process.* event
    Filtering --> ProcessEvent: Is Process.* event

    ProcessEvent --> CheckAccount: Load authorized accounts
    
    CheckAccount --> CICDChange: Is authorized CI/CD
    CheckAccount --> ManualChange: Is manual change

    CICDChange --> StoreOnly: Store without alert
    ManualChange --> SendAlert: Trigger email

    SendAlert --> EmailSuccess: SES success
    SendAlert --> EmailFailed: SES error

    EmailFailed --> DLQ: Queue for retry
    DLQ --> SendAlert: Retry

    EmailSuccess --> StoreWithAlert: Update AlertSent=true
    StoreOnly --> [*]
    StoreWithAlert --> [*]
    Excluded --> [*]
:::

## DynamoDB Table Design

:::mermaid
erDiagram
    ProcessChangeAlerts {
        string PartitionKey PK "YYYY-MM"
        string SortKey SK "CorrelationId-Timestamp"
        number EventTimestamp "When change occurred"
        string ActorId "Who made change"
        string ActorDisplayName "Human-readable name"
        string ActorIP "IP address"
        string Action "e.g. Process.Field.Add"
        string Details "Change description"
        string ProcessName "Affected process"
        string WorkItemType "Affected WIT"
        boolean AlertSent "Email sent?"
        number TTL "Auto-delete after 90 days"
        string RawEventJson "Full event payload"
    }

    GSI_EventTimestamp {
        string PartitionKey PK "YYYY-MM"
        number EventTimestamp RK "Unix epoch"
    }

    ProcessChangeAlerts ||--o{ GSI_EventTimestamp : "indexed by"
:::

## Security Model

:::mermaid
flowchart TB
    subgraph IAM["IAM Roles"]
        LambdaRole["Lambda Execution Role"]
        APIGWRole["API Gateway Role"]
    end

    subgraph Permissions["Permissions"]
        P1["dynamodb:PutItem<br/>dynamodb:Query"]
        P2["ses:SendEmail"]
        P3["ssm:GetParameter"]
        P4["sqs:SendMessage<br/>sqs:ReceiveMessage"]
        P5["logs:CreateLogGroup<br/>logs:PutLogEvents"]
    end

    subgraph Resources["Protected Resources"]
        DDB["DynamoDB Table"]
        SESv["SES Verified Domain"]
        PSv["Parameter Store"]
        SQSv["SQS Queue"]
        CW["CloudWatch Logs"]
    end

    LambdaRole --> P1 & P2 & P3 & P4 & P5
    P1 --> DDB
    P2 --> SESv
    P3 --> PSv
    P4 --> SQSv
    P5 --> CW

    APIGWRole --> P1
:::

---

## Usage in Azure DevOps Wiki

To use these diagrams in Azure DevOps Wiki:

1. Copy the diagram section (including `:::mermaid` and `:::` markers)
2. Paste directly into your wiki page
3. The diagrams will render automatically

**Note**: Azure DevOps Wiki uses the `:::mermaid` fence syntax instead of standard markdown code fences.

