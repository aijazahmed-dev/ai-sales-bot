from slowapi import Limiter
from slowapi.util import get_remote_address

# Limits per client IP. Stored in memory (per server process).
# Behind Caddy/Nginx, start uvicorn with --proxy-headers so the REAL visitor IP is used.
limiter = Limiter(key_func=get_remote_address)
