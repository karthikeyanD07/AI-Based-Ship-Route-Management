"""Audit logging utility."""
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import Request
from backend.app.services.db_service import db_service
from backend.app.models.database import AuditLog, get_db_session

logger = logging.getLogger(__name__)


class AuditLogger:
    """Log user actions for audit trail."""
    
    @staticmethod
    def log_action(
        action: str,
        request: Request,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        resource: Optional[str] = None,
        resource_id: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log an audit event.
        
        Args:
            action: Action performed (e.g., "ship_view", "route_create")
            request: FastAPI request object
            user_id: User ID if authenticated
            username: Username if authenticated
            resource: Resource type (e.g., "ship", "route")
            resource_id: Resource identifier
            status_code: HTTP status code
            details: Additional details as dict
        """
        try:
            # Get request metadata
            request_id = getattr(request.state, "request_id", None)
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent", "")
            
            # Create audit log entry
            audit_entry = {
                "user_id": user_id,
                "username": username,
                "action": action,
                "resource": resource,
                "resource_id": resource_id,
                "ip_address": ip_address,
                "user_agent": user_agent[:500],  # Limit length
                "request_id": request_id,
                "status_code": status_code,
                "details": json.dumps(details) if details else None,
                "created_at": datetime.utcnow()
            }
            
            # Save to database if available
            if db_service.is_available():
                try:
                    with get_db_session() as db:
                        db_audit = AuditLog(**audit_entry)
                        db.add(db_audit)
                        db.commit()
                except Exception as e:
                    logger.error(f"Failed to save audit log: {e}")
            
            # Also log to application log
            logger.info(
                f"Audit: {action} by {username or 'anonymous'} "
                f"on {resource or 'unknown'} "
                f"(status: {status_code})"
            )
            
        except Exception as e:
            logger.error(f"Error in audit logging: {e}", exc_info=True)


# Global audit logger instance
audit_logger = AuditLogger()
