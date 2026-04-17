"""Exploration 5: BSD parity on bsd_joined — now fast."""
import sys, io, time
import psycopg2
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("EXPLORATION 5: BSD PARITY ON bsd_joined (2.48M rows, 1s queries)")
print("=" * 70)

conn = psycopg2.connect(host='192.168.1.176', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
cur = conn.cursor()

# Full parity sweep
t0 = time.time()
cur.execute("""
SELECT COUNT(*) AS total,
       SUM(CASE WHEN ec_rank::int = order_of_vanishing::int THEN 1 ELSE 0 END) AS rank_agree,
       SUM(CASE WHEN root_number::numeric = CASE WHEN ec_rank::int % 2 = 0 THEN 1 ELSE -1 END THEN 1 ELSE 0 END) AS parity_agree
FROM bsd_joined
WHERE ec_rank IS NOT NULL AND order_of_vanishing IS NOT NULL AND root_number IS NOT NULL
""")
total, rank_agree, parity_agree = cur.fetchone()
elapsed = time.time() - t0
print(f"\nFull bsd_joined sweep [{elapsed:.2f}s]:")
print(f"  Total: {total:,}")
print(f"  rank = analytic_rank: {rank_agree:,}/{total:,} ({rank_agree/total*100:.6f}%)")
print(f"  root_number = (-1)^rank: {parity_agree:,}/{total:,} ({parity_agree/total*100:.6f}%)")

# Break down by rank
print("\nPer-rank breakdown:")
cur.execute("""
SELECT ec_rank::int AS rank, COUNT(*) AS n,
       SUM(CASE WHEN ec_rank::int = order_of_vanishing::int THEN 1 ELSE 0 END) AS rank_ok,
       SUM(CASE WHEN root_number::numeric = CASE WHEN ec_rank::int % 2 = 0 THEN 1 ELSE -1 END THEN 1 ELSE 0 END) AS parity_ok
FROM bsd_joined
WHERE ec_rank IS NOT NULL AND order_of_vanishing IS NOT NULL AND root_number IS NOT NULL
GROUP BY ec_rank::int
ORDER BY ec_rank::int
""")
for rank, n, rok, pok in cur.fetchall():
    print(f"  rank {rank}: n={n:>10,}, rank=ov: {rok}/{n} ({rok/n*100:.4f}%), parity ok: {pok}/{n} ({pok/n*100:.4f}%)")

# Find ANY disagreement - this is the specimen hunt
t0 = time.time()
cur.execute("""
SELECT ec_label, ec_rank, ec_conductor, order_of_vanishing, root_number
FROM bsd_joined
WHERE ec_rank IS NOT NULL AND order_of_vanishing IS NOT NULL AND root_number IS NOT NULL
AND (ec_rank::int != order_of_vanishing::int
     OR root_number::numeric != CASE WHEN ec_rank::int % 2 = 0 THEN 1 ELSE -1 END)
LIMIT 20
""")
disagrees = cur.fetchall()
print(f"\nDisagreements [{time.time()-t0:.2f}s]: {len(disagrees)}")
for row in disagrees:
    print(f"  {row}")

# Rank 4, 5 — the edge cases
print("\n=== RANK 4 AND RANK 5 (the frontier) ===")
for target_rank in [4, 5]:
    cur.execute("""
    SELECT ec_label, ec_conductor::numeric AS cond, order_of_vanishing, root_number, leading_term
    FROM bsd_joined
    WHERE ec_rank::int = %s
    ORDER BY ec_conductor::numeric
    """, (target_rank,))
    rows = cur.fetchall()
    print(f"\nRank {target_rank}: {len(rows)} curves in bsd_joined")
    if rows:
        for label, cond, ov, rn, lt in rows[:5]:
            lt_str = f"{float(lt):.4e}" if lt else "None"
            print(f"  {label}: cond={cond:.0f}, ov={ov}, root#={rn}, L^({target_rank})/{target_rank}!={lt_str}")
        if len(rows) > 5:
            print(f"  ... and {len(rows)-5} more")

conn.close()
print("\nEXPLORATION 5 COMPLETE")
