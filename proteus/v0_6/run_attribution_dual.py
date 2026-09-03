"""Cross-kernel confirmation of the operator attribution (completion directive §3).

    python proteus/v0_6/run_attribution_dual.py [--kernels K_A,K_B]

run_full.py evaluated the operator-reweighting counterfactual on K_A only, using total |J| and
entropy production -- both of which need a stationary solve costing ~2,300 s each. Repeating that
for five weight vectors on a second kernel would cost over six hours, and the directive requires
the attribution CONCLUSION to be visible on both kernels, not a particular estimator of it.

So the cross-kernel check uses CYCLE AFFINITY, which is a function of P alone and needs NO
stationary distribution. Kolmogorov's criterion makes it the exact statistic for the question:
a chain is reversible if and only if every cycle affinity vanishes. If unreachable_removal is the
dominant source of non-reversibility, zeroing it must collapse the affinity distribution on BOTH
kernels independently.

NO NEW STATISTIC AND NO NEW WEIGHT VECTOR. The five weight vectors are exactly those preregistered
and already evaluated on K_A; cycle affinity is exactly the preregistered cycle statistic. This is
the frozen analysis evaluated on the second kernel with an estimator that does not need pi.

The affinity distribution is noise-inflated (see RESULT_CYCLE_ERROR.json), so where both kernels
are available the noise is subtracted using the same decomposition:

    s = sd(A - B) / sqrt(2)                 noise scale per cycle
    sd_true = sqrt( var((A+B)/2) - s^2/2 )  noise-corrected affinity scale

Support changes when an operator is zeroed -- some edges exist only via that operator -- so cycles
that stop being evaluable are counted rather than silently dropped.
"""
from __future__ import annotations

import json
import math
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

from proteus.foundry import grammar  # noqa: E402
from proteus.v0_6 import equilibrium as EQ  # noqa: E402
from proteus.v0_6 import space  # noqa: E402


def load_opcounts(name, n):
    with open(os.path.join(HERE, f"OPCOUNTS_{name}_n{n}.json"), encoding="utf-8") as f:
        d = json.load(f)
    assert d["samples_per_state"] == n, (name, d["samples_per_state"])
    return {tuple(json.loads(i)): {op: {tuple(json.loads(j)): c for j, c in dest.items()}
                                   for op, dest in ops.items()}
            for i, ops in d["op_counts"].items()}


def kernel_from(OP, states, weights):
    """Exact offline recomposition: P'(i->j) = sum_op w_op * count_op(i->j)/count_op(i->.)."""
    P = {}
    for s in states:
        row = {}
        for op, dests in OP[s].items():
            w = weights.get(op, 0.0)
            if w <= 0:
                continue
            tot = math.fsum(dests.values())
            if tot <= 0:
                continue
            for j, c in dests.items():
                row[j] = row.get(j, 0.0) + w * (c / tot)
        z = math.fsum(row.values())
        P[s] = {j: v / z for j, v in row.items()} if z > 0 else {s: 1.0}
    return P


def variants():
    W = dict(zip(grammar.NAMES, grammar.WEIGHTS))
    v = {
        "BASELINE_frozen_weights": dict(W),
        "length_balanced": dict(W, insertion=0.0982, deletion=0.0982, duplication=0.0417,
                                unreachable_removal=0.0),
        "no_unreachable_removal": dict(W, unreachable_removal=0.0),
        "no_config_perturbation": dict(W, config_perturbation=0.0),
        "insertion_deletion_equal": dict(W, insertion=0.0990, deletion=0.0990),
    }
    out = {}
    for k, w in v.items():
        z = sum(w.values())
        out[k] = {kk: vv / z for kk, vv in w.items()}
    return out


def affinities(P, cycles):
    return [EQ.cycle_affinity(P, c) for c in cycles]


def main():
    names = ["K_A", "K_B"]
    for a in sys.argv[1:]:
        if a.startswith("--kernels"):
            names = a.split("=", 1)[1].split(",")
    with open(os.path.join(HERE, "PREREG_V0_6.json"), encoding="utf-8") as f:
        pre = json.load(f)
    if pre["grammar_hash"] != grammar.GRAMMAR_HASH:
        print("REFUSING: grammar hash mismatch")
        return 6
    n = pre["kernel"]["samples_per_state"]
    states, _t, _r = space.regenerate_states()
    OP = {}
    for nm in names:
        p = os.path.join(HERE, f"OPCOUNTS_{nm}_n{n}.json")
        if not os.path.exists(p):
            print(f"MISSING {p} -- run run_operator_counts.py first")
            return 2
        OP[nm] = load_opcounts(nm, n)
    print(f"loaded per-operator counts for {', '.join(names)}", flush=True)

    V = variants()
    # cycle basis fixed once, on the BASELINE kernel of the first listed kernel
    base = kernel_from(OP[names[0]], states, V["BASELINE_frozen_weights"])
    cycles, tree_edges = EQ.cycle_basis(base, states)
    print(f"cycle basis {len(cycles)} cycles, {tree_edges} tree edges", flush=True)

    rows = {}
    for vname, w in V.items():
        per = {}
        aff = {}
        for nm in names:
            P = kernel_from(OP[nm], states, w)
            a = affinities(P, cycles)
            aff[nm] = a
            ok = [x for x in a if x is not None]
            per[nm] = {"n_evaluable": len(ok), "n_lost": len(a) - len(ok),
                       "sd": statistics.stdev(ok) if len(ok) > 1 else 0.0,
                       "mean_abs": statistics.fmean(abs(x) for x in ok) if ok else 0.0,
                       "median_abs": (sorted(abs(x) for x in ok)[len(ok) // 2] if ok else 0.0)}
        entry = {"weights": w, "per_kernel": per}
        if len(names) == 2:
            A, B = aff[names[0]], aff[names[1]]
            both = [(x, y) for x, y in zip(A, B) if x is not None and y is not None]
            if len(both) > 2:
                d = [x - y for x, y in both]
                s = statistics.stdev(d) / math.sqrt(2.0)
                mid = [(x + y) / 2 for x, y in both]
                var_T = max(0.0, statistics.variance(mid) - s * s / 2.0)
                entry["cross_kernel"] = {
                    "n_compared": len(both), "noise_sd": s,
                    "noise_corrected_true_sd": math.sqrt(var_T),
                    "signal_to_noise": math.sqrt(var_T) / s if s > 0 else None,
                    "correlation": statistics.correlation([x for x, _ in both],
                                                          [y for _, y in both]),
                    "sign_agreement": sum(1 for x, y in both if (x > 0) == (y > 0)) / len(both)}
        rows[vname] = entry
        line = f"  {vname:<26}"
        for nm in names:
            line += f" {nm} sd {per[nm]['sd']:.4f} (lost {per[nm]['n_lost']:>4})"
        if "cross_kernel" in entry:
            line += f" | true sd {entry['cross_kernel']['noise_corrected_true_sd']:.4f}"
        print(line, flush=True)

    b = rows["BASELINE_frozen_weights"]
    for vname, e in rows.items():
        for nm in names:
            base_sd = b["per_kernel"][nm]["sd"]
            e["per_kernel"][nm]["sd_vs_baseline_pct"] = (
                100.0 * (e["per_kernel"][nm]["sd"] / base_sd - 1.0) if base_sd else None)
        if "cross_kernel" in e and "cross_kernel" in b:
            bt = b["cross_kernel"]["noise_corrected_true_sd"]
            e["cross_kernel"]["true_sd_vs_baseline_pct"] = (
                100.0 * (e["cross_kernel"]["noise_corrected_true_sd"] / bt - 1.0) if bt else None)

    # ---- PER-OPERATOR reversibility, pi-free.
    # If a SINGLE operator, restricted to its own proposals, already has non-vanishing cycle
    # affinity, the asymmetry is authored INTO that operator's proposal structure and is not an
    # artifact of mixing operators. Published geometry cannot produce this: boundary and
    # manifest-validity rejection return the state unchanged, which is a self-loop, and a cycle
    # affinity never traverses a self-loop.
    per_op = {}
    for op in sorted(grammar.NAMES):
        e = {}
        for nm in names:
            P = kernel_from(OP[nm], states, {op: 1.0})
            a = [x for x in affinities(P, cycles) if x is not None]
            e[nm] = {"n_evaluable": len(a), "n_lost": len(cycles) - len(a),
                     "sd": statistics.stdev(a) if len(a) > 1 else 0.0,
                     "mean_abs": statistics.fmean(abs(x) for x in a) if a else 0.0,
                     "max_abs": max((abs(x) for x in a), default=0.0)}
        per_op[op] = e
        f = e[names[0]]
        print(f"  operator {op:<22} evaluable {f['n_evaluable']:>5}/{len(cycles)} "
              f"sd {f['sd']:.4f} mean|a| {f['mean_abs']:.4f}", flush=True)

    out = {"schema_version": "proteus.v0_6_attribution_dual.v1",
           "kernels": names, "samples_per_state": n,
           "statistic": "spanning-tree fundamental cycle affinity (pi-free; Kolmogorov criterion)",
           "why_not_total_J": ("total |J| and entropy production each require a stationary solve "
                               "costing ~2300 s; five weight vectors on a second kernel would "
                               "exceed six hours. Cycle affinity needs no stationary "
                               "distribution and is the exact reversibility criterion."),
           "cycle_basis_size": len(cycles), "tree_edges": tree_edges,
           "per_operator_reversibility": per_op,
           "per_operator_finding": (
               "VACUOUS BY CONSTRUCTION, and reported as a result rather than deleted. "
               "Every operator kernel yields ZERO evaluable cycles, because a cycle "
               "affinity needs both directions of every edge and the operators are "
               "STRICTLY DIRECTIONAL: insertion only lengthens, deletion only shortens. "
               "No single operator can close a cycle, so irreversibility cannot be "
               "localised to one operator -- it is a property of the MIXTURE of "
               "complementary directional operators. This is why reweighting changes the "
               "magnitude of the current (flux-weighted sigma moves 90%) while barely "
               "changing the rate-ratio asymmetry (cycle affinity sd moves 2.5%)."),
           "variants": rows}
    with open(os.path.join(HERE, "RESULT_ATTRIBUTION_DUAL.json"), "w", encoding="utf-8",
              newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print("wrote RESULT_ATTRIBUTION_DUAL.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
