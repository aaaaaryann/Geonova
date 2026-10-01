import uuid
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from security import require_auth

router = APIRouter(prefix="/api/packages", tags=["Tourism Packages & Bookings"])

@router.get("/", response_model=List[schemas.TourismPackageOut])
def list_packages(
    state_code: Optional[str] = None,
    travel_type: Optional[str] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.TourismPackage)
    if state_code:
        st = db.query(models.StateUT).filter(models.StateUT.code == state_code.upper()).first()
        if st:
            query = query.filter(models.TourismPackage.state_id == st.id)
    if travel_type:
        query = query.filter(models.TourismPackage.travel_type.ilike(f"%{travel_type}%"))
    if max_price:
        query = query.filter(models.TourismPackage.price <= max_price)
    if search:
        query = query.filter(
            models.TourismPackage.title.ilike(f"%{search}%") |
            models.TourismPackage.destination.ilike(f"%{search}%")
        )

    return query.all()

@router.get("/{package_id}", response_model=schemas.TourismPackageOut)
def get_package_detail(package_id: int, db: Session = Depends(get_db)):
    pkg = db.query(models.TourismPackage).filter(models.TourismPackage.id == package_id).first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Tourism package not found.")
    return pkg

@router.post("/book", response_model=schemas.BookingOut)
def book_package(
    payload: schemas.BookingCreate,
    user: models.User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    pkg = db.query(models.TourismPackage).filter(models.TourismPackage.id == payload.package_id).first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Package not found.")

    unit_price = pkg.discount_price if pkg.discount_price else pkg.price
    total_amount = unit_price * max(payload.travelers_count, 1)

    booking_ref = f"SY-BK-{uuid.uuid4().hex[:8].upper()}"
    invoice_num = f"INV-{uuid.uuid4().hex[:8].upper()}"

    booking = models.Booking(
        user_id=user.id,
        package_id=pkg.id,
        travel_date=payload.travel_date,
        travelers_count=payload.travelers_count,
        total_amount=total_amount,
        booking_status="confirmed",
        payment_status="paid",
        booking_reference=booking_ref
    )
    db.add(booking)
    db.flush()

    payment = models.Payment(
        booking_id=booking.id,
        user_id=user.id,
        amount=total_amount,
        currency="INR",
        payment_method=payload.payment_method or "UPI / Card",
        transaction_id=f"TXN_{uuid.uuid4().hex[:12].upper()}",
        payment_status="success",
        invoice_number=invoice_num
    )
    db.add(payment)

    # Log audit
    audit = models.AuditLog(
        user_id=user.id,
        action="PACKAGE_BOOKED",
        details=f"Booking Ref: {booking_ref}, Amount: INR {total_amount}"
    )
    db.add(audit)
    db.commit()
    db.refresh(booking)

    return {
        "id": booking.id,
        "package_id": pkg.id,
        "package_title": pkg.title,
        "travel_date": booking.travel_date,
        "travelers_count": booking.travelers_count,
        "total_amount": booking.total_amount,
        "booking_status": booking.booking_status,
        "payment_status": booking.payment_status,
        "booking_reference": booking.booking_reference,
        "created_at": booking.created_at
    }

@router.get("/user/my-bookings", response_model=List[schemas.BookingOut])
def get_user_bookings(user: models.User = Depends(require_auth), db: Session = Depends(get_db)):
    bookings = db.query(models.Booking).filter(models.Booking.user_id == user.id).all()
    results = []
    for b in bookings:
        pkg = db.query(models.TourismPackage).filter(models.TourismPackage.id == b.package_id).first()
        results.append({
            "id": b.id,
            "package_id": b.package_id,
            "package_title": pkg.title if pkg else "Custom Travel Package",
            "travel_date": b.travel_date,
            "travelers_count": b.travelers_count,
            "total_amount": b.total_amount,
            "booking_status": b.booking_status,
            "payment_status": b.payment_status,
            "booking_reference": b.booking_reference,
            "created_at": b.created_at
        })
    return results
