"""Simple in-memory rate limiter (suitable for basic / single-instance use)."""

import time
import threading
from typing import Dict, Tuple

from .config import RATE_LIMIT_SECONDS

_lock = threading.Lock()
_last_request: Dict[str, float] = {}

def check_rate_limit(client_ip: str) -> Tuple[bool, int]:
    if not client_ip:
        client_ip = "unknown"
    now = time.time()
    with _lock:
        last = _last_request.get(client_ip, 0.0)
        elapsed = now - last
        if elapsed < RATE_LIMIT_SECONDS:
            retry = int(RATE_LIMIT_SECONDS - elapsed) + 1
            return False, retry
        _last_request[client_ip] = now
        if len(_last_request) > 10000:
            cutoff = now - RATE_LIMIT_SECONDS * 2
            to_del = [k for k, v in _last_request.items() if v < cutoff]
            for k in to_del:
                del _last_request[k]
        return True, 0
