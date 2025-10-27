"""
Unit tests for validation logic.
"""
import os
import pytest
from function_app.validation import validate_event


def test_validate_event_happy_path():
    """Test validation passes for workitem.updated event."""
    os.environ["AI_USER_MATCH"] = "AI Teammate"
    os.environ["SPEC_COLUMN_NAME"] = "Specification – Doing"
    
    event = {
        "eventType": "workitem.updated",
        "resource": {
            "workItemId": 123,
            "fields": {
                "System.WorkItemType": "Feature",
                "System.AssignedTo": {"displayName": "AI Teammate"},
                "System.BoardColumn": "Specification – Doing"
            }
        }
    }
    
    is_valid, reason = validate_event(event)
    assert is_valid is True
    assert reason == "ok"


def test_validate_event_invalid_type():
    """Test validation fails for non-update events."""
    event = {
        "eventType": "workitem.created",
        "resource": {"workItemId": 123}
    }
    
    is_valid, reason = validate_event(event)
    assert is_valid is False
    assert "Invalid event type" in reason


def test_validate_event_missing_event_type():
    """Test validation fails when eventType missing."""
    event = {"resource": {"workItemId": 123}}
    
    is_valid, reason = validate_event(event)
    assert is_valid is False


def test_validate_event_wrong_work_item_type():
    """Test validation fails for non-Feature work items."""
    event = {
        "eventType": "workitem.updated",
        "resource": {
            "workItemId": 123,
            "fields": {
                "System.WorkItemType": "Bug",
                "System.AssignedTo": {"displayName": "AI Teammate"},
                "System.BoardColumn": "Specification – Doing"
            }
        }
    }
    
    is_valid, reason = validate_event(event)
    assert is_valid is False
    assert "Invalid work item type" in reason


def test_validate_event_wrong_assignee():
    """Test validation fails for wrong assignee."""
    os.environ["AI_USER_MATCH"] = "AI Teammate"
    
    event = {
        "eventType": "workitem.updated",
        "resource": {
            "workItemId": 123,
            "fields": {
                "System.WorkItemType": "Feature",
                "System.AssignedTo": {"displayName": "Human Developer"},
                "System.BoardColumn": "Specification – Doing"
            }
        }
    }
    
    is_valid, reason = validate_event(event)
    assert is_valid is False
    assert "Assignee mismatch" in reason


def test_validate_event_wrong_column():
    """Test validation fails for wrong board column."""
    os.environ["SPEC_COLUMN_NAME"] = "Specification – Doing"
    
    event = {
        "eventType": "workitem.updated",
        "resource": {
            "workItemId": 123,
            "fields": {
                "System.WorkItemType": "Feature",
                "System.AssignedTo": {"displayName": "AI Teammate"},
                "System.BoardColumn": "Planning – Doing"
            }
        }
    }
    
    is_valid, reason = validate_event(event)
    assert is_valid is False
    assert "Column mismatch" in reason

