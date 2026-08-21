"""CAT-MATH-0348 MIDDLE-SLICE replication (P77) — the genuinely independent sample.

The pooled test (P73) reused the two committed heads; its pre-registration
protected the statistic, not sample independence. This script measures the
label-space MIDDLE: rows strictly between the ASC head's last label and the
DESC head's first label — disjoint from both committed samples BY
CONSTRUCTION (range bounds) and verified empirically (set intersections must
be zero or the test halts). DISTINCT ON (label) per MIRROR_LABEL_AUDIT.

Pre-stated readings (committed BEFORE first run, binding):
  MIDDLE-REPLICATES      direction (sd > ns) AND permutation p < 0.05
  MIDDLE-DIRECTION-ONLY  direction preserved, p >= 0.05
  MIDDLE-REVERSED        direction flips — the pooled claim is demoted to
                         sample-dependent and the artifact must say so
                         prominently.
Seed 20260877. Unfolding via nt_helpers (shared module).
"""
from __future__ import annotations
import json
import pathlib
import sys
import time

import numpy as np
import psycopg2

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from nt_helpers import unfold_u1

OUT = HERE / "attack_0348_middle_results.json"
desc = json.loads((HERE / "attack_0348_disjoint_results.json").read_text(encoding="utf-8"))

conn = psycopg2.connect(host="localhost", port=5432, dbname="lmfdb", user="postgres")
cur = conn.cursor()
cur.execute("SET statement_timeout='600s'")
BASE = ("FROM public.lfunc_lfunctions WHERE degree::int = 1 AND {w} "
        "AND positive_zeros IS NOT NULL AND conductor::numeric > 1")
WHERE = {"sd": "self_dual::boolean", "ns": "NOT self_dual::boolean"}
LIM = {"sd": 800, "ns": 4000}
DESC_KEY = {"sd": "labels_self_dual", "ns": "labels_non_self_dual"}

data = {}
meta = {}
for k, w in WHERE.items():
    t0 = time.time()
    # committed-head boundaries: ASC head refetched raw (identical query to the
    # test of record), DESC head labels from the committed results file
    cur.execute(f"SELECT label {BASE.format(w=w)} ORDER BY label LIMIT {LIM[k]}")
    asc_labels = {r[0] for r in cur.fetchall()}
    desc_labels = set(desc[DESC_KEY[k]])
    lo, hi = max(asc_labels), min(desc_labels)
    assert lo < hi, f"{k}: label ranges touch — no middle exists (lo={lo}, hi={hi})"
    cur.execute(f"""
      SELECT DISTINCT ON (label) label, conductor::numeric, positive_zeros::text
      {BASE.format(w=w)} AND label > %s AND label < %s
      ORDER BY label LIMIT {LIM[k]}""", (lo, hi))
    rows = cur.fetchall()
    labels, u1 = [], []
    for lab, q, zt in rows:
        zs = json.loads(zt)
        if zs:
            labels.append(lab)
            u1.append(unfold_u1(float(zs[0]), float(q)))
    mid = set(labels)
    ov_a, ov_d = mid & asc_labels, mid & desc_labels
    assert not ov_a and not ov_d, f"{k}: overlap ASC={len(ov_a)} DESC={len(ov_d)} — halt"
    data[k] = (np.array(u1), labels)
    meta[k] = {"asc_max_label": lo, "desc_min_label": hi, "n": len(u1),
               "overlap_asc": 0, "overlap_desc": 0}
    print(f"{k}: middle n={len(u1)} median={np.median(u1):.4f} "
          f"(range ({lo!r}, {hi!r})) ({time.time()-t0:.0f}s)", flush=True)
conn.close()

sd, ns = data["sd"][0], data["ns"][0]
d = float(np.median(sd) - np.median(ns))
rng = np.random.default_rng(20260877)
allv = np.concatenate([sd, ns])
nA = len(sd)
cnt = 0
NPERM = 10_000
for _ in range(NPERM):
    p = rng.permutation(allv)
    if float(np.median(p[:nA]) - np.median(p[nA:])) >= d:
        cnt += 1
p_perm = cnt / NPERM
verdict = ("MIDDLE-REPLICATES" if (d > 0 and p_perm < 0.05)
           else "MIDDLE-DIRECTION-ONLY" if d > 0
           else "MIDDLE-REVERSED")
print(f"diff {d:+.4f}, permutation p = {p_perm:.4f} -> {verdict}", flush=True)

OUT.write_text(json.dumps({
    "protocol": "label-range middle slice (> max ASC-head label, < min DESC-head label), DISTINCT ON (label), seed 20260877, unfolding via nt_helpers",
    "slice_meta": meta,
    "n_self_dual": int(len(sd)), "n_non_self_dual": int(len(ns)),
    "median_u1_self_dual": float(np.median(sd)),
    "median_u1_non_self_dual": float(np.median(ns)),
    "median_diff": d, "n_perm": NPERM, "p_perm": p_perm,
    "pre_stated_branch": verdict,
    "labels_self_dual": data["sd"][1],
    "labels_non_self_dual": data["ns"][1],
    "u1_self_dual": [round(float(x), 6) for x in sd],
    "u1_non_self_dual": [round(float(x), 6) for x in ns]}, indent=1), encoding="utf-8")
print(f"-> {OUT.name} (labels + FULL arrays stored)", flush=True)
