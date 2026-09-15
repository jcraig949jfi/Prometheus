"""D-R6-1: leave-one-family-out on the CANDIDATE B-R5-1 itself (SWARM_R6 s5 D, prompts_r6/D.md item 1).

D-R5-1 asked whether w13's ELIGIBILITY rests on one RNG family (it does not). This asks the same of the candidate's
PASS: B-R5-1 (int4 linear + a4 codebook, 16 B, w13 train128_held64) scored progress_above_floor 1.5914, CI
[1.1389, 1.8271] over 32 runs in 4 families (receipt 1789473262958-0). Zero new QD: committed rows only
(B-R5-1 run rows, pinned against commit 4e69568e8; G R16 baseline + floor rows through metric.eligibility).

For each held-out family (4200, 2101, 3303, 5501) the remaining 24 runs (3 families, 8 per family) are re-read:
  progress = (median - floor) / (baseline median - floor), CI = metric.ci.median_ci mapped through the same formula
  -- floor, baseline and denominator from eligibility.w13_eligibility(), exactly as check_r4 computes them.
check_r4 is called on every pool with the pool's honest sample stamp; on a 24-run pool it refuses INELIGIBLE
CANDIDATE_N (expected, recorded). This is a robustness read of an existing PASS, not a new Clause A verdict.

Rule (fixed before reading): ROBUST iff the progress CI low > 0.95 in 4/4 held-out pools; NOT_ROBUST otherwise
(-> one minimum discriminator, item 3); INDETERMINATE if I1 (the 32-run pool reproduces B's receipt through
check_r4: PASS, same progress and CI) or either planted control fails.
Reported, not judged: matched-baseline LOO (baseline median also without the held-out family), 8-run family
blocks, runs below the floor per family.

    worker.submit("D", "primordial.cohorts.d.r6_1_b_r5_1_family_loo:job", EXP, ROWS, 300, envelope={...PRODUCTION...})
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import time

import numpy as np

from primordial.metric import baseline as BL
from primordial.metric import eligibility as EL
from primordial.metric import readout as RO
from primordial.metric import sample as SM
from primordial.metric.ci import median_ci
from primordial.ops import qd_ledger as QL

EXP = "D-R6-1-b-r5-1-family-loo"
PREDICATE_ID = EXP
ROOT = pathlib.Path(__file__).resolve().parents[3]
CAND_ROWS = "primordial/ledger/rows/B/B-R5-1-cand-int4a4-w13-train128.jsonl"
CAND_COMMIT = "4e69568e8"
BASE_ROWS = "primordial/ledger/rows/G/G-R16-baseline.jsonl"
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
WORLD, GS, PRESSURE = "w13", 13, "train128_held64"
ORDER = tuple(BL.FAMILIES)              # B-R5-1 plan order: families x run seeds (the pooled order median_ci saw)
B_RECEIPT = {"id": "1789473262958-0", "progress": 1.5913978494623655,
             "progress_ci95": (1.1388888888888888, 1.8270609318996416)}
ROBUST_AT = QL.PROGRESS_PASS            # 0.95, imported from the judge
TOL = 1e-9


def load_runs(text: str) -> list[dict]:
    """w13 train128 run rows, last row per (family, run seed) wins, in ORDER then run seed."""
    runs = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        x = json.loads(line)
        if x.get("kind") == "run" and int(x.get("gen_seed") or -1) == GS and x.get("pressure") == PRESSURE:
            runs[(int(x["rng_family"]), int(x["run_seed"]))] = x
    return [runs[k] for k in sorted(runs, key=lambda k: (ORDER.index(k[0]), k[1]))]


def held_of(runs) -> list[float]:
    return [float(x["held64_per_seed"]) for x in runs]


def progress_row(runs, floor: float, den: float, judge=None) -> dict:
    """One pool read through the shared formula; `judge(median, held, stamp)` -> check_r4's dict (or None)."""
    held = held_of(runs)
    s = SM.stamp(runs)
    med = float(np.median(held))
    lo, hi = median_ci(held)
    out = {k: s[k] for k in ("runs_total", "rng_family_count", "runs_per_family", "families", "n_per_family")}
    out.update(median=med, candidate_ci95=[lo, hi], progress=(med - floor) / den,
               progress_ci95=[(lo - floor) / den, (hi - floor) / den],
               runs_below_floor=int(sum(v < floor for v in held)))
    out["ci_low_gt_robust_at"] = bool(out["progress_ci95"][0] > ROBUST_AT)
    if judge is not None:
        j = judge(med, held, s)
        out["judge"] = {k: j.get(k) for k in ("verdict", "why", "progress", "progress_ci95")}
    return out


def _reproduces(row: dict, ref: dict) -> bool:
    j = row.get("judge") or {}
    return (j.get("verdict") == "PASS" and abs(row["progress"] - ref["progress"]) < TOL
            and all(abs(a - b) < TOL for a, b in zip(row["progress_ci95"], ref["progress_ci95"]))
            and abs(float(j.get("progress") or 0) - ref["progress"]) < TOL
            and all(abs(a - b) < TOL for a, b in zip(j.get("progress_ci95") or (0, 0), ref["progress_ci95"])))


def loo(runs, floor, den, judge=None) -> dict:
    return {str(f): progress_row([x for x in runs if int(x["rng_family"]) != f], floor, den, judge) for f in ORDER}


def planted(runs, value_of) -> list[dict]:
    return [{**x, "held64_per_seed": value_of(x)} for x in runs]


def analyse(cand, base, floor: float, den: float, judge=None, ref=B_RECEIPT) -> dict:
    full = progress_row(cand, floor, den, judge)
    held_out = loo(cand, floor, den, judge)
    k = sum(v["ci_low_gt_robust_at"] for v in held_out.values())
    # controls: the rule must be able to say NOT_ROBUST (one family carries the pool) and ROBUST (every run at 2x)
    carried = planted(cand, lambda x: float(x["held64_per_seed"]) if int(x["rng_family"]) == ORDER[0] else floor - 1.0)
    flat = planted(cand, lambda x: floor + 2.0 * den)
    k_carried = sum(v["ci_low_gt_robust_at"] for v in loo(carried, floor, den).values())
    k_flat = sum(v["ci_low_gt_robust_at"] for v in loo(flat, floor, den).values())
    controls = {"planted_one_family_carries": {"k_of_4": k_carried, "detected_not_robust": k_carried < 4},
                "planted_all_runs_progress_2": {"k_of_4": k_flat, "passes_robust": k_flat == 4}}
    matched = {}
    base_held = {f: [float(x["held64_per_seed"]) for x in base if int(x["rng_family"]) != f] for f in ORDER}
    for f in ORDER:
        bm = float(np.median(base_held[f]))
        d = bm - floor
        row = held_out[str(f)]
        lo, hi = row["candidate_ci95"]
        matched[str(f)] = {"baseline_median_wo_family": bm, "denominator": d,
                           "progress": (row["median"] - floor) / d if d > 0 else None,
                           "progress_ci95": [(lo - floor) / d, (hi - floor) / d] if d > 0 else None}
    blocks = {str(f): progress_row([x for x in cand if int(x["rng_family"]) == f], floor, den) for f in ORDER}
    i1 = _reproduces(full, ref)
    ctl_ok = controls["planted_one_family_carries"]["detected_not_robust"] and controls["planted_all_runs_progress_2"]["passes_robust"]
    decision = "INDETERMINATE" if not (i1 and ctl_ok) else ("ROBUST" if k == 4 else "NOT_ROBUST")
    return {"full": full, "leave_one_family_out": held_out, "loo_ci_low_gt_095_k_of_4": k,
            "min_loo_ci_low": min(v["progress_ci95"][0] for v in held_out.values()),
            "controls": controls, "reported_not_judged": {
                "matched_baseline_loo": matched, "family_blocks_8": blocks,
                "runs_below_floor_by_family": {str(f): blocks[str(f)]["runs_below_floor"] for f in ORDER}},
            "checks": {"I1_full_pool_reproduces_B_receipt_via_check_r4": bool(i1), "controls_ok": bool(ctl_ok),
                       "P_loo_ci_low_gt_095_k_of_4": k},
            "decision": decision}


def _git_show(commit: str, path: str) -> bytes:
    q = subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{path}"], capture_output=True)
    return q.stdout if q.returncode == 0 else b""


def job(ctx, status="record"):
    t0 = time.perf_counter()
    doc = EL.r16_doc()
    el = EL.eligibility(WORLD, PRESSURE, doc)
    floor, den = float(el["floor"]), float(el["progress_denominator"])
    cand_bytes = (ROOT / CAND_ROWS).read_bytes()
    pinned = _git_show(CAND_COMMIT, CAND_ROWS)
    cand_text = cand_bytes.decode("utf-8")
    summary = [json.loads(l) for l in cand_text.splitlines() if l.strip() and json.loads(l).get("kind") == "candidate"][-1]
    cand = load_runs(cand_text)
    base = load_runs((ROOT / BASE_ROWS).read_text(encoding="utf-8"))

    def judge(med, held, s):
        return QL.check_r4(WORLD, PRESSURE, med, int(summary["bytes"]), s["runs_total"],
                           oracle_clean=bool(summary["oracle_clean"]), held=held, doc=doc, readout=RO.NAME,
                           runs_total=s["runs_total"], rng_family_count=s["rng_family_count"],
                           runs_per_family=s["runs_per_family"], n_per_family=s["n_per_family"])

    res = analyse(cand, base, floor, den, judge)
    by_run = summary["held64_by_run"]
    integrity = {
        "cand_rows_sha256": hashlib.sha256(cand_bytes).hexdigest(),
        "cand_rows_equal_commit_4e69568e8": bool(pinned) and hashlib.sha256(pinned).hexdigest() == hashlib.sha256(cand_bytes).hexdigest(),
        "cand_runs": len(cand), "cand_held_equal_summary_held64_by_run": len(by_run) == len(cand) and all(
            float(by_run[f"{x['rng_family']}|{x['run_seed']}"]) == float(x["held64_per_seed"]) for x in cand),
        "cand_readout": sorted({x.get("readout") for x in cand}), "baseline_runs": len(base),
        "floor_equal_summary": float(summary["floor"]) == floor,
        "baseline_equal_summary": float(summary["baseline"]) == float(el["baseline"]["median"]),
        "baseline_median_equal_pool_median": abs(float(np.median(held_of(base))) - float(el["baseline"]["median"])) < TOL}
    integrity["clean"] = bool(integrity["cand_rows_equal_commit_4e69568e8"] and integrity["cand_runs"] == 32
                              and integrity["cand_held_equal_summary_held64_by_run"] and integrity["baseline_runs"] == 32
                              and integrity["floor_equal_summary"] and integrity["baseline_equal_summary"]
                              and integrity["cand_readout"] == [RO.NAME])
    if not integrity["clean"]:
        res["decision"] = "INDETERMINATE"
    ctx.emit({"kind": "summary", "exp": EXP, "predicate_id": PREDICATE_ID, "status": status, "ts": round(time.time(), 3),
              "cell": f"{WORLD} {PRESSURE}", "candidate": "B-R5-1 int4 linear + a4 codebook 16 B",
              "candidate_receipt": B_RECEIPT["id"], "variant": el["variant"], "floor": floor,
              "baseline_median": el["baseline"]["median"], "progress_denominator": den, "robust_at": ROBUST_AT,
              "source_rows": {"candidate": CAND_ROWS, "candidate_commit": CAND_COMMIT, "baseline": BASE_ROWS,
                              "eligibility_rows_commits": el["rows_commits"]},
              "pool_order": list(ORDER), "runs_total": 32, "rng_family_count": 4, "runs_per_family": 8,
              "loo_pool": {"runs_total": 24, "rng_family_count": 3, "runs_per_family": 8},
              "qd_runs": 0, "oracle_source_rows_integrity": integrity,
              "wall_s": round(time.perf_counter() - t0, 3), **res})
