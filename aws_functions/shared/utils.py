"""Common utilities for AWS Lambda functions."""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def setup_logging(correlation_id: str = None) -> logging.Logger:
    """
    Set up structured logging with correlation ID.

    Args:
        correlation_id: Optional correlation ID for request tracing

    Returns:
        Configured logger instance
    """
    if correlation_id:
        logger.addFilter(CorrelationIdFilter(correlation_id))
    return logger


class CorrelationIdFilter(logging.Filter):
    """Logging filter to add correlation ID to log records."""

    def __init__(self, correlation_id: str):
        super().__init__()
        self.correlation_id = correlation_id

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = self.correlation_id
        return True


def format_timestamp_iso8601(timestamp: float) -> str:
    """
    Convert Unix epoch timestamp to ISO 8601 format.

    Args:
        timestamp: Unix epoch timestamp (seconds)

    Returns:
        ISO 8601 formatted string (UTC)
    """
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return dt.isoformat()


def format_timestamp_unix(timestamp: float) -> int:
    """
    Convert timestamp to Unix epoch integer.

    Args:
        timestamp: Unix epoch timestamp (seconds)

    Returns:
        Unix epoch integer
    """
    return int(timestamp)


def calculate_ttl_timestamp(event_timestamp: float, days: int = 90) -> int:
    """
    Calculate DynamoDB TTL timestamp (Unix epoch) for given event timestamp.

    Args:
        event_timestamp: Event timestamp in Unix epoch (seconds)
        days: Number of days until expiration (default: 90)

    Returns:
        TTL timestamp as Unix epoch integer
    """
    seconds_per_day = 86400
    ttl_timestamp = event_timestamp + (days * seconds_per_day)
    return int(ttl_timestamp)


def format_partition_key(timestamp: float) -> str:
    """
    Format partition key as YYYY-MM from Unix epoch timestamp.

    Args:
        timestamp: Unix epoch timestamp (seconds)

    Returns:
        Partition key string in YYYY-MM format
    """
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return dt.strftime("%Y-%m")


def format_sort_key(correlation_id: str, timestamp: float) -> str:
    """
    Format sort key as CorrelationId-Timestamp.

    Args:
        correlation_id: Event correlation ID
        timestamp: Unix epoch timestamp (seconds)

    Returns:
        Sort key string
    """
    return f"{correlation_id}-{int(timestamp)}"


def safe_json_dumps(obj: Any) -> str:
    """
    Safely serialize object to JSON string.

    Args:
        obj: Object to serialize

    Returns:
        JSON string representation

    Raises:
        ValueError: If object cannot be serialized
    """
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to serialize object to JSON: {e}") from e


def create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create standardized error response for API Gateway.

    Args:
        status_code: HTTP status code
        error_code: Application error code
        message: Human-readable error message
        details: Optional additional error details

    Returns:
        Error response dictionary
    """
    response = {
        "error": error_code,
        "message": message
    }
    if details:
        response["details"] = details

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(response)
    }

