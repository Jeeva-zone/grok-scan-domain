"use client";

import { FormEvent, useState } from "react";

interface DomainFormProps {
  onSubmit: (domain: string) => void;
  onCancel: () => void;
  isScanning: boolean;
  disabled?: boolean;
}

export default function DomainForm({ onSubmit, onCancel, isScanning, disabled = false }: DomainFormProps) {
  const [value, setValue] = useState("");
  const [localError, setLocalError] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed) {
      setLocalError("Please enter a valid domain, for example: speedtest.net");
      return;
    }
    const normalized = trimmed
      .toLowerCase()
      .replace(/^https?:\/\//, "")
      .replace(/^www\./, "")
      .split("/")[0]
      .replace(/\.$/, "");
    if (!/^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$/i.test(normalized)) {
      setLocalError("Please enter a valid domain, for example: speedtest.net");
      return;
    }
    setLocalError("");
    onSubmit(normalized);
  };

  return (
    <form onSubmit={handleSubmit} noValidate>
      <label htmlFor="domain-input" className="sr-only">Domain to scan</label>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        <input
          id="domain-input"
          type="text"
          inputMode="url"
          autoComplete="off"
          autoCapitalize="none"
          spellCheck={false}
          placeholder="Enter a domain, for example speedtest.net"
          value={value}
          onChange={(e) => { setValue(e.target.value); if (localError) setLocalError(""); }}
          disabled={isScanning || disabled}
          aria-invalid={!!localError}
          aria-describedby={localError ? "domain-error" : undefined}
          style={{
            width: "100%",
            padding: "0.85rem 1rem",
            fontSize: "1rem",
            background: "#0f1117",
            border: `1px solid ${localError ? "var(--error)" : "var(--card-border)"}`,
            borderRadius: "8px",
            color: "var(--text)",
            outline: "none",
          }}
        />
        {localError && (
          <p id="domain-error" role="alert" style={{ color: "var(--error)", fontSize: "0.9rem" }}>
            {localError}
          </p>
        )}
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
          <button
            type="submit"
            disabled={isScanning || disabled}
            aria-label="Start Orange Test"
            style={{
              flex: "1 1 auto",
              minWidth: "160px",
              padding: "0.85rem 1.25rem",
              fontSize: "1rem",
              fontWeight: 600,
              background: isScanning ? "#4a4a4a" : "linear-gradient(135deg, #ff8a00, #ff6b00)",
              color: "#fff",
              border: "none",
              borderRadius: "8px",
              opacity: isScanning || disabled ? 0.7 : 1,
              transition: "opacity 0.15s",
            }}
          >
            \ud83d\udfe0 Start Orange Test
          </button>
          {isScanning && (
            <button
              type="button"
              onClick={onCancel}
              aria-label="Cancel scan"
              style={{
                padding: "0.85rem 1.25rem",
                fontSize: "1rem",
                background: "transparent",
                color: "var(--text-secondary)",
                border: "1px solid var(--card-border)",
                borderRadius: "8px",
              }}
            >
              Cancel Scan
            </button>
          )}
        </div>
      </div>
    </form>
  );
}
