# eKYC System Integration Guide

Complete guide for connecting Frontend, Backend, and Database.

## System Architecture

```
┌─────────────────┐      HTTP/REST      ┌─────────────────┐      SQLAlchemy      ┌─────────────────┐
│                 │ ──────────────────> │                 │ ──────────────────> │                 │
│  Next.js        │                     │  FastAPI        │                     │  SQLite/        │
│  Frontend       │ <────────────────── │  Backend        │ <────────────────── │  PostgreSQL     │
│  (Port 3000)    │      JSON           │  (Port 8000)    │      ORM Models     │  Database       │
└─────────────────┘                     └─────────────────┘                     └─────────────────┘
```

## Prerequisites

### Backend
- Python 3.10+
- pip and virtualenv

### Frontend
- Node.js 18+
- npm

## Step-by-Step Setup

### 1. Database Setup

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment (if not already activated)
# Windows:
venv310\Scripts\activate
# Linux/Mac:
source venv310/bin/activate

# Initialize database
python scripts/init_db.py
```

This will create:
- `users` table
- `verification_sessions` table
- `cnic_data` table
- `biometric_data` table
- `accounts` table
- `audit_logs` table

Database file location: `backend/ekyc.db` (SQLite)

### 2. Backend Setup

```bash
# Still in backend directory with venv activated

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Start the backend server
python main.py
# Or use uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies (already done)
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## Testing the Integration

### 1. Test Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "eKYC Digital Banking System",
  "version": "1.0.0"
}
```

### 2. Test Frontend

Open browser: `http://localhost:3000`

You should see the homepage with:
- Hero section
- Features grid
- How it works section
- Security information

### 3. Test Verification Flow

To test the complete flow, you need to:

1. **Generate a verification token** (via Rasa chat or directly via API):

```bash
curl -X POST http://localhost:8000/api/chat/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Muhammad Ahmed Khan",
    "email": "ahmed@example.com",
    "phone": "+923001234567"
  }'
```

Response will include a `verification_link` like:
```
http://localhost:3000/verify?token=eyJhbGc...
```

2. **Open the verification link** in your browser

3. **Complete the verification steps**:
   - Upload CNIC front and back
   - Capture selfie
   - Complete liveness check
   - Submit fingerprint (simulated)

## API Endpoints Reference

### Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/register` | Register user and create session |
| POST | `/api/chat/generate-link` | Generate verification link |
| GET | `/api/chat/status/{session_id}` | Get verification status |

### Verification Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/verify/validate-token` | Validate JWT token |
| POST | `/api/verify/upload-cnic` | Upload CNIC images |
| POST | `/api/verify/upload-selfie` | Upload selfie image |
| POST | `/api/verify/liveness-check` | Submit liveness video |
| POST | `/api/verify/submit-fingerprint` | Submit fingerprint data |
| POST | `/api/verify/finalize` | Finalize verification and create account |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/users` | List all users |
| GET | `/api/admin/audit-logs` | View audit logs |
| GET | `/api/admin/stats` | System statistics |

## Database Schema

### users
- id (PK)
- name
- email (unique)
- phone (unique)
- created_at
- updated_at

### verification_sessions
- id (PK)
- session_id (unique)
- user_id (FK)
- token (JWT)
- status (enum)
- step flags (booleans)
- timestamps

### cnic_data
- id (PK)
- user_id (FK, unique)
- encrypted fields (CNIC number, name, DOB, etc.)
- validation flags
- image paths (encrypted)

### biometric_data
- id (PK)
- user_id (FK, unique)
- face match score
- liveness score
- fingerprint data (encrypted)
- verification results

### accounts
- id (PK)
- user_id (FK, unique)
- account_number (unique)
- account_type
- status
- created_at

### audit_logs
- id (PK)
- user_id (FK)
- session_id
- event_type
- event_data (JSON)
- ip_address
- user_agent
- created_at

## Environment Variables

### Backend (.env)

```env
# Application
APP_NAME=eKYC Digital Banking System
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./ekyc.db

# Security
SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=15
ENCRYPTION_KEY=your-encryption-key-here-change-in-production

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Verification Thresholds
FACE_MATCH_THRESHOLD=0.6
LIVENESS_THRESHOLD=0.7
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Common Issues & Solutions

### Issue: CORS Error

**Symptom**: Frontend can't connect to backend, CORS errors in browser console

**Solution**: 
1. Check `ALLOWED_ORIGINS` in backend `.env`
2. Ensure it includes `http://localhost:3000`
3. Restart backend server

### Issue: Database Not Found

**Symptom**: Backend crashes with "no such table" error

**Solution**:
```bash
cd backend
python scripts/init_db.py
```

### Issue: Camera Not Working

**Symptom**: Camera permission denied or not accessible

**Solution**:
1. Use HTTPS in production (required for camera access)
2. For local development, use `localhost` (not `127.0.0.1`)
3. Grant camera permissions in browser settings

### Issue: Token Expired

**Symptom**: "Token expired" error on verification page

**Solution**:
- Tokens expire in 15 minutes
- Generate a new verification link
- Increase `JWT_EXPIRATION_MINUTES` in backend `.env` if needed

## Production Deployment

### Backend

1. Use PostgreSQL instead of SQLite
2. Set strong `SECRET_KEY` and `ENCRYPTION_KEY`
3. Enable HTTPS
4. Use environment variables for all secrets
5. Set up proper logging and monitoring
6. Configure rate limiting

### Frontend

1. Build for production: `npm run build`
2. Set `NEXT_PUBLIC_API_URL` to production backend URL
3. Deploy to Vercel, Netlify, or similar
4. Enable HTTPS

### Database

1. Use PostgreSQL in production
2. Set up regular backups
3. Enable SSL connections
4. Implement proper access controls

## Monitoring

### Backend Health Check

```bash
curl http://localhost:8000/health
```

### Database Connection

```python
from backend.database.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("Database connected:", result.fetchone())
```

### Frontend Build

```bash
cd frontend
npm run build
# Should complete without errors
```

## Security Checklist

- [ ] Change default `SECRET_KEY` in production
- [ ] Change default `ENCRYPTION_KEY` in production
- [ ] Use HTTPS for all connections
- [ ] Enable rate limiting on API endpoints
- [ ] Implement proper session management
- [ ] Set up audit logging
- [ ] Regular security updates
- [ ] Penetration testing
- [ ] GDPR/data protection compliance

## Support

For issues or questions:
1. Check logs: `backend/logs/` and browser console
2. Review API documentation: `http://localhost:8000/docs`
3. Check database: Use SQLite browser or psql for PostgreSQL
