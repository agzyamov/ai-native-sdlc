"""
Shared function modules for spec-dispatch Azure Function.
This package contains validation, dispatch, and configuration logic.
"""

# Export public API for easier imports
from .ado_client import get_work_item
from .config import get_config
from .dispatch import dispatch_workflow
from .models import WorkItemEvent
from .util import generate_correlation_id
from .validation import validate_event

__all__ = [
    "WorkItemEvent",
    "dispatch_workflow",
    "generate_correlation_id",
    "get_config",
    "get_work_item",
    "validate_event",
]
