"""CAT-MATH-0348 POOLED adjudication (P73) — runs the test the P71 addendum
pre-stated, no new readings invented here.

Pools the two committed samples: ASC head (attack_0348_powered_results.json,
the P67 test of record) + DESC head (attack_0348_disjoint_results.json).
Readings, committed P71 BEFORE any pooled number existed:
  POOLED-CONFIRM   direction + p < 0.01
  POOLED-MARGINAL  p in [0.01, 0.05]
  POOLED-GONE      p >= 0.05

Disjointness is verified EMPIRICALLY before pooling: the ASC results file
predates label storage, so this script refetches label-only heads under the
identical deterministic ORDER BY and intersects them with the DESC run's
stored labels. Any overlap halts the test.
"""
from __future__ import annotations
import json
import pathlib
import time

import numpy as np
import psycopg2

HERE = pathlib.Path(__file__).parent
OUT = HERE / "attack_0348_pooled_results.json"

asc = json.loads((HERE / "attack_0348_powered_results.json").read_text(encoding="utf-8"))
desc = json.loads((HERE / "attack_0348_disjoint_results.json").read_text(encoding="utf-8"))

# --- empirical disjointness gate ---------------------------------------------
conn = psycopg2.connect(host="localhost", port=5432, dbname="lmfdb", user="postgres")
cur = conn.cursor()
cur.execute("SET statement_timeout='600s'")
BASE = ("FROM public.lfunc_lfunctions WHERE degree::int = 1 AND {w} "
        "AND positive_zeros IS NOT NULL AND conductor::numeric > 1")
WHERE = {"sd": "self_dual::boolean", "ns": "NOT self_dual::boolean"}
LIM = {"sd": 800, "ns": 4000}
overlap = {}
for k, w in WHERE.items():
    t0 = time.time()
    cur.execute(f"SELECT label {BASE.format(w=w)} ORDER BY label LIMIT {LIM[k]}")
    asc_labels = {r[0] for r in cur.fetchall()}
    desc_labels = set(desc[f"labels_{'self_dual' if k=='sd' else 'non_self_dual'}"])
    overlap[k] = sorted(asc_labels & desc_labels)
    print(f"{k}: |ASC|={len(asc_labels)} |DESC|={len(desc_labels)} "
          f"overlap={len(overlap[k])} ({time.time()-t0:.0f}s)", flush=True)
conn.close()
assert not overlap["sd"] and not overlap["ns"], f"OVERLAP — halt: {overlap}"

# --- pooled permutation test -------------------------------------------------
sd = np.array(asc["u1_self_dual"] + desc["u1_self_dual"])
ns = np.array(asc["u1_non_self_dual"] + desc["u1_non_self_dual"])
print(f"pooled: sd n={len(sd)} median={np.median(sd):.4f}; "
      f"ns n={len(ns)} median={np.median(ns):.4f}", flush=True)

d = float(np.median(sd) - np.median(ns))
rng = np.random.default_rng(20260873)
allv = np.concatenate([sd, ns])
nA = len(sd)
cnt = 0
NPERM = 10_000
for _ in range(NPERM):
    p = rng.permutation(allv)
    if float(np.median(p[:nA]) - np.median(p[nA:])) >= d:
        cnt += 1
p_perm = cnt / NPERM
print(f"diff {d:+.4f}, permutation p = {p_perm:.4f}", flush=True)

verdict = ("POOLED-CONFIRM" if (d > 0 and p_perm < 0.01)
           else "POOLED-MARGINAL" if (d > 0 and p_perm < 0.05)
           else "POOLED-GONE")
print(f"pre-stated branch: {verdict}", flush=True)

OUT.write_text(json.dumps({
    "protocol": "pool of the two committed samples (ASC head P67 + DESC head P71), empirical label-disjointness gate, seed 20260873",
    "disjointness": {k: {"overlap_count": len(v)} for k, v in overlap.items()},
    "n_self_dual": int(len(sd)), "n_non_self_dual": int(len(ns)),
    "median_u1_self_dual": float(np.median(sd)),
    "median_u1_non_self_dual": float(np.median(ns)),
    "median_diff": d, "n_perm": NPERM, "p_perm": p_perm,
    "pre_stated_branch": verdict}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
