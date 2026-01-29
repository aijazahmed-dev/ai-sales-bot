from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.db.session import SessionLocal
from app.models.models import Admin
from app.config import settings



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_super_admin():
    db: Session = SessionLocal()

    admin_exists = db.query(Admin).first()
    if admin_exists:
        db.close()
        return

    email = settings.ADMIN_EMAIL
    password = settings.ADMIN_PASSWORD

    if not email or not password:
        raise Exception("Super admin env vars not set")

    hashed_password = pwd_context.hash(password)

    admin = Admin(
        email=email,
        hashed_password=hashed_password,
        role="admin"
    )

    db.add(admin)
    db.commit()
    db.close()