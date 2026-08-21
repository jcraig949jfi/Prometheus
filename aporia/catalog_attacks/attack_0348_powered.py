"""CAT-MATH-0348 POWERED test — committed, deterministic, reproducible.

Written P66 under ELEN-CAMPAIGN-P51-P62 (invalidates-claim): the P62 powered
test ran as an uncommitted inline command; its evidence files self-contradict
(0.9354 / 0.9602 / rows-median 0.7877). This script IS the test of record:
deterministic fetches (ORDER BY label — no TABLESAMPLE, no synchronized-scan
dependence), full u1 arrays STORED, seeded permutation test. Whatever it says
replaces every prior 0348 powered number.
"""
from __future__ import annotations
import json
import math
import pathlib
import time

import numpy as np
import psycopg2

OUT = pathlib.Path(__file__).parent / "attack_0348_powered_results.json"

def fetch(where, limit):
    conn = psycopg2.connect(host="localhost", port=5432, dbname="lmfdb", user="postgres")
    cur = conn.cursor()
    cur.execute("SET statement_timeout='600s'")
    cur.execute(f"""
      SELECT conductor::numeric, positive_zeros::text
      FROM public.lfunc_lfunctions
      WHERE degree::int = 1 AND {where} AND positive_zeros IS NOT NULL
            AND conductor::numeric > 1
      ORDER BY label
      LIMIT {limit}""")
    rows = cur.fetchall()
    conn.close()
    out = []
    for q, zt in rows:
        zs = json.loads(zt)
        if zs:
            out.append(float(zs[0]) * math.log(float(q)) / (2 * math.pi))
    return np.array(out)

t0 = time.time()
sd = fetch("self_dual::boolean", 800)
print(f"self-dual: n={len(sd)} median={np.median(sd):.4f} ({time.time()-t0:.0f}s)", flush=True)
t0 = time.time()
ns = fetch("NOT self_dual::boolean", 4000)
print(f"non-self-dual: n={len(ns)} median={np.median(ns):.4f} ({time.time()-t0:.0f}s)", flush=True)

d = float(np.median(sd) - np.median(ns))
rng = np.random.default_rng(20260866)
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
    "protocol": "ORDER BY label (deterministic), unfolding u1=gamma1*log(q)/(2pi), seed 20260866",
    "n_self_dual": int(len(sd)), "n_non_self_dual": int(len(ns)),
    "median_u1_self_dual": float(np.median(sd)),
    "median_u1_non_self_dual": float(np.median(ns)),
    "median_diff": d, "n_perm": NPERM, "p_perm": cnt / NPERM,
    "u1_self_dual": [round(float(x), 6) for x in sd],
    "u1_non_self_dual": [round(float(x), 6) for x in ns]}, indent=1), encoding="utf-8")
print(f"-> {OUT.name} (FULL arrays stored)", flush=True)
