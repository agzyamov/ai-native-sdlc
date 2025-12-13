# Lambda function: ProcessChangeMonitor
resource "aws_lambda_function" "process_change_monitor" {
  filename         = "${path.module}/../../aws_functions/process_change_monitor.zip"
  function_name    = "ado-process-change-monitor"
  role             = aws_iam_role.process_change_monitor.arn
  handler          = "handler.lambda_handler"
  source_code_hash = filebase64sha256("${path.module}/../../aws_functions/process_change_monitor.zip")
  runtime          = "python3.11"
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory_size

  environment {
    variables = {
      AUTHORIZED_SERVICE_ACCOUNTS_PARAM = "/ado-process-alert/authorized-service-accounts"
      SES_FROM_EMAIL                    = var.ses_from_email
      ALERT_EMAIL_DISTRIBUTION_LIST     = var.alert_email_distribution_list
      DYNAMODB_TABLE_NAME               = aws_dynamodb_table.alert_history.name
      SQS_DLQ_URL                       = aws_sqs_queue.email_dlq.url
      AWS_REGION                        = var.aws_region
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.process_change_monitor,
    aws_iam_role_policy.process_change_monitor
  ]

  tags = {
    Name = "ProcessChangeMonitor Lambda"
  }
}

# Lambda function: AlertHistoryAPI
resource "aws_lambda_function" "alert_history_api" {
  filename         = "${path.module}/../../aws_functions/alert_history_api.zip"
  function_name    = "ado-alert-history-api"
  role             = aws_iam_role.alert_history_api.arn
  handler          = "handler.lambda_handler"
  source_code_hash = filebase64sha256("${path.module}/../../aws_functions/alert_history_api.zip")
  runtime          = "python3.11"
  timeout          = 30 # API should be fast
  memory_size      = 256

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.alert_history.name
      AWS_REGION          = var.aws_region
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.alert_history_api,
    aws_iam_role_policy.alert_history_api
  ]

  tags = {
    Name = "AlertHistoryAPI Lambda"
  }
}

# Note: Lambda deployment packages (.zip files) must be created before running terraform apply
# Use the deployment script (T049) or manually zip the function directories

