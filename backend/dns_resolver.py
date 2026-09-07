"""DNS resolution for A and AAAA records with concurrency control."""

import concurrent.futures
import logging
import socket
from typing import Dict, List, Set

from .config import DNS_CONCURRENCY, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

def _resolve_one(hostname: str) -> List[str]:
    ips: Set[str] = set()
    try:
        infos = socket.getaddrinfo(hostname, None, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM)
        for info in infos:
            addr = info[4][0]
            if addr:
                ips.add(addr)
    except (socket.gaierror, socket.timeout, OSError) as e:
        logger.debug("DNS resolve failed for %s: %s", hostname, e)
    except Exception as e:
        logger.debug("Unexpected DNS error for %s: %s", hostname, e)
    return list(ips)

def resolve_hostnames(hostnames: List[str]) -> Dict[str, List[str]]:
    results: Dict[str, List[str]] = {}
    if not hostnames:
        return results
    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(min(REQUEST_TIMEOUT, 10))
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=DNS_CONCURRENCY) as executor:
            future_to_host = {executor.submit(_resolve_one, h): h for h in hostnames}
            for future in concurrent.futures.as_completed(future_to_host):
                host = future_to_host[future]
                try:
                    ips = future.result()
                    if ips:
                        results[host] = ips
                except Exception as e:
                    logger.debug("Resolver future error for %s: %s", host, e)
    finally:
        socket.setdefaulttimeout(old_timeout)
    logger.info("Resolved %d/%d hostnames", len(results), len(hostnames))
    return results
