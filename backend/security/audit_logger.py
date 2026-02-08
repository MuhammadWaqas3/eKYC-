"""
Audit logging service for compliance and security tracking.
Logs all critical user actions and system events.
"""
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
from config import settings


class AuditLogger:
    """Audit logger for tracking user actions and system events."""
    
    # Event types
    USER_REGISTERED = "user_registered"
    VERIFICATION_LINK_GENERATED = "verification_link_generated"
    VERIFICATION_STARTED = "verification_started"
    CNIC_UPLOADED = "cnic_uploaded"
    OCR_COMPLETED = "ocr_completed"
    SELFIE_UPLOADED = "selfie_uploaded"
    FACE_MATCH_COMPLETED = "face_match_completed"
    LIVENESS_CHECK_COMPLETED = "liveness_check_completed"
    FINGERPRINT_CAPTURED = "fingerprint_captured"
    VERIFICATION_COMPLETED = "verification_completed"
    VERIFICATION_FAILED = "verification_failed"
    ACCOUNT_CREATED = "account_created"
    DATA_VALIDATION_FAILED = "data_validation_failed"
    SECURITY_VIOLATION = "security_violation"
    
    def __init__(self):
        """Initialize audit logger."""
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration."""
        # Create logger
        logger = logging.getLogger("audit")
        logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # Create logs directory if it doesn't exist
        log_path = Path(settings.AUDIT_LOG_PATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # File handler for persistent logs
        file_handler = logging.FileHandler(settings.AUDIT_LOG_PATH)
        file_handler.setLevel(logging.INFO)
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # JSON formatter for structured logging
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_event(
        self,
        event_type: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        level: str = "INFO"
    ):
        """
        Log an audit event.
        
        Args:
            event_type: Type of event (use class constants)
            user_id: User ID associated with event
            session_id: Session ID associated with event
            data: Additional event data
            level: Log level (INFO, WARNING, ERROR)
        """
        log_entry = {
            "event_type": event_type,
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data or {}
        }
        
        # Convert to JSON string for logging
        log_message = json.dumps(log_entry)
        
        # Log at appropriate level
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(log_message)
    
    def log_user_registered(self, user_id: int, email: str, phone: str):
        """Log user registration event."""
        self.log_event(
            self.USER_REGISTERED,
            user_id=user_id,
            data={"email": email, "phone": phone}
        )
    
    def log_verification_link_generated(self, user_id: int, session_id: str):
        """Log verification link generation."""
        self.log_event(
            self.VERIFICATION_LINK_GENERATED,
            user_id=user_id,
            session_id=session_id
        )
    
    def log_verification_started(self, user_id: int, session_id: str):
        """Log verification process start."""
        self.log_event(
            self.VERIFICATION_STARTED,
            user_id=user_id,
            session_id=session_id
        )
    
    def log_cnic_uploaded(self, user_id: int, session_id: str):
        """Log CNIC upload."""
        self.log_event(
            self.CNIC_UPLOADED,
            user_id=user_id,
            session_id=session_id
        )
    
    def log_ocr_completed(
        self,
        user_id: int,
        session_id: str,
        success: bool,
        cnic_number: Optional[str] = None
    ):
        """Log OCR completion."""
        self.log_event(
            self.OCR_COMPLETED,
            user_id=user_id,
            session_id=session_id,
            data={"success": success, "cnic_number": cnic_number},
            level="INFO" if success else "WARNING"
        )
    
    def log_face_match(
        self,
        user_id: int,
        session_id: str,
        match_score: float,
        is_match: bool
    ):
        """Log face matching result."""
        self.log_event(
            self.FACE_MATCH_COMPLETED,
            user_id=user_id,
            session_id=session_id,
            data={"match_score": match_score, "is_match": is_match},
            level="INFO" if is_match else "WARNING"
        )
    
    def log_liveness_check(
        self,
        user_id: int,
        session_id: str,
        liveness_score: float,
        is_live: bool
    ):
        """Log liveness detection result."""
        self.log_event(
            self.LIVENESS_CHECK_COMPLETED,
            user_id=user_id,
            session_id=session_id,
            data={"liveness_score": liveness_score, "is_live": is_live},
            level="INFO" if is_live else "WARNING"
        )
    
    def log_verification_completed(self, user_id: int, session_id: str):
        """Log successful verification completion."""
        self.log_event(
            self.VERIFICATION_COMPLETED,
            user_id=user_id,
            session_id=session_id
        )
    
    def log_verification_failed(
        self,
        user_id: int,
        session_id: str,
        reason: str
    ):
        """Log verification failure."""
        self.log_event(
            self.VERIFICATION_FAILED,
            user_id=user_id,
            session_id=session_id,
            data={"reason": reason},
            level="WARNING"
        )
    
    def log_account_created(self, user_id: int, account_number: str):
        """Log account creation."""
        self.log_event(
            self.ACCOUNT_CREATED,
            user_id=user_id,
            data={"account_number": account_number}
        )
    
    def log_security_violation(
        self,
        event_description: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ):
        """Log security violation."""
        self.log_event(
            self.SECURITY_VIOLATION,
            user_id=user_id,
            data={"description": event_description, "ip_address": ip_address},
            level="ERROR"
        )


# Global audit logger instance
audit_logger = AuditLogger()
