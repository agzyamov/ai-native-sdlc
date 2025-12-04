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
    try:
        logger.info(f"[{correlation_id}] Request received - method={req.method}")
        print(f"STDOUT: Request received - correlation_id={correlation_id}")  # Force stdout logging
    except Exception as log_err:
        # Even logging can fail, so use print as fallback
        print(f"STDOUT: Request received - correlation_id={correlation_id} (logger failed: {log_err})")
    
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
        try:
            cfg = config.get_config()
            config_valid, missing_vars = cfg.validate()
            if not config_valid:
                logger.error(f"[{correlation_id}] Missing configuration: {missing_vars}")
                # Check if it's a Key Vault reference issue
                pat = os.getenv("GH_WORKFLOW_DISPATCH_PAT", "")
                if pat and pat.startswith("@Microsoft.KeyVault"):
                    error_msg = "Key Vault secret not accessible - GH_WORKFLOW_DISPATCH_PAT reference unresolved. Check function managed identity has 'Key Vault Secrets User' role."
                else:
                    error_msg = f"Missing required configuration: {', '.join(missing_vars)}"
                return func.HttpResponse(
                    json.dumps({"error": error_msg, "missing": missing_vars}),
                    status_code=500,
                    mimetype="application/json"
                )
        except Exception as config_err:
            logger.exception(f"[{correlation_id}] Configuration validation failed: {config_err}")
            return func.HttpResponse(
                json.dumps({
                    "error": "Configuration error",
                    "error_type": type(config_err).__name__,
                    "error_message": str(config_err),
                    "correlation_id": correlation_id
                }),
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
        
        # Extract work item details from payload (primary source) or fetch from ADO (fallback)
        # Note: Payload already contains all needed data, so ADO fetch is optional
        description = ""
        title = f"Work Item #{work_item_id}"
        
        # First, try to extract from payload (most reliable, no network call needed)
        resource = body.get("resource", {})
        revision = resource.get("revision", {})
        fields = revision.get("fields", {})
        
        if fields:
            description = fields.get("System.Description", "")
            title = fields.get("System.Title", title)
            logger.info(f"[{correlation_id}] Using payload data - has_description={bool(description)}, title={title[:50]}...")
        else:
            # Fallback: try to fetch from ADO API (may fail due to expired PAT or network issues)
            logger.info(f"[{correlation_id}] Payload missing revision.fields, attempting ADO API fetch")
            try:
                work_item = ado_client.get_work_item(work_item_id)
                
                if work_item is not None:
                    description = work_item.get("fields", {}).get("System.Description", "")
                    title = work_item.get("fields", {}).get("System.Title", title)
                    logger.info(f"[{correlation_id}] Fetched work item {work_item_id} from ADO - has_description={bool(description)}, title={title[:50]}...")
                else:
                    logger.warning(f"[{correlation_id}] ADO API returned None (may be expired PAT or network issue) - using defaults")
            except Exception as e:
                # ADO fetch failed (likely expired PAT or network issue) - log but continue with defaults
                logger.warning(f"[{correlation_id}] ADO API fetch failed (non-fatal): {str(e)} - using defaults")
                print(f"STDOUT WARNING: ADO fetch failed but continuing - {str(e)}")
        
        # Use Description if available, fallback to Title
        feature_description = description if description else title
        
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
        try:
            latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            error_type = type(e).__name__
            error_message = str(e)
            logger.exception(f"[{correlation_id}] Unexpected exception: {error_type} - {error_message} - latency={latency_ms}ms")
            print(f"STDOUT EXCEPTION: {error_type} - {error_message}")
        except Exception as log_err:
            # Even error logging can fail
            error_type = type(e).__name__
            error_message = str(e)
            print(f"STDOUT EXCEPTION (logging failed): {error_type} - {error_message}")
        
        # Always return a proper error response, even if logging failed
        try:
            error_response = {
                "error": "Internal server error",
                "error_type": error_type if 'error_type' in locals() else "Unknown",
                "error_message": error_message if 'error_message' in locals() else str(e),
                "correlation_id": correlation_id
            }
            return func.HttpResponse(
                json.dumps(error_response),
                status_code=500,
                mimetype="application/json"
            )
        except Exception as response_err:
            # Last resort: return minimal error
            print(f"STDOUT: Failed to create error response: {response_err}")
            return func.HttpResponse(
                f"Internal server error: {str(e)}",
                status_code=500
            )
