import hashlib
import hmac
import os
import json
import base64
import time
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
import models

SECRET_KEY = os.environ.get("GEONOVA_SECRET", "geonova-secure-tourist-safety-platform-token-secret-2026")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def hash_password(password: str) -> str:
    """Hash a password using PBKDF2 with SHA-256."""
    salt = "geonova_salt_secure_2026".encode("utf-8")
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return key.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_in_seconds: int = 86400 * 7) -> str:
    """Creates a signed base64 JSON web token."""
    payload = data.copy()
    payload["exp"] = int(time.time()) + expires_in_seconds
    payload_json = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    b64_payload = base64.urlsafe_b64encode(payload_json).decode('utf-8').rstrip('=')
    
    signature = hmac.new(SECRET_KEY.encode('utf-8'), b64_payload.encode('utf-8'), hashlib.sha256).hexdigest()
    return f"{b64_payload}.{signature}"

def decode_access_token(token: str) -> Optional[dict]:
    """Decodes and verifies a signed token."""
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        b64_payload, signature = parts
        expected_signature = hmac.new(SECRET_KEY.encode('utf-8'), b64_payload.encode('utf-8'), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            return None
        
        # Add padding back if necessary
        padding = len(b64_payload) % 4
        if padding:
            b64_payload += '=' * (4 - padding)
            
        payload_bytes = base64.urlsafe_b64decode(b64_payload)
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        if payload.get("exp", 0) < int(time.time()):
            return None # Expired
            
        return payload
    except Exception:
        return None

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[models.User]:
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    user_id = payload["sub"]
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user

def require_auth(user: Optional[models.User] = Depends(get_current_user)) -> models.User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please login.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def require_admin(user: models.User = Depends(require_auth)) -> models.User:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required.",
        )
    return user
