# API Contracts

This directory contains API contracts for the ADO Process Change Alert feature.

## Files

- `alert-history-api.yaml` - OpenAPI 3.0 specification for the alert history query and export API

## API Overview

The Alert History API provides endpoints for:
1. **Querying alerts** - Retrieve alert history with filtering options
2. **Exporting alerts** - Export alert history as CSV or JSON

## Authentication

The API supports two authentication methods:
- **API Key**: Via `X-API-Key` header (for operations team access)
- **IAM**: AWS IAM authentication (for programmatic/automated access)

## Rate Limiting

- **Query Endpoint**: 100 requests per minute per API key
- **Export Endpoint**: 10 requests per minute per API key

## Usage Examples

### Query Alerts

```bash
# Get alerts for December 2025
curl -H "X-API-Key: your-api-key" \
  "https://api.example.com/v1/alerts?startDate=2025-12-01&endDate=2025-12-31"

# Get alerts by specific actor
curl -H "X-API-Key: your-api-key" \
  "https://api.example.com/v1/alerts?actorId=aad|12345-67890"

# Get alerts with pagination
curl -H "X-API-Key: your-api-key" \
  "https://api.example.com/v1/alerts?limit=50&nextToken=eyJ..."
```

### Export Alerts

```bash
# Export as JSON
curl -H "X-API-Key: your-api-key" \
  "https://api.example.com/v1/alerts/export?format=json&startDate=2025-12-01&endDate=2025-12-31" \
  -o alerts.json

# Export as CSV
curl -H "X-API-Key: your-api-key" \
  "https://api.example.com/v1/alerts/export?format=csv&startDate=2025-12-01&endDate=2025-12-31" \
  -o alerts.csv
```

## Implementation

The API is implemented as:
- **API Gateway**: REST API endpoint
- **Lambda Function**: `alert_history_api` handler
- **DynamoDB**: Data source for alert history

See `plan.md` for detailed implementation architecture.

