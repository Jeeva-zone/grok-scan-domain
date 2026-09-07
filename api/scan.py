"""POST /api/scan – Orange Test scan endpoint."""

from http.server import BaseHTTPRequestHandler
import json
import logging
import sys
import os
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.validation import validate_and_normalize
from backend.scanner import run_scan
from backend.rate_limit import check_rate_limit
from backend.config import ALLOWED_ORIGINS, API_ACCESS_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api.scan")

def _get_client_ip(headers) -> str:
    for key in ("x-forwarded-for", "x-real-ip", "cf-connecting-ip"):
        val = headers.get(key)
        if val:
            return val.split(",")[0].strip()
    return "unknown"

def _cors_headers(origin):
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-API-Key",
    }
    if ALLOWED_ORIGINS and origin and origin in ALLOWED_ORIGINS:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Vary"] = "Origin"
    return headers

class handler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict, origin=None):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        for k, v in _cors_headers(origin).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        origin = self.headers.get("Origin")
        self.send_response(204)
        for k, v in _cors_headers(origin).items():
            self.send_header(k, v)
        self.end_headers()

    def do_POST(self):
        origin = self.headers.get("Origin")
        try:
            if API_ACCESS_KEY:
                provided = self.headers.get("X-API-Key") or self.headers.get("Authorization", "").replace("Bearer ", "")
                if provided != API_ACCESS_KEY:
                    self._send_json(401, {"success": False, "error": {"code": "UNAUTHORIZED", "message": "Invalid or missing API key."}}, origin)
                    return
            client_ip = _get_client_ip(self.headers)
            allowed, retry_after = check_rate_limit(client_ip)
            if not allowed:
                self._send_json(429, {"success": False, "error": {"code": "RATE_LIMITED", "message": f"Please wait {retry_after} seconds before scanning again."}}, origin)
                return
            length = int(self.headers.get("Content-Length", 0))
            if length <= 0 or length > 10000:
                self._send_json(400, {"success": False, "error": {"code": "INVALID_REQUEST", "message": "Request body is required."}}, origin)
                return
            raw = self.rfile.read(length).decode("utf-8", errors="replace")
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                self._send_json(400, {"success": False, "error": {"code": "INVALID_JSON", "message": "Invalid JSON body."}}, origin)
                return
            domain_raw = data.get("domain", "")
            ok, domain, err_msg = validate_and_normalize(domain_raw)
            if not ok:
                self._send_json(400, {"success": False, "error": {"code": "INVALID_DOMAIN", "message": err_msg}}, origin)
                return
            try:
                result = run_scan(domain)
                self._send_json(200, result, origin)
            except RuntimeError as e:
                msg = str(e)
                if "RATE_LIMITED" in msg:
                    self._send_json(429, {"success": False, "error": {"code": "RATE_LIMITED", "message": "External service rate limit. Please try again later."}}, origin)
                elif "DISCOVERY_UNAVAILABLE" in msg:
                    self._send_json(503, {"success": False, "error": {"code": "DISCOVERY_UNAVAILABLE", "message": "Subdomain discovery is temporarily unavailable. Please try again later."}}, origin)
                elif "CLOUDFLARE_RANGES_UNAVAILABLE" in msg:
                    self._send_json(503, {"success": False, "error": {"code": "CLOUDFLARE_VERIFICATION_UNAVAILABLE", "message": "Cloudflare verification is temporarily unavailable. Please try again later."}}, origin)
                else:
                    logger.error("Scan RuntimeError: %s", msg)
                    self._send_json(502, {"success": False, "error": {"code": "EXTERNAL_ERROR", "message": "An external service error occurred. Please try again later."}}, origin)
            except Exception as e:
                logger.error("Unexpected scan error: %s\n%s", e, traceback.format_exc())
                self._send_json(500, {"success": False, "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred. Please try again later."}}, origin)
        except Exception as e:
            logger.error("Handler error: %s\n%s", e, traceback.format_exc())
            self._send_json(500, {"success": False, "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."}}, origin)

    def log_message(self, format, *args):
        pass
