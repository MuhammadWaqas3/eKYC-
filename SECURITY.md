# eKYC Security Documentation

## Overview

This document outlines the security measures implemented in the Chat-Based Digital Bank Account Opening System.

## Data Protection

### Encryption at Rest

All Personally Identifiable Information (PII) is encrypted using **AES-256-GCM** (Galois/Counter Mode):

- **Algorithm**: AES-256-GCM
- **Key Derivation**: PBKDF2 with SHA-256
- **Iterations**: 100,000
- **Nonce**: 12 bytes (randomly generated per encryption)

**Encrypted Fields**:
- CNIC number
- Full name
- Father's name
- Date of birth
- Address
- Biometric data (selfie, fingerprint templates)
- File paths

### Encryption in Transit

- **HTTPS Only**: All API communications must use TLS 1.2+
- **Certificate Pinning**: Recommended for production mobile apps
- **Secure WebSocket**: For real-time Rasa communication

### Key Management

**Best Practices**:
1. Store encryption keys in environment variables (never in code)
2. Use hardware security modules (HSM) in production
3. Implement key rotation policy (every 90 days)
4. Separate keys for different environments

**Key Generation**:
```python
# Generate secure encryption key
import secrets
encryption_key = secrets.token_hex(32)  # 32 bytes = 256 bits

# Generate salt
salt = secrets.token_hex(16)  # 16 bytes
```

## Authentication & Authorization

### JWT Tokens

**Verification Links**:
- **Expiration**: 15 minutes
- **Algorithm**: HS256
- **Secret**: Stored in environment variables
- **Claims**: user_id, session_id, expiration timestamp

**Security Measures**:
- Short expiration time to minimize token theft impact
- Single-use tokens (session marked as invalid after use)
- Signature verification on every request

### Session Management

- Sessions expire after link expiration
- Failed verification attempts logged
- Maximum 3 verification attempts per session

## Input Validation

### Email Validation
- Regex pattern matching
- Domain validation
- Length limits (max 255 characters)

### Phone Validation
- Pakistani format: +92XXXXXXXXXX
- Numeric validation
- Length validation (13 characters)

### CNIC Validation
- Format: XXXXX-XXXXXXX-X
- Checksum validation
- Expiry date verification
- Age verification (minimum 18 years)

### File Upload Security
- **Allowed file types**: JPEG, PNG, MP4
- **Maximum file size**: 10 MB
- **Virus scanning**: Recommended for production
- **File type verification**: Magic number checking
- **Secure storage**: Files stored outside web root

## Biometric Security

### Face Matching
- **Model**: VGG-Face (DeepFace)
- **Threshold**: 0.6 (60% similarity)
- **Anti-spoofing**: Liveness detection required

### Liveness Detection
- **Eye Blink Detection**: Minimum 2 blinks in 5 seconds
- **Head Movement**: Left-right or up-down movement required
- **Video Analysis**: Frame-by-frame facial landmark tracking

### Fingerprint Security
- Templates stored encrypted
- NADRA-compliant SDK integration
- ISO 19794-2 or WSQ template format

## Database Security

### Connection Security
- **SSL/TLS**: Required for database connections
- **Connection Pooling**: Limited pool size to prevent exhaustion
- **Credential Management**: Environment variables only

### Query Security
- **ORM**: SQLAlchemy prevents SQL injection
- **Parameterized Queries**: All queries use bound parameters
- **Least Privilege**: Database user has minimal required permissions

### Backup & Recovery
- **Encrypted Backups**: All backups encrypted at rest
- **Regular Schedule**: Daily automated backups
- **Retention Policy**: 30 days
- **Disaster Recovery**: Tested recovery procedures

## Compliance & Audit

### Audit Logging

**Logged Events**:
- User registration
- Verification link generation
- CNIC uploads
- OCR processing results
- Face match attempts and results
- Liveness check results
- Fingerprint captures
- Account creation
- Failed verification attempts
- Security violations

**Log Format**:
```json
{
  "timestamp": "2026-01-28T13:00:00Z",
  "event_type": "face_match_completed",
  "user_id": 123,
  "session_id": "uuid",
  "data": {
    "match_score": 0.85,
    "is_match": true
  }
}
```

**Log Storage**:
- Database table for searchability
- File-based logs for backup
- Retention: 2 years minimum (compliance requirement)

### GDPR/Privacy Compliance

**User Rights**:
- Right to access data
- Right to deletion
- Right to data portability
- Right to correction

**Implementation**:
- User consent required before data collection
- Clear privacy policy
- Data minimization (only collect necessary data)
- Purpose limitation (data used only for account opening)

## Security Best Practices

### Production Deployment

1. **Environment Separation**:
   - Separate dev, staging, production environments
   - Different encryption keys per environment
   - No production data in dev/staging

2. **Access Control**:
   - Role-based access control (RBAC) for admin endpoints
   - Multi-factor authentication for admin users
   - IP whitelisting for admin access

3. **Rate Limiting**:
   - Implement rate limiting on all endpoints
   - Threshold: 100 requests/minute per IP
   - CAPTCHA after multiple failed attempts

4. **Monitoring & Alerts**:
   - Real-time monitoring of security events
   - Alerts for suspicious activities
   - Automated lockout after multiple failures

5. **Regular Security Audits**:
   - Penetration testing (quarterly)
   - Code review (all changes)
   - Dependency vulnerability scanning
   - Security training for developers

###Incident Response

**Procedure**:
1. Detect and contain breach
2. Assess scope and impact
3. Notify affected users (if required)
4. Remediate vulnerabilities
5. Document and learn

## Known Limitations

1. **Liveness Detection**: Basic implementation using dlib landmarks
   - **Recommendation**: Use commercial liveness SDK for production
   - **Vulnerability**: Can be fooled by high-quality 3D masks

2. **Fingerprint Integration**: Placeholder implementation
   - **Recommendation**: Integrate NADRA-compliant SDK
   - **Current Status**: Mock implementation for development

3. **CNIC OCR Accuracy**: Depends on image quality
   - **Mitigation**: Image quality validation before processing
   - **Recommendation**: Manual review for low-confidence extractions

## Security Contacts

**Report Security Issues**:
- Email: security@example.com
- Response Time: Within 24 hours
- Responsible Disclosure Policy: 90 days

---

**Last Updated**: 2026-01-28  
**Version**: 1.0  
**Next Review**: 2026-04-28
