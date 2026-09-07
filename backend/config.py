"""Configuration for Orange Test backend."""

import os

MAX_CANDIDATES = int(os.getenv("MAX_CANDIDATES", "1000"))
DNS_CONCURRENCY = int(os.getenv("DNS_CONCURRENCY", "25"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
MAX_RESULTS = int(os.getenv("MAX_RESULTS", "500"))
RATE_LIMIT_SECONDS = int(os.getenv("RATE_LIMIT_SECONDS", "60"))
SCAN_TIMEOUT_SECONDS = int(os.getenv("SCAN_TIMEOUT_SECONDS", "90"))
CF_CACHE_TTL = int(os.getenv("CF_CACHE_TTL", "3600"))
USER_AGENT = os.getenv(
    "USER_AGENT",
    "OrangeTest/1.0 (+https://github.com/Jeeva-zone/grok-scan-domain; passive research tool)",
)
API_ACCESS_KEY = os.getenv("API_ACCESS_KEY", "")
ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()
]
