"use client";

import { useState } from "react";

export default function HelpPanel() {
  const [open, setOpen] = useState(false);
  return (
    <div style={{ marginTop: "1.5rem" }}>
      <button
        type="button"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        style={{
          background: "transparent",
          border: "none",
          color: "var(--text-secondary)",
          fontSize: "0.9rem",
          textDecoration: "underline",
          cursor: "pointer",
        }}
      >
        {open ? "Hide help" : "About this tool & limitations"}
      </button>
      {open && (
        <div className="card" style={{ marginTop: "0.75rem", fontSize: "0.9rem", color: "var(--text-secondary)", lineHeight: 1.6 }}>
          <p style={{ marginBottom: "0.75rem" }}>
            <strong style={{ color: "var(--text)" }}>Orange Test</strong> performs passive subdomain discovery using Certificate Transparency logs (crt.sh) and classifies resolved IPs against Cloudflare\u2019s official public IP ranges.
          </p>
          <p style={{ marginBottom: "0.75rem" }}>
            <strong style={{ color: "var(--text)" }}>Limitations:</strong> Certificate Transparency records do not guarantee discovery of every DNS subdomain. Only subdomains that have appeared in public certificates will be found. No brute-force enumeration is performed.
          </p>
          <p style={{ marginBottom: "0.75rem" }}>
            Only results whose resolved IP addresses belong to Cloudflare are shown (\ud83d\udfe0). Unresolved hosts and non-Cloudflare IPs are never displayed.
          </p>
          <p>
            <strong style={{ color: "var(--orange)" }}>Authorization:</strong> Use this tool only on domains you own or are authorized to assess. This is a passive research tool; no port scanning, vulnerability scanning, or exploitation is performed.
          </p>
        </div>
      )}
    </div>
  );
}
