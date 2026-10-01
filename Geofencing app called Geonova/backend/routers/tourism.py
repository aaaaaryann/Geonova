from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/tourism", tags=["Tourism Exploration"])

@router.get("/states", response_model=List[schemas.StateUTOut])
def list_states_and_uts(
    region: Optional[str] = Query(None, description="Filter by region: Northern, Southern, Eastern, Western/Central, Northeastern"),
    category: Optional[str] = Query(None, description="Filter by state or union_territory"),
    search: Optional[str] = Query(None, description="Search by state name or keyword"),
    db: Session = Depends(get_db)
):
    query = db.query(models.StateUT)
    if region:
        query = query.filter(models.StateUT.region.ilike(f"%{region}%"))
    if category:
        query = query.filter(models.StateUT.category == category.lower())
    if search:
        query = query.filter(models.StateUT.name.ilike(f"%{search}%"))

    return query.order_by(models.StateUT.name).all()

@router.get("/states/{code}", response_model=schemas.StateUTOut)
def get_state_detail(code: str, db: Session = Depends(get_db)):
    state = db.query(models.StateUT).filter(models.StateUT.code == code.upper()).first()
    if not state:
        # Check by name as fallback
        state = db.query(models.StateUT).filter(models.StateUT.name.ilike(code)).first()
    if not state:
        raise HTTPException(status_code=404, detail="State or Union Territory not found.")
    return state

@router.get("/destinations", response_model=List[schemas.DestinationOut])
def list_destinations(
    state_code: Optional[str] = None,
    category: Optional[str] = None,
    featured_only: Optional[bool] = False,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Destination)
    if state_code:
        state = db.query(models.StateUT).filter(models.StateUT.code == state_code.upper()).first()
        if state:
            query = query.filter(models.Destination.state_id == state.id)
    if category:
        query = query.filter(models.Destination.category.ilike(f"%{category}%"))
    if featured_only:
        query = query.filter(models.Destination.is_featured == True)
    if search:
        query = query.filter(
            models.Destination.name.ilike(f"%{search}%") | 
            models.Destination.description.ilike(f"%{search}%")
        )

    return query.all()
