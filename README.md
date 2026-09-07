# 🟠 Orange Test

**Find Cloudflare-hosted subdomains** via passive Certificate Transparency discovery and official Cloudflare IP-range classification.

> **Authorization notice:** Use this tool only on domains you own or are authorized to assess. This is a passive research tool. No port scanning, vulnerability scanning, login testing, or exploitation is performed.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FJeeva-zone%2Fgrok-scan-domain&env=MAX_CANDIDATES,DNS_CONCURRENCY,REQUEST_TIMEOUT,MAX_RESULTS,RATE_LIMIT_SECONDS&envDescription=Optional%20tuning%20variables%20(defaults%20work)&project-name=orange-test&repository-name=orange-test)
[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/Jeeva-zone/grok-scan-domain)

---

## What it does

1. You enter a root domain (e.g. `speedtest.net`).
2. The backend queries [crt.sh](https://crt.sh) Certificate Transparency logs for related names.
3. Discovered hostnames are resolved to IPv4 and IPv6 addresses.
4. Each IP is checked against Cloudflare’s official public CIDR ranges.
5. **Only** results whose IP belongs to Cloudflare are returned and displayed with an orange indicator:

```
🟠 www.speedtest.net — 104.17.147.22
🟠 app.speedtest.net — 104.18.6.178
```

Unresolved hosts, non-Cloudflare IPs, and “gray” results are never shown.

---

## Features

- Passive subdomain discovery (Certificate Transparency / crt.sh)
- Server-side DNS resolution (A + AAAA)
- Official Cloudflare IP-range matching (cached)
- Clean dark security-dashboard UI (mobile / tablet / desktop)
- Live status stages + Cancel Scan (AbortController)
- Copy Results & Download CSV
- Rate limiting & resource caps
- Vercel-ready Python serverless API + Next.js frontend
- Health endpoint, structured errors, no stack traces to clients
- Accessibility (labels, focus, aria-live, keyboard)
- Zero secrets in frontend code

---

## Architecture

```
orange-test-web / grok-scan-domain
├── app/                          # Next.js App Router (frontend)
│   ├── page.tsx
│   ├── layout.tsx
│   ├── globals.css
│   └── components/
│       ├── DomainForm.tsx
│       ├── ScanStatus.tsx
│       ├── ResultsTable.tsx
│       └── HelpPanel.tsx
├── api/                          # Vercel Python serverless functions
│   ├── scan.py                   # POST /api/scan
│   └── health.py                 # GET  /api/health
├── backend/                      # Shared Python business logic
│   ├── config.py
│   ├── validation.py
│   ├── discovery.py              # crt.sh
│   ├── dns_resolver.py
│   ├── cloudflare_ranges.py
│   ├── scanner.py
│   ├── formatting.py
│   └── rate_limit.py
├── tests/
├── public/
├── .env.example
├── vercel.json
├── package.json
├── requirements.txt
├── README.md
└── LICENSE
```

**Request flow**

```
Browser  →  POST /api/scan  →  validate domain
                           →  rate-limit check
                           →  crt.sh discovery
                           →  concurrent DNS
                           →  Cloudflare CIDR match
                           →  return only 🟠 results
```

---

## One-click deploy

### Vercel (recommended)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FJeeva-zone%2Fgrok-scan-domain&env=MAX_CANDIDATES,DNS_CONCURRENCY,REQUEST_TIMEOUT,MAX_RESULTS,RATE_LIMIT_SECONDS&envDescription=Optional%20tuning%20variables%20(defaults%20work)&project-name=orange-test&repository-name=orange-test)

1. Click the button above.
2. Connect your GitHub account if prompted.
3. Accept the suggested environment variables (defaults are fine).
4. Deploy.

### Netlify

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/Jeeva-zone/grok-scan-domain)

> **Note:** The primary target is Vercel (Python serverless functions). Netlify works best if you adapt the API routes or use a Node-compatible backend. Prefer Vercel for the out-of-the-box experience.

---

## Local installation

### Prerequisites

- Node.js 18+
- Python 3.10+
- npm (or pnpm / yarn)

### Steps

```bash
git clone https://github.com/Jeeva-zone/grok-scan-domain.git
cd grok-scan-domain

# Frontend
npm install

# Optional Python virtual environment (for running tests / local scripts)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Environment
cp .env.example .env.local
```

---

## Environment variables

All variables are **server-side only**. Never prefix secrets with `NEXT_PUBLIC_`.

| Variable              | Default | Description                              |
|-----------------------|---------|------------------------------------------|
| `MAX_CANDIDATES`      | 1000    | Max hostnames from discovery             |
| `DNS_CONCURRENCY`     | 25      | Concurrent DNS lookups                   |
| `REQUEST_TIMEOUT`     | 30      | HTTP timeout (seconds)                   |
| `MAX_RESULTS`         | 500     | Max Cloudflare results returned          |
| `RATE_LIMIT_SECONDS`  | 60      | Minimum seconds between scans per IP     |
| `SCAN_TIMEOUT_SECONDS`| 90      | Soft scan budget                         |
| `CF_CACHE_TTL`        | 3600    | Cloudflare range cache TTL (seconds)     |
| `ALLOWED_ORIGINS`     | (empty) | Comma-separated CORS origins             |
| `API_ACCESS_KEY`      | (empty) | Optional server-side API key             |

---

## Local development

```bash
# Start Next.js frontend
npm run dev
# → http://localhost:3000
```

**Note:** `next dev` does not execute the Vercel Python functions.  
For full end-to-end testing of `/api/scan` use a Vercel preview deployment or the unit tests below.

### Run tests

```bash
python tests/test_validation.py
python tests/test_cloudflare_ranges.py
python tests/test_formatting.py
python tests/test_api_contract.py
```

---

## API documentation

### `GET /api/health`

```json
{ "status": "ok" }
```

### `POST /api/scan`

**Request**

```http
POST /api/scan
Content-Type: application/json

{
  "domain": "speedtest.net"
}
```

**Success (200)**

```json
{
  "success": true,
  "domain": "speedtest.net",
  "results": [
    {
      "hostname": "www.speedtest.net",
      "ip": "104.17.147.22",
      "cloudflare": true
    }
  ],
  "count": 1,
  "duration_ms": 1234,
  "discovery_source": "crt.sh",
  "note": "Certificate Transparency discovery may not find every subdomain."
}
```

Only records with `"cloudflare": true` are ever returned.

**Error example**

```json
{
  "success": false,
  "error": {
    "code": "INVALID_DOMAIN",
    "message": "Please enter a valid domain."
  }
}
```

| HTTP | Code                                   | Meaning                          |
|------|----------------------------------------|----------------------------------|
| 400  | `INVALID_DOMAIN`                       | Bad input                        |
| 429  | `RATE_LIMITED`                         | Too many requests                |
| 503  | `DISCOVERY_UNAVAILABLE`                | crt.sh problem                   |
| 503  | `CLOUDFLARE_VERIFICATION_UNAVAILABLE`  | CF ranges unreachable            |
| 500  | `INTERNAL_ERROR`                       | Unexpected server error          |

### Example curl

```bash
curl -X POST https://your-app.vercel.app/api/scan \
  -H "Content-Type: application/json" \
  -d '{"domain":"speedtest.net"}'
```

### CORS

Same-origin by default.  
To allow external clients set `ALLOWED_ORIGINS` to an explicit comma-separated list.  
Wildcard (`*`) CORS is **not** enabled.

---

## Rate limits & resource control

| Limit                     | Default |
|---------------------------|---------|
| Scans per client IP       | 1 / 60 s |
| Max candidate hostnames   | 1000    |
| Max returned results      | 500     |
| DNS concurrency           | 25      |
| Scan soft timeout         | 90 s    |

In-memory rate limiting is suitable for a basic single-instance deployment.  
The code is structured so a shared store (Redis / Vercel KV) can be added later.

---

## How the Cloudflare detection works

The backend periodically fetches:

- https://www.cloudflare.com/ips-v4  
- https://www.cloudflare.com/ips-v6  

Ranges are parsed as CIDR networks with Python’s `ipaddress` module and cached in memory (default 1 hour).  
An IP is classified as Cloudflare **only** if it falls inside one of these official ranges.  
HTTP header checks alone are never used.

---

## Certificate Transparency limitations

Certificate Transparency logs only contain domains that have appeared in publicly logged certificates.  
Many internal, short-lived, or DNS-only subdomains will **not** be discovered.  
This tool deliberately does **not** perform brute-force wordlist enumeration.

---

## Security guidance

- Never commit secrets, Telegram tokens, or API keys.
- Never expose private backend values via `NEXT_PUBLIC_` variables.
- Do not store submitted domains or scan results permanently by default.
- Do not send data to third-party analytics.
- Stack traces are never returned to the client.
- User input is never executed as shell commands or arbitrary code.

---

## Troubleshooting

| Symptom                                              | Possible cause                          |
|------------------------------------------------------|-----------------------------------------|
| “Subdomain discovery is temporarily unavailable”     | crt.sh down / rate-limited / network    |
| “Cloudflare verification is temporarily unavailable” | Cannot fetch ips-v4 / ips-v6            |
| Empty results                                        | No CT records on Cloudflare, or none resolved |
| 429                                                  | Wait `RATE_LIMIT_SECONDS` before retrying |
| Build fails on Vercel                                | Check Node / Python runtime settings    |

---

## Adding future features

The backend is organized so new capabilities can be added as modules, e.g.:

```
backend/features/
  orange_test/   ← current
  dns_lookup/
  http_status/
  ssl_info/
  ...
```

The frontend already contains a navigation placeholder (“More tools coming soon”).

---

## License

MIT – see [LICENSE](LICENSE).

---

**Passive research only.** Only scan domains you own or are authorized to assess.
