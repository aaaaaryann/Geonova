import math
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from security import get_current_user, require_auth

router = APIRouter(prefix="/api/safety", tags=["Tourist Safety & Emergency"])

def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

@router.get("/geofences", response_model=List[schemas.GeofenceOut])
def list_geofences(db: Session = Depends(get_db)):
    return db.query(models.Geofence).filter(models.Geofence.is_active == True).all()

@router.post("/geofence-check", response_model=schemas.GeofenceCheckResult)
def check_geofences(location: schemas.LocationUpdate, db: Session = Depends(get_db)):
    """Evaluate current coordinates against all active geofences."""
    geofences = db.query(models.Geofence).filter(models.Geofence.is_active == True).all()
    triggered = []
    highest_severity = "safe"
    warning_texts = []

    for gf in geofences:
        dist = haversine_distance_meters(location.latitude, location.longitude, gf.center_latitude, gf.center_longitude)
        if dist <= gf.radius_meters:
            triggered.append(gf)
            if gf.zone_type in ["restricted", "hazard"]:
                highest_severity = "danger" if gf.zone_type == "restricted" else "warning"
                warning_texts.append(gf.warning_message)
            elif gf.zone_type == "tourist_safety" and highest_severity == "safe":
                warning_texts.append(gf.warning_message)

    msg = " | ".join(warning_texts) if warning_texts else "You are within standard travel territory. Stay alert and enjoy your trip."

    return {
        "inside_geofence": len(triggered) > 0,
        "geofences_triggered": triggered,
        "alert_level": highest_severity,
        "message": msg
    }

@router.post("/tracking/update")
def update_live_location(
    location: schemas.LocationUpdate,
    user: Optional[models.User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates user live location session with consent."""
    if user:
        session = db.query(models.TrackingSession).filter(
            models.TrackingSession.user_id == user.id,
            models.TrackingSession.is_active == True
        ).first()

        now = datetime.datetime.now(datetime.timezone.utc)
        if not session:
            session = models.TrackingSession(
                user_id=user.id,
                start_time=now,
                is_active=True,
                last_latitude=location.latitude,
                last_longitude=location.longitude,
                last_updated=now,
                share_with_contacts=location.share_with_contacts
            )
            db.add(session)
        else:
            session.last_latitude = location.latitude
            session.last_longitude = location.longitude
            session.last_updated = now
            session.share_with_contacts = location.share_with_contacts
            
        db.commit()

    return {"status": "location_recorded", "lat": location.latitude, "lng": location.longitude}

@router.post("/tracking/stop")
def stop_tracking(user: models.User = Depends(require_auth), db: Session = Depends(get_db)):
    active_sessions = db.query(models.TrackingSession).filter(
        models.TrackingSession.user_id == user.id,
        models.TrackingSession.is_active == True
    ).all()
    for s in active_sessions:
        s.is_active = False
        s.end_time = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    return {"message": "Location tracking stopped. Session closed."}

@router.post("/sos", response_model=schemas.SOSIncidentOut)
def trigger_emergency_sos(
    payload: schemas.SOSCreate,
    user: Optional[models.User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Records an emergency SOS incident.
    Returns the created incident with emergency instructions and contact info.
    """
    user_id = user.id if user else None
    phone = payload.contact_phone or (user.phone_number if user else "Not provided")
    
    incident = models.SOSIncident(
        user_id=user_id,
        emergency_type=payload.emergency_type,
        status="reported",
        latitude=payload.latitude,
        longitude=payload.longitude,
        location_name=payload.location_name or "Detected GPS Location",
        description=payload.description or f"Emergency SOS triggered: {payload.emergency_type}",
        contact_phone=phone,
        reported_at=datetime.datetime.now(datetime.timezone.utc)
    )
    db.add(incident)

    # Log audit event
    audit = models.AuditLog(
        user_id=user_id,
        action="SOS_TRIGGERED",
        details=f"Type: {payload.emergency_type}, Lat: {payload.latitude}, Lng: {payload.longitude}"
    )
    db.add(audit)
    db.commit()
    db.refresh(incident)

    return incident

@router.get("/authorities", response_model=List[schemas.LocalAuthorityOut])
def list_local_authorities(
    category: Optional[str] = Query(None, description="police, tourist_police, hospital, ambulance, fire, disaster"),
    state_code: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.LocalAuthority)
    if category:
        query = query.filter(models.LocalAuthority.category == category.lower())
    if state_code:
        st = db.query(models.StateUT).filter(models.StateUT.code == state_code.upper()).first()
        if st:
            query = query.filter(models.LocalAuthority.state_id == st.id)

    authorities = query.all()

    # If coordinates are provided, sort by proximity
    if lat is not None and lng is not None:
        authorities.sort(key=lambda a: haversine_distance_meters(lat, lng, a.latitude, a.longitude))

    return authorities

@router.get("/protocols", response_model=List[schemas.SafetyProtocolOut])
def get_safety_protocols(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.SafetyProtocol)
    if category:
        query = query.filter(models.SafetyProtocol.category.ilike(f"%{category}%"))
    if search:
        query = query.filter(
            models.SafetyProtocol.title.ilike(f"%{search}%") |
            models.SafetyProtocol.summary.ilike(f"%{search}%") |
            models.SafetyProtocol.dos.ilike(f"%{search}%")
        )

    return query.all()
