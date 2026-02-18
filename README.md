# Chat-Based Digital Bank Account Opening System (eKYC)

A secure, conversational digital onboarding system for opening bank accounts via chat interface with AI-powered KYC verification.

## 🏗️ Architecture

The system consists of three main layers:

1. **Chat Layer (Rasa)**: Conversational AI that collects user information
2. **Verification Layer (Python + FastAPI)**: Computer vision and biometric verification
3. **Data Layer (PostgreSQL)**: Encrypted storage of user data and audit logs

![System Architecture](brain/2c04a106-dd1f-4843-8bb0-fd4140b7d7c4/system_architecture_diagram_1769589516180.png)

## 🚀 Features

- **Conversational Onboarding**: Natural language chat interface using Rasa
- **CNIC OCR Extraction**: Automated data extraction from Pakistani CNIC using EasyOCR
- **Face Matching**: DeepFace-powered face verification comparing selfie with CNIC photo
- **Liveness Detection**: Eye blink and head movement detection using OpenCV
- **Secure Authentication**: JWT-based verification links with 15-minute expiration
- **Data Encryption**: AES-256-GCM encryption for all PII data at rest
- **Audit Logging**: Comprehensive compliance tracking
- **Fingerprint Integration**: Placeholder for NADRA SDK integration

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL 14+
- Node.js 18+ (for frontend)
- 8GB RAM minimum (for ML models)
- Windows/Linux/macOS

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd eKYC
```

### 2. Set Up Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Set Up Rasa

```bash
cd ../rasa
pip install -r requirements.txt

# Download dlib facial landmarks model (required for liveness detection)
# Download from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
# Extract and place in: backend/models/shape_predictor_68_face_landmarks.dat
```

### 4. Configure Database

```bash
# Install PostgreSQL and create database
createdb ekyc_db

# Or using psql
psql -U postgres
CREATE DATABASE ekyc_db;
\q
```

### 5. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# - DATABASE_URL
# - JWT_SECRET_KEY (generate a secure random key)
# - ENCRYPTION_KEY (32 bytes, base64 encoded)
```

### 6. Initialize Database

```bash
cd backend
python -c "from database import init_db; init_db()"
```

### 7. Train Rasa Model

```bash
cd ../rasa
rasa train
```

## 🎯 Running the Application

### Option 1: Run Services Individually

**Terminal 1 - Backend API:**
```bash
cd backend
python main.py
# API runs on http://process.env.NEXT_PUBLIC_API_URL
```

**Terminal 2 - Rasa Server:**
```bash
cd rasa
rasa run --enable-api --port 5005
```

**Terminal 3 - Rasa Actions Server:**
```bash
cd rasa
rasa run actions
```

**Terminal 4 - Frontend (Next.js):**
```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:3000
```

### Option 2: Using Docker Compose

```bash
docker-compose up -d
```

## 📖 Usage Flow

### User Journey

1. **Chat Initiation**: User greets the chatbot
2. **Data Collection**: Bot asks for name, email, and phone number
3. **Verification Link**: Bot generates a secure JWT link
4. **CNIC Upload**: User uploads front and back of Pakistani CNIC
5. **OCR Processing**: System extracts and validates CNIC data
6. **Selfie Capture**: User takes a selfie
7. **Face Matching**: System compares selfie with CNIC photo
8. **Liveness Check**: User performs eye blinks and head movements
9. **Fingerprint** (Optional): Fingerprint capture if SDK is available
10. **Account Creation**: System creates bank account on successful verification

### API Endpoints

#### Chat Endpoints
- `POST /api/chat/register` - Register new user
- `POST /api/chat/generate-link` - Generate verification link
- `GET /api/chat/status/{session_id}` - Check verification status

#### Verification Endpoints
- `POST /api/verify/validate-token` - Validate JWT token
- `POST /api/verify/upload-cnic` - Upload CNIC images
- `POST /api/verify/upload-selfie` - Upload selfie and match face
- `POST /api/verify/liveness-check` - Perform liveness detection
- `POST /api/verify/finalize` - Complete verification and create account

#### Admin Endpoints
- `GET /api/admin/users` - List all users
- `GET /api/admin/audit-logs` - View audit logs
- `GET /api/admin/stats` - System statistics

## 🔒 Security Features

### Data Protection
- **AES-256-GCM Encryption**: All PII data encrypted at rest
- **PBKDF2 Key Derivation**: Secure encryption key generation
- **JWT Tokens**: 15-minute expiration for verification links
- **HTTPS Only**: All communications must use HTTPS in production

### Compliance
- **Audit Logging**: Every action logged with timestamp and user context
- **CNIC Validation**: Pakistani ID card format and expiry validation
- **Age Verification**: Minimum 18 years old requirement
- **Data Isolation**: User data separated and encrypted

## 📊 Project Structure

```
eKYC/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration management
│   ├── api/routes/                # API endpoints
│   ├── database/                  # SQLAlchemy models
│   ├── security/                  # Encryption, JWT, audit logging
│   └── services/
│       ├── cv/                    # Computer vision modules
│       ├── validation/            # Data validation
│       └── biometric/             # Fingerprint integration
├── rasa/
│   ├── domain.yml                 # Bot domain
│   ├── config.yml                 # NLU & policies config  
│   ├── data/                      # Training data
│   └── actions/                   # Custom actions
├── frontend/                      # Next.js verification portal
└── docs/                          # Documentation
```

## 🔍 Testing

### Run Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Test Rasa Bot
```bash
cd rasa
rasa shell
# Interactive testing
```

### API Documentation
Visit `http://process.env.NEXT_PUBLIC_API_URL/docs` for interactive Swagger API documentation.

## 🎨 Frontend Development

The verification portal (Next.js) is where users complete the verification process:

```bash
cd frontend
npm run dev
```

Components:
- `CNICUpload.tsx` - CNIC image upload
- `SelfieCapture.tsx` - Webcam selfie capture
- `LivenessCheck.tsx` - Liveness detection with instructions
- `VerificationResult.tsx` - Success/failure display

## 📝 Environment Variables

Required environment variables in `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/ekyc_db
JWT_SECRET_KEY=<your-secret-key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
ENCRYPTION_KEY=<32-byte-base64-encoded-key>
SALT=<16-byte-salt>
FRONTEND_URL=http://localhost:3000
RASA_API_URL=http://localhost:5005
FACE_MATCH_THRESHOLD=0.6
LIVENESS_CONFIDENCE_THRESHOLD=0.7
```

## 🚧 Production Deployment Checklist

- [ ] Generate secure JWT secret and encryption keys
- [ ] Configure PostgreSQL with SSL
- [ ] Set up HTTPS with valid SSL certificates
- [ ] Configure CORS for production domain
- [ ] Set up backup and disaster recovery
- [ ] Enable rate limiting
- [ ] Configure monitoring and alerts
- [ ] Perform security audit
- [ ] Test with real CNIC samples
- [ ] Integrate actual NADRA fingerprint SDK
- [ ] Deploy behind reverse proxy (Nginx)
- [ ] Set up log rotation
- [ ] Configure environment-specific settings

## 🤝 Integration Notes

### NADRA Fingerprint SDK Integration

The fingerprint integration is currently a placeholder. To integrate:

1. Obtain NADRA Verisys SDK license
2. Install SDK and hardware drivers
3. Replace `fingerprint_integration.py` with actual SDK calls
4. Configure API credentials in environment variables
5. Test with certified fingerprint scanners

See `backend/services/biometric/fingerprint_integration.py` for integration guide.

## 📄 License

[Your License Here]

## 👥 Authors

[Your Team/Company]

## 📞 Support

For issues or questions, contact: [support@example.com]

---

**Note**: This system is designed for Pakistani banking onboarding. CNIC validation and formats are specific to Pakistan. Adjust as needed for other regions.
