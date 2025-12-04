# Python Coding Standards

## Code Quality Standards

When writing Python code, always:

1. **Follow PEP 8** style guidelines
2. **Use type hints** where appropriate
3. **Add docstrings** to all functions, classes, and modules
4. **Keep line length** to 100 characters maximum

## Linting Requirements

All Python code must pass these linters without errors:

- **flake8** with `--max-line-length=100`
- **pylint** with `--max-line-length=100`

### Common Issues to Avoid

- No trailing whitespace on blank lines
- No blank line at end of file (only newline)
- Import order: standard library → third-party → local
- Always add `timeout` parameter to HTTP requests
- Remove f-strings without placeholders

## Code Formatting

- Use 4 spaces for indentation
- Blank lines: 2 between top-level definitions, 1 between methods
- Consistent quote style (prefer single quotes unless needed)

## Best Practices

- Add timeout to all network requests (e.g., `requests.get(..., timeout=30)`)
- Use context managers for file operations
- Handle exceptions explicitly
- Validate user input
- Log important operations

Always run linters before committing code!

## Type Hints

Use type hints for function parameters and return values:

```python
from typing import Optional, Tuple

def validate_event(event: dict) -> Tuple[bool, str]:
    """
    Validate if the event should trigger spec generation.
    
    Args:
        event: Raw Service Hook payload (dictionary)
    
    Returns:
        Tuple of (is_valid, reason)
    """
    # Implementation
```

## Docstrings

All functions, classes, and modules must have docstrings:

```python
"""
Module-level docstring describing the module's purpose.
"""

class Config:
    """Configuration loader for Azure Function environment variables."""
    
    def validate(self) -> Tuple[bool, list[str]]:
        """
        Validate required configuration is present.
        
        Returns:
            Tuple of (is_valid, missing_vars)
        """
        # Implementation
```

## Import Organization

Organize imports in this order:
1. Standard library imports
2. Third-party imports
3. Local application imports

```python
import json
import logging
import os
from datetime import datetime
from typing import Optional

import azure.functions as func
import requests

import validation
import dispatch
import config
```

## Error Handling

Handle exceptions explicitly with appropriate logging:

```python
try:
    result = process_data(data)
except ValueError as e:
    logger.error(f"Validation failed: {e}")
    raise
except Exception as e:
    logger.exception("Unexpected error occurred")
    raise
```

## Logging

Use structured logging with appropriate levels:

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Detailed debugging information")
logger.info("General informational message")
logger.warning("Warning message")
logger.error("Error occurred")
logger.exception("Exception with traceback")
```

## Related Rules

- See [azure-functions.md](azure-functions.md) for Azure Functions-specific patterns
- See [ado-integration.md](ado-integration.md) for ADO client patterns

