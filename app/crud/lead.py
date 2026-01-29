from sqlalchemy.orm import Session
from app.models.models import Lead
from app.schemas.schemas import LeadCreate, LeadUpdate
from .chat import get_messages_by_lead_id
from sqlalchemy import and_
from datetime import datetime

def create_lead(db: Session, lead: LeadCreate) -> Lead:
    db_lead = Lead(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        message=lead.message
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

def get_lead_by_id(db: Session, lead_id: int) -> Lead | None:
    return db.query(Lead).filter(Lead.id == lead_id).first()

def get_chat_history(db: Session, lead_id: int):
    lead_exists = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead_exists:
        return None
    
    messages = get_messages_by_lead_id(db, lead_id)
    return [{"role": m.role, "content": m.content} for m in messages]

def update_lead_info(db: Session, lead_id: int, data: LeadUpdate):
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        return None

    if data.name is not None and not lead.name:
        lead.name = data.name

    if data.email is not None and not lead.email:
        lead.email = data.email

    if data.phone is not None and not lead.phone:
        lead.phone = data.phone

    if data.intent_detected is not None:
        lead.intent_detected = data.intent_detected

    db.commit()
    db.refresh(lead)
    return lead

def get_all_leads(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    intent_detected: bool | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    name: str | None = None,
    email: str | None = None,
):
    query = db.query(Lead)

    if intent_detected is not None:
        query = query.filter(Lead.intent_detected == intent_detected)

    if from_date:
        from_dt = datetime.fromisoformat(from_date)
        query = query.filter(Lead.created_at >= from_dt)
    if to_date:
        to_dt = datetime.fromisoformat(to_date)
        query = query.filter(Lead.created_at <= to_dt)

    if name:
        query = query.filter(Lead.name.ilike(f"%{name}%"))  # case-insensitive partial match

    if email:
        query = query.filter(Lead.email == email)  # exact match

    leads = query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()
    return leads

def mark_lead_as_interested(db: Session, lead_id: int):
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        return None
    
    if not lead.intent_detected:
        lead.intent_detected = True
        db.commit()
        db.refresh(lead)
    return lead
