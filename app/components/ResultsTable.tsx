"use client";

interface Result {
  hostname: string;
  ip: string;
  cloudflare: boolean;
}

interface ResultsTableProps {
  results: Result[];
  domain: string;
  count: number;
  durationMs: number;
  onCopyAll: () => void;
  onDownloadCsv: () => void;
  onClear: () => void;
}

export default function ResultsTable({
  results, domain, count, durationMs, onCopyAll, onDownloadCsv, onClear,
}: ResultsTableProps) {
  const copyOne = async (hostname: string, ip: string) => {
    try {
      await navigator.clipboard.writeText(`\ud83d\udfe0 ${hostname} \u2014 ${ip}`);
    } catch {}
  };

  if (count === 0) {
    return (
      <div className="card" style={{ marginTop: "1.25rem" }}>
        <p style={{ color: "var(--text-secondary)" }}>
          No \ud83d\udfe0 Cloudflare subdomains were found for {domain}.
        </p>
        <div style={{ marginTop: "1rem" }}>
          <button type="button" onClick={onClear} style={{
            padding: "0.5rem 1rem", background: "transparent", color: "var(--text-secondary)",
            border: "1px solid var(--card-border)", borderRadius: "6px", fontSize: "0.9rem",
          }}>Clear</button>
        </div>
      </div>
    );
  }

  return (
    <div className="card" style={{ marginTop: "1.25rem" }}>
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "0.75rem", marginBottom: "1rem" }}>
        <div>
          <strong style={{ color: "var(--orange)" }}>{count}</strong>{" "}
          <span style={{ color: "var(--text-secondary)" }}>
            Cloudflare result{count !== 1 ? "s" : ""} \u00b7 {(durationMs / 1000).toFixed(1)}s
          </span>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          <button type="button" onClick={onCopyAll} aria-label="Copy all results" style={btnStyle}>Copy Results</button>
          <button type="button" onClick={onDownloadCsv} aria-label="Download CSV" style={btnStyle}>Download CSV</button>
          <button type="button" onClick={onClear} aria-label="Clear results" style={btnStyle}>Clear</button>
        </div>
      </div>
      <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "0.4rem" }}>
        {results.map((r) => (
          <li key={`${r.hostname}-${r.ip}`} style={{
            display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.5rem 0.65rem",
            background: "rgba(255, 138, 0, 0.06)", borderRadius: "6px", fontSize: "0.95rem", wordBreak: "break-all",
          }}>
            <span aria-hidden="true">\ud83d\udfe0</span>
            <span style={{ flex: 1 }}>
              <span style={{ fontWeight: 500 }}>{r.hostname}</span>
              <span style={{ color: "var(--text-secondary)" }}> \u2014 {r.ip}</span>
            </span>
            <button type="button" onClick={() => copyOne(r.hostname, r.ip)} aria-label={`Copy ${r.hostname}`} style={{
              background: "transparent", border: "none", color: "var(--text-secondary)", fontSize: "0.85rem", padding: "0.25rem 0.4rem", flexShrink: 0,
            }}>Copy</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

const btnStyle: React.CSSProperties = {
  padding: "0.45rem 0.85rem", background: "transparent", color: "var(--text)",
  border: "1px solid var(--card-border)", borderRadius: "6px", fontSize: "0.875rem",
};
