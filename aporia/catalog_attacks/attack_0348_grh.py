"""CAT-MATH-0348 — low-lying zeros of the degree-1 Dirichlet family (spec ELENCHUS-CORRECTED).

Cardinality FIRST (P58 rule): sample rows via TABLESAMPLE + the P49 degree index,
record n, zeros-per-row, conductor range BEFORE the statistic. Then the Katz-Sarnak
qualitative signature: self-dual (real character -> symplectic) unfolded first-zero
heights vs non-self-dual (unitary), permutation test on the median difference.
A PASS characterizes the STORED data; GRH is untouched and untouchable here.
"""
from __future__ import annotations
import json
import math
import pathlib
import time

import numpy as np
import psycopg2

OUT = pathlib.Path(__file__).parent / "attack_0348_results.json"

t0 = time.time()
conn = psycopg2.connect(host="localhost", port=5432, dbname="lmfdb", user="postgres")
cur = conn.cursor()
cur.execute("SET statement_timeout='300s'")
cur.execute("""
  SELECT conductor::numeric, self_dual::boolean, positive_zeros::text
  FROM public.lfunc_lfunctions TABLESAMPLE SYSTEM (0.2)
  WHERE degree::int = 1 AND positive_zeros IS NOT NULL AND conductor::numeric > 1
  LIMIT 6000""")
rows = cur.fetchall()
conn.close()
print(f"sampled {len(rows)} deg-1 rows in {time.time()-t0:.1f}s")

# ---- cardinality record (BEFORE the statistic) ----
zeros_per_row = []
parsed = []
for q, sd, zt in rows:
    try:
        zs = json.loads(zt)
    except Exception:
        continue
    if zs:
        zeros_per_row.append(len(zs))
        parsed.append((float(q), bool(sd), float(zs[0])))
zpr = np.array(zeros_per_row)
qs = np.array([p[0] for p in parsed])
card = {"rows_sampled": len(rows), "rows_parsed": len(parsed),
        "zeros_per_row": {"min": int(zpr.min()), "median": float(np.median(zpr)),
                          "max": int(zpr.max())},
        "conductor_range": [float(qs.min()), float(qs.max())],
        "n_self_dual": int(sum(1 for p in parsed if p[1])),
        "n_non_self_dual": int(sum(1 for p in parsed if not p[1]))}
print("CARDINALITY:", card)

# ---- statistic: unfolded first-zero height by symmetry type ----
u1_sd, u1_ns = [], []
for q, sd, g1 in parsed:
    u1 = g1 * math.log(q) / (2 * math.pi)     # stated approximate unfolding
    (u1_sd if sd else u1_ns).append(u1)
u1_sd, u1_ns = np.array(u1_sd), np.array(u1_ns)
d_real = float(np.median(u1_sd) - np.median(u1_ns))
print(f"median unfolded first zero: self-dual {np.median(u1_sd):.4f} "
      f"vs non-self-dual {np.median(u1_ns):.4f}  (diff {d_real:+.4f})")

rng = np.random.default_rng(20260862)
allv = np.concatenate([u1_sd, u1_ns])
nA = len(u1_sd)
count = 0
NPERM = 10_000
for _ in range(NPERM):
    perm = rng.permutation(allv)
    if float(np.median(perm[:nA]) - np.median(perm[nA:])) >= d_real:
        count += 1
p_perm = count / NPERM
print(f"permutation P(diff >= observed | no split) = {p_perm:.4f}  ({NPERM} perms)")

OUT.write_text(json.dumps({"cardinality": card,
    "median_u1_self_dual": float(np.median(u1_sd)),
    "median_u1_non_self_dual": float(np.median(u1_ns)),
    "median_diff": d_real, "n_perm": NPERM, "p_perm": p_perm,
    "unfolding": "u1 = gamma1 * log(q) / (2*pi), stated approximation"},
    indent=1), encoding="utf-8")
print(f"-> {OUT.name}")
