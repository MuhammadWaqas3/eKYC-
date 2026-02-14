
import os
import sys
import time
import argparse
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Add the current directory to sys.path to allow imports from database and security
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.models import User, ChatMessage, VerificationSession, CNICData, BiometricData, Account
    from database.database import Base
    from config import settings
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you are running this from the backend directory.")
    sys.exit(1)

# Setup Database Connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_date(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "N/A"

def view_users():
    db = SessionLocal()
    users = db.query(User).all()
    print("\n--- Registered Users ---")
    print(f"{'ID':<5} | {'Name':<20} | {'Email':<25} | {'Phone':<15}")
    print("-" * 75)
    for user in users:
        print(f"{user.id:<5} | {user.name:<20} | {user.email:<25} | {user.phone:<15}")
    db.close()

def view_chat_history(limit=20):
    db = SessionLocal()
    messages = db.query(ChatMessage).order_by(ChatMessage.timestamp.desc()).limit(limit).all()
    messages.reverse()
    
    print("\n--- Chat History ---")
    for msg in messages:
        sender = msg.sender.upper()
        print(f"[{format_date(msg.timestamp)}] {sender}: {msg.message}")
    db.close()

def watch_messages():
    db = SessionLocal()
    last_id = 0
    # Find the last message ID to start watching from
    last_msg = db.query(ChatMessage).order_by(ChatMessage.id.desc()).first()
    if last_msg:
        last_id = last_msg.id
    
    print("\n--- Watching for new messages (Press Ctrl+C to stop) ---")
    try:
        while True:
            new_messages = db.query(ChatMessage).filter(ChatMessage.id > last_id).order_by(ChatMessage.id.asc()).all()
            for msg in new_messages:
                sender = msg.sender.upper()
                print(f"[{format_date(msg.timestamp)}] {sender}: {msg.message}")
                last_id = msg.id
            time.sleep(2)
            db.expire_all() # Ensure we get fresh data
    except KeyboardInterrupt:
        print("\nStopped watching.")
    finally:
        db.close()

def view_sessions():
    db = SessionLocal()
    sessions = db.query(VerificationSession).all()
    print("\n--- Verification Sessions ---")
    print(f"{'User ID':<8} | {'Status':<12} | {'CNIC':<5} | {'Face':<5} | {'Finger':<5} | {'Session ID'}")
    print("-" * 80)
    for s in sessions:
        print(f"{s.user_id:<8} | {s.status.value:<12} | {'[x]' if s.cnic_uploaded else '[ ]':<5} | {'[x]' if s.face_match_completed else '[ ]':<5} | {'[x]' if s.fingerprint_captured else '[ ]':<5} | {s.session_id}")
    db.close()

def view_accounts():
    db = SessionLocal()
    accounts = db.query(Account).all()
    print("\n--- Bank Accounts ---")
    print(f"{'User ID':<8} | {'Account Number':<20} | {'Type':<10} | {'Status'}")
    print("-" * 60)
    for acc in accounts:
        print(f"{acc.user_id:<8} | {acc.account_number:<20} | {acc.account_type:<10} | {acc.status}")
    db.close()

def view_details(session_id=None):
    db = SessionLocal()
    if session_id:
        sessions = db.query(VerificationSession).filter(VerificationSession.session_id == session_id).all()
    else:
        sessions = db.query(VerificationSession).all()

    print("\n--- Detailed File Paths ---")
    
    for s in sessions:
        print(f"\n[Session: {s.session_id}] User ID: {s.user_id}")
        
        cnic = db.query(CNICData).filter(CNICData.user_id == s.user_id).first()
        if cnic:
            print(f"  CNIC Front: {cnic.encrypted_front_image_path}")
            print(f"  CNIC Back:  {cnic.encrypted_back_image_path}")
        else:
            print("  CNIC: Not uploaded")
            
        bio = db.query(BiometricData).filter(BiometricData.user_id == s.user_id).first()
        if bio:
            print(f"  Selfie:     {bio.encrypted_selfie_path}")
            if bio.encrypted_liveness_video_path:
                print(f"  Video:      {bio.encrypted_liveness_video_path}")
            if bio.encrypted_fingerprint_data:
                print(f"  Fingerprint:{bio.encrypted_fingerprint_data}")
        else:
             print("  Biometrics: Not uploaded")
             
    db.close()

def main():
    parser = argparse.ArgumentParser(description="eKYC Database Inspection Tool")
    parser.add_argument("--users", action="store_true", help="View all registered users")
    parser.add_argument("--chat", action="store_true", help="View chat history")
    parser.add_argument("--sessions", action="store_true", help="View verification sessions")
    parser.add_argument("--accounts", action="store_true", help="View bank accounts")
    parser.add_argument("--details", nargs='?', const='all', help="View detailed file paths (optional: provide session_id)")
    parser.add_argument("--watch", action="store_true", help="Watch for new chat messages in real-time")
    parser.add_argument("--limit", type=int, default=20, help="Limit number of messages displayed")
    
    args = parser.parse_args()
    
    if args.users:
        view_users()
    elif args.chat:
        view_chat_history(args.limit)
    elif args.sessions:
        view_sessions()
    elif args.accounts:
        view_accounts()
    elif args.details:
        sid = args.details if args.details != 'all' else None
        view_details(sid)
    elif args.watch:
        watch_messages()
    else:
        # Default: show a summary
        view_users()
        view_chat_history(10)
        print("\nUsage: python inspect_db.py [--users] [--chat] [--sessions] [--accounts] [--details] [--watch]")

if __name__ == "__main__":
    main()
