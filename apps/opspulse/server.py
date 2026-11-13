"""OpsPulse server: stdlib-only HTTP server.

Serves the dashboard (static/) and JSON APIs backed by SQLite,
with a background thread re-running ingest on an interval so
freshly dropped log files and new git commits show up live.
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"
DB_PATH = BASE / "data" / "opspulse.db"
REFRESH_SECONDS = int(os.environ.get("OPSPULSE_REFRESH", "60"))
PORT = int(os.environ.get("PORT", "8100"))

import ingest as ingest_mod  # noqa: E402


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def meta(conn) -> dict:
    return {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM meta")}


def api_summary() -> dict:
    conn = db()
    m = meta(conn)
    open_n = conn.execute("SELECT COUNT(*) c FROM incidents WHERE status='open'").fetchone()["c"]
    total_n = conn.execute("SELECT COUNT(*) c FROM incidents").fetchone()["c"]
    deploy_n = conn.execute("SELECT COUNT(*) c FROM deploys").fetchone()["c"]
    events_n = conn.execute("SELECT COUNT(*) c FROM events").fetchone()["c"]
    # error rate over the last 30 minutes of log data
    rows = conn.execute(
        """SELECT
             COUNT(*) total,
             SUM(CASE WHEN level IN ('ERROR','CRITICAL','ALERT','EMERGENCY') THEN 1 ELSE 0 END) errors
           FROM events
           WHERE ts >= datetime((SELECT MAX(ts) FROM events), '-30 minutes')"""
    ).fetchone()
    conn.close()
    rate = (rows["errors"] / rows["total"] * 100) if rows["total"] else 0
    return {
        "open_incidents": open_n,
        "total_incidents": total_n,
        "deploys": deploy_n,
        "events": events_n,
        "error_rate": round(rate, 1),
        "last_refresh": m.get("last_refresh"),
        "log_window_end": m.get("log_end"),
        "sources": json.loads(m.get("sources") or "[]"),
        "refresh_seconds": REFRESH_SECONDS,
    }


def api_deploys() -> list[dict]:
    conn = db()
    rows = [dict(r) for r in conn.execute("SELECT * FROM deploys ORDER BY ts DESC")]
    conn.close()
    return rows


def api_incidents() -> list[dict]:
    conn = db()
    rows = [dict(r) for r in conn.execute("SELECT * FROM incidents")]
    for r in rows:
        r["tenants"] = json.loads(r["tenants"] or "[]")
        r["endpoints"] = json.loads(r["endpoints"] or "[]")
    conn.close()
    return rows


def api_incident_timeline(iid: int) -> dict:
    conn = db()
    inc = conn.execute("SELECT * FROM incidents WHERE id=?", (iid,)).fetchone()
    if not inc:
        conn.close()
        return {}
    timeline = [dict(r) for r in conn.execute(
        "SELECT ts, kind, detail FROM incident_events WHERE incident_id=? ORDER BY ts", (iid,))]
    conn.close()
    out = dict(inc)
    out["tenants"] = json.loads(out["tenants"] or "[]")
    out["endpoints"] = json.loads(out["endpoints"] or "[]")
    out["timeline"] = timeline
    return out


def api_series() -> dict:
    """Error-rate and event-volume series, bucketed."""
    conn = db()
    buckets = {}
    for r in conn.execute("SELECT ts, level FROM events"):
        minute = int(r["ts"][14:16])
        bucket_min = minute - (minute % ingest_mod.BUCKET_MINUTES)
        key = r["ts"][:14] + f"{bucket_min:02d}"
        b = buckets.setdefault(key, {"total": 0, "errors": 0, "warnings": 0})
        b["total"] += 1
        if r["level"] in ("ERROR", "CRITICAL", "ALERT", "EMERGENCY"):
            b["errors"] += 1
        elif r["level"] == "WARNING":
            b["warnings"] += 1
    conn.close()
    labels = sorted(buckets)
    return {
        "labels": labels,
        "total": [buckets[k]["total"] for k in labels],
        "errors": [buckets[k]["errors"] for k in labels],
        "warnings": [buckets[k]["warnings"] for k in labels],
        "error_rate": [round(buckets[k]["errors"] / buckets[k]["total"] * 100, 1) for k in labels],
    }


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        qs = parse_qs(urlparse(self.path).query)
        if path == "/api/summary":
            return self._json(api_summary())
        if path == "/api/deploys":
            return self._json(api_deploys())
        if path == "/api/incidents":
            return self._json(api_incidents())
        if path == "/api/incident":
            iid = int(qs.get("id", ["0"])[0])
            return self._json(api_incident_timeline(iid))
        if path == "/api/series":
            return self._json(api_series())
        if path == "/api/refresh":
            summary = ingest_mod.ingest()
            return self._json({"ok": True, **summary})
        if path == "/" or path == "/index.html":
            path = "/index.html"
        f = (STATIC / path.lstrip("/")).resolve()
        if not str(f).startswith(str(STATIC.resolve())) or not f.is_file():
            self.send_error(404)
            return
        ctype = {".html": "text/html", ".css": "text/css", ".js": "application/javascript",
                 ".svg": "image/svg+xml", ".png": "image/png"}.get(f.suffix, "application/octet-stream")
        body = f.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if urlparse(self.path).path == "/api/refresh":
            summary = ingest_mod.ingest()
            return self._json({"ok": True, **summary})
        self.send_error(404)


def refresher():
    while True:
        try:
            ingest_mod.ingest()
        except Exception as e:
            print(f"[ingest] error: {e}", flush=True)
        time.sleep(REFRESH_SECONDS)


def main():
    print(f"[ingest] initial run ...", flush=True)
    summary = ingest_mod.ingest()
    print(f"[ingest] {summary}", flush=True)
    threading.Thread(target=refresher, daemon=True).start()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[server] OpsPulse on :{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
