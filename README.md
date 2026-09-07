# 🟠 Orange Test

**Find Cloudflare-hosted subdomains** via passive Certificate Transparency discovery and official Cloudflare IP range classification.

> **Authorization notice:** Use this tool only on domains you own or are authorized to assess. This is a passive research tool.

---

## Features

- Passive subdomain discovery using crt.sh Certificate Transparency logs
- DNS resolution (A + AAAA) on the server
- Cloudflare IP classification against the official public ranges
- **Only** Cloudflare-matched results are returned and displayed (🟠)
- Responsive dark-themed UI
- Copy results & download CSV
- Rate limiting and resource caps
- Vercel-ready (Next.js + Python serverless API)

See the full README in the repository for installation, API docs, and deployment instructions.

## Quick start

```bash
npm install
npm run dev
```

## License

MIT
