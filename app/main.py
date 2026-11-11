from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import your routers
from app.routers import chat_router, admin_router

# Initialize FastAPI app
app = FastAPI(
    title="AI Customer Support & Lead Qualification Platform",
    description="Engage website visitors, detect buying intent, and notify humans via email.",
    version="1.0.0",
)

# Enable CORS (so your frontend chat widget can connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok"}

# Include routers
app.include_router(chat_router.router)
app.include_router(admin_router.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)