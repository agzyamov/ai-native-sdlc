#!/usr/bin/env python3
"""
Unit tests for get_child_issues() and get_work_item_comments() functions.
Uses mocked API responses.
"""
import os
import sys
from unittest import mock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set required environment variables for tests
os.environ["ADO_ORG_URL"] = "https://dev.azure.com/TestOrg"
os.environ["ADO_PROJECT"] = "TestProject"
os.environ["ADO_WORK_ITEM_PAT"] = "test-pat-123"

import pytest
from ado_client import get_child_issues, get_work_item_comments


class TestGetChildIssues:
    """Tests for get_child_issues function."""
    
    @mock.patch("ado_client.requests.get")
    @mock.patch("ado_client.requests.post")
    def test_get_child_issues_success(self, mock_post, mock_get):
        """Test successful fetch of closed child Issues."""
        # Mock WIQL response
        mock_wiql_response = mock.Mock()
        mock_wiql_response.status_code = 200
        mock_wiql_response.json.return_value = {
            "workItems": [
                {"id": 101},
                {"id": 102}
            ]
        }
        mock_post.return_value = mock_wiql_response
        
        # Mock batch fetch response
        mock_batch_response = mock.Mock()
        mock_batch_response.status_code = 200
        mock_batch_response.json.return_value = {
            "value": [
                {
                    "id": 101,
                    "fields": {
                        "System.Title": "Clarification Q1: How should users interact?",
                        "System.Description": "Touch or keyboard?"
                    }
                },
                {
                    "id": 102,
                    "fields": {
                        "System.Title": "Clarification Q2: What platform?",
                        "System.Description": "Web, mobile, or desktop?"
                    }
                }
            ]
        }
        mock_get.return_value = mock_batch_response
        
        # Call function
        result = get_child_issues(615)
        
        # Verify
        assert len(result) == 2
        assert result[0]["id"] == 101
        assert result[0]["title"] == "Clarification Q1: How should users interact?"
        assert result[0]["description"] == "Touch or keyboard?"
        assert result[1]["id"] == 102
        
        # Verify WIQL query was called with correct parameters
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "wiql" in call_args[0][0]
        assert "System.State" in str(call_args[1]["json"])
        assert "Closed" in str(call_args[1]["json"])
    
    @mock.patch("ado_client.requests.post")
    def test_get_child_issues_no_results(self, mock_post):
        """Test when no closed Issues are found."""
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"workItems": []}
        mock_post.return_value = mock_response
        
        result = get_child_issues(615)
        
        assert result == []
    
    @mock.patch("ado_client.requests.post")
    def test_get_child_issues_api_error(self, mock_post):
        """Test graceful handling of API errors."""
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response
        
        result = get_child_issues(615)
        
        assert result == []
    
    def test_get_child_issues_missing_env_vars(self):
        """Test graceful handling when env vars are missing."""
        # Temporarily clear env vars
        orig_url = os.environ.pop("ADO_ORG_URL", None)
        
        result = get_child_issues(615)
        
        assert result == []
        
        # Restore env var
        if orig_url:
            os.environ["ADO_ORG_URL"] = orig_url


class TestGetWorkItemComments:
    """Tests for get_work_item_comments function."""
    
    @mock.patch("ado_client.requests.get")
    def test_get_comments_success(self, mock_get):
        """Test successful fetch of comments."""
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "comments": [
                {"text": "Users should interact via touch gestures."},
                {"text": "Also consider keyboard support for accessibility."},
                {"text": "  "}  # Empty comment should be filtered
            ]
        }
        mock_get.return_value = mock_response
        
        result = get_work_item_comments(101)
        
        assert len(result) == 2
        assert result[0] == "Users should interact via touch gestures."
        assert result[1] == "Also consider keyboard support for accessibility."
    
    @mock.patch("ado_client.requests.get")
    def test_get_comments_no_comments(self, mock_get):
        """Test when no comments exist."""
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"comments": []}
        mock_get.return_value = mock_response
        
        result = get_work_item_comments(101)
        
        assert result == []
    
    @mock.patch("ado_client.requests.get")
    def test_get_comments_api_error(self, mock_get):
        """Test graceful handling of API errors."""
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response
        
        result = get_work_item_comments(101)
        
        assert result == []


class TestContextEnrichmentIntegration:
    """Integration test for the full context enrichment flow."""
    
    @mock.patch("ado_client.requests.get")
    @mock.patch("ado_client.requests.post")
    def test_full_context_enrichment(self, mock_post, mock_get):
        """Test building enriched context from closed Issues and comments."""
        # Mock WIQL response for get_child_issues
        mock_wiql_response = mock.Mock()
        mock_wiql_response.status_code = 200
        mock_wiql_response.json.return_value = {
            "workItems": [{"id": 101}, {"id": 102}]
        }
        mock_post.return_value = mock_wiql_response
        
        # Set up mock_get to return different responses based on URL
        def get_side_effect(url, **kwargs):
            mock_resp = mock.Mock()
            mock_resp.status_code = 200
            
            if "workitems?" in url and "ids=" in url:
                # Batch work items fetch
                mock_resp.json.return_value = {
                    "value": [
                        {
                            "id": 101,
                            "fields": {
                                "System.Title": "Q1: Touch or keyboard?",
                                "System.Description": "How should users interact?"
                            }
                        },
                        {
                            "id": 102,
                            "fields": {
                                "System.Title": "Q2: Platform?",
                                "System.Description": "What platform to target?"
                            }
                        }
                    ]
                }
            elif "101/comments" in url:
                mock_resp.json.return_value = {
                    "comments": [
                        {"text": "Use touch gestures primarily."},
                        {"text": "Keyboard for accessibility."}
                    ]
                }
            elif "102/comments" in url:
                mock_resp.json.return_value = {
                    "comments": [
                        {"text": "Target iOS and Android."}
                    ]
                }
            else:
                mock_resp.json.return_value = {}
            
            return mock_resp
        
        mock_get.side_effect = get_side_effect
        
        # Simulate the context enrichment logic from function_app.py
        feature_description = "Build a hockey simulator game"
        closed_issues = get_child_issues(615)
        
        assert len(closed_issues) == 2
        
        closed_issues_context_parts = []
        for issue in closed_issues:
            issue_id = issue.get("id")
            issue_title = issue.get("title", "")
            issue_description = issue.get("description", "")
            
            issue_context = f"--- Closed Issue #{issue_id}: {issue_title} ---"
            
            if issue_description:
                issue_context += f"\nDescription: {issue_description}"
            
            comments = get_work_item_comments(issue_id)
            if comments:
                issue_context += "\nComments:"
                for comment in comments:
                    issue_context += f"\n- {comment}"
            
            closed_issues_context_parts.append(issue_context)
        
        # Build final enriched description
        closed_issues_context = "\n\n".join(closed_issues_context_parts)
        enriched_description = f"{feature_description}\n\n=== Previously Answered Clarifications ===\n\n{closed_issues_context}"
        
        # Verify the enriched description contains expected content
        assert "Build a hockey simulator game" in enriched_description
        assert "=== Previously Answered Clarifications ===" in enriched_description
        assert "--- Closed Issue #101: Q1: Touch or keyboard? ---" in enriched_description
        assert "Use touch gestures primarily." in enriched_description
        assert "Keyboard for accessibility." in enriched_description
        assert "--- Closed Issue #102: Q2: Platform? ---" in enriched_description
        assert "Target iOS and Android." in enriched_description
        
        print("\n✓ Enriched description preview:")
        print(enriched_description)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
