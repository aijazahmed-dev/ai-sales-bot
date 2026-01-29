from contextlib import asynccontextmanager
from app.startup import create_super_admin

@asynccontextmanager
async def lifespan(app):
    # 🔹 STARTUP
    create_super_admin()

    yield