"""The scorer as a program (backlog F12): a progress VECTOR per cohort, computed from rows and
receipts only. No single master score, no manual path, no prose read.

Axes (a round is a ts window over receipts, rows and anomaly records):

  compression          clause A cells that PASS against the baseline front AND read PASS against
                       the trivial-policy floor (qd_ledger.check()['floor']['verdict'], builder G's
                       M1). BELOW_FLOOR, NO_HEADROOM and NO_FLOOR score nothing (conductor
                       1789426590314-0). Superseded rows are dropped; the superseding row counts.
  landscape            distinct QD cells (world, pressure, representation, substrate, channel)
                       the cohort evaluated, at any status
  failure_landscape    committed rows with status dev / aborted / timeout / cheat (kept, not filtered)
  anomalies_filed      ANOMALY records the cohort filed
  anomalies_resolved   RESOLVED / REFUTED events whose exp_id has a committed rows file
  refutations          board-eligible receipts whose `refutes` names ANOTHER lane's exp_id
  kills_own            KILL receipts that refute no other lane: reported, never scored
  corrections          QD rows that supersede an earlier row + receipts refuting the cohort's own
                       earlier result (detect -> disclose -> repair, lineage kept)
  instruments          PASS receipts whose rows hold both cheat and control rows (a validated
                       instrument: planted positive and cheat run by the same harness)
  transfer             clause B: NOT_OPEN until S1 (check-b) lands; 0

The prior-vs-reality ledger (F10) and the budget (F13) are reported elsewhere and never enter
the vector.

    python -m primordial.score.progress [--write]
"""
from __future__ import annotations

import argparse
import glob
import json
import pathlib
import re

from primordial.core.contract import board_eligible
from primordial.score.round2 import DATE, EXPORT, ROOT, ROUND2_START, jsonl

COHORTS = ("B", "C", "D", "E")
FAILURE_STATUSES = ("dev", "aborted", "timeout", "cheat")
RESOLVED = ("RESOLVED", "REFUTED")
OUT = ROOT / "primordial" / "ledger" / "rows" / "H" / "F12-progress-vector-r2.jsonl"
AXES = ("compression", "landscape", "failure_landscape", "anomalies_filed", "anomalies_resolved",
        "refutations", "kills_own", "corrections", "instruments", "transfer")
SCORED = tuple(a for a in AXES if a != "kills_own")


def _ts(x) -> float | None:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _in(x, window) -> bool:
    t = _ts(x)
    return t is not None and window[0] <= t < window[1]


def _cell(r) -> tuple:
    c = r["cell"]
    return tuple(c.get(k) for k in ("world", "pressure", "representation", "substrate", "channel"))


def rows_of(root, lane: str, window) -> list[dict]:
    """Committed JSONL rows of a lane inside the window; unparseable lines are skipped (counted by caller)."""
    out = []
    for f in sorted(glob.glob(str(pathlib.Path(root) / "primordial" / "ledger" / "rows" / lane / "*.jsonl"))):
        for line in pathlib.Path(f).read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if isinstance(r, dict) and _in(r.get("ts"), window):
                out.append(dict(r, _file=pathlib.Path(f).name))
    return out


def compression(qd: list[dict], lane: str, window) -> dict:
    from primordial.ops import qd_ledger as Q
    mine = [r for r in qd if r.get("cohort") == lane and not r.get("baseline") and not r.get("floor")
            and _in(r.get("ts"), window)]
    superseded = {(r["supersedes"]["exp_id"], _cell(r)) for r in mine if isinstance(r.get("supersedes"), dict)}
    by_floor: dict[str, int] = {}
    raw_pass, scored = 0, []
    for r in mine:
        f = r.get("fitness") or {}
        if r.get("status") != "record" or f.get("held64_median") is None or (r.get("exp_id"), _cell(r)) in superseded:
            continue
        c = r["cell"]
        res = Q.check(qd, c["world"], c["pressure"], f["held64_median"], f.get("iqr") or 0.0,
                      int(r["footprint"]["genome_bytes"]), int(f.get("n_runs") or 0))
        fv = (res.get("floor") or {}).get("verdict", "NO_FLOOR")
        by_floor[fv] = by_floor.get(fv, 0) + 1
        if res["verdict"] == "PASS":
            raw_pass += 1
            if fv == "PASS":
                scored.append({"exp_id": r.get("exp_id"), "cell": list(_cell(r)),
                               "genome_bytes": r["footprint"]["genome_bytes"]})
    return {"value": len(scored), "raw_pass": raw_pass, "floor_verdicts": by_floor, "scored": scored,
            "superseded_dropped": len(superseded)}


def _exp_lane(results: list[dict]) -> dict[str, str]:
    return {r["exp_id"]: r["lane"] for r in results}


def refuted_targets(rec: dict, exp_lane: dict[str, str]) -> list[str]:
    """exp_ids named in `refutes` (identifier match only; the surrounding text is ignored)."""
    ref = rec.get("refutes")
    text = " ".join(map(str, ref)) if isinstance(ref, list) else str(ref or "")
    names = set(re.findall(r"[A-Za-z0-9][\w.-]*", text))
    return sorted(n for n in names if n in exp_lane and n != rec["exp_id"])


def vector(export=EXPORT, root=ROOT, window=(ROUND2_START, float("inf")), cohorts=COHORTS) -> dict:
    export, root = pathlib.Path(export), pathlib.Path(root)
    results = jsonl(export / f"pm_results_{DATE}.jsonl")
    anomalies = jsonl(export / f"pm_anomalies_{DATE}.jsonl")
    qd = jsonl(root / "primordial" / "ledger" / "qd" / "cells.jsonl")
    exp_lane = _exp_lane(results)
    out = {}
    for lane in cohorts:
        recs = [r for r in results if r["lane"] == lane and _in(r["ts"], window)]
        rows = rows_of(root, lane, window)
        comp = compression(qd, lane, window)
        cells = {_cell(r) for r in qd if r.get("cohort") == lane and not r.get("baseline") and not r.get("floor")
                 and _in(r.get("ts"), window)}
        failures = [r for r in rows if r.get("status") in FAILURE_STATUSES]
        filed = [a for a in anomalies if not a.get("event") and a["lane"] == lane and _in(a["ts"], window)]
        events = [a for a in anomalies if a.get("event") and a["lane"] == lane and _in(a["ts"], window)
                  and a.get("status") in RESOLVED]
        backed = [a for a in events
                  if (root / "primordial" / "ledger" / "rows" / lane / f"{a.get('exp_id')}.jsonl").exists()]
        refutations, corrections_r, kills_own = [], [], []
        for r in recs:
            targets = refuted_targets(r, exp_lane)
            other = [t for t in targets if exp_lane[t] != lane]
            own = [t for t in targets if exp_lane[t] == lane]
            if other and board_eligible(r):
                refutations.append({"exp_id": r["exp_id"], "refutes": other})
            if own:
                corrections_r.append({"exp_id": r["exp_id"], "corrects": own})
            if r["status"] == "KILL" and not other:
                kills_own.append(r["exp_id"])
        corrections_q = [r["exp_id"] for r in qd if r.get("cohort") == lane and isinstance(r.get("supersedes"), dict)
                         and _in(r.get("ts"), window)]
        instruments = []
        for r in recs:
            if r["status"] != "PASS":
                continue
            paths = set(re.findall(r"primordial/ledger/rows/[\w./-]+\.jsonl", str(r.get("rows", ""))))
            st = set()
            for p in paths:
                if (root / p).exists():
                    for line in (root / p).read_text(encoding="utf-8").splitlines():
                        try:
                            st.add(json.loads(line).get("status"))
                        except (ValueError, AttributeError):
                            continue
            if {"cheat", "control"} <= st:
                instruments.append(r["exp_id"])
        axes = {"compression": comp["value"], "landscape": len(cells), "failure_landscape": len(failures),
                "anomalies_filed": len(filed), "anomalies_resolved": len(backed), "refutations": len(refutations),
                "kills_own": len(kills_own), "corrections": len(corrections_r) + len(corrections_q),
                "instruments": len(instruments), "transfer": 0}
        out[lane] = {"cohort": lane, "axes": axes, "detail": {
            "receipts": len(recs), "rows": len(rows), "compression": comp,
            "anomalies_resolved_unbacked": [a["id"] for a in events if a not in backed],
            "refutations": refutations, "kills_own": kills_own,
            "corrections": {"receipts": corrections_r, "superseding_rows": corrections_q},
            "instruments": instruments, "transfer": "NOT_OPEN"}}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", default=str(EXPORT))
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    v = vector(a.export)
    print("cohort " + " ".join(f"{x[:11]:>11s}" for x in AXES))
    for lane, d in v.items():
        print(f"{lane:6s} " + " ".join(f"{d['axes'][x]:11d}" for x in AXES))
    for lane, d in v.items():
        c = d["detail"]["compression"]
        print(f"{lane} compression raw_pass={c['raw_pass']} floor={c['floor_verdicts']} scored={c['value']}")
    if a.write:
        if OUT.exists():
            print(f"{OUT.relative_to(ROOT).as_posix()} exists; rows are append-only, not rewritten")
            return 1
        from primordial.fabric.rows import RowWriter
        with RowWriter(OUT, "F12-progress-vector-r2", commit_every_s=10**9) as w:
            for d in v.values():
                w.write({"kind": "progress_vector", "status": "record", "window": [ROUND2_START, None], **d})
        print(f"wrote {OUT.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
