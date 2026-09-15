"""D-R7-2 (ANOM-1789485427773-0, prompts_r7/D.md item 2): B-R5-1 PASS -- all 3 of 32 candidate runs below the w13 floor
are in RNG family 3303 (3303|2 165.875, |6 162.0, |7 161.609375; floor 166.46875). Minimum discriminator from committed
rows first, zero QD.

Seen before this predicate: the anomaly text; D-R6-1 (receipt 1789488540808-0: leave-one-family-out ROBUST; 8-run 3303
block CI low -0.256); D-R4-2 memory (w13 train128 baseline family medians at M2 differ); the row schemas; and that B's
32 run streams are G's float-baseline streams: metric.baseline.seeds_of gives mutation [F, rs, 13, 128] and sampler
[F+1, rs, 13, 128] to both, the (family, run seed) keys match 32/32 and every pair's sampler seed is equal. No 3303
baseline value and no control_obs_use value was read.

Two questions, one rule each, over the same 32 same-stream pairs (B-R5-1 candidate rows, G-R16-baseline w13
train128_held64 rows through D-R6-1's loader; floor from metric.eligibility as check_r4 uses it):
  L = candidate runs with held64 < floor.
  STREAM axis   q = #L whose same-stream BASELINE run is among the 8 lowest of the 32 baseline runs.
                SHARED_STREAM  q == |L|, |L| >= 3  (chance for 3 of 3: C(8,3)/C(32,3) = 1.1%): the streams are low for
                               both representations
                NOT_STREAM     q <= 1                                     : the low runs are candidate-specific
                MIXED_STREAM   otherwise
  OBS axis      u = #L whose control_obs_use.uses_observations is True; U = the same count over the other runs.
                OBS_UNUSED     u == 0 and U >= 0.9 * (32 - |L|)  : the low runs are the ones that stopped reading observations
                OBS_USED       u == |L|
                OBS_MIXED      otherwise
  decision = "<STREAM>+<OBS>".
  I1  32 pairs, 8 per family, keys and sampler seeds equal pairwise; L == {3303|2, 3303|6, 3303|7} with the filed
      values; B's candidate row held64_by_run equals the run rows. Else INDETERMINATE.
  controls (binding): planted_shared (baseline of the L keys set to the 3 lowest baseline values -> SHARED_STREAM) and
      planted_specific (baseline of the L keys set to the baseline max -> NOT_STREAM).
Reported, not judged: baseline values and ranks of the L streams; baseline family medians; Spearman candidate vs
baseline over the 32 pairs, and under a within-family rotation of the baseline; candidate - baseline per L pair;
held64_w_zeroed of the L runs vs the other runs' median.

    worker.submit("D", "primordial.cohorts.d.r7_2_fam3303_same_stream:job", EXP, ROWS, 300, envelope={...PRODUCTION...})
"""
from __future__ import annotations

import hashlib
import json
import time

import numpy as np

from primordial.cohorts.d import r6_1_b_r5_1_family_loo as L6
from primordial.metric import eligibility as EL

EXP = "D-R7-2-fam3303-same-stream"
PREDICATE_ID = EXP
ANOMALY = "1789485427773-0"
ROOT = L6.ROOT
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
CAND_ROWS, BASE_ROWS = L6.CAND_ROWS, L6.BASE_ROWS
ORDER = L6.ORDER
FILED_LOW = {(3303, 2): 165.875, (3303, 6): 162.0, (3303, 7): 161.609375}
BOTTOM = 8


def key(x) -> tuple[int, int]:
    return int(x["rng_family"]), int(x["run_seed"])


def stream_axis(low_keys, base_by_key: dict) -> tuple[str, int]:
    bottom = set(sorted(base_by_key, key=lambda k: (base_by_key[k], k))[:BOTTOM])
    q = sum(k in bottom for k in low_keys)
    if len(low_keys) >= 3 and q == len(low_keys):
        return "SHARED_STREAM", q
    if q <= 1:
        return "NOT_STREAM", q
    return "MIXED_STREAM", q


def obs_axis(low_keys, uses: dict) -> tuple[str, int, int]:
    u = sum(bool(uses[k]) for k in low_keys)
    others = [k for k in uses if k not in set(low_keys)]
    big_u = sum(bool(uses[k]) for k in others)
    if u == 0 and big_u >= 0.9 * len(others):
        return "OBS_UNUSED", u, big_u
    if u == len(low_keys):
        return "OBS_USED", u, big_u
    return "OBS_MIXED", u, big_u


def spearman(a, b) -> float:
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def analyse(cand: list[dict], base: list[dict], floor: float, by_run=None) -> dict:
    ck, bk = [key(x) for x in cand], [key(x) for x in base]
    cv = {key(x): float(x["held64_per_seed"]) for x in cand}
    bv = {key(x): float(x["held64_per_seed"]) for x in base}
    uses = {key(x): bool((x.get("control_obs_use") or {}).get("uses_observations")) for x in cand}
    low = [k for k in ck if cv[k] < floor]
    per_fam = {str(f): sum(k[0] == f for k in ck) for f in ORDER}
    i1 = {"pairs_32": len(ck) == 32 and ck == bk, "per_family_8": all(v == 8 for v in per_fam.values()),
          "sampler_seeds_equal": all(list(a.get("sampler_seed") or []) == list(b.get("sampler_seed") or [])
                                     for a, b in zip(cand, base)),
          "low_set_as_filed": set(low) == set(FILED_LOW) and all(cv[k] == v for k, v in FILED_LOW.items()),
          "held64_by_run_matches": by_run is None or [float(v) for v in by_run] == [cv[k] for k in ck]}
    stream, q = stream_axis(low, bv)
    obs, u, big_u = obs_axis(low, uses)
    lowest = sorted(bv.values())[:len(low)]
    shared = {**bv, **dict(zip(low, lowest))}
    specific = {**bv, **{k: max(bv.values()) for k in low}}
    controls = {"planted_shared": {"label": stream_axis(low, shared)[0]},
                "planted_specific": {"label": stream_axis(low, specific)[0]}}
    controls["planted_shared"]["ok"] = controls["planted_shared"]["label"] == "SHARED_STREAM"
    controls["planted_specific"]["ok"] = controls["planted_specific"]["label"] == "NOT_STREAM"
    ok = all(c["ok"] for c in controls.values())
    decision = f"{stream}+{obs}" if (all(i1.values()) and ok) else "INDETERMINATE"
    rank = {k: i + 1 for i, k in enumerate(sorted(bv, key=lambda k: (bv[k], k)))}
    rot = []
    for f in ORDER:
        ks = [k for k in ck if k[0] == f]
        rot += [(cv[k], bv[ks[(i + 1) % len(ks)]]) for i, k in enumerate(ks)]
    zeroed = {key(x): (x.get("control_obs_use") or {}).get("held64_w_zeroed") for x in cand}
    return {"checks": {"I1": i1, "controls_ok": ok}, "controls": controls, "decision": decision,
            "stats": {"floor": floor, "low": [list(k) for k in low], "q_low_in_baseline_bottom8": q,
                      "u_low_using_obs": u, "U_others_using_obs": big_u, "stream": stream, "obs": obs},
            "reported_not_judged": {
                "baseline_of_low": {f"{k[0]}|{k[1]}": {"held": bv[k], "rank_of_32": rank[k]} for k in low},
                "cand_minus_base_low": {f"{k[0]}|{k[1]}": cv[k] - bv[k] for k in low},
                "baseline_family_median": {str(f): float(np.median([bv[k] for k in bk if k[0] == f])) for f in ORDER},
                "candidate_family_median": {str(f): float(np.median([cv[k] for k in ck if k[0] == f])) for f in ORDER},
                "spearman_cand_base_same_stream": spearman([cv[k] for k in ck], [bv[k] for k in ck]),
                "spearman_within_family_rotation": spearman([a for a, _ in rot], [b for _, b in rot]),
                "held64_w_zeroed_low": {f"{k[0]}|{k[1]}": zeroed[k] for k in low},
                "held64_w_zeroed_median_others": float(np.median([zeroed[k] for k in ck if k not in set(low)
                                                                  and zeroed[k] is not None] or [np.nan]))},
            "sample": {"runs_total": len(ck), "rng_family_count": len([f for f in per_fam if per_fam[f]]),
                       "runs_per_family": 8, "families": list(ORDER), "n_per_family": per_fam}}


def job(ctx, status="record"):
    t0 = time.perf_counter()
    doc = EL.r16_doc()
    floor = float(EL.eligibility(L6.WORLD, L6.PRESSURE, doc)["floor"])
    cand_bytes, base_bytes = (ROOT / CAND_ROWS).read_bytes(), (ROOT / BASE_ROWS).read_bytes()
    cand_text = cand_bytes.decode("utf-8")
    summary = [json.loads(l) for l in cand_text.splitlines() if l.strip() and json.loads(l).get("kind") == "candidate"][-1]
    res = analyse(L6.load_runs(cand_text), L6.load_runs(base_bytes.decode("utf-8")), floor, summary.get("held64_by_run"))
    ctx.emit({"kind": "summary", "exp": EXP, "predicate_id": PREDICATE_ID, "anomaly": ANOMALY, "status": status,
              "ts": round(time.time(), 3), "qd_runs": 0,
              "source_rows": {CAND_ROWS: hashlib.sha256(cand_bytes).hexdigest(),
                              BASE_ROWS: hashlib.sha256(base_bytes).hexdigest()},
              **res.pop("sample"), **res, "wall_s": round(time.perf_counter() - t0, 3)})
