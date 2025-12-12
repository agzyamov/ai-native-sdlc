# Research: ADO Process Change Alert - AWS Implementation

**Date**: 2025-12-12  
**Feature**: ADO Process Change Alert  
**Research Phase**: Phase 0

## Research Questions & Findings

### Q1: How to bridge Azure DevOps audit streaming to AWS?

**Decision**: Use Azure Event Grid as a bridge, then forward events to AWS EventBridge via HTTP API.

**Rationale**: 
- Azure DevOps audit streaming natively supports Azure Event Grid (no other AWS-native options)
- AWS EventBridge supports custom event buses with HTTP API endpoints
- Minimal Azure footprint (only Event Grid subscription)
- Standard HTTP integration pattern

**Alternatives Considered**:
1. **Splunk → AWS**: Would require Splunk infrastructure, more complex
2. **Azure Monitor Logs → AWS**: Requires log export/API polling, higher latency
3. **Direct Azure DevOps API polling**: Not real-time, violates 5-minute SLA

**Reference**: [Azure DevOps Audit Streaming](https://learn.microsoft.com/en-us/azure/devops/organizations/audit/auditing-streaming)

---

### Q2: Which AWS service for event processing?

**Decision**: AWS Lambda with EventBridge as trigger source.

**Rationale**:
- Serverless, no infrastructure management
- EventBridge provides event routing and filtering
- Lambda supports Python 3.11 (consistent with existing codebase)
- Pay-per-use pricing model
- Native integration with other AWS services

**Alternatives Considered**:
1. **Amazon ECS/Fargate**: Overkill for event processing, requires container management
2. **AWS Step Functions**: Adds complexity for simple filtering logic
3. **Amazon Kinesis Data Analytics**: More suited for streaming analytics, not filtering

**Reference**: [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)

---

### Q3: Which AWS service for email delivery?

**Decision**: Amazon Simple Email Service (SES).

**Rationale**:
- Fully managed email service
- Supports distribution lists and email templates
- Cost-effective ($0.10 per 1,000 emails)
- High deliverability rates
- Simple API integration from Lambda

**Alternatives Considered**:
1. **Amazon SNS → Email**: Requires SNS topic setup, less control over email formatting
2. **Amazon Pinpoint**: Overkill for simple email alerts, more marketing-focused
3. **Third-party (SendGrid)**: Adds external dependency, additional cost

**Reference**: [Amazon SES Documentation](https://docs.aws.amazon.com/ses/)

---

### Q4: Which AWS service for alert history storage?

**Decision**: Amazon DynamoDB with Time-to-Live (TTL) for automatic cleanup.

**Rationale**:
- Serverless NoSQL database, no infrastructure management
- TTL feature automatically deletes records after 90 days (meets FR-005)
- Fast query performance for date range filtering (FR-007)
- Supports JSON export for compliance (FR-008)
- Cost-effective for low-volume alert storage

**Alternatives Considered**:
1. **Amazon S3**: Better for large files, overkill for structured alert records
2. **Amazon RDS**: Requires database management, more expensive for low volume
3. **Amazon Timestream**: Optimized for time-series, but adds complexity

**Reference**: [Amazon DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)

---

### Q5: How to handle event queuing if email service is unavailable?

**Decision**: Use Amazon SQS Dead Letter Queue (DLQ) + retry logic in Lambda.

**Rationale**:
- EventBridge → Lambda → SES: If SES fails, Lambda can catch exception
- Store failed events in SQS DLQ for retry
- Lambda can be triggered from DLQ to retry email sending
- Meets FR-006 requirement for queuing

**Alternatives Considered**:
1. **Amazon EventBridge Archive**: Stores events but doesn't provide retry mechanism
2. **DynamoDB for queuing**: Not designed for queue semantics, inefficient
3. **External queue service**: Adds complexity and external dependency

**Reference**: [AWS Lambda Error Handling](https://docs.aws.amazon.com/lambda/latest/dg/invocation-retries.html)

---

### Q6: How to configure authorized CI/CD service accounts?

**Decision**: Store authorized service account identifiers in AWS Systems Manager Parameter Store.

**Rationale**:
- Secure, encrypted parameter storage
- Easy to update without code changes
- Lambda can read parameters at runtime
- Supports versioning and audit trail
- No additional cost for small parameter sets

**Alternatives Considered**:
1. **DynamoDB configuration table**: Works but adds unnecessary database calls
2. **Environment variables in Lambda**: Harder to update, requires redeployment
3. **AWS Secrets Manager**: Overkill for non-secret configuration data

**Reference**: [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)

---

### Q7: How to provide alert history query/export API?

**Decision**: AWS Lambda HTTP API (API Gateway) for querying DynamoDB.

**Rationale**:
- Serverless API, no infrastructure management
- API Gateway provides authentication/authorization
- Lambda can query DynamoDB and return JSON/CSV
- Meets FR-007 and FR-008 requirements
- Cost-effective for low-volume queries

**Alternatives Considered**:
1. **Amazon QuickSight**: Overkill for simple query interface
2. **AWS AppSync**: GraphQL adds complexity for simple queries
3. **Direct DynamoDB console access**: Not suitable for operations team

**Reference**: [Amazon API Gateway Best Practices](https://docs.aws.amazon.com/apigateway/latest/developerguide/best-practices.html)

---

## Technology Stack Summary

| Component | AWS Service | Rationale |
|-----------|------------|-----------|
| **Event Ingestion** | EventBridge (Custom Event Bus) | Receives events from Azure Event Grid bridge |
| **Event Processing** | AWS Lambda (Python 3.11) | Filters process changes, excludes CI/CD accounts |
| **Email Delivery** | Amazon SES | Sends alerts to operations team |
| **History Storage** | Amazon DynamoDB | Stores alert history with 90-day TTL |
| **Configuration** | Systems Manager Parameter Store | Stores authorized CI/CD account list |
| **Error Handling** | Amazon SQS (DLQ) | Queues failed email sends for retry |
| **History API** | API Gateway + Lambda | Provides query/export interface |

## Architecture Pattern

**Event-Driven Serverless Architecture**:
- Azure DevOps → Azure Event Grid → AWS EventBridge → Lambda → SES/DynamoDB
- All processing is serverless, event-driven
- No long-running services or infrastructure to manage
- Scales automatically with event volume

## Security Considerations

1. **IAM Roles**: Lambda uses IAM roles (no hardcoded credentials)
2. **Parameter Store**: Encrypted at rest, access via IAM policies
3. **API Gateway**: Can use IAM authentication or API keys
4. **DynamoDB**: Encryption at rest enabled by default
5. **SES**: Requires verified email addresses/domains

## Cost Estimation

- **EventBridge**: $1.00 per million events (likely <$1/month)
- **Lambda**: $0.20 per million requests + compute time (likely <$5/month)
- **SES**: $0.10 per 1,000 emails (likely <$1/month)
- **DynamoDB**: Free tier covers 25GB storage + 25 RCU/WCU (likely free)
- **API Gateway**: $3.50 per million API calls (likely <$1/month)
- **Parameter Store**: Free for standard parameters

**Estimated Monthly Cost**: <$10/month for typical usage

## Performance Targets

- **Event Processing Latency**: <1 second (Lambda execution)
- **Email Delivery**: <30 seconds (SES SLA)
- **Total Alert Time**: <5 minutes (meets SC-001)
- **API Query Response**: <500ms (DynamoDB query)

## Dependencies

1. **Azure Event Grid**: Must be configured in Azure DevOps organization
2. **AWS Account**: With appropriate IAM permissions
3. **SES Verified Domain**: For email sending
4. **Python 3.11**: For Lambda function development

