from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    LLM_API_KEY: str
    
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_HOST: str | None = None
    SMTP_PORT: int | None = None
    NOTIFY_EMAIL: str | None = None
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
