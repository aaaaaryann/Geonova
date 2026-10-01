from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# --- Auth Schemas ---
class UserRegister(BaseModel):
    full_name: str
    email: str
    phone_number: str
    password: str
    role: Optional[str] = "tourist"
    nationality: Optional[str] = "Indian"
    preferred_language: Optional[str] = "English"

class UserLogin(BaseModel):
    email: str
    password: str

class GoogleLoginRequest(BaseModel):
    email: str
    full_name: Optional[str] = None
    google_id: Optional[str] = None

class PhoneSendOtpRequest(BaseModel):
    phone_number: str

class PhoneVerifyOtpRequest(BaseModel):
    phone_number: str
    otp: str
    full_name: Optional[str] = None

class AadhaarSendOtpRequest(BaseModel):
    aadhaar_number: str
    consent: bool = True

class AadhaarVerifyOtpRequest(BaseModel):
    aadhaar_number: str
    otp: str
    full_name: Optional[str] = None

class OtpResponse(BaseModel):
    status: str
    message: str
    demo_otp: str
    masked_target: Optional[str] = None

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    nationality: Optional[str] = None
    preferred_language: Optional[str] = None
    medical_notes: Optional[str] = None
    profile_photo: Optional[str] = None

class EmergencyContactCreate(BaseModel):
    name: str
    relationship_type: str
    phone_number: str
    email: Optional[str] = None
    is_primary: Optional[bool] = False

class EmergencyContactOut(BaseModel):
    id: int
    name: str
    relationship_type: str
    phone_number: str
    email: Optional[str]
    is_primary: bool

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    phone_number: str
    role: str
    nationality: str
    preferred_language: str
    medical_notes: Optional[str] = None
    profile_photo: Optional[str] = None
    aadhaar_number: Optional[str] = None
    is_aadhaar_verified: Optional[bool] = False
    auth_provider: Optional[str] = "email"
    emergency_contacts: List[EmergencyContactOut] = []

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

# --- Tourism Schemas ---
class DestinationOut(BaseModel):
    id: int
    name: str
    category: str
    description: str
    latitude: float
    longitude: float
    image_url: str
    safety_score: float
    entry_fee: str
    timings: str
    is_featured: bool

    class Config:
        from_attributes = True

class StateUTOut(BaseModel):
    id: int
    code: str
    name: str
    category: str
    region: str
    capital: str
    banner_image: str
    description: str
    best_season: str
    official_website: str
    culture_traditions: str
    local_food: str
    emergency_helpline: str
    tourism_office: Optional[str] = None
    destinations: List[DestinationOut] = []

    class Config:
        from_attributes = True

# --- Safety & Geofencing Schemas ---
class GeofenceCreate(BaseModel):
    state_code: Optional[str] = None
    name: str
    zone_type: str # tourist_safety, restricted, hazard, protected
    description: str
    center_latitude: float
    center_longitude: float
    radius_meters: float
    warning_message: str

class GeofenceOut(BaseModel):
    id: int
    name: str
    zone_type: str
    description: str
    center_latitude: float
    center_longitude: float
    radius_meters: float
    warning_message: str
    is_active: bool

    class Config:
        from_attributes = True

class LocationUpdate(BaseModel):
    latitude: float
    longitude: float
    share_with_contacts: Optional[bool] = True

class GeofenceCheckResult(BaseModel):
    inside_geofence: bool
    geofences_triggered: List[GeofenceOut]
    alert_level: str # safe, warning, danger
    message: str

class SOSCreate(BaseModel):
    emergency_type: str # Medical, Accident, Lost tourist, Harassment/threat, Natural disaster, Other
    latitude: float
    longitude: float
    location_name: Optional[str] = None
    description: Optional[str] = None
    contact_phone: Optional[str] = None

class SOSIncidentOut(BaseModel):
    id: int
    emergency_type: str
    status: str
    latitude: float
    longitude: float
    location_name: Optional[str]
    description: Optional[str]
    contact_phone: Optional[str]
    reported_at: datetime
    resolved_at: Optional[datetime] = None
    admin_notes: Optional[str] = None

    class Config:
        from_attributes = True

class LocalAuthorityOut(BaseModel):
    id: int
    name: str
    category: str
    phone: str
    address: str
    website: Optional[str]
    latitude: float
    longitude: float
    operating_hours: str
    is_emergency: bool

    class Config:
        from_attributes = True

class SafetyProtocolOut(BaseModel):
    id: int
    category: str
    title: str
    summary: str
    warning_signs: str
    dos: str
    donts: str
    emergency_guidance: str
    icon_name: str

    class Config:
        from_attributes = True

# --- Tourism Packages Schemas ---
class TourismPackageOut(BaseModel):
    id: int
    provider_name: str
    title: str
    destination: str
    duration_days: int
    duration_nights: int
    price: float
    discount_price: Optional[float]
    travel_type: str
    max_group_size: int
    accommodation: str
    transportation: str
    meals: str
    guide_included: bool
    safety_features: str
    itinerary: str
    image_url: str
    rating: float
    reviews_count: int

    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    package_id: int
    travel_date: str
    travelers_count: int = 1
    payment_method: str = "UPI / Card"

class BookingOut(BaseModel):
    id: int
    package_id: int
    package_title: Optional[str] = None
    travel_date: str
    travelers_count: int
    total_amount: float
    booking_status: str
    payment_status: str
    booking_reference: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Document Vault Schemas ---
class DocumentUpload(BaseModel):
    document_type: str
    document_name: str
    document_number: Optional[str] = None
    expiry_date: str # YYYY-MM-DD
    file_type: Optional[str] = "pdf"
    file_size_kb: Optional[int] = 100
    file_content_base64: Optional[str] = None

class DocumentOut(BaseModel):
    id: int
    document_type: str
    document_name: str
    document_number: Optional[str]
    expiry_date: str
    file_type: str
    file_size_kb: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Payments & Subscriptions ---
class SubscriptionCreate(BaseModel):
    plan: str # free, premium, partner
    payment_method: Optional[str] = "UPI / Card"

class InvoiceOut(BaseModel):
    invoice_number: str
    amount: float
    currency: str
    payment_method: str
    transaction_id: str
    payment_status: str
    created_at: datetime
    customer_name: str
    customer_email: str
    items: List[str]
