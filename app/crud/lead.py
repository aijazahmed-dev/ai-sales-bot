from sqlalchemy.orm import Session
from app.models.models import Lead
from app.schemas.schemas import LeadCreate, LeadUpdate

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

def update_lead(db, lead, lead_data: LeadUpdate):
    for field, value in lead_data.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)

    db.commit()
    db.refresh(lead)
    return lead

def get_all_leads(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(Lead)
        .order_by(Lead.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def mark_lead_as_interested(db: Session, lead: Lead) -> Lead:
    lead.intent_detected = True
    db.commit()
    db.refresh(lead)
    return lead
