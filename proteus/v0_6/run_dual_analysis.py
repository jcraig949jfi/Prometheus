"""Keep K_A and K_B separately visible for every adjudicated quantity (completion directive §3).

    python proteus/v0_6/run_dual_analysis.py

run_full.py computes the stationary distribution, entropy-production decomposition, cycle
affinities and the operator-reweighting counterfactual on K_A, and reports only summary statistics
for K_B. The directive requires a reviewer to be able to see whether the claimed phenomenon exists
in BOTH independently measured kernels rather than only in their average. This script re-derives
the same frozen quantities on K_A, K_B and the pooled n=40,000 kernel, from the transition counts
persisted during production.

NO NEW STATISTIC IS INTRODUCED. Every quantity here is one the preregistration already names:
stationary distribution, probability current, detailed balance, entropy production, spanning-tree
fundamental-cycle affinity. They are simply evaluated on the second kernel and on the pool as well
as on the first.

Two design points worth stating:

  * Cycle affinity is a function of P alone and needs no stationary distribution, so the
    non-reversibility signature can be compared across kernels without three extra solves.
  * The cycle BASIS is built once on K_A and then reused for K_B and the pool, so the three are
    compared cycle-for-cycle rather than across differently-chosen bases.

Pooling is reported but never replaces the separate kernels.
"""
from __future__ import annotations

import json
import math
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

from proteus.foundry import grammar  # noqa: E402
from proteus.foundry.affordances import AFFORDANCE_HASH, STORAGE_BOUNDS  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH  # noqa: E402
from proteus.v0_6 import equilibrium as EQ  # noqa: E402
from proteus.v0_6 import space  # noqa: E402

IW = STORAGE_BOUNDS["instruction_words"]


def region(st):
    L, T = st
    cap = T // IW
    if L == 1:
        return "length_min"
    if L == cap:
        return "length_at_tape_cap"
    if T == 16:
        return "tape_min"
    if T == 4096:
        return "tape_max"
    return "interior"


def load_counts(name, n):
    with open(os.path.join(HERE, f"COUNTS_{name}_n{n}.json"), encoding="utf-8") as f:
        d = json.load(f)
    assert d["samples_per_state"] == n
    return {tuple(json.loads(i)): {tuple(json.loads(j)): c for j, c in row.items()}
            for i, row in d["counts"].items()}


def normalise(counts):
    P = {}
    for i, row in counts.items():
        z = math.fsum(row.values())
        P[i] = {j: c / z for j, c in row.items()} if z > 0 else {i: 1.0}
    return P


def pool(a, b):
    out = {}
    for i in a:
        row = dict(a[i])
        for j, c in b.get(i, {}).items():
            row[j] = row.get(j, 0) + c
        out[i] = row
    return out


def affinities(P, cycles):
    vals = []
    for c in cycles:
        v = EQ.cycle_affinity(P, c)
        if v is not None:
            vals.append(v)
        else:
            vals.append(None)
    return vals


def aff_stats(vals):
    ok = [v for v in vals if v is not None]
    if not ok:
        return {"n_evaluable": 0}
    a = sorted(abs(v) for v in ok)
    return {"n_evaluable": len(ok), "max_abs": a[-1], "median_abs": a[len(a) // 2],
            "mean_abs": statistics.fmean(a),
            "frac_abs_gt_0p01": sum(1 for x in a if x > 0.01) / len(a),
            "frac_abs_gt_0p10": sum(1 for x in a if x > 0.10) / len(a)}


def main():
    t0 = time.time()
    with open(os.path.join(HERE, "PREREG_V0_6.json"), encoding="utf-8") as f:
        pre = json.load(f)
    for key, got in (("grammar_hash", grammar.GRAMMAR_HASH), ("runtime_hash", RUNTIME_HASH),
                     ("affordance_hash", AFFORDANCE_HASH)):
        if pre[key] != got:
            print(f"REFUSING: {key} is {got}, preregistration froze {pre[key]}")
            return 6
    n = pre["kernel"]["samples_per_state"]
    states, _t, _r = space.regenerate_states()
    tol = pre["gates"]["stationary"]["power_tol"]

    cA, cB = load_counts("K_A", n), load_counts("K_B", n)
    kernels = {"K_A": normalise(cA), "K_B": normalise(cB), "pooled": normalise(pool(cA, cB))}
    print(f"loaded K_A, K_B and pooled (n={2*n:,}) over {len(states)} states", flush=True)

    # ---- cycle basis built ONCE on K_A, reused for all three so they compare cycle-for-cycle
    cycles, tree_edges = EQ.cycle_basis(kernels["K_A"], states)
    print(f"cycle basis: {len(cycles)} fundamental cycles, {tree_edges} tree edges "
          f"({time.time()-t0:.0f}s)", flush=True)
    aff = {k: affinities(kernels[k], cycles) for k in kernels}
    cyc_out = {k: aff_stats(v) for k, v in aff.items()}
    both = [(a, b) for a, b in zip(aff["K_A"], aff["K_B"]) if a is not None and b is not None]
    cyc_out["K_A_vs_K_B"] = {
        "n_compared": len(both),
        "sign_agreement": (sum(1 for a, b in both if (a > 0) == (b > 0)) / len(both)) if both
        else None,
        "max_abs_difference": max((abs(a - b) for a, b in both), default=0.0),
        "median_abs_difference": (sorted(abs(a - b) for a, b in both)[len(both) // 2] if both
                                  else None),
        "correlation": (statistics.correlation([a for a, _ in both], [b for _, b in both])
                        if len(both) > 2 else None)}
    # the largest-affinity cycles on K_A, shown with their K_B value side by side
    order = sorted((i for i, v in enumerate(aff["K_A"]) if v is not None),
                   key=lambda i: -abs(aff["K_A"][i]))[:15]
    cyc_out["top_cycles_K_A_with_K_B"] = [
        {"cycle": [list(s) for s in cycles[i]], "regions": sorted({region(s) for s in cycles[i]}),
         "affinity_K_A": aff["K_A"][i], "affinity_K_B": aff["K_B"][i],
         "affinity_pooled": aff["pooled"][i]} for i in order]
    print(f"  cycle affinity max|a|: K_A {cyc_out['K_A']['max_abs']:.4f} "
          f"K_B {cyc_out['K_B']['max_abs']:.4f} pooled {cyc_out['pooled']['max_abs']:.4f} | "
          f"sign agreement {cyc_out['K_A_vs_K_B']['sign_agreement']:.4f}", flush=True)

    # ---- stationary distribution for each kernel, same adjudicated method as production
    st, cur, ep = {}, {}, {}
    for k in ("K_A", "K_B", "pooled"):
        pi, m = EQ.stationary_power(kernels[k], states, tol=tol)
        st[k] = {"iterations": m["iterations"], "residual_l1": m["residual_l1"],
                 "min_pi": min(pi.values()), "max_pi": max(pi.values()),
                 "entropy_bits": -math.fsum(p * math.log2(p) for p in pi.values() if p > 0)}
        cur[k] = EQ.currents(kernels[k], pi, states)
        e = EQ.entropy_production(kernels[k], pi, states)
        by_region = {}
        for (i, _j), t in e["_by_edge"]:
            by_region[region(i)] = by_region.get(region(i), 0.0) + t
        e.pop("_by_edge", None)
        ep[k] = {**e, "by_region": by_region}
        st[k]["pi"] = {repr(list(s)): pi[s] for s in states}
        print(f"  {k}: pi solved in {m['iterations']} iters residual {m['residual_l1']:.2e} | "
              f"sigma {e['sigma']:.6e} one-way {e['one_way_edges']} ({time.time()-t0:.0f}s)",
              flush=True)

    # ---- current maps and their agreement
    maps = {k: {(r["i"], r["j"]): r["J"] for r in cur[k]} for k in cur}
    edges = sorted(set(maps["K_A"]) | set(maps["K_B"]))
    diffs = sorted(abs(maps["K_A"].get(e, 0.0) - maps["K_B"].get(e, 0.0)) for e in edges)
    thr = diffs[min(len(diffs) - 1, int(0.99 * len(diffs)))] * \
        pre["gates"]["current"]["material_multiplier"]
    matA = {e for e in edges if abs(maps["K_A"].get(e, 0.0)) > thr}
    matB = {e for e in edges if abs(maps["K_B"].get(e, 0.0)) > thr}
    inter = matA & matB
    signs = [e for e in inter if (maps["K_A"][e] > 0) == (maps["K_B"][e] > 0)]
    cur_out = {
        "material_threshold": thr, "n_pairs": len(edges),
        "noise_p99_abs_diff": diffs[min(len(diffs) - 1, int(0.99 * len(diffs)))],
        "per_kernel": {k: {"total_abs": math.fsum(abs(v) for v in maps[k].values()),
                           "max_abs": max((abs(v) for v in maps[k].values()), default=0.0),
                           "n_material": sum(1 for v in maps[k].values() if abs(v) > thr)}
                       for k in maps},
        "K_A_vs_K_B": {"n_material_K_A": len(matA), "n_material_K_B": len(matB),
                       "n_material_both": len(inter),
                       "jaccard": len(inter) / len(matA | matB) if (matA | matB) else None,
                       "sign_agreement_on_shared": len(signs) / len(inter) if inter else None},
        "top_edges_K_A_with_K_B": [
            {"i": list(e[0]), "j": list(e[1]), "region": region(e[0]),
             "J_K_A": maps["K_A"].get(e, 0.0), "J_K_B": maps["K_B"].get(e, 0.0),
             "J_pooled": maps["pooled"].get(e, 0.0)}
            for e in sorted(matA, key=lambda e: -abs(maps["K_A"][e]))[:25]],
    }
    print(f"  material edges: K_A {len(matA)} K_B {len(matB)} both {len(inter)} "
          f"jaccard {cur_out['K_A_vs_K_B']['jaccard']:.4f} sign agreement "
          f"{cur_out['K_A_vs_K_B']['sign_agreement_on_shared']:.4f}", flush=True)

    db = {k: {"global_abs_flux_imbalance": math.fsum(abs(r["f_ij"] - r["f_ji"]) for r in cur[k]),
              "relative_imbalance": math.fsum(abs(r["f_ij"] - r["f_ji"]) for r in cur[k])
              / math.fsum(r["f_ij"] + r["f_ji"] for r in cur[k])} for k in cur}

    out = {"schema_version": "proteus.v0_6_dual_analysis.v1",
           "samples_per_state_each_kernel": n, "pooled_samples_per_state": 2 * n,
           "identities": {"grammar_hash": grammar.GRAMMAR_HASH, "runtime_hash": RUNTIME_HASH,
                          "affordance_hash": AFFORDANCE_HASH},
           "note": "no new statistic; the frozen quantities evaluated on both kernels and the pool",
           "cycles": cyc_out, "cycle_basis_size": len(cycles), "tree_edges": tree_edges,
           "stationary": st, "currents": cur_out, "detailed_balance": db,
           "entropy_production": ep, "wall_s": time.time() - t0}
    with open(os.path.join(HERE, "RESULT_DUAL_ANALYSIS.json"), "w", encoding="utf-8",
              newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"wrote RESULT_DUAL_ANALYSIS.json ({out['wall_s']:.0f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
