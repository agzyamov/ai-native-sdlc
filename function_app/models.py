"""
Data models for function payloads.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class WorkItemEvent:
    """
    Simplified Azure DevOps work item event model.
    Maps to Service Hook payload structure.
    """
    work_item_id: int
    event_type: str
    work_item_type: Optional[str] = None
    assignee_display_name: Optional[str] = None
    board_column: Optional[str] = None
    title: Optional[str] = None
    
    @classmethod
    def from_payload(cls, payload: dict) -> "WorkItemEvent":
        """
        Parse Service Hook JSON payload into WorkItemEvent.
        
        Args:
            payload: Raw Service Hook dictionary
        
        Returns:
            WorkItemEvent instance
        
        Raises:
            KeyError: If required fields missing
        """
        resource = payload.get("resource", {})
        fields = resource.get("fields", {})
        
        # Extract assignee display name
        assignee = fields.get("System.AssignedTo", {})
        assignee_name = None
        if isinstance(assignee, dict):
            assignee_name = assignee.get("displayName")
        
        return cls(
            work_item_id=resource.get("workItemId"),
            event_type=payload.get("eventType", ""),
            work_item_type=fields.get("System.WorkItemType"),
            assignee_display_name=assignee_name,
            board_column=fields.get("System.BoardColumn"),
            title=fields.get("System.Title")
        )
