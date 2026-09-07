"""Cloudflare public IP range fetching, caching, and matching."""

import ipaddress
import logging
import time
from typing import List, Optional, Union
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import ssl

from .config import REQUEST_TIMEOUT, USER_AGENT, CF_CACHE_TTL

logger = logging.getLogger(__name__)

_cache: dict = {"networks": None, "fetched_at": 0.0}

def _fetch_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/plain"}, method="GET")
    ctx = ssl.create_default_context()
    with urlopen(req, timeout=REQUEST_TIMEOUT, context=ctx) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Cloudflare ranges HTTP {resp.status}")
        return resp.read().decode("utf-8", errors="replace")

def _parse_cidrs(text: str) -> List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]:
    networks = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            net = ipaddress.ip_network(line, strict=False)
            networks.append(net)
        except ValueError:
            logger.warning("Skipping invalid CIDR: %s", line)
    return networks

def get_cloudflare_networks(force_refresh: bool = False):
    now = time.time()
    if (not force_refresh and _cache["networks"] is not None and (now - _cache["fetched_at"]) < CF_CACHE_TTL):
        return _cache["networks"]
    try:
        v4_text = _fetch_text("https://www.cloudflare.com/ips-v4")
        v6_text = _fetch_text("https://www.cloudflare.com/ips-v6")
        networks = _parse_cidrs(v4_text) + _parse_cidrs(v6_text)
        if not networks:
            raise RuntimeError("No Cloudflare networks parsed")
        _cache["networks"] = networks
        _cache["fetched_at"] = now
        logger.info("Refreshed Cloudflare ranges: %d networks", len(networks))
        return networks
    except (HTTPError, URLError, RuntimeError, OSError) as e:
        if _cache["networks"] is not None:
            logger.warning("Cloudflare range fetch failed, using stale cache: %s", e)
            return _cache["networks"]
        raise RuntimeError(f"CLOUDFLARE_RANGES_UNAVAILABLE: {e}") from e

def is_cloudflare_ip(ip_str: str, networks: Optional[List] = None) -> bool:
    if networks is None:
        networks = get_cloudflare_networks()
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    for net in networks:
        try:
            if addr in net:
                return True
        except TypeError:
            continue
    return False
