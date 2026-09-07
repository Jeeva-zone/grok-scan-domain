"""Tests for result formatting."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from backend.formatting import results_to_plain_text, results_to_csv

SAMPLE = [
    {"hostname": "www.speedtest.net", "ip": "104.17.147.22", "cloudflare": True},
    {"hostname": "app.speedtest.net", "ip": "104.18.6.178", "cloudflare": True},
]

def test_plain_text():
    text = results_to_plain_text(SAMPLE)
    assert "www.speedtest.net" in text and "104.17.147.22" in text
    assert "false" not in text.lower()

def test_csv():
    csv_str = results_to_csv(SAMPLE)
    assert "hostname,ip,cloudflare" in csv_str
    assert "www.speedtest.net,104.17.147.22,true" in csv_str
    assert "false" not in csv_str

if __name__ == "__main__":
    test_plain_text()
    test_csv()
    print("All formatting tests passed.")
