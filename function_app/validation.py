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
    
    # Extract resource fields
    resource = event.get("resource", {})
    fields = resource.get("fields", {})
    
    # Validate work item type
    work_item_type = fields.get("System.WorkItemType", "")
    if work_item_type != "Feature":
        return False, f"Invalid work item type: {work_item_type} (expected Feature)"
    
    # Validate assignee
    ai_user_match = os.getenv("AI_USER_MATCH", "AI Teammate")
    assignee = fields.get("System.AssignedTo", {})
    assignee_name = ""
    if isinstance(assignee, dict):
        assignee_name = assignee.get("displayName", "")
    
    if assignee_name.lower() != ai_user_match.lower():
        return False, f"Assignee mismatch: '{assignee_name}' (expected '{ai_user_match}')"
    
    # Validate board column and "Doing" state (not Done)
    spec_column = os.getenv("SPEC_COLUMN_NAME", "Specification")
    board_column = fields.get("System.BoardColumn", "")
    board_column_done = fields.get("System.BoardColumnDone", False)
    
    if board_column != spec_column:
        return False, f"Column mismatch: '{board_column}' (expected '{spec_column}')"
    
    if board_column_done:
        return False, f"Column state is 'Done' (expected 'Doing' - BoardColumnDone should be false)"
    
    return True, "ok"

