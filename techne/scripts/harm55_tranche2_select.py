"""Tranche 2 selection rules for rollout fossils (operator directive 6, 2026-09-19, s3) -- FROZEN BEFORE ANY
NATIVE (Flax) SCORE EXISTS. Committed on main before HARM55_FLAX_NATIVE_*.json; the rules below are not edited
after that file appears (a change is a new, dated selector).

Input: the original-observer column (HARM55_TORCH_ORIGINAL_2026-09-19.json) and the native column
(harm55_flax_score.py --path flax output), both keyed by stage_idx. Output: {key: reason} with EVERY category
below represented where it is non-empty, plus the two pair types.

Categories (directive s3), each with an explicit, fixed rule:
  D1 largest observer disagreements          top 8 by |signed_diff| among alive rollouts
  D2 crossing -> non-crossing flips           all rollouts below garbage_mean under original, >= under native
  D3 non-crossing -> crossing flips           all rollouts >= garbage_mean under original, below under native
  D4 class flips                              all rollouts whose re-derived class under native differs
  D5 genuine organisms low under BOTH         GENUINE class, below garbage_mean under both observers (up to 8 lowest by native)
  D6 exploits that become ordinary            METRIC_EXPLOIT below garbage_mean under original, >= garbage_mean under native
  D7 catalogue crossings that survive         S0 rows below garbage_mean under both
  D8 catalogue crossings that disappear       S0 rows below garbage_mean under original, >= under native
  P1 nearest BEHAVIOURAL pairs, very different metric   5 pairs: nearest in standardised (coh, d_pix, mass_cv, disp)
                                              space with the largest |score_original difference| >= 0.02
  P2 nearest METRIC pairs, very different behaviour     5 pairs: |score_original difference| <= 0.002 with the
                                              largest standardised behavioural distance
Boundaries: garbage_mean 0.8167 (the frozen convention), the same under both observers (VIEW 1, locked
thresholds). VIEW 2 (native anchors) is Harmonia's; this selector does not move a threshold.
Run: python techne/scripts/harm55_tranche2_select.py --flax HARM55_FLAX_NATIVE_<date>.json --out ROLLOUT_FOSSILS_TRANCHE2_<date>.json
"""
from __future__ import annotations

import argparse
import itertools
import json
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve()
REPO = HERE.parents[2]
TORCH = REPO / "techne" / "acquisition" / "poet_alife" / "HARM55_TORCH_ORIGINAL_2026-09-19.json"
ROWS = REPO / "roles" / "Harmonia" / "science" / "asal_ruler" / "out" / "run_2026-09-18" / "search" / "rows.jsonl"
G = 0.8167


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--flax", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    t = json.loads(TORCH.read_text(encoding="utf-8")); f = json.loads(pathlib.Path(a.flax).read_text(encoding="utf-8"))
    rows = {"%s_%s" % (r["stage"], r["idx"]): r for r in (json.loads(l) for l in open(ROWS, encoding="utf-8")) if "error" not in r}
    tr, fs = t["rows"], f["scores"]
    alive = [k for k in tr if tr[k]["alive"] and k in fs and tr[k]["score_original"] is not None]
    o = {k: tr[k]["score_original"] for k in alive}; n = {k: fs[k] for k in alive}
    sel = {}
    def add(k, reason):
        sel.setdefault(k, reason)
    for k in sorted(alive, key=lambda k: -abs(n[k] - o[k]))[:8]:
        add(k, "D1 largest observer disagreement (signed %.4f)" % (n[k] - o[k]))
    for k in alive:
        if o[k] < G <= n[k]: add(k, "D2 crossing -> non-crossing under the native observer")
        if o[k] >= G > n[k]: add(k, "D3 non-crossing -> crossing under the native observer")
        fr = f["rows"].get(k, {})
        if fr.get("class_changed"): add(k, "D4 class flip %s -> %s" % (tr[k]["class"], fr.get("class_flax")))
    gen = sorted([k for k in alive if tr[k]["class"] == "GENUINE_DYNAMICAL_NOVELTY" and o[k] < G and n[k] < G], key=lambda k: n[k])[:8]
    for k in gen: add(k, "D5 genuine organism low under BOTH observers")
    for k in alive:
        if tr[k]["class"] == "METRIC_EXPLOIT" and o[k] < G <= n[k]: add(k, "D6 exploit that becomes ordinary under the native observer")
        if tr[k]["stage"] == "S0" and o[k] < G and n[k] < G: add(k, "D7 catalogue crossing that survives")
        if tr[k]["stage"] == "S0" and o[k] < G <= n[k]: add(k, "D8 catalogue crossing that disappears")
    # behavioural space (frame-based observables only; observer-independent)
    feats = {k: [rows[k].get("coh"), rows[k].get("d_pix"), rows[k].get("mass_cv"), rows[k].get("disp")] for k in alive if k in rows}
    ks = [k for k in feats if all(v is not None and np.isfinite(v) for v in feats[k])]
    X = np.array([feats[k] for k in ks]); X = (X - X.mean(0)) / (X.std(0) + 1e-12)
    pairs = []
    for i, j in itertools.combinations(range(len(ks)), 2):
        pairs.append((float(np.linalg.norm(X[i] - X[j])), abs(o[ks[i]] - o[ks[j]]), ks[i], ks[j]))
    p1 = sorted([p for p in pairs if p[1] >= 0.02], key=lambda p: p[0])[:5]
    p2 = sorted([p for p in pairs if p[1] <= 0.002], key=lambda p: -p[0])[:5]
    pair_log = {"P1_nearest_behaviour_far_metric": [{"a": p[2], "b": p[3], "behav_dist": p[0], "score_gap": p[1]} for p in p1],
                "P2_nearest_metric_far_behaviour": [{"a": p[2], "b": p[3], "behav_dist": p[0], "score_gap": p[1]} for p in p2]}
    for p in p1:
        add(p[2], "P1 nearest behavioural pair with very different metric (with %s; dist %.3f, gap %.4f)" % (p[3], p[0], p[1])); add(p[3], "P1 pair partner of %s" % p[2])
    for p in p2:
        add(p[2], "P2 nearest metric pair with very different behaviour (with %s; gap %.4f, dist %.3f)" % (p[3], p[1], p[0])); add(p[3], "P2 pair partner of %s" % p[2])
    out = {"selector": str(HERE.relative_to(REPO)).replace("\\", "/"), "flax_input": a.flax, "garbage_mean": G, "n_alive_compared": len(alive),
           "counts_by_category": {c: sum(1 for r in sel.values() if r.startswith(c)) for c in ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "P1", "P2")},
           "pairs": pair_log, "selection": sel}
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out["counts_by_category"]), "| total", len(sel), "->", a.out)


if __name__ == "__main__":
    main()
