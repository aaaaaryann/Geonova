import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add backend directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from main import app
from seed_data import seed_database

# Ensure database is seeded for tests
seed_database()

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_states_and_uts_exact_36():
    """Verify all 28 states and 8 union territories are present."""
    response = client.get("/api/tourism/states")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 36, f"Expected 36 States & UTs, got {len(data)}"
    
    # Check breakdown
    states = [s for s in data if s["category"] == "state"]
    uts = [s for s in data if s["category"] == "union_territory"]
    assert len(states) == 28, f"Expected 28 states, got {len(states)}"
    assert len(uts) == 8, f"Expected 8 union territories, got {len(uts)}"

def test_regional_filter():
    response = client.get("/api/tourism/states?region=Northern")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    names = [s["name"] for s in data]
    assert "Delhi" in names
    assert "Rajasthan" in names
    assert "Ladakh" in names

def test_state_detail():
    response = client.get("/api/tourism/states/RJ")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Rajasthan"
    assert data["capital"] == "Jaipur"
    assert len(data["destinations"]) >= 2

def test_geofences_and_collision_check():
    response = client.get("/api/safety/geofences")
    assert response.status_code == 200
    geofences = response.json()
    assert len(geofences) >= 5

    # Check Connaught Place safe zone coordinate (28.6315, 77.2167)
    check_payload = {"latitude": 28.6315, "longitude": 77.2167}
    check_res = client.post("/api/safety/geofence-check", json=check_payload)
    assert check_res.status_code == 200
    res_data = check_res.json()
    assert res_data["inside_geofence"] is True
    assert "Safe Tourist Zone" in res_data["message"]

def test_emergency_sos():
    sos_payload = {
        "emergency_type": "Medical emergency",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "location_name": "Near India Gate, New Delhi",
        "description": "Tourist sprained ankle and needs immediate medical assistance",
        "contact_phone": "+91 9999988888"
    }
    response = client.post("/api/safety/sos", json=sos_payload)
    assert response.status_code == 200
    incident = response.json()
    assert incident["emergency_type"] == "Medical emergency"
    assert incident["status"] == "reported"
    assert incident["id"] is not None

def test_safety_protocols_count():
    response = client.get("/api/safety/protocols")
    assert response.status_code == 200
    protocols = response.json()
    assert len(protocols) >= 13

def test_auth_login_tourist_and_admin():
    # Login tourist
    login_tourist = client.post("/api/auth/login", json={
        "email": "tourist@geonova.in",
        "password": "Tourist@123"
    })
    assert login_tourist.status_code == 200
    assert "access_token" in login_tourist.json()
    assert login_tourist.json()["user"]["role"] == "tourist"

    # Login admin
    login_admin = client.post("/api/auth/login", json={
        "email": "admin@geonova.in",
        "password": "Admin@123"
    })
    assert login_admin.status_code == 200
    assert login_admin.json()["user"]["role"] == "admin"

def test_tourism_packages():
    response = client.get("/api/packages/")
    assert response.status_code == 200
    pkgs = response.json()
    assert len(pkgs) >= 3

def test_subscription_plans():
    response = client.get("/api/payments/plans")
    assert response.status_code == 200
    plans = response.json()
    assert len(plans) == 3
    plan_ids = [p["id"] for p in plans]
    assert "free" in plan_ids
    assert "premium" in plan_ids
    assert "partner" in plan_ids

def test_google_auth():
    res = client.post("/api/auth/google", json={
        "email": "traveler.priya@gmail.com",
        "full_name": "Priya Sharma"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "traveler.priya@gmail.com"
    assert data["user"]["auth_provider"] == "google"

def test_phone_otp_flow():
    # Send OTP
    send_res = client.post("/api/auth/phone/send-otp", json={
        "phone_number": "+91 9876501234"
    })
    assert send_res.status_code == 200
    otp = send_res.json()["demo_otp"]
    assert len(otp) == 6

    # Verify OTP
    verify_res = client.post("/api/auth/phone/verify-otp", json={
        "phone_number": "+91 9876501234",
        "otp": otp,
        "full_name": "Karan Singhania"
    })
    assert verify_res.status_code == 200
    data = verify_res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "tourist"

def test_aadhaar_otp_flow():
    # Invalid without consent
    no_consent = client.post("/api/auth/aadhaar/send-otp", json={
        "aadhaar_number": "5489 2104 7782",
        "consent": False
    })
    assert no_consent.status_code == 400

    # Valid send OTP
    send_res = client.post("/api/auth/aadhaar/send-otp", json={
        "aadhaar_number": "5489 2104 7782",
        "consent": True
    })
    assert send_res.status_code == 200
    otp = send_res.json()["demo_otp"]

    # Verify OTP
    verify_res = client.post("/api/auth/aadhaar/verify-otp", json={
        "aadhaar_number": "5489 2104 7782",
        "otp": otp,
        "full_name": "Vikramaditya Rathore"
    })
    assert verify_res.status_code == 200
    data = verify_res.json()
    assert data["user"]["is_aadhaar_verified"] is True
    assert data["user"]["nationality"] == "Indian"
    assert "5489 2104 7782" in data["user"]["aadhaar_number"]

