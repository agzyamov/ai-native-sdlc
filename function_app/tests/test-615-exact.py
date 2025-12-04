#!/usr/bin/env python3
"""
Test script to reproduce the exact error with the provided payload.
"""
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the Azure Functions request object
class MockHttpRequest:
    def __init__(self, body_json):
        self._body_json = body_json
        self.method = "POST"
    
    def get_json(self):
        return self._body_json

# Load the exact payload
payload = {
  "subscriptionId": "20eeb007-3451-4aad-a749-4f069e36b67c",
  "notificationId": 80,
  "id": "59437b90-f084-48cb-b93c-6d0ff1f4da62",
  "eventType": "workitem.updated",
  "publisherId": "tfs",
  "message": {
    "text": "Feature #615 (hockey simulator game) transitioned to Specification by Rustem Agziamov\r\n(https://dev.azure.com/RustemAgziamov/web/wi.aspx?pcguid=888cd319-7a3f-479e-8ee4-c9d07c81641d&id=615)",
    "html": "<a href=\"https://dev.azure.com/RustemAgziamov/web/wi.aspx?pcguid=888cd319-7a3f-479e-8ee4-c9d07c81641d&amp;id=615\">Feature #615</a> (hockey simulator game) transitioned to Specification by Rustem Agziamov",
    "markdown": "[Feature #615](https://dev.azure.com/RustemAgziamov/web/wi.aspx?pcguid=888cd319-7a3f-479e-8ee4-c9d07c81641d&id=615) (hockey simulator game) transitioned to Specification by Rustem Agziamov"
  },
  "detailedMessage": {
    "text": "Feature #615 (hockey simulator game) transitioned to Specification by Rustem Agziamov\r\n(https://dev.azure.com/RustemAgziamov/web/wi.aspx?pcguid=888cd319-7a3f-479e-8ee4-c9d07c81641d&id=615)\r\n\r\n- New State: Specification\r\n",
    "html": "<a href=\"https://dev.azure.com/RustemAgziamov/web/wi.aspx?pcguid=888cd319-7a3f-479e-8ee4-c9d07c81641d&amp;id=615\">Feature #615</a> (hockey simulator game) transitioned to Specification by Rustem Agziamov<ul>\r\n<li>New State: Specification</li></ul>",
    "markdown": "[Feature #615](https://dev.azure.com/RustemAgziamov/web/wi.aspx?pcguid=888cd319-7a3f-479e-8ee4-c9d07c81641d&id=615) (hockey simulator game) transitioned to Specification by Rustem Agziamov\r\n\r\n* New State: Specification\r\n"
  },
  "resource": {
    "id": 8,
    "workItemId": 615,
    "rev": 8,
    "revisedBy": {
      "id": "8ec6f80d-0ef1-6357-9fe4-e09eca72d843",
      "name": "Rustem Agziamov <Rustem_Agziamov@epam.com>",
      "displayName": "Rustem Agziamov",
      "url": "https://spsprodweu5.vssps.visualstudio.com/A3653ea85-9acf-42cc-bbe5-7ce3be07e3f4/_apis/Identities/8ec6f80d-0ef1-6357-9fe4-e09eca72d843",
      "_links": {
        "avatar": {
          "href": "https://dev.azure.com/RustemAgziamov/_apis/GraphProfile/MemberAvatars/aad.OGVjNmY4MGQtMGVmMS03MzU3LTlmZTQtZTA5ZWNhNzJkODQz"
        }
      },
      "uniqueName": "Rustem_Agziamov@epam.com",
      "imageUrl": "https://dev.azure.com/RustemAgziamov/_apis/GraphProfile/MemberAvatars/aad.OGVjNmY4MGQtMGVmMS03MzU3LTlmZTQtZTA5ZWNhNzJkODQz",
      "descriptor": "aad.OGVjNmY4MGQtMGVmMS03MzU3LTlmZTQtZTA5ZWNhNzJkODQz"
    },
    "revisedDate": "9999-01-01T00:00:00Z",
    "fields": {
      "System.Rev": {
        "oldValue": 7,
        "newValue": 8
      },
      "System.AuthorizedDate": {
        "oldValue": "2025-12-04T12:19:10.957Z",
        "newValue": "2025-12-04T15:24:40.473Z"
      },
      "System.RevisedDate": {
        "oldValue": "2025-12-04T15:24:40.473Z",
        "newValue": "9999-01-01T00:00:00Z"
      },
      "System.State": {
        "oldValue": "New",
        "newValue": "Specification"
      },
      "System.Reason": {
        "oldValue": "Moved out of state Specification",
        "newValue": "Moved to state Specification"
      },
      "System.ChangedDate": {
        "oldValue": "2025-12-04T12:19:10.957Z",
        "newValue": "2025-12-04T15:24:40.473Z"
      },
      "System.Watermark": {
        "oldValue": 1584,
        "newValue": 1585
      },
      "System.BoardColumn": {
        "oldValue": "New",
        "newValue": "Specification"
      },
      "Microsoft.VSTS.Common.StateChangeDate": {
        "oldValue": "2025-12-04T12:19:10.957Z",
        "newValue": "2025-12-04T15:24:40.473Z"
      },
      "WEF_D88D961D5BD24EFEB690C902459A9FFA_Kanban.Column": {
        "oldValue": "New",
        "newValue": "Specification"
      }
    },
    "_links": {
      "self": {
        "href": "https://dev.azure.com/RustemAgziamov/753432ed-c013-4dd9-8760-7f0cdf436bf9/_apis/wit/workItems/615/updates/8"
      },
      "workItemUpdates": {
        "href": "https://dev.azure.com/RustemAgziamov/753432ed-c013-4dd9-8760-7f0cdf436bf9/_apis/wit/workItems/615/updates"
      },
      "parent": {
        "href": "https://dev.azure.com/RustemAgziamov/753432ed-c013-4dd9-8760-7f0cdf436bf9/_apis/wit/workItems/615"
      },
      "html": {
        "href": "https://dev.azure.com/RustemAgziamov/web/wi.aspx?pcguid=888cd319-7a3f-479e-8ee4-c9d07c81641d&id=615"
      }
    },
    "url": "https://dev.azure.com/RustemAgziamov/753432ed-c013-4dd9-8760-7f0cdf436bf9/_apis/wit/workItems/615/updates/8",
    "revision": {
      "id": 615,
      "rev": 8,
      "fields": {
        "System.AreaPath": "ai-native-sdlc-blueprint",
        "System.TeamProject": "ai-native-sdlc-blueprint",
        "System.IterationPath": "ai-native-sdlc-blueprint",
        "System.WorkItemType": "Feature",
        "System.State": "Specification",
        "System.Reason": "Moved to state Specification",
        "System.AssignedTo": "AI Teammate <Bot_AI_Teammate_ai-teammate@epam.com>",
        "System.CreatedDate": "2025-12-04T12:10:05.707Z",
        "System.CreatedBy": "Rustem Agziamov <Rustem_Agziamov@epam.com>",
        "System.ChangedDate": "2025-12-04T15:24:40.473Z",
        "System.ChangedBy": "Rustem Agziamov <Rustem_Agziamov@epam.com>",
        "System.CommentCount": 0,
        "System.Title": "hockey simulator game",
        "System.BoardColumn": "Specification",
        "System.BoardColumnDone": False,
        "Microsoft.VSTS.Common.StateChangeDate": "2025-12-04T15:24:40.473Z",
        "Microsoft.VSTS.Common.Priority": 2,
        "Microsoft.VSTS.Common.StackRank": 1999817378.0,
        "Microsoft.VSTS.Common.ValueArea": "Business",
        "WEF_D88D961D5BD24EFEB690C902459A9FFA_Kanban.Column": "Specification",
        "WEF_D88D961D5BD24EFEB690C902459A9FFA_Kanban.Column.Done": False,
        "System.Description": "create a hockey simulator game using unreal engine"
      },
      "multilineFieldsFormat": {
        "System.Description": "markdown"
      },
      "_links": {
        "self": {
          "href": "https://dev.azure.com/RustemAgziamov/753432ed-c013-4dd9-8760-7f0cdf436bf9/_apis/wit/workItems/615/revisions/8"
        },
        "workItemRevisions": {
          "href": "https://dev.azure.com/RustemAgziamov/753432ed-c013-4dd9-8760-7f0cdf436bf9/_apis/wit/workItems/615/revisions"
        },
        "parent": {
          "href": "https://dev.azure.com/RustemAgziamov/753432ed-c013-4dd9-8760-7f0cdf436bf9/_apis/wit/workItems/615"
        }
      },
      "url": "https://dev.azure.com/RustemAgziamov/753432ed-c013-4dd9-8760-7f0cdf436bf9/_apis/wit/workItems/615/revisions/8"
    }
  },
  "resourceVersion": "1.0",
  "resourceContainers": {
    "collection": {
      "id": "888cd319-7a3f-479e-8ee4-c9d07c81641d",
      "baseUrl": "https://dev.azure.com/RustemAgziamov/"
    },
    "account": {
      "id": "3653ea85-9acf-42cc-bbe5-7ce3be07e3f4",
      "baseUrl": "https://dev.azure.com/RustemAgziamov/"
    },
    "project": {
      "id": "753432ed-c013-4dd9-8760-7f0cdf436bf9",
      "baseUrl": "https://dev.azure.com/RustemAgziamov/"
    }
  },
  "createdDate": "2025-12-04T15:24:47.4493006Z"
}

def test_validation():
    """Test validation logic"""
    print("=" * 60)
    print("Testing validation...")
    print("=" * 60)
    try:
        import validation
        is_valid, reason = validation.validate_event(payload)
        print(f"Validation result: is_valid={is_valid}, reason={reason}")
        return is_valid
    except Exception as e:
        print(f"Validation error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_extraction():
    """Test data extraction"""
    print("\n" + "=" * 60)
    print("Testing data extraction...")
    print("=" * 60)
    try:
        resource = payload.get("resource", {})
        revision = resource.get("revision", {})
        fields = revision.get("fields", {})
        
        work_item_id = payload.get("resource", {}).get("workItemId")
        description = fields.get("System.Description", "")
        title = fields.get("System.Title", "")
        
        print(f"Work Item ID: {work_item_id}")
        print(f"Title: {title}")
        print(f"Description: {description[:100]}...")
        print(f"Has fields: {bool(fields)}")
        return True
    except Exception as e:
        print(f"Extraction error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dispatch():
    """Test dispatch logic (will fail without PAT, but should show error)"""
    print("\n" + "=" * 60)
    print("Testing dispatch...")
    print("=" * 60)
    try:
        import dispatch
        work_item_id = payload.get("resource", {}).get("workItemId")
        resource = payload.get("resource", {})
        revision = resource.get("revision", {})
        fields = revision.get("fields", {})
        description = fields.get("System.Description", "")
        title = fields.get("System.Title", "")
        feature_description = description if description else title
        
        success, message = dispatch.dispatch_workflow(
            work_item_id=work_item_id,
            description_placeholder=feature_description
        )
        print(f"Dispatch result: success={success}, message={message}")
        return success
    except Exception as e:
        print(f"Dispatch error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing function logic with exact payload...\n")
    
    # Test each component
    validation_ok = test_validation()
    extraction_ok = test_extraction()
    dispatch_ok = test_dispatch()
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    print(f"Validation: {'✓' if validation_ok else '✗'}")
    print(f"Extraction: {'✓' if extraction_ok else '✗'}")
    print(f"Dispatch: {'✓' if dispatch_ok else '✗'}")
    
    if not validation_ok:
        print("\n❌ Validation failed - this would cause a 204 response (filtered)")
    elif not extraction_ok:
        print("\n❌ Extraction failed - this would cause a 500 error")
    elif not dispatch_ok:
        print("\n❌ Dispatch failed - this would cause a 500 error")
    else:
        print("\n✅ All tests passed!")

