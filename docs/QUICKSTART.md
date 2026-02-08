# eKYC System - Quick Start Guide

## Prerequisites

- Python 3.9+
- PostgreSQL 14+
- 8GB RAM minimum

## Installation Steps

### 1. Setup Database

```powershell
# Install PostgreSQL if not already installed
# Then create database
createdb ekyc_db
```

### 2. Clone and Navigate

```powershell
cd c:\Users\user\OneDrive\Desktop\eKYC
```

### 3. Backend Setup

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure Environment

```powershell
# Copy and edit .env file
cp .env.example .env

# Generate secure keys (run in Python):
# python -c "import secrets; print(f'JWT_SECRET_KEY={secrets.token_hex(32)}')"
# python -c "import secrets; print(f'ENCRYPTION_KEY={secrets.token_hex(32)}')"
# python -c "import secrets; print(f'SALT={secrets.token_hex(16)}')"
```

### 5. Initialize Database

```powershell
python -c "from database import init_db; init_db()"
```

### 6. Rasa Setup

```powershell
cd ..\rasa
pip install -r requirements.txt
rasa train
```

### 7. Download Required Models

```powershell
# Download dlib facial landmarks model
# URL: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
# Extract and place in: backend\models\shape_predictor_68_face_landmarks.dat
```

## Running the System

### Terminal 1 - Backend API

```powershell
cd backend
venv\Scripts\activate
python main.py
```

API will be available at http://localhost:8000

### Terminal 2 - Rasa Server

```powershell
cd rasa
rasa run --enable-api --cors "*"
```

Rasa will run on http://localhost:5005

### Terminal 3 - Rasa Actions

```powershell
cd rasa
rasa run actions
```

Actions server runs on http://localhost:5055

## Testing the System

### 1. Test Backend API

Visit: http://localhost:8000/docs

This will show the interactive Swagger API documentation.

### 2. Test Rasa Chatbot

```powershell
cd rasa
rasa shell
```

Try these commands:
- "Hello"
- "I want to open an account"
- Provide name, email, phone when prompted

### 3. Test End-to-End Flow

1. Start chatbot interaction
2. Provide user details
3. Chatbot will generate a verification link
4. (Frontend not built yet - will be Next.js app)

## Common Issues

### Issue: Database connection error

**Solution**: Check DATABASE_URL in .env file matches your PostgreSQL configuration

### Issue: Rasa fails to train

**Solution**: Ensure all dependencies installed correctly:
```powershell
pip install rasa==3.6.0 --no-cache-dir
```

### Issue: Missing dlib model error

**Solution**: Download shape_predictor_68_face_landmarks.dat and place in backend/models/

### Issue: Import errors in Python

**Solution**: Activate virtual environment:
```powershell
cd backend
venv\Scripts\activate
```

## Next Steps

1. Test API endpoints using Swagger UI (http://localhost:8000/docs)
2. Train Rasa with more dialogue examples
3. Build Next.js frontend for verification portal
4. Add sample CNIC images for testing
5. Implement rate limiting for production

## API Quick Reference

### User Registration
```bash
POST http://localhost:8000/api/chat/register
{
  "name": "Ahmed Khan",
  "email": "ahmed@example.com",
  "phone": "+923001234567"
}
```

### Generate Verification Link
```bash
POST http://localhost:8000/api/chat/generate-link?user_id=1
```

### Check Status
```bash
GET http://localhost:8000/api/chat/status/{session_id}
```

## Project Structure

```
eKYC/
├── backend/           # FastAPI backend
│   ├── main.py       # Application entry point
│   ├── api/          # API routes
│   ├── database/     # Models and DB config
│   ├── security/     # Encryption, JWT, logging
│   └── services/     # CV and validation services
├── rasa/             # Rasa chatbot
│   ├── domain.yml    # Bot domain
│   ├── data/         # Training data
│   └── actions/      # Custom actions
└── docs/             # Documentation
```

## Support

- Documentation: See README.md
- Security: See SECURITY.md
- API Reference: http://localhost:8000/docs
