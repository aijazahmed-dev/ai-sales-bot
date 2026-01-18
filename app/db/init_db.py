from .database import engine
from .base import Base
import app.models.models  # important: imports models

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Tables created successfully!")