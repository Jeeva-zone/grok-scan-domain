"""Domain validation and normalization."""

import re
from typing import Tuple

DOMAIN_PATTERN = re.compile(
    r"^(?=.{1,253}$)(?!-)[a-z0-9-]{1,63}(?<!-)(\.(?!-)[a-z0-9-]{1,63}(?<!-))*\.[a-z]{2,}$",
    re.IGNORECASE,
)

def normalize_domain(raw: str) -> str:
    if not raw or not isinstance(raw, str):
        return ""
    domain = raw.strip().lower()
    for prefix in ("https://", "http://", "www."):
        if domain.startswith(prefix):
            domain = domain[len(prefix):]
    domain = domain.split("/")[0].split("?")[0].split("#")[0]
    domain = domain.rstrip(".")
    return domain

def is_valid_domain(domain: str) -> bool:
    if not domain or len(domain) > 253:
        return False
    if domain.startswith(".") or domain.endswith("."):
        return False
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain):
        return False
    if ":" in domain:
        return False
    return bool(DOMAIN_PATTERN.match(domain))

def validate_and_normalize(raw: str) -> Tuple[bool, str, str]:
    normalized = normalize_domain(raw)
    if not normalized:
        return False, "", "Please enter a valid domain, for example: speedtest.net"
    if not is_valid_domain(normalized):
        return False, "", "Please enter a valid domain, for example: speedtest.net"
    return True, normalized, ""
