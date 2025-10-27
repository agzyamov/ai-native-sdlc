"""
Structured logging abstraction for Azure Function.
"""
import json
import logging
import os
from typing import Any, Dict


class StructuredLogger:
    """
    Logger that outputs structured JSON logs.
    
    Usage:
        logger = StructuredLogger(__name__)
        logger.info("event_name", {"key": "value", "latency_ms": 123})
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.logger.setLevel(getattr(logging, self.log_level))
    
    def _log(self, level: str, event: str, data: Dict[str, Any]):
        """
        Internal log method that formats as JSON.
        
        Args:
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            event: Event name or type
            data: Additional structured data
        """
        log_entry = {
            "event": event,
            **data
        }
        
        # TODO (T054): Add log sampling strategy for high-volume events
        # Future: If event in SAMPLE_EVENTS and random() > sample_rate: return
        
        log_method = getattr(self.logger, level.lower())
        log_method(json.dumps(log_entry))
    
    def info(self, event: str, data: Dict[str, Any] = None):
        """Log INFO level message."""
        self._log("INFO", event, data or {})
    
    def warning(self, event: str, data: Dict[str, Any] = None):
        """Log WARNING level message."""
        self._log("WARNING", event, data or {})
    
    def error(self, event: str, data: Dict[str, Any] = None):
        """Log ERROR level message."""
        self._log("ERROR", event, data or {})
    
    def debug(self, event: str, data: Dict[str, Any] = None):
        """Log DEBUG level message."""
        self._log("DEBUG", event, data or {})
