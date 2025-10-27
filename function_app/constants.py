"""
Constants for Azure Function configuration.
"""

# Timeout values (seconds)
GITHUB_API_TIMEOUT = 15
ADO_API_TIMEOUT = 15
FUNCTION_MAX_EXECUTION_TIME = 30

# Retry configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_BACKOFF_DELAYS = [2, 6, 14]  # Exponential backoff in seconds

# Default configuration
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_SPEC_COLUMN_NAME = "Specification – Doing"
DEFAULT_AI_USER_MATCH = "AI Teammate"
DEFAULT_WORKFLOW_FILENAME = "spec-kit-specify.yml"
