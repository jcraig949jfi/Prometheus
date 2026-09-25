"""B-R4-7: is B's w13 train128 clause A front readout-dependent? (A 1789449028866-0, D-R4-4 1789451426433-0)

The M2 baseline and every B candidate use the same readout: the top-16 elites by TRAIN fitness, per-seed mean on
HELD64. D-R4-4 re-read G's saved M2 archives: the w13 train128 baseline median is 182.72 (top-16) but 189.53
under top-1-by-TRAIN, so the progress denominator moves from 16.25 to 23.06 over the gate_in|HOLD floor 166.47.
A top-1 baseline against top-16 candidates would mix readouts. This re-reads B's own SAVED elites under both
readouts, so progress is computed readout-for-readout. Scoring only: no QD, no new genomes.

Per (source exp, rung, run seed) row: top16 (must reproduce the committed held64_per_seed exactly -- the
self-check), top1 (the single best elite by (-train fitness, genome bytes), per-seed mean on HELD64). Summary per
(rung, seed set): medians, and progress under each readout against D-R4-4's baseline median for that readout.
Validation-selected readouts are not computed: B's runs trained on all of TRAIN128 with no held-back split.

    python -m primordial.fabric.worker submit B primordial.cohorts.b.r4_7_readout:job --exp B-R4-7-readout-w13-train128 \\
        --rows primordial/ledger/rows/B/B-R4-7-readout-w13-train128.jsonl --ttl-cpu-s 600 --kwargs '{}'
"""
from __future__ import annotations

import json

import numpy as np

from primordial.cohorts.b.b1_qlinear import QLin
from primordial.cohorts.b.r4_1_qladder import ROOT, score
from primordial.metric import floors as F
from primordial.qd.archive import load_elites

FLOOR = 166.46875
BASELINE = {"top16": 182.71875, "top1": 189.53}          # D-R4-4 (1789451426433-0): m2 / top1 medians
SOURCES = (("B-R4-4-int5-codebook-w13-train128", "int4_a4"), ("B-R4-5-a4-replicate-w13-train128", "int4_a4"),
           ("B-R4-2-qladder-hi-w13-train128", "int5_a8"), ("B-R4-3-int5-replicate-w13-train128", "int5_a8"),
           ("B-R4-4-int5-codebook-w13-train128", "int5_a4"), ("B-R4-5-a4-replicate-w13-train128", "int5_a4"),
           ("B-R4-1-qladder-w13-train128", "int4_a8"), ("B-R4-3-int5-replicate-w13-train128", "int4_a8"))


def _runs(exp: str, rung: str) -> list[dict]:
    p = ROOT / "primordial" / "ledger" / "rows" / "B" / f"{exp}.jsonl"
    rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    return sorted((r for r in rows if r.get("kind") == "run" and r.get("rung") == rung), key=lambda r: r["run_seed"])


def readouts(q: QLin, elites_path: str) -> dict:
    doc = load_elites(elites_path)
    el = sorted(((e[1], bytes.fromhex(e[2])) for e in doc["elites"]), key=lambda v: (-v[0], v[1]))
    raw = lambda n: np.frombuffer(b"".join(g for _, g in el[:n]), np.uint8).reshape(-1, q.glen)
    return {"top16": score(q, raw(16), F.HELD64), "top1": score(q, raw(1), F.HELD64), "n_elites": len(el)}


def job(ctx, sources=SOURCES):
    acc: dict = {}
    for exp, rung in sources:
        runs = _runs(exp, rung)
        bits, acts = int(runs[0]["bits"]), int(runs[0]["acts"])
        q = QLin(13, bits, acts)
        for r in runs:
            ro = readouts(q, r["elites"])
            row = {"kind": "readout", "status": "control", "source_exp": exp, "rung": rung, "run_seed": r["run_seed"],
                   "genome_bytes": q.glen, "committed_held64": r["held64_per_seed"], **ro,
                   "reproduces_committed": bool(ro["top16"] == r["held64_per_seed"])}
            ctx.emit(row)
            acc.setdefault((rung, exp), []).append(row)
    for (rung, exp), rows in acc.items():
        med = {k: float(np.median([x[k] for x in rows])) for k in ("top16", "top1")}
        prog = {k: (med[k] - FLOOR) / (BASELINE[k] - FLOOR) for k in med}
        ctx.emit({"kind": "readout_summary", "status": "control", "rung": rung, "source_exp": exp,
                  "seeds": [x["run_seed"] for x in rows], "genome_bytes": rows[0]["genome_bytes"], "median": med,
                  "progress_same_readout": prog, "baseline_medians_d_r4_4": BASELINE, "floor": FLOOR,
                  "all_reproduce_committed": all(x["reproduces_committed"] for x in rows),
                  "pass_same_readout": {k: bool(v >= 0.95) for k, v in prog.items()}})
