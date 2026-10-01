"""Evidence collectors. Each returns plain data plus the provenance needed to cite it.

Sources (charter 'at minimum inspect'): roles/, top-level engine dirs, base-role files, git history
(all origin refs), MWO/CWO files, comms (successor of Agora) and the legacy agora tables,
experiment receipts (commit vocabulary + ew.experiments), WORK_STATE/STATUS files, the fleet
queue/census ledgers, MONITORS.md (scheduler/process registry), documented hosts.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import util
from .util import parse_time

REC, HDR_END, FS = "\x1e", "\x1d", "\x1f"


# ---------------------------------------------------------------- git

def ref_tips(git: util.Git) -> dict:
    out = {}
    for line in git.run("for-each-ref", "refs/remotes/origin", "--format=%(refname:short) %(objectname)").splitlines():
        parts = line.split()
        if len(parts) == 2 and not parts[0].endswith("/HEAD") and parts[0] != "origin":
            out[parts[0]] = parts[1]
    return out


def roles_on_ref(git: util.Git, ref: str) -> list:
    out = git.run("ls-tree", "-d", "--name-only", ref + ":roles", check=False)
    return [n for n in out.split() if n and n != "base-role"]


def branch_only_roles(git: util.Git, tips: dict, main_roles: set) -> dict:
    """roles/<X> present on some origin branch but not on main (e.g. Chiron). {name: [refs]}"""
    found = {}
    for ref in sorted(tips):
        if ref == "origin/main":
            continue
        for name in roles_on_ref(git, ref):
            if name not in main_roles:
                found.setdefault(name, []).append(ref)
    return found


def read_commits(git: util.Git, include: list, exclude_tips: list | None = None, since: str | None = None) -> list:
    """Non-merge commits reachable from `include` refs and not from `exclude_tips` (the incremental cursor)."""
    args = ["log", "--no-merges", "--name-only",
            "--format=" + REC + "%H" + FS + "%cI" + FS + "%an" + FS + "%s" + FS + "%(trailers:only,unfold)" + HDR_END]
    if since:
        args.append("--since=" + since)
    args += include
    if exclude_tips:
        args += ["--not"] + exclude_tips
    raw = git.run(*args, timeout=900)
    commits = []
    for rec in raw.split(REC):
        if not rec.strip():
            continue
        head, _, names = rec.partition(HDR_END)
        f = head.split(FS)
        if len(f) < 5:
            continue
        files = [n.strip() for n in names.splitlines() if n.strip()]
        commits.append({"sha": f[0], "time": f[1], "author": f[2], "subject": f[3], "trailers": f[4], "files": files})
    return commits


def main_contains(git: util.Git, sha: str) -> bool:
    return git.ok("merge-base", "--is-ancestor", sha, "origin/main")


def last_commit_for_paths(git: util.Git, paths: list) -> dict | None:
    out = git.run("log", "-1", "--no-merges", "--format=%H" + FS + "%cI" + FS + "%s", "origin/main", "--", *paths,
                  check=False).strip()
    if not out:
        return None
    sha, t, s = (out.split(FS) + ["", ""])[:3]
    return {"sha": sha, "time": t, "subject": s}


def show(git: util.Git, ref: str, path: str) -> str | None:
    out = git.run("show", ref + ":" + path, check=False)
    return out or None


# ---------------------------------------------------------------- seat files

ENTRY_ORDER = ("BOOTSTRAP.md", "STARTUP.md", "RESPONSIBILITIES.md", "ROLE.md", "CHARTER.md")
CURRENCY_RE = re.compile(r"(?i)^\s*currency:\s*(\d{4}-\d{2}-\d{2}(?:[T ][0-9:]+Z?)?)", re.M)


def seat_files(root: Path, seat: str) -> dict:
    d = root / "roles" / seat
    out = {"dir_exists": d.is_dir(), "entry_file": None, "status_text": None, "work_state": None,
           "currency": None}
    if not d.is_dir():
        return out
    for name in ENTRY_ORDER:
        if (d / name).is_file():
            out["entry_file"] = "roles/{}/{}".format(seat, name)
            txt = (d / name).read_text(encoding="utf-8", errors="replace")
            m = CURRENCY_RE.search(txt[:4000])
            out["currency"] = m.group(1) if m else None
            break
    if (d / "STATUS.md").is_file():
        out["status_text"] = (d / "STATUS.md").read_text(encoding="utf-8", errors="replace")
    ws = util.read_json(d / "WORK_STATE.json")
    if isinstance(ws, dict):
        out["work_state"] = ws
    return out


def newest_work_state(git: util.Git, root: Path, seat: str, tips: dict) -> tuple:
    """Newest WORK_STATE.json by updated_at across main and the seat's own branch namespace.

    MWO-0001: 'never infer inactivity from a stale STATUS file when a newer pushed branch or
    WORK_STATE exists' (Archaeon's lives only on origin/archaeon/mwo0001-2026-09-28).
    Returns (work_state, source_label).
    """
    best, label = None, None
    main_ws = util.read_json(root / "roles" / seat / "WORK_STATE.json")
    if isinstance(main_ws, dict):
        best, label = main_ws, "origin/main:roles/{}/WORK_STATE.json".format(seat)
    prefix = "origin/" + seat.lower() + "/"
    for ref in tips:
        if not ref.lower().startswith(prefix):
            continue
        txt = show(git, ref, "roles/{}/WORK_STATE.json".format(seat))
        if not txt:
            continue
        try:
            ws = json.loads(txt)
        except ValueError:
            continue
        if not isinstance(ws, dict):
            continue
        t_new = parse_time(ws.get("updated_at_utc") or ws.get("updated_at"))
        t_old = parse_time((best or {}).get("updated_at_utc") or (best or {}).get("updated_at"))
        if best is None or (t_new and (t_old is None or t_new > t_old)):
            best, label = ws, "{}:roles/{}/WORK_STATE.json".format(ref, seat)
    return best, label


def operator_prompt(git: util.Git, root: Path, seat: str) -> dict | None:
    """Newest operator-originated prompt directory for the seat (charter / creation / directive)."""
    pdir = root / "roles" / seat / "prompts"
    if not pdir.is_dir():
        return None
    cands = []
    for d in pdir.iterdir():
        if not d.is_dir():
            continue
        names = " ".join(p.name for p in d.iterdir()) if d.is_dir() else ""
        low = (d.name + " " + names).lower()
        if any(k in low for k in ("charter", "creation", "operator", "directive", "mission")):
            m = re.match(r"(\d{4}-\d{2}-\d{2})", d.name)
            if m:
                cands.append((m.group(1), d))
    if not cands:
        return None
    date, d = max(cands, key=lambda c: (c[0], c[1].name))
    rel = "roles/{}/prompts/{}".format(seat, d.name)
    lc = git.run("log", "-1", "--format=%cI", "origin/main", "--", rel, check=False).strip()
    first = ""
    for p in sorted(d.iterdir()):
        if p.suffix.lower() in (".md", ".txt") and "manifest" not in p.name.lower() and (
                "verbatim" in p.name.lower() or "operator" in p.name.lower()):
            try:
                first = " ".join(p.read_text(encoding="utf-8", errors="replace").split())[:220]
            except OSError:
                pass
            break
    return {"path": rel, "date": date, "committed": util.iso(parse_time(lc)) if lc else None, "excerpt": first}


# ---------------------------------------------------------------- ops ledgers

def ops_ledgers(root: Path) -> dict:
    fleet = root / "ops" / "fleet"
    cwos = sorted(fleet.glob("CWO_*.md"))
    cur = root / "ops" / "work_orders" / "CURRENT.md"
    mwo = None
    if cur.is_file():
        m = re.search(r"MWO-\d{4}", cur.read_text(encoding="utf-8", errors="replace")[:2000])
        mwo = m.group(0) if m else None
    return {
        "queue": util.read_json(fleet / "QUEUE.json", {}) or {},
        "census_v1": util.read_json(fleet / "CENSUS.json", {}) or {},
        "unowned": util.read_json(fleet / "UNOWNED.json", {}) or {},
        "current_mwo": mwo,
        "latest_cwo": "ops/fleet/" + cwos[-1].name if cwos else None,
        "cwo_files": ["ops/fleet/" + p.name for p in cwos],
    }


MON_COLS = ("name", "kind", "owner", "host", "input", "freshness", "dormancy", "alarm", "state", "productivity",
            "bound", "accountable_seat")


def monitors(root: Path) -> list:
    """Rows of roles/base-role/MONITORS.md, parsed exactly as archaeon/tests/test_base_role.py does
    (a line containing ' | ' that is not indented, not the header or the 'One row' prose)."""
    p = root / "roles" / "base-role" / "MONITORS.md"
    rows = []
    if not p.is_file():
        return rows
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if " | " not in line or line.startswith(("  ", "One row", "name |")):
            continue
        cols = [c.strip() for c in line.split(" | ")]
        if len(cols) < 9:
            continue
        rows.append(dict(zip(MON_COLS, cols)))
    return rows


EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def redact(text):
    """Published artifacts never carry an email address (the mailer's receipt names its recipient)."""
    return EMAIL_RE.sub("<redacted>", text) if isinstance(text, str) else text


# ---------------------------------------------------------------- database (read-only)

def _rows(conn, sql, params=()):
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]
    finally:
        conn.rollback()


def comms_agents(conn) -> dict:
    out = {}
    for r in _rows(conn, "select agent, status, machine, model, last_sync_at, last_active_at, last_bootstrap_at, "
                         "branch, worktree_path, last_sync_branch, last_sync_worktree, last_sync_sha, updated_at "
                         "from comms.agents"):
        out[r["agent"]] = r
    for r in _rows(conn, "select distinct on (agent) agent, instance, machine, last_sync_at, last_active_at "
                         "from comms.agent_instances order by agent, greatest(last_sync_at, last_active_at) desc nulls last"):
        out.setdefault(r["agent"], {})["newest_instance"] = r
    return out


def comms_messages(conn, after_id: int = 0) -> list:
    return _rows(conn, "select id, created_at, sender, sender_instance, recipients, kind, subject, machine "
                       "from comms.messages where id > %s order by id", (after_id,))


def ew_experiments(conn) -> dict:
    out = {}
    for r in _rows(conn, "select distinct on (agent_id) agent_id, experiment_id, title, project, git_commit, created_at "
                         "from ew.experiments order by agent_id, created_at desc"):
        out[r["agent_id"]] = r
    return out


def agora_heartbeats(conn) -> dict:
    try:
        return {r["agent_name"]: r for r in _rows(
            conn, "select agent_name, machine, status, last_heartbeat from agora.agent_heartbeats")}
    except Exception:
        return {}


def mailer_events(conn, hours: int = 72) -> list:
    """The existing mailer's own receipts (scripts/send_brief_email.py emit_event 'email_dispatched')."""
    try:
        return _rows(conn, "select stage, success, output_summary, error, finished_at from agora.intelligence_outputs "
                           "where stage = 'email_dispatched' and finished_at > now() - make_interval(hours => %s) "
                           "order by finished_at desc limit 40", (hours,))
    except Exception:
        return []
