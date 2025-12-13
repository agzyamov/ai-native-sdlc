# API Gateway HTTP API
resource "aws_apigatewayv2_api" "alert_history_api" {
  name          = "ado-alert-history-api"
  protocol_type = "HTTP"
  description   = "API Gateway for querying and exporting ADO process change alert history"

  cors_configuration {
    allow_origins = ["*"] # Configure appropriately for production
    allow_methods = ["GET", "OPTIONS"]
    allow_headers = ["content-type", "x-api-key", "authorization"]
    max_age       = 300
  }

  tags = {
    Name = "Alert History API"
  }
}

# API Gateway Stage
resource "aws_apigatewayv2_stage" "alert_history_api" {
  api_id      = aws_apigatewayv2_api.alert_history_api.id
  name        = var.api_gateway_stage_name
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }

  tags = {
    Name = "Alert History API Stage"
  }
}

# CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/ado-alert-history-api"
  retention_in_days = 30
}

# API Gateway Integration: GET /alerts
resource "aws_apigatewayv2_integration" "query_alerts" {
  api_id           = aws_apigatewayv2_api.alert_history_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.alert_history_api.invoke_arn
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "query_alerts" {
  api_id    = aws_apigatewayv2_api.alert_history_api.id
  route_key = "GET /alerts"
  target    = "integrations/${aws_apigatewayv2_integration.query_alerts.id}"
}

# API Gateway Integration: GET /alerts/export
resource "aws_apigatewayv2_integration" "export_alerts" {
  api_id           = aws_apigatewayv2_api.alert_history_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.alert_history_api.invoke_arn
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "export_alerts" {
  api_id    = aws_apigatewayv2_api.alert_history_api.id
  route_key = "GET /alerts/export"
  target    = "integrations/${aws_apigatewayv2_integration.export_alerts.id}"
}

# Permission for API Gateway to invoke Lambda
resource "aws_lambda_permission" "api_gateway_invoke" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.alert_history_api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.alert_history_api.execution_arn}/*/*"
}

# API Key (optional - for API key authentication)
resource "aws_apigatewayv2_api_key" "alert_history_api_key" {
  name = "ado-alert-history-api-key"
}

# Note: Custom domain requires ACM certificate and Route53 configuration
# For MVP, use the default API Gateway endpoint
# To add custom domain, uncomment and configure:
# resource "aws_apigatewayv2_domain_name" "alert_history_api" {
#   domain_name = "api.yourdomain.com"
#   domain_name_configuration {
#     certificate_arn = aws_acm_certificate.api_cert.arn
#     endpoint_type   = "REGIONAL"
#     security_policy = "TLS_1_2"
#   }
# }
# resource "aws_apigatewayv2_api_mapping" "alert_history_api" {
#   api_id      = aws_apigatewayv2_api.alert_history_api.id
#   domain_name = aws_apigatewayv2_domain_name.alert_history_api.domain_name
#   stage       = aws_apigatewayv2_stage.alert_history_api.id
# }

