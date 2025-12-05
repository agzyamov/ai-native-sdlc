"""
Azure DevOps REST API client for fetching and updating work items.
"""
import base64
import logging
import os
import sys
from typing import List, Optional

import requests

logger = logging.getLogger(__name__)


def get_work_item(work_item_id: int) -> Optional[dict]:
    """
    Fetch work item details from Azure DevOps REST API.
    
    Args:
        work_item_id: Work item ID to fetch
    
    Returns:
        Work item JSON if successful, None on error
    
    Uses environment variables:
        - ADO_ORG_URL: Azure DevOps organization URL (e.g., https://dev.azure.com/org)
        - ADO_PROJECT: Project name
        - ADO_WORK_ITEM_PAT: Personal Access Token (Work Items: Read)
    """
    org_url = os.getenv("ADO_ORG_URL")
    project = os.getenv("ADO_PROJECT")
    pat = os.getenv("ADO_WORK_ITEM_PAT")
    
    if not all([org_url, project, pat]):
        logger.error("Missing required ADO environment variables (ADO_ORG_URL, ADO_PROJECT, ADO_WORK_ITEM_PAT)")
        return None
    
    # Construct API URL
    url = f"{org_url}/{project}/_apis/wit/workitems/{work_item_id}?api-version=7.0"
    
    # Encode PAT for basic auth
    import base64
    auth_header = base64.b64encode(f":{pat}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to fetch work item {work_item_id}: HTTP {response.status_code} - {response.text[:500]}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching work item {work_item_id}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching work item {work_item_id}: {str(e)}")
        return None


def get_work_item_latest_revision(work_item_id: int) -> Optional[dict]:
    """
    Fetch the latest revision of a work item from Azure DevOps REST API.
    This is useful for getting the most recent ChangedBy user information.
    
    Args:
        work_item_id: Work item ID to fetch revisions for
    
    Returns:
        Latest revision JSON if successful, None on error
    
    Uses environment variables:
        - ADO_ORG_URL: Azure DevOps organization URL (e.g., https://dev.azure.com/org)
        - ADO_PROJECT: Project name
        - ADO_WORK_ITEM_PAT: Personal Access Token (Work Items: Read)
    """
    org_url = os.getenv("ADO_ORG_URL")
    project = os.getenv("ADO_PROJECT")
    pat = os.getenv("ADO_WORK_ITEM_PAT")
    
    if not all([org_url, project, pat]):
        logger.error("Missing required ADO environment variables (ADO_ORG_URL, ADO_PROJECT, ADO_WORK_ITEM_PAT)")
        return None
    
    # First, get the work item to find the latest revision number
    work_item = get_work_item(work_item_id)
    if work_item is None:
        logger.error(f"Failed to fetch work item {work_item_id} to get revision number")
        return None
    
    # Get the latest revision number from the work item
    latest_rev = work_item.get("rev", None)
    if latest_rev is None:
        logger.warning(f"Work item {work_item_id} has no 'rev' field")
        return None
    
    # Construct API URL to get the specific revision
    url = f"{org_url}/{project}/_apis/wit/workitems/{work_item_id}/revisions/{latest_rev}?api-version=7.0"
    
    # Encode PAT for basic auth
    import base64
    auth_header = base64.b64encode(f":{pat}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to fetch revision {latest_rev} for work item {work_item_id}: HTTP {response.status_code} - {response.text[:500]}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching revision {latest_rev} for work item {work_item_id}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching revision {latest_rev} for work item {work_item_id}: {str(e)}")
        return None


def update_work_item_description(work_item_id: int, description: str) -> bool:
    """
    Update work item description using PATCH operation.
    
    Args:
        work_item_id: Work item ID to update
        description: New description HTML content
    
    Returns:
        True if successful, False on error
    
    Uses environment variables:
        - ADO_ORG_URL: Azure DevOps organization URL
        - ADO_PROJECT: Project name
        - ADO_WORK_ITEM_PAT: Personal Access Token (Work Items: Read & Write)
    """
    org_url = os.getenv("ADO_ORG_URL")
    project = os.getenv("ADO_PROJECT")
    pat = os.getenv("ADO_WORK_ITEM_PAT")
    
    if not all([org_url, project, pat]):
        logger.error("Missing required ADO environment variables")
        return False
    
    url = f"{org_url}/{project}/_apis/wit/workitems/{work_item_id}?api-version=7.1"
    
    import base64
    auth_header = base64.b64encode(f":{pat}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json-patch+json"
    }
    
    # JSON Patch format for ADO API
    payload = [
        {
            "op": "add",
            "path": "/fields/System.Description",
            "value": description
        }
    ]
    
    try:
        response = requests.patch(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code in [200, 201]:
            logger.info(f"Successfully updated description for work item {work_item_id}")
            return True
        else:
            logger.error(f"Failed to update work item {work_item_id}: HTTP {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout updating work item {work_item_id}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating work item {work_item_id}: {str(e)}")
        return False


def create_issue_workitem(
    parent_feature_id: int,
    title: str,
    description: str,
    tags: str,
    idempotency_key: str,
    assigned_to: Optional[str] = None
) -> Optional[dict]:
    """
    Create ADO Issue work item with Parent-Child link to Feature.
    
    Args:
        parent_feature_id: Parent Feature work item ID
        title: Issue title
        description: Issue description (HTML)
        tags: Semicolon-separated tags
        idempotency_key: Unique key to prevent duplicates
        assigned_to: Optional assignee email/UPN
    
    Returns:
        Issue dict if created, None if duplicate detected or error
    
    Uses environment variables:
        - ADO_ORG_URL: Azure DevOps organization URL
        - ADO_PROJECT: Project name  
        - ADO_WORK_ITEM_PAT: Personal Access Token (Work Items: Read & Write)
    """
    org_url = os.getenv("ADO_ORG_URL")
    project = os.getenv("ADO_PROJECT")
    pat = os.getenv("ADO_WORK_ITEM_PAT")
    
    if not all([org_url, project, pat]):
        logger.error("Missing required ADO environment variables")
        return None
    
    import base64
    auth_header = base64.b64encode(f":{pat}".encode()).decode()
    
    # Check for existing Issue (idempotency)
    query_url = f"{org_url}/{project}/_apis/wit/wiql?api-version=7.0"
    query_payload = {
        "query": f"""
            SELECT [System.Id] 
            FROM WorkItems 
            WHERE [System.WorkItemType] = 'Issue' 
            AND [System.Parent] = {parent_feature_id}
            AND [System.Description] CONTAINS '{idempotency_key}'
        """
    }
    
    try:
        query_response = requests.post(
            query_url,
            json=query_payload,
            headers={
                "Authorization": f"Basic {auth_header}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if query_response.ok and query_response.json().get('workItems'):
            logger.info(f"Issue already exists for idempotency key {idempotency_key}")
            return None  # Duplicate, skip
    except requests.exceptions.RequestException as e:
        logger.warning(f"Idempotency check failed: {str(e)} - proceeding with creation")
    
    # Create Issue (JSON Patch format)
    create_url = f"{org_url}/{project}/_apis/wit/workitems/$Issue?api-version=7.0"
    
    # Add idempotency key to description for duplicate detection
    description_with_key = f"{description}\n\n<!-- idempotency_key: {idempotency_key} -->"
    
    payload = [
        {"op": "add", "path": "/fields/System.Title", "value": title},
        {"op": "add", "path": "/fields/System.Description", "value": description_with_key},
        # Set description field format to Markdown (as per Microsoft docs)
        # https://devblogs.microsoft.com/devops/markdown-support-arrives-for-work-items/
        {"op": "add", "path": "/multilineFieldsFormat/System.Description", "value": "Markdown"},
        {"op": "add", "path": "/fields/System.Tags", "value": tags},
        {
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "System.LinkTypes.Hierarchy-Reverse",
                "url": f"{org_url}/{project}/_apis/wit/workitems/{parent_feature_id}",
                "attributes": {"comment": "Auto-generated clarification"}
            }
        }
    ]
    
    if assigned_to:
        payload.append({"op": "add", "path": "/fields/System.AssignedTo", "value": assigned_to})
    
    try:
        response = requests.post(
            create_url,
            json=payload,
            headers={
                "Authorization": f"Basic {auth_header}",
                "Content-Type": "application/json-patch+json"
            },
            timeout=30
        )
        
        if response.ok:
            issue = response.json()
            logger.info(f"Created Issue {issue['id']}: {title}")
            return issue
        else:
            error_msg = f"HTTP {response.status_code}"
            if response.status_code == 401:
                error_msg += " - Authentication failed (invalid/expired PAT or missing 'Work Items: Read & Write' scope)"
            elif response.status_code == 403:
                error_msg += " - Authorization failed (insufficient permissions)"
            elif response.status_code == 404:
                error_msg += f" - Parent work item {parent_feature_id} not found"
            else:
                error_msg += f" - {response.text[:500]}"
            
            logger.error(f"Failed to create Issue: {error_msg}")
            print(f"❌ Failed to create Issue: {error_msg}", file=sys.stderr)
            if response.text:
                print(f"Response: {response.text[:500]}", file=sys.stderr)
            return None
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout creating Issue for Feature {parent_feature_id}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating Issue: {str(e)}")
        return None


def get_child_issues(parent_feature_id: int) -> List[dict]:
    """
    Fetch closed child Issues for a Feature using WIQL query.
    
    Args:
        parent_feature_id: Parent Feature work item ID
    
    Returns:
        List of work items with id, title, and description
        Empty list on error or if no closed Issues found
    
    Uses environment variables:
        - ADO_ORG_URL: Azure DevOps organization URL
        - ADO_PROJECT: Project name
        - ADO_WORK_ITEM_PAT: Personal Access Token (Work Items: Read)
    """
    org_url = os.getenv("ADO_ORG_URL")
    project = os.getenv("ADO_PROJECT")
    pat = os.getenv("ADO_WORK_ITEM_PAT")
    
    if not all([org_url, project, pat]):
        logger.error("Missing required ADO environment variables for get_child_issues")
        return []
    
    auth_header = base64.b64encode(f":{pat}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json"
    }
    
    # WIQL query to find closed child Issues
    wiql_url = f"{org_url}/{project}/_apis/wit/wiql?api-version=7.0"
    wiql_query = {
        "query": f"""
            SELECT [System.Id], [System.Title], [System.Description]
            FROM WorkItems
            WHERE [System.WorkItemType] = 'Issue'
            AND [System.Parent] = {parent_feature_id}
            AND [System.State] = 'Closed'
        """
    }
    
    try:
        response = requests.post(wiql_url, json=wiql_query, headers=headers, timeout=15)
        
        if response.status_code != 200:
            logger.error(f"WIQL query failed for parent {parent_feature_id}: HTTP {response.status_code} - {response.text[:500]}")
            return []
        
        query_result = response.json()
        work_items_refs = query_result.get("workItems", [])
        
        if not work_items_refs:
            logger.info(f"No closed Issues found for Feature {parent_feature_id}")
            return []
        
        # Extract work item IDs
        work_item_ids = [wi["id"] for wi in work_items_refs]
        logger.info(f"Found {len(work_item_ids)} closed Issues for Feature {parent_feature_id}: {work_item_ids}")
        
        # Batch fetch work item details
        ids_param = ",".join(str(wi_id) for wi_id in work_item_ids)
        batch_url = f"{org_url}/{project}/_apis/wit/workitems?ids={ids_param}&fields=System.Id,System.Title,System.Description&api-version=7.0"
        
        batch_response = requests.get(batch_url, headers=headers, timeout=15)
        
        if batch_response.status_code != 200:
            logger.error(f"Batch fetch failed for Issues: HTTP {batch_response.status_code} - {batch_response.text[:500]}")
            return []
        
        batch_result = batch_response.json()
        work_items = []
        
        for wi in batch_result.get("value", []):
            fields = wi.get("fields", {})
            work_items.append({
                "id": wi.get("id"),
                "title": fields.get("System.Title", ""),
                "description": fields.get("System.Description", "")
            })
        
        return work_items
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching child Issues for Feature {parent_feature_id}")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching child Issues for Feature {parent_feature_id}: {str(e)}")
        return []


def get_work_item_comments(work_item_id: int) -> List[str]:
    """
    Fetch comments for a work item from Azure DevOps Comments API.
    
    Args:
        work_item_id: Work item ID to fetch comments for
    
    Returns:
        List of comment text strings (newest first)
        Empty list on error or if no comments found
    
    Uses environment variables:
        - ADO_ORG_URL: Azure DevOps organization URL
        - ADO_PROJECT: Project name
        - ADO_WORK_ITEM_PAT: Personal Access Token (Work Items: Read)
    """
    org_url = os.getenv("ADO_ORG_URL")
    project = os.getenv("ADO_PROJECT")
    pat = os.getenv("ADO_WORK_ITEM_PAT")
    
    if not all([org_url, project, pat]):
        logger.error("Missing required ADO environment variables for get_work_item_comments")
        return []
    
    auth_header = base64.b64encode(f":{pat}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json"
    }
    
    # Comments API endpoint
    comments_url = f"{org_url}/{project}/_apis/wit/workitems/{work_item_id}/comments?api-version=7.0-preview.3"
    
    try:
        response = requests.get(comments_url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch comments for work item {work_item_id}: HTTP {response.status_code} - {response.text[:500]}")
            return []
        
        result = response.json()
        comments = []
        
        # Comments API returns either "comments" or "value" array
        comments_list = result.get("comments", result.get("value", []))
        
        for comment in comments_list:
            # Comment can be a string or an object with "text" property
            if isinstance(comment, str):
                text = comment.strip()
            else:
                text = comment.get("text", "").strip()
            
            if text:
                comments.append(text)
        
        logger.info(f"Fetched {len(comments)} comments for work item {work_item_id}")
        return comments
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching comments for work item {work_item_id}")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching comments for work item {work_item_id}: {str(e)}")
        return []
