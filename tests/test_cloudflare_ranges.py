"""Tests for Cloudflare IP matching."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import ipaddress
from backend.cloudflare_ranges import is_cloudflare_ip, _parse_cidrs

def test_parse_cidrs():
    text = "# comment\n104.16.0.0/13\n172.64.0.0/13\n2606:4700::/32\n"
    assert len(_parse_cidrs(text)) == 3

def test_cloudflare_ipv4_match():
    nets = [ipaddress.ip_network("104.16.0.0/13"), ipaddress.ip_network("172.64.0.0/13")]
    assert is_cloudflare_ip("104.17.147.22", nets) is True
    assert is_cloudflare_ip("8.8.8.8", nets) is False

def test_cloudflare_ipv6_match():
    nets = [ipaddress.ip_network("2606:4700::/32")]
    assert is_cloudflare_ip("2606:4700:4700::1111", nets) is True
    assert is_cloudflare_ip("2001:4860:4860::8888", nets) is False

if __name__ == "__main__":
    test_parse_cidrs()
    test_cloudflare_ipv4_match()
    test_cloudflare_ipv6_match()
    print("All Cloudflare range tests passed.")
