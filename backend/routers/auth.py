from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from security import hash_password, verify_password, create_access_token, require_auth, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.TokenResponse)
def register_user(payload: schemas.UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == payload.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    user = models.User(
        full_name=payload.full_name,
        email=payload.email.lower(),
        phone_number=payload.phone_number,
        password_hash=hash_password(payload.password),
        role=payload.role if payload.role in ["tourist", "provider"] else "tourist",
        nationality=payload.nationality or "Indian",
        preferred_language=payload.preferred_language or "English"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Automatically grant default free subscription
    sub = models.Subscription(user_id=user.id, plan="free", amount=0.0)
    db.add(sub)
    db.commit()

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login", response_model=schemas.TokenResponse)
def login_user(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

# --- Multi-Channel Authentication Handlers ---

import random
import time
import secrets

PHONE_OTP_STORE = {}
AADHAAR_OTP_STORE = {}

@router.post("/google", response_model=schemas.TokenResponse)
def google_auth(payload: schemas.GoogleLoginRequest, db: Session = Depends(get_db)):
    email_clean = payload.email.strip().lower()
    if not email_clean or "@" not in email_clean:
        raise HTTPException(status_code=400, detail="Invalid Gmail or Google email address.")

    user = db.query(models.User).filter(models.User.email == email_clean).first()
    if not user:
        # Auto-provision new tourist user via Google
        name = payload.full_name or email_clean.split("@")[0].replace(".", " ").title()
        user = models.User(
            full_name=name,
            email=email_clean,
            phone_number="+91 9800000000",
            password_hash=hash_password(secrets.token_urlsafe(16)),
            role="tourist",
            nationality="Indian",
            preferred_language="English",
            auth_provider="google"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Free tier subscription
        sub = models.Subscription(user_id=user.id, plan="free", amount=0.0)
        db.add(sub)
        db.commit()
    else:
        if not user.auth_provider or user.auth_provider == "email":
            user.auth_provider = "google"
            db.commit()
            db.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/phone/send-otp", response_model=schemas.OtpResponse)
def send_phone_otp(payload: schemas.PhoneSendOtpRequest):
    phone_digits = "".join(filter(str.isdigit, payload.phone_number))
    if len(phone_digits) < 10:
        raise HTTPException(status_code=400, detail="Please provide a valid 10-digit mobile number.")

    otp = str(random.randint(100000, 999999))
    # Fallback/standard demo OTP option for easy testing
    PHONE_OTP_STORE[phone_digits] = {"otp": otp, "expires": time.time() + 300}
    masked = f"******{phone_digits[-4:]}"

    return {
        "status": "success",
        "message": f"6-digit SMS verification code sent to {masked}",
        "demo_otp": otp,
        "masked_target": masked
    }

@router.post("/phone/verify-otp", response_model=schemas.TokenResponse)
def verify_phone_otp(payload: schemas.PhoneVerifyOtpRequest, db: Session = Depends(get_db)):
    phone_digits = "".join(filter(str.isdigit, payload.phone_number))
    stored = PHONE_OTP_STORE.get(phone_digits)

    # Allow generated OTP or universal testing code '123456'
    is_valid = (stored and stored["otp"] == payload.otp.strip()) or payload.otp.strip() == "123456"
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code. Use demo code 123456.")

    # Search user by phone
    user = db.query(models.User).filter(models.User.phone_number.like(f"%{phone_digits[-10:]}%")).first()
    if not user:
        # Auto-provision new tourist user
        name = payload.full_name.strip() if payload.full_name else f"Tourist ({phone_digits[-4:]})"
        unique_email = f"tourist_{phone_digits[-6:]}@geonova.in"
        user = models.User(
            full_name=name,
            email=unique_email,
            phone_number=f"+91 {phone_digits[-10:]}",
            password_hash=hash_password(secrets.token_urlsafe(16)),
            role="tourist",
            nationality="Indian",
            preferred_language="English",
            auth_provider="phone"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        sub = models.Subscription(user_id=user.id, plan="free", amount=0.0)
        db.add(sub)
        db.commit()

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/aadhaar/send-otp", response_model=schemas.OtpResponse)
def send_aadhaar_otp(payload: schemas.AadhaarSendOtpRequest):
    aadhaar_digits = "".join(filter(str.isdigit, payload.aadhaar_number))
    if len(aadhaar_digits) != 12:
        raise HTTPException(status_code=400, detail="Aadhaar number must contain exactly 12 numeric digits.")

    if not payload.consent:
        raise HTTPException(status_code=400, detail="Voluntary resident e-KYC consent is mandatory for Aadhaar verification.")

    otp = str(random.randint(100000, 999999))
    AADHAAR_OTP_STORE[aadhaar_digits] = {"otp": otp, "expires": time.time() + 300}
    masked = f"XXXX-XXXX-{aadhaar_digits[-4:]}"

    return {
        "status": "success",
        "message": f"UIDAI e-KYC authentication OTP generated for Aadhaar {masked}",
        "demo_otp": otp,
        "masked_target": f"Linked Mobile ending in ····{aadhaar_digits[-4:]}"
    }

@router.post("/aadhaar/verify-otp", response_model=schemas.TokenResponse)
def verify_aadhaar_otp(payload: schemas.AadhaarVerifyOtpRequest, db: Session = Depends(get_db)):
    aadhaar_digits = "".join(filter(str.isdigit, payload.aadhaar_number))
    if len(aadhaar_digits) != 12:
        raise HTTPException(status_code=400, detail="Aadhaar number must be 12 digits.")

    stored = AADHAAR_OTP_STORE.get(aadhaar_digits)
    is_valid = (stored and stored["otp"] == payload.otp.strip()) or payload.otp.strip() == "123456"
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid Aadhaar OTP. Please enter the OTP or demo code 123456.")

    formatted_aadhaar = f"{aadhaar_digits[:4]} {aadhaar_digits[4:8]} {aadhaar_digits[8:]}"

    # Search existing user by aadhaar
    user = db.query(models.User).filter(
        (models.User.aadhaar_number == formatted_aadhaar) | (models.User.aadhaar_number == aadhaar_digits)
    ).first()

    if not user:
        # Create Aadhaar-verified Indian resident account
        default_names = ["Arjun Sharma", "Priya Patel", "Rohan Verma", "Sneha Iyer", "Vikram Singh"]
        chosen_name = payload.full_name.strip() if payload.full_name else random.choice(default_names)

        user = models.User(
            full_name=chosen_name,
            email=f"aadhaar_{aadhaar_digits[-6:]}@geonova.in",
            phone_number=f"+91 98{aadhaar_digits[-8:]}",
            password_hash=hash_password(secrets.token_urlsafe(16)),
            role="tourist",
            nationality="Indian",
            preferred_language="English",
            aadhaar_number=formatted_aadhaar,
            is_aadhaar_verified=True,
            auth_provider="aadhaar"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        sub = models.Subscription(user_id=user.id, plan="free", amount=0.0)
        db.add(sub)
        db.commit()
    else:
        user.is_aadhaar_verified = True
        user.nationality = "Indian"
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=schemas.UserOut)
def get_current_user_profile(user: models.User = Depends(require_auth)):
    return user

@router.put("/profile", response_model=schemas.UserOut)
def update_profile(payload: schemas.UserProfileUpdate, user: models.User = Depends(require_auth), db: Session = Depends(get_db)):
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.phone_number is not None:
        user.phone_number = payload.phone_number
    if payload.nationality is not None:
        user.nationality = payload.nationality
    if payload.preferred_language is not None:
        user.preferred_language = payload.preferred_language
    if payload.medical_notes is not None:
        user.medical_notes = payload.medical_notes
    if payload.profile_photo is not None:
        user.profile_photo = payload.profile_photo

    db.commit()
    db.refresh(user)
    return user

@router.get("/emergency-contacts", response_model=list[schemas.EmergencyContactOut])
def get_emergency_contacts(user: models.User = Depends(require_auth), db: Session = Depends(get_db)):
    return db.query(models.EmergencyContact).filter(models.EmergencyContact.user_id == user.id).all()

@router.post("/emergency-contacts", response_model=schemas.EmergencyContactOut)
def add_emergency_contact(payload: schemas.EmergencyContactCreate, user: models.User = Depends(require_auth), db: Session = Depends(get_db)):
    # If is_primary is set, reset other contacts
    if payload.is_primary:
        db.query(models.EmergencyContact).filter(models.EmergencyContact.user_id == user.id).update({"is_primary": False})
    
    contact = models.EmergencyContact(
        user_id=user.id,
        name=payload.name,
        relationship_type=payload.relationship_type,
        phone_number=payload.phone_number,
        email=payload.email,
        is_primary=payload.is_primary or False
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

@router.delete("/emergency-contacts/{contact_id}")
def delete_emergency_contact(contact_id: int, user: models.User = Depends(require_auth), db: Session = Depends(get_db)):
    contact = db.query(models.EmergencyContact).filter(
        models.EmergencyContact.id == contact_id,
        models.EmergencyContact.user_id == user.id
    ).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found.")
    db.delete(contact)
    db.commit()
    return {"message": "Emergency contact deleted successfully."}
