import requests
import uuid

# Configuration
BASE_URL = "http://localhost:8000/api/chat"
SESSION_ID = str(uuid.uuid4())

# 1. Create a dummy user session first by simulating a chat message
# This is needed because our endpoint logic looks for a user associated with the session_id
def init_session():
    print(f"Initializing session: {SESSION_ID}")
    # We need to simulate the /webhook call or manually insert into DB
    # Let's try sending a message to the bot to create the user/session mapping
    # Note: The chat flow requires a user_id or session_id.
    
    # Actually, the endpoints look for a ChatMessage with this session_id.
    # So we need to ensure such a message exists.
    # Since we can't easily inject into DB without direct DB access here (simulating client),
    # let's try to hit the chat endpoint first.
    
    payload = {
        "message": "My name is Test User",
        "session_id": SESSION_ID
    }
    try:
        resp = requests.post(f"{BASE_URL}/webhook", json=payload)
        print("Chat Init Response:", resp.status_code)
    except Exception as e:
        print("Chat Init Failed (server might be down):", e)
        return False
    return True

def test_cnic_upload():
    print("\nTesting CNIC Upload...")
    files = {
        'cnic_front': ('front.jpg', b'fake_image_content', 'image/jpeg'),
        'cnic_back': ('back.jpg', b'fake_image_content', 'image/jpeg')
    }
    data = {'session_id': SESSION_ID}
    
    try:
        resp = requests.post(f"{BASE_URL}/submit-cnic", files=files, data=data)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_face_upload():
    print("\nTesting Face Upload...")
    files = {
        'selfie': ('selfie.jpg', b'fake_selfie', 'image/jpeg'),
        'liveness_video': ('video.webm', b'fake_video', 'video/webm')
    }
    data = {'session_id': SESSION_ID}
    
    try:
        resp = requests.post(f"{BASE_URL}/submit-face", files=files, data=data)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_fingerprint_upload():
    print("\nTesting Fingerprint Upload...")
    payload = {
        "session_id": SESSION_ID,
        "fingerprint_data": "fake_fingerprint_blob_base64"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/submit-fingerprint", json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if init_session():
        test_cnic_upload()
        test_face_upload()
        test_fingerprint_upload()
    else:
        print("Skipping tests due to init failure")
