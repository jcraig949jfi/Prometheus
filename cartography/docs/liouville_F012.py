"""Liouville side-check for F012 — definitional-drift audit.

Prior: sessionB wsw_F012 killed H85 using Möbius μ(n) on abs_disc stratified by aut_grp_label.
Result: max|z| over adequate strata = 0.39, permutation-null p = 0.6843.

This task: re-run IDENTICALLY but with Liouville λ(n) = (-1)^Ω(n) where Ω counts prime
factors with multiplicity. Liouville is never 0 (unlike μ which zeros out non-squarefree).
If λ gives |z| >> 0.39, the original H85 |z|=6.15 was Liouville-based and kill needs rescinding.
If λ agrees with μ (p ~ 0.7), the F012 kill is confirmed regardless of definition.

Output: cartography/docs/liouville_F012_results.json
"""
import json
import os
import time
from pathlib import Path

import numpy as np
import psycopg2
from sympy.ntheory import factorint

DB = dict(host="192.168.1.176", port=5432, dbname="lmfdb", user="lmfdb", password="lmfdb")
N_PERM = 1000
SEED = 20260417  # SAME seed as wsw_F012.py for stratum-shuffle reproducibility
MIN_N_PER_STRATUM = 100
OUT_PATH = Path("D:/Prometheus/cartography/docs/liouville_F012_results.json")

rng = np.random.default_rng(SEED)


def liouville(n: int) -> int:
    """λ(n) = (-1)^Ω(n). Ω = sum of exponents in prime factorization. λ(1) = 1."""
    if n <= 0:
        return 0
    if n == 1:
        return 1
    fs = factorint(n)
    omega = sum(fs.values())
    return -1 if (omega % 2 == 1) else 1


# ---------------------------------------------------------------------------
# Load g2c_curves
# ---------------------------------------------------------------------------
t0 = time.time()
conn = psycopg2.connect(**DB)
cur = conn.cursor()
cur.execute("""
    SELECT id, aut_grp_label, abs_disc, mw_rank
    FROM g2c_curves
    WHERE aut_grp_label IS NOT NULL AND abs_disc IS NOT NULL
""")
rows = cur.fetchall()
conn.close()
print(f"[load] {len(rows)} rows in {time.time()-t0:.1f}s")

curves = []
for cid, aut, d_txt, mwr in rows:
    try:
        d = int(d_txt)
    except (ValueError, TypeError):
        continue
    try:
        r = int(mwr) if mwr is not None else -1
    except (ValueError, TypeError):
        r = -1
    curves.append((cid, aut, d, r))
print(f"[parse] {len(curves)} valid")


# ---------------------------------------------------------------------------
# Liouville per unique discriminant
# ---------------------------------------------------------------------------
t0 = time.time()
disc_to_lam = {}
lam_vals = np.empty(len(curves), dtype=np.int8)
for i, (_, _, d, _) in enumerate(curves):
    if d not in disc_to_lam:
        disc_to_lam[d] = liouville(d)
    lam_vals[i] = disc_to_lam[d]
print(f"[liouville] {len(disc_to_lam)} unique discs in {time.time()-t0:.1f}s")
print(f"[liouville] +1={int((lam_vals==1).sum())}  -1={int((lam_vals==-1).sum())}")

aut_labels = np.array([c[1] for c in curves])
ranks = np.array([c[3] for c in curves])

lam_mean = float(lam_vals.astype(np.float64).mean())
lam_var = float(lam_vals.astype(np.float64).var(ddof=0))
print(f"[stats] lam_mean={lam_mean:.4f}  lam_var={lam_var:.4f}  n={len(lam_vals)}")


# ---------------------------------------------------------------------------
# Per-stratum
# ---------------------------------------------------------------------------
def per_stratum_z(vals: np.ndarray, lbls: np.ndarray, v_mean: float, v_var: float) -> dict:
    out = {}
    for lbl in np.unique(lbls):
        mask = (lbls == lbl)
        n = int(mask.sum())
        s = int(vals[mask].sum())
        exp = n * v_mean
        std = (n * v_var) ** 0.5 if v_var > 0 else 1.0
        z = float((s - exp) / std) if std > 0 else 0.0
        out[str(lbl)] = {"n": n, "signed_sum_lam": s, "z": z, "expected": float(exp)}
    return out


baseline = per_stratum_z(lam_vals, aut_labels, lam_mean, lam_var)
print("[baseline] per-stratum:")
for lbl, s in sorted(baseline.items(), key=lambda kv: -abs(kv[1]["z"])):
    tag = "ADEQ" if s["n"] >= MIN_N_PER_STRATUM else "n<100"
    print(f"  {lbl:8s} n={s['n']:6d}  sum_lam={s['signed_sum_lam']:+6d}  z={s['z']:+6.2f}  [{tag}]")

obs_max_all = max(abs(s["z"]) for s in baseline.values())
obs_max_adeq = max((abs(s["z"]) for s in baseline.values() if s["n"] >= MIN_N_PER_STRATUM), default=0.0)
obs_carrier = max(baseline.items(), key=lambda kv: abs(kv[1]["z"]))[0]
print(f"[baseline] max |z| (all):  {obs_max_all:.2f} at {obs_carrier}")
print(f"[baseline] max |z| (adeq): {obs_max_adeq:.2f}")


# ---------------------------------------------------------------------------
# Permutation null
# ---------------------------------------------------------------------------
t0 = time.time()
unique_labels, label_idx = np.unique(aut_labels, return_inverse=True)
L = len(unique_labels)
ns_per_label = np.bincount(label_idx, minlength=L)
adequate_mask = ns_per_label >= MIN_N_PER_STRATUM

null_max_all = np.empty(N_PERM, dtype=np.float64)
null_max_adeq = np.empty(N_PERM, dtype=np.float64)
buf = label_idx.copy()
for p in range(N_PERM):
    rng.shuffle(buf)
    s = np.bincount(buf, weights=lam_vals.astype(np.float64), minlength=L)
    exp = ns_per_label * lam_mean
    std = np.sqrt(ns_per_label * lam_var)
    z = np.where(std > 0, (s - exp) / std, 0.0)
    null_max_all[p] = float(np.abs(z).max())
    null_max_adeq[p] = float(np.abs(z[adequate_mask]).max()) if adequate_mask.any() else 0.0
print(f"[perm] {N_PERM} shuffles in {time.time()-t0:.1f}s")
print(f"[perm] null max|z| ADEQ: mean={null_max_adeq.mean():.2f} std={null_max_adeq.std():.2f} "
      f"p99={np.percentile(null_max_adeq,99):.2f}")

p_adeq = float((null_max_adeq >= obs_max_adeq).sum() + 1) / (N_PERM + 1)
p_all = float((null_max_all >= obs_max_all).sum() + 1) / (N_PERM + 1)


# ---------------------------------------------------------------------------
# Prior Möbius results for direct comparison
# ---------------------------------------------------------------------------
try:
    with open("D:/Prometheus/cartography/docs/wsw_F012_results.json", "r", encoding="utf-8") as f:
        mu_res = json.load(f)
    mu_cmp = {
        "mu_mean": mu_res.get("mu_mean"),
        "mu_variance": mu_res.get("mu_variance"),
        "mu_max_abs_z_adequate": mu_res["permutation_null_summary"]["observed_max_abs_z_adequate_strata"],
        "mu_p_adeq": mu_res["permutation_null_summary"]["p_value_adequate_strata"],
        "mu_verdict": mu_res.get("verdict"),
        "mu_per_stratum_z": {k: v["z"] for k, v in mu_res.get("per_aut_grp", {}).items()},
    }
except Exception as e:
    mu_cmp = {"error": str(e)}


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
if obs_max_adeq > 3.0 and p_adeq < 0.01:
    verdict = "LIOUVILLE_RESCUES_H85"
    reading = ("Liouville gives |z| >> 0.39 with low permutation-null p. The original H85 |z|=6.15 "
               "is consistent with λ, not μ. F012 kill should be rescinded; tensor entry needs "
               "'coordinate system: Liouville-on-abs_disc' added to the F012 row.")
elif obs_max_adeq > 2.0:
    verdict = "LIOUVILLE_PARTIAL"
    reading = "Liouville lifts |z| above noise but not to H85's claimed 6.15. Worth further audit."
else:
    verdict = "F012_KILL_CONFIRMED_ACROSS_DEFINITIONS"
    reading = ("Liouville agrees with Möbius: no significant per-stratum signal. The H85 |z|=6.15 "
               "cannot be reproduced under either definition. F012 kill is definitional-independent. "
               "Tensor entry for F012 should be demoted; the |z|=6.15 number came from a different "
               "subset, a different scorer, or was never reproducible.")


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------
output = {
    "specimen_id": "F012_liouville",
    "specimen_label": "H85 Möbius-vs-Liouville definitional audit",
    "completed_by": "Harmonia_M2_sessionB",
    "n_curves": len(curves),
    "n_unique_discs": len(disc_to_lam),
    "scorer": "Liouville λ(n) = (-1)^Ω(n)",
    "lam_mean": lam_mean,
    "lam_variance": lam_var,
    "lam_distribution": {
        "+1": int((lam_vals == 1).sum()),
        "-1": int((lam_vals == -1).sum()),
        "0": 0,  # Liouville never zero
    },
    "min_n_per_stratum_threshold": MIN_N_PER_STRATUM,
    "per_aut_grp": {
        lbl: {
            "n": s["n"],
            "signed_sum_lam": s["signed_sum_lam"],
            "z": s["z"],
            "n_adequate": bool(s["n"] >= MIN_N_PER_STRATUM),
        }
        for lbl, s in baseline.items()
    },
    "permutation_null_summary": {
        "n_perm": N_PERM,
        "seed": SEED,
        "observed_max_abs_z_all": obs_max_all,
        "observed_max_abs_z_adequate": obs_max_adeq,
        "observed_carrier_stratum": obs_carrier,
        "null_adequate_p99": float(np.percentile(null_max_adeq, 99)),
        "null_adequate_mean": float(null_max_adeq.mean()),
        "null_adequate_std": float(null_max_adeq.std()),
        "p_value_adequate": p_adeq,
        "p_value_all": p_all,
    },
    "comparison_vs_mobius": mu_cmp,
    "definitional_drift_delta": {
        "mu_observed_max_abs_z_adeq": mu_cmp.get("mu_max_abs_z_adequate") if isinstance(mu_cmp, dict) and "mu_max_abs_z_adequate" in mu_cmp else None,
        "lam_observed_max_abs_z_adeq": obs_max_adeq,
        "delta_abs_z": (obs_max_adeq - mu_cmp.get("mu_max_abs_z_adequate")) if (isinstance(mu_cmp, dict) and "mu_max_abs_z_adequate" in mu_cmp and mu_cmp.get("mu_max_abs_z_adequate") is not None) else None,
    },
    "verdict": verdict,
    "reading": reading,
    "notes": [
        "Liouville λ(n) is always ±1 (unlike μ which is 0 on non-squarefree n).",
        "Using SAME seed and SAME permutation-null structure as sessionB wsw_F012 for apples-to-apples comparison.",
        "If H85's |z|=6.15 came from a different subset (e.g. rank-restricted, CM-only), neither this test nor the prior μ test would find it; that is a separate DATA-FRAME hypothesis not addressed here.",
    ],
}

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with OUT_PATH.open("w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n===== VERDICT: {verdict} =====")
print(reading)
print(f"Wrote: {OUT_PATH}")
