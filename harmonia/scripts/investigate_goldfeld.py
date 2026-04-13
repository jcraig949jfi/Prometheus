"""
Goldfeld Anomaly Investigation

Average rank = 0.738 at large conductor, trending AWAY from predicted 0.5.
Questions:
  1. Is this a sampling bias in LMFDB? (more rank-1 curves catalogued?)
  2. Are rank-2+ curves driving the average up?
  3. What's the rank-0 fraction trend? (Goldfeld really predicts 50% rank-0)
  4. Does it depend on parity (even vs odd conductor)?
  5. What does the trend look like per-isogeny-class? (one curve per class)
"""
import numpy as np
import json
import psycopg2
from pathlib import Path
from collections import Counter

print("GOLDFELD ANOMALY INVESTIGATION")
print("=" * 60)
print("Why is average rank 0.738 instead of 0.5 at large N?")
print()

conn = psycopg2.connect(host="devmirror.lmfdb.xyz", port=5432, dbname="lmfdb",
                         user="lmfdb", password="lmfdb", connect_timeout=30)
cur = conn.cursor()

# ---- Fine-grained conductor trend ----
print("TEST 1: Fine-grained conductor trend")
print("-" * 40)

cur.execute("""
    SELECT conductor, rank, class_size, lmfdb_iso
    FROM ec_curvedata
    WHERE rank IS NOT NULL AND conductor <= 500000
    ORDER BY conductor
""")
all_rows = cur.fetchall()
print(f"Total curves: {len(all_rows):,}")

conductors = np.array([r[0] for r in all_rows])
ranks = np.array([r[1] for r in all_rows])
class_sizes = np.array([r[2] or 1 for r in all_rows])
iso_classes = [r[3] for r in all_rows]

# Fine conductor bins (30 log-spaced bins)
cond_edges = np.logspace(1, np.log10(500000), 31)
print(f"\n{'Conductor':>12} {'n':>10} {'avg rank':>10} {'% r=0':>8} {'% r=1':>8} {'% r>=2':>8}")
print("-" * 60)

trend_data = []
for i in range(len(cond_edges) - 1):
    mask = (conductors >= cond_edges[i]) & (conductors < cond_edges[i + 1])
    if mask.sum() < 100:
        continue
    n = mask.sum()
    avg_r = np.mean(ranks[mask])
    pct0 = np.mean(ranks[mask] == 0) * 100
    pct1 = np.mean(ranks[mask] == 1) * 100
    pct2p = np.mean(ranks[mask] >= 2) * 100
    center = np.sqrt(cond_edges[i] * cond_edges[i + 1])
    print(f"{center:12.0f} {n:10,} {avg_r:10.4f} {pct0:7.1f}% {pct1:7.1f}% {pct2p:7.1f}%")
    trend_data.append({
        "conductor_center": float(center),
        "n": int(n),
        "avg_rank": float(avg_r),
        "pct_rank_0": float(pct0),
        "pct_rank_1": float(pct1),
        "pct_rank_ge2": float(pct2p),
    })


# ---- TEST 2: One curve per isogeny class ----
print("\nTEST 2: One curve per isogeny class (remove isogenous duplicates)")
print("-" * 40)
print("Each isogeny class shares the same L-function and rank.")
print("Multiple curves per class inflate the count without adding information.")

# Keep only the first curve per isogeny class
seen_iso = set()
unique_rows = []
for cond, rank, cs, iso in zip(conductors, ranks, class_sizes, iso_classes):
    if iso not in seen_iso:
        seen_iso.add(iso)
        unique_rows.append((cond, rank))

u_cond = np.array([r[0] for r in unique_rows])
u_rank = np.array([r[1] for r in unique_rows])
print(f"Unique isogeny classes: {len(unique_rows):,} (from {len(all_rows):,} curves)")
print(f"Average rank (all curves): {np.mean(ranks):.4f}")
print(f"Average rank (one per class): {np.mean(u_rank):.4f}")

print(f"\n{'Conductor':>12} {'n_classes':>10} {'avg rank':>10} {'% r=0':>8}")
print("-" * 44)
for i in range(len(cond_edges) - 1):
    mask = (u_cond >= cond_edges[i]) & (u_cond < cond_edges[i + 1])
    if mask.sum() < 50:
        continue
    center = np.sqrt(cond_edges[i] * cond_edges[i + 1])
    print(f"{center:12.0f} {mask.sum():10,} {np.mean(u_rank[mask]):10.4f} {np.mean(u_rank[mask] == 0)*100:7.1f}%")


# ---- TEST 3: Rank-2+ contribution ----
print("\nTEST 3: Rank-2+ contribution to average")
print("-" * 40)

rank_dist = Counter(ranks)
total = len(ranks)
print(f"Rank distribution:")
for r in sorted(rank_dist.keys()):
    print(f"  rank {r}: {rank_dist[r]:,} ({rank_dist[r]/total*100:.3f}%)")

avg_without_2plus = np.mean(ranks[ranks <= 1])
print(f"\nAverage rank (all): {np.mean(ranks):.4f}")
print(f"Average rank (rank 0-1 only): {avg_without_2plus:.4f}")
print(f"Rank-2+ fraction: {np.mean(ranks >= 2)*100:.2f}%")
print(f"Rank-2+ contribution to average: {np.mean(ranks) - avg_without_2plus * np.mean(ranks <= 1):.4f}")


# ---- TEST 4: Even vs odd conductor ----
print("\nTEST 4: Even vs odd conductor")
print("-" * 40)

even_mask = conductors % 2 == 0
odd_mask = conductors % 2 == 1
print(f"Even conductor: n={even_mask.sum():,}, avg rank={np.mean(ranks[even_mask]):.4f}, % r=0={np.mean(ranks[even_mask]==0)*100:.1f}%")
print(f"Odd conductor:  n={odd_mask.sum():,}, avg rank={np.mean(ranks[odd_mask]):.4f}, % r=0={np.mean(ranks[odd_mask]==0)*100:.1f}%")

# Prime vs composite conductor
cur.execute("""
    SELECT conductor, rank FROM ec_curvedata
    WHERE rank IS NOT NULL AND conductor <= 500000
      AND conductor IN (
          SELECT DISTINCT level FROM mf_newforms WHERE level <= 500000
      )
""")
# Just use a simple primality check
from sympy import isprime
prime_mask = np.array([isprime(int(c)) for c in conductors[:50000]])  # limit for speed
print(f"\nPrime conductor (first 50K): avg rank={np.mean(ranks[:50000][prime_mask]):.4f}")
print(f"Composite conductor (first 50K): avg rank={np.mean(ranks[:50000][~prime_mask]):.4f}")


# ---- TEST 5: Is this a database completeness artifact? ----
print("\nTEST 5: Database completeness")
print("-" * 40)

# How many curves per conductor?
cond_counts = Counter(conductors)
conductors_with_many = sum(1 for c, n in cond_counts.items() if n > 10)
conductors_with_few = sum(1 for c, n in cond_counts.items() if n <= 2)
print(f"Conductors with >10 curves: {conductors_with_many:,}")
print(f"Conductors with <=2 curves: {conductors_with_few:,}")

# At large conductor, is the database biased toward certain types?
for crange in [(1, 1000), (1000, 10000), (10000, 100000), (100000, 500000)]:
    mask = (conductors >= crange[0]) & (conductors < crange[1])
    n_conds = len(set(conductors[mask]))
    n_curves = mask.sum()
    print(f"  N in [{crange[0]:,}, {crange[1]:,}): {n_conds:,} distinct conductors, "
          f"{n_curves:,} curves, {n_curves/max(n_conds,1):.1f} curves/conductor")

conn.close()

# ---- SUMMARY ----
print("\n" + "=" * 60)
print("GOLDFELD INVESTIGATION SUMMARY")
print("=" * 60)

# The key question: is the trend real or an artifact?
if np.mean(u_rank) < np.mean(ranks):
    print("One-per-class average is LOWER than all-curves average.")
    print("Isogenous duplicates inflate the count but not the rank distribution.")

# Check if rank-0 fraction is actually trending toward 50%
r0_early = trend_data[0]["pct_rank_0"] if trend_data else 0
r0_late = trend_data[-1]["pct_rank_0"] if trend_data else 0
if r0_late < r0_early:
    print(f"Rank-0 fraction: {r0_early:.1f}% (small N) -> {r0_late:.1f}% (large N)")
    print("TREND: rank-0 fraction DECREASING with conductor (opposite Goldfeld)")
else:
    print("Rank-0 fraction increasing — consistent with Goldfeld approaching 50%")

results = {
    "overall_avg_rank": float(np.mean(ranks)),
    "one_per_class_avg_rank": float(np.mean(u_rank)),
    "n_curves": len(all_rows),
    "n_unique_classes": len(unique_rows),
    "rank_distribution": {str(k): int(v) for k, v in sorted(rank_dist.items())},
    "trend": trend_data,
}

out = Path("harmonia/results/goldfeld_investigation.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out}")
