from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
import re
import httpx 
import shutil
import os

from database import get_db, User, VerificationSession, VerificationStatus, AuditLog, ChatMessage, Account, CNICData, BiometricData
from security import jwt_handler, audit_logger
from config import settings

router = APIRouter()

# --- Request/Response Models ---
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = None
    session_id: Optional[str] = None

class UserRegistrationRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    
    @validator('phone')
    def validate_phone(cls, v):
        cleaned = re.sub(r'[^\d+]', '', v)
        if not re.match(r'^\+92\d{10}$', cleaned):
            raise ValueError('Phone must be in format +92XXXXXXXXXX')
        return cleaned

class VerificationLinkResponse(BaseModel):
    success: bool
    verification_link: str
    session_id: str
    expires_at: str

# --- LLM Integration with Strict Instructions ---

async def call_llm_api(prompt: str, history: List[dict] = None):
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # System Prompt jo LLM ko control karega
    system_prompt = f"""
    You are the {settings.APP_NAME} Assistant. Your ONLY mission is to help users open a bank account by collecting:
    1. Full Name
    2. Email Address
    3. Phone Number (starting with +92)
    4. Account Type (Savings, Current, or Credit)

    PROCESS EXPLANATION:
    Tell the user that after providing these details, they will need to complete eKYC which includes:
    - CNIC Capture (Front & Back)
    - Real-time Face Verification
    - Fingerprint Scanning

    RULES:
    - Be professional and helpful.
    - If any info (Name, Email, Phone, Account Type) is missing, ask for it politely.
    - Check the conversation history to see what info you already have. DO NOT ASK FOR INFO ALREADY GIVEN.
    - ONCE YOU HAVE ALL FOUR (Name, Email, Phone, Account Type), you MUST end your response with this EXACT tag for our system to process:
      [DATA_COLLECTED] Name: {{name}}, Email: {{email}}, Phone: {{phone}}, Account Type: {{account_type}}
    """

    messages = [{"role": "system", "content": system_prompt}]
    
    # Add history if available
    if history:
        messages.extend(history)
    
    # Add current user message
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": settings.GROQ_MODEL,
        "messages": messages,
        "temperature": 0.1
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(settings.GROQ_API_URL, headers=headers, json=payload, timeout=40.0)
            data = response.json()
            
            # Check if API returned an error
            if 'error' in data:
                error_msg = data.get('error', {}).get('message', 'Unknown API error')
                return f"I'm having trouble connecting to my AI brain. Error: {error_msg}"
            
            # Check if response has expected format
            if 'choices' not in data or len(data['choices']) == 0:
                return f"I received an unexpected response. Please check your API key and try again."
            
            return data['choices'][0]['message']['content']
    except httpx.TimeoutException:
        return "The request took too long. Please try again."
    except Exception as e:
        return f"Chat Error: {str(e)}"


# --- Smart Webhook Endpoint ---

@router.post("/webhook")
async def chat_with_llm(payload: ChatRequest, db: Session = Depends(get_db)):
    user_msg = payload.message
    uid = payload.user_id
    sid = payload.session_id

    # 1. Fetch History (Last 15 messages)
    history_entries = []
    if uid or sid:
        filter_query = (ChatMessage.user_id == uid) if uid else (ChatMessage.session_id == sid)
        history_msgs = db.query(ChatMessage).filter(filter_query).order_by(ChatMessage.timestamp.asc()).limit(15).all()
        for h in history_msgs:
            role = "user" if h.sender == "user" else "assistant"
            history_entries.append({"role": role, "content": h.message})

    # 2. Save User Message
    db.add(ChatMessage(user_id=uid, session_id=sid, sender="user", message=user_msg))
    db.commit()

    # 3. Get Bot Reply with Context
    bot_reply = await call_llm_api(user_msg, history=history_entries)

    # 4. Check for Data Collection Tag [DATA_COLLECTED]
    verification_link = None
    
    if "[DATA_COLLECTED]" in bot_reply:
        try:
            # Regex se data nikalna
            name_match = re.search(r"Name: (.*?),", bot_reply)
            email_match = re.search(r"Email: (.*?),", bot_reply)
            phone_match = re.search(r"Phone: (.*?),", bot_reply)
            account_match = re.search(r"Account Type: (.*)", bot_reply)

            if name_match and email_match and phone_match and account_match:
                name = name_match.group(1).strip()
                email = email_match.group(1).strip()
                phone = phone_match.group(1).strip()
                account_type = account_match.group(1).strip()

                # Auto-Register or Get User
                user = db.query(User).filter((User.email == email) | (User.phone == phone)).first()
                if not user:
                    user = User(name=name, email=email, phone=phone)
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                
                # Check/Create Account
                account = db.query(Account).filter(Account.user_id == user.id).first()
                if not account:
                    # Generate random account number for demo
                    import random
                    acc_num = f"PK{random.randint(1000000000, 9999999999)}"
                    account = Account(user_id=user.id, account_number=acc_num, account_type=account_type)
                    db.add(account)
                    db.commit()
                
                uid = user.id
                
                # Generate Verification Link
                session_id = str(uuid.uuid4())
                token = jwt_handler.create_verification_token(user_id=user.id, session_id=session_id)
                expires_at = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
                
                session = VerificationSession(
                    session_id=session_id, 
                    user_id=user.id, 
                    token=token, 
                    status=VerificationStatus.PENDING, 
                    expires_at=expires_at
                )
                db.add(session)
                db.commit()

                verification_link = f"{settings.FRONTEND_URL}/verify/{token}"
                
                # ✅ UPDATED: Clean message without URL in text
                bot_reply = f"Thank you {name}! I've registered your initial details.\n\nTo complete your account opening, please click the button below to proceed with eKYC verification (CNIC, Face, and Fingerprints)."
            
        except Exception as e:
            print(f"Extraction/Link Error: {e}")

    # 5. Save Bot Reply
    db.add(ChatMessage(user_id=uid, session_id=sid, sender="bot", message=bot_reply))
    db.commit()

    # ✅ UPDATED: Return verification_link separately
    response_data = {
        "success": True, 
        "reply": bot_reply
    }
    
    if verification_link:
        response_data["verification_link"] = verification_link
    
    return response_data


@router.post("/register", response_model=dict)
async def register_user(user_data: UserRegistrationRequest, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter((User.email == user_data.email) | (User.phone == user_data.phone)).first()
        if existing_user:
            return {"success": True, "message": "User already registered", "user_id": existing_user.id, "existing": True}

        new_user = User(name=user_data.name, email=user_data.email, phone=user_data.phone)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        audit_logger.log_user_registered(new_user.id, user_data.email, user_data.phone)
        return {"success": True, "user_id": new_user.id, "existing": False}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-link", response_model=VerificationLinkResponse)
async def generate_verification_link(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    session_id = str(uuid.uuid4())
    token = jwt_handler.create_verification_token(user_id=user.id, session_id=session_id)
    expires_at = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    session = VerificationSession(session_id=session_id, user_id=user.id, token=token, status=VerificationStatus.PENDING, expires_at=expires_at)
    db.add(session)
    db.commit()
    return VerificationLinkResponse(success=True, verification_link=f"{settings.FRONTEND_URL}/verify/{token}", session_id=session_id, expires_at=expires_at.isoformat())


# --- Upload Helper ---
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_upload_file(upload_file: UploadFile, filename: str) -> str:
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return file_path

# --- Validation Endpoints for Chat ---

@router.post("/submit-cnic")
async def submit_cnic(
    session_id: str = Form(...),
    cnic_front: UploadFile = File(...), 
    cnic_back: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Find active session
    # Note: For demo, we assume session_id is a match directly or we might need to look up active verification session
    # We will look for the verification session
    
    # 1. Find User by searching active sessions or just creating a placeholder link if needed.
    # ideally headers should have auth, but here we use session_id form field
    
    # Check if a verification session exists, or if this session_id refers to the chat session
    # If it is chat session id, we need to find the user associated with it.
    
    # Fix: session_id from frontend is likely the chat session UUID. 
    # We need to find which user belongs to this chat session.
    # In chat, we stored `session_id` in ChatMessage. Let's find the latest user msg with this session_id
    
    # Alternative: The frontend also passes `session_id` to chat messages. 
    # Let's trust the frontend is sending the same UUID.
    
    user = db.query(User).join(VerificationSession).filter(VerificationSession.session_id == session_id).first()
    if not user:
        # Fallback: maybe session_id is the chat session id from local storage
        # Let's try to find a user who has this session_id in a recent chat message? 
        # Or simpler: The chat flow creates a VerificationSession. 
        # Wait, the chat flow creates a VerificationSession with a NEW session_id (uuid)
        # But the frontend `sessionId` is just a random UUID created in `ChatWindow`.
        # When `generate_verification_link` is called, it makes a VerificationSession.
        
        # FIX: The current chat flow creates a VerificationSession in `chat_with_llm` inside `[DATA_COLLECTED]`.
        # But it creates a NEW `session_id` there. The frontend `sessionId` is different.
        # We need to link them.
        
        # For this prototype to work smoothly without deep auth changes:
        # We will assume `session_id` passed here IS the `chatSessionId` from frontend.
        # We need to find which user belongs to this chat session.
        
        last_msg = db.query(ChatMessage).filter(ChatMessage.session_id == session_id, ChatMessage.user_id != None).order_by(ChatMessage.timestamp.desc()).first()
        if not last_msg:
             # Just create a dummy user or fail? 
             # For demo robustness, let's create a temporary connection or fail gracefully.
             # Actually, if the user completed the flow, `chat_with_llm` found/created a user.
             # And it saved a message with `user_id` and `session_id`.
             pass
        
        if last_msg:
             user_id = last_msg.user_id
        else:
             # Should not happen if flow was followed
             raise HTTPException(status_code=400, detail="User session not found")
    else:
        user_id = user.id

    # Save Files
    front_path = save_upload_file(cnic_front, f"{session_id}_front.jpg")
    back_path = save_upload_file(cnic_back, f"{session_id}_back.jpg")
    
    # Update/Create CNIC Data
    # For security we should encrpyt paths but for now storing plain for inspection visibility
    
    cnic_data = db.query(CNICData).filter(CNICData.user_id == user_id).first()
    if not cnic_data:
        cnic_data = CNICData(
            user_id=user_id,
            encrypted_cnic_number=encryption_service.encrypt("PENDING"), # Placeholder
            encrypted_name=encryption_service.encrypt("PENDING"),
            encrypted_front_image_path=encryption_service.encrypt(front_path),
            encrypted_back_image_path=encryption_service.encrypt(back_path)
        )
        db.add(cnic_data)
    else:
        cnic_data.encrypted_front_image_path = encryption_service.encrypt(front_path)
        cnic_data.encrypted_back_image_path = encryption_service.encrypt(back_path)
    
    db.commit()
    return {"status": "success", "message": "CNIC uploaded"}

@router.post("/submit-face")
async def submit_face(
    session_id: str = Form(...),
    selfie: UploadFile = File(...),
    liveness_video: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Resolve User ID (Same logic as above)
    last_msg = db.query(ChatMessage).filter(ChatMessage.session_id == session_id, ChatMessage.user_id != None).order_by(ChatMessage.timestamp.desc()).first()
    if not last_msg:
        raise HTTPException(status_code=400, detail="User session not found")
    user_id = last_msg.user_id

    # Save files
    selfie_path = save_upload_file(selfie, f"{session_id}_selfie.jpg")
    video_path = None
    if liveness_video:
        video_path = save_upload_file(liveness_video, f"{session_id}_liveness.webm")

    
    # Update/Create Biometric Data
    bio_data = db.query(BiometricData).filter(BiometricData.user_id == user_id).first()
    if not bio_data:
        bio_data = BiometricData(
            user_id=user_id,
            encrypted_selfie_path=encryption_service.encrypt(selfie_path),
            face_match_score=0.95, # Simulated
            face_match_result=True,
            liveness_score=0.98, # Simulated
            liveness_result=True
        )
        if video_path:
            bio_data.encrypted_liveness_video_path = encryption_service.encrypt(video_path)
        db.add(bio_data)
    else:
        bio_data.encrypted_selfie_path = encryption_service.encrypt(selfie_path)
        if video_path:
            bio_data.encrypted_liveness_video_path = encryption_service.encrypt(video_path)
    
    db.commit()
    return {"status": "success", "message": "Face data uploaded"}

@router.post("/submit-fingerprint")
async def submit_fingerprint(
    request: Request,
    db: Session = Depends(get_db)
):
    data = await request.json()
    session_id = data.get('session_id')
    fingerprint_blob = data.get('fingerprint_data') # This might be the base64 string or similar
    
    # Resolve User ID
    last_msg = db.query(ChatMessage).filter(ChatMessage.session_id == session_id, ChatMessage.user_id != None).order_by(ChatMessage.timestamp.desc()).first()
    if not last_msg:
        raise HTTPException(status_code=400, detail="User session not found")
    user_id = last_msg.user_id
    
    # Save fingerprint (mocking saving a file or just data)
    # If it's a huge blob, maybe save to file. For now let's assume it's small enough or just save a dummy file.
    # In a real app we would decode the base64 and save as .wsq or .iso
    
    fp_path = os.path.join(UPLOAD_DIR, f"{session_id}_fingerprint.txt")
    with open(fp_path, "w") as f:
        f.write(str(fingerprint_blob))
        
    
    bio_data = db.query(BiometricData).filter(BiometricData.user_id == user_id).first()
    if not bio_data:
        # Create if not exists (unlikely if flow followed)
        bio_data = BiometricData(
             user_id=user_id, 
             fingerprint_verified=True,
             encrypted_fingerprint_data=encryption_service.encrypt(fp_path)
        )
        db.add(bio_data)
    else:
        bio_data.fingerprint_verified = True
        bio_data.encrypted_fingerprint_data = encryption_service.encrypt(fp_path)
        
    db.commit()
    
    return {"status": "success", "message": "Fingerprint captured"}

@router.get("/status/{session_id}")
async def check_status(session_id: str, db: Session = Depends(get_db)):
    session = db.query(VerificationSession).filter(VerificationSession.session_id == session_id).first()
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {"status": session.status.value, "steps_completed": {"cnic": session.cnic_uploaded, "face": session.face_match_completed}}