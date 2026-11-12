import logging
import logging.config

from app.config import settings


def setup_logging() -> None:
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False, 
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",  
                "formatter": "default",
            },
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console"],
        },
        "loggers": {
            
            "sqlalchemy.engine": {"level": "WARNING"},
            "httpx": {"level": "WARNING"},   
        },
    })