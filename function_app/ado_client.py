"""
Azure DevOps REST API client for fetching work item details.
"""
import logging
import os
from typing import Optional

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
            logger.error(f"Failed to fetch work item {work_item_id}: HTTP {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching work item {work_item_id}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching work item {work_item_id}: {str(e)}")
        return None
