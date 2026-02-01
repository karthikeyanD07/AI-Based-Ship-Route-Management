"""Structured logging configuration."""
import logging
import sys
import json
from pythonjsonlogger import jsonlogger
from backend.app.config.settings import settings


class StructuredFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = self.formatTime(record, self.datefmt)
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno
        
        # Add request ID if available
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id


def setup_structured_logging():
    """Setup structured JSON logging."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Create JSON formatter
    formatter = StructuredFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional, for production)
    if not settings.DEBUG:
        try:
            file_handler = logging.FileHandler("app.log")
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception:
            pass  # File logging is optional
    
    return root_logger
