"""POLY-05: the saturation curve of the May 2026 scour, from the archived event log.

Reads roles/Polyhymnia/ledgers/tensor_body_2026-09-11/events_2026-05-24_to_05-30.jsonl
(the byte-identical archive of agents/polyhymnia/events.jsonl) and writes
roles/Polyhymnia/ledgers/scour_saturation_2026-05.json plus a fixed-width table.

Per UTC day: ticks, integrating ticks, null ticks, new tesserae, merged
tesserae, approval requests. Then the day the last new tessera appeared and
the null-tick run length after it. No plotting; a table is the artifact.

Usage:  python roles/Polyhymnia/science/saturation_curve.py
"""
from __future__ import annotations

import collections
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGERS = HERE.parent / "ledgers"
SRC = LEDGERS / "tensor_body_2026-09-11" / "events_2026-05-24_to_05-30.jsonl"
OUT_JSON = LEDGERS / "scour_saturation_2026-05.json"
OUT_MD = LEDGERS / "scour_saturation_2026-05.md"
EXPECTED_SHA = "7ecceb3825861c0fe52030e42819099e62626beb6aed0542073b1710258d1f3f"


def main() -> int:
    raw = SRC.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != EXPECTED_SHA:
        print("REFUSING: archive sha256 {} != manifest {}".format(sha, EXPECTED_SHA))
        return 2
    days: dict = collections.defaultdict(lambda: collections.Counter())
    last_new_day = None
    ticks_after_last_new = 0
    tick_ends = 0
    for line in raw.splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        day = r["timestamp"][:10]
        ev = r.get("event")
        if ev == "tick_end":
            tick_ends += 1
            d = days[day]
            d["ticks"] += 1
            new = int(r.get("new_tesserae") or 0)
            d["new_tesserae"] += new
            d["merged_tesserae"] += int(r.get("merged_tesserae") or 0)
            d["candidates"] += int(r.get("candidates") or 0)
            if str(r.get("action", "")).endswith("_null"):
                d["null_ticks"] += 1
            elif str(r.get("action", "")).endswith("_integrated"):
                d["integrating_ticks"] += 1
            if new > 0:
                last_new_day = r["timestamp"]
                ticks_after_last_new = 0
            else:
                ticks_after_last_new += 1
        elif ev == "self_improvement_cycle" and r.get("action") == "approval_requested":
            days[day]["approval_requests"] += 1
    table = []
    cols = ["ticks", "integrating_ticks", "null_ticks", "candidates", "new_tesserae", "merged_tesserae", "approval_requests"]
    for day in sorted(days):
        row = {"day": day}
        row.update({c: int(days[day][c]) for c in cols})
        table.append(row)
    total = {c: sum(r[c] for r in table) for c in cols}
    out = {
        "source": str(SRC.relative_to(LEDGERS.parent.parent.parent)).replace("\\", "/"),
        "source_sha256": sha,
        "tick_end_events": tick_ends,
        "per_day": table,
        "total": total,
        "last_tick_with_new_tesserae_at": last_new_day,
        "null_run_after_last_new_tessera": ticks_after_last_new,
        "reading": "the single scour saturated; every tick after last_tick_with_new_tesserae_at was PRESENT and ACTIVE, not PRODUCTIVE (base rule 8)",
    }
    OUT_JSON.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    lines = ["# Scour saturation, May 2026 (POLY-05)", "",
             "Source: {} (sha256 {}...)".format(out["source"], sha[:16]),
             "tick_end events: {}".format(tick_ends), "",
             "day         ticks  integ  null  cand  new  merged  approvals",
             "----------  -----  -----  ----  ----  ---  ------  ---------"]
    for r in table:
        lines.append("{day}  {ticks:5d}  {integrating_ticks:5d}  {null_ticks:4d}  {candidates:4d}  {new_tesserae:3d}  {merged_tesserae:6d}  {approval_requests:9d}".format(**r))
    lines.append("{:10s}  {ticks:5d}  {integrating_ticks:5d}  {null_ticks:4d}  {candidates:4d}  {new_tesserae:3d}  {merged_tesserae:6d}  {approval_requests:9d}".format("TOTAL", **total))
    lines += ["", "last tick that added a tessera: {}".format(last_new_day),
              "null-tick run after it: {}".format(ticks_after_last_new), "", out["reading"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
