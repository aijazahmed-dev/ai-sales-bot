from sqlalchemy.orm import Session
from app.crud.lead import get_lead_by_id
from app.services.notification_service import notify_human
import re

def extract_user_info(message: str) -> dict:
    """
    Extracts name, email, and phone from user message.
    Only captures the name if explicitly mentioned using "my name is"
    Email: regex
    Phone: 10-15 digits
    """
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", message)
    phone_match = re.search(r"\b\d{10,15}\b", message)

    # Only extract name if user says "my name is ..."
    name = None
    match = re.search(r"\bmy name is ([\w\s]+)", message, re.IGNORECASE)
    if match:
        name = match.group(1).strip().title()

    return {
        "name": name,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None
    }

def try_notify_human(db: Session, lead_id: int):
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        return

    if (
        lead.intent_detected
        and lead.email
        and lead.phone
        and not lead.human_notified
    ):
        notify_human(lead)
        lead.human_notified = True
        db.commit()
        db.refresh(lead)
