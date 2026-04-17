"""
C-FP-1: Isospectral Drum Pairs — Kac's question applied to LMFDB.

Find EC pairs with identical L-function zeros (same Lhash) but differing
algebraic properties. These are specimens where the spectrum CANNOT see
the algebraic difference — what is the hidden invariant?

Author: Harmonia
"""
import sys, io, time, json
from collections import defaultdict
import psycopg2
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = psycopg2.connect(host='192.168.1.176', port=5432, dbname='lmfdb',
                        user='postgres', password='prometheus')
cur = conn.cursor()

print("=" * 70)
print("C-FP-1: ISOSPECTRAL DRUM PAIRS")
print("=" * 70)

# Step 1: find all Lhash groups with > 1 EC L-function
t0 = time.time()
cur.execute("""
SELECT "Lhash", COUNT(*) as n, array_agg(origin) AS origins
FROM lfunc_lfunctions
WHERE origin LIKE 'EllipticCurve/Q/%'
  AND "Lhash" IS NOT NULL
GROUP BY "Lhash"
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC
""")
groups = cur.fetchall()
print(f"\n[{time.time()-t0:.1f}s] Lhash groups with > 1 EC: {len(groups)}")

# Group-size histogram
size_hist = defaultdict(int)
for _, n, _ in groups:
    size_hist[n] += 1
print("Group size distribution:")
for sz in sorted(size_hist.keys()):
    print(f"  size {sz}: {size_hist[sz]} groups")

# Step 2: for each group, extract the EC labels and pull algebraic data
def origin_to_iso(origin):
    # origin = 'EllipticCurve/Q/conductor/iso_letter'
    parts = origin.split('/')
    if len(parts) >= 4:
        return f"{parts[2]}.{parts[3]}"
    return None

drum_pairs = []  # groups with at least 2 distinct isogeny classes
print("\nExamining top 30 groups for algebraic differences...")
t0 = time.time()
for lhash, n, origins in groups[:500]:
    # Map origins to isogeny classes
    iso_classes = list(set(origin_to_iso(o) for o in origins if origin_to_iso(o)))
    if len(iso_classes) < 2:
        continue  # all from same isogeny class (trivial)

    # Pull EC data for these isogeny classes
    cur.execute("""
    SELECT DISTINCT lmfdb_iso, conductor, rank, analytic_rank, cm, torsion, class_size
    FROM ec_curvedata
    WHERE lmfdb_iso = ANY(%s)
    """, (iso_classes,))
    rows = cur.fetchall()

    # Check for disagreement in any algebraic property
    if len(rows) < 2:
        continue

    # Aggregate attributes
    attrs = defaultdict(set)
    for iso, cond, rank, arank, cm, tor, cs in rows:
        attrs['conductor'].add(cond)
        attrs['rank'].add(rank)
        attrs['cm'].add(cm)
        attrs['torsion'].add(tor)
        attrs['class_size'].add(cs)

    # Which attributes vary?
    varying = {k: list(v) for k, v in attrs.items() if len(v) > 1}
    if varying:
        drum_pairs.append({
            'lhash': lhash,
            'iso_classes': iso_classes,
            'rows': rows,
            'varying': varying,
        })

print(f"[{time.time()-t0:.1f}s] Found {len(drum_pairs)} isospectral groups with algebraic disagreement")

# Step 3: categorize and report
if drum_pairs:
    print("\n=== DRUM PAIRS (same L-function zeros, different algebra) ===\n")

    # Sort by most interesting: most-varied properties first
    drum_pairs.sort(key=lambda d: len(d['varying']), reverse=True)

    for i, dp in enumerate(drum_pairs[:20]):
        print(f"Group {i+1}: Lhash={dp['lhash']}")
        print(f"  Isogeny classes: {dp['iso_classes']}")
        print(f"  Varying attributes:")
        for k, v in dp['varying'].items():
            print(f"    {k}: {sorted(v)}")
        print(f"  Full rows:")
        for r in dp['rows'][:4]:
            print(f"    iso={r[0]}, cond={r[1]}, rank={r[2]}, ov={r[3]}, cm={r[4]}, tor={r[5]}, cs={r[6]}")
        print()

    # Summary by disagreement type
    print("=" * 70)
    print("DISAGREEMENT TYPE SUMMARY")
    print("=" * 70)
    attr_counts = defaultdict(int)
    for dp in drum_pairs:
        for k in dp['varying']:
            attr_counts[k] += 1
    for k, n in sorted(attr_counts.items(), key=lambda x: -x[1]):
        print(f"  {k} varies across groups: {n} drum pairs")
else:
    print("\nNO DRUM PAIRS FOUND.")
    print("Every Lhash group shares complete algebraic structure.")
    print("Interpretation: Lhash is capturing the complete EC L-function fingerprint,")
    print("and the spectrum is fully determining algebraic properties (modularity working).")

# Step 4: also check CROSS-FAMILY isospectral — EC L-function matching a modular form L-function
print("\n=== CROSS-FAMILY ISOSPECTRAL (EC matching MF via Lhash) ===")
t0 = time.time()
cur.execute("""
SELECT "Lhash", array_agg(DISTINCT origin) AS origins, COUNT(*) AS n
FROM lfunc_lfunctions
WHERE "Lhash" IN (
  SELECT "Lhash" FROM lfunc_lfunctions
  WHERE origin LIKE 'EllipticCurve/Q/%' AND "Lhash" IS NOT NULL
)
AND (origin LIKE 'EllipticCurve/Q/%' OR origin LIKE 'ModularForm/%')
GROUP BY "Lhash"
HAVING COUNT(DISTINCT CASE WHEN origin LIKE 'EllipticCurve%' THEN 'ec' WHEN origin LIKE 'Modular%' THEN 'mf' END) > 1
LIMIT 10
""")
cross = cur.fetchall()
print(f"[{time.time()-t0:.1f}s] EC<->MF isospectral groups: {len(cross)}")
for lhash, origins, n in cross[:5]:
    print(f"  Lhash={lhash}: {n} L-functions")
    for o in origins[:4]:
        print(f"    {o}")

conn.close()
print("\nDONE")
