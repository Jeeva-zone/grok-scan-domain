"""Main scan orchestration: discover → resolve → filter Cloudflare."""

import logging
import time
from typing import Any, Dict, List

from .config import MAX_RESULTS
from .discovery import discover_subdomains
from .dns_resolver import resolve_hostnames
from .cloudflare_ranges import get_cloudflare_networks, is_cloudflare_ip

logger = logging.getLogger(__name__)

def run_scan(domain: str) -> Dict[str, Any]:
    start = time.time()
    results: List[Dict[str, Any]] = []
    try:
        candidates = discover_subdomains(domain)
    except RuntimeError as e:
        msg = str(e)
        if "RATE_LIMITED" in msg or "DISCOVERY_UNAVAILABLE" in msg:
            raise
        raise RuntimeError(f"DISCOVERY_UNAVAILABLE: {msg}") from e
    if not candidates:
        duration_ms = int((time.time() - start) * 1000)
        return {"success": True, "domain": domain, "results": [], "count": 0, "duration_ms": duration_ms, "discovery_source": "crt.sh", "note": "Certificate Transparency discovery may not find every subdomain."}
    try:
        networks = get_cloudflare_networks()
    except RuntimeError as e:
        raise RuntimeError(str(e)) from e
    resolved = resolve_hostnames(candidates)
    for hostname, ips in resolved.items():
        for ip in ips:
            if is_cloudflare_ip(ip, networks):
                results.append({"hostname": hostname, "ip": ip, "cloudflare": True})
                if len(results) >= MAX_RESULTS:
                    break
        if len(results) >= MAX_RESULTS:
            break
    results.sort(key=lambda r: (r["hostname"], r["ip"]))
    duration_ms = int((time.time() - start) * 1000)
    return {"success": True, "domain": domain, "results": results, "count": len(results), "duration_ms": duration_ms, "discovery_source": "crt.sh", "note": "Certificate Transparency discovery may not find every subdomain."}
