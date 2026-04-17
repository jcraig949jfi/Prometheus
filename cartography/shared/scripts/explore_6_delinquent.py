"""Exploration 6: The Delinquent — EC without L-function data."""
import sys, io, time
import psycopg2
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("EXPLORATION 6: THE DELINQUENT — 747K EC without L-function data")
print("=" * 70)

conn = psycopg2.connect(host='192.168.1.176', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
cur = conn.cursor()

# Set A: all EC
# Set B: EC in bsd_joined (has L-function)
# Delinquents: A - B

t0 = time.time()
cur.execute("SELECT COUNT(DISTINCT lmfdb_iso) FROM ec_curvedata")
total_iso = cur.fetchone()[0]
cur.execute("SELECT COUNT(DISTINCT ec_iso) FROM bsd_joined")
joined_iso = cur.fetchone()[0]
print(f"\nIsogeny class coverage [{time.time()-t0:.1f}s]:")
print(f"  Total ec_curvedata isogeny classes: {total_iso:,}")
print(f"  With L-function in bsd_joined: {joined_iso:,}")
print(f"  Delinquent (no L-function): {total_iso - joined_iso:,} ({(total_iso-joined_iso)/total_iso*100:.1f}%)")

# Conductor distribution of delinquents
print("\nDelinquent conductor distribution:")
t0 = time.time()
cur.execute("""
WITH delinquent AS (
    SELECT DISTINCT e.lmfdb_iso, e.conductor::numeric AS cond
    FROM ec_curvedata e
    WHERE NOT EXISTS (
        SELECT 1 FROM bsd_joined b WHERE b.ec_iso = e.lmfdb_iso
    )
)
SELECT
  CASE
    WHEN cond < 100000 THEN '<100K'
    WHEN cond < 400000 THEN '100K-400K'
    WHEN cond < 1000000 THEN '400K-1M'
    WHEN cond < 5000000 THEN '1M-5M'
    ELSE '>5M'
  END AS band,
  COUNT(*) AS n,
  MIN(cond) AS min_cond,
  MAX(cond) AS max_cond
FROM delinquent
GROUP BY band
ORDER BY MIN(cond)
""")
for band, n, mn, mx in cur.fetchall():
    print(f"  {band}: {n:>10,} classes ({mn:.0f} to {mx:.0f})")
print(f"  [{time.time()-t0:.1f}s]")

# Rank distribution of delinquents
print("\nDelinquent rank distribution (high ranks are most interesting):")
t0 = time.time()
cur.execute("""
SELECT e.rank::int AS rank, COUNT(*) AS n
FROM ec_curvedata e
WHERE NOT EXISTS (SELECT 1 FROM bsd_joined b WHERE b.ec_iso = e.lmfdb_iso)
  AND e.rank IS NOT NULL
GROUP BY e.rank::int
ORDER BY e.rank::int
""")
print(f"  [{time.time()-t0:.1f}s]")
for rank, n in cur.fetchall():
    print(f"  rank {rank}: {n:>10,} delinquent curves")

# High-rank delinquent conductors — where L-function extension would be most valuable
print("\nHigh-rank delinquents (candidates for new L-function computation):")
t0 = time.time()
cur.execute("""
SELECT e.lmfdb_label, e.conductor::numeric AS cond, e.rank::int AS rank
FROM ec_curvedata e
WHERE NOT EXISTS (SELECT 1 FROM bsd_joined b WHERE b.ec_iso = e.lmfdb_iso)
  AND e.rank::int >= 4
ORDER BY e.conductor::numeric
LIMIT 20
""")
print(f"  [{time.time()-t0:.1f}s]")
for label, cond, rank in cur.fetchall():
    print(f"  {label}: cond={cond:.0f}, rank={rank}")

# Rank 5 delinquents specifically (19 total in database)
print("\nALL rank 5 delinquents:")
t0 = time.time()
cur.execute("""
SELECT e.lmfdb_label, e.conductor::numeric AS cond
FROM ec_curvedata e
WHERE NOT EXISTS (SELECT 1 FROM bsd_joined b WHERE b.ec_iso = e.lmfdb_iso)
  AND e.rank::int = 5
ORDER BY e.conductor::numeric
""")
rows = cur.fetchall()
print(f"  [{time.time()-t0:.1f}s] Found {len(rows)} rank-5 delinquent curves:")
for label, cond in rows:
    print(f"    {label}: cond={cond:.0f}")

# Isogeny class size patterns — are delinquents unusual?
print("\nIsogeny class size: delinquent vs covered")
t0 = time.time()
cur.execute("""
WITH delinquent AS (
    SELECT DISTINCT e.lmfdb_iso, AVG(e.class_size::int) AS avg_size
    FROM ec_curvedata e
    WHERE NOT EXISTS (SELECT 1 FROM bsd_joined b WHERE b.ec_iso = e.lmfdb_iso)
    GROUP BY e.lmfdb_iso
),
covered AS (
    SELECT DISTINCT e.lmfdb_iso, AVG(e.class_size::int) AS avg_size
    FROM ec_curvedata e
    WHERE EXISTS (SELECT 1 FROM bsd_joined b WHERE b.ec_iso = e.lmfdb_iso)
    GROUP BY e.lmfdb_iso
)
SELECT 'delinquent' AS type, AVG(avg_size) AS mean_class_size, COUNT(*) AS n FROM delinquent
UNION ALL
SELECT 'covered' AS type, AVG(avg_size) AS mean_class_size, COUNT(*) AS n FROM covered
""")
for typ, mean_sz, n in cur.fetchall():
    print(f"  {typ}: mean class size = {mean_sz:.3f}, n={n:,}")
print(f"  [{time.time()-t0:.1f}s]")

conn.close()
print("\nEXPLORATION 6 COMPLETE")
