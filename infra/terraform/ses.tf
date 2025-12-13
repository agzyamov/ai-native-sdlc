# SES Domain Identity (must be verified manually via DNS)
resource "aws_ses_domain_identity" "alert_domain" {
  domain = var.ses_verified_domain
}

# SES Email Identity (must be verified manually)
resource "aws_ses_email_identity" "alert_sender" {
  email = var.ses_from_email
}

# Configuration set for email tracking (optional)
resource "aws_ses_configuration_set" "alert_config" {
  name = "ado-process-alert-config"
}

# Event destination for bounce/complaint tracking (optional)
resource "aws_ses_event_destination" "cloudwatch" {
  name                   = "cloudwatch-destination"
  configuration_set_name = aws_ses_configuration_set.alert_config.name
  enabled                = true
  matching_types         = ["bounce", "complaint"]

  cloudwatch_destination {
    default_value  = "default"
    dimension_name = "MessageTag"
    value_source   = "messageTag"
  }
}

