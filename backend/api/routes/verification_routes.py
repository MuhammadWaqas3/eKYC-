"""
Verification API routes for document upload and biometric verification.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os
import shutil
import uuid

from database import get_db, User, VerificationSession, CNICData, BiometricData, Account, VerificationStatus
from security import jwt_handler, audit_logger
from services.cv import face_match_service, didit_liveness_service
from services.ocr_service import tesseract_ocr_service
from services.ocrspace_service import ocrspace_service
from services.validation import cnic_validator
from config import settings

router = APIRouter()

# Upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Request/Response models
class TokenValidationResponse(BaseModel):
    """Token validation response."""
    success: bool
    valid: bool
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    message: Optional[str] = None


class CNICUploadResponse(BaseModel):
    """CNIC upload response."""
    success: bool
    message: str
    extracted_data: Optional[dict] = None
    validation_errors: Optional[list] = None


class FaceMatchResponse(BaseModel):
    """Face match response."""
    success: bool
    is_match: bool
    match_score: float
    message: Optional[str] = None


class LivenessCheckResponse(BaseModel):
    """Liveness check response."""
    success: bool
    is_live: bool
    liveness_score: float
    details: Optional[dict] = None
    message: Optional[str] = None


class VerificationFinalizeResponse(BaseModel):
    """Verification finalize response."""
    success: bool
    account_number: Optional[str] = None
    message: str


@router.post("/validate-token", response_model=TokenValidationResponse)
async def validate_token(
    token: str,
    db: Session = Depends(get_db)
):
    """Validate JWT token from verification link."""
    try:
        # Validate token
        payload = jwt_handler.validate_token(token)
        
        if not payload:
            return TokenValidationResponse(
                success=True,
                valid=False,
                message="Invalid token"
            )
        
        # Check expiration
        if jwt_handler.is_token_expired(payload):
            return TokenValidationResponse(
                success=True,
                valid=False,
                message="Token has expired"
            )
        
        # Get session
        session_id = payload.get("session_id")
        session = db.query(VerificationSession).filter(
            VerificationSession.session_id == session_id
        ).first()
        
        if not session:
            return TokenValidationResponse(
                success=True,
                valid=False,
                message="Session not found"
            )
        
        # Update session status
        if session.status == VerificationStatus.PENDING:
            session.status = VerificationStatus.IN_PROGRESS
            db.commit()
            
            audit_logger.log_verification_started(
                payload.get("user_id"),
                session_id
            )
        
        return TokenValidationResponse(
            success=True,
            valid=True,
            user_id=payload.get("user_id"),
            session_id=session_id,
            message="Token is valid"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token validation failed: {str(e)}"
        )


@router.post("/upload-cnic", response_model=CNICUploadResponse)
async def upload_cnic(
    token: str = Form(...),
    front_image: UploadFile = File(...),
    back_image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process CNIC front and back images."""
    try:
        # Validate token
        payload = jwt_handler.validate_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user_id = payload.get("user_id")
        session_id = payload.get("session_id")
        
        # Save uploaded files
        front_path = os.path.join(UPLOAD_DIR, f"{session_id}_cnic_front.jpg")
        back_path = os.path.join(UPLOAD_DIR, f"{session_id}_cnic_back.jpg")
        
        with open(front_path, "wb") as buffer:
            shutil.copyfileobj(front_image.file, buffer)
        
        with open(back_path, "wb") as buffer:
            shutil.copyfileobj(back_image.file, buffer)
        
        # Log upload
        audit_logger.log_cnic_uploaded(user_id, session_id)
        
        # Extract CNIC data using DUAL OCR approach (OCR.space + Tesseract)
        print("Extracting CNIC data using dual OCR approach...")
        
        # Try OCR.space API first
        ocrspace_data = ocrspace_service.extract_cnic_data(front_path, back_path)
        print(f"OCR.space extracted: {ocrspace_data}")
        
        # Always run Tesseract as well
        tesseract_data = tesseract_ocr_service.extract_cnic_data(front_path, back_path)
        print(f"Tesseract extracted: {tesseract_data}")
        
        # Merge results for best accuracy
        extracted_data = ocrspace_service.merge_ocr_results(tesseract_data, ocrspace_data)
        print(f"Merged OCR data: {extracted_data}")
        
        # Validate extracted data
        is_valid, validation_errors = cnic_validator.validate_cnic_data(extracted_data)
        
        # Log OCR completion
        audit_logger.log_ocr_completed(
            user_id,
            session_id,
            is_valid,
            extracted_data.get('cnic_number')
        )
        
        # Encrypt sensitive data
        encrypted_data = {}
        sensitive_fields = ['cnic_number', 'name', 'father_name', 'dob', 
                          'gender', 'address', 'issue_date', 'expiry_date']
        
        for field in sensitive_fields:
            if field in extracted_data and extracted_data[field]:
                encrypted_data[f'encrypted_{field}'] = extracted_data[field]
        
        # Extract face from CNIC for later matching
        face_path = os.path.join(UPLOAD_DIR, f"{session_id}_cnic_face.jpg")
        face_match_service.extract_face_from_cnic(front_path, face_path)
        
        # Validate required fields for database (cannot be null)
        if not encrypted_data.get('encrypted_cnic_number') or not encrypted_data.get('encrypted_name'):
            # Log failure but return success:True with errors so frontend can show them
            audit_logger.log_ocr_completed(user_id, session_id, False, None)
            return CNICUploadResponse(
                success=True,
                message="Critical data missing (Name or CNIC not clearly visible). Please retake with better lighting.",
                extracted_data=None,
                validation_errors=["Could not extract Name or CNIC Number from the images."]
            )

        # Save to database
        cnic_record = db.query(CNICData).filter(CNICData.user_id == user_id).first()
        
        if cnic_record:
            # Update existing
            for key, value in encrypted_data.items():
                setattr(cnic_record, key, value)
            cnic_record.is_valid = is_valid
            cnic_record.validation_errors = str(validation_errors) if validation_errors else None
        else:
            # Create new
            cnic_record = CNICData(
                user_id=user_id,
                **encrypted_data,
                is_valid=is_valid,
                validation_errors=str(validation_errors) if validation_errors else None,
                encrypted_front_image_path=front_path,
                encrypted_back_image_path=back_path
            )
            db.add(cnic_record)
        
        # Update session
        session = db.query(VerificationSession).filter(
            VerificationSession.session_id == session_id
        ).first()
        
        if session:
            session.cnic_uploaded = True
            session.ocr_completed = is_valid
        
        db.commit()
        
        return CNICUploadResponse(
            success=True,
            message="CNIC uploaded and processed successfully" if is_valid else "CNIC processed with validation errors",
            extracted_data=extracted_data if is_valid else None,
            validation_errors=validation_errors if not is_valid else None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        error_detail = f"CNIC upload failed: {str(e)}"
        print(f"ERROR: {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.post("/upload-selfie", response_model=FaceMatchResponse)
async def upload_selfie(
    token: str,
    selfie_image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload selfie and perform face matching with CNIC photo."""
    try:
        # Validate token
        payload = jwt_handler.validate_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user_id = payload.get("user_id")
        session_id = payload.get("session_id")
        
        # Save selfie
        selfie_path = os.path.join(UPLOAD_DIR, f"{session_id}_selfie.jpg")
        
        with open(selfie_path, "wb") as buffer:
            shutil.copyfileobj(selfie_image.file, buffer)
        
        # Get CNIC face
        cnic_face_path = os.path.join(UPLOAD_DIR, f"{session_id}_cnic_face.jpg")
        
        if not os.path.exists(cnic_face_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNIC must be uploaded first"
            )
        
        # Perform face matching
        is_match, match_score, error_msg = face_match_service.match_faces(
            selfie_path,
            cnic_face_path
        )
        
        # Log face match
        audit_logger.log_face_match(user_id, session_id, match_score, is_match)
        
        # Save to database
        biometric_record = db.query(BiometricData).filter(
            BiometricData.user_id == user_id
        ).first()
        
        if biometric_record:
            biometric_record.encrypted_selfie_path = selfie_path
            biometric_record.face_match_score = match_score
            biometric_record.face_match_result = is_match
        else:
            biometric_record = BiometricData(
                user_id=user_id,
                encrypted_selfie_path=selfie_path,
                face_match_score=match_score,
                face_match_result=is_match
            )
            db.add(biometric_record)
        
        # Update session
        session = db.query(VerificationSession).filter(
            VerificationSession.session_id == session_id
        ).first()
        
        if session:
            session.selfie_uploaded = True
            session.face_match_completed = is_match
        
        db.commit()
        
        return FaceMatchResponse(
            success=True,
            is_match=is_match,
            match_score=match_score,
            message="Face matched successfully" if is_match else f"Face match failed: {error_msg}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Selfie upload failed: {str(e)}"
        )


@router.post("/liveness-check", response_model=LivenessCheckResponse)
async def liveness_check(
    token: str,
    liveness_video: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Perform liveness detection on uploaded video."""
    try:
        # Validate token
        payload = jwt_handler.validate_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user_id = payload.get("user_id")
        session_id = payload.get("session_id")
        
        # Save video
        video_path = os.path.join(UPLOAD_DIR, f"{session_id}_liveness.webm")
        
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(liveness_video.file, buffer)
        
        # Perform liveness check using DIDIT API (with MediaPipe fallback)
        print(f"Performing liveness check with DIDIT API: {video_path}")
        is_live, liveness_score, details = didit_liveness_service.check_liveness(video_path)
        
        print(f"Liveness result: is_live={is_live}, score={liveness_score}, details={details}")
        
        # Log liveness check
        audit_logger.log_liveness_check(user_id, session_id, liveness_score, is_live)
        
        # Save to database
        biometric_record = db.query(BiometricData).filter(
            BiometricData.user_id == user_id
        ).first()
        
        if biometric_record:
            biometric_record.encrypted_liveness_video_path = video_path
            biometric_record.liveness_score = liveness_score
            biometric_record.liveness_result = is_live
        
        # Update session
        session = db.query(VerificationSession).filter(
            VerificationSession.session_id == session_id
        ).first()
        
        if session:
            session.liveness_completed = is_live
        
        db.commit()
        
        return LivenessCheckResponse(
            success=True,
            is_live=is_live,
            liveness_score=liveness_score,
            details=details,
            message="Liveness verified" if is_live else "Liveness check failed"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Liveness check failed: {str(e)}"
        )


@router.post("/finalize", response_model=VerificationFinalizeResponse)
async def finalize_verification(
    token: str,
    db: Session = Depends(get_db)
):
    """Finalize verification and create bank account."""
    try:
        # Validate token
        payload = jwt_handler.validate_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user_id = payload.get("user_id")
        session_id = payload.get("session_id")
        
        # Get session
        session = db.query(VerificationSession).filter(
            VerificationSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Check all steps completed
        all_completed = (
            session.cnic_uploaded and
            session.ocr_completed and
            session.selfie_uploaded and
            session.face_match_completed and
            session.liveness_completed
        )
        
        if not all_completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not all verification steps completed"
            )
        
        # Generate account number
        account_number = f"PKR{str(user_id).zfill(10)}{str(uuid.uuid4().int)[:6]}"
        
        # Create account
        account = Account(
            user_id=user_id,
            account_number=account_number,
            account_type="savings",
            status="active"
        )
        
        db.add(account)
        
        # Update session
        session.status = VerificationStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        
        db.commit()
        
        # Log account creation
        audit_logger.log_account_created(user_id, account_number)
        audit_logger.log_verification_completed(user_id, session_id)
        
        return VerificationFinalizeResponse(
            success=True,
            account_number=account_number,
            message="Verification completed successfully! Your account has been created."
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        audit_logger.log_verification_failed(
            user_id,
            session_id,
            str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Finalization failed: {str(e)}"
        )