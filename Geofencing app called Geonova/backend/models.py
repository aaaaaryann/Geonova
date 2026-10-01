import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    phone_number = Column(String(30), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), default="tourist")  # tourist, provider, authority, admin
    nationality = Column(String(60), default="Indian")
    preferred_language = Column(String(40), default="English")
    medical_notes = Column(Text, nullable=True)
    profile_photo = Column(String(255), nullable=True)
    aadhaar_number = Column(String(20), unique=True, index=True, nullable=True)
    is_aadhaar_verified = Column(Boolean, default=False)
    auth_provider = Column(String(30), default="email")  # email, google, phone, aadhaar
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    emergency_contacts = relationship("EmergencyContact", back_populates="user", cascade="all, delete-orphan")
    tracking_sessions = relationship("TrackingSession", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    incidents = relationship("SOSIncident", back_populates="user")
    subscription = relationship("Subscription", back_populates="user", uselist=False)

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    relationship_type = Column(String(50), nullable=False)
    phone_number = Column(String(30), nullable=False)
    email = Column(String(120), nullable=True)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="emergency_contacts")

class StateUT(Base):
    __tablename__ = "states_uts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, nullable=False) # e.g. DL, RJ, MH
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(20), nullable=False) # state or union_territory
    region = Column(String(30), nullable=False) # Northern, Southern, Eastern, Western/Central, Northeastern
    capital = Column(String(100), nullable=False)
    banner_image = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    best_season = Column(String(100), nullable=False)
    official_website = Column(String(255), nullable=False)
    culture_traditions = Column(Text, nullable=False)
    local_food = Column(Text, nullable=False)
    emergency_helpline = Column(String(50), default="112")
    tourism_office = Column(Text, nullable=True)

    destinations = relationship("Destination", back_populates="state_ut", cascade="all, delete-orphan")
    authorities = relationship("LocalAuthority", back_populates="state_ut", cascade="all, delete-orphan")
    packages = relationship("TourismPackage", back_populates="state_ut", cascade="all, delete-orphan")
    geofences = relationship("Geofence", back_populates="state_ut")

class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(Integer, ForeignKey("states_uts.id"), nullable=False)
    name = Column(String(120), nullable=False)
    category = Column(String(50), nullable=False) # Historical, Natural, Adventure, Cultural, Pilgrimage
    description = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    image_url = Column(String(255), nullable=False)
    safety_score = Column(Float, default=4.8) # Out of 5.0
    entry_fee = Column(String(60), default="Free")
    timings = Column(String(100), default="6:00 AM - 6:00 PM")
    is_featured = Column(Boolean, default=False)

    state_ut = relationship("StateUT", back_populates="destinations")

class Geofence(Base):
    __tablename__ = "geofences"

    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(Integer, ForeignKey("states_uts.id"), nullable=True)
    name = Column(String(120), nullable=False)
    zone_type = Column(String(30), nullable=False) # tourist_safety, restricted, hazard, protected
    description = Column(Text, nullable=False)
    center_latitude = Column(Float, nullable=False)
    center_longitude = Column(Float, nullable=False)
    radius_meters = Column(Float, nullable=False)
    warning_message = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)

    state_ut = relationship("StateUT", back_populates="geofences")

class TrackingSession(Base):
    __tablename__ = "tracking_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    last_latitude = Column(Float, nullable=True)
    last_longitude = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    share_with_contacts = Column(Boolean, default=True)

    user = relationship("User", back_populates="tracking_sessions")

class SOSIncident(Base):
    __tablename__ = "sos_incidents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    emergency_type = Column(String(50), nullable=False) # Medical, Accident, Lost tourist, Harassment/threat, Natural disaster, Other
    status = Column(String(30), default="reported") # reported, investigating, resolved
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)
    contact_phone = Column(String(30), nullable=True)
    reported_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    admin_notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="incidents")

class LocalAuthority(Base):
    __tablename__ = "local_authorities"

    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(Integer, ForeignKey("states_uts.id"), nullable=False)
    name = Column(String(150), nullable=False)
    category = Column(String(40), nullable=False) # police, tourist_police, hospital, ambulance, fire, disaster
    phone = Column(String(50), nullable=False)
    address = Column(Text, nullable=False)
    website = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    operating_hours = Column(String(60), default="24x7")
    is_emergency = Column(Boolean, default=True)

    state_ut = relationship("StateUT", back_populates="authorities")

class SafetyProtocol(Base):
    __tablename__ = "safety_protocols"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(60), nullable=False) # Solo Travel, Women's Safety, High-Altitude, Coastal, Wildlife, Scams, etc.
    title = Column(String(150), nullable=False)
    summary = Column(Text, nullable=False)
    warning_signs = Column(Text, nullable=False) # JSON or bulleted string
    dos = Column(Text, nullable=False) # JSON or newline separated
    donts = Column(Text, nullable=False)
    emergency_guidance = Column(Text, nullable=False)
    icon_name = Column(String(50), default="shield")

class TourismPackage(Base):
    __tablename__ = "tourism_packages"

    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(Integer, ForeignKey("states_uts.id"), nullable=False)
    provider_name = Column(String(120), default="Incredible India Authorized Partner")
    title = Column(String(150), nullable=False)
    destination = Column(String(120), nullable=False)
    duration_days = Column(Integer, nullable=False)
    duration_nights = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, nullable=True)
    travel_type = Column(String(50), default="Family & Leisure") # Adventure, Heritage, Family & Leisure, Solo, Spiritual
    max_group_size = Column(Integer, default=15)
    accommodation = Column(String(100), default="3-Star or 4-Star Certified Hotel")
    transportation = Column(String(100), default="AC SUV / Luxury Coach")
    meals = Column(String(100), default="Breakfast & Dinner Included")
    guide_included = Column(Boolean, default=True)
    safety_features = Column(Text, default="GPS Tracked, First Aid Kit, Female Guide on Request")
    itinerary = Column(Text, nullable=False)
    image_url = Column(String(255), nullable=False)
    rating = Column(Float, default=4.9)
    reviews_count = Column(Integer, default=48)

    state_ut = relationship("StateUT", back_populates="packages")
    bookings = relationship("Booking", back_populates="package")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    package_id = Column(Integer, ForeignKey("tourism_packages.id"), nullable=False)
    travel_date = Column(String(30), nullable=False)
    travelers_count = Column(Integer, default=1)
    total_amount = Column(Float, nullable=False)
    booking_status = Column(String(30), default="confirmed") # pending, confirmed, cancelled
    payment_status = Column(String(30), default="paid")
    booking_reference = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    package = relationship("TourismPackage", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    payment_method = Column(String(40), default="UPI / Card")
    transaction_id = Column(String(100), unique=True, nullable=False)
    payment_status = Column(String(30), default="success") # success, failed, refunded
    invoice_number = Column(String(60), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    booking = relationship("Booking", back_populates="payments")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    plan = Column(String(30), default="free") # free, premium, partner
    is_active = Column(Boolean, default=True)
    amount = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="subscription")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_type = Column(String(50), nullable=False) # Passport, Visa, Driving License, Travel Insurance, Permits
    document_name = Column(String(150), nullable=False)
    document_number = Column(String(100), nullable=True)
    expiry_date = Column(String(30), nullable=False) # YYYY-MM-DD
    file_type = Column(String(20), default="pdf") # pdf, jpg, png
    file_size_kb = Column(Integer, default=150)
    file_content_base64 = Column(Text, nullable=True) # Encrypted / encoded storage
    status = Column(String(30), default="valid") # valid, expiring_soon, expired
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="documents")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), default="127.0.0.1")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
