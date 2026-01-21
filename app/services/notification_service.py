import smtplib
from email.mime.text import MIMEText
from app.config import settings 

def notify_human(lead):
    if not all([settings.SMTP_HOST, settings.SMTP_PORT, settings.SMTP_USER,
                settings.SMTP_PASSWORD, settings.NOTIFY_EMAIL]):
        print("SMTP not configured, skipping email.")
        return
    
    subject = f"New Interested Lead: {lead.name or 'Anonymous'}"
    body = f"""
    Lead ID: {lead.id}
    Name: {lead.name or 'Anonymous'}
    Email: {lead.email or 'N/A'}
    Phone: {lead.phone or 'N/A'}
    Message: {lead.message or 'N/A'}
    """
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USER
    msg["To"] = settings.NOTIFY_EMAIL  # human agent

    try:
        with smtplib.SMTP(settings.SMTP_HOST, int(settings.SMTP_PORT)) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            print(f"✅ Email sent to {settings.NOTIFY_EMAIL} for lead {lead.id}")
    except Exception as e:
        print(f"Failed to send notification: {e}")
