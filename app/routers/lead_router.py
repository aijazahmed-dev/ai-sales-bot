from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.schemas import LeadCreate, LeadResponse
from app.crud.lead import create_lead, get_lead_by_id, get_all_leads

router = APIRouter(
    prefix="/leads",
    tags=["Leads"]
)

# Create a new lead
@router.post("/", response_model=LeadResponse)
def create_new_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    return create_lead(db, lead)

# Get a single lead by ID
@router.get("/{lead_id}", response_model=LeadResponse)
def read_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

# Get all leads
@router.get("/", response_model=List[LeadResponse])
def read_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_all_leads(db, skip=skip, limit=limit)
