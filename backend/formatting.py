"""Result formatting helpers (CSV, plain text)."""

from typing import List, Dict, Any
import csv
import io

def results_to_plain_text(results: List[Dict[str, Any]]) -> str:
    lines = []
    for r in results:
        lines.append(f"\ud83d\udfe0 {r['hostname']} \u2014 {r['ip']}")
    return "\n".join(lines)

def results_to_csv(results: List[Dict[str, Any]]) -> str:
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["hostname", "ip", "cloudflare"])
    for r in results:
        writer.writerow([r["hostname"], r["ip"], "true"])
    return output.getvalue()
