"""
Azure Function to bridge Azure Event Grid events to AWS EventBridge.

This minimal Azure Function receives audit events from Azure DevOps via Event Grid
and forwards them to AWS EventBridge for processing.
"""

import json
import os
import logging
from typing import Dict, Any
import azure.functions as func
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS EventBridge configuration from environment variables
EVENTBRIDGE_ENDPOINT = os.environ.get("EVENTBRIDGE_ENDPOINT", "https://events.us-east-1.amazonaws.com")
EVENTBRIDGE_BUS_NAME = os.environ.get("EVENTBRIDGE_BUS_NAME", "ado-audit-events")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# AWS credentials (should use Managed Identity or Key Vault in production)
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")


def transform_to_eventbridge(event_grid_event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform Azure Event Grid event to AWS EventBridge format.

    Args:
        event_grid_event: Azure Event Grid event dictionary

    Returns:
        AWS EventBridge event dictionary
    """
    # Extract audit event data
    audit_event = event_grid_event.get("data", {})

    # Transform to EventBridge format
    eventbridge_event = {
        "Source": "azure.devops",
        "DetailType": "Process Change",
        "Detail": json.dumps(audit_event),
        "EventBusName": EVENTBRIDGE_BUS_NAME
    }

    return eventbridge_event


def send_to_eventbridge(event: Dict[str, Any]) -> bool:
    """
    Send event to AWS EventBridge using HTTP API.

    Args:
        event: EventBridge-formatted event dictionary

    Returns:
        True if successful, False otherwise
    """
    import hmac
    import hashlib
    from datetime import datetime
    from urllib.parse import quote

    # AWS Signature Version 4 signing
    # Note: In production, use AWS SDK or boto3 with proper credentials
    # This is a simplified version for demonstration

    try:
        # For production, use AWS SDK or proper signature signing
        # Here we use a simple HTTP POST (requires proper IAM authentication)
        url = f"{EVENTBRIDGE_ENDPOINT}/events"
        headers = {
            "Content-Type": "application/x-amz-json-1.1",
            "X-Amz-Target": "AWSEvents.PutEvents"
        }

        # Prepare request payload
        payload = {
            "Entries": [event]
        }

        # In production, add AWS Signature Version 4 authentication
        # For now, this requires AWS credentials configured in environment
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            auth=(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) if AWS_ACCESS_KEY_ID else None,
            timeout=10
        )

        response.raise_for_status()
        logger.info(f"Successfully sent event to EventBridge: {response.status_code}")
        return True

    except Exception as e:
        logger.error(f"Failed to send event to EventBridge: {e}")
        return False


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger for Event Grid webhook.

    Args:
        req: HTTP request from Event Grid

    Returns:
        HTTP response
    """
    try:
        # Validate Event Grid subscription validation request
        if req.method == "GET" or (req.method == "POST" and "validationCode" in req.get_json()):
            validation_code = req.params.get("validationCode") or req.get_json().get("validationCode")
            if validation_code:
                logger.info("Event Grid subscription validation")
                return func.HttpResponse(
                    validation_code,
                    status_code=200,
                    mimetype="text/plain"
                )

        # Process Event Grid events
        events = req.get_json()

        # Handle both single event and array of events
        if not isinstance(events, list):
            events = [events]

        success_count = 0
        for event_grid_event in events:
            # Transform to EventBridge format
            eventbridge_event = transform_to_eventbridge(event_grid_event)

            # Send to AWS EventBridge
            if send_to_eventbridge(eventbridge_event):
                success_count += 1

        logger.info(f"Processed {success_count}/{len(events)} events successfully")

        return func.HttpResponse(
            json.dumps({"status": "success", "processed": success_count}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logger.error(f"Error processing Event Grid webhook: {e}")
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

