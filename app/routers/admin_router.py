from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from typing import List
from app.schemas.schemas import LeadResponse, LeadCreate, LeadUpdate, MessageResponse, DashboardStatsResponse
from app.crud.lead import get_all_leads, create_lead, get_lead_by_id, update_lead_info, mark_lead_as_interested, get_chat_history
from app.db.database import get_db
from app.services.analytics import get_stats
from app.auth.dependencies import get_current_admin
from datetime import datetime


router = APIRouter(
    prefix="/api/admin/leads",
    tags=["Admin"],
    dependencies=[Depends(get_current_admin)]
)


# Create a new lead
@router.post("/create", response_model=LeadResponse)
def create_new_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    return create_lead(db, lead)

# Update Lead
@router.patch("/{lead_id}/update", response_model=LeadResponse)
def update_lead(lead_id: int, data: LeadUpdate, db: Session = Depends(get_db)):
    lead = update_lead_info(db, lead_id, data)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
    

# Get a single lead by ID
@router.get("/{lead_id}/show-single-lead", response_model=LeadResponse)
def read_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

# Mark lead as interested
@router.post("/{lead_id}/mark-interested", response_model=LeadResponse)
def mark_interested(lead_id: int, db: Session = Depends(get_db)):
    lead = mark_lead_as_interested(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

# Chat history 
@router.get("/{lead_id}/history", response_model=List[MessageResponse])
def get_history(lead_id: int, db: Session = Depends(get_db)):
    messages = get_chat_history(db, lead_id)
    if messages is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return messages

# Analytics
@router.get("/stats", response_model=DashboardStatsResponse)
def dashboard_stats(
    start_date: str = Query(None, description="Start date in YYYY-MM-DD"),
    end_date: str = Query(None, description="End date in YYYY-MM-DD"),
    hot_only: bool = Query(False, description="Show only hot leads"),
    db: Session = Depends(get_db)
):
    # Parse dates
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    stats = get_stats(db, start_date=start_dt, end_date=end_dt, hot_only=hot_only)
    return stats


# Get all leads
@router.get("/", response_model=List[LeadResponse])
def read_leads(
    skip: int = 0,
    limit: int = 100,
    intent_detected: Optional[str] = Query(None, description="true/false filter for hot leads"),
    from_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    to_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    name: Optional[str] = Query(None, description="Search by lead name"),
    email: Optional[str] = Query(None, description="Search by lead email"),
    db: Session = Depends(get_db)
):
    # -------------------------------
    # Validate intent_detected
    # -------------------------------
    intent_bool: Optional[bool] = None
    if intent_detected is not None:
        if intent_detected.lower() == "true":
            intent_bool = True
        elif intent_detected.lower() == "false":
            intent_bool = False
        else:
            raise HTTPException(status_code=400, detail="Invalid intent_detected value. Use true or false.")

    # -------------------------------
    # Validate dates
    # -------------------------------
    from_dt = None
    to_dt = None
    if from_date:
        try:
            from_dt = datetime.fromisoformat(from_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid from_date format. Use YYYY-MM-DD")
    if to_date:
        try:
            to_dt = datetime.fromisoformat(to_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid to_date format. Use YYYY-MM-DD")

    # -------------------------------
    # Validate email
    # -------------------------------
    if email is not None and "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email format.")

    # -------------------------------
    # Call service
    # -------------------------------
    leads = get_all_leads(
        db,
        skip=skip,
        limit=limit,
        intent_detected=intent_bool,
        from_date=from_dt,
        to_date=to_dt,
        name=name,
        email=email
    )

    return leads






