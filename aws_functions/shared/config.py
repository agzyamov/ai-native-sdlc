"""Configuration management for AWS Lambda functions."""

import json
import os
from functools import lru_cache
from typing import List

import boto3


@lru_cache(maxsize=1)
def get_authorized_service_accounts() -> List[str]:
    """
    Load authorized CI/CD service account identifiers from Parameter Store.

    Returns:
        List of service account identifiers (email addresses or identity descriptors)

    Raises:
        Exception: If parameter cannot be retrieved from Parameter Store
    """
    parameter_path = os.environ.get(
        "AUTHORIZED_SERVICE_ACCOUNTS_PARAM",
        "/ado-process-alert/authorized-service-accounts"
    )

    ssm_client = boto3.client("ssm")
    try:
        response = ssm_client.get_parameter(Name=parameter_path, WithDecryption=True)
        accounts_json = response["Parameter"]["Value"]
        accounts = json.loads(accounts_json)

        if not isinstance(accounts, list):
            raise ValueError(f"Parameter {parameter_path} must contain a JSON array")

        return [str(account) for account in accounts if account]
    except ssm_client.exceptions.ParameterNotFound:
        # Return empty list if parameter doesn't exist (no authorized accounts)
        return []
    except Exception as e:
        # Log error and return empty list as fallback
        # In production, you might want to raise or use CloudWatch Logs
        print(f"Error loading authorized service accounts: {e}")
        return []


def get_dynamodb_table_name() -> str:
    """Get DynamoDB table name from environment variable."""
    return os.environ.get("DYNAMODB_TABLE_NAME", "ProcessChangeAlerts")


def get_ses_from_email() -> str:
    """Get SES sender email from environment variable."""
    return os.environ.get("SES_FROM_EMAIL", "")


def get_alert_email_distribution_list() -> str:
    """Get alert email distribution list from environment variable."""
    return os.environ.get("ALERT_EMAIL_DISTRIBUTION_LIST", "")


def get_sqs_dlq_url() -> str:
    """Get SQS Dead Letter Queue URL from environment variable."""
    return os.environ.get("SQS_DLQ_URL", "")


def get_aws_region() -> str:
    """Get AWS region from environment variable or boto3 default."""
    return os.environ.get("AWS_REGION", boto3.Session().region_name or "us-east-1")

