"""Small shared helpers: time, git, read-only database access, provenance fields."""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
from pathlib import Path

UTC = dt.timezone.utc


def now_utc() -> dt.datetime:
    return dt.datetime.now(UTC)


def iso(t: dt.datetime | None) -> str | None:
    if t is None:
        return None
    return t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_time(s) -> dt.datetime | None:
    """Parse the timestamp spellings seats actually write; None when unparseable."""
    if s is None:
        return None
    if isinstance(s, dt.datetime):
        return s if s.tzinfo else s.replace(tzinfo=UTC)
    s = str(s).strip()
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    for cand in (s, s.replace(" ", "T", 1)):
        try:
            t = dt.datetime.fromisoformat(cand)
            return t if t.tzinfo else t.replace(tzinfo=UTC)
        except ValueError:
            pass
    for fmt in ("%Y-%m-%dT%H:%M%z", "%Y-%m-%d"):
        try:
            t = dt.datetime.strptime(s, fmt)
            return t if t.tzinfo else t.replace(tzinfo=UTC)
        except ValueError:
            pass
    return None


def age_hours(t: dt.datetime | None, now: dt.datetime) -> float | None:
    if t is None:
        return None
    return (now - t).total_seconds() / 3600.0


def human_age(hours: float | None) -> str:
    if hours is None:
        return "never"
    if hours < 0:
        return "future?"
    if hours < 1:
        return "{}m".format(int(hours * 60))
    if hours < 48:
        return "{:.0f}h".format(hours)
    return "{:.0f}d".format(hours / 24)


def field(value, source, source_time=None, observed=None, confidence="MEDIUM", **extra):
    """A provenance-carrying field: value plus where it came from and how sure we are."""
    out = {"value": value, "source": source,
           "source_time": iso(source_time) if isinstance(source_time, dt.datetime) else source_time,
           "observed_at": iso(observed) if isinstance(observed, dt.datetime) else observed,
           "confidence": confidence}
    out.update(extra)
    return out


class Git:
    """git -C <root> with a timeout; returns stdout (text) and raises on failure when check=True."""

    def __init__(self, root: Path, timeout: int = 300):
        self.root = Path(root)
        self.timeout = timeout

    def run(self, *args, check=True, timeout=None) -> str:
        r = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout or self.timeout)
        if check and r.returncode != 0:
            raise RuntimeError("git {} failed ({}): {}".format(" ".join(args[:3]), r.returncode, r.stderr.strip()[:400]))
        return r.stdout

    def ok(self, *args) -> bool:
        r = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True, timeout=self.timeout)
        return r.returncode == 0


def read_json(path: Path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=False, default=str) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def db_connect_readonly(repo_root: Path):
    """Connect to the canonical M1 store through comms' own guarded connector, read-only.

    Returns (conn, None) or (None, reason). The census never writes to the database: the
    session is forced READ ONLY so even a coding mistake cannot mutate comms/ew/agora.
    """
    import sys
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    try:
        from comms import api  # noqa: WPS433 (runtime import: optional dependency)
        conn = api.connect()
        cur = conn.cursor()
        cur.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY")
        conn.commit()  # the session setting outlives this transaction
        cur.execute("SHOW default_transaction_read_only")
        if cur.fetchone()[0] != "on":
            conn.close()
            return None, "could not force the session read-only"
        conn.rollback()
        return conn, None
    except Exception as e:  # unreachable host, missing driver, identity guard refusal
        return None, "{}: {}".format(type(e).__name__, str(e)[:300])
