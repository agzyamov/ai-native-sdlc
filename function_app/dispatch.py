"""
GitHub workflow_dispatch client for triggering spec generation.
"""
import logging
import os
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)


def dispatch_workflow(
    work_item_id: int,
    description_placeholder: str = "",
    changed_by_user_id: Optional[str] = None
) -> tuple[bool, str]:
    """
    Trigger GitHub Actions workflow via workflow_dispatch API with retry logic.
    
    Args:
        work_item_id: Azure DevOps work item ID
        description_placeholder: Optional description text
        changed_by_user_id: Optional Azure DevOps user ID who last changed the work item
    
    Returns:
        Tuple of (success, message)
        - (True, "dispatched") on HTTP 204
        - (False, error_message) on failure
    
    Retry Strategy:
        - 3 attempts with exponential backoff (2s, 6s, 14s)
        - Only retries on network/transport errors, not validation failures
    """
    try:
        github_owner = os.getenv("GITHUB_OWNER")
        github_repo = os.getenv("GITHUB_REPO")
        workflow_filename = os.getenv("GITHUB_WORKFLOW_FILENAME", "spec-kit-specify.yml")
        workflow_ref = os.getenv("GITHUB_WORKFLOW_REF", "main")  # Branch/tag to dispatch on
        pat = os.getenv("GH_WORKFLOW_DISPATCH_PAT")
    except Exception as env_err:
        logger.exception(f"Failed to read environment variables: {env_err}")
        return False, f"Configuration error: Failed to read environment variables - {str(env_err)}"
    
    # Check if PAT is a Key Vault reference that wasn't resolved
    if pat and pat.startswith("@Microsoft.KeyVault"):
        logger.error(f"Key Vault reference not resolved: GH_WORKFLOW_DISPATCH_PAT appears to be unresolved Key Vault reference")
        return False, "Key Vault secret not accessible - GH_WORKFLOW_DISPATCH_PAT reference unresolved. Check function managed identity has 'Key Vault Secrets User' role and Key Vault network ACLs allow access."
    
    # Log PAT status (without exposing the actual value)
    if pat:
        pat_prefix = pat[:10] if len(pat) > 10 else pat[:len(pat)]
        pat_length = len(pat)
        logger.info(f"PAT retrieved - length={pat_length}, prefix={pat_prefix}...")
        print(f"STDOUT: PAT retrieved - length={pat_length}, starts_with_ghp={pat.startswith('ghp_')}, starts_with_github_pat={pat.startswith('github_pat_')}")
    else:
        logger.error("PAT is None or empty")
        print("STDOUT: PAT is None or empty")
    
    if not all([github_owner, github_repo, pat]):
        missing = []
        if not github_owner:
            missing.append("GITHUB_OWNER")
        if not github_repo:
            missing.append("GITHUB_REPO")
        if not pat:
            missing.append("GH_WORKFLOW_DISPATCH_PAT")
        return False, f"Missing required environment variables: {', '.join(missing)}"
    
    url = f"https://api.github.com/repos/{github_owner}/{github_repo}/actions/workflows/{workflow_filename}/dispatches"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    inputs = {
        "feature_description": description_placeholder or f"ADO Work Item #{work_item_id}",
        "create_branch": "true",
        "work_item_id": str(work_item_id)
    }
    
    # Add changed_by_user_id if provided
    if changed_by_user_id:
        inputs["ado_changed_by_user_id"] = str(changed_by_user_id)
    
    payload = {
        "ref": workflow_ref,  # Use configured branch
        "inputs": inputs
    }
    
    max_attempts = 3
    backoff_delays = [2, 6, 14]  # seconds (exponential: 2, 4+2, 8+6)
    
    for attempt in range(max_attempts):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 204:
                logger.info(f"Successfully dispatched workflow for work item {work_item_id} (attempt {attempt + 1})")
                return True, "dispatched"
            elif response.status_code in [401, 403, 404, 422]:
                # Client errors - don't retry
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.error(f"Dispatch failed (client error, no retry): {error_msg}")
                return False, error_msg
            else:
                # Server error - retry
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                if attempt < max_attempts - 1:
                    delay = backoff_delays[attempt]
                    logger.warning(f"Dispatch failed (attempt {attempt + 1}), retrying in {delay}s: {error_msg}")
                    time.sleep(delay)
                else:
                    logger.error(f"Dispatch failed after {max_attempts} attempts: {error_msg}")
                    return False, error_msg
                    
        except requests.exceptions.Timeout:
            if attempt < max_attempts - 1:
                delay = backoff_delays[attempt]
                logger.warning(f"Timeout (attempt {attempt + 1}), retrying in {delay}s")
                time.sleep(delay)
            else:
                return False, "GitHub API timeout after 3 attempts"
        except requests.exceptions.RequestException as e:
            if attempt < max_attempts - 1:
                delay = backoff_delays[attempt]
                logger.warning(f"Request error (attempt {attempt + 1}), retrying in {delay}s: {str(e)}")
                time.sleep(delay)
            else:
                return False, f"Request error after 3 attempts: {str(e)}"
    
    return False, "Max retry attempts exceeded"


