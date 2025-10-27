"""
Unit tests for GitHub dispatch logic.
"""
import os
from unittest import mock

import pytest
import requests

from function_app.dispatch import dispatch_workflow


@mock.patch("function_app.dispatch.requests.post")
def test_dispatch_workflow_success(mock_post):
    """Test successful workflow dispatch."""
    os.environ["GITHUB_OWNER"] = "test-owner"
    os.environ["GITHUB_REPO"] = "test-repo"
    os.environ["GH_WORKFLOW_DISPATCH_PAT"] = "test-pat"
    
    # Mock successful response
    mock_response = mock.Mock()
    mock_response.status_code = 204
    mock_post.return_value = mock_response
    
    success, message = dispatch_workflow(
        work_item_id=123,
        branch_hint="feature/wi-123"
    )
    
    assert success is True
    assert message == "dispatched"
    mock_post.assert_called_once()


@mock.patch("function_app.dispatch.requests.post")
def test_dispatch_workflow_missing_env_vars(mock_post):
    """Test dispatch fails with missing environment variables."""
    # Clear env vars
    for var in ["GITHUB_OWNER", "GITHUB_REPO", "GH_WORKFLOW_DISPATCH_PAT"]:
        os.environ.pop(var, None)
    
    success, message = dispatch_workflow(
        work_item_id=123,
        branch_hint="feature/wi-123"
    )
    
    assert success is False
    assert "Missing required environment variables" in message
    mock_post.assert_not_called()


@mock.patch("function_app.dispatch.requests.post")
def test_dispatch_workflow_client_error_no_retry(mock_post):
    """Test dispatch doesn't retry on client errors (404, 401, etc.)."""
    os.environ["GITHUB_OWNER"] = "test-owner"
    os.environ["GITHUB_REPO"] = "test-repo"
    os.environ["GH_WORKFLOW_DISPATCH_PAT"] = "test-pat"
    
    # Mock 404 response
    mock_response = mock.Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_post.return_value = mock_response
    
    success, message = dispatch_workflow(
        work_item_id=123,
        branch_hint="feature/wi-123"
    )
    
    assert success is False
    assert "HTTP 404" in message
    # Should only call once (no retries for client errors)
    assert mock_post.call_count == 1


@mock.patch("function_app.dispatch.requests.post")
@mock.patch("function_app.dispatch.time.sleep")
def test_dispatch_workflow_retry_on_500(mock_sleep, mock_post):
    """Test dispatch retries on server errors (500)."""
    os.environ["GITHUB_OWNER"] = "test-owner"
    os.environ["GITHUB_REPO"] = "test-repo"
    os.environ["GH_WORKFLOW_DISPATCH_PAT"] = "test-pat"
    
    # Mock 500 response on first two attempts, success on third
    mock_response_500 = mock.Mock()
    mock_response_500.status_code = 500
    mock_response_500.text = "Internal Server Error"
    
    mock_response_204 = mock.Mock()
    mock_response_204.status_code = 204
    
    mock_post.side_effect = [mock_response_500, mock_response_500, mock_response_204]
    
    success, message = dispatch_workflow(
        work_item_id=123,
        branch_hint="feature/wi-123"
    )
    
    assert success is True
    assert message == "dispatched"
    # Should call 3 times (2 failures + 1 success)
    assert mock_post.call_count == 3
    # Should sleep twice (after first two failures)
    assert mock_sleep.call_count == 2


@mock.patch("function_app.dispatch.requests.post")
def test_dispatch_workflow_timeout(mock_post):
    """Test dispatch handles timeout."""
    os.environ["GITHUB_OWNER"] = "test-owner"
    os.environ["GITHUB_REPO"] = "test-repo"
    os.environ["GH_WORKFLOW_DISPATCH_PAT"] = "test-pat"
    
    # Mock timeout exception
    mock_post.side_effect = requests.exceptions.Timeout()
    
    success, message = dispatch_workflow(
        work_item_id=123,
        branch_hint="feature/wi-123"
    )
    
    assert success is False
    assert "timeout" in message.lower()
    # Should retry 3 times
    assert mock_post.call_count == 3
