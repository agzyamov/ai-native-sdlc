"""
Utility functions for Azure Function.
"""
import uuid


def generate_correlation_id() -> str:
    """
    Generate a unique correlation ID for request tracking.
    
    Returns:
        UUID4 string
    """
    return str(uuid.uuid4())
