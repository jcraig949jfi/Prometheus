"""Part II: the structural Markov kernel of the frozen V0.4 grammar, and its equilibrium analysis.

    python proteus/v0_5/run_kernel.py [primary|sensitivity]

Measures the kernel from the live operator, validates it against a second independent sample under
the frozen tolerance, solves for the stationary distribution, computes probability currents, cycle
currents and entropy production, builds the reversible reference, and runs matched trajectories.
Nothing here changes the grammar.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

from proteus.foundry import grammar  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH  # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from  # noqa: E402
from proteus.v0_5 import kernel as K  # noqa: E402

IW = 4


def load_prereg():
    with open(os.path.join(HERE, "PREREG_V0_5.json"), encoding="utf-8") as f:
        pre = json.load(f)
    if pre["grammar_hash"] != grammar.GRAMMAR_HASH:
        raise SystemExit("REFUSED: grammar hash differs from the preregistered v0.4 grammar")
    if pre["runtime_hash"] != RUNTIME_HASH:
        raise SystemExit("REFUSED: runtime hash differs")
    return pre


def short_cycles(cur_rows, pi, P, max_nodes=3, top=25):
    """Directed 3-cycles carrying net current, ranked by their minimum edge current.

    A cycle current is well defined as the common circulation around the loop; we report the
    minimum |J| along the loop as a conservative lower bound on the circulating flux, and the
    cycle affinity sum log(P_ij/P_ji), which is zero for every cycle iff the chain is reversible
    (Kolmogorov's criterion).
    """
    adj = defaultdict(set)
    for i in P:
        for j, p in P[i].items():
            if j != i and p > 0:
                adj[i].add(j)
    seen = set()
    out = []
    nodes = sorted(P, key=lambda s: -pi.get(s, 0.0))[:120]
    nodeset = set(nodes)
    for a in nodes:
        for b in adj[a]:
            if b not in nodeset:
                continue
            for c in adj[b]:
                if c not in nodeset or c == a:
                    continue
                if a not in adj[c]:
                    continue
                key = tuple(sorted([a, b, c]))
                if key in seen:
                    continue
                seen.add(key)
                legs = [(a, b), (b, c), (c, a)]
                aff = 0.0
                ok = True
                for (x, y) in legs:
                    f, r = P[x].get(y, 0.0), P[y].get(x, 0.0)
                    if f <= 0 or r <= 0:
                        ok = False
                        break
                    aff += math.log(f / r)
                if not ok:
                    continue
                js = [pi[x] * P[x].get(y, 0.0) - pi[y] * P[y].get(x, 0.0) for (x, y) in legs]
                out.append({"cycle": [list(a), list(b), list(c)],
                            "affinity": aff,
                            "min_abs_edge_current": min(abs(v) for v in js),
                            "edge_currents": js})
    out.sort(key=lambda d: -abs(d["affinity"]))
    return out[:top]


def main():
    pre = load_prereg()
    mode = sys.argv[1] if len(sys.argv) > 1 else "primary"
    kc = pre["kernel"]
    if mode == "primary":
        tapes, mx, ns = tuple(kc["primary_tapes"]), kc["primary_max_len"], kc["primary_samples"]
    else:
        tapes, mx, ns = tuple(kc["sensitivity_tapes"]), kc["sensitivity_max_len"], kc["sensitivity_samples"]
    states = K.state_space(tapes, mx)
    print(f"[{mode}] {len(states)} states, {ns} samples/state, grammar {grammar.GRAMMAR_HASH[:12]}")
    t0 = time.time()

    P, opc, trunc = K.measure_kernel(states, ns, pre["seed"], f"{mode}.A")
    print(f"  kernel A measured ({time.time()-t0:.0f}s)")
    P2, _o2, _t2 = K.measure_kernel(states, ns, pre["seed"] + 1, f"{mode}.B")
    print(f"  kernel B measured ({time.time()-t0:.0f}s)")

    tv = K.compare_kernels(P, P2, states)
    med = sorted(d["tv_distance"] for d in tv)[len(tv) // 2]
    mx_tv = tv[0]["tv_distance"]
    tol = kc["live_agreement_tolerance"]
    agree_ok = (med <= tol["median_tv_max"]) and (mx_tv <= tol["max_tv_max"])
    print(f"  live-agreement: median TV {med:.5f} (<= {tol['median_tv_max']}), "
          f"max TV {mx_tv:.5f} (<= {tol['max_tv_max']}) -> {'OK' if agree_ok else 'ABORT'}")

    Pan = K.analytic_kernel(states)
    tv_an = K.compare_kernels(P, Pan, states)
    med_an = sorted(d["tv_distance"] for d in tv_an)[len(tv_an) // 2]

    classes = K.communicating_classes(P, states)
    closed = K.closed_classes(P, classes, states)
    pi, iters, delta = K.stationary(P, states)
    print(f"  classes {len(classes)} (closed {sum(closed)}), stationary in {iters} iters, "
          f"L1 delta {delta:.2e}")

    cur = K.currents(P, pi, states)
    # Monte-Carlo noise floor: the same statistic computed between the two independent samples
    pi2, _i2, _d2 = K.stationary(P2, states)
    cur2 = K.currents(P2, pi2, states)
    c2 = {(tuple(r["i"]), tuple(r["j"])): r["J"] for r in cur2}
    noise = [abs(r["J"] - c2.get((tuple(r["i"]), tuple(r["j"])), 0.0)) for r in cur]
    noise_floor = max(noise) if noise else 0.0
    med_noise = sorted(noise)[len(noise) // 2] if noise else 0.0

    for r in cur:
        i, j = tuple(r["i"]), tuple(r["j"])
        r["attribution"] = K.attribute_edge(i, j, opc, tapes, mx)
        r["above_noise_floor"] = abs(r["J"]) > noise_floor
    tot_abs = sum(abs(r["J"]) for r in cur)
    above = [r for r in cur if r["above_noise_floor"]]
    mx_cur = max((abs(r["J"]) for r in cur), default=0.0)
    print(f"  currents: {len(cur)} pairs, total |J| {tot_abs:.3e}, max |J| {mx_cur:.3e}, "
          f"MC noise floor {noise_floor:.3e} (median {med_noise:.3e}), above floor {len(above)}")

    ep = K.entropy_production(P, pi, states)
    cyc = short_cycles(cur, pi, P)
    Q = K.reversible_reference(P, pi, states)
    curQ = K.currents(Q, pi, states)
    print(f"  entropy production sigma {ep['sigma']:.6e} over {ep['n_terms']} terms; "
          f"one-way edges {ep['one_way_edges']}")
    print(f"  reference max |J| {max((abs(r['J']) for r in curQ), default=0.0):.3e} (must be ~0)")
    if cyc:
        print(f"  top cycle affinity {cyc[0]['affinity']:+.6f}")

    # matched trajectories
    steps = kc["trajectory_steps"] if mode == "primary" else 200000
    start = max(states, key=lambda s: pi[s])
    rA = SplitMix64(seed_from("traj.active", pre["seed"]))
    rB = SplitMix64(seed_from("traj.reference", pre["seed"]))
    tA = K.simulate(P, states, start, steps, rA, record_every=1)
    tB = K.simulate(Q, states, start, steps, rB, record_every=1)

    def occ_stats(t):
        tot = sum(t["occupancy"].values())
        mean_L = sum(s[0] * n for s, n in t["occupancy"].items()) / tot
        mean_lT = sum(math.log2(s[1]) * n for s, n in t["occupancy"].items()) / tot
        return mean_L, mean_lT, tot

    aL, alT, _ = occ_stats(tA)
    bL, blT, _ = occ_stats(tB)
    tvocc = 0.5 * sum(abs(tA["occupancy"][s] / steps - tB["occupancy"][s] / steps) for s in states)
    print(f"  trajectories {steps}: active meanL {aL:.3f} log2T {alT:.3f} | "
          f"reference meanL {bL:.3f} log2T {blT:.3f} | occupancy TV {tvocc:.5f}")
    print(f"  direction tallies active up/dn L {tA['length_up']}/{tA['length_down']} "
          f"T {tA['tape_up']}/{tA['tape_down']} | reference L {tB['length_up']}/{tB['length_down']} "
          f"T {tB['tape_up']}/{tB['tape_down']}")

    attribution = Counter(r["attribution"] for r in cur if abs(r["J"]) > 0)
    attribution_above = Counter(r["attribution"] for r in above)
    out = {
        "schema_version": "proteus.v0_5_kernel.v1", "mode": mode,
        "prereg_id": pre["prereg_id"], "grammar_hash": grammar.GRAMMAR_HASH,
        "runtime_hash": RUNTIME_HASH,
        "n_states": len(states), "samples_per_state": ns,
        "truncated_mass": {"max": max(trunc.values()), "mean": sum(trunc.values()) / len(trunc)},
        "live_agreement": {"median_tv": med, "max_tv": mx_tv, "tolerance": tol, "ok": agree_ok},
        "analytic_kernel_comparison": {"median_tv": med_an, "max_tv": tv_an[0]["tv_distance"],
                                       "worst_states": tv_an[:10]},
        "communicating_classes": {"n": len(classes), "n_closed": sum(closed),
                                  "largest": max(len(c) for c in classes),
                                  "singletons": sum(1 for c in classes if len(c) == 1)},
        "stationary": {"iterations": iters, "l1_delta": delta,
                       "top": [{"state": list(s), "pi": pi[s]}
                               for s in sorted(states, key=lambda x: -pi[x])[:20]],
                       "entropy_bits": -sum(p * math.log2(p) for p in pi.values() if p > 0),
                       "max_pi": max(pi.values()), "min_pi": min(pi.values())},
        "currents": {"n_pairs": len(cur), "total_abs": tot_abs, "max_abs": mx_cur,
                     "mc_noise_floor": noise_floor, "mc_noise_median": med_noise,
                     "n_above_noise_floor": len(above),
                     "attribution_all": dict(attribution),
                     "attribution_above_floor": dict(attribution_above),
                     "top_edges": sorted(cur, key=lambda r: -abs(r["J"]))[:40]},
        "reference_max_abs_current": max((abs(r["J"]) for r in curQ), default=0.0),
        "entropy_production": ep,
        "cycles": cyc,
        "trajectories": {"steps": steps, "start": list(start),
                         "active": {"mean_length": aL, "mean_log2_tape": alT,
                                    "length_up": tA["length_up"], "length_down": tA["length_down"],
                                    "tape_up": tA["tape_up"], "tape_down": tA["tape_down"],
                                    "states_visited": tA["states_visited"]},
                         "reference": {"mean_length": bL, "mean_log2_tape": blT,
                                       "length_up": tB["length_up"], "length_down": tB["length_down"],
                                       "tape_up": tB["tape_up"], "tape_down": tB["tape_down"],
                                       "states_visited": tB["states_visited"]},
                         "occupancy_tv_active_vs_reference": tvocc},
        "wall_s": time.time() - t0,
    }
    path = os.path.join(HERE, f"RESULT_KERNEL_{mode}.json")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"  wrote {path} ({out['wall_s']:.0f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
