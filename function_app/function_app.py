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

# Configure structured logging with explicit handlers
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=log_level,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

# Log startup
logger.info("Azure Function starting up - spec-dispatch endpoint initialized")

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
    
    # Log at multiple levels to ensure visibility
    logger.info(f"[{correlation_id}] Request received - method={req.method}")
    print(f"STDOUT: Request received - correlation_id={correlation_id}")  # Force stdout logging
    
    try:
        # Parse request body
        try:
            body = req.get_json()
            logger.info(f"[{correlation_id}] Parsed JSON body - eventType={body.get('eventType', 'unknown')}")
        except ValueError as e:
            logger.error(f"[{correlation_id}] Invalid JSON: {str(e)}")
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
            logger.warning(f"[{correlation_id}] Missing work item ID - body_keys={list(body.keys())}")
            return func.HttpResponse(
                json.dumps({"error": "Missing resource.workItemId in payload"}),
                status_code=400,
                mimetype="application/json"
            )
        
        logger.info(f"[{correlation_id}] Work item ID: {work_item_id}")
        
        # Validate configuration
        cfg = config.get_config()
        config_valid, missing_vars = cfg.validate()
        if not config_valid:
            logger.error(f"[{correlation_id}] Missing configuration: {missing_vars}")
            return func.HttpResponse(
                json.dumps({"error": "Missing required configuration", "missing": missing_vars}),
                status_code=500,
                mimetype="application/json"
            )
        
        # Validate event (uses environment variables directly)
        is_valid, reason = validation.validate_event(body)
        if not is_valid:
            logger.info(f"[{correlation_id}] Validation filtered: {reason}")
            print(f"STDOUT: Validation filtered - work_item_id={work_item_id}, reason={reason}")
            # Return 204 (No Content) instead of 403 to prevent "Failed" status in Azure DevOps
            # The function is working correctly - it's just filtering out events that don't match criteria
            return func.HttpResponse(status_code=204)
        
        # Fetch full work item details from ADO
        try:
            work_item = ado_client.get_work_item(work_item_id)
            
            if work_item is None:
                raise ValueError("ADO API returned None - check credentials and work item ID")
            
            description = work_item.get("fields", {}).get("System.Description", "")
            title = work_item.get("fields", {}).get("System.Title", f"Work Item #{work_item_id}")
            
            # Use Description if available, fallback to Title
            feature_description = description if description else title
            
            logger.info(f"[{correlation_id}] Fetched work item {work_item_id} - has_description={bool(description)}, title={title[:50]}...")
        except Exception as e:
            logger.error(f"[{correlation_id}] Failed to fetch work item {work_item_id}: {str(e)}")
            print(f"STDOUT ERROR: Failed to fetch work item - {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to fetch work item from ADO", "details": str(e)}),
                status_code=500,
                mimetype="application/json"
            )
        
        # Dispatch workflow (uses environment variables directly)
        success, message = dispatch.dispatch_workflow(
            work_item_id=work_item_id,
            description_placeholder=feature_description
        )
        
        # Calculate latency
        latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        if success:
            logger.info(f"[{correlation_id}] Workflow dispatched successfully for work item {work_item_id} - latency={latency_ms}ms")
            print(f"STDOUT SUCCESS: Dispatched workflow for work item {work_item_id}")
            return func.HttpResponse(status_code=204)
        else:
            logger.error(f"[{correlation_id}] Failed to dispatch workflow for work item {work_item_id}: {message} - latency={latency_ms}ms")
            print(f"STDOUT ERROR: Dispatch failed - {message}")
            return func.HttpResponse(
                json.dumps({"error": message}),
                status_code=500,
                mimetype="application/json"
            )
        
    except Exception as e:
        latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        logger.exception(f"[{correlation_id}] Unexpected exception: {type(e).__name__} - {str(e)} - latency={latency_ms}ms")
        print(f"STDOUT EXCEPTION: {type(e).__name__} - {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "correlation_id": correlation_id}),
            status_code=500,
            mimetype="application/json"
        )
