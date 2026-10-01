"""W2-15 / D12 sensitivity (read-only). python -B d12_sensitivity.py -> d12_sensitivity.json

D12 (W2-8): run_dd.screen seeds the L2 assay on the genome's INDEX in the sorted checkpoint list and
re-draws at every checkpoint, so P(labelled COMPETENT) is 0.036 / 0.21 / 0.55 at true rate 0.3 / 0.4 / 0.5.
Borderline genomes get a fresh lottery ticket at every checkpoint; "any checkpoint with L2" therefore
admits genomes whose 20-seed rate sits near 0.5.

Question: do the verdicts whose endpoint is "run has an L2 donor" (C-DENSE-COPY) or
"runaway given L2" (C-STATELESS, C-STATELESS-FFA6, X-DD-DENSE-COPY) change if L2 is re-defined
strictly (best recorded 20-seed rate >= 0.6, >= 0.7)? A run is re-classified as L2 only if some
checkpoint records a competent genome at or above the strict rate. Runaway = depth >= 20 (as frozen).
This cannot recover genomes the noisy screen MISSED (false negatives), only drop borderline admissions.
"""
from __future__ import annotations

import glob
import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2] / "campaigns" / "npe-w1-donor-discovery-2026-09-26"
OUT = pathlib.Path(__file__).resolve().parent / "d12_sensitivity.json"


def fisher_one_sided(a, n1, c, n2):
    """P(X >= a) for X ~ hypergeometric: row1 successes a of n1, row2 successes c of n2 (row1 > row2)."""
    k = a + c
    N = n1 + n2
    tot = math.comb(N, k)
    return sum(math.comb(n1, x) * math.comb(n2, k - x) for x in range(a, min(n1, k) + 1)) / tot


def best_rate(rec):
    rates = [g["rate"] for cp in rec.get("checkpoints", []) for g in cp.get("competent_genomes", [])]
    return max(rates) if rates else None


def load(pattern):
    return [json.loads(pathlib.Path(p).read_text()) for p in sorted(glob.glob(str(ROOT / pattern)))]


def summarise(recs, thr):
    l2 = [r for r in recs if (best_rate(r) is not None and best_rate(r) >= thr)]
    est = [r for r in l2 if r["depth"] >= 20]
    return {"n": len(recs), "L2": len(l2), "L4_given_L2": len(est)}


out = {"thresholds": [0.5, 0.6, 0.7]}

# C-DENSE-COPY: endpoint = runs with a donor (L2), PLAIN vs DENSE_COPY.
cdc = load("c_dense_copy/results/*.json")
arms = sorted({r["arm"] for r in cdc})
out["C-DENSE-COPY"] = {}
for thr in out["thresholds"]:
    row = {a: summarise([r for r in cdc if r["arm"] == a], thr) for a in arms}
    if len(arms) == 2:
        hi, lo = ("DENSE_COPY", "PLAIN") if "DENSE_COPY" in arms else (arms[1], arms[0])
        row["fisher_p_L2"] = fisher_one_sided(row[hi]["L2"], row[hi]["n"], row[lo]["L2"], row[lo]["n"])
    out["C-DENSE-COPY"][str(thr)] = row

# C-STATELESS-FFA6 and C-STATELESS: endpoint = runaway given L2, DENSE vs STATELESS.
for name, dd, sd in (("C-STATELESS-FFA6", "c_stateless_ffa6/dense/results/*.json", "c_stateless_ffa6/stateless/results/*.json"),
                     ("C-STATELESS", "c_stateless/dense/results/*.json", "c_stateless/stateless/results/*.json")):
    D, S = load(dd), load(sd)
    if not D or not S:
        out[name] = {"error": "result files not found", "dense": len(D), "stateless": len(S)}
        continue
    out[name] = {}
    for thr in out["thresholds"]:
        d, s = summarise(D, thr), summarise(S, thr)
        p = fisher_one_sided(s["L4_given_L2"], s["L2"], d["L4_given_L2"], d["L2"]) if d["L2"] and s["L2"] else None
        out[name][str(thr)] = {"DENSE": d, "STATELESS": s,
                               "rate_DENSE": round(d["L4_given_L2"] / d["L2"], 4) if d["L2"] else None,
                               "rate_STATELESS": round(s["L4_given_L2"] / s["L2"], 4) if s["L2"] else None,
                               "fisher_p": p}
    # borderline-donor runs per arm (best rate < 0.6): is the noisy admission differential between arms?
    out[name]["borderline_runs_best_rate_lt_0.6"] = {
        "DENSE": sum(1 for r in D if best_rate(r) is not None and best_rate(r) < 0.6),
        "STATELESS": sum(1 for r in S if best_rate(r) is not None and best_rate(r) < 0.6)}

OUT.write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))


# --- part 2: records without per-genome rates (C-STATELESS, C-STATELESS-FFA6 store only L2 counts per
# checkpoint). Proxy for borderline admission: a run whose L2 label appears at exactly ONE checkpoint
# (a flicker) vs at >= 2 checkpoints (persistent). Recompute runaway-given-L2 with the persistent definition.
def l2_cps(rec):
    return sum(1 for c in rec.get("checkpoints", []) if c.get("L2", 0) > 0)


def summarise_cp(recs, min_cps):
    l2 = [r for r in recs if l2_cps(r) >= min_cps]
    return {"n": len(recs), "L2": len(l2), "L4_given_L2": sum(r["depth"] >= 20 for r in l2)}


for name, dd, sd in (("C-STATELESS-FFA6", "c_stateless_ffa6/dense/results/*.json", "c_stateless_ffa6/stateless/results/*.json"),
                     ("C-STATELESS", "c_stateless/dense/results/*.json", "c_stateless/stateless/results/*.json")):
    D, S = load(dd), load(sd)
    res = {}
    for m in (1, 2, 3):
        d, s = summarise_cp(D, m), summarise_cp(S, m)
        res["min_L2_checkpoints_%d" % m] = {
            "DENSE": d, "STATELESS": s,
            "rate_DENSE": round(d["L4_given_L2"] / d["L2"], 4) if d["L2"] else None,
            "rate_STATELESS": round(s["L4_given_L2"] / s["L2"], 4) if s["L2"] else None,
            "fisher_p": fisher_one_sided(s["L4_given_L2"], s["L2"], d["L4_given_L2"], d["L2"]) if d["L2"] and s["L2"] else None}
    res["single_checkpoint_L2_runs"] = {"DENSE": sum(1 for r in D if l2_cps(r) == 1),
                                        "STATELESS": sum(1 for r in S if l2_cps(r) == 1),
                                        "of_which_runaway": {"DENSE": sum(1 for r in D if l2_cps(r) == 1 and r["depth"] >= 20),
                                                             "STATELESS": sum(1 for r in S if l2_cps(r) == 1 and r["depth"] >= 20)}}
    out[name] = res

OUT.write_text(json.dumps(out, indent=1))
print(json.dumps({k: out[k] for k in ("C-STATELESS-FFA6", "C-STATELESS")}, indent=1))
