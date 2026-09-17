"""G-R5-4 (round 5 P-BUILD, builder G): clause A eligibility on individual cells from G's R16 rows.

The R16 re-screen (operator 16, 32 runs over 4 RNG families, top1_train) was parked by operator 18 after one cell,
w13 train128_held64, was complete: floors (J1), baseline (J2) and the train128 input-invariant learner (J3).
worlds_r4/v2 must not be written from a partial screen, but the judge must be able to judge a candidate on that
cell alone. This module builds an IN-MEMORY worlds_r4/v2-shaped document restricted to complete cells, from the
committed rows only (never recomputed, never written):

    doc = r16_doc()                       # default: w13 train128_held64
    qd_ledger.check_r4("w13", "train128_held64", ..., doc=doc)
    w13_eligibility()                     # {eligible, verdict, floor, baseline, sample fields, sources}

Any cell not listed is absent from the document, so check() returns INELIGIBLE(UNSCREENED) for it.
"""
from __future__ import annotations

import subprocess

from primordial.metric import r16 as R
from primordial.metric import screen as SC
from primordial.metric import worlds as WR

W13 = (13, "train128_held64")
SCOPE = "R16 rows, partial screen (operator 18): listed cells only; NOT worlds_r4/v2"


def _rows_commit(paths) -> dict:
    out = {}
    for p in paths:
        q = subprocess.run(["git", "-C", str(R.ROOT), "log", "-1", "--format=%h", "--", str(p)],
                           capture_output=True, text=True)
        out[str(p)] = q.stdout.strip() or None
    return out


def r16_doc(cells=(W13,), floors=R.ROWS["floors"], baseline=R.ROWS["baseline"],
            learner128=R.ROWS["learner128"]) -> dict:
    """A worlds_r4/v2-shaped document holding only `cells`, each complete in the R16 rows: a floor_suite_r16 row,
    a baseline_r16 row and, where the floor would otherwise be a bound that can change a verdict, the train128
    learner. Refuses an incomplete cell, a PENDING verdict, or any entry below 32 runs x 4 families x 8."""
    want = {(int(g), p) for g, p in cells}
    recs = [c for c in R.assemble_v2(floors=floors, baseline=baseline, learner128=learner128)
            if (c["gen_seed"], c["pressure"]) in want]
    got = {(c["gen_seed"], c["pressure"]) for c in recs}
    if got != want:
        raise ValueError(f"cells without R16 floor rows: {sorted(want - got)}")
    for c in recs:
        if c["stage"] != 2:
            raise ValueError(f"w{c['gen_seed']} {c['pressure']}: no R16 baseline row (J2 did not reach it)")
        if c.get("pending"):
            raise ValueError(f"w{c['gen_seed']} {c['pressure']}: floor is a bound that can change a verdict ({c['pending']})")
    doc = WR.build(recs, commit="", max_survivors=None, schema=WR.SCHEMA_V2)
    bad = WR.v2_defects(doc)
    if bad:
        raise ValueError(f"BASELINE_N: {bad}")
    doc["scope"] = SCOPE
    doc["rows_commits"] = _rows_commit([floors, baseline, learner128])
    doc["commit"] = doc["rows_commits"].get(str(baseline)) or ""
    return doc


def eligibility(world: str, pressure: str, doc: dict | None = None) -> dict:
    """The cell's screen state under the document's active variant, as the judge will read it."""
    doc = doc if doc is not None else r16_doc()
    c = WR.lookup(doc, world, pressure)
    k = SC.vkey(doc["q1_floor_policy"], doc["q2_policy"])
    if c is None:
        return {"world": world, "pressure": pressure, "eligible": False, "verdict": "UNSCREENED", "variant": k,
                "scope": doc.get("scope")}
    v = c["verdicts"][k]
    b = c["baseline"] or {}
    return {"world": world, "pressure": pressure, "eligible": v["verdict"] == "SURVIVED", "verdict": v["verdict"],
            "cull_reason": v.get("cull_reason"), "variant": k, "floor": v["floor"], "floor_parts": c["floor_parts"],
            "gate_held64": c["gate_held64"],
            "baseline": {key: b.get(key) for key in ("median", "ci95", "bytes", "readout", "runs_total",
                                                    "rng_family_count", "runs_per_family", "n_runs", "families",
                                                    "n_per_family")},
            "progress_denominator": (b.get("median") - v["floor"]) if b.get("median") is not None else None,
            "scope": doc.get("scope"), "rows_commits": doc.get("rows_commits"), "sources": c.get("sources")}


def w13_eligibility() -> dict:
    return eligibility("w13", "train128_held64", r16_doc())
