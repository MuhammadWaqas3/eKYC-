"""
Admin API routes for monitoring and management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db, User, VerificationSession, Account, AuditLog, VerificationStatus

router = APIRouter()


# Response models
class UserInfo(BaseModel):
    """User information model."""
    id: int
    name: str
    email: str
    phone: str
    created_at: datetime
    account_number: Optional[str] = None
    verification_status: Optional[str] = None


class AuditLogEntry(BaseModel):
    """Audit log entry model."""
    id: int
    user_id: Optional[int]
    session_id: Optional[str]
    event_type: str
    event_data: Optional[str]
    created_at: datetime


class SystemStats(BaseModel):
    """System statistics model."""
    total_users: int
    total_accounts: int
    pending_verifications: int
    completed_verifications: int
    failed_verifications: int
    today_registrations: int
    today_completions: int


@router.get("/users", response_model=List[UserInfo])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get list of users with pagination.
    
    For admin monitoring purposes.
    """
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        
        user_list = []
        for user in users:
            # Get latest verification session
            latest_session = db.query(VerificationSession).filter(
                VerificationSession.user_id == user.id
            ).order_by(desc(VerificationSession.created_at)).first()
            
            # Get account if exists
            account = db.query(Account).filter(Account.user_id == user.id).first()
            
            user_info = UserInfo(
                id=user.id,
                name=user.name,
                email=user.email,
                phone=user.phone,
                created_at=user.created_at,
                account_number=account.account_number if account else None,
                verification_status=latest_session.status.value if latest_session else "not_started"
            )
            
            user_list.append(user_info)
        
        return user_list
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )


@router.get("/audit-logs", response_model=List[AuditLogEntry])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = None,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get audit logs with optional filtering.
    
    For compliance and security monitoring.
    """
    try:
        query = db.query(AuditLog)
        
        # Apply filters
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        
        # Order by most recent
        logs = query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit).all()
        
        log_entries = [
            AuditLogEntry(
                id=log.id,
                user_id=log.user_id,
                session_id=log.session_id,
                event_type=log.event_type,
                event_data=log.event_data,
                created_at=log.created_at
            )
            for log in logs
        ]
        
        return log_entries
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch audit logs: {str(e)}"
        )


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    db: Session = Depends(get_db)
):
    """
    Get system statistics for dashboard.
    
    Provides overview of system usage and verification status.
    """
    try:
        # Calculate date for "today"
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Total users
        total_users = db.query(func.count(User.id)).scalar()
        
        # Total accounts
        total_accounts = db.query(func.count(Account.id)).scalar()
        
        # Verification statistics
        pending_verifications = db.query(func.count(VerificationSession.id)).filter(
            VerificationSession.status.in_([VerificationStatus.PENDING, VerificationStatus.IN_PROGRESS])
        ).scalar()
        
        completed_verifications = db.query(func.count(VerificationSession.id)).filter(
            VerificationSession.status == VerificationStatus.COMPLETED
        ).scalar()
        
        failed_verifications = db.query(func.count(VerificationSession.id)).filter(
            VerificationSession.status == VerificationStatus.FAILED
        ).scalar()
        
        # Today's registrations
        today_registrations = db.query(func.count(User.id)).filter(
            User.created_at >= today_start
        ).scalar()
        
        # Today's completions
        today_completions = db.query(func.count(VerificationSession.id)).filter(
            VerificationSession.status == VerificationStatus.COMPLETED,
            VerificationSession.completed_at >= today_start
        ).scalar()
        
        return SystemStats(
            total_users=total_users,
            total_accounts=total_accounts,
            pending_verifications=pending_verifications,
            completed_verifications=completed_verifications,
            failed_verifications=failed_verifications,
            today_registrations=today_registrations,
            today_completions=today_completions
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch statistics: {str(e)}"
        )
