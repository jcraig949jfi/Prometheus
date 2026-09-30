"""Fleet status: make stale seat state visible without a fleet review (CWO 2026-09-30, BUILDER-OBSERVABILITY).

Reads every roles/<Seat>/WORK_STATE.json at a git ref (default origin/main), the current MWO id from
ops/work_orders/CURRENT.md, and optionally Fabric and comms, then flags:

  STALE_MWO     the seat's mwo_id is not the current MWO
  STALE_UPDATE  updated_at_utc older than --stale-hours
  NO_QUEUE      no current/next fields (CWO s5 format not adopted)
  IDLE_HOLD     HOLD with nothing blocked and no operator decision (CWO 1.1: HOLD is exceptional)
  IDLE_WORKERS  Fabric has online workers and no non-terminal Tasks

Usage: python ops/fleet/fleet_status.py [--ref origin/main] [--stale-hours 12] [--no-db] [--json]
Read-only. Exit code 0 always; the report is the product.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys


def _git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8").stdout


def current_mwo(ref):
    m = re.search(r"MWO-\d{4}", _git("show", ref + ":ops/work_orders/CURRENT.md"))
    return m.group(0) if m else None


def work_states(ref):
    out = {}
    for path in _git("ls-tree", "-r", "--name-only", ref, "roles/").split():
        parts = path.split("/")
        if len(parts) == 3 and parts[2] == "WORK_STATE.json":
            try:
                out[parts[1]] = json.loads(_git("show", ref + ":" + path))
            except ValueError as e:
                out[parts[1]] = {"_parse_error": str(e)}
    return out


def _age_hours(stamp, now):
    if not stamp:
        return None
    s = stamp.replace("Z", "+00:00")
    try:
        t = dt.datetime.fromisoformat(s)
    except ValueError:
        return None
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return (now - t).total_seconds() / 3600.0


def flags_for(ws, mwo, now, stale_hours):
    if "_parse_error" in ws:
        return ["PARSE_ERROR"]
    f = []
    if mwo and ws.get("mwo_id") != mwo:
        f.append("STALE_MWO({})".format(ws.get("mwo_id")))
    age = _age_hours(ws.get("updated_at_utc"), now)
    if age is None or age > stale_hours:
        f.append("STALE_UPDATE({})".format("?" if age is None else "{:.0f}h".format(age)))
    if not any(k in ws for k in ("current", "CURRENT")):
        f.append("NO_QUEUE")
    if ws.get("state") == "HOLD" and not ws.get("blocked_on") and not ws.get("operator_decisions_required"):
        f.append("IDLE_HOLD")
    return f


def fabric_view():
    try:
        tasks = json.loads(subprocess.run([sys.executable, "-m", "fabric", "tasks"], capture_output=True, text=True).stdout)
        agents = json.loads(subprocess.run([sys.executable, "-m", "fabric", "agents"], capture_output=True, text=True).stdout)
    except (ValueError, OSError):
        return {"status": "NOT_VERIFIED"}
    live = [t for t in tasks if t.get("state") not in ("completed", "failed", "cancelled")]
    online = sorted({a["agent"] for a in agents if a.get("status") == "online"})
    return {"status": "OK", "non_terminal_tasks": len(live), "online_workers": online,
            "idle_workers": bool(online) and not live}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--stale-hours", type=float, default=12.0)
    ap.add_argument("--no-db", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    now = dt.datetime.now(dt.timezone.utc)
    mwo = current_mwo(a.ref)
    rows = []
    for seat, ws in sorted(work_states(a.ref).items()):
        rows.append({"seat": seat, "state": ws.get("state"), "mwo": ws.get("mwo_id"),
                     "updated": ws.get("updated_at_utc"), "flags": flags_for(ws, mwo, now, a.stale_hours)})
    report = {"ref": a.ref, "current_mwo": mwo, "generated_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "seats": rows}
    if not a.no_db:
        report["fabric"] = fabric_view()
    if a.json:
        print(json.dumps(report, indent=1))
        return 0
    print("fleet status @ {} (current {}) {}".format(a.ref, mwo, report["generated_utc"]))
    for r in rows:
        print("  {:<12} {:<8} {:<9} {:<22} {}".format(r["seat"], str(r["state"]), str(r["mwo"]), str(r["updated"]),
                                                   " ".join(r["flags"]) or "ok"))
    fab = report.get("fabric")
    if fab:
        if fab["status"] != "OK":
            print("  fabric: NOT_VERIFIED")
        else:
            print("  fabric: {} non-terminal tasks; online workers {}{}".format(
                fab["non_terminal_tasks"], fab["online_workers"], "  IDLE_WORKERS" if fab["idle_workers"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
