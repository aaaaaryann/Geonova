import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine, Base
import seed_data
import fix_images

from routers.auth import router as auth_router
from routers.tourism import router as tourism_router
from routers.safety import router as safety_router
from routers.packages import router as packages_router
from routers.vault import router as vault_router
from routers.payments import router as payments_router
from routers.admin import router as admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema and seed on startup
    Base.metadata.create_all(bind=engine)
    
    # Safe SQLite column migration for new auth fields
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(users)")).fetchall()
            existing_cols = [row[1] for row in result]
            if "aadhaar_number" not in existing_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN aadhaar_number VARCHAR(20)"))
            if "is_aadhaar_verified" not in existing_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_aadhaar_verified BOOLEAN DEFAULT 0"))
            if "auth_provider" not in existing_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN auth_provider VARCHAR(30) DEFAULT 'email'"))
            conn.commit()
    except Exception as mig_err:
        print(f"Migration note: {mig_err}")

    try:
        seed_data.seed_database()
    except Exception as e:
        print(f"Seed note: {e}")

    try:
        fix_images.fix_images()
    except Exception as e:
        print(f"Image update note: {e}")
    yield

app = FastAPI(
    title="Geonova API — Smart Tourist Safety & Tourism Promotion Platform",
    description="Full-stack API providing real-time geofencing, GPS tracking, emergency SOS, 36 Indian states/UTs discovery, travel packages, and secure document vault.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Always revalidate frontend assets so UI changes are never hidden by a stale browser cache
@app.middleware("http")
async def no_cache_frontend(request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path == "/" or path == "/index.html" or path.startswith("/static"):
        response.headers["Cache-Control"] = "no-cache, must-revalidate"
    return response

# Include Routers
app.include_router(auth_router)
app.include_router(tourism_router)
app.include_router(safety_router)
app.include_router(packages_router)
app.include_router(vault_router)
app.include_router(payments_router)
app.include_router(admin_router)

# Mount frontend static directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
@app.get("/index.html")
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Geonova backend is online. Explore documentation at /docs"}

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Geonova Smart Safety & Tourism Platform",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting Geonova Server at http://127.0.0.1:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
