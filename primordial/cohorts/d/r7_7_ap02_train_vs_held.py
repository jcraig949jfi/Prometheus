"""D-R7-7 (ANOM-1789517546515-0, still OPEN after D-R7-6 returned MIXED): C-R7-AP-02's byte_charge PARTIALLY bound --
it is materially paid (median 3.65% of what the winner earned) and it shrinks the winner in 22 of 32 paired streams --
yet the charged cell still reached held-out parity (held median 2116036.84 vs control 2116423.73, bar 2102284.02;
receipt 1789517835009-0). The unanswered half: does the charge cost TRAIN fitness that never transferred to held-out?

This is D-R6-8's instrument (receipt 1789490865360-0) pointed at a second cell, deliberately unchanged so both cells
are read on one axis. On C-R6-AP-01 (tucker / nk_stub / cpu_ttl / graphblas) it returned MIXED at t = 32, h = 17, and
D-R7-1 then showed that cell's parity came from search saturation.

Zero QD: C's committed rows only (primordial/ledger/rows/C/C-R7-AP-02-codebook-nk-bytecharge-falkordb-metered.jsonl,
read from origin), cell and control paired on the same (family, run seed) -- same GA and sampler streams -- 32 pairs,
families 4200 / 2101 / 3303 / 5501 x run seeds 0..7. Fields: train_nk_per_landscape_top1, held_per_landscape_top1,
beta, top1_program.functional_bytes, held_minus_random.

Rule (fixed before reading; pairs p = 1..32, exactly D-R6-8's thresholds):
  t = #pairs with control train > cell train;  h = #pairs with control held > cell held
  TRAIN_NOT_HELD  t >= 26 and h <= 16   (the charge costs train fitness that does not transfer to held-out)
  BOTH_LOSE       t >= 26 and h >= 26   (it costs both: parity is a bar artifact, not transfer)
  NO_TRAIN_COST   t <= 16               (the charged winner is not even worse on train)
  MIXED           otherwise
  INDETERMINATE if I1 or the binding control fails.
I1: 32 pairs, 8 per family, beta equal to the summary's beta in every run, and the recomputed held medians equal C's
summary held_median_cell / held_median_control to 0.01.
Controls: self_pair (binding: control against itself gives t = 0, h = 0); shuffled_pairing (reported, not binding:
cell runs rotated within family, to show whether t and h depend on the same-stream pairing).
Reported, not judged: median paired train and held differences; Spearman of charge_share against the held difference
(does paying more cost more held-out?); per-family t and h; D-R6-8's own counts on the round 6 cell for comparison.

Predicate hygiene (A 1789517887578-0): this text is posted to ALL, so it names only the CELL and the MECHANISM. Cell
routing metadata is conductor-only while the round is live and appears nowhere in this module, its rows or its receipt.

    worker.submit("D", "primordial.cohorts.d.r7_7_ap02_train_vs_held:job", EXP, ROWS, 300, envelope={...})
"""
from __future__ import annotations

import hashlib
import json
import time

import numpy as np

from primordial.cohorts.d import r7_6_ap02_pressure_binding as B6

EXP = "D-R7-7-ap02-train-vs-held"
PREDICATE_ID = EXP
ANOMALY = "1789517546515-0"
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
SRC_ROWS = B6.SRC_ROWS
FAMILIES = B6.FAMILIES
TRAIN_HI, HELD_LO = 26, 16
R6 = {"exp": "C-R6-AP-01", "cell": "tucker / nk_stub / cpu_ttl / graphblas", "d_receipt": "1789490865360-0",
      "t": 32, "h": 17, "decision": "MIXED",
      "mechanism_found_later": "SATURATED (D-R7-1, receipt 1789511852981-0): held-out NK plateaus by ~80-100 generations"}


def counts(pp) -> tuple[int, int]:
    t = int(sum(float(k["train_nk_per_landscape_top1"]) > float(c["train_nk_per_landscape_top1"]) for c, k in pp))
    h = int(sum(float(k["held_per_landscape_top1"]) > float(c["held_per_landscape_top1"]) for c, k in pp))
    return t, h


def decide(i1: bool, controls_ok: bool, t: int, h: int) -> str:
    if not (i1 and controls_ok):
        return "INDETERMINATE"
    if t <= HELD_LO:
        return "NO_TRAIN_COST"
    if t >= TRAIN_HI and h <= HELD_LO:
        return "TRAIN_NOT_HELD"
    if t >= TRAIN_HI and h >= TRAIN_HI:
        return "BOTH_LOSE"
    return "MIXED"


def spearman(a, b) -> float:
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1]) if len(a) > 2 else float("nan")


def job(ctx, status: str = "record", exp: str = EXP, predicate_id: str = PREDICATE_ID):
    t0 = time.perf_counter()
    text, provenance = B6.source_text()
    runs, summ = B6.load(text)
    pp = B6.pairs_of(runs)
    per_fam = {str(f): sum(int(c["family"]) == f for c, _ in pp) for f in FAMILIES}
    cell_h = [float(c["held_per_landscape_top1"]) for c, _ in pp]
    ctrl_h = [float(k["held_per_landscape_top1"]) for _, k in pp]
    beta = summ.get("beta")
    i1 = {"pairs_32": len(pp) == 32, "per_family_8": all(v == 8 for v in per_fam.values()),
          "beta_consistent": all(float(x["beta"]) == float(beta) for x, _ in pp) if beta is not None else False,
          "median_cell_matches_summary": abs(float(np.median(cell_h)) - float(summ.get("held_median_cell", np.nan))) < 0.01,
          "median_control_matches_summary": abs(float(np.median(ctrl_h)) - float(summ.get("held_median_control", np.nan))) < 0.01}
    t, h = counts(pp)
    rot = []
    for f in FAMILIES:
        fam = [(c, k) for c, k in pp if int(c["family"]) == f]
        cells = [c for c, _ in fam]
        rot += [(cells[(i + 1) % len(cells)], k) for i, (_, k) in enumerate(fam)]
    t_rot, h_rot = counts(rot)
    t_self, h_self = counts([(k, k) for _, k in pp])
    controls = {"self_pair": {"t": t_self, "h": h_self, "ok": t_self == 0 and h_self == 0},
                "shuffled_pairing": {"t": t_rot, "h": h_rot, "binding": False,
                                     "note": "within-family rotation of the cell runs; reported to show whether t and h depend on the same-stream pairing"}}
    ok = controls["self_pair"]["ok"]
    dtr = [float(k["train_nk_per_landscape_top1"]) - float(c["train_nk_per_landscape_top1"]) for c, k in pp]
    dhd = [float(k["held_per_landscape_top1"]) - float(c["held_per_landscape_top1"]) for c, k in pp]
    shares = [B6.charge_share(c) for c, _ in pp]
    by_fam = {str(f): dict(zip(("t", "h"), counts([(c, k) for c, k in pp if int(c["family"]) == f]))) for f in FAMILIES}
    ctx.emit({"kind": "summary", "exp": exp, "predicate_id": predicate_id, "anomaly": ANOMALY, "status": status,
              "evidence_class": "VERDICT", "ts": round(time.time(), 3), "qd_runs": 0,
              "source_rows": SRC_ROWS, "source_provenance": provenance,
              "source_rows_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
              "runs_total": len(pp), "rng_family_count": len([f for f in per_fam if per_fam[f]]), "runs_per_family": 8,
              "families": list(FAMILIES), "n_per_family": per_fam, "beta": beta,
              "checks": {"I1": i1, "controls_ok": ok}, "controls": controls,
              "t_control_train_gt_cell": t, "h_control_held_gt_cell": h,
              "decision": decide(all(i1.values()), ok, t, h),
              "reported_not_judged": {
                  "median_train_diff_control_minus_cell": float(np.median(dtr)),
                  "median_held_diff_control_minus_cell": float(np.median(dhd)),
                  "spearman_charge_share_vs_held_diff": spearman(shares, dhd),
                  "median_charge_share": float(np.median(shares)),
                  "by_family": by_fam, "round6_same_instrument": R6},
              "wall_s": round(time.perf_counter() - t0, 3)})
