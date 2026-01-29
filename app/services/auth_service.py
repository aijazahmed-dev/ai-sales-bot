from sqlalchemy.orm import Session
from app.models.models import Admin
from app.utils.security import verify_password

def authenticate_admin(db: Session, email: str, password: str):
    admin = (
        db.query(Admin)
        .filter(Admin.email == email, Admin.is_active == 1)
        .first()
    )

    if not admin:
        return None

    if not verify_password(password, admin.hashed_password):
        return None

    return admin