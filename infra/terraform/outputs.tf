output "eventbridge_bus_name" {
  description = "Name of the EventBridge custom event bus"
  value       = aws_cloudwatch_event_bus.ado_audit.name
}

output "eventbridge_bus_arn" {
  description = "ARN of the EventBridge custom event bus"
  value       = aws_cloudwatch_event_bus.ado_audit.arn
}

output "process_change_monitor_lambda_arn" {
  description = "ARN of the ProcessChangeMonitor Lambda function"
  value       = aws_lambda_function.process_change_monitor.arn
}

output "process_change_monitor_lambda_name" {
  description = "Name of the ProcessChangeMonitor Lambda function"
  value       = aws_lambda_function.process_change_monitor.function_name
}

output "alert_history_api_lambda_arn" {
  description = "ARN of the AlertHistoryAPI Lambda function"
  value       = aws_lambda_function.alert_history_api.arn
}

output "alert_history_api_lambda_name" {
  description = "Name of the AlertHistoryAPI Lambda function"
  value       = aws_lambda_function.alert_history_api.function_name
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table for alert history"
  value       = aws_dynamodb_table.alert_history.name
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table"
  value       = aws_dynamodb_table.alert_history.arn
}

output "sqs_dlq_url" {
  description = "URL of the SQS Dead Letter Queue"
  value       = aws_sqs_queue.email_dlq.url
}

output "sqs_dlq_arn" {
  description = "ARN of the SQS Dead Letter Queue"
  value       = aws_sqs_queue.email_dlq.arn
}

output "api_gateway_endpoint" {
  description = "API Gateway HTTP API endpoint URL"
  value       = aws_apigatewayv2_api.alert_history_api.api_endpoint
}

output "api_gateway_id" {
  description = "API Gateway HTTP API ID"
  value       = aws_apigatewayv2_api.alert_history_api.id
}

output "parameter_store_path" {
  description = "Parameter Store path for authorized service accounts"
  value       = "/ado-process-alert/authorized-service-accounts"
}

