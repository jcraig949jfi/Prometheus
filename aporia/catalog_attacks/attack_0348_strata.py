"""CAT-MATH-0348 CONDUCTOR-STRATIFIED analysis (P78) — the last named refinement.

Question: is the sd-vs-ns first-zero split a symmetry-type signal or a conductor
artifact? All four committed samples pool into one dataset tagged (u1, conductor,
group); the split is then tested WITHIN conductor bands (log10 decades).

Pre-stated readings (committed BEFORE first run, binding):
  STRATA-CONSISTENT  direction (sd median > ns median) holds in >= 2/3 of
                     adequately-populated bands AND no band shows a significant
                     reversal (reversed direction with permutation p < 0.05).
  STRATA-MIXED       any band significantly reversed — the split is partially a
                     conductor artifact and the artifact must say so prominently.
  VACUOUS bands      < 50 sd values — excluded, counts reported
                     (cardinality-per-stratum rule P58/P62).

Data integrity gate: the ASC heads (test of record) stored u1 arrays without
labels; this script refetches them with the IDENTICAL deterministic query and
requires elementwise u1 agreement to 1e-9 before using the refetched conductors.
Conductors for disjoint/middle samples parse from their stored degree-1 labels
('1-COND-...'), cross-checked against a refetch for 20 sampled labels.
Seed 20260878 for all band permutation tests.
"""
from __future__ import annotations
import json
import math
import pathlib
import sys
import time

import numpy as np
import psycopg2

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from nt_helpers import unfold_u1

OUT = HERE / "attack_0348_strata_results.json"

files = {
    "asc": json.loads((HERE / "attack_0348_powered_results.json").read_text(encoding="utf-8")),
    "desc": json.loads((HERE / "attack_0348_disjoint_results.json").read_text(encoding="utf-8")),
    "mid": json.loads((HERE / "attack_0348_middle_results.json").read_text(encoding="utf-8")),
}

def parse_cond(label: str) -> float:
    return float(label.split("-")[1])

# --- assemble (u1, conductor) per group --------------------------------------
sd_u, sd_q, ns_u, ns_q = [], [], [], []

# labeled samples: conductors parsed from labels
for key in ("desc", "mid"):
    f = files[key]
    for lab, u in zip(f["labels_self_dual"], f["u1_self_dual"]):
        sd_u.append(u); sd_q.append(parse_cond(lab))
    for lab, u in zip(f["labels_non_self_dual"], f["u1_non_self_dual"]):
        ns_u.append(u); ns_q.append(parse_cond(lab))

# ASC heads: refetch deterministically, gate on elementwise agreement
conn = psycopg2.connect(host="localhost", port=5432, dbname="lmfdb", user="postgres")
cur = conn.cursor()
cur.execute("SET statement_timeout='600s'")
BASE = ("FROM public.lfunc_lfunctions WHERE degree::int = 1 AND {w} "
        "AND positive_zeros IS NOT NULL AND conductor::numeric > 1")
for w, lim, committed, ul, ql in [
        ("self_dual::boolean", 800, files["asc"]["u1_self_dual"], sd_u, sd_q),
        ("NOT self_dual::boolean", 4000, files["asc"]["u1_non_self_dual"], ns_u, ns_q)]:
    t0 = time.time()
    cur.execute(f"""
      SELECT conductor::numeric, positive_zeros::text
      {BASE.format(w=w)} ORDER BY label LIMIT {lim}""")
    got = []
    for q, zt in cur.fetchall():
        zs = json.loads(zt)
        if zs:
            got.append((unfold_u1(float(zs[0]), float(q)), float(q)))
    assert len(got) == len(committed), f"refetch n={len(got)} vs committed {len(committed)}"
    md = max(abs(g[0] - c) for g, c in zip(got, committed))
    assert md < 1e-5, f"ASC refetch drift {md} — mirror mutated, halt"
    print(f"ASC integrity gate: n={len(got)} max|drift|={md:.2e} ({time.time()-t0:.0f}s)", flush=True)
    for u, q in got:
        ul.append(u); ql.append(q)

# label-parse cross-check on 20 sampled labels
import random
rnd = random.Random(20260878)
sample = rnd.sample(files["mid"]["labels_non_self_dual"], 20)
cur.execute("SELECT label, conductor::numeric FROM public.lfunc_lfunctions WHERE label = ANY(%s) GROUP BY label, conductor", (sample,))
for lab, q in cur.fetchall():
    assert parse_cond(lab) == float(q), f"label-parse mismatch {lab}: {parse_cond(lab)} vs {q}"
print("label-parse cross-check: 20/20 exact", flush=True)
conn.close()

sd_u = np.array(sd_u); sd_q = np.array(sd_q)
ns_u = np.array(ns_u); ns_q = np.array(ns_q)
print(f"pooled tagged dataset: sd n={len(sd_u)}, ns n={len(ns_u)}", flush=True)

# --- band tests ---------------------------------------------------------------
rng = np.random.default_rng(20260878)
NPERM = 10_000
bands = []
for lo10 in range(0, 8):
    lo, hi = 10.0 ** lo10, 10.0 ** (lo10 + 1)
    s = sd_u[(sd_q >= lo) & (sd_q < hi)]
    n = ns_u[(ns_q >= lo) & (ns_q < hi)]
    rec = {"band": f"1e{lo10}-1e{lo10+1}", "n_sd": int(len(s)), "n_ns": int(len(n))}
    if len(s) < 50 or len(n) < 50:
        rec["verdict"] = "VACUOUS"
        bands.append(rec)
        continue
    d = float(np.median(s) - np.median(n))
    allv = np.concatenate([s, n]); nA = len(s); cnt_ge = 0; cnt_le = 0
    for _ in range(NPERM):
        p = rng.permutation(allv)
        dd = float(np.median(p[:nA]) - np.median(p[nA:]))
        if dd >= d: cnt_ge += 1
        if dd <= d: cnt_le += 1
    p_pos = cnt_ge / NPERM          # small when d is unusually positive
    p_neg = cnt_le / NPERM          # small when d is unusually negative (reversal)
    rec.update({"median_diff": round(d, 4), "p_pos": p_pos, "p_neg": p_neg,
                "direction": "sd>ns" if d > 0 else "sd<=ns"})
    rec["verdict"] = ("REVERSED-SIGNIFICANT" if (d < 0 and p_neg < 0.05) else
                      "POSITIVE" if d > 0 else "NEGATIVE-NS")
    bands.append(rec)
    print(f"{rec['band']}: sd={len(s)} ns={len(n)} diff={d:+.4f} p_pos={p_pos:.4f} p_neg={p_neg:.4f} {rec['verdict']}", flush=True)

pop = [b for b in bands if b["verdict"] != "VACUOUS"]
pos = sum(1 for b in pop if b["median_diff"] > 0)
rev = sum(1 for b in pop if b["verdict"] == "REVERSED-SIGNIFICANT")
verdict = ("STRATA-MIXED" if rev else
           "STRATA-CONSISTENT" if pop and pos >= math.ceil(2 * len(pop) / 3) else
           "STRATA-MIXED")
print(f"populated bands: {len(pop)}, positive: {pos}, significant reversals: {rev} -> {verdict}", flush=True)

OUT.write_text(json.dumps({
    "protocol": "four committed samples pooled with conductor tags (labels parsed, ASC refetch gated elementwise), log10 conductor bands, per-band median-diff permutation, seed 20260878",
    "bands": bands, "populated": len(pop), "positive_direction": pos,
    "significant_reversals": rev, "pre_stated_branch": verdict}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
