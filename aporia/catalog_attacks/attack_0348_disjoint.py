"""CAT-MATH-0348 DISJOINT-SLICE replication (P71) — the P67 residue executed.

Same protocol as attack_0348_powered.py (the test of record) on a slice provably
disjoint from it: ORDER BY label DESC takes the far end of the label ordering,
and a COUNT guard verifies each stratum has >= 2x the fetch limit so the DESC
head cannot overlap the committed ASC head. Labels are STORED this run so
disjointness is checkable from artifacts, not argued.

Pre-stated readings (committed BEFORE first run, binding):
  SPLIT-REPLICATES          sd median > ns median AND permutation p < 0.05
  DIRECTION-ONLY-UNDERPOWERED  direction preserved, p >= 0.05
  SPLIT-FAILS               direction reversed (sd median <= ns median)
Either way the P67 numbers stand as committed; this run speaks only to
robustness across the label space.

Unfolding imports nt_helpers (P69 module) — NOT a fresh reimplementation.
"""
from __future__ import annotations
import json
import pathlib
import sys
import time

import numpy as np
import psycopg2

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from nt_helpers import unfold_u1

OUT = pathlib.Path(__file__).parent / "attack_0348_disjoint_results.json"
LIMITS = {"sd": 800, "ns": 4000}


def q(cur, sql, args=()):
    cur.execute(sql, args)
    return cur.fetchall()


conn = psycopg2.connect(host="localhost", port=5432, dbname="lmfdb", user="postgres")
cur = conn.cursor()
cur.execute("SET statement_timeout='600s'")

BASE = ("FROM public.lfunc_lfunctions WHERE degree::int = 1 AND {w} "
        "AND positive_zeros IS NOT NULL AND conductor::numeric > 1")
WHERE = {"sd": "self_dual::boolean", "ns": "NOT self_dual::boolean"}

# --- disjointness guard: stratum counts must be >= 2x the fetch limit --------
counts = {}
for k, w in WHERE.items():
    t0 = time.time()
    counts[k] = q(cur, f"SELECT count(*) {BASE.format(w=w)}")[0][0]
    print(f"count[{k}] = {counts[k]} ({time.time()-t0:.0f}s)", flush=True)

fetch_n = {}
for k in WHERE:
    if counts[k] >= 2 * LIMITS[k]:
        fetch_n[k] = LIMITS[k]                      # DESC head provably disjoint
    else:
        fetch_n[k] = max(0, counts[k] - LIMITS[k])  # only the tail beyond ASC head
        print(f"GUARD: {k} stratum has {counts[k]} < 2x{LIMITS[k]} — "
              f"shrinking to the {fetch_n[k]}-row disjoint tail", flush=True)

data = {}
for k, w in WHERE.items():
    t0 = time.time()
    rows = q(cur, f"""
      SELECT label, conductor::numeric, positive_zeros::text
      {BASE.format(w=w)}
      ORDER BY label DESC
      LIMIT %s""", (fetch_n[k],))
    u1, labels = [], []
    for lab, cond, zt in rows:
        zs = json.loads(zt)
        if zs:
            labels.append(lab)
            u1.append(unfold_u1(float(zs[0]), float(cond)))
    data[k] = (np.array(u1), labels)
    print(f"{k}: n={len(u1)} median={np.median(u1):.4f} ({time.time()-t0:.0f}s)", flush=True)
conn.close()

sd, ns = data["sd"][0], data["ns"][0]
d = float(np.median(sd) - np.median(ns))
rng = np.random.default_rng(20260871)
allv = np.concatenate([sd, ns])
nA = len(sd)
cnt = 0
NPERM = 10_000
for _ in range(NPERM):
    p = rng.permutation(allv)
    if float(np.median(p[:nA]) - np.median(p[nA:])) >= d:
        cnt += 1
print(f"diff {d:+.4f}, permutation p = {cnt/NPERM:.4f}", flush=True)

OUT.write_text(json.dumps({
    "protocol": "ORDER BY label DESC (disjoint far end; COUNT guard), unfolding via nt_helpers.unfold_u1, seed 20260871",
    "stratum_counts": counts,
    "n_self_dual": int(len(sd)), "n_non_self_dual": int(len(ns)),
    "median_u1_self_dual": float(np.median(sd)),
    "median_u1_non_self_dual": float(np.median(ns)),
    "median_diff": d, "n_perm": NPERM, "p_perm": cnt / NPERM,
    "labels_self_dual": data["sd"][1],
    "labels_non_self_dual": data["ns"][1],
    "u1_self_dual": [round(float(x), 6) for x in sd],
    "u1_non_self_dual": [round(float(x), 6) for x in ns]}, indent=1), encoding="utf-8")
print(f"-> {OUT.name} (labels + FULL arrays stored)", flush=True)
