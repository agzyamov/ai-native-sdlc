# Implementation Plan: ADO Process Change Alert

**Branch**: `005-ado-process-change-alert` | **Date**: 2025-12-12 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/005-ado-process-change-alert/spec.md`

## Summary

Implement a serverless AWS-based monitoring system that detects Azure DevOps process template changes and alerts the operations team via email when unauthorized manual changes occur. The solution uses Azure Event Grid as a bridge from Azure DevOps audit streaming, then processes events through AWS EventBridge, Lambda, and Amazon SES, with alert history stored in DynamoDB.

**Technical Approach**: Event-driven serverless architecture using AWS Lambda for processing, Amazon SES for email delivery, and DynamoDB for history storage. Minimal Azure footprint (only Event Grid bridge).

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: boto3 (AWS SDK), python-dateutil  
**Storage**: Amazon DynamoDB (alert history), AWS Systems Manager Parameter Store (configuration)  
**Testing**: pytest, moto (AWS mocking), pytest-cov  
**Target Platform**: AWS Lambda (serverless Linux runtime)  
**Project Type**: single (serverless functions + infrastructure)  
**Performance Goals**: Process events within 1 second, deliver emails within 30 seconds, total alert time <5 minutes  
**Constraints**: 15-minute Lambda timeout, 512MB memory limit, 90-day DynamoDB TTL for automatic cleanup  
**Scale/Scope**: ~100-1000 process change events/month, <10 alerts/month, operations team of 5-10 users

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Azure DevOps (Production Organization)                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Audit Log                                     │   │
│  │  (Captures all Process.* events: Field, State, Rule changes, etc.)  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Audit Stream (Azure Event Grid)                   │   │
│  │  Streams audit events to Azure Event Grid every ≤30 minutes          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Azure Event Grid Topic (Bridge)                          │
│                                                                             │
│  - Receives audit events from Azure DevOps                                  │
│  - Forwards to AWS EventBridge via HTTP webhook                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AWS EventBridge (Custom Event Bus)                       │
│                                                                             │
│  - Receives events from Azure Event Grid webhook                            │
│  - Routes Process.* events to Lambda function                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AWS Lambda (ProcessChangeMonitor)                        │
│                                                                             │
│  1. Filter: Only Process.* area events                                      │
│  2. Exclude: Changes by authorized CI/CD service accounts                   │
│  3. Enrich: Add human-readable descriptions                                 │
│  4. Store: Log to DynamoDB for history                                     │
│  5. Send: Email via Amazon SES                                              │
│  6. Retry: Failed emails → SQS DLQ for retry                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
┌──────────────────────────────────┐  ┌──────────────────────────────────┐
│         Amazon SES                │  │      Amazon DynamoDB              │
│                                   │  │                                   │
│  Sends email alerts to            │  │  Stores alert history with      │
│  operations team distribution     │  │  90-day TTL for auto-cleanup     │
│  list                             │  │                                   │
└──────────────────────────────────┘  └──────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Operations Team Email Distribution List                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: ✅ PASSED

- **Single Project Structure**: All components are serverless functions within one codebase
- **Test-First Development**: Unit tests with moto for AWS service mocking
- **Simplicity**: Serverless architecture, no infrastructure management
- **Observability**: CloudWatch Logs for Lambda, DynamoDB metrics for storage

## Project Structure

### Documentation (this feature)

```text
specs/005-ado-process-change-alert/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
aws_functions/
├── process_change_monitor/
│   ├── __init__.py
│   ├── handler.py              # Lambda handler for EventBridge events
│   ├── event_filter.py          # Filter Process.* events
│   ├── cicd_filter.py          # Exclude authorized CI/CD accounts
│   ├── email_service.py         # SES email sending
│   ├── history_service.py       # DynamoDB operations
│   └── models.py                # Data models
│
├── alert_history_api/
│   ├── __init__.py
│   ├── handler.py              # API Gateway Lambda handler
│   ├── query_service.py         # DynamoDB query operations
│   └── export_service.py        # CSV/JSON export
│
└── shared/
    ├── __init__.py
    ├── config.py                # Configuration from Parameter Store
    └── utils.py                 # Common utilities

tests/
├── unit/
│   ├── test_event_filter.py
│   ├── test_cicd_filter.py
│   ├── test_email_service.py
│   └── test_history_service.py
│
├── integration/
│   ├── test_end_to_end.py      # Full event flow test
│   └── test_api_endpoints.py
│
└── fixtures/
    └── sample_audit_events.json

infra/
├── terraform/
│   ├── main.tf                 # AWS provider configuration
│   ├── eventbridge.tf          # EventBridge custom bus
│   ├── lambda.tf               # Lambda functions
│   ├── dynamodb.tf             # DynamoDB table
│   ├── ses.tf                  # SES configuration
│   ├── api_gateway.tf          # API Gateway for history
│   ├── iam.tf                  # IAM roles and policies
│   ├── variables.tf
│   └── outputs.tf
│
└── azure_bridge/
    └── event_grid_webhook.py   # Minimal Azure Function to forward to AWS
```

**Structure Decision**: Single project structure with AWS Lambda functions organized by feature. Infrastructure as Code via Terraform. Minimal Azure bridge function (separate directory) to forward Event Grid events to AWS.

## Component Design

### Component 1: Azure Event Grid Bridge (Minimal Azure)

**Purpose**: Receive audit events from Azure DevOps and forward to AWS EventBridge.

**Implementation**: Small Azure Function (HTTP trigger) that:
1. Receives Event Grid webhook
2. Validates event signature
3. Forwards to AWS EventBridge HTTP API endpoint
4. Returns 200 OK to Event Grid

**Location**: `infra/azure_bridge/event_grid_webhook.py`

**Dependencies**: Minimal - only needs HTTP client to call AWS EventBridge API

### Component 2: AWS EventBridge Custom Event Bus

**Purpose**: Receive events from Azure bridge and route to Lambda.

**Configuration**:
- Custom event bus: `ado-audit-events`
- Event pattern: Match events with `source = "azure.devops"` and `detail-type = "Process Change"`
- Target: Lambda function `ProcessChangeMonitor`

**Terraform Resource**:
```hcl
resource "aws_cloudwatch_event_bus" "ado_audit" {
  name = "ado-audit-events"
}

resource "aws_cloudwatch_event_rule" "process_changes" {
  name           = "ado-process-changes"
  event_bus_name = aws_cloudwatch_event_bus.ado_audit.name
  event_pattern  = jsonencode({
    source      = ["azure.devops"]
    detail-type = ["Process Change"]
  })
}

resource "aws_cloudwatch_event_target" "lambda" {
  rule      = aws_cloudwatch_event_rule.process_changes.name
  target_id = "ProcessChangeMonitor"
  arn       = aws_lambda_function.process_change_monitor.arn
}
```

### Component 3: AWS Lambda (ProcessChangeMonitor)

**Purpose**: Filter process change events, exclude CI/CD accounts, store history, send alerts.

**Runtime**: Python 3.11

**Trigger**: EventBridge rule

**Key Logic**:

```python
# Event filtering - only process change events
PROCESS_EVENT_PREFIXES = [
    "Process.Field.",
    "Process.State.",
    "Process.Rule.",
    "Process.Process.",
    "Process.WorkItemType.",
    "Process.Control.",
    "Process.Page.",
    "Process.Group.",
    "Process.Behavior.",
    "Process.List.",
]

def is_process_change_event(event_data: dict) -> bool:
    """Check if event is a process template change."""
    action = event_data.get("action", "")
    area = event_data.get("area", "")
    return area == "Process" or any(action.startswith(prefix) for prefix in PROCESS_EVENT_PREFIXES)

# CI/CD service account exclusion
def is_authorized_cicd_account(actor_id: str, config: dict) -> bool:
    """Check if actor is an authorized CI/CD service account."""
    authorized_accounts = config.get("authorized_service_accounts", [])
    return actor_id in authorized_accounts
```

**Environment Variables**:
- `AUTHORIZED_SERVICE_ACCOUNTS_PARAM`: Parameter Store path for authorized accounts
- `SES_FROM_EMAIL`: Verified SES email address
- `ALERT_EMAIL_DISTRIBUTION_LIST`: Email distribution list
- `DYNAMODB_TABLE_NAME`: DynamoDB table name
- `SQS_DLQ_URL`: Dead letter queue URL for failed emails

**Files**: `aws_functions/process_change_monitor/`

### Component 4: Amazon DynamoDB

**Purpose**: Persist alert history for 90+ days, enable querying and export.

**Table Schema** (`ProcessChangeAlerts`):

| Attribute | Type | Description |
|-----------|------|-------------|
| `PartitionKey` | String | YYYY-MM (for efficient date range queries) |
| `SortKey` | String | Event correlation ID + timestamp |
| `Timestamp` | Number | DynamoDB-managed timestamp |
| `EventTimestamp` | Number | When the change occurred in ADO (Unix epoch) |
| `ActorId` | String | Who made the change |
| `ActorDisplayName` | String | Human-readable actor name |
| `ActorIP` | String | IP address of actor |
| `Action` | String | The specific action (e.g., Process.Field.Add) |
| `Details` | String | Human-readable change description |
| `ProcessName` | String | Affected process template name |
| `WorkItemType` | String | Affected work item type (if applicable) |
| `AlertSent` | Boolean | Whether email alert was sent |
| `AlertSentTimestamp` | Number | When alert was sent (Unix epoch) |
| `TTL` | Number | Time-to-live for automatic deletion (90 days) |
| `RawEventJson` | String | Full event payload for audit |

**Global Secondary Index**: `EventTimestamp-index` for date range queries

**Terraform Resource**:
```hcl
resource "aws_dynamodb_table" "alert_history" {
  name           = "ProcessChangeAlerts"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "PartitionKey"
  range_key      = "SortKey"

  attribute {
    name = "PartitionKey"
    type = "S"
  }

  attribute {
    name = "SortKey"
    type = "S"
  }

  attribute {
    name = "EventTimestamp"
    type = "N"
  }

  global_secondary_index {
    name     = "EventTimestamp-index"
    hash_key = "PartitionKey"
    range_key = "EventTimestamp"
  }

  ttl {
    attribute_name = "TTL"
    enabled        = true
  }
}
```

### Component 5: Amazon SES

**Purpose**: Send email alerts to operations team.

**Configuration**:
- Verified sender email address (from domain)
- Verified recipient email addresses or distribution list
- Email template with change details

**Email Template**:
```
Subject: ⚠️ ADO Process Change Alert: {Action} by {ActorDisplayName}

Body:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AZURE DEVOPS PROCESS CHANGE DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A manual change to the Production ADO process template has been detected.
This change was NOT made through the authorized CI/CD pipeline.

CHANGE DETAILS:
• Action: {Action}
• Process: {ProcessName}
• Work Item Type: {WorkItemType}
• Description: {Details}

WHO MADE THE CHANGE:
• User: {ActorDisplayName}
• IP Address: {ActorIP}
• Timestamp: {EventTimestamp} UTC

WHAT TO DO:
1. Verify if this change was authorized
2. If unauthorized, investigate and remediate
3. Consider reverting the change if it violates policy

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated alert from the ADO Process Change Monitor.
Alert ID: {CorrelationId}
```

### Component 6: Amazon SQS Dead Letter Queue

**Purpose**: Queue failed email sends for retry.

**Configuration**:
- Standard queue (not FIFO - order not critical)
- Visibility timeout: 5 minutes
- Message retention: 14 days
- Lambda function triggered from DLQ for retry

### Component 7: AWS Systems Manager Parameter Store

**Purpose**: Store authorized CI/CD service account identifiers.

**Parameter Path**: `/ado-process-alert/authorized-service-accounts`

**Format**: JSON array of account identifiers:
```json
["svc-cicd@org.com", "build-agent@org.com"]
```

**Encryption**: AWS managed key (SSM Parameter Store encryption)

### Component 8: API Gateway + Lambda (Alert History API)

**Purpose**: Provide HTTP API for querying and exporting alert history.

**Endpoints**:
- `GET /alerts` - Query alerts with date range filter
- `GET /alerts/export` - Export alerts as CSV/JSON

**Authentication**: API Key or IAM authentication

**Files**: `aws_functions/alert_history_api/`

## Implementation Tasks

### Phase 1: Infrastructure Setup (P1)

| Task | Description | Est. Hours |
|------|-------------|------------|
| 1.1 | Create Terraform for EventBridge custom bus | 2 |
| 1.2 | Create Terraform for DynamoDB table | 2 |
| 1.3 | Create Terraform for Lambda functions | 3 |
| 1.4 | Create Terraform for SES configuration | 1 |
| 1.5 | Create Terraform for API Gateway | 2 |
| 1.6 | Create Terraform for IAM roles and policies | 2 |
| 1.7 | Create minimal Azure Function bridge | 3 |

### Phase 2: Lambda Function Development (P1)

| Task | Description | Est. Hours |
|------|-------------|------------|
| 2.1 | Create `process_change_monitor/handler.py` with EventBridge trigger | 4 |
| 2.2 | Implement process change event filtering | 2 |
| 2.3 | Implement CI/CD service account exclusion | 2 |
| 2.4 | Create `history_service.py` for DynamoDB operations | 3 |
| 2.5 | Create `email_service.py` for SES integration | 3 |
| 2.6 | Implement SQS DLQ retry logic | 2 |
| 2.7 | Add unit tests with moto | 4 |
| 2.8 | Add integration tests | 3 |

### Phase 3: Alert History API (P3)

| Task | Description | Est. Hours |
|------|-------------|------------|
| 3.1 | Create `alert_history_api/handler.py` | 3 |
| 3.2 | Implement DynamoDB query with date filtering | 2 |
| 3.3 | Implement CSV/JSON export | 2 |
| 3.4 | Add API Gateway integration | 2 |
| 3.5 | Add tests | 2 |

### Phase 4: Azure DevOps Configuration (P1)

| Task | Description | Est. Hours |
|------|-------------|------------|
| 4.1 | Enable auditing in Production ADO organization | 0.5 |
| 4.2 | Create and configure audit stream to Azure Event Grid | 1 |
| 4.3 | Configure Event Grid subscription to forward to AWS | 1 |
| 4.4 | Document authorized CI/CD service accounts | 1 |

### Total Estimated Effort: ~45 hours

## Configuration Requirements

### AWS Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AUTHORIZED_SERVICE_ACCOUNTS_PARAM` | Parameter Store path | `/ado-process-alert/authorized-service-accounts` |
| `SES_FROM_EMAIL` | Verified SES email | `alerts@yourdomain.com` |
| `ALERT_EMAIL_DISTRIBUTION_LIST` | Distribution list | `ops-team@yourdomain.com` |
| `DYNAMODB_TABLE_NAME` | DynamoDB table name | `ProcessChangeAlerts` |
| `SQS_DLQ_URL` | Dead letter queue URL | `https://sqs.us-east-1.amazonaws.com/...` |

### Terraform Variables

```hcl
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "ado_organization_name" {
  description = "Name of the Production Azure DevOps organization"
  type        = string
}

variable "authorized_service_accounts" {
  description = "List of CI/CD service account identifiers to exclude from alerting"
  type        = list(string)
  default     = []
}

variable "alert_email_distribution_list" {
  description = "Email address/distribution list for alerts"
  type        = string
}

variable "ses_verified_domain" {
  description = "Verified SES domain for sending emails"
  type        = string
}
```

## Security Considerations

1. **IAM Roles**: Lambda uses IAM roles with least privilege (no hardcoded credentials)
2. **Parameter Store**: Encrypted at rest, access via IAM policies
3. **API Gateway**: IAM authentication or API keys for history API
4. **DynamoDB**: Encryption at rest enabled by default
5. **SES**: Requires verified email addresses/domains
6. **EventBridge**: Resource-based policies for custom event bus
7. **Azure Event Grid**: Shared access key stored in AWS Secrets Manager

## Monitoring & Alerting

1. **Lambda Failures**: CloudWatch Alarms on Lambda errors
2. **Email Delivery Failures**: CloudWatch Alarms on SQS DLQ message count
3. **DynamoDB Throttling**: CloudWatch Alarms on consumed read/write capacity
4. **EventBridge Dead Letters**: Monitor for undeliverable events
5. **API Gateway Errors**: CloudWatch Alarms on 5xx errors

## Testing Strategy

### Unit Tests
- Event filtering logic
- Service account exclusion
- Email payload formatting
- DynamoDB operations (using moto)

### Integration Tests
- EventBridge → Lambda → SES flow
- EventBridge → Lambda → DynamoDB flow
- API Gateway → Lambda → DynamoDB flow
- SQS DLQ retry mechanism

### Manual Acceptance Testing
1. Make a manual process change in ADO test organization
2. Verify alert email received within 5 minutes
3. Make a change via CI/CD service account
4. Verify NO alert is generated
5. Query alert history API and verify records
6. Export alert history and verify format

## Rollback Plan

1. **Disable EventBridge Rule**: Stop routing events to Lambda
2. **Disable Lambda Function**: Set reserved concurrency to 0
3. **Disable Azure Event Grid Subscription**: In Azure DevOps audit stream settings
4. **Archive DynamoDB Table**: Export data before deletion if needed

## Dependencies

- AWS Account with appropriate IAM permissions
- Azure subscription for Event Grid bridge (minimal cost)
- Azure DevOps organization backed by Microsoft Entra ID
- SES verified domain for email sending
- Terraform >= 1.6.0
- Python 3.11 for Lambda development

## References

- [AWS EventBridge Custom Event Bus](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-event-bus.html)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Amazon SES Documentation](https://docs.aws.amazon.com/ses/)
- [Amazon DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [Azure DevOps Audit Streaming](https://learn.microsoft.com/en-us/azure/devops/organizations/audit/auditing-streaming)
