"""D-R7-11 (A 1789520995354-0, narrowed in D 1789521363649-0): the third passing cell, C-R7-AP-03 (small_program /
signal_world_d1 / byte_charge / falkordb_cypher / metered_stream, receipt 1789520952417-0), measured on the ONE axis
that makes the three cells comparable -- did the pressure press on the readout's own winner?

Scope, cut deliberately so D does not re-derive what C published:
  ALREADY ANSWERED BY C, not remeasured here. C's receipt reports the cell is VACUOUS by construction: all 64 runs in
  both arms returned exactly 31.71875 held charge per episode with IQR 0.0 on both sides, because at 3-bit symbols a
  delivered send costs alpha_int * 3 = 6 while a right action earns y_int = 3, so signalling never pays on d1 and every
  winner settles on the silent constant-action attractor. C also reports the charge DID shrink programs: cell top1
  functional bytes median 14 (non-nop 3) against control 22 (non-nop 7).
  DEGENERATE HERE, so not run. D-R7-7's paired train-vs-held instrument cannot discriminate on this cell: with every
  held value identical and IQR 0.0, h is 0 by construction and t carries no information.
  WHAT THIS ADDS. D-R7-6's quantity, unchanged, so that AP-01, AP-02 and AP-03 carry ONE comparable number:
  charge_share, the charge the winner actually paid as a share of what it earned, paired cell-vs-control on the same
  (family, run seed).

Zero QD: C's committed rows only (primordial/ledger/rows/C/C-R7-AP-03-small-program-d1-bytecharge-falkordb-metered.jsonl,
read from origin), 32 pairs, families 4200 / 2101 / 3303 / 5501 x run seeds 0..7.

Arithmetic, stated because it differs from AP-02's row shape. C's selection fitness is SCALE * TRAIN charge sum -
BETA * functional bytes, so the cell arm's `train_fit_top1` is NET of the charge while the control's carries no charge.
The winner therefore earned gross = train_fit_top1 + beta * top1_functional_bytes in the cell arm, and
    charge_share = beta * top1_functional_bytes / (train_fit_top1 + beta * top1_functional_bytes).
For the control arm the same expression is reported with beta = 0 by definition (it pays nothing).

Rule (fixed before any value is read), identical to D-R7-6's so the cells are comparable:
  s     = median over the 32 cell runs of charge_share
  small = #pairs where the cell winner's functional bytes are fewer than the control winner's
  same  = #pairs where they are equal
  PRESSURE_DID_NOT_BIND  s <= 0.01 and same >= 24
  PRESSURE_BOUND         s >= 0.05 and small >= 24
  MIXED                  otherwise
  INDETERMINATE if I1 or a planted control fails.
I1: 32 cell and 32 control runs, 8 per family, identical (family, run seed) key sets; beta equal to the reference row's
beta in every run; every run's oracles.ok true; the recomputed held median equals C's summary held_median_cell to 0.01.
Planted controls (binding), exactly D-R7-6's: planted_bound must read PRESSURE_BOUND and planted_free must read
PRESSURE_DID_NOT_BIND.
Reported, not judged: functional bytes and non-nop counts per arm; held_charge_per_episode and its IQR (C's vacuity,
reproduced as a number, not re-argued); held_unaffordable_per_episode; train_fit_top1 per arm; and the cross-cell table
carrying AP-01's mechanism (saturation), AP-02's measured charge_share, and this cell's.

    worker.submit("D", "primordial.cohorts.d.r7_11_ap03_pressure_binding:job", EXP, ROWS, 300, envelope={...})
"""
from __future__ import annotations

import hashlib
import json
import time

import numpy as np

from primordial.cohorts.d import r7_6_ap02_pressure_binding as B6

EXP = "D-R7-11-ap03-pressure-binding"
PREDICATE_ID = EXP
ANOMALY = "1789517546515-0"
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
SRC_ROWS = "primordial/ledger/rows/C/C-R7-AP-03-small-program-d1-bytecharge-falkordb-metered.jsonl"
FAMILIES = B6.FAMILIES
CROSS_CELL = {
    "C-R6-AP-01": {"cell": "tucker / nk_stub / cpu_ttl / graphblas", "mechanism": "SATURATED",
                   "d_receipt": "1789511852981-0",
                   "note": "held-out NK plateaus by ~80-100 generations, so a 1/5-CPU cut reaches parity"},
    "C-R7-AP-02": {"cell": "codebook / nk_stub / byte_charge / falkordb_cypher / metered_stream", "decision": "MIXED",
                   "d_receipt": "1789517835009-0", "median_charge_share": 0.0365,
                   "note": "charge materially paid and winner smaller in 22/32, but the meter never bound"},
    "C-R7-AP-03": {"cell": "small_program / signal_world_d1 / byte_charge / falkordb_cypher / metered_stream",
                   "c_receipt": "1789520952417-0", "measured_here": True}}


def load(text: str):
    rows = [json.loads(l) for l in text.splitlines() if l.strip()]
    runs = {(x["arm"], int(x["family"]), int(x["run_seed"])): x for x in rows
            if x.get("kind") == "run" and x.get("arm") in ("cell", "control")}
    ref = next((x for x in rows if x.get("kind") == "reference"), {})
    summ = [x for x in rows if x.get("kind") == "summary"]
    return runs, ref, (summ[-1] if summ else {})


def fb(row: dict) -> int:
    return int(row["top1_functional_bytes"])


def charge_share(row: dict, beta: float) -> float:
    """The charge the winner paid as a share of what it earned; train_fit_top1 is NET of the charge in the cell arm."""
    paid = float(beta) * fb(row)
    gross = float(row["train_fit_top1"]) + paid
    return paid / gross if gross else float("nan")


def counts(pp) -> tuple[int, int]:
    small = int(sum(fb(c) < fb(k) for c, k in pp))
    same = int(sum(fb(c) == fb(k) for c, k in pp))
    return small, same


def job(ctx, status: str = "record", exp: str = EXP, predicate_id: str = PREDICATE_ID):
    t0 = time.perf_counter()
    text, provenance = B6.source_text(SRC_ROWS)
    runs, ref, summ = load(text)
    pp = B6.pairs_of(runs)
    beta = float(ref.get("beta", summ.get("beta", 0)))
    per_fam = {str(f): sum(int(c["family"]) == f for c, _ in pp) for f in FAMILIES}
    shares = [charge_share(c, beta) for c, _ in pp]
    s = float(np.median(shares)) if shares else float("nan")
    small, same = counts(pp)
    cell_h = [float(c["held_charge_per_episode"]) for c, _ in pp]
    ctrl_h = [float(k["held_charge_per_episode"]) for _, k in pp]
    i1 = {"pairs_32": len(pp) == 32, "per_family_8": all(v == 8 for v in per_fam.values()),
          "beta_consistent": all(float(x["beta"]) == beta for x, _ in pp) and beta > 0,
          "oracles_ok": all((x.get("oracles") or {}).get("ok", True) for pair in pp for x in pair),
          "median_cell_matches_summary": abs(float(np.median(cell_h)) - float(summ.get("held_median_cell", np.nan))) < 0.01}
    bound = B6.decide(True, True, 0.10, B6.AGREE_PAIRS, 0)
    free = B6.decide(True, True, 0.001, 0, B6.AGREE_PAIRS)
    controls = {"planted_bound": {"reads": bound, "ok": bound == "PRESSURE_BOUND"},
                "planted_free": {"reads": free, "ok": free == "PRESSURE_DID_NOT_BIND"}}
    ok = all(c["ok"] for c in controls.values())
    decision = B6.decide(all(i1.values()), ok, s, small, same)
    d = lambda xs: {"median": float(np.median(xs)), "min": float(min(xs)), "max": float(max(xs)),
                    "iqr": float(np.percentile(xs, 75) - np.percentile(xs, 25))}
    cross = dict(CROSS_CELL)
    cross["C-R7-AP-03"] = dict(cross["C-R7-AP-03"], decision=decision, median_charge_share=s)
    ctx.emit({"kind": "summary", "exp": exp, "predicate_id": predicate_id, "anomaly": ANOMALY, "status": status,
              "evidence_class": "VERDICT", "ts": round(time.time(), 3), "qd_runs": 0,
              "source_rows": SRC_ROWS, "source_provenance": provenance,
              "source_rows_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
              "runs_total": len(pp), "rng_family_count": len([f for f in per_fam if per_fam[f]]), "runs_per_family": 8,
              "families": list(FAMILIES), "n_per_family": per_fam, "beta": beta,
              "checks": {"I1": i1, "controls_ok": ok}, "controls": controls,
              "median_charge_share": s, "pairs_cell_winner_smaller": small, "pairs_equal_functional_bytes": same,
              "decision": decision,
              "reported_not_judged": {
                  "charge_share": d(shares),
                  "functional_bytes_cell": d([fb(c) for c, _ in pp]),
                  "functional_bytes_control": d([fb(k) for _, k in pp]),
                  "nonnop_cell": d([int(c["top1_nonnop"]) for c, _ in pp]),
                  "nonnop_control": d([int(k["top1_nonnop"]) for _, k in pp]),
                  "held_charge_cell": d(cell_h), "held_charge_control": d(ctrl_h),
                  "held_unaffordable_cell": d([float(c["held_unaffordable_per_episode"]) for c, _ in pp]),
                  "train_fit_cell": d([float(c["train_fit_top1"]) for c, _ in pp]),
                  "train_fit_control": d([float(k["train_fit_top1"]) for _, k in pp]),
                  "vacuity_note": ("C's own finding, reproduced here as numbers rather than re-argued: the held "
                                   "readout is identical across both arms (IQR 0.0), so the primary could not have "
                                   "come out any other way and carries no evidence about byte_charge"),
                  "cross_cell": cross},
              "wall_s": round(time.perf_counter() - t0, 3)})
