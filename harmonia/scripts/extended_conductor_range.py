"""
Extended Conductor Range Test + Conductor Factorization Confound

Attack surfaces from frontier review:
  A) Does the signal persist at conductor > 50,000?
  B) Does conductor prime factorization structure explain the coupling?
  C) Does the N^(-1/2) scaling hold or collapse at large N?

Uses LMFDB Postgres for conductor > 50,000 data.
"""
import numpy as np
import json
import psycopg2
from pathlib import Path
from scipy.stats import spearmanr
from collections import defaultdict

print("EXTENDED CONDUCTOR RANGE + FACTORIZATION CONFOUND")
print("=" * 60)

# ---- Pull large-conductor data from LMFDB ----
print("Querying LMFDB Postgres for conductor range 1-500,000...")
conn = psycopg2.connect(host="devmirror.lmfdb.xyz", port=5432, dbname="lmfdb",
                         user="lmfdb", password="lmfdb", connect_timeout=30)
cur = conn.cursor()

# Get ec_curvedata with class_size
cur.execute("""
    SELECT lmfdb_label, conductor, class_size, rank, cm
    FROM ec_curvedata
    WHERE conductor <= 500000
      AND class_size IS NOT NULL
    LIMIT 200000
""")
ec_rows = {r[0]: {"conductor": int(r[1]), "class_size": int(r[2]),
                    "rank": int(r[3] or 0), "cm": int(r[4] or 0)}
           for r in cur.fetchall()}
print(f"EC data from Postgres: {len(ec_rows)} curves")

# Get zeros from lfunc_lfunctions
cur.execute("""
    SELECT origin, z1, z2, z3
    FROM lfunc_lfunctions
    WHERE degree = 2 AND motivic_weight = 1
      AND z1 IS NOT NULL AND z2 IS NOT NULL AND z3 IS NOT NULL
      AND origin LIKE 'EllipticCurve/Q/%%'
    LIMIT 200000
""")
zero_rows = cur.fetchall()
print(f"L-function zeros from Postgres: {len(zero_rows)} entries")
conn.close()

# Match zeros to EC data
data = []
for origin, z1, z2, z3 in zero_rows:
    # Extract label from origin like "EllipticCurve/Q/11/a/1"
    parts = origin.replace("EllipticCurve/Q/", "").split("/")
    if len(parts) >= 3:
        label = f"{parts[0]}.{parts[1]}{parts[2]}"
    else:
        continue

    if label not in ec_rows:
        # Try alternate label formats
        continue

    ec = ec_rows[label]
    zeros = sorted([float(z) for z in [z1, z2, z3] if z is not None and float(z) > 0])
    if len(zeros) < 2:
        continue

    data.append({
        "conductor": ec["conductor"],
        "class_size": ec["class_size"],
        "rank": ec["rank"],
        "cm": ec["cm"],
        "gamma1": zeros[0],
        "spacing": zeros[1] - zeros[0] if len(zeros) > 1 else None,
    })

print(f"Matched curves with zeros: {len(data)}")

if len(data) < 100:
    print("Insufficient matched data from Postgres z1/z2/z3 columns.")
    print("Falling back to DuckDB for extended analysis...")

    import duckdb
    db = duckdb.connect(str(Path("charon/data/charon.duckdb")), read_only=True)
    rows = db.sql("""
        SELECT ec.conductor, ec.class_size, ec.rank, ec.cm,
               oz.zeros_vector
        FROM object_zeros oz
        JOIN elliptic_curves ec ON oz.object_id = ec.object_id
        WHERE oz.n_zeros_stored >= 5 AND oz.zeros_vector IS NOT NULL
              AND ec.conductor IS NOT NULL
              AND ec.class_size IS NOT NULL
    """).fetchall()
    db.close()

    data = []
    for cond, cs, rank, cm, zvec in rows:
        zeros = sorted([z for z in (zvec or []) if z is not None and z > 0])
        if len(zeros) < 2:
            continue
        data.append({
            "conductor": int(cond),
            "class_size": int(cs),
            "rank": int(rank or 0),
            "cm": int(cm or 0),
            "gamma1": zeros[0],
            "spacing": zeros[1] - zeros[0],
        })
    print(f"DuckDB fallback: {len(data)} curves")

conductors = np.array([d["conductor"] for d in data])
class_sizes = np.array([d["class_size"] for d in data])
spacings = np.array([d["spacing"] for d in data])
log_N = np.log10(np.clip(conductors, 2, None))

print(f"Conductor range: {conductors.min()} to {conductors.max()}")

# ---- EXTENDED SCALING LAW ----
print("\n" + "-" * 40)
print("EXTENDED SCALING LAW")
print("-" * 40)

# Use more conductor windows for better resolution
cond_edges = np.logspace(np.log10(max(10, conductors.min())),
                          np.log10(conductors.max()), 25)
windows = []
for i in range(len(cond_edges) - 1):
    mask = (conductors >= cond_edges[i]) & (conductors < cond_edges[i + 1])
    if mask.sum() < 50:
        continue
    rho, p = spearmanr(spacings[mask], class_sizes[mask])
    windows.append({
        "cond_lo": float(cond_edges[i]),
        "cond_hi": float(cond_edges[i + 1]),
        "cond_center": float(np.sqrt(cond_edges[i] * cond_edges[i + 1])),
        "n": int(mask.sum()),
        "rho": float(rho),
        "abs_rho": float(abs(rho)),
        "p": float(p),
    })

print(f"{'Conductor':>12} {'n':>8} {'rho':>8} {'p':>12}")
for w in windows:
    sig = "***" if w["p"] < 0.001 else "**" if w["p"] < 0.01 else "*" if w["p"] < 0.05 else ""
    print(f"{w['cond_center']:12.0f} {w['n']:8d} {w['rho']:8.4f} {w['p']:12.2e} {sig}")

# Fit power law on significant windows
sig_windows = [w for w in windows if w["abs_rho"] > 0.01 and w["n"] >= 50]
if len(sig_windows) >= 3:
    log_c = np.log10([w["cond_center"] for w in sig_windows])
    log_r = np.log10([w["abs_rho"] for w in sig_windows])
    coeffs = np.polyfit(log_c, log_r, 1)
    alpha = -coeffs[0]
    A = 10**coeffs[1]
    print(f"\nPower law fit: |rho| = {A:.4f} * N^(-{alpha:.4f})")
    print(f"Decay exponent alpha = {alpha:.4f}")
    print(f"Comparison to RMT prediction (alpha=0.5): deviation = {abs(alpha - 0.5):.4f}")

# ---- CONDUCTOR FACTORIZATION CONFOUND ----
print("\n" + "-" * 40)
print("CONDUCTOR FACTORIZATION CONFOUND TEST")
print("-" * 40)

def prime_factorize(n):
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

# Compute factorization features for each curve
print("Computing factorization features...")
fact_data = []
for d in data:
    factors = prime_factorize(d["conductor"])
    fact_data.append({
        "omega": len(set(factors)),     # distinct prime factors
        "Omega": len(factors),           # total prime factors (with mult)
        "largest_pf": max(factors) if factors else 1,
        "smallest_pf": min(factors) if factors else 1,
        "is_prime_cond": 1 if len(factors) == 1 and len(set(factors)) == 1 else 0,
        "is_squarefree": 1 if len(factors) == len(set(factors)) else 0,
    })

# Stratify by factorization type
omega_vals = np.array([f["omega"] for f in fact_data])
is_prime = np.array([f["is_prime_cond"] for f in fact_data])
is_sqfree = np.array([f["is_squarefree"] for f in fact_data])

print(f"\nBy number of distinct prime factors (omega):")
for om in sorted(set(omega_vals)):
    mask = omega_vals == om
    if mask.sum() < 100:
        continue
    rho, p = spearmanr(spacings[mask], class_sizes[mask])
    print(f"  omega={om}: n={mask.sum():6d}, spacing-cs rho={rho:.4f}, p={p:.2e}")

print(f"\nPrime conductor vs composite:")
for label, mask in [("Prime conductor", is_prime == 1), ("Composite conductor", is_prime == 0)]:
    if mask.sum() < 100:
        continue
    rho, p = spearmanr(spacings[mask], class_sizes[mask])
    # Also within-bin
    logN_m = log_N[mask]
    bins = np.percentile(logN_m, np.linspace(0, 100, 21))
    wrhos = []
    for b in range(20):
        bmask = (logN_m >= bins[b]) & (logN_m < bins[b + 1])
        if bmask.sum() < 20:
            continue
        r, _ = spearmanr(spacings[mask][bmask], class_sizes[mask][bmask])
        if not np.isnan(r):
            wrhos.append(r)
    wmean = np.mean(wrhos) if wrhos else 0.0
    print(f"  {label}: n={mask.sum():6d}, raw rho={rho:.4f}, within-bin rho={wmean:.4f}")

print(f"\nSquarefree vs non-squarefree conductor:")
for label, mask in [("Squarefree", is_sqfree == 1), ("Non-squarefree", is_sqfree == 0)]:
    if mask.sum() < 100:
        continue
    rho, p = spearmanr(spacings[mask], class_sizes[mask])
    logN_m = log_N[mask]
    bins = np.percentile(logN_m, np.linspace(0, 100, 21))
    wrhos = []
    for b in range(20):
        bmask = (logN_m >= bins[b]) & (logN_m < bins[b + 1])
        if bmask.sum() < 20:
            continue
        r, _ = spearmanr(spacings[mask][bmask], class_sizes[mask][bmask])
        if not np.isnan(r):
            wrhos.append(r)
    wmean = np.mean(wrhos) if wrhos else 0.0
    print(f"  {label}: n={mask.sum():6d}, raw rho={rho:.4f}, within-bin rho={wmean:.4f}")

# ---- DIRECT FACTORIZATION CONDITIONING ----
print("\n" + "-" * 40)
print("CONDITIONING ON FACTORIZATION FEATURES")
print("-" * 40)

from sklearn.linear_model import LinearRegression

fact_features = np.array([[f["omega"], f["Omega"], np.log10(max(f["largest_pf"], 2)),
                            f["is_prime_cond"], f["is_squarefree"]] for f in fact_data])

# Predict spacing from conductor + factorization
X = np.column_stack([log_N, fact_features])
reg = LinearRegression().fit(X, spacings)
resid_sp = spacings - reg.predict(X)

# Predict class_size from conductor + factorization
reg_cs = LinearRegression().fit(X, class_sizes)
resid_cs = class_sizes - reg_cs.predict(X)

# Residual correlation
rho_resid, p_resid = spearmanr(resid_sp, resid_cs)
rho_raw, _ = spearmanr(spacings, class_sizes)
print(f"Raw spacing-class_size rho: {rho_raw:.4f}")
print(f"After factorization conditioning: rho={rho_resid:.4f}, p={p_resid:.2e}")
print(f"Signal reduction: {(1 - abs(rho_resid)/abs(rho_raw))*100:.1f}%")

verdict_fact = "KILLED" if abs(rho_resid) < 0.02 or p_resid > 0.01 else "SURVIVES"
print(f"FACTORIZATION CONFOUND: {verdict_fact}")

# ---- SAVE ----
results = {
    "n_curves": len(data),
    "conductor_range": [int(conductors.min()), int(conductors.max())],
    "scaling_windows": windows,
    "power_law_alpha": float(alpha) if len(sig_windows) >= 3 else None,
    "factorization_conditioning": {
        "raw_rho": float(rho_raw),
        "residual_rho": float(rho_resid),
        "residual_p": float(p_resid),
        "reduction_pct": float((1 - abs(rho_resid)/abs(rho_raw))*100),
        "verdict": verdict_fact,
    },
}

out = Path("harmonia/results/extended_conductor_factorization.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out}")
