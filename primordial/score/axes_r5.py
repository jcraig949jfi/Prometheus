"""H-R5-3 (round 5 P-BUILD, builder H): F12 PROGRESS AXES by rule (prompt 19 s12, SWARM_R5 O8).

Scientific result and institutional value stay separate. These axes are computed from receipt TYPE and LINEAGE
only; no receipt field that states its own points is read, and no prose is read.

  error_metabolism     +1 per distinct exp_id of ANOTHER lane named in `refutes` (identifier match) by a
                       board-eligible PASS or KILL receipt. Credited to the lane that FILED the refutation,
                       earliest filer first; never to the claim's originator (O8). Refuting a claim of one's own
                       lane scores 0 (reported under own_refutations_unscored, 19 s12 last line).
  instrument_gain      +1 per PASS receipt whose experiment_class (F-R5-1 envelope, or top level) is an instrument
                       class AND whose `regression_test` names a committed test file under primordial/ that exists
                       (FIXED_WITH_REGRESSION): a tooling repair with its regression test.
  boundary_resolution  +1 per scientific FAIL or KILL receipt with committed rows AND science.boundary =
                       {parameter, below: {value, verdict}, above: {value, verdict}} where below.value < above.value
                       and the two verdicts differ: the FAIL located a regime boundary in a named parameter.

    from primordial.score.axes_r5 import axes; axes(receipts)
"""
from __future__ import annotations

import pathlib
import re

from primordial.core.contract import board_eligible
from primordial.score.round2 import ROOT

AXES = ("boundary_resolution", "instrument_gain", "error_metabolism")
INSTRUMENT_CLASSES = ("instrument", "tooling")
SCIENTIFIC_FAILS = ("FAIL", "KILL")
REFUTING = ("PASS", "KILL")
TEST_RE = re.compile(r"primordial/[\w./-]*test_[\w-]+\.py")
ROWS_RE = re.compile(r"primordial/[\w./-]+\.jsonl?")


def experiment_class(rec: dict) -> str | None:
    return (rec.get("envelope") or {}).get("experiment_class") or rec.get("experiment_class")


def refuted_targets(rec: dict, exp_lane: dict[str, str]) -> list[str]:
    from primordial.score.progress import refuted_targets as rt      # F12's identifier-only matcher
    return rt(rec, exp_lane)


def _num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def boundary_ok(b) -> bool:
    if not isinstance(b, dict) or not str(b.get("parameter") or "").strip():
        return False
    lo, hi = b.get("below"), b.get("above")
    if not isinstance(lo, dict) or not isinstance(hi, dict):
        return False
    if not (_num(lo.get("value")) and _num(hi.get("value")) and lo["value"] < hi["value"]):
        return False
    return bool(lo.get("verdict")) and bool(hi.get("verdict")) and lo["verdict"] != hi["verdict"]


def axes(receipts: list[dict], root=ROOT, lanes=None) -> dict:
    root = pathlib.Path(root)
    exp_lane = {r["exp_id"]: r["lane"] for r in receipts}
    lanes = list(lanes or sorted({r["lane"] for r in receipts}))
    out = {lane: {**{a: 0 for a in AXES},
                  "detail": {**{a: [] for a in AXES}, "own_refutations_unscored": []}} for lane in lanes}
    credited: set[str] = set()
    for r in sorted(receipts, key=lambda x: (float(x.get("ts") or 0), x["exp_id"])):
        lane = r["lane"]
        if lane not in out:
            continue
        d = out[lane]["detail"]
        targets = refuted_targets(r, exp_lane)
        own = [t for t in targets if exp_lane[t] == lane]
        other = [t for t in targets if exp_lane[t] != lane]
        if own:
            d["own_refutations_unscored"].append({"exp_id": r["exp_id"], "refutes": own})
        if other and r.get("status") in REFUTING and board_eligible(r):
            new = [t for t in other if t not in credited]
            credited.update(new)
            if new:
                out[lane]["error_metabolism"] += len(new)
                d["error_metabolism"].append({"exp_id": r["exp_id"], "refutes": new,
                                              "originators": sorted({exp_lane[t] for t in new})})
        if r.get("status") == "PASS" and experiment_class(r) in INSTRUMENT_CLASSES:
            tests = [p for p in TEST_RE.findall(str(r.get("regression_test") or "")) if (root / p).exists()]
            if tests:
                out[lane]["instrument_gain"] += 1
                d["instrument_gain"].append({"exp_id": r["exp_id"], "regression_test": tests})
        b = (r.get("science") or {}).get("boundary")
        rows = [p for p in ROWS_RE.findall(str(r.get("rows") or "")) if (root / p).exists()]
        if r.get("status") in SCIENTIFIC_FAILS and rows and boundary_ok(b):
            out[lane]["boundary_resolution"] += 1
            d["boundary_resolution"].append({"exp_id": r["exp_id"], "parameter": b["parameter"]})
    return out
