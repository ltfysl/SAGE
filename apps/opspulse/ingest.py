"""OpsPulse ingest: parses SAGE's real log samples, meeting notes and git
history into a SQLite database the dashboard serves.

Sources (all inside the SAGE repo):
- data/samples/*.log              -> events + incidents
- data/samples/project_memory/meetings/weekly_sync.md -> recorded owners
- git history of the repo          -> deploys + file-level owner attribution
"""

from __future__ import annotations

import json
import re
import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(__file__).resolve().parent / "data" / "opspulse.db"
LOG_SOURCES = sorted((REPO_ROOT / "data" / "samples").glob("*.log"))
MEETING_NOTES = REPO_ROOT / "data" / "samples" / "project_memory" / "meetings" / "weekly_sync.md"
BUCKET_MINUTES = 5
OPEN_WINDOW_MINUTES = 30  # last-seen within this window of log end => open

LOG_LINE_RE = re.compile(
    r"^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]\s+(\w+)\.(\w+):\s+(.*)"
)

RECOVERY_RE = re.compile(
    r"restarted successfully|re-established|restored|health check passed|"
    r"worker restarted|horizon restarted",
    re.IGNORECASE,
)

# Recorded owners come from weekly_sync.md ("Owner: <name> <service>").
# Services they own map to incident components; anything else falls back to
# the git author of the implicated file, or "unassigned".
COMPONENT_OWNERS = {
    "database": "alice",   # Alice owns the event store service
    "queue": "alice",
    "api": "bob",          # Bob owns the frontend dashboard
    "frontend": "bob",
}

COMPONENT_KEYWORDS = [
    ("database", ("sqlstate", "queryexception", "connection refused", "too many connections", "slow query")),
    ("mailer", ("mail", "swift_transport", "sendgrid", "email")),
    ("queue", ("queue", "horizon", "redis", "worker", "maxattemptsexceeded", "job")),
    ("auth", ("authentication", "login", "password reset", "csrf")),
    ("api", ("500 internal", "404", "405", "http", "route", "endpoint", "/api/")),
    ("scorm", ("scorm", "manifest")),
]


def parse_log_file(path: Path) -> list[dict]:
    """Parse a Laravel log into structured blocks (multi-line aware)."""
    blocks = []
    current = None
    for line in path.read_text(errors="replace").split("\n"):
        m = LOG_LINE_RE.match(line)
        if m:
            if current:
                _finalize(current)
                blocks.append(current)
            ts, env, level, message = m.groups()
            current = {
                "ts": ts,
                "env": env,
                "level": level.upper(),
                "message": message.strip(),
                "exception": None,
                "file": None,
                "raw": [line],
                "source": path.name,
            }
        elif current is not None:
            current["raw"].append(line)
    if current:
        _finalize(current)
        blocks.append(current)
    return blocks


def _finalize(block: dict) -> None:
    raw = "\n".join(block["raw"])
    block["raw_block"] = raw
    exc = re.search(r'"exception":"([^"]*)"', raw)
    if exc:
        block["exception"] = exc.group(1)
    else:
        m = re.search(r"([A-Z][\w\\]*(?:Exception|Error|FatalError))", raw)
        block["exception"] = m.group(1) if m else None
    f = re.search(r'"file":"([^"]+)"', raw)
    if f:
        block["file"] = f.group(1)
    else:
        frames = re.findall(r"#\d+\s+(/[^:(]+\.[a-z]+)", raw)
        app_frames = [fr for fr in frames if "/vendor/" not in fr]
        block["file"] = app_frames[0] if app_frames else (frames[0] if frames else None)


def normalize_signature(block: dict) -> str:
    """Group blocks into one incident by normalized message + exception."""
    msg = block["message"].lower()
    msg = re.sub(r"[0-9a-f]{8,}", "<id>", msg)
    msg = re.sub(r"\d+", "<n>", msg)
    msg = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "<email>", msg)
    msg = re.sub(r"\d+\.\d+\.\d+\.\d+", "<ip>", msg)
    key = msg[:60]
    exc = (block["exception"] or "").split("\\")[-1]
    return f"{exc}:{key}" if exc else key


def component_of(block: dict) -> str:
    text = f"{block['message']} {block.get('exception') or ''} {block.get('file') or ''}".lower()
    for component, kws in COMPONENT_KEYWORDS:
        if any(kw in text for kw in kws):
            return component
    return "other"


def severity_of(group: dict) -> str:
    text = f"{group['signature']} {' '.join(e['message'] for e in group['events'][:3])}".lower()
    if any(k in text for k in ("connection refused", "too many connections", "fatalerror", "maxattemptsexceeded", "500 internal")):
        return "critical"
    if group["level"] == "ERROR" or group["count"] >= 10:
        return "high"
    if group["level"] == "WARNING" or group["count"] >= 3:
        return "medium"
    return "low"


def recovery_component(message: str) -> str:
    m = message.lower()
    if "redis" in m or "queue" in m or "horizon" in m or "worker" in m:
        return "queue"
    if "mail" in m:
        return "mailer"
    return "other"


def load_recorded_owners() -> dict[str, str]:
    """Owners recorded in the weekly sync: 'Owner: Alice event store service'."""
    owners = {}
    if MEETING_NOTES.exists():
        for line in MEETING_NOTES.read_text().splitlines():
            m = re.match(r"-?\s*Owner:\s*(\w+)\s+(.+)", line.strip())
            if m:
                owners[m.group(1).lower()] = m.group(2).strip()
    return owners


def git_author_of(rel_path: str) -> str | None:
    """Last commit author for a file inside the repo (real attribution)."""
    rel_path = re.sub(r":\d+$", "", rel_path)  # drop ":line" suffix
    stripped = rel_path.lstrip("/")
    candidates = [rel_path, "data/samples/codebases/laravel_sample/" + stripped]
    for prefix in ("var/www/app/", "var/www/"):
        if stripped.startswith(prefix):
            candidates.append("data/samples/codebases/laravel_sample/" + stripped[len(prefix):])
    for cand in candidates:
        try:
            out = subprocess.run(
                ["git", "log", "-1", "--format=%an", "--", cand],
                cwd=REPO_ROOT, capture_output=True, text=True, timeout=10,
            )
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.strip()
        except Exception:
            pass
    return None


def owner_for(component: str, implicated_file: str | None, owners: dict[str, str]) -> tuple[str, str]:
    """Return (owner, owner_source). All values trace to a real record."""
    name_key = COMPONENT_OWNERS.get(component)
    if name_key and name_key in owners:
        return name_key.title(), f"weekly sync: {owners[name_key]}"
    if name_key:
        return name_key.title(), "weekly sync"
    if implicated_file:
        author = git_author_of(implicated_file)
        if author:
            return author, f"git: last commit to {Path(implicated_file).name}"
    return "unassigned", "no recorded owner"


def fetch_deploys(limit: int = 25) -> list[dict]:
    """Real deploy events: commits pushed to the repo's main branch."""
    out = subprocess.run(
        ["git", "log", "origin/main", f"-{limit}", "--format=%H|%aI|%an|%s"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=15,
    )
    deploys = []
    for i, line in enumerate(out.stdout.splitlines()):
        parts = line.split("|", 3)
        if len(parts) != 4:
            continue
        sha, ts, author, subject = parts
        stat = subprocess.run(
            ["git", "show", "--format=", "--stat", sha],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=10,
        )
        files_changed = sum(1 for l in stat.stdout.splitlines() if "|" in l)
        deploys.append({
            "sha": sha[:7],
            "ts": ts,
            "author": author,
            "subject": subject,
            "files_changed": files_changed,
            "status": "deployed",
            "version": f"v1.{len(out.stdout.splitlines()) - i}",
        })
    return deploys


def ingest() -> dict:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript(
        """
        DROP TABLE IF EXISTS events;
        DROP TABLE IF EXISTS incidents;
        DROP TABLE IF EXISTS incident_events;
        DROP TABLE IF EXISTS deploys;
        DROP TABLE IF EXISTS meta;

        CREATE TABLE events (
            ts TEXT, env TEXT, level TEXT, message TEXT,
            exception TEXT, file TEXT, source TEXT
        );
        CREATE TABLE incidents (
            id INTEGER PRIMARY KEY,
            signature TEXT, title TEXT, severity TEXT, status TEXT,
            component TEXT, owner TEXT, owner_source TEXT,
            first_seen TEXT, last_seen TEXT, count INTEGER,
            exception TEXT, implicated_file TEXT, tenants TEXT, endpoints TEXT
        );
        CREATE TABLE incident_events (
            incident_id INTEGER, ts TEXT, kind TEXT, detail TEXT
        );
        CREATE TABLE deploys (
            sha TEXT, ts TEXT, author TEXT, subject TEXT,
            files_changed INTEGER, status TEXT, version TEXT
        );
        CREATE TABLE meta (key TEXT, value TEXT);
        """
    )

    owners = load_recorded_owners()
    all_blocks: list[dict] = []
    for path in LOG_SOURCES:
        all_blocks.extend(parse_log_file(path))
    all_blocks.sort(key=lambda b: b["ts"])

    log_end = max((b["ts"] for b in all_blocks), default=None)

    groups: dict[str, dict] = {}
    recoveries: list[dict] = []
    for b in all_blocks:
        if b["level"] in ("ERROR", "WARNING", "CRITICAL", "ALERT", "EMERGENCY"):
            sig = normalize_signature(b)
            g = groups.setdefault(sig, {"events": [], "level": b["level"], "signature": sig, "count": 0})
            g["events"].append(b)
            g["count"] += 1
            if b["level"] in ("CRITICAL", "ALERT", "EMERGENCY"):
                g["level"] = b["level"]
        elif b["level"] == "INFO" and RECOVERY_RE.search(b["message"]):
            recoveries.append(b)

    for b in all_blocks:
        c.execute(
            "INSERT INTO events VALUES (?,?,?,?,?,?,?)",
            (b["ts"], b["env"], b["level"], b["message"], b["exception"], b["file"], b["source"]),
        )

    incidents = []
    for sig, g in groups.items():
        evs = g["events"]
        first, last = evs[0]["ts"], evs[-1]["ts"]
        comp = component_of(evs[0])
        sev = severity_of(g)
        files = [e["file"] for e in evs if e["file"]]
        implicated = next((f for f in files if "/vendor/" not in f and "/app/" in f), files[0] if files else None)
        if not implicated:
            # fall back to an App\Foo\Bar class named in the message -> app/Foo/Bar.php
            for e in evs:
                m = re.search(r"App\\\\([A-Z][\w\\\\]*)", e["raw_block"]) or re.search(r"App\\([A-Z][\w\\]*)", e["raw_block"])
                if m:
                    implicated = "app/" + m.group(1).replace("\\\\", "/").replace("\\", "/") + ".php"
                    break
        owner, owner_src = owner_for(comp, implicated, owners)

        last_dt = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(log_end, "%Y-%m-%d %H:%M:%S") if log_end else last_dt
        matched_recoveries = [r for r in recoveries if r["ts"] >= last and recovery_component(r["message"]) in (comp, "other")]
        resolved = bool(matched_recoveries) and (end_dt - last_dt) > timedelta(minutes=OPEN_WINDOW_MINUTES)
        status = "resolved" if resolved else "open"

        tenants = sorted({json.loads(m.group(0))["tenant"] for e in evs if (m := re.search(r'\{[^}]*"tenant"[^}]*\}', e["raw_block"]))})
        endpoints = sorted({m.group(1) for e in evs if (m := re.search(r'"path":"([^"]+)"', e["raw_block"]))})

        short = evs[0]["message"]
        title = short if len(short) <= 90 else short[:87] + "..."
        incidents.append({
            "signature": sig, "title": title, "severity": sev, "status": status,
            "component": comp, "owner": owner, "owner_source": owner_src,
            "first_seen": first, "last_seen": last, "count": g["count"],
            "exception": evs[0]["exception"], "implicated_file": implicated,
            "tenants": json.dumps(tenants), "endpoints": json.dumps(endpoints),
            "_events": evs, "_recoveries": matched_recoveries,
        })

    sev_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    incidents.sort(key=lambda i: (0 if i["status"] == "open" else 1, sev_rank[i["severity"]], i["last_seen"]))

    for inc in incidents:
        cur = c.execute(
            """INSERT INTO incidents
               (signature,title,severity,status,component,owner,owner_source,
                first_seen,last_seen,count,exception,implicated_file,tenants,endpoints)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (inc["signature"], inc["title"], inc["severity"], inc["status"], inc["component"],
             inc["owner"], inc["owner_source"], inc["first_seen"], inc["last_seen"], inc["count"],
             inc["exception"], inc["implicated_file"], inc["tenants"], inc["endpoints"]),
        )
        iid = cur.lastrowid
        evs = inc["_events"]
        c.execute("INSERT INTO incident_events VALUES (?,?,?,?)",
                  (iid, evs[0]["ts"], "detected", evs[0]["message"]))
        # Recurrence timeline entries, coalesced per ~15 min window
        last_marked = evs[0]["ts"]
        pending = 0
        for e in evs[1:]:
            gap = (datetime.strptime(e["ts"], "%Y-%m-%d %H:%M:%S")
                   - datetime.strptime(last_marked, "%Y-%m-%d %H:%M:%S"))
            if gap > timedelta(minutes=15) and pending:
                c.execute("INSERT INTO incident_events VALUES (?,?,?,?)",
                          (iid, last_marked, "recurrence", f"{pending} more occurrence{'s' if pending != 1 else ''}"))
                pending = 0
            pending += 1
            last_marked = e["ts"]
        if pending:
            c.execute("INSERT INTO incident_events VALUES (?,?,?,?)",
                      (iid, last_marked, "recurrence", f"{pending} more occurrence{'s' if pending != 1 else ''}"))
        for r in inc["_recoveries"]:
            c.execute("INSERT INTO incident_events VALUES (?,?,?,?)",
                      (iid, r["ts"], "recovery", r["message"]))
        c.execute("INSERT INTO incident_events VALUES (?,?,?,?)",
                  (iid, log_end, "status",
                   "Still open at end of log window" if inc["status"] == "open"
                   else "Resolved — no further occurrences"))

    for d in fetch_deploys():
        c.execute("INSERT INTO deploys VALUES (?,?,?,?,?,?,?)",
                  (d["sha"], d["ts"], d["author"], d["subject"], d["files_changed"], d["status"], d["version"]))

    c.execute("INSERT INTO meta VALUES (?,?)", ("last_refresh", datetime.utcnow().isoformat() + "Z"))
    c.execute("INSERT INTO meta VALUES (?,?)", ("log_end", log_end or ""))
    c.execute("INSERT INTO meta VALUES (?,?)", ("sources", json.dumps([p.name for p in LOG_SOURCES])))
    conn.commit()
    summary = {
        "events": len(all_blocks), "incidents": len(incidents),
        "open": sum(1 for i in incidents if i["status"] == "open"),
    }
    conn.close()
    return summary


if __name__ == "__main__":
    print(json.dumps(ingest()))
