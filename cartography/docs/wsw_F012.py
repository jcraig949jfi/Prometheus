"""Weak Signal Walk — F012: Möbius bias at g2c aut groups (task wsw_F012).

Task: Run P040 (aut_grp label permutation null, 1000 shuffles) on the |z|=6.15 signal.
      Identify which aut_grp carries the signal. Check n_per_stratum >= 100.
      P023 as joint stratification for rank-mediation (EC rank — for g2c, use mw_rank).

Data source: lmfdb.g2c_curves
Projections: P022 (aut_grp stratification) × P040 (label permutation null) × P023 (rank) × P043 (bootstrap)

Output: cartography/docs/wsw_F012_results.json
"""
import json
import os
import time
from pathlib import Path

import numpy as np
import psycopg2
from sympy.ntheory import factorint

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
DB = dict(host="192.168.1.176", port=5432, dbname="lmfdb", user="lmfdb", password="lmfdb")
N_PERM = 1000
SEED = 20260417
MIN_N_PER_STRATUM = 100
OUT_PATH = Path("D:/Prometheus/cartography/docs/wsw_F012_results.json")

rng = np.random.default_rng(SEED)

# -----------------------------------------------------------------------------
# Möbius μ(n) — 0 if not squarefree, (-1)^k if squarefree with k prime factors
# -----------------------------------------------------------------------------
def mobius(n: int) -> int:
    if n <= 0:
        return 0
    if n == 1:
        return 1
    fs = factorint(n)
    for e in fs.values():
        if e >= 2:
            return 0
    return -1 if (len(fs) % 2 == 1) else 1


# -----------------------------------------------------------------------------
# Load data
# -----------------------------------------------------------------------------
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

# Parse
curves = []
for cid, aut_lbl, abs_disc_txt, mwr in rows:
    try:
        d = int(abs_disc_txt)
    except (ValueError, TypeError):
        continue
    try:
        rank = int(mwr) if mwr is not None else None
    except (ValueError, TypeError):
        rank = None
    curves.append((cid, aut_lbl, d, rank))
print(f"[parse] {len(curves)} valid curves")

# -----------------------------------------------------------------------------
# Compute Möbius per curve (cached by disc since many curves may share disc)
# -----------------------------------------------------------------------------
t0 = time.time()
disc_to_mu = {}
mu_vals = np.empty(len(curves), dtype=np.int8)
for i, (_, _, d, _) in enumerate(curves):
    if d not in disc_to_mu:
        disc_to_mu[d] = mobius(d)
    mu_vals[i] = disc_to_mu[d]
print(f"[mobius] computed on {len(disc_to_mu)} unique discs in {time.time()-t0:.1f}s")
print(f"[mobius] distribution: +1={int((mu_vals==1).sum())} -1={int((mu_vals==-1).sum())} 0={int((mu_vals==0).sum())}")

# Arrays
aut_labels = np.array([c[1] for c in curves])
ranks = np.array([c[3] if c[3] is not None else -1 for c in curves])

# Variance of μ across the whole population — used as denominator for z
mu_var = float(mu_vals.astype(np.float64).var(ddof=0))
mu_mean = float(mu_vals.astype(np.float64).mean())
print(f"[stats] mu_mean={mu_mean:.4f} mu_var={mu_var:.4f} n={len(mu_vals)}")


# -----------------------------------------------------------------------------
# Per-stratum baseline
# -----------------------------------------------------------------------------
def per_stratum_z(mu: np.ndarray, lbls: np.ndarray, mu_mean: float, mu_var: float) -> dict:
    """Per-stratum signed sum + z-score relative to iid-under-null expectation."""
    out = {}
    for lbl in np.unique(lbls):
        mask = (lbls == lbl)
        n = int(mask.sum())
        sum_mu = int(mu[mask].sum())
        # Under H0 (aut_grp independent of μ): mean = n*mu_mean, var = n*mu_var
        expected = n * mu_mean
        std = (n * mu_var) ** 0.5 if mu_var > 0 else 1.0
        z = (sum_mu - expected) / std if std > 0 else 0.0
        out[str(lbl)] = {"n": n, "signed_sum_mu": sum_mu, "z": float(z), "expected": float(expected)}
    return out


baseline = per_stratum_z(mu_vals, aut_labels, mu_mean, mu_var)
print("[baseline] per-stratum:")
for lbl, s in sorted(baseline.items(), key=lambda kv: -abs(kv[1]["z"])):
    adequate = "ADEQ" if s["n"] >= MIN_N_PER_STRATUM else "n<100"
    print(f"  {lbl:8s} n={s['n']:6d}  sum_mu={s['signed_sum_mu']:+6d}  z={s['z']:+6.2f}  [{adequate}]")

observed_max_abs_z = max(abs(s["z"]) for s in baseline.values())
observed_max_abs_z_adequate = max(
    (abs(s["z"]) for s in baseline.values() if s["n"] >= MIN_N_PER_STRATUM),
    default=0.0,
)
observed_max_stratum = max(baseline.items(), key=lambda kv: abs(kv[1]["z"]))[0]
print(f"[baseline] max |z| over ALL strata: {observed_max_abs_z:.2f} at {observed_max_stratum}")
print(f"[baseline] max |z| over ADEQUATE strata (n>=100): {observed_max_abs_z_adequate:.2f}")


# -----------------------------------------------------------------------------
# Permutation null (P040): shuffle aut_grp_label 1000x, recompute max |z|
# -----------------------------------------------------------------------------
t0 = time.time()

# For speed: vectorize per-permutation computation.
# For each aut_grp label g, we need signed-sum_mu over the shuffled assignment.
# Implementation: group-by on the shuffled labels using np.add.at.
unique_labels, label_idx = np.unique(aut_labels, return_inverse=True)
L = len(unique_labels)
ns_per_label = np.bincount(label_idx, minlength=L)

null_max_all = np.empty(N_PERM, dtype=np.float64)
null_max_adequate = np.empty(N_PERM, dtype=np.float64)
adequate_mask_labels = ns_per_label >= MIN_N_PER_STRATUM

perm_buf = label_idx.copy()
for p in range(N_PERM):
    rng.shuffle(perm_buf)
    # Sum mu by shuffled label
    sum_mu_per_label = np.bincount(perm_buf, weights=mu_vals.astype(np.float64),
                                   minlength=L)
    expected = ns_per_label * mu_mean
    std = np.sqrt(ns_per_label * mu_var)
    z = np.where(std > 0, (sum_mu_per_label - expected) / std, 0.0)
    null_max_all[p] = float(np.abs(z).max())
    if adequate_mask_labels.any():
        null_max_adequate[p] = float(np.abs(z[adequate_mask_labels]).max())
    else:
        null_max_adequate[p] = 0.0

print(f"[perm] {N_PERM} shuffles in {time.time()-t0:.1f}s")
print(f"[perm] null max|z| (ALL): mean={null_max_all.mean():.2f} std={null_max_all.std():.2f} "
      f"99th={np.percentile(null_max_all, 99):.2f}")
print(f"[perm] null max|z| (ADEQ): mean={null_max_adequate.mean():.2f} std={null_max_adequate.std():.2f} "
      f"99th={np.percentile(null_max_adequate, 99):.2f}")

# p-values
p_all = float((null_max_all >= observed_max_abs_z).sum() + 1) / (N_PERM + 1)
p_adeq = float((null_max_adequate >= observed_max_abs_z_adequate).sum() + 1) / (N_PERM + 1)


# -----------------------------------------------------------------------------
# Joint P022 × P023 — rank stratification within aut_grp for tautology check
# -----------------------------------------------------------------------------
rank_crosstab = {}
rank_mask = ranks >= 0
for lbl in unique_labels:
    m = (aut_labels == lbl) & rank_mask
    if m.sum() < MIN_N_PER_STRATUM:
        continue
    per_rank = {}
    for r_val in sorted(set(ranks[m].tolist())):
        rm = m & (ranks == r_val)
        n = int(rm.sum())
        if n == 0:
            continue
        s = int(mu_vals[rm].sum())
        exp = n * mu_mean
        std = (n * mu_var) ** 0.5 if mu_var > 0 else 1.0
        z = float((s - exp) / std) if std > 0 else 0.0
        per_rank[int(r_val)] = {"n": n, "sum_mu": s, "z": z}
    rank_crosstab[str(lbl)] = per_rank


# -----------------------------------------------------------------------------
# Bootstrap stability (P043) — resample with replacement, recompute max|z|
# -----------------------------------------------------------------------------
t0 = time.time()
N_BOOT = 1000
boot_max_abs = np.empty(N_BOOT, dtype=np.float64)
n = len(curves)
for b in range(N_BOOT):
    idx = rng.integers(0, n, size=n)
    mu_b = mu_vals[idx]
    lbl_b = label_idx[idx]
    sum_mu = np.bincount(lbl_b, weights=mu_b.astype(np.float64), minlength=L)
    ns_b = np.bincount(lbl_b, minlength=L)
    exp = ns_b * mu_mean
    std = np.sqrt(ns_b * mu_var)
    z = np.where(std > 0, (sum_mu - exp) / std, 0.0)
    boot_max_abs[b] = float(np.abs(z).max())
print(f"[boot] {N_BOOT} resamples in {time.time()-t0:.1f}s  mean|z|={boot_max_abs.mean():.2f}  5-95pct=[{np.percentile(boot_max_abs,5):.2f},{np.percentile(boot_max_abs,95):.2f}]")


# -----------------------------------------------------------------------------
# Verdict
# -----------------------------------------------------------------------------
# SURVIVES if observed exceeds 99th percentile of null AND at least one
#           stratum has n >= MIN and carries meaningful |z| (>3)
# KILLED if p_adeq >= 0.05 or all stratum |z| trivially explainable
# INCONCLUSIVE otherwise
if p_adeq < 0.01 and observed_max_abs_z_adequate > 3.0:
    verdict = "SURVIVES"
elif p_adeq >= 0.05:
    verdict = "KILLED"
else:
    verdict = "INCONCLUSIVE"

# Shape sentence
carriers = [
    (lbl, s) for lbl, s in baseline.items()
    if s["n"] >= MIN_N_PER_STRATUM and abs(s["z"]) > 2.0
]
carriers.sort(key=lambda kv: -abs(kv[1]["z"]))
if carriers:
    shape = (f"Signal carried by {len(carriers)} adequate stratum/strata. "
             f"Top: {carriers[0][0]} (n={carriers[0][1]['n']}, z={carriers[0][1]['z']:+.2f}). "
             f"Permutation-null p (adequate-strata max|z|) = {p_adeq:.4f}.")
else:
    shape = (f"No adequate stratum carries |z|>2. Permutation-null p = {p_adeq:.4f}. "
             f"Observed max|z| over adequate strata = {observed_max_abs_z_adequate:.2f}.")


# -----------------------------------------------------------------------------
# Write output
# -----------------------------------------------------------------------------
output = {
    "specimen_id": "F012",
    "specimen_label": "Möbius bias at g2c aut groups",
    "completed_by": "Harmonia_M2_sessionB",
    "n_curves": len(curves),
    "n_unique_discs": len(disc_to_mu),
    "mu_mean": mu_mean,
    "mu_variance": mu_var,
    "mu_distribution": {
        "mu=+1": int((mu_vals == 1).sum()),
        "mu=-1": int((mu_vals == -1).sum()),
        "mu=0": int((mu_vals == 0).sum()),
    },
    "min_n_per_stratum_threshold": MIN_N_PER_STRATUM,
    "projections_used": {
        "P022": "aut_grp stratification (primary axis)",
        "P040": f"F1 label permutation null, {N_PERM} shuffles",
        "P023": "mw_rank stratification (joint with P022 for tautology check)",
        "P043": f"Bootstrap stability, {N_BOOT} resamples",
    },
    "per_aut_grp": {
        lbl: {
            "n": s["n"],
            "signed_sum_mu": s["signed_sum_mu"],
            "z": s["z"],
            "survives_perm_null": bool(abs(s["z"]) > np.percentile(null_max_all, 99)),
            "n_adequate": bool(s["n"] >= MIN_N_PER_STRATUM),
        }
        for lbl, s in baseline.items()
    },
    "permutation_null_summary": {
        "n_perm": N_PERM,
        "seed": SEED,
        "observed_max_abs_z_all_strata": observed_max_abs_z,
        "observed_max_abs_z_adequate_strata": observed_max_abs_z_adequate,
        "observed_carrier_stratum": observed_max_stratum,
        "null_max_abs_z_all": {
            "mean": float(null_max_all.mean()),
            "std": float(null_max_all.std()),
            "median": float(np.median(null_max_all)),
            "p99": float(np.percentile(null_max_all, 99)),
        },
        "null_max_abs_z_adequate_only": {
            "mean": float(null_max_adequate.mean()),
            "std": float(null_max_adequate.std()),
            "median": float(np.median(null_max_adequate)),
            "p99": float(np.percentile(null_max_adequate, 99)),
        },
        "p_value_all_strata": p_all,
        "p_value_adequate_strata": p_adeq,
    },
    "bootstrap_summary_P043": {
        "n_boot": N_BOOT,
        "mean_max_abs_z": float(boot_max_abs.mean()),
        "p5": float(np.percentile(boot_max_abs, 5)),
        "p95": float(np.percentile(boot_max_abs, 95)),
    },
    "rank_crosstab_P023xP022": rank_crosstab,
    "verdict": verdict,
    "shape_summary": shape,
    "notes": [
        "Möbius μ(n) computed via sympy.factorint on abs_disc; 0 if n not squarefree, (-1)^k otherwise.",
        "Stratum adequacy threshold: n >= 100 per aut_grp_label. Only 2.1 and 4.2 meet this.",
        "Rank is mw_rank (Mordell-Weil rank of the Jacobian) per task P023 joint-stratification instruction.",
        "Baseline z uses normal approximation with population μ-variance as denominator (Lindeberg-CLT valid given mu_var > 0 and n large).",
    ],
}

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with OUT_PATH.open("w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n=== VERDICT: {verdict} ===")
print(f"Shape: {shape}")
print(f"Wrote: {OUT_PATH}")
