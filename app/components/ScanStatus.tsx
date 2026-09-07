"use client";

interface ScanStatusProps {
  status: string;
  isError?: boolean;
}

const STATUS_MESSAGES: Record<string, string> = {
  ready: "Ready.",
  validating: "Validating domain\u2026",
  connecting: "Connecting\u2026",
  discovering: "Discovering subdomains\u2026",
  resolving: "Resolving DNS and checking Cloudflare\u2026",
  formatting: "Preparing results\u2026",
  complete: "Complete.",
  cancelled: "Scan cancelled.",
  error: "Error.",
};

export default function ScanStatus({ status, isError = false }: ScanStatusProps) {
  const message = STATUS_MESSAGES[status] || status;
  return (
    <div
      role="status"
      aria-live="polite"
      aria-atomic="true"
      style={{
        marginTop: "1rem",
        padding: "0.65rem 0.9rem",
        borderRadius: "8px",
        background: isError ? "rgba(255, 95, 86, 0.12)" : "rgba(255, 138, 0, 0.08)",
        color: isError ? "var(--error)" : "var(--text-secondary)",
        fontSize: "0.95rem",
        display: "flex",
        alignItems: "center",
        gap: "0.5rem",
      }}
    >
      {status !== "ready" && status !== "complete" && status !== "cancelled" && status !== "error" && (
        <span
          aria-hidden="true"
          style={{
            width: "0.7rem",
            height: "0.7rem",
            borderRadius: "50%",
            border: "2px solid var(--orange)",
            borderTopColor: "transparent",
            animation: "spin 0.8s linear infinite",
            display: "inline-block",
          }}
        />
      )}
      <span>{message}</span>
      <style jsx>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
