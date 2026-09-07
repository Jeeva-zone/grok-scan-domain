"use client";

import { useCallback, useRef, useState } from "react";
import DomainForm from "./components/DomainForm";
import ScanStatus from "./components/ScanStatus";
import ResultsTable from "./components/ResultsTable";
import HelpPanel from "./components/HelpPanel";

interface ScanResult {
  hostname: string;
  ip: string;
  cloudflare: boolean;
}

interface ScanResponse {
  success: boolean;
  domain?: string;
  results?: ScanResult[];
  count?: number;
  duration_ms?: number;
  discovery_source?: string;
  note?: string;
  error?: { code: string; message: string };
}

type Status =
  | "ready"
  | "validating"
  | "connecting"
  | "discovering"
  | "resolving"
  | "formatting"
  | "complete"
  | "cancelled"
  | "error";

export default function HomePage() {
  const [status, setStatus] = useState<Status>("ready");
  const [isError, setIsError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [results, setResults] = useState<ScanResult[]>([]);
  const [domain, setDomain] = useState("");
  const [count, setCount] = useState(0);
  const [durationMs, setDurationMs] = useState(0);
  const [isScanning, setIsScanning] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const resetResults = useCallback(() => {
    setResults([]);
    setCount(0);
    setDurationMs(0);
    setDomain("");
    setErrorMessage("");
    setIsError(false);
    setStatus("ready");
  }, []);

  const handleScan = useCallback(async (inputDomain: string) => {
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setIsScanning(true);
    setIsError(false);
    setErrorMessage("");
    setResults([]);
    setCount(0);
    setDurationMs(0);
    setDomain(inputDomain);
    setStatus("connecting");

    try {
      setStatus("discovering");
      const res = await fetch("/api/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain: inputDomain }),
        signal: controller.signal,
      });
      setStatus("resolving");
      let data: ScanResponse;
      try {
        data = await res.json();
      } catch {
        throw new Error("Invalid response from server");
      }
      if (!res.ok || !data.success) {
        const msg =
          data.error?.message ||
          (res.status === 429
            ? "Rate limited. Please wait before scanning again."
            : res.status === 503
            ? "Subdomain discovery is temporarily unavailable. Please try again later."
            : "An error occurred. Please try again later.");
        setIsError(true);
        setErrorMessage(msg);
        setStatus("error");
        return;
      }
      setStatus("formatting");
      const orange = (data.results || []).filter((r) => r.cloudflare === true);
      setResults(orange);
      setCount(data.count ?? orange.length);
      setDurationMs(data.duration_ms ?? 0);
      setStatus("complete");
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === "AbortError") {
        setStatus("cancelled");
        setIsError(false);
        setErrorMessage("");
      } else {
        setIsError(true);
        setErrorMessage(err instanceof Error ? err.message : "Network error. Please try again.");
        setStatus("error");
      }
    } finally {
      setIsScanning(false);
      abortRef.current = null;
    }
  }, []);

  const handleCancel = useCallback(() => {
    if (abortRef.current) abortRef.current.abort();
  }, []);

  const handleCopyAll = useCallback(async () => {
    const text = results.map((r) => `\ud83d\udfe0 ${r.hostname} \u2014 ${r.ip}`).join("\n");
    try {
      await navigator.clipboard.writeText(text);
    } catch {}
  }, [results]);

  const handleDownloadCsv = useCallback(() => {
    const header = "hostname,ip,cloudflare\n";
    const rows = results
      .map((r) => {
        const h = r.hostname.includes(",") ? `\"${r.hostname}\"` : r.hostname;
        const ip = r.ip.includes(",") ? `\"${r.ip}\"` : r.ip;
        return `${h},${ip},true`;
      })
      .join("\n");
    const blob = new Blob([header + rows], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `orange-test-${domain || "results"}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }, [results, domain]);

  return (
    <div className="container">
      <header style={{ marginBottom: "1.75rem" }}>
        <h1 style={{ fontSize: "1.75rem", fontWeight: 700, letterSpacing: "-0.02em", marginBottom: "0.35rem" }}>
          \ud83d\udfe0 Orange Test
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "1.05rem" }}>
          Find Cloudflare-hosted subdomains
        </p>
      </header>

      <nav aria-label="Features" style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem", fontSize: "0.9rem", color: "var(--text-secondary)" }}>
        <span style={{ color: "var(--orange)", fontWeight: 600 }}>\ud83d\udfe0 Orange Test</span>
        <span style={{ opacity: 0.6 }}>More tools coming soon</span>
      </nav>

      <div className="card">
        <DomainForm onSubmit={handleScan} onCancel={handleCancel} isScanning={isScanning} />
        {(status !== "ready" || isError) && <ScanStatus status={status} isError={isError} />}
        {isError && errorMessage && (
          <p role="alert" style={{ marginTop: "0.75rem", color: "var(--error)", fontSize: "0.95rem" }}>
            {errorMessage}
          </p>
        )}
      </div>

      {(status === "complete" || (results.length > 0 && status !== "cancelled")) && (
        <ResultsTable
          results={results}
          domain={domain}
          count={count}
          durationMs={durationMs}
          onCopyAll={handleCopyAll}
          onDownloadCsv={handleDownloadCsv}
          onClear={resetResults}
        />
      )}

      <p style={{ marginTop: "1.5rem", fontSize: "0.8rem", color: "var(--text-secondary)", textAlign: "center" }}>
        Use this tool only on domains you own or are authorized to assess.
      </p>

      <HelpPanel />
    </div>
  );
}
