"""
JWT token handler for secure verification link generation and validation.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from config import settings


class JWTHandler:
    """Handler for JWT token operations."""
    
    def __init__(self):
        """Initialize JWT handler with configuration."""
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.expiration_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    
    def create_verification_token(
        self,
        user_id: int,
        session_id: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create JWT token for verification link.
        
        Args:
            user_id: User database ID
            session_id: Unique verification session ID
            additional_data: Optional additional payload data
            
        Returns:
            JWT token string
        """
        # Calculate expiration time
        expire = datetime.utcnow() + timedelta(minutes=self.expiration_minutes)
        
        # Build payload
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "verification"
        }
        
        # Add additional data if provided
        if additional_data:
            payload.update(additional_data)
        
        # Create token
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate JWT token and extract payload.
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload dict if valid, None otherwise
        """
        try:
            # Decode and validate token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Verify token type
            if payload.get("type") != "verification":
                return None
            
            return payload
        
        except JWTError as e:
            print(f"JWT validation error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error during token validation: {e}")
            return None
    
    def is_token_expired(self, payload: Dict[str, Any]) -> bool:
        """
        Check if token is expired.
        
        Args:
            payload: Token payload dict
            
        Returns:
            True if expired, False otherwise
        """
        exp = payload.get("exp")
        if not exp:
            return True
        
        expiration = datetime.fromtimestamp(exp)
        return datetime.utcnow() > expiration
    
    def get_user_id(self, token: str) -> Optional[int]:
        """
        Extract user ID from token.
        
        Args:
            token: JWT token string
            
        Returns:
            User ID if valid, None otherwise
        """
        payload = self.validate_token(token)
        if payload:
            return payload.get("user_id")
        return None
    
    def get_session_id(self, token: str) -> Optional[str]:
        """
        Extract session ID from token.
        
        Args:
            token: JWT token string
            
        Returns:
            Session ID if valid, None otherwise
        """
        payload = self.validate_token(token)
        if payload:
            return payload.get("session_id")
        return None


# Global JWT handler instance
jwt_handler = JWTHandler()
