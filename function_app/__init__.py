"""
Azure Function: ADO Service Hook → GitHub Workflow Dispatch
Handles work item update events and triggers spec generation workflow.
"""
import json
import logging
import os
import uuid
from datetime import datetime

import azure.functions as func

from .ado_client import get_work_item
from .config import get_config
from .dispatch import dispatch_workflow
from .models import WorkItemEvent
from .validation import validate_event

# Configure structured logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

app = func.FunctionApp()


@app.route(route="spec-dispatch", auth_level=func.AuthLevel.FUNCTION)
def spec_dispatch(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger for Azure DevOps Service Hook events.
    Validates work item update and dispatches GitHub workflow.
    
    Returns:
        200: Event accepted but not processed (validation failed gracefully)
        204: Successfully dispatched workflow
        400: Malformed request payload
        403: Validation failed (wrong type, assignee, or column)
        500: Internal error
    """
    correlation_id = str(uuid.uuid4())
    start_time = datetime.utcnow()
    
    logger.info(json.dumps({
        "correlation_id": correlation_id,
        "event": "request_received",
        "method": req.method
    }))
    
    try:
        # Parse request body
        try:
            body = req.get_json()
        except ValueError as e:
            logger.error(json.dumps({
                "correlation_id": correlation_id,
                "error": "invalid_json",
                "error_classification": "validation",
                "details": str(e)
            }))
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON payload"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Extract work item ID
        work_item_id = None
        if "resource" in body and "workItemId" in body["resource"]:
            work_item_id = body["resource"]["workItemId"]
        
        if not work_item_id:
            logger.warning(json.dumps({
                "correlation_id": correlation_id,
                "error": "missing_work_item_id",
                "error_classification": "validation",
                "body_keys": list(body.keys())
            }))
            return func.HttpResponse(
                json.dumps({"error": "Missing resource.workItemId in payload"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Validate configuration
        config = get_config()
        config_valid, missing_vars = config.validate()
        if not config_valid:
            logger.error(json.dumps({
                "correlation_id": correlation_id,
                "error": "missing_configuration",
                "error_classification": "validation",
                "missing_vars": missing_vars
            }))
            return func.HttpResponse(
                json.dumps({"error": "Missing required configuration", "missing": missing_vars}),
                status_code=500,
                mimetype="application/json"
            )
        
        # DEBOUNCE INSERTION POINT: Add hash-based duplicate check (deferred - T041)
        # Future: Calculate hash of (work_item_id + column + description_hash)
        # Check cache/storage for recent identical hash within time window
        # If found: return 202 with "debounced" status
        
        # Validate event
        is_valid, reason = validate_event(body)
        if not is_valid:
            logger.info(json.dumps({
                "correlation_id": correlation_id,
                "work_item_id": work_item_id,
                "event": "validation_failed",
                "error_classification": "validation",
                "reason": reason
            }))
            return func.HttpResponse(
                json.dumps({"status": "rejected", "reason": reason}),
                status_code=403,
                mimetype="application/json"
            )
        
        # Derive branch hint
        branch_hint = f"feature/wi-{work_item_id}"
        
        # Extract description placeholder (if available in payload)
        description_placeholder = ""
        fields = body.get("resource", {}).get("fields", {})
        if "System.Title" in fields:
            description_placeholder = fields["System.Title"]
        
        # Dispatch workflow
        success, message = dispatch_workflow(
            work_item_id=work_item_id,
            branch_hint=branch_hint,
            description_placeholder=description_placeholder
        )
        
        # Calculate latency
        latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        if success:
            logger.info(json.dumps({
                "correlation_id": correlation_id,
                "work_item_id": work_item_id,
                "event": "dispatch_success",
                "dispatch_status": "success",
                "latency_ms": latency_ms
            }))
            return func.HttpResponse(
                json.dumps({
                    "status": "dispatched",
                    "correlation_id": correlation_id,
                    "work_item_id": work_item_id,
                    "latency_ms": latency_ms
                }),
                status_code=204,
                mimetype="application/json"
            )
        else:
            logger.error(json.dumps({
                "correlation_id": correlation_id,
                "work_item_id": work_item_id,
                "event": "dispatch_failed",
                "error_classification": "transport",
                "dispatch_status": "failed",
                "message": message,
                "latency_ms": latency_ms
            }))
            return func.HttpResponse(
                json.dumps({
                    "status": "failed",
                    "correlation_id": correlation_id,
                    "error": message
                }),
                status_code=500,
                mimetype="application/json"
            )
        
    except Exception as e:
        latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        logger.exception(json.dumps({
            "correlation_id": correlation_id,
            "error": "unexpected_exception",
            "error_classification": "transport",
            "exception_type": type(e).__name__,
            "latency_ms": latency_ms
        }))
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "correlation_id": correlation_id}),
            status_code=500,
            mimetype="application/json"
        )

