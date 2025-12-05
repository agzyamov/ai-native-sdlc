#!/usr/bin/env python3
"""
Test script for get_child_issues() and get_work_item_comments() functions.
Tests against real Azure DevOps instance using local.settings.json credentials.
"""
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from local.settings.json
settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "local.settings.json")
if os.path.exists(settings_path):
    with open(settings_path) as f:
        settings = json.load(f)
        for key, value in settings.get("Values", {}).items():
            os.environ[key] = value
    print(f"✓ Loaded settings from {settings_path}")
else:
    print(f"✗ Settings file not found: {settings_path}")
    sys.exit(1)

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from ado_client import get_child_issues, get_work_item_comments, get_work_item


def test_get_child_issues(feature_id: int):
    """Test fetching closed child issues for a feature."""
    print(f"\n{'='*60}")
    print(f"Testing get_child_issues(feature_id={feature_id})")
    print('='*60)
    
    issues = get_child_issues(feature_id)
    
    if issues:
        print(f"✓ Found {len(issues)} closed Issues:")
        for issue in issues:
            print(f"  - Issue #{issue['id']}: {issue['title'][:60]}...")
            if issue['description']:
                desc_preview = issue['description'][:100].replace('\n', ' ')
                print(f"    Description: {desc_preview}...")
    else:
        print("✓ No closed Issues found (or error occurred)")
    
    return issues


def test_get_work_item_comments(work_item_id: int):
    """Test fetching comments for a work item."""
    print(f"\n{'='*60}")
    print(f"Testing get_work_item_comments(work_item_id={work_item_id})")
    print('='*60)
    
    comments = get_work_item_comments(work_item_id)
    
    if comments:
        print(f"✓ Found {len(comments)} comments:")
        for i, comment in enumerate(comments, 1):
            comment_preview = comment[:100].replace('\n', ' ')
            print(f"  {i}. {comment_preview}...")
    else:
        print("✓ No comments found (or error occurred)")
    
    return comments


def test_full_context_enrichment(feature_id: int):
    """Test the full context enrichment flow as used in function_app.py"""
    print(f"\n{'='*60}")
    print(f"Testing full context enrichment for Feature #{feature_id}")
    print('='*60)
    
    # First, get the feature itself
    feature = get_work_item(feature_id)
    if feature:
        title = feature.get("fields", {}).get("System.Title", "")
        description = feature.get("fields", {}).get("System.Description", "")
        print(f"✓ Feature: {title}")
        print(f"  Description length: {len(description)} chars")
    else:
        print("✗ Could not fetch feature")
        return
    
    # Get closed child issues
    closed_issues = get_child_issues(feature_id)
    
    if not closed_issues:
        print("ℹ No closed Issues to enrich context with")
        return
    
    # Build enriched context (same logic as function_app.py)
    closed_issues_context_parts = []
    for issue in closed_issues:
        issue_id = issue.get("id")
        issue_title = issue.get("title", "")
        issue_description = issue.get("description", "")
        
        # Format issue header
        issue_context = f"--- Closed Issue #{issue_id}: {issue_title} ---"
        
        # Add description if present
        if issue_description:
            issue_context += f"\nDescription: {issue_description}"
        
        # Fetch and add comments
        comments = get_work_item_comments(issue_id)
        if comments:
            issue_context += "\nComments:"
            for comment in comments:
                issue_context += f"\n- {comment}"
        
        closed_issues_context_parts.append(issue_context)
    
    # Build final enriched description
    if closed_issues_context_parts:
        closed_issues_context = "\n\n".join(closed_issues_context_parts)
        feature_description = description if description else title
        enriched_description = f"{feature_description}\n\n=== Previously Answered Clarifications ===\n\n{closed_issues_context}"
        
        print(f"\n✓ Enriched description created!")
        print(f"  Original length: {len(feature_description)} chars")
        print(f"  Enriched length: {len(enriched_description)} chars")
        print(f"  Added context: {len(enriched_description) - len(feature_description)} chars")
        
        print(f"\n--- Preview of enriched context (last 500 chars) ---")
        print(enriched_description[-500:])


if __name__ == "__main__":
    # Default feature ID to test with (can be overridden via command line)
    # Use a known Feature ID from the ADO project
    feature_id = 615  # Default test Feature ID
    
    if len(sys.argv) > 1:
        try:
            feature_id = int(sys.argv[1])
        except ValueError:
            print(f"Usage: {sys.argv[0]} [feature_id]")
            sys.exit(1)
    
    print(f"Testing with Feature ID: {feature_id}")
    print(f"ADO Organization: {os.getenv('ADO_ORG_URL')}")
    print(f"ADO Project: {os.getenv('ADO_PROJECT')}")
    
    # Run tests
    issues = test_get_child_issues(feature_id)
    
    # If we found issues, test comments on the first one
    if issues:
        test_get_work_item_comments(issues[0]['id'])
    
    # Test full enrichment flow
    test_full_context_enrichment(feature_id)
    
    print(f"\n{'='*60}")
    print("Tests completed!")
    print('='*60)
