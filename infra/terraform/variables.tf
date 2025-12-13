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

variable "ses_from_email" {
  description = "Verified SES email address for sending alerts"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 900 # 15 minutes
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 512
}

variable "dynamodb_ttl_days" {
  description = "DynamoDB TTL in days for automatic cleanup"
  type        = number
  default     = 90
}

variable "sqs_dlq_retention_days" {
  description = "SQS Dead Letter Queue message retention in days"
  type        = number
  default     = 14
}

variable "api_gateway_stage_name" {
  description = "API Gateway stage name"
  type        = string
  default     = "v1"
}

