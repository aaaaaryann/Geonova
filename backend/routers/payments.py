import uuid
import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from security import require_auth

router = APIRouter(prefix="/api/payments", tags=["Payments & Subscriptions"])

@router.get("/plans")
def get_subscription_plans():
    return [
        {
            "id": "free",
            "name": "Standard Traveler",
            "price": 0,
            "currency": "INR",
            "billing": "Forever Free",
            "description": "Essential safety and exploration features for casual domestic travelers.",
            "features": [
                "Full exploration of all 28 States & 8 Union Territories",
                "Instant Emergency SOS with 112 direct dialing",
                "Verified Local Authorities directory",
                "Standard Interactive OpenStreetMap exploration",
                "Complete 13-category Safety Protocols library"
            ],
            "is_popular": False
        },
        {
            "id": "premium",
            "name": "Geonova Shield Pro",
            "price": 999,
            "currency": "INR",
            "billing": "per month",
            "description": "Comprehensive safety suite with live geofencing radar and encrypted document vault.",
            "features": [
                "All Free Tier features included",
                "Real-time GPS geofence collision & audio hazard warnings",
                "Encrypted Travel Document Vault with expiry alerts",
                "Unlimited Live Location sharing with emergency contacts",
                "Exclusive discounts on verified tourism packages",
                "Priority 24/7 tourist concierge and assistance"
            ],
            "is_popular": False
        },
        {
            "id": "partner",
            "name": "Tourism Partner & Enterprise",
            "price": 3999,
            "currency": "INR",
            "billing": "per month",
            "description": "Designed for state tourism agencies, hotels, and licensed tour operators.",
            "features": [
                "All Shield Pro features included",
                "Publish & manage verified tourism packages",
                "Enterprise booking & guest safety tracking",
                "Authorized provider trust badge",
                "Direct incident dispatch integration API",
                "Comprehensive regional analytics dashboard"
            ],
            "is_popular": True
        },
        {
            "id": "elite",
            "name": "Guardian Elite",
            "price": 9999,
            "currency": "INR",
            "billing": "per month",
            "description": "Maximum protection with dedicated emergency response, air ambulance coordination, and 24/7 crisis support.",
            "features": [
                "All Tourism Partner features included",
                "Dedicated 24/7 personal SOS emergency responder",
                "Air ambulance & medical evacuation coordination",
                "Family emergency crisis hotline (toll-free)",
                "Real-time police & hospital dispatch on SOS trigger",
                "Geo-fenced panic button with instant authority alert",
                "Travel insurance liaison & on-ground legal assistance",
                "Priority incident escalation to District Collector office"
            ],
            "is_popular": False
        }
    ]

@router.post("/subscribe")
def upgrade_subscription(
    payload: schemas.SubscriptionCreate,
    user: models.User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    plan_prices = {"free": 0.0, "premium": 999.0, "partner": 3999.0, "elite": 9999.0}
    plan = payload.plan.lower()
    if plan not in plan_prices:
        raise HTTPException(status_code=400, detail="Invalid plan selected.")

    amount = plan_prices[plan]
    now = datetime.datetime.now(datetime.timezone.utc)
    expires = now + datetime.timedelta(days=365 if plan == "premium" else 30)

    sub = db.query(models.Subscription).filter(models.Subscription.user_id == user.id).first()
    if not sub:
        sub = models.Subscription(user_id=user.id, plan=plan, amount=amount, is_active=True, started_at=now, expires_at=expires)
        db.add(sub)
    else:
        sub.plan = plan
        sub.amount = amount
        sub.is_active = True
        sub.started_at = now
        sub.expires_at = expires

    # Record payment entry if not free
    if amount > 0:
        inv_num = f"INV-SUB-{uuid.uuid4().hex[:8].upper()}"
        payment = models.Payment(
            user_id=user.id,
            amount=amount,
            currency="INR",
            payment_method=payload.payment_method or "UPI Sandbox",
            transaction_id=f"TXN_SUB_{uuid.uuid4().hex[:10].upper()}",
            payment_status="success",
            invoice_number=inv_num
        )
        db.add(payment)

    audit = models.AuditLog(
        user_id=user.id,
        action="SUBSCRIPTION_UPDATED",
        details=f"Plan: {plan}, Amount: INR {amount}"
    )
    db.add(audit)
    db.commit()

    return {
        "status": "success",
        "plan": plan,
        "message": f"Successfully subscribed to {plan.capitalize()} Plan!",
        "expires_at": expires
    }

@router.get("/invoices")
def get_user_invoices(user: models.User = Depends(require_auth), db: Session = Depends(get_db)):
    payments = db.query(models.Payment).filter(models.Payment.user_id == user.id).order_by(models.Payment.created_at.desc()).all()
    invoices = []
    for p in payments:
        invoices.append({
            "invoice_number": p.invoice_number,
            "transaction_id": p.transaction_id,
            "amount": p.amount,
            "currency": p.currency,
            "payment_method": p.payment_method,
            "status": p.payment_status,
            "created_at": p.created_at,
            "customer_name": user.full_name,
            "customer_email": user.email
        })
    return invoices
