"""E-002 T-009/T-010/T-011: continuity criteria on the preserved PTE cases (bounded; CPU; engine read-only).

    python3 -m archaeon.causal_lens.e002_pte repro  OUT.json   reproduce out_v02/PTE_ARCH_V02.json (regress_v02.pte_arch, same seed)
    python3 -m archaeon.causal_lens.e002_pte arch   OUT.json   the same 48 children + a controlled share sweep, full readings
    python3 -m archaeon.causal_lens.e002_pte ga     OUT.json   the in-GA crossovers of out_v02/PTE_V02.json (instrumented replay)

Needs numpy + torch (CPU) and the committed PTE rows roles/Ananke/pte/c1_rows/cells.jsonl.gz. Writes nothing into out_v02/.
Readings per crossover child (T-007_CRITERION.md):
  C-MAJ flow   v0.2 MAJORITY over mask shares of all G x L instructions (what out_v02 reports)
  C-MAJ diff   the same rule over the instructions where the parents DIFFER (the only mask bits that change the child)
  C-OP         ILL_POSED by mechanism (search.crossover is exchangeable in (a, b); parents drawn identically in search.evolve)
  M1           can flipping causally inert mask bits (positions where a == b) reverse C-MAJ flow's answer?
  M2           exact two-sided Binomial(n, 1/2) p of the realized share (flow over n = G*L; diff over n = differing positions)
  ARCH exact   the FROZEN criterion (equal 8-world accuracy vector); ARCH nearer: L1 distance of accuracy vectors, only where the
               parents' vectors differ (non-saturation guard, B7); degenerate = equal to the zero-genome control
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
import time
from collections import Counter

import numpy as np

from archaeon.causal_lens import adapters_v02 as A2
from archaeon.causal_lens.e002_continuity import binom_two_sided_p, continuity_op
from archaeon.causal_lens.schema_v02 import ILL, continuity

ROWS = "roles/Ananke/pte/c1_rows/cells.jsonl.gz"
PTE_CROSS = {"name": "prometheus.ananke.search.crossover", "code_ref": "prometheus/ananke/search.py:76-78 (m = g.random < 0.5); "
             "parents drawn identically at :119-121", "exchangeable": [["a", "b"]]}


def _champs(group):
    out = []; row0 = None
    with gzip.open(ROWS, "rt") as fh:
        for l in fh:
            r = json.loads(l)
            if r["kind"] != "evolve": continue
            key = hashlib.sha256(json.dumps([r["physics"], r["env"]], sort_keys=True).encode()).hexdigest()[:12]
            if key != group: continue
            res = r.get("result") or {}; ch = res.get("champion") or (r.get("extra") or {}).get("genome")
            if ch is not None: out.append((r["cell_id"], (res.get("held") or {}).get("acc"), np.array(ch))); row0 = row0 or r
    out.sort(key=lambda x: -(x[1] or 0)); return out, row0


def _read(mask, a, b, sig, cid, aid, bid, zero):
    ident = np.all(a == b, axis=-1); diff = ~ident; n = int(mask.size); nd = int(diff.sum())
    fa = int(mask.sum()); fa_d = int((mask & diff).sum())
    flow = continuity({"a": fa / n, "b": 1 - fa / n}, A2.MAJ_ILL)["hu_continuity"]
    dmaj = continuity({"a": fa_d / nd, "b": 1 - fa_d / nd}, A2.MAJ_ILL)["hu_continuity"] if nd else "NO_DIFFERENCE"
    lo, hi = fa_d, fa_d + int(ident.sum())                      # from_a reachable by flipping inert bits only
    reach = {continuity({"a": k / n, "b": 1 - k / n}, A2.MAJ_ILL)["hu_continuity"] for k in range(lo, hi + 1)}
    sc, sa, sb = sig[cid], sig[aid], sig[bid]
    exact = "same_as_a" if sc == sa and sc != sb else ("same_as_b" if sc == sb and sc != sa else ("same_as_both" if sc == sa == sb else "new_class"))
    if sa == sb: nearer = "NOT_IDENTIFIABLE(parents_saturated)"
    else:
        da = sum(abs(x - y) for x, y in zip(sc, sa)); db = sum(abs(x - y) for x, y in zip(sc, sb))
        nearer = "a" if da < db else ("b" if db < da else "tie")
    return {"from_a": fa, "total": n, "n_differing": nd, "from_a_differing": fa_d,
            "C-MAJ_flow": flow, "C-MAJ_diff": dmaj, "C-OP": continuity_op({"a": fa / n, "b": 1 - fa / n}, PTE_CROSS, {"a": "a", "b": "b"})["hu_continuity"],
            "M1_flow_answer_invariant": len(reach) == 1, "M1_reachable": sorted(reach),
            "M2_p_flow": round(binom_two_sided_p(fa, n), 4), "M2_p_diff": round(binom_two_sided_p(fa_d, nd), 4) if nd else None,
            "arch_exact": exact, "arch_nearer": nearer, "degenerate": sc == sig[zero], "sig": list(sc)}


def repro(group="1455015bd05a", n_children=24, seed=20260927):
    """exactly regress_v02.pte_arch's draws and genome set; compare with the preserved out_v02/PTE_ARCH_V02.json."""
    from prometheus.ananke import envs
    from prometheus.ananke.physics import Physics
    champs, row0 = _champs(group)
    ph = Physics.from_dict(row0["physics"]); env = envs.EnvSpec(**row0["env"]); rng = np.random.default_rng(seed)
    pairs = [(champs[0], champs[1]), (champs[2], champs[3])]
    genomes = {"ZERO_CONTROL": np.zeros_like(champs[0][2])}; kids = []
    for x, y in pairs:
        ca, a, cb, b = x[0], x[2], y[0], y[2]; genomes["P:" + ca] = a; genomes["P:" + cb] = b
        for k in range(n_children):
            m = rng.random(a.shape[:2]) < 0.5; c = np.where(m[..., None], a, b); cid = "C:%s:%s:%d" % (ca[:6], cb[:6], k); genomes[cid] = c
            kids.append((cid, "P:" + ca, "P:" + cb, m))
    t0 = time.time(); sig = A2.pte_behavior(ph, env, genomes); beh = time.time() - t0
    pres = {r["child"]: r for r in json.load(open("archaeon/causal_lens/out_v02/PTE_ARCH_V02.json"))["rows"]}
    ppar = json.load(open("archaeon/causal_lens/out_v02/PTE_ARCH_V02.json"))["parent_signatures_distinct"]
    rows = []; mism = Counter()
    for cid, aid, bid, m in kids:
        r = _read(m, genomes[aid], genomes[bid], sig, cid, aid, bid, "ZERO_CONTROL"); r.update(child=cid, a=aid, b=bid)
        p = pres[cid]
        for k_new, k_old in (("from_a", "from_a"), ("C-MAJ_flow", "hu_continuity"), ("degenerate", "degenerate")):
            if r[k_new] != p[k_old]: mism[k_old] += 1
        if r["arch_exact"] != p["arch"]: mism["arch"] += 1
        rows.append(r)
    par_ok = all(list(sig[k]) == v for k, v in ppar.items())
    return {"group": group, "children": len(rows), "mismatches_vs_preserved": dict(mism), "parent_signatures_equal": par_ok,
            "genome_shape": list(champs[0][2].shape), "behavior_s": round(beh, 1), "rows": rows,
            "sha256_masks": hashlib.sha256(b"".join(np.packbits(k[3]).tobytes() for k in kids)).hexdigest()}


def arch(group="1455015bd05a", sweep_per_k=6, sweep_seed=20260928):
    """the 48 preserved children (re-derived by repro) + a controlled sweep: for each pair and each k in 0..G*L, children whose
    mask takes exactly k instructions from a (positions uniform). k = 0 / G*L are exact parent copies (determinism control)."""
    from prometheus.ananke import envs
    from prometheus.ananke.physics import Physics
    base = repro(group)
    champs, row0 = _champs(group)
    ph = Physics.from_dict(row0["physics"]); env = envs.EnvSpec(**row0["env"]); rng = np.random.default_rng(sweep_seed)
    pairs = [(champs[0], champs[1]), (champs[2], champs[3])]
    genomes = {"ZERO_CONTROL": np.zeros_like(champs[0][2])}; kids = []
    for x, y in pairs:
        ca, a, cb, b = x[0], x[2], y[0], y[2]; genomes["P:" + ca] = a; genomes["P:" + cb] = b
        n = a.shape[0] * a.shape[1]
        for k in range(n + 1):
            for j in range(sweep_per_k):
                pos = rng.permutation(n)[:k]; m = np.zeros(n, dtype=bool); m[pos] = True; m = m.reshape(a.shape[:2])
                cid = "S:%s:%s:k%02d:%d" % (ca[:6], cb[:6], k, j); genomes[cid] = np.where(m[..., None], a, b); kids.append((cid, "P:" + ca, "P:" + cb, m))
    t0 = time.time(); sig = A2.pte_behavior(ph, env, genomes); beh = time.time() - t0
    rows = []
    for cid, aid, bid, m in kids:
        r = _read(m, genomes[aid], genomes[bid], sig, cid, aid, bid, "ZERO_CONTROL"); r.update(child=cid, a=aid, b=bid); rows.append(r)
    ident = {"%s|%s" % ("P:" + x[0], "P:" + y[0]): int(np.all(x[2] == y[2], axis=-1).sum()) for x, y in pairs}
    return {"repro": {k: v for k, v in base.items() if k != "rows"}, "preserved48": base["rows"], "sweep": rows,
            "identical_instructions_per_pair": ident, "parent_sigs": {k: list(sig[k]) for k in genomes if k.startswith("P:")},
            "zero_sig": list(sig["ZERO_CONTROL"]), "sweep_behavior_s": round(beh, 1)}


def ga():
    """the in-GA crossovers behind out_v02/PTE_V02.json: identical instrumented replay, now keeping the parent genomes."""
    from prometheus.ananke import search as S, envs
    from prometheus.ananke.physics import Physics
    row = None
    with gzip.open(ROWS, "rt") as fh:
        for l in fh:
            r = json.loads(l)
            if r["kind"] == "evolve": row = r; break
    small = {"pop": 16, "gens": 6, "M": 2, "M_final": 2, "M_held": 4}
    ph = Physics.from_dict(row["physics"]); env = envs.EnvSpec(**row["env"]); sp = S.SearchSpec(**{**row["search"], **small})
    recs = []; oc = S.crossover

    def cross(g, a, b):
        m = g.random(a.shape[:2]) < 0.5; recs.append((m.copy(), np.array(a), np.array(b))); return np.where(m[..., None], a, b)
    S.crossover = cross
    try:
        t0 = time.time(); out = S.evolve(ph, env, row["search_seed"], sp, device="cpu"); evo = time.time() - t0
    finally:
        S.crossover = oc
    pres = json.load(open("archaeon/causal_lens/out_v02/PTE_V02.json"))
    rows = []
    for (m, a, b), p in zip(recs, pres["crossover_rows"]):
        ident = np.all(a == b, axis=-1); diff = ~ident; n = m.size; nd = int(diff.sum()); fa = int(m.sum()); fa_d = int((m & diff).sum())
        flow = continuity({"a": fa / n, "b": 1 - fa / n}, A2.MAJ_ILL)["hu_continuity"]
        reach = {continuity({"a": k / n, "b": 1 - k / n}, A2.MAJ_ILL)["hu_continuity"] for k in range(fa_d, fa_d + int(ident.sum()) + 1)}
        rows.append({"from_a": fa, "preserved_from_a": p["from_a"], "total": n, "self_cross": bool(np.array_equal(a, b)), "n_differing": nd,
                     "from_a_differing": fa_d, "C-MAJ_flow": flow,
                     "C-MAJ_diff": continuity({"a": fa_d / nd, "b": 1 - fa_d / nd}, A2.MAJ_ILL)["hu_continuity"] if nd else "NO_DIFFERENCE",
                     "M1_flow_answer_invariant": len(reach) == 1, "M1_reachable": sorted(reach),
                     "M2_p_flow": round(binom_two_sided_p(fa, n), 4), "M2_p_diff": round(binom_two_sided_p(fa_d, nd), 4) if nd else None})
    return {"cell_id": row["cell_id"], "crossovers": len(rows), "preserved_crossovers": len(pres["crossover_rows"]),
            "from_a_all_equal_preserved": all(r["from_a"] == r["preserved_from_a"] for r in rows) and len(rows) == len(pres["crossover_rows"]),
            "champion_hash": hashlib.sha256(np.ascontiguousarray(out["champion"], dtype=np.int64).tobytes()).hexdigest()[:16],
            "evolve_s": round(evo, 1), "rows": rows}


if __name__ == "__main__":
    what, path = sys.argv[1], sys.argv[2]
    import torch; torch.set_num_threads(3)
    res = {"repro": repro, "arch": arch, "ga": ga}[what]()
    with open(path, "w", encoding="utf-8", newline="\n") as fh: json.dump(res, fh, indent=1, default=str); fh.write("\n")
    print(json.dumps({k: v for k, v in res.items() if k not in ("rows", "sweep", "preserved48")}, default=str)[:3000])
