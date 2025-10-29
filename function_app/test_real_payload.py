#!/usr/bin/env python3
"""Test validation with the real ADO webhook payload that returned 403"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from validation import validate_event

# Actual payload from ADO webhook that returned 403
payload = {
    "subscriptionId": "20eeb007-3451-4aad-a749-4f069e36b67c",
    "notificationId": 4,
    "id": "3797d6f3-7b5a-4858-80f5-5014597ee949",
    "eventType": "workitem.updated",
    "publisherId": "tfs",
    "resource": {
        "id": 24,
        "workItemId": 451,
        "rev": 23,
        "revisedDate": "2025-10-28T11:13:15.977Z",
        "fields": {
            "System.Rev": {"oldValue": 22, "newValue": 23},
            "System.State": {"oldValue": "New", "newValue": "Specification"},
            "System.BoardColumn": {"oldValue": "New", "newValue": "Specification"}
        },
        "revision": {
            "id": 451,
            "rev": 23,
            "fields": {
                "System.WorkItemType": "Feature",
                "System.State": "Specification",
                "System.Reason": "Moved to state Specification",
                "System.AssignedTo": "AI Teammate <Bot_AI_Teammate_ai-teammate@epam.com>",
                "System.Title": "test - motivation quotes",
                "System.BoardColumn": "Specification",
                "System.BoardColumnDone": False,
                "System.Description": "create motivation quote generator\n"
            }
        }
    }
}

# Set environment variables
os.environ["AI_USER_MATCH"] = "AI Teammate"
os.environ["SPEC_COLUMN_NAME"] = "Specification"

print("Testing validation with REAL ADO payload that returned 403...")
print(f"Environment: AI_USER_MATCH={os.getenv('AI_USER_MATCH')}, SPEC_COLUMN_NAME={os.getenv('SPEC_COLUMN_NAME')}")

is_valid, reason = validate_event(payload)

print(f"\nValidation result: {is_valid}")
print(f"Reason: {reason}")

if is_valid:
    print("\n✅ SUCCESS: Validation passed!")
    sys.exit(0)
else:
    print(f"\n❌ FAILED: {reason}")
    sys.exit(1)
