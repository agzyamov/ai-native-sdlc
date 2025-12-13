# IAM Role for ProcessChangeMonitor Lambda
resource "aws_iam_role" "process_change_monitor" {
  name = "ado-process-change-monitor-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "ProcessChangeMonitor Lambda Role"
  }
}

# IAM Policy for ProcessChangeMonitor Lambda
resource "aws_iam_role_policy" "process_change_monitor" {
  name = "ado-process-change-monitor-policy"
  role = aws_iam_role.process_change_monitor.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/ado-process-change-monitor*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]
        Resource = aws_dynamodb_table.alert_history.arn
      },
      {
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "ses:FromAddress" = var.ses_from_email
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Resource = "arn:aws:ssm:${var.aws_region}:*:parameter/ado-process-alert/*"
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage"
        ]
        Resource = aws_sqs_queue.email_dlq.arn
      }
    ]
  })
}

# IAM Role for AlertHistoryAPI Lambda
resource "aws_iam_role" "alert_history_api" {
  name = "ado-alert-history-api-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "AlertHistoryAPI Lambda Role"
  }
}

# IAM Policy for AlertHistoryAPI Lambda
resource "aws_iam_role_policy" "alert_history_api" {
  name = "ado-alert-history-api-policy"
  role = aws_iam_role.alert_history_api.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/ado-alert-history-api*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.alert_history.arn,
          "${aws_dynamodb_table.alert_history.arn}/index/*"
        ]
      }
    ]
  })
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "process_change_monitor" {
  name              = "/aws/lambda/ado-process-change-monitor"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "alert_history_api" {
  name              = "/aws/lambda/ado-alert-history-api"
  retention_in_days = 30
}

