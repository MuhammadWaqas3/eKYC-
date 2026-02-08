"""
Database models for eKYC application.
All sensitive data is stored encrypted.
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base


class VerificationStatus(str, enum.Enum):
    """Verification session status enum."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class User(Base):
    """User model for storing basic user information."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    verification_sessions = relationship("VerificationSession", back_populates="user")
    cnic_data = relationship("CNICData", back_populates="user", uselist=False)
    biometric_data = relationship("BiometricData", back_populates="user", uselist=False)
    account = relationship("Account", back_populates="user", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")



class VerificationSession(Base):
    """Verification session tracking."""
    __tablename__ = "verification_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(Text, nullable=False)
    status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    
    # Verification steps completed
    cnic_uploaded = Column(Boolean, default=False)
    ocr_completed = Column(Boolean, default=False)
    selfie_uploaded = Column(Boolean, default=False)
    face_match_completed = Column(Boolean, default=False)
    liveness_completed = Column(Boolean, default=False)
    fingerprint_captured = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="verification_sessions")


class CNICData(Base):
    """CNIC data extracted from OCR (encrypted)."""
    __tablename__ = "cnic_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # All sensitive fields stored encrypted
    encrypted_cnic_number = Column(Text, nullable=False)
    encrypted_name = Column(Text, nullable=False)
    encrypted_father_name = Column(Text, nullable=True)
    encrypted_dob = Column(Text, nullable=True)
    encrypted_gender = Column(Text, nullable=True)
    encrypted_address = Column(Text, nullable=True)
    encrypted_issue_date = Column(Text, nullable=True)
    encrypted_expiry_date = Column(Text, nullable=True)
    
    # Validation flags
    is_valid = Column(Boolean, default=False)
    validation_errors = Column(Text, nullable=True)  # JSON string
    
    # Image paths (stored encrypted)
    encrypted_front_image_path = Column(Text, nullable=True)
    encrypted_back_image_path = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="cnic_data")


class BiometricData(Base):
    """Biometric data storage (encrypted)."""
    __tablename__ = "biometric_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Face matching
    encrypted_selfie_path = Column(Text, nullable=True)
    face_match_score = Column(Float, nullable=True)
    face_match_result = Column(Boolean, default=False)
    
    # Liveness detection
    liveness_score = Column(Float, nullable=True)
    liveness_result = Column(Boolean, default=False)
    encrypted_liveness_video_path = Column(Text, nullable=True)
    
    # Fingerprint (placeholder for NADRA SDK integration)
    encrypted_fingerprint_data = Column(Text, nullable=True)
    fingerprint_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="biometric_data")


class Account(Base):
    """Bank account created after successful verification."""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    account_number = Column(String(20), unique=True, nullable=False)
    account_type = Column(String(50), default="savings")
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="account")


class AuditLog(Base):
    """Audit log for compliance tracking."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(255), nullable=True)
    event_type = Column(String(100), nullable=False, index=True)
    event_data = Column(Text, nullable=True)  # JSON string
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User", back_populates="audit_logs")


class ChatMessage(Base):
    """Store chat history between user and LLM."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) 
    session_id = Column(String(255), nullable=True, index=True) # For anonymous session tracking
    sender = Column(String(50), nullable=False) # 'user' or 'bot'
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="chat_messages")

