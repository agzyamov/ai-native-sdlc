"""
Shared function modules for spec-dispatch Azure Function.
This package contains validation, dispatch, and configuration logic.
"""

# Export public API for easier imports
from .validation import validate_event
from .dispatch import dispatch_workflow
from .config import get_config
from .models import WorkItemEvent
from .ado_client import get_work_item
from .util import generate_correlation_id

__all__ = [
    "validate_event",
    "dispatch_workflow", 
    "get_config",
    "WorkItemEvent",
    "get_work_item",
    "generate_correlation_id"
]
