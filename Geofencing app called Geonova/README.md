# Geonova — Smart Tourist Safety & Tourism Promotion Platform

**Tagline:** "Explore Freely. Travel Safely."

Geonova is a modern, responsive, full-stack tourism and safety platform combining state-wise exploration across all **28 Indian states and 8 Union Territories** with real-time GPS tracking, geofencing, emergency SOS, document management, and payments.

---

## 🌟 Key Features

1. **Explore India (All 28 States & 8 Union Territories)**:
   - Dedicated structured pages for every single state and Union Territory.
   - High-quality photography, capitals, best travel seasons, official government tourism portals.
   - Major historical, natural, cultural, and adventure attractions with safety scores and entry fees.
   - Cultural traditions and local culinary delicacies.
   - Regional filters: Northern, Western & Central, Eastern, Southern, Northeastern.

2. **Real-Time Geofencing & GPS Radar**:
   - Interactive Leaflet / OpenStreetMap visual radar with layer toggles (Safe Tourist Corridors, Hazard Caution Zones, Restricted Areas).
   - Live location tracking with consent controls.
   - Real-time Haversine distance collision detection triggering audio alerts and on-screen hazard advisories.
   - Route simulator with pre-configured journeys (Delhi Heritage Walk, Goa Coastal, Manali Pass) to test alerts dynamically.

3. **Emergency SOS System**:
   - Prominent persistent SOS trigger button with pulse animation.
   - 3-second accidental activation countdown timer with cancel button.
   - Emergency category triage: Medical Emergency, Vehicle Accident, Threat / Harassment, Lost Tourist, Natural Disaster, Other.
   - Web Audio API emergency siren alarm synthesizer.
   - One-tap direct dialers for official Indian helplines (112 National, 100 Police, 102/108 Ambulance, 1090 Women, 1363 Tourist Helpline).
   - Automated incident logging to the database.

4. **Encrypted Document Vault**:
   - Store Passports, Visas, Driving Licenses, and Travel Insurance.
   - Automated expiration calculations: `Valid`, `Expiring Soon` (within 30 days), and `Expired`.
   - Base64 encrypted local & server storage with preview and deletion.

5. **Tourism Packages & Marketplace**:
   - Verified tour packages with certified guides and GPS tracking.
   - Interactive booking checkout flow with sandbox UPI and Card simulation.
   - Instant printable booking invoice receipt generation.

6. **Tourist & Admin Portals**:
   - **Tourist Dashboard:** Live trip telemetry, emergency contact management, saved documents, and booking receipts.
   - **Admin Command Console:** System KPIs, SOS incident triage (investigate / resolve with notes), new geofence polygon/radius creator, registered user directory, and security audit trail.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ installed
- Dependencies: `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `httpx`, `pytest`

### Running the Application
1. Double-click `start.bat` or run:
```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
2. Open your web browser and navigate to:
```
http://127.0.0.1:8000
```
3. Interactive OpenAPI documentation is accessible at:
```
http://127.0.0.1:8000/docs
```

---

## 🔑 Demo Accounts

| Role | Email | Password | Privileges |
|------|-------|----------|------------|
| **Chief Admin** | `admin@geonova.in` | `Admin@123` | Full admin telemetry, incident triage, geofence management, audit logs |
| **Tourist** | `tourist@geonova.in` | `Tourist@123` | Trip tracking, emergency contacts, document vault, tour bookings |
| **Provider** | `provider@geonova.in` | `Provider@123` | Tourism package manager & booking receipts |
| **Authority** | `police@geonova.in` | `Police@123` | Local assistance cell and helpline access |

*(Quick-fill login buttons are also provided on the sign-in modal for instant one-click testing.)*

---

## 🧪 Running Automated Tests

Run the full automated test suite:
```bash
python -m pytest tests/test_api.py -v
```

All 10 tests verify:
- API health check
- Exact 28 States & 8 Union Territories database presence
- Regional filtering
- State detail lookups
- Geofence collision distance algorithms
- Emergency SOS incident logging
- Safety protocols count
- Role-based authentication
- Tourism packages marketplace
- Subscription plans
