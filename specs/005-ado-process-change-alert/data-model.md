# Data Model: ADO Process Change Alert

**Feature**: ADO Process Change Alert  
**Date**: 2025-12-12  
**Storage**: Amazon DynamoDB

## Entities

### ProcessChangeEvent

Represents a detected modification to an Azure DevOps process template.

**Storage**: DynamoDB table `ProcessChangeAlerts`

| Attribute | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `PartitionKey` | String | Yes | YYYY-MM format for date partitioning | `2025-12` |
| `SortKey` | String | Yes | Correlation ID + timestamp for uniqueness | `abc123-1702387200` |
| `Timestamp` | Number | Auto | DynamoDB managed timestamp | `1702387200000` |
| `EventTimestamp` | Number | Yes | When change occurred in ADO (Unix epoch) | `1702387200` |
| `ActorId` | String | Yes | Identity descriptor of who made the change | `aad|12345-67890` |
| `ActorDisplayName` | String | Yes | Human-readable actor name | `John Doe` |
| `ActorIP` | String | Yes | IP address of actor | `192.168.1.1` |
| `Action` | String | Yes | The specific audit action | `Process.Field.Add` |
| `Area` | String | Yes | Product area (always "Process") | `Process` |
| `Category` | String | Yes | Action category (Create/Modify/Delete) | `Create` |
| `Details` | String | Yes | Human-readable change description | `Field "CustomField" created on work item type "User Story"` |
| `ProcessName` | String | No | Affected process template name | `Agile` |
| `WorkItemType` | String | No | Affected work item type (if applicable) | `User Story` |
| `FieldReferenceName` | String | No | Affected field reference name (if applicable) | `Custom.CustomField` |
| `StateName` | String | No | Affected state name (if applicable) | `In Progress` |
| `CorrelationId` | String | Yes | Links related events together | `corr-abc123` |
| `AlertSent` | Boolean | Yes | Whether email alert was sent | `true` |
| `AlertSentTimestamp` | Number | No | When alert was sent (Unix epoch) | `1702387250` |
| `AlertFailed` | Boolean | No | Whether alert sending failed | `false` |
| `RetryCount` | Number | No | Number of retry attempts for failed alerts | `0` |
| `TTL` | Number | Yes | Time-to-live for automatic deletion (90 days) | `1733923200` |
| `RawEventJson` | String | Yes | Full event payload as JSON string | `{"id":"...","actor":{...}}` |

**Partition Key Strategy**: 
- `PartitionKey = YYYY-MM` enables efficient date range queries
- Allows querying all alerts for a specific month
- Supports 90-day retention via TTL

**Sort Key Strategy**:
- `SortKey = {CorrelationId}-{EventTimestamp}` ensures uniqueness
- Enables querying by correlation ID for related events
- Chronological ordering within partition

**Global Secondary Index**: `EventTimestamp-index`
- Hash Key: `PartitionKey`
- Range Key: `EventTimestamp`
- Purpose: Efficient date range queries across partitions

**Validation Rules**:
- `EventTimestamp` must be valid Unix epoch timestamp
- `ActorId` must not be empty
- `Action` must start with `Process.` prefix
- `TTL` must be > current timestamp (future date)
- `AlertSent` must be boolean

**State Transitions**:
- `AlertSent: false` → `AlertSent: true` (when email sent successfully)
- `AlertFailed: false` → `AlertFailed: true` (when email send fails)
- `RetryCount: N` → `RetryCount: N+1` (on retry attempt)

---

### Alert

A notification generated and sent to the operations team, linked to one or more ProcessChangeEvents.

**Storage**: DynamoDB table `ProcessChangeAlerts` (same table as ProcessChangeEvent)

**Note**: Alert is not a separate entity - it's represented by ProcessChangeEvent records where `AlertSent = true`. The email delivery status is tracked within the ProcessChangeEvent record.

**Relationships**:
- One ProcessChangeEvent → One Alert (1:1)
- Alert is created when ProcessChangeEvent is processed and email is sent

---

### AuthorizedServiceAccount

An identity registered as an authorized CI/CD actor, whose changes are excluded from alerting.

**Storage**: AWS Systems Manager Parameter Store

**Parameter Path**: `/ado-process-alert/authorized-service-accounts`

**Format**: JSON array of strings

**Example**:
```json
[
  "svc-cicd@organization.com",
  "build-agent@organization.com",
  "aad|12345-67890-abcdef"
]
```

**Validation Rules**:
- Must be non-empty array
- Each element must be a non-empty string
- Supports email addresses and Azure AD identity descriptors
- Maximum 100 accounts (reasonable limit)

**Access**: Read-only by Lambda function via IAM policy

---

### AlertHistoryQuery

Represents a query request for alert history.

**Storage**: Not persisted - used in API requests

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `startDate` | String | No | ISO 8601 date (YYYY-MM-DD) | `2025-12-01` |
| `endDate` | String | No | ISO 8601 date (YYYY-MM-DD) | `2025-12-31` |
| `actorId` | String | No | Filter by actor ID | `aad|12345` |
| `action` | String | No | Filter by action type | `Process.Field.Add` |
| `limit` | Number | No | Maximum results (default: 100) | `50` |
| `format` | String | No | Export format: `json` or `csv` | `json` |

**Validation Rules**:
- `startDate` must be <= `endDate`
- `limit` must be between 1 and 1000
- `format` must be `json` or `csv`
- Date range cannot exceed 90 days (TTL limit)

---

## Relationships

```
AuthorizedServiceAccount (Parameter Store)
    │
    │ (excludes from alerting)
    │
    ▼
ProcessChangeEvent (DynamoDB)
    │
    │ (generates)
    │
    ▼
Alert (Email via SES)
    │
    │ (stored as)
    │
    ▼
ProcessChangeEvent with AlertSent=true
```

## Data Flow

1. **Event Ingestion**: Azure DevOps audit event → EventBridge → Lambda
2. **Event Processing**: Lambda filters, checks authorized accounts, enriches
3. **Storage**: Lambda writes ProcessChangeEvent to DynamoDB
4. **Alert Generation**: Lambda sends email via SES, updates `AlertSent=true`
5. **History Query**: API Gateway → Lambda → DynamoDB query → Response

## Retention Policy

- **TTL**: 90 days from `EventTimestamp` (automatic deletion)
- **Rationale**: Meets FR-005 requirement for 90-day minimum retention
- **Cleanup**: DynamoDB automatically deletes records when TTL expires
- **Export**: Users can export data before TTL expiration via API

## Indexes

### Primary Index
- **Hash Key**: `PartitionKey` (YYYY-MM)
- **Range Key**: `SortKey` (CorrelationId-Timestamp)

### Global Secondary Index: `EventTimestamp-index`
- **Hash Key**: `PartitionKey` (YYYY-MM)
- **Range Key**: `EventTimestamp` (Unix epoch)
- **Purpose**: Efficient date range queries
- **Projection**: All attributes (KEYS_ONLY would require additional queries)

## Access Patterns

1. **Write Alert**: Insert ProcessChangeEvent with PartitionKey=YYYY-MM, SortKey=CorrelationId-Timestamp
2. **Query by Date Range**: Query EventTimestamp-index with PartitionKey=YYYY-MM, EventTimestamp BETWEEN start AND end
3. **Query by Correlation ID**: Query primary index with PartitionKey=YYYY-MM, SortKey BEGINS_WITH CorrelationId
4. **Query by Actor**: Scan with filter on ActorId (less efficient, but acceptable for low volume)

## Constraints

- **DynamoDB Item Size**: Max 400KB (RawEventJson must be < 400KB)
- **Partition Key Cardinality**: 12 partitions per year (one per month)
- **Query Limits**: 1MB result limit per query (pagination required for large date ranges)
- **TTL Precision**: DynamoDB TTL deletion happens within 48 hours of expiration

