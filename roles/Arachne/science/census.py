"""ARACHNE-02: the landscape census. For each of the six adapters: does it
answer, why not if not, which credential source resolved, how many rows or
files sit behind it, and how the June run's landscape set compares.

NO expand() call, NO edge, NO write to any fabric: the census reads
availability and counts only (operator ruling 2026-09-11 s1). Writes
roles/Arachne/ledgers/landscape_census_<date>.json with the workspace
receipt. Run from a linked worktree (D-23).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from archaeon.workspace import assert_not_canonical      # noqa: E402
from agents.arachne.landscapes import build_landscapes_report, _pg   # noqa: E402

JUNE_AVAILABLE = ["mathlib", "lmfdb", "algolib", "oeis", "knots", "groups"]
COUNTS = {
    "lmfdb": ("lmfdb", "SELECT count(*) FROM ec_curvedata"),
    "oeis": ("prometheus_sci", "SELECT count(*) FROM analysis.oeis"),
    "knots": ("prometheus_sci", "SELECT count(*) FROM topology.knots"),
    "groups": ("prometheus_sci", "SELECT count(*) FROM algebra.groups"),
}


def _count(db: str, sql: str):
    conn = _pg.connect(db)
    if conn is None:
        return None, _pg.LAST_ERROR.get(db)
    try:
        cur = conn.cursor(); cur.execute(sql); n = cur.fetchone()[0]; cur.close(); conn.close()
        return int(n), "ok"
    except Exception as e:  # noqa: BLE001
        return None, "{}: {}".format(type(e).__name__, str(e).strip().splitlines()[0][:200])


def run() -> dict:
    ws = assert_not_canonical("run the Arachne landscape census", allow_override=False)
    rep = build_landscapes_report()
    out = {}
    for name, row in rep.items():
        inst = row.pop("_inst")
        entry = dict(row)
        entry["in_june_run"] = name in JUNE_AVAILABLE
        if name in COUNTS:
            db, sql = COUNTS[name]
            n, why = _count(db, sql)
            entry["rows"] = n; entry["count_status"] = why; entry["database"] = db
        elif name == "mathlib":
            entry["files"] = len(getattr(inst, "_files", []) or []) if inst is not None else 0
            entry["root_tried"] = str(getattr(sys.modules.get("agents.arachne.landscapes.mathlib"), "_ROOT", "?"))
        elif name == "algolib":
            entry["callables"] = len(getattr(inst, "_obj", {}) or {}) if inst is not None else 0
        out[name] = entry
    census = {
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "workspace": ws,
        "credential_resolution": dict(_pg.RESOLUTION),
        "landscapes": out,
        "available_now": sorted(k for k, v in out.items() if v["available"]),
        "available_june": JUNE_AVAILABLE,
        "lost_since_june": sorted(k for k in JUNE_AVAILABLE if not out.get(k, {}).get("available")),
        "expand_called": False,
        "edges_written": 0,
    }
    return census


def main() -> int:
    c = run()
    date = c["computed_at"][:10]
    path = REPO / "roles" / "Arachne" / "ledgers" / "landscape_census_{}.json".format(date)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(c, indent=2, default=str), encoding="utf-8")
    for name, e in c["landscapes"].items():
        extra = e.get("rows", e.get("files", e.get("callables")))
        print("{:8s} available={!s:5s} reason={} | size={} | creds={}".format(
            name, e["available"], e["reason"], extra, e.get("credential_source")))
    print("lost since June:", c["lost_since_june"], "->", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
