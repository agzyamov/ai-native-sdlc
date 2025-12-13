# Dead Letter Queue for failed email sends
resource "aws_sqs_queue" "email_dlq" {
  name                      = "ado-process-alert-email-dlq"
  message_retention_seconds = var.sqs_dlq_retention_days * 24 * 60 * 60 # Convert days to seconds
  visibility_timeout_seconds = 300 # 5 minutes

  tags = {
    Name        = "ADO Process Alert Email DLQ"
    Description = "Dead letter queue for failed email sends"
  }
}

# Queue policy to allow Lambda to send messages
resource "aws_sqs_queue_policy" "email_dlq_policy" {
  queue_url = aws_sqs_queue.email_dlq.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = [
          "sqs:SendMessage"
        ]
        Resource = aws_sqs_queue.email_dlq.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_lambda_function.process_change_monitor.arn
          }
        }
      }
    ]
  })
}

