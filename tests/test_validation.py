"""
Unit tests for validation logic.
"""

import os

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
                "System.BoardColumn": "Specification – Doing",
            },
        },
    }

    is_valid, reason = validate_event(event)
    assert is_valid is True
    assert reason == "ok"


def test_validate_event_invalid_type():
    """Test validation fails for non-update events."""
    event = {"eventType": "workitem.created", "resource": {"workItemId": 123}}

    is_valid, reason = validate_event(event)
    assert is_valid is False
    assert "Invalid event type" in reason


def test_validate_event_missing_event_type():
    """Test validation fails when eventType missing."""
    event = {"resource": {"workItemId": 123}}

    is_valid, _ = validate_event(event)
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
                "System.BoardColumn": "Specification – Doing",
            },
        },
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
                "System.BoardColumn": "Specification – Doing",
            },
        },
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
                "System.BoardColumn": "Planning – Doing",
            },
        },
    }

    is_valid, reason = validate_event(event)
    assert is_valid is False
    assert "Column mismatch" in reason


def test_validate_event_comment_only_update():
    """Test validation rejects comment-only updates to prevent GHA feedback loops.

    When a GHA workflow posts a comment to ADO, it triggers another workitem.updated
    service hook. The changed fields will only contain noise fields (timestamps,
    watermark, comment count, history). These must be rejected to avoid infinite loops.
    """
    event = {
        "eventType": "workitem.updated",
        "resource": {
            "workItemId": 819,
            "fields": {
                "System.Rev": {"oldValue": 5, "newValue": 6},
                "System.AuthorizedDate": {
                    "oldValue": "2026-03-09T08:01:42.323Z",
                    "newValue": "2026-03-09T08:02:11.777Z",
                },
                "System.RevisedDate": {
                    "oldValue": "2026-03-09T08:02:11.777Z",
                    "newValue": "9999-01-01T00:00:00Z",
                },
                "System.ChangedDate": {
                    "oldValue": "2026-03-09T08:01:42.323Z",
                    "newValue": "2026-03-09T08:02:11.777Z",
                },
                "System.Watermark": {"oldValue": 2280, "newValue": 2281},
                "System.CommentCount": {"oldValue": 0, "newValue": 1},
                "System.History": {
                    "newValue": "Processing started. CI Run: https://github.com/org/repo/actions/runs/123"
                },
            },
            "revision": {
                "fields": {
                    "System.WorkItemType": "User Story",
                    "System.AssignedTo": "AI Teammate <bot@example.com>",
                    "System.BoardColumn": "Specification",
                    "System.BoardColumnDone": False,
                }
            },
        },
    }

    is_valid, reason = validate_event(event)
    assert is_valid is False
    assert "feedback loop" in reason
