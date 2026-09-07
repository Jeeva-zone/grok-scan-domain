"""API contract and scanner behavior tests with mocks."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from unittest.mock import patch
from backend.validation import validate_and_normalize
from backend.scanner import run_scan
from backend.formatting import results_to_csv

def test_invalid_domain_contract():
    ok, _, msg = validate_and_normalize("!!!")
    assert ok is False and "valid domain" in msg.lower()

def test_scanner_only_returns_cloudflare():
    fake_candidates = ["www.example.com", "cdn.example.com"]
    fake_resolved = {"www.example.com": ["104.17.147.22"], "cdn.example.com": ["8.8.8.8"]}
    with patch("backend.scanner.discover_subdomains", return_value=fake_candidates), \
         patch("backend.scanner.resolve_hostnames", return_value=fake_resolved), \
         patch("backend.scanner.get_cloudflare_networks", return_value=[]), \
         patch("backend.scanner.is_cloudflare_ip") as mock_cf:
        mock_cf.side_effect = lambda ip, nets=None: ip.startswith("104.")
        result = run_scan("example.com")
    assert result["success"] is True
    assert all(r["cloudflare"] is True for r in result["results"])
    assert not any(r["ip"] == "8.8.8.8" for r in result["results"])

def test_csv_only_orange():
    data = [{"hostname": "a.com", "ip": "1.1.1.1", "cloudflare": True}]
    assert "true" in results_to_csv(data) and "false" not in results_to_csv(data)

if __name__ == "__main__":
    test_invalid_domain_contract()
    test_scanner_only_returns_cloudflare()
    test_csv_only_orange()
    print("All API contract tests passed.")
