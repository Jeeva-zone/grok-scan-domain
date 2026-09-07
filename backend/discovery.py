"""Passive subdomain discovery via Certificate Transparency (crt.sh)."""

import json
import logging
from typing import List, Set
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import ssl

from .config import REQUEST_TIMEOUT, USER_AGENT, MAX_CANDIDATES

logger = logging.getLogger(__name__)

def _fetch_crtsh(domain: str) -> List[dict]:
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}, method="GET")
    ctx = ssl.create_default_context()
    try:
        with urlopen(req, timeout=REQUEST_TIMEOUT, context=ctx) as resp:
            if resp.status != 200:
                raise RuntimeError(f"crt.sh returned HTTP {resp.status}")
            raw = resp.read().decode("utf-8", errors="replace")
            if not raw or not raw.strip():
                return []
            data = json.loads(raw)
            if not isinstance(data, list):
                return []
            return data
    except HTTPError as e:
        if e.code == 429:
            raise RuntimeError("RATE_LIMITED: crt.sh rate limit exceeded") from e
        raise RuntimeError(f"crt.sh HTTP error: {e.code}") from e
    except URLError as e:
        raise RuntimeError(f"crt.sh connection error: {e.reason}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError("crt.sh returned invalid JSON") from e
    except Exception as e:
        raise RuntimeError(f"crt.sh unexpected error: {type(e).__name__}") from e

def _normalize_name(name: str, root: str):
    if not name or not isinstance(name, str):
        return None
    n = name.strip().lower()
    if n.startswith("*."):
        n = n[2:]
    n = n.strip().rstrip(".")
    if not n:
        return None
    if n == root or n.endswith("." + root):
        return n
    return None

def discover_subdomains(domain: str) -> List[str]:
    candidates: Set[str] = set()
    candidates.add(domain)
    try:
        records = _fetch_crtsh(domain)
    except RuntimeError as e:
        msg = str(e)
        if "RATE_LIMITED" in msg:
            raise
        raise RuntimeError(f"DISCOVERY_UNAVAILABLE: {msg}") from e
    for record in records:
        if not isinstance(record, dict):
            continue
        name_value = record.get("name_value")
        if not name_value:
            continue
        for part in str(name_value).split("\n"):
            normalized = _normalize_name(part, domain)
            if normalized:
                candidates.add(normalized)
            if len(candidates) >= MAX_CANDIDATES:
                break
        if len(candidates) >= MAX_CANDIDATES:
            break
    result = sorted(candidates)[:MAX_CANDIDATES]
    logger.info("Discovered %d candidates for %s", len(result), domain)
    return result
