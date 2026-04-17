"""Exploration 1: GUE deviation redemption. Properly unfold zeros this time."""
import sys, io, json, time
import numpy as np
from scipy import stats
import psycopg2
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("EXPLORATION 1: GUE DEVIATION — PROPER UNFOLDING")
print("=" * 70)

conn = psycopg2.connect(host='192.168.1.176', port=5432, dbname='prometheus_fire',
                        user='postgres', password='prometheus')
cur = conn.cursor()

# Pull zeros with conductor + root_number from object_zeros joined with registry
print("\nPulling zero data from prometheus_fire...")
t0 = time.time()
cur.execute("""
SELECT z.object_id, z.zeros_vector, z.root_number, z.analytic_rank
FROM zeros.object_zeros z
WHERE array_length(z.zeros_vector, 1) >= 10
LIMIT 10000
""")
rows = cur.fetchall()
print(f"Got {len(rows)} curves with >= 10 zeros in {time.time()-t0:.1f}s")

if not rows:
    print("No data. Bailing.")
    sys.exit(0)

# Also pull conductor via object_registry
object_ids = [r[0] for r in rows]
cur.execute("""
SELECT object_id, object_type, label, metadata->>'conductor' AS conductor
FROM xref.object_registry
WHERE object_id = ANY(%s)
""", (object_ids,))
reg_map = {r[0]: (r[1], r[2], r[3]) for r in cur.fetchall()}
print(f"Registry matches: {len(reg_map)}")

# Build dataset
data = []
for obj_id, zeros, rn, rank in rows:
    reg = reg_map.get(obj_id)
    if reg:
        obj_type, label, cond = reg
        try:
            cond = float(cond) if cond else None
        except:
            cond = None
        data.append({
            'id': obj_id,
            'type': obj_type,
            'label': label,
            'conductor': cond,
            'rank': rank or 0,
            'root_number': rn,
            'zeros': np.array(zeros, dtype=np.float64),
        })
print(f"Dataset: {len(data)} curves with registry metadata")

# Group by object_type
by_type = {}
for d in data:
    by_type.setdefault(d['type'], []).append(d)
for t, ds in by_type.items():
    print(f"  {t}: {len(ds)}")

# Pick EC curves for unfolding analysis
ec_data = by_type.get('ec_curve', by_type.get('elliptic_curve', []))
if not ec_data:
    ec_data = data  # fallback

print(f"\n=== UNFOLDING: N(T) = T/(2pi) * log(T*sqrt(N)/(2pi*e)) for GL(2) L-fcns ===")

# For EC L-functions at height T, expected zero density is:
# rho(T) ~ (1/(2pi)) * log(N*T^2/(4pi^2)) where N is conductor
# Unfolded zeros: tilde_gamma_j = integral_0^gamma_j rho(T) dT
# Approximation: tilde_gamma_j ~ (gamma_j / (2pi)) * log(N * gamma_j^2 / (4*pi^2*e^2))

def unfold_zeros(zeros, conductor):
    """Unfold imaginary parts using GL(2) density formula."""
    if conductor is None or conductor <= 0:
        return None
    out = []
    for g in zeros:
        if g <= 0:
            continue
        # Riemann-von Mangoldt type formula for degree-2 L-function
        arg = conductor * g * g / (4 * np.pi * np.pi)
        if arg <= 0:
            continue
        tilde = (g / (2 * np.pi)) * (np.log(arg) - 2)
        if tilde > 0:
            out.append(tilde)
    return np.array(out) if out else None

raw_spacings = []
unfolded_spacings = []
for d in ec_data:
    if d['conductor'] is None or d['conductor'] < 10:
        continue
    raw = d['zeros']
    unf = unfold_zeros(raw, d['conductor'])
    if unf is None or len(unf) < 3:
        continue

    # Raw spacings (normalized by mean gap)
    raw_g = np.diff(np.sort(raw))
    if len(raw_g) > 0 and raw_g.mean() > 1e-10:
        raw_spacings.extend((raw_g / raw_g.mean()).tolist())

    # Unfolded spacings (mean gap should be ~1 automatically)
    unf_g = np.diff(np.sort(unf))
    if len(unf_g) > 0:
        unfolded_spacings.extend(unf_g.tolist())

raw_spacings = np.array(raw_spacings)
unfolded_spacings = np.array(unfolded_spacings)

print(f"\nRaw spacings: n={len(raw_spacings)}")
print(f"  mean={raw_spacings.mean():.4f} (should be ~1.0 after normalization)")
print(f"  var={raw_spacings.var():.4f} (GUE Wigner = 0.178)")

print(f"\nUnfolded spacings: n={len(unfolded_spacings)}")
if len(unfolded_spacings) > 0:
    print(f"  mean={unfolded_spacings.mean():.4f}")
    print(f"  var={unfolded_spacings.var():.4f}")

# Variance z-scores
GUE_VAR = 0.178
if len(raw_spacings) > 0:
    se_raw = raw_spacings.std() / np.sqrt(len(raw_spacings))
    z_raw = (raw_spacings.var() - GUE_VAR) / (2 * raw_spacings.var() / np.sqrt(len(raw_spacings)))
    print(f"\n  Raw variance z-score vs GUE: {z_raw:.2f}")

# KS test
if len(unfolded_spacings) > 10:
    # Normalize unfolded to unit mean
    normalized = unfolded_spacings / unfolded_spacings.mean()
    # Wigner CDF
    def wigner_cdf(s):
        return 1 - np.exp(-4 * s**2 / np.pi)
    sorted_s = np.sort(normalized)
    ecdf = np.arange(1, len(sorted_s) + 1) / len(sorted_s)
    theoretical = wigner_cdf(sorted_s)
    ks = np.max(np.abs(ecdf - theoretical))
    print(f"\n  KS statistic (unfolded vs Wigner): {ks:.4f}")
    p_ks = stats.kstwobign.sf(ks * np.sqrt(len(sorted_s)))
    print(f"  KS p-value: {p_ks:.4e}")

# VERDICT
print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)
raw_var = raw_spacings.var() if len(raw_spacings) > 0 else 0
unf_var_norm = (unfolded_spacings / unfolded_spacings.mean()).var() if len(unfolded_spacings) > 0 else 0

print(f"  Raw spacings variance: {raw_var:.4f}")
print(f"  Unfolded+normalized variance: {unf_var_norm:.4f}")
print(f"  GUE Wigner target: {GUE_VAR:.4f}")

if abs(unf_var_norm - GUE_VAR) < 0.01:
    print(f"\n  REDEMPTION: After proper unfolding, variance matches GUE.")
    print(f"  Yesterday's z=-19.26 was an UNFOLDING ARTIFACT.")
elif unf_var_norm < GUE_VAR - 0.01:
    print(f"\n  SURVIVES: Even after unfolding, variance is below GUE.")
    print(f"  Deviation: {GUE_VAR - unf_var_norm:.4f} below GUE prediction.")
    print(f"  This is REAL fine structure.")
else:
    print(f"\n  UNCLEAR: Unfolded variance differs from raw AND from GUE.")

conn.close()
