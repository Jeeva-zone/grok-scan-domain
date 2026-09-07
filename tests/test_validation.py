"""Tests for domain validation and normalization."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from backend.validation import normalize_domain, is_valid_domain, validate_and_normalize
from backend.discovery import _normalize_name

def test_normalize_basic():
    assert normalize_domain("SpeedTest.NET") == "speedtest.net"
    assert normalize_domain("  speedtest.net.  ") == "speedtest.net"
    assert normalize_domain("https://www.speedtest.net/path") == "speedtest.net"

def test_valid_domains():
    assert is_valid_domain("speedtest.net") is True
    assert is_valid_domain("sub.example.co.uk") is True

def test_invalid_domains():
    assert is_valid_domain("") is False
    assert is_valid_domain("192.168.1.1") is False
    assert is_valid_domain("no_tld") is False

def test_validate_and_normalize_ok():
    ok, domain, err = validate_and_normalize("  WWW.SpeedTest.Net  ")
    assert ok is True and domain == "speedtest.net"

def test_wildcard_normalization():
    assert _normalize_name("*.speedtest.net", "speedtest.net") == "speedtest.net"
    assert _normalize_name("APP.SPEEDTEST.NET.", "speedtest.net") == "app.speedtest.net"
    assert _normalize_name("other.com", "speedtest.net") is None

if __name__ == "__main__":
    test_normalize_basic()
    test_valid_domains()
    test_invalid_domains()
    test_validate_and_normalize_ok()
    test_wildcard_normalization()
    print("All validation tests passed.")
