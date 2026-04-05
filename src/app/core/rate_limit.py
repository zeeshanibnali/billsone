"""
Per-IP rate limiting via slowapi (in-memory storage by default).

Uses the direct TCP client address. Behind a reverse proxy, configure the proxy
or uvicorn to set the real client IP on the request (e.g. ProxyHeadersMiddleware)
so limits apply to actual clients, not the proxy.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Tune these for your traffic profile: burst per minute + sustained hourly cap.
DEFAULT_RATE_LIMITS = ["120/minute", "5000/hour"]

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=DEFAULT_RATE_LIMITS,
    headers_enabled=True,
)
