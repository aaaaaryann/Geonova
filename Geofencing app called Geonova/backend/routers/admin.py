import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
import schemas
from database import get_db
from security import require_admin

router = APIRouter(prefix="/api/admin", tags=["Administration & Operations"])

class IncidentStatusUpdate(BaseModel):
    status: str # reported, investigating, resolved
    admin_notes: Optional[str] = None

class GeofenceCreateAdmin(BaseModel):
    name: str
    zone_type: str
    description: str
    center_latitude: float
    center_longitude: float
    radius_meters: float
    warning_message: str
    state_code: Optional[str] = None

@router.get("/stats")
def get_admin_stats(admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    total_users = db.query(models.User).count()
    total_geofences = db.query(models.Geofence).count()
    active_geofences = db.query(models.Geofence).filter(models.Geofence.is_active == True).count()
    open_incidents = db.query(models.SOSIncident).filter(models.SOSIncident.status != "resolved").count()
    total_incidents = db.query(models.SOSIncident).count()
    total_bookings = db.query(models.Booking).count()
    total_revenue = db.query(models.Payment).filter(models.Payment.payment_status == "success").all()
    revenue_sum = sum(p.amount for p in total_revenue)

    return {
        "total_users": total_users,
        "total_geofences": total_geofences,
        "active_geofences": active_geofences,
        "open_sos_incidents": open_incidents,
        "total_sos_incidents": total_incidents,
        "total_bookings": total_bookings,
        "total_revenue_inr": revenue_sum,
        "system_status": "Operational",
        "timestamp": datetime.datetime.now(datetime.timezone.utc)
    }

@router.get("/incidents", response_model=List[schemas.SOSIncidentOut])
def get_all_incidents(admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(models.SOSIncident).order_by(models.SOSIncident.reported_at.desc()).all()

@router.put("/incidents/{incident_id}")
def update_incident_status(
    incident_id: int,
    payload: IncidentStatusUpdate,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    incident = db.query(models.SOSIncident).filter(models.SOSIncident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident record not found.")

    incident.status = payload.status
    if payload.admin_notes:
        incident.admin_notes = payload.admin_notes
    if payload.status == "resolved":
        incident.resolved_at = datetime.datetime.now(datetime.timezone.utc)

    # Log audit
    audit = models.AuditLog(
        user_id=admin.id,
        action="INCIDENT_STATUS_UPDATED",
        details=f"Incident ID {incident_id} changed to {payload.status}"
    )
    db.add(audit)
    db.commit()
    db.refresh(incident)

    return incident

@router.post("/geofences")
def create_geofence(
    payload: GeofenceCreateAdmin,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    state_id = None
    if payload.state_code:
        st = db.query(models.StateUT).filter(models.StateUT.code == payload.state_code.upper()).first()
        if st:
            state_id = st.id

    gf = models.Geofence(
        state_id=state_id,
        name=payload.name,
        zone_type=payload.zone_type,
        description=payload.description,
        center_latitude=payload.center_latitude,
        center_longitude=payload.center_longitude,
        radius_meters=payload.radius_meters,
        warning_message=payload.warning_message,
        is_active=True
    )
    db.add(gf)
    db.commit()
    db.refresh(gf)
    return gf

@router.delete("/geofences/{geofence_id}")
def delete_geofence(
    geofence_id: int,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    gf = db.query(models.Geofence).filter(models.Geofence.id == geofence_id).first()
    if not gf:
        raise HTTPException(status_code=404, detail="Geofence not found.")
    db.delete(gf)
    db.commit()
    return {"message": "Geofence removed successfully."}

@router.get("/users")
def list_users(admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [{
        "id": u.id,
        "name": u.full_name,
        "email": u.email,
        "phone": u.phone_number,
        "role": u.role,
        "nationality": u.nationality,
        "created_at": u.created_at
    } for u in users]

@router.get("/audit-logs")
def get_audit_logs(admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    logs = db.query(models.AuditLog).order_by(models.AuditLog.created_at.desc()).limit(100).all()
    return [{
        "id": l.id,
        "user_id": l.user_id,
        "action": l.action,
        "details": l.details,
        "ip_address": l.ip_address,
        "created_at": l.created_at
    } for l in logs]
