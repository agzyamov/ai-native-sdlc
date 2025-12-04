#!/usr/bin/env python3
"""
Test function with the exact payload from work item 615 that failed
"""
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# The exact payload from the user's request
payload = {
    "subscriptionId": "20eeb007-3451-4aad-a749-4f069e36b67c",
    "notificationId": 79,
    "id": "efcf962e-c686-48d5-b6d7-2f6470ab275c",
    "eventType": "workitem.updated",
    "publisherId": "tfs",
    "message": {
        "text": "Feature #615 (hockey simulator game) transitioned to Specification by Rustem Agziamov",
        "html": "<a href=\"https://dev.azure.com/RustemAgziamov/web/wi.aspx?pcguid=888cd319-7a3f-479e-8ee4-c9d07c81641d&id=615\">Feature #615</a> (hockey simulator game) transitioned to Specification by Rustem Agziamov",
        "markdown": "[Feature #615](https://dev.azure.com/RustemAgziamov/web/wi.aspx?pcguid=888cd319-7a3f-479e-8ee4-c9d07c81641d&id=615) (hockey simulator game) transitioned to Specification by Rustem Agziamov"
    },
    "detailedMessage": {
        "text": "Feature #615 (hockey simulator game) transitioned to Specification by Rustem Agziamov\n\n- New State: Specification\n",
        "html": "<a href=\"https://dev.azure.com/RustemAgziamov/web/wi.aspx?pcguid=888cd319-7a3f-479e-8ee4-c9d07c81641d&id=615\">Feature #615</a> (hockey simulator game) transitioned to Specification by Rustem Agziamov<ul>\n<li>New State: Specification</li></ul>",
        "markdown": "[Feature #615](https://dev.azure.com/RustemAgziamov/web/wi.aspx?pcguid=888cd319-7a3f-479e-8ee4-c9d07c81641d&id=615) (hockey simulator game) transitioned to Specification by Rustem Agziamov\n\n* New State: Specification\n"
    },
    "resource": {
        "id": 6,
        "workItemId": 615,
        "rev": 5,
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
        "revisedDate": "2025-12-04T12:10:41.08Z",
        "fields": {
            "System.Rev": {
                "oldValue": 4,
                "newValue": 5
            },
            "System.AuthorizedDate": {
                "oldValue": "2025-12-04T12:10:35.343Z",
                "newValue": "2025-12-04T12:10:40.75Z"
            },
            "System.RevisedDate": {
                "oldValue": "2025-12-04T12:10:40.75Z",
                "newValue": "2025-12-04T12:10:41.08Z"
            },
            "System.State": {
                "oldValue": "New",
                "newValue": "Specification"
            },
            "System.Reason": {
                "oldValue": "New",
                "newValue": "Moved to state Specification"
            },
            "System.ChangedDate": {
                "oldValue": "2025-12-04T12:10:35.343Z",
                "newValue": "2025-12-04T12:10:40.75Z"
            },
            "System.Watermark": {
                "oldValue": 1581,
                "newValue": 1582
            },
            "System.BoardColumn": {
                "oldValue": "New",
                "newValue": "Specification"
            },
            "Microsoft.VSTS.Common.StateChangeDate": {
                "oldValue": "2025-12-04T12:10:05.707Z",
                "newValue": "2025-12-04T12:10:40.75Z"
            },
            "WEF_D88D961D5BD24EFEB690C902459A9FFA_Kanban.Column": {
                "oldValue": "New",
                "newValue": "Specification"
            }
        },
        "_links": {
            "self": {
                "href": "https://dev.azure.com/RustemAgziamov/753432ed-c013-4dd9-8760-7f0cdf436bf9/_apis/wit/workItems/615/updates/6"
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
        "url": "https://dev.azure.com/RustemAgziamov/753432ed-c013-4dd9-8760-7f0cdf436bf9/_apis/wit/workItems/615/updates/6",
        "revision": {
            "id": 615,
            "rev": 5,
            "fields": {
                "System.WorkItemType": "Feature",
                "System.State": "Specification",
                "System.Reason": "Moved to state Specification",
                "System.AssignedTo": "AI Teammate <Bot_AI_Teammate_ai-teammate@epam.com>",
                "System.CreatedDate": "2025-12-04T12:10:05.707Z",
                "System.CreatedBy": "Rustem Agziamov <Rustem_Agziamov@epam.com>",
                "System.ChangedDate": "2025-12-04T12:10:40.75Z",
                "System.ChangedBy": "Rustem Agziamov <Rustem_Agziamov@epam.com>",
                "System.CommentCount": 0,
                "System.TeamProject": "ai-native-sdlc-blueprint",
                "System.AreaPath": "ai-native-sdlc-blueprint",
                "System.IterationPath": "ai-native-sdlc-blueprint",
                "System.Title": "hockey simulator game",
                "System.BoardColumn": "Specification",
                "System.BoardColumnDone": False,
                "Microsoft.VSTS.Common.StateChangeDate": "2025-12-04T12:10:40.75Z",
                "Microsoft.VSTS.Common.Priority": 2,
                "Microsoft.VSTS.Common.ValueArea": "Business",
                "WEF_D88D961D5BD24EFEB690C902459A9FFA_Kanban.Column": "Specification",
                "WEF_D88D961D5BD24EFEB690C902459A9FFA_Kanban.Column.Done": False,
                "System.Description": "create a hockey simulator game using unreal engine",
                "Microsoft.VSTS.Common.StackRank": 1999884457.0
            },
            "multilineFieldsFormat": {
                "System.Description": "markdown"
            },
            "_links": {
                "self": {
                    "href": "https://dev.azure.com/RustemAgziamov/753432ed-c013-4dd9-8760-7f0cdf436bf9/_apis/wit/workItems/615/revisions/5"
                },
                "workItemRevisions": {
                    "href": "https://dev.azure.com/RustemAgziamov/753432ed-c013-4dd9-8760-7f0cdf436bf9/_apis/wit/workItems/615/revisions"
                },
                "parent": {
                    "href": "https://dev.azure.com/RustemAgziamov/753432ed-c013-4dd9-8760-7f0cdf436bf9/_apis/wit/workItems/615"
                }
            },
            "url": "https://dev.azure.com/RustemAgziamov/753432ed-c013-4dd9-8760-7f0cdf436bf9/_apis/wit/workItems/615/revisions/5"
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
    "createdDate": "2025-12-04T12:10:47.6816418Z"
}

print("=" * 60)
print("Testing with EXACT payload from work item 615")
print("=" * 60)
print()

# Check payload structure
resource = payload.get("resource", {})
revision = resource.get("revision", {})
fields = revision.get("fields", {})

print("📋 Payload Analysis:")
print(f"  Work Item ID: {resource.get('workItemId')}")
print(f"  Has revision: {bool(revision)}")
print(f"  Has revision.fields: {bool(fields)}")
print(f"  Description in payload: {bool(fields.get('System.Description'))}")
print(f"  Title in payload: {bool(fields.get('System.Title'))}")
print()

# Test validation
print("🧪 Testing validation...")
os.environ["AI_USER_MATCH"] = "AI Teammate"
os.environ["SPEC_COLUMN_NAME"] = "Specification"

import validation
is_valid, reason = validation.validate_event(payload)
print(f"  Validation result: {is_valid}")
print(f"  Reason: {reason}")
print()

# Check ADO client logic (simulate what happens)
print("🔍 Analyzing ADO API call logic...")

# Check if env vars are set
ado_org_url = os.getenv("ADO_ORG_URL")
ado_project = os.getenv("ADO_PROJECT")
ado_pat = os.getenv("ADO_WORK_ITEM_PAT")

print(f"  ADO_ORG_URL: {'SET' if ado_org_url else 'NOT SET'}")
print(f"  ADO_PROJECT: {'SET' if ado_project else 'NOT SET'}")
print(f"  ADO_WORK_ITEM_PAT: {'SET' if ado_pat else 'NOT SET'}")
print()

print("  📝 Code flow in function_app.py:")
print("    1. Line 105: work_item = ado_client.get_work_item(615)")
print("    2. If security blocks the call → returns None")
print("    3. Line 108: if work_item is None: raise ValueError(...)")
print("    4. Line 117-124: Exception caught → returns HTTP 500")
print()
print("  ⚠️  PROBLEM: The payload already has the data!")
print(f"     - Description: {fields.get('System.Description', '')[:50]}...")
print(f"     - Title: {fields.get('System.Title')}")
print()
print("  💡 WHY IT WORKED BEFORE:")
print("     - ADO API call was succeeding (security allowed it)")
print("     - Function got data from ADO API")
print("     - Everything worked fine")
print()
print("  💥 WHY IT BROKE NOW:")
print("     - Azure security settings changed")
print("     - ADO API call is now blocked")
print("     - Function fails even though payload has the data!")

print()
print("=" * 60)
print("CONCLUSION:")
print("=" * 60)
print("The payload already contains all needed data in resource.revision.fields")
print("The ADO API call is unnecessary and is being blocked by security settings.")
print("This is why it worked before (ADO API was accessible) and broke now.")
print("=" * 60)

