from app.logging_config import setup_logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.rate_limit import limiter
import uvicorn
from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Import your routers
from app.routers import chat_router, admin_router

BASE_DIR = Path(__file__).resolve().parent.parent

setup_logging()

# ...uske baad baqi imports aur app = FastAPI(...)

# Initialize FastAPI app
app = FastAPI(
    title="AI Customer Support & Lead Qualification Platform",
    description="Engage website visitors, detect buying intent, and notify humans via email.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS (so your frontend chat widget can connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve URLs from static folder
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(BASE_DIR / "templates" / "index.html")

@app.get("/")
def health_check():
    return {"status": "ok"}

# Include routers
app.include_router(chat_router.router)
app.include_router(admin_router.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)