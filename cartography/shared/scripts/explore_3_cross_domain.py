"""Exploration 3: Cross-domain joins that were impossible yesterday."""
import sys, io, time
import numpy as np
from scipy import stats
import psycopg2
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("EXPLORATION 3: CROSS-DOMAIN JOINS — things that used to be impossible")
print("=" * 70)

# --- 3a: CM vs non-CM zero spacings ---
print("\n--- 3a: CM vs non-CM EC zero spacings ---")
conn = psycopg2.connect(host='192.168.1.176', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
cur = conn.cursor()
t0 = time.time()
cur.execute("""
SELECT ec_cm::int AS cm, ec_rank::int AS rank, positive_zeros, ec_conductor::numeric AS cond
FROM bsd_joined
WHERE positive_zeros IS NOT NULL AND positive_zeros != ''
  AND ec_conductor::numeric BETWEEN 100000 AND 500000
LIMIT 8000
""")
rows = cur.fetchall()
print(f"  Got {len(rows)} curves [{time.time()-t0:.1f}s]")

import json
cm_spacings = []
noncm_spacings = []
for cm, rank, zeros_str, cond in rows:
    try:
        zeros = json.loads(str(zeros_str))
        if len(zeros) < 5:
            continue
        z = np.array(zeros)
        gaps = np.diff(np.sort(z))
        mg = gaps.mean()
        if mg > 1e-10:
            norm = gaps / mg
            if cm != 0:
                cm_spacings.extend(norm.tolist())
            else:
                noncm_spacings.extend(norm.tolist())
    except:
        pass

if cm_spacings and noncm_spacings:
    cm_arr = np.array(cm_spacings)
    noncm_arr = np.array(noncm_spacings)
    ks, p = stats.ks_2samp(cm_arr, noncm_arr)
    print(f"  CM spacings: n={len(cm_arr)}, var={cm_arr.var():.4f}")
    print(f"  Non-CM spacings: n={len(noncm_arr)}, var={noncm_arr.var():.4f}")
    print(f"  KS test: stat={ks:.4f}, p={p:.4e}")
    if p < 0.01:
        print(f"  SIGNAL: CM and non-CM zero spacings differ at p<0.01")
    else:
        print(f"  NULL: indistinguishable")
else:
    print("  Insufficient data for comparison")

# --- 3b: Knot signature vs determinant bounds ---
conn2 = psycopg2.connect(host='192.168.1.176', port=5432, dbname='prometheus_sci',
                         user='postgres', password='prometheus')
cur2 = conn2.cursor()
print("\n--- 3b: Knot signature vs determinant (Murasugi bound) ---")
t0 = time.time()
cur2.execute("""
SELECT name, crossing_number, signature, determinant
FROM topology.knots
WHERE signature IS NOT NULL AND determinant IS NOT NULL
  AND determinant > 0
""")
knots = cur2.fetchall()
print(f"  {len(knots)} knots with signature + determinant [{time.time()-t0:.1f}s]")

# Murasugi: |sigma(K)| <= 2*g(K) where g is genus
# For 4-genus: signature is bounded by 2 * signature bound
sig_abs = []
det_vals = []
sig_vs_det = []
for name, cn, sig, det in knots:
    if cn and det and sig is not None:
        sig_abs.append(abs(sig))
        det_vals.append(det)
        # A known relation: sigma(K) mod 4 relates to det(K) mod 4
        sig_vs_det.append((abs(sig), det))

sig_arr = np.array(sig_abs)
det_arr = np.array(det_vals)
print(f"  |signature|: mean={sig_arr.mean():.2f}, max={sig_arr.max()}")
print(f"  determinant: mean={det_arr.mean():.1f}, max={det_arr.max()}")

# Spearman correlation
rho, p = stats.spearmanr(sig_arr, det_arr)
print(f"  Spearman(|sig|, det): rho={rho:.4f}, p={p:.4e}")

# A mathematical prediction: det(K) >= |sigma(K)| + 1 for alternating knots
# Count violations (should be zero for alternating knots)
# But we don't have alternating flag — check global
violations = sum(1 for s, d in sig_vs_det if d < s + 1 and d > 0)
print(f"  det < |sig| + 1: {violations}/{len(sig_vs_det)} ({violations/len(sig_vs_det)*100:.2f}%)")
print(f"  (Known: violated for non-alternating knots)")

# --- 3c: Space group → QM9 via spacegroup proxy ---
# No direct join, but we can compare band gap distribution in high-sym vs low-sym materials
# and check if QM9 molecules show any analogous clustering
print("\n--- 3c: Crystal symmetry vs molecular properties (indirect) ---")
t0 = time.time()

# High-sym crystals: sg in cubic system (195-230)
# Low-sym: triclinic (1-2)
cur2.execute("""
SELECT
  CASE WHEN spacegroup_number BETWEEN 195 AND 230 THEN 'cubic'
       WHEN spacegroup_number BETWEEN 1 AND 2 THEN 'triclinic'
       ELSE 'other' END AS sym_class,
  AVG(band_gap) AS mean_gap, STDDEV(band_gap) AS std_gap,
  AVG(density) AS mean_density, COUNT(*) AS n
FROM physics.materials
WHERE band_gap IS NOT NULL
GROUP BY sym_class
ORDER BY sym_class
""")
print(f"  Crystal symmetry classes [{time.time()-t0:.1f}s]:")
for sym, mg, sg, dens, n in cur2.fetchall():
    mg_str = f"{mg:.3f}" if mg is not None else "nan"
    sg_str = f"{sg:.3f}" if sg is not None else "nan"
    dens_str = f"{dens:.3f}" if dens is not None else "nan"
    print(f"    {sym}: mean_gap={mg_str}, std={sg_str}, mean_density={dens_str}, n={n}")

# QM9: molecules can't have a space group, but HOMO-LUMO gap analogue to band gap
cur2.execute("""
SELECT AVG(homo_lumo_gap) AS mean_gap, STDDEV(homo_lumo_gap) AS std_gap, COUNT(*) AS n
FROM chemistry.qm9
WHERE homo_lumo_gap IS NOT NULL
""")
mg, sg, n = cur2.fetchone()
print(f"  QM9 HOMO-LUMO: mean={mg:.3f}, std={sg:.3f}, n={n}")

print("\nEXPLORATION 3 COMPLETE")
conn.close(); conn2.close()
