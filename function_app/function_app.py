"""
Azure Function: ADO Service Hook → GitHub Workflow Dispatch
Azure Functions v2 Programming Model
"""

import json
import logging
import os
import uuid
from datetime import datetime

import ado_client
import azure.functions as func
import config
import dispatch

# Import function modules - use absolute imports for entry point
import validation

# Configure structured logging with explicit handlers
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

# Log startup
logger.info("Azure Function starting up - spec-dispatch endpoint initialized")

app = func.FunctionApp()


@app.route(route="spec-dispatch", auth_level=func.AuthLevel.ANONYMOUS)
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
        print(
            f"STDOUT: Request received - correlation_id={correlation_id} (logger failed: {log_err})"
        )

    try:
        # Parse request body
        try:
            body = req.get_json()
            logger.info(
                f"[{correlation_id}] Parsed JSON body - eventType={body.get('eventType', 'unknown')}"
            )
        except ValueError as e:
            logger.error(f"[{correlation_id}] Invalid JSON: {e!s}")
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON payload"}),
                status_code=400,
                mimetype="application/json",
            )

        # Extract work item ID
        work_item_id = None
        if "resource" in body and "workItemId" in body["resource"]:
            work_item_id = body["resource"]["workItemId"]

        if not work_item_id:
            logger.warning(
                f"[{correlation_id}] Missing work item ID - body_keys={list(body.keys())}"
            )
            return func.HttpResponse(
                json.dumps({"error": "Missing resource.workItemId in payload"}),
                status_code=400,
                mimetype="application/json",
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
                    mimetype="application/json",
                )
        except Exception as config_err:
            logger.exception(f"[{correlation_id}] Configuration validation failed: {config_err}")
            return func.HttpResponse(
                json.dumps(
                    {
                        "error": "Configuration error",
                        "error_type": type(config_err).__name__,
                        "error_message": str(config_err),
                        "correlation_id": correlation_id,
                    }
                ),
                status_code=500,
                mimetype="application/json",
            )

        # Validate event (uses environment variables directly)
        is_valid, reason = validation.validate_event(body)
        if not is_valid:
            logger.info(f"[{correlation_id}] Validation filtered: {reason}")
            print(f"STDOUT: Validation filtered - work_item_id={work_item_id}, reason={reason}")
            # Return 204 (No Content) instead of 403 to prevent "Failed" status in Azure DevOps
            # The function is working correctly - it's just filtering out events that don't match criteria
            return func.HttpResponse(status_code=204)

        # Extract ChangedBy from revision history (most reliable source for initiator email)
        changed_by_user_id = None

        # Quick initial read from payload revisedBy (no network call)
        resource = body.get("resource", {})
        revised_by = resource.get("revisedBy", {})
        if isinstance(revised_by, dict):
            changed_by_user_id = revised_by.get("uniqueName")

        # Always verify from ADO revision history for accuracy
        try:
            latest_revision = ado_client.get_work_item_latest_revision(work_item_id)
            if latest_revision is not None:
                revision_fields = latest_revision.get("fields", {})
                changed_by = revision_fields.get("System.ChangedBy", {})
                if isinstance(changed_by, dict):
                    revision_changed_by = changed_by.get("uniqueName")
                    if revision_changed_by:
                        changed_by_user_id = revision_changed_by
                        logger.info(
                            f"[{correlation_id}] ChangedBy from revision history: {changed_by_user_id}"
                        )
                    else:
                        logger.warning(
                            f"[{correlation_id}] ChangedBy.uniqueName not found in revision history"
                        )
                else:
                    logger.warning(
                        f"[{correlation_id}] ChangedBy field in revision is not a dict: {type(changed_by)}"
                    )
            else:
                logger.warning(
                    f"[{correlation_id}] ADO API returned None when fetching latest revision"
                )
        except Exception as e:
            logger.warning(
                f"[{correlation_id}] Failed to fetch ChangedBy from revision history (non-fatal): {e!s}"
            )
            print(f"STDOUT WARNING: Failed to fetch ChangedBy from revision history - {e!s}")

        if changed_by_user_id:
            logger.info(f"[{correlation_id}] Dispatching as initiator: {changed_by_user_id}")
        else:
            logger.warning(
                f"[{correlation_id}] changed_by_user_id is None/empty - dispatch will proceed without initiator"
            )
            print("STDOUT WARNING: changed_by_user_id is None/empty")

        # Dispatch workflow
        success, message = dispatch.dispatch_workflow(
            work_item_id=work_item_id, changed_by_user_id=changed_by_user_id
        )

        # Calculate latency
        latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        if success:
            logger.info(
                f"[{correlation_id}] Workflow dispatched successfully for work item {work_item_id} - latency={latency_ms}ms"
            )
            print(f"STDOUT SUCCESS: Dispatched workflow for work item {work_item_id}")
            return func.HttpResponse(status_code=204)
        else:
            logger.error(
                f"[{correlation_id}] Failed to dispatch workflow for work item {work_item_id}: {message} - latency={latency_ms}ms"
            )
            print(f"STDOUT ERROR: Dispatch failed - {message}")
            return func.HttpResponse(
                json.dumps({"error": message}), status_code=500, mimetype="application/json"
            )

    except Exception as e:
        try:
            latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            error_type = type(e).__name__
            error_message = str(e)
            logger.exception(
                f"[{correlation_id}] Unexpected exception: {error_type} - {error_message} - latency={latency_ms}ms"
            )
            print(f"STDOUT EXCEPTION: {error_type} - {error_message}")
        except Exception:
            # Even error logging can fail
            error_type = type(e).__name__
            error_message = str(e)
            print(f"STDOUT EXCEPTION (logging failed): {error_type} - {error_message}")

        # Always return a proper error response, even if logging failed
        try:
            error_response = {
                "error": "Internal server error",
                "error_type": error_type if "error_type" in locals() else "Unknown",
                "error_message": error_message if "error_message" in locals() else str(e),
                "correlation_id": correlation_id,
            }
            return func.HttpResponse(
                json.dumps(error_response), status_code=500, mimetype="application/json"
            )
        except Exception as response_err:
            # Last resort: return minimal error
            print(f"STDOUT: Failed to create error response: {response_err}")
            return func.HttpResponse(f"Internal server error: {e!s}", status_code=500)
