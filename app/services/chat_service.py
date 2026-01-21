from sqlalchemy.orm import Session
from app.crud.chat import create_message, get_messages_by_lead_id
from app.services.llm_service import generate_response
from app.models.models import Lead
from app.crud.lead import mark_lead_as_interested, update_lead_info
from .intent_service import detect_intent
from app.utils.helpers import extract_user_info
from app.schemas.schemas import LeadUpdate
from app.services.notification_service import notify_human
from app.utils.helpers import try_notify_human


SYSTEM_PROMPT = """
You are a helpful SEO expert sales assistant for a digital marketing company.

Rules:
- Keep replies short (3-5 sentences maximum).
- Be concise, conversational, professional, and persuasive.
- Do NOT write long explanations or blog-style content.
- Answer like a live chat agent, not a blog post.
- If the user greets or introduces themselves, reply with a friendly greeting and ask how you can help with SEO.
- If the user asks anything unrelated to SEO or digital marketing, politely apologize and say you can only help with SEO-related questions.
- Provide clear SEO advice only when an SEO-related question is asked.
- No bullet lists or headings.
- If the user shows clear buying intent (pricing, packages, hiring, contact), politely ask for contact details.
- After taking contact details say thanks/thank you we will reach out you within one to two hours.
"""

def handle_first_message(db: Session, message: str) -> int:
    # Create anonymous lead
    lead = Lead()
    db.add(lead)
    db.commit()
    db.refresh(lead)

    # Save first user message
    create_message(
        db=db,
        lead_id=lead.id,
        role="user",
        content=message
    )

    # Return lead id
    return lead.id

def get_chat_history(db: Session, lead_id: int):
    messages = get_messages_by_lead_id(db, lead_id)
    return [{"role": m.role, "content": m.content} for m in messages]

def process_message(db: Session, lead_id: int, user_message: str,):
    """
    1. Fetch chat history
    2. Build LLM messages
    3. Call LLM to get reply
    4. Save user and bot messages
    5. Detect buying intent and mark lead if needed
    """

    # Fetch chat history
    chat_history = get_chat_history(db, lead_id)

    # Build LLM messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    # Call LLM
    bot_reply = generate_response(messages)

    # Save messages
    create_message(db, lead_id, "user", user_message)

    # Extract & save user info
    user_info = extract_user_info(user_message)
    if any(user_info.values()):
        lead_update = LeadUpdate(**user_info)
        update_lead_info(db, lead_id, lead_update)
        try_notify_human(db, lead_id)

    # Detect intent (simple keyword check; can replace with AI intent detection later)
    if detect_intent(user_message):
        mark_lead_as_interested(db, lead_id)
        try_notify_human(db, lead_id)

        # Only notify human if contact info exists AND hasn't been notified before
        # if lead.intent_detected and lead.email and lead.phone and not lead.human_notified:
        #     notify_human(lead)
        #     lead.human_notified = True
        #     db.commit()
        #     db.refresh(lead)

        # else:
        #     # Ask user for missing info
        #     missing = []
        #     if not lead.email:
        #         missing.append("email")
        #     if not lead.phone:
        #         missing.append("phone")
        #     missing_str = " or ".join(missing)
        #     bot_reply = f"{bot_reply.strip()} Could you please provide your {missing_str} so we can assist you further?"

    return bot_reply
