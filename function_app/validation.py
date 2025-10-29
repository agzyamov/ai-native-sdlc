"""
Validation logic for Azure DevOps Service Hook events.
Determines if a work item event should trigger spec generation.
"""
import os


def validate_event(event: dict) -> tuple[bool, str]:
    """
    Validate if the event should trigger spec generation.
    
    Args:
        event: Raw Service Hook payload (dictionary)
    
    Returns:
        Tuple of (is_valid, reason)
        - (True, "ok") if event passes all validation
        - (False, reason) if validation fails
    
    Validation Rules:
        - eventType must be "workitem.updated"
        - workItemType must be "Feature"
        - assignee display name must match AI_USER_MATCH (case-insensitive)
        - board column must match SPEC_COLUMN_NAME
        - board column done state must be false (Doing, not Done)
    """
    # Check event type
    event_type = event.get("eventType", "")
    if event_type != "workitem.updated":
        return False, f"Invalid event type: {event_type}"
    
    # Extract resource fields - check revision.fields for full work item state
    resource = event.get("resource", {})
    revision = resource.get("revision", {})
    fields = revision.get("fields", {})
    
    # Validate work item type
    work_item_type = fields.get("System.WorkItemType", "")
    if work_item_type != "Feature":
        return False, f"Invalid work item type: {work_item_type} (expected Feature)"
    
    # Validate assignee
    ai_user_match = os.getenv("AI_USER_MATCH", "AI Teammate")
    assignee_raw = fields.get("System.AssignedTo", "")
    assignee_name = ""
    
    # AssignedTo can be string "DisplayName <email>" or dict with displayName
    if isinstance(assignee_raw, dict):
        assignee_name = assignee_raw.get("displayName", "")
    elif isinstance(assignee_raw, str):
        # Extract display name from "DisplayName <email>" format
        assignee_name = assignee_raw.split("<")[0].strip()
    
    if assignee_name.lower() != ai_user_match.lower():
        return False, f"Assignee mismatch: '{assignee_name}' (expected '{ai_user_match}')"
    
    # Validate board column and "Doing" state (not Done)
    # Note: Azure DevOps reports BoardColumn as "Specification" regardless of Doing/Done state
    # We check BoardColumnDone to ensure it's in the "Doing" sub-column
    spec_column = os.getenv("SPEC_COLUMN_NAME", "Specification")
    board_column = fields.get("System.BoardColumn", "")
    board_column_done = fields.get("System.BoardColumnDone", False)
    
    # Strip " – Doing" or " – Done" suffix from expected column name for comparison
    spec_column_base = spec_column.split(" – ")[0].strip()
    
    if board_column != spec_column_base:
        return False, f"Column mismatch: '{board_column}' (expected '{spec_column_base}')"
    
    if board_column_done:
        return False, f"Column state is 'Done' (expected 'Doing' - BoardColumnDone should be false)"
    
    return True, "ok"

