"""
Azure Function: ADO Service Hook → GitHub Workflow Dispatch
Azure Functions v2 Programming Model
"""
import json
import logging
import os
import uuid
from datetime import datetime

import azure.functions as func

# Import function modules - use absolute imports for entry point
import validation
import dispatch
import config
import util
import ado_client

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
        204: Successfully dispatched workflow
        400: Malformed request payload
        403: Validation failed (wrong type, assignee, or column)
        500: Internal error or dispatch failure
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
        cfg = config.get_config()
        config_valid, missing_vars = cfg.validate()
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
        
        # Validate event (uses environment variables directly)
        is_valid, reason = validation.validate_event(body)
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
        
        # Fetch full work item details from ADO
        try:
            work_item = ado_client.get_work_item(work_item_id)
            
            if work_item is None:
                raise ValueError("ADO API returned None - check credentials and work item ID")
            
            description = work_item.get("fields", {}).get("System.Description", "")
            title = work_item.get("fields", {}).get("System.Title", f"Work Item #{work_item_id}")
            
            # Use Description if available, fallback to Title
            feature_description = description if description else title
            
            logger.info(json.dumps({
                "correlation_id": correlation_id,
                "work_item_id": work_item_id,
                "event": "fetched_work_item",
                "has_description": bool(description),
                "title": title[:100]  # Log first 100 chars
            }))
        except Exception as e:
            logger.error(json.dumps({
                "correlation_id": correlation_id,
                "work_item_id": work_item_id,
                "error": "failed_to_fetch_work_item",
                "error_classification": "transport",
                "details": str(e)
            }))
            return func.HttpResponse(
                json.dumps({"error": "Failed to fetch work item from ADO", "details": str(e)}),
                status_code=500,
                mimetype="application/json"
            )
        
        # Derive branch hint
        branch_hint = f"feature/wi-{work_item_id}"
        
        # Dispatch workflow (uses environment variables directly)
        success, message = dispatch.dispatch_workflow(
            work_item_id=work_item_id,
            branch_hint=branch_hint,
            description_placeholder=feature_description
        )
        
        # Calculate latency
        latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        if success:
            logger.info(json.dumps({
                "correlation_id": correlation_id,
                "work_item_id": work_item_id,
                "event": "dispatch_success",
                "latency_ms": latency_ms
            }))
            return func.HttpResponse(status_code=204)
        else:
            logger.error(json.dumps({
                "correlation_id": correlation_id,
                "work_item_id": work_item_id,
                "event": "dispatch_failed",
                "error_classification": "transport",
                "message": message,
                "latency_ms": latency_ms
            }))
            return func.HttpResponse(
                json.dumps({"error": message}),
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
