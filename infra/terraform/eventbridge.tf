# Custom Event Bus for ADO audit events
resource "aws_cloudwatch_event_bus" "ado_audit" {
  name = "ado-audit-events"

  tags = {
    Name        = "ADO Audit Events Bus"
    Description = "Receives audit events from Azure DevOps via Event Grid bridge"
  }
}

# Event Rule to match Process.* events
resource "aws_cloudwatch_event_rule" "process_changes" {
  name           = "ado-process-changes"
  event_bus_name = aws_cloudwatch_event_bus.ado_audit.name
  description    = "Matches Azure DevOps process template change events"

  event_pattern = jsonencode({
    source      = ["azure.devops"]
    detail-type = ["Process Change"]
  })

  tags = {
    Name = "ADO Process Changes Rule"
  }
}

# EventBridge Target: Lambda function
resource "aws_cloudwatch_event_target" "process_change_monitor" {
  rule      = aws_cloudwatch_event_rule.process_changes.name
  target_id = "ProcessChangeMonitor"
  arn       = aws_lambda_function.process_change_monitor.arn
  event_bus_name = aws_cloudwatch_event_bus.ado_audit.name
}

# Permission for EventBridge to invoke Lambda
resource "aws_lambda_permission" "eventbridge_invoke" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.process_change_monitor.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.process_changes.arn
}

# Resource-based policy for EventBridge custom bus (allows Azure Event Grid to send events)
resource "aws_cloudwatch_event_bus_policy" "ado_audit_policy" {
  event_bus_name = aws_cloudwatch_event_bus.ado_audit.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowAzureEventGrid"
        Effect = "Allow"
        Principal = {
          AWS = "*" # In production, restrict to specific Azure Event Grid service principal
        }
        Action = [
          "events:PutEvents"
        ]
        Resource = aws_cloudwatch_event_bus.ado_audit.arn
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}

data "aws_caller_identity" "current" {}

