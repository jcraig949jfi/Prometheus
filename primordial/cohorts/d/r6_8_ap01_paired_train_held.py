"""D-R6-8 (ANOM-1789490583451-0): C-R6-AP-01's anti-prior-arm PASS -- a tucker/nk_stub cell cut to 1/5 CPU (75-91 of 400
generations) scores a HIGHER held-out median than the 400-generation control. Do the extra generations buy train fitness
that does not transfer to the held-out landscapes?

Zero QD: C's committed per-run rows (primordial/ledger/rows/C/C-R6-AP-01-tucker-nk-cpu-ttl-graphblas.jsonl), cell and
control paired on the same (family, run seed) -- same mutation and sampler streams, 32 pairs, families 4200 / 2101 /
3303 / 5501 x run seeds 0..7. Fields: train_per_landscape_top1, held_per_landscape_top1, gens_done; the reference row's
random_bits_mean_per_held_landscape.

Rule (fixed before reading; pairs p = 1..32):
  I1  32 pairs, 8 per family, every control gens_done == 400 and every cell gens_done < 400; the recomputed medians of
      held_per_landscape_top1 equal C's summary held_median_cell / held_median_control to 0.01 -- else INDETERMINATE.
  t = #pairs with control train > cell train; h = #pairs with control held > cell held.
  TRAIN_NOT_HELD  t >= 26 and h <= 16   (the extra generations raise train fitness in >= 80% of pairs, held-out in at most half)
  BOTH_GAIN       t >= 26 and h >= 26
  NO_TRAIN_GAIN   t <= 16               (by ~80 generations the train fitness is already where 400 gets it)
  MIXED           otherwise
Controls: self_pair (binding: control vs itself gives t = 0, h = 0); shuffled_pairing (reported, not binding: t and h
with cell runs rotated within family, to show whether the counts depend on the same-stream pairing).
Reported, not judged: paired medians of train and held differences, held minus random per arm, gens_done range,
Spearman rank correlation of train vs held within each arm.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import time

import numpy as np

EXP = "D-R6-8-ap01-paired-train-held"
PREDICATE_ID = EXP
ANOMALY = "1789490583451-0"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
SRC_ROWS = "primordial/ledger/rows/C/C-R6-AP-01-tucker-nk-cpu-ttl-graphblas.jsonl"
FAMILIES = (4200, 2101, 3303, 5501)


def load(text: str):
    rows = [json.loads(l) for l in text.splitlines() if l.strip()]
    runs = {}
    for x in rows:
        if x.get("kind") == "run" and x.get("arm") in ("cell", "control"):
            runs[(x["arm"], int(x["family"]), int(x["run_seed"]))] = x
    ref = next((x for x in rows if x.get("kind") == "reference"), {})
    summ = [x for x in rows if x.get("kind") == "summary"]
    return runs, ref, (summ[-1] if summ else {})


def pairs(runs) -> list[tuple[dict, dict]]:
    keys = sorted({(f, s) for (_, f, s) in runs}, key=lambda k: (FAMILIES.index(k[0]) if k[0] in FAMILIES else 99, k[1]))
    return [(runs[("cell", f, s)], runs[("control", f, s)]) for f, s in keys if ("cell", f, s) in runs and ("control", f, s) in runs]


def counts(pp) -> tuple[int, int]:
    t = sum(c["train_per_landscape_top1"] > x["train_per_landscape_top1"] for x, c in pp)
    h = sum(c["held_per_landscape_top1"] > x["held_per_landscape_top1"] for x, c in pp)
    return int(t), int(h)


def decide(i1: bool, controls_ok: bool, t: int, h: int) -> str:
    if not (i1 and controls_ok):
        return "INDETERMINATE"
    if t <= 16:
        return "NO_TRAIN_GAIN"
    if t >= 26 and h <= 16:
        return "TRAIN_NOT_HELD"
    if t >= 26 and h >= 26:
        return "BOTH_GAIN"
    return "MIXED"


def spearman(a, b) -> float:
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1]) if len(a) > 2 else float("nan")


def job(ctx, status="record"):
    t0 = time.perf_counter()
    text = (ROOT / SRC_ROWS).read_text(encoding="utf-8")
    runs, ref, summ = load(text)
    pp = pairs(runs)
    per_fam = {str(f): sum(int(x["family"]) == f for x, _ in pp) for f in FAMILIES}
    cell_h = [x["held_per_landscape_top1"] for x, _ in pp]
    ctrl_h = [c["held_per_landscape_top1"] for _, c in pp]
    i1 = {"pairs_32": len(pp) == 32, "per_family_8": all(v == 8 for v in per_fam.values()),
          "control_gens_400": all(int(c["gens_done"]) == 400 for _, c in pp),
          "cell_gens_below_400": all(int(x["gens_done"]) < 400 for x, _ in pp),
          "median_cell_matches_summary": abs(float(np.median(cell_h)) - float(summ.get("held_median_cell", np.nan))) < 0.01,
          "median_control_matches_summary": abs(float(np.median(ctrl_h)) - float(summ.get("held_median_control", np.nan))) < 0.01}
    t, h = counts(pp)
    rot = []
    for f in FAMILIES:
        fam = [(x, c) for x, c in pp if int(x["family"]) == f]
        cells = [x for x, _ in fam]
        rot += [(cells[(i + 1) % len(cells)], c) for i, (_, c) in enumerate(fam)]
    t_rot, h_rot = counts(rot)
    t_self, h_self = counts([(c, c) for _, c in pp])
    controls = {"shuffled_pairing": {"t": t_rot, "h": h_rot, "binding": False,
                                     "note": "within-family rotation of cell runs; reported to show whether t depends on the stream pairing"},
                "self_pair": {"t": t_self, "h": h_self, "ok": t_self == 0 and h_self == 0}}
    ok = controls["self_pair"]["ok"]
    dtr = [c["train_per_landscape_top1"] - x["train_per_landscape_top1"] for x, c in pp]
    dhd = [c["held_per_landscape_top1"] - x["held_per_landscape_top1"] for x, c in pp]
    rnd = float(ref.get("random_bits_mean_per_held_landscape", np.nan))
    ctx.emit({"kind": "summary", "exp": EXP, "predicate_id": PREDICATE_ID, "anomaly": ANOMALY, "status": status,
              "ts": round(time.time(), 3), "qd_runs": 0, "source_rows": SRC_ROWS,
              "source_rows_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
              "runs_total": len(pp), "rng_family_count": len([f for f in per_fam if per_fam[f]]), "runs_per_family": 8,
              "families": list(FAMILIES), "n_per_family": per_fam,
              "checks": {"I1": i1, "controls_ok": bool(ok)}, "controls": controls,
              "t_control_train_gt_cell": t, "h_control_held_gt_cell": h,
              "reported_not_judged": {
                  "median_train_diff_control_minus_cell": float(np.median(dtr)),
                  "median_held_diff_control_minus_cell": float(np.median(dhd)),
                  "median_held_minus_random": {"cell": float(np.median(cell_h)) - rnd, "control": float(np.median(ctrl_h)) - rnd},
                  "cell_gens_done_range": [int(min(x["gens_done"] for x, _ in pp)), int(max(x["gens_done"] for x, _ in pp))],
                  "spearman_train_held": {"cell": spearman([x["train_per_landscape_top1"] for x, _ in pp], cell_h),
                                          "control": spearman([c["train_per_landscape_top1"] for _, c in pp], ctrl_h)}},
              "decision": decide(all(i1.values()), ok, t, h), "wall_s": round(time.perf_counter() - t0, 3)})
