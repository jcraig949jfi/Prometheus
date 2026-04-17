"""Exploration 2: Extremes tour — weirdest object in each domain."""
import sys, io, time
import psycopg2
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("EXPLORATION 2: EXTREMES TOUR — weirdest objects in each domain")
print("=" * 70)

# EC: extreme leading_term/conductor ratios (from bsd_joined)
print("\n--- EC: most extreme L^(r)(1)/r! per conductor ---")
conn = psycopg2.connect(host='192.168.1.176', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
cur = conn.cursor()
t0 = time.time()
cur.execute("""
SELECT ec_label, ec_rank, ec_conductor::numeric AS cond, leading_term::numeric AS lt
FROM bsd_joined
WHERE leading_term IS NOT NULL AND leading_term != ''
  AND ec_conductor::numeric > 0
  AND ec_rank::int <= 4
ORDER BY leading_term::numeric DESC
LIMIT 5
""")
print(f"  Top 5 largest leading_term [{time.time()-t0:.1f}s]:")
for label, rank, cond, lt in cur.fetchall():
    print(f"    {label}: rank={rank}, cond={cond:.0f}, L^(r)/r! = {float(lt):.4e}")

t0 = time.time()
cur.execute("""
SELECT ec_label, ec_rank, ec_conductor::numeric AS cond, leading_term::numeric AS lt
FROM bsd_joined
WHERE leading_term IS NOT NULL AND leading_term != ''
  AND ec_conductor::numeric > 0
  AND ec_rank::int = 0
ORDER BY leading_term::numeric ASC
LIMIT 5
""")
print(f"  Top 5 smallest leading_term for rank 0 [{time.time()-t0:.1f}s]:")
for label, rank, cond, lt in cur.fetchall():
    print(f"    {label}: rank={rank}, cond={cond:.0f}, L(1) = {float(lt):.4e}")
conn.close()

# Knots, Groups, Materials, QM9
conn = psycopg2.connect(host='192.168.1.176', port=5432, dbname='prometheus_sci',
                        user='postgres', password='prometheus')
cur = conn.cursor()

# Knots: Alexander vs Jones determinant mismatch
print("\n--- Knots: extreme Alexander-Jones disagreement ---")
t0 = time.time()
cur.execute("""
SELECT name, crossing_number, determinant, alexander_coeffs, jones_coeffs
FROM topology.knots
WHERE alexander_coeffs IS NOT NULL AND jones_coeffs IS NOT NULL
  AND array_length(jones_coeffs, 1) > 0
ORDER BY determinant DESC
LIMIT 5
""")
print(f"  Knots with largest determinant [{time.time()-t0:.1f}s]:")
for name, cn, det, alex, jones in cur.fetchall():
    print(f"    {name}: crossing={cn}, det={det}, |alex|={len(alex)}, |jones|={len(jones)}")

# Groups: n_conjugacy / sqrt(order) outliers
print("\n--- Groups: n_conjugacy / sqrt(order) outliers ---")
t0 = time.time()
cur.execute("""
SELECT label, order_val, exponent, n_conjugacy, is_abelian, is_solvable,
       n_conjugacy::float / sqrt(order_val::float) AS ratio
FROM algebra.groups
WHERE order_val::float > 100 AND order_val::float < 1e9
ORDER BY ratio DESC
LIMIT 5
""")
print(f"  Groups with highest n_conjugacy/sqrt(order) [{time.time()-t0:.1f}s]:")
for label, order, exp, ncc, abel, solv, ratio in cur.fetchall():
    print(f"    {label}: |G|={order}, n_cc={ncc}, ratio={ratio:.3f}, abelian={abel}")

cur.execute("""
SELECT label, order_val, n_conjugacy,
       n_conjugacy::float / sqrt(order_val::float) AS ratio
FROM algebra.groups
WHERE order_val::float > 100 AND order_val::float < 1e9 AND is_abelian = false
ORDER BY ratio ASC
LIMIT 5
""")
print(f"  Groups with lowest ratio (most 'concentrated' class structure):")
for label, order, ncc, ratio in cur.fetchall():
    print(f"    {label}: |G|={order}, n_cc={ncc}, ratio={ratio:.3f}")

# Materials: band gap outliers per space group
print("\n--- Materials: band gap z-score within space group ---")
t0 = time.time()
cur.execute("""
WITH sg_stats AS (
    SELECT spacegroup_number,
           AVG(band_gap) as mean_gap,
           STDDEV(band_gap) as std_gap,
           COUNT(*) as n
    FROM physics.materials
    WHERE band_gap IS NOT NULL
    GROUP BY spacegroup_number
    HAVING COUNT(*) >= 20
)
SELECT m.material_id, m.spacegroup_number, m.band_gap, s.mean_gap, s.std_gap, s.n,
       (m.band_gap - s.mean_gap) / s.std_gap AS zscore
FROM physics.materials m
JOIN sg_stats s ON m.spacegroup_number = s.spacegroup_number
WHERE s.std_gap > 0 AND m.band_gap IS NOT NULL
ORDER BY ABS((m.band_gap - s.mean_gap) / s.std_gap) DESC
LIMIT 5
""")
print(f"  Extreme band gaps (z within space group) [{time.time()-t0:.1f}s]:")
for mid, sg, bg, mean_g, std_g, n_sg, z in cur.fetchall():
    print(f"    {mid}: sg={sg}, gap={bg:.3f}eV, sg_mean={mean_g:.3f}+-{std_g:.3f} (n={n_sg}), z={z:.2f}")

# QM9: smallest HOMO-LUMO gap per atom
print("\n--- QM9: tightest HOMO-LUMO gap per atom ---")
t0 = time.time()
cur.execute("""
SELECT smiles, homo, lumo, homo_lumo_gap, n_atoms,
       homo_lumo_gap::float / n_atoms::float AS gap_per_atom
FROM chemistry.qm9
WHERE homo_lumo_gap IS NOT NULL AND n_atoms > 3
ORDER BY homo_lumo_gap::float / n_atoms::float ASC
LIMIT 5
""")
print(f"  Smallest HOMO-LUMO gap per atom [{time.time()-t0:.1f}s]:")
for smi, h, l, gap, na, gpa in cur.fetchall():
    print(f"    {smi}: HOMO={h:.3f}, LUMO={l:.3f}, gap={gap:.3f}, n_atoms={na}, gap/atom={gpa:.4f}")

cur.close(); conn.close()
print("\nEXPLORATION 2 COMPLETE")
