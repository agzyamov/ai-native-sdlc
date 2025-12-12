# Quickstart Guide: ADO Process Change Alert

**Feature**: ADO Process Change Alert  
**Date**: 2025-12-12  
**Estimated Setup Time**: 2-3 hours

## Prerequisites

1. **AWS Account** with appropriate IAM permissions
2. **Azure Subscription** (for minimal Event Grid bridge)
3. **Azure DevOps Organization** backed by Microsoft Entra ID
4. **Terraform** >= 1.6.0 installed
5. **Python** 3.11 installed
6. **AWS CLI** configured with credentials
7. **Azure CLI** configured (for bridge setup)

## Step 1: Configure AWS Infrastructure

### 1.1 Clone and Navigate

```bash
cd /path/to/ai-native-sdlc
cd infra/terraform
```

### 1.2 Set Terraform Variables

Create `terraform.tfvars`:

```hcl
aws_region = "us-east-1"
ado_organization_name = "your-ado-org"
authorized_service_accounts = [
  "svc-cicd@organization.com",
  "build-agent@organization.com"
]
alert_email_distribution_list = "ops-team@organization.com"
ses_verified_domain = "yourdomain.com"
```

### 1.3 Initialize and Apply

```bash
terraform init
terraform plan
terraform apply
```

This creates:
- EventBridge custom event bus
- Lambda functions
- DynamoDB table
- API Gateway
- IAM roles and policies
- Systems Manager Parameter Store entry

### 1.4 Configure SES

1. Verify your domain in Amazon SES:
   ```bash
   aws ses verify-domain-identity --domain yourdomain.com
   ```
2. Add DNS records to your domain (provided by AWS)
3. Verify sender email:
   ```bash
   aws ses verify-email-identity --email-address alerts@yourdomain.com
   ```

## Step 2: Deploy Lambda Functions

### 2.1 Package Lambda Code

```bash
cd ../../aws_functions/process_change_monitor
zip -r function.zip .
```

### 2.2 Deploy to Lambda

```bash
aws lambda update-function-code \
  --function-name ProcessChangeMonitor \
  --zip-file fileb://function.zip
```

Repeat for `alert_history_api` function.

## Step 3: Configure Azure Event Grid Bridge

### 3.1 Create Azure Event Grid Topic

```bash
az eventgrid topic create \
  --name ado-audit-events \
  --resource-group your-rg \
  --location westeurope
```

### 3.2 Get Event Grid Endpoint and Key

```bash
az eventgrid topic show \
  --name ado-audit-events \
  --resource-group your-rg \
  --query "endpoint" -o tsv

az eventgrid topic key list \
  --name ado-audit-events \
  --resource-group your-rg \
  --query "key1" -o tsv
```

### 3.3 Deploy Bridge Function

Deploy the minimal Azure Function from `infra/azure_bridge/event_grid_webhook.py`:

1. Create Function App:
   ```bash
   az functionapp create \
     --name ado-bridge-function \
     --resource-group your-rg \
     --consumption-plan-location westeurope \
     --runtime python \
     --functions-version 4
   ```

2. Set environment variables:
   ```bash
   az functionapp config appsettings set \
     --name ado-bridge-function \
     --resource-group your-rg \
     --settings \
     EVENTBRIDGE_ENDPOINT=https://events.us-east-1.amazonaws.com \
     EVENTBRIDGE_BUS_NAME=ado-audit-events \
     AWS_REGION=us-east-1
   ```

3. Deploy function code (use Azure Functions Core Tools or VS Code)

### 3.4 Create Event Grid Subscription

Create a subscription that forwards events to the bridge function HTTP endpoint.

## Step 4: Configure Azure DevOps Audit Streaming

### 4.1 Enable Auditing

1. Navigate to Azure DevOps Organization Settings → Auditing
2. Enable auditing if not already enabled
3. Ensure you have "Manage audit streams" permission

### 4.2 Create Audit Stream

1. Go to **Streams** tab → **New stream**
2. Select **Azure Event Grid**
3. Enter Event Grid Topic Endpoint and Access Key (from Step 3.2)
4. Select **Set up**

Events will begin flowing within 30 minutes.

## Step 5: Configure Authorized Service Accounts

### 5.1 Update Parameter Store

```bash
aws ssm put-parameter \
  --name /ado-process-alert/authorized-service-accounts \
  --value '["svc-cicd@org.com","build-agent@org.com"]' \
  --type String \
  --overwrite
```

## Step 6: Test the System

### 6.1 Make a Test Process Change

1. Log into Azure DevOps as a non-CI/CD user
2. Navigate to Organization Settings → Process
3. Make a small change (e.g., add a field to a work item type)
4. Wait up to 5 minutes

### 6.2 Verify Alert Email

Check the operations team email distribution list for an alert email.

### 6.3 Verify No Alert for CI/CD Change

1. Make a change using a CI/CD service account
2. Verify NO alert email is received

### 6.4 Query Alert History

```bash
curl -H "X-API-Key: your-api-key" \
  "https://api.example.com/v1/alerts?startDate=2025-12-01&endDate=2025-12-31"
```

## Step 7: Monitor and Troubleshoot

### 7.1 Check Lambda Logs

```bash
aws logs tail /aws/lambda/ProcessChangeMonitor --follow
```

### 7.2 Check EventBridge Events

```bash
aws events list-rules --event-bus-name ado-audit-events
```

### 7.3 Check DynamoDB Records

```bash
aws dynamodb scan --table-name ProcessChangeAlerts --limit 5
```

### 7.4 Check SES Email Status

```bash
aws ses get-send-statistics
```

## Common Issues

### Issue: No events received in EventBridge

**Solution**: 
- Verify Azure Event Grid subscription is active
- Check bridge function logs for errors
- Verify EventBridge endpoint URL is correct

### Issue: Emails not being sent

**Solution**:
- Verify SES domain/email is verified
- Check Lambda execution logs for SES errors
- Verify email distribution list is correct
- Check SES sending limits (sandbox mode)

### Issue: Alerts sent for CI/CD changes

**Solution**:
- Verify Parameter Store contains correct service account IDs
- Check Lambda logs for parameter retrieval
- Ensure actor IDs match exactly (case-sensitive)

## Next Steps

1. **Set up CloudWatch Alarms** for monitoring (see `plan.md`)
2. **Configure API Gateway API Keys** for operations team access
3. **Set up automated testing** for the alert system
4. **Document runbooks** for operations team

## Rollback

If you need to disable the system:

1. **Disable EventBridge Rule**:
   ```bash
   aws events disable-rule --name ado-process-changes --event-bus-name ado-audit-events
   ```

2. **Disable Lambda Function**:
   ```bash
   aws lambda put-function-concurrency \
     --function-name ProcessChangeMonitor \
     --reserved-concurrent-executions 0
   ```

3. **Disable Azure Event Grid Subscription**: In Azure DevOps audit stream settings

## Support

For issues or questions:
- Check CloudWatch Logs for errors
- Review `plan.md` for architecture details
- Contact operations team

