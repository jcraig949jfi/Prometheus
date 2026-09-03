"""V0.6 production run: full-space live kernel, equilibrium analysis, references, counterfactuals.

    python proteus/v0_6/run_full.py

Reads the frozen PREREG_V0_6.json (sample count, gates, tolerances) and refuses to run against
any grammar or runtime other than the preregistered ones. Writes RESULT_FULL.json.
"""
from __future__ import annotations

import json
import math
import os
import statistics
import sys
import time
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

from proteus.foundry import grammar  # noqa: E402
from proteus.foundry.affordances import AFFORDANCE_HASH  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH, hash_obj  # noqa: E402
from proteus.v0_6 import equilibrium as EQ  # noqa: E402
from proteus.v0_6 import livekernel as LK  # noqa: E402
from proteus.v0_6 import space  # noqa: E402

IW = 4


def prereg():
    with open(os.path.join(HERE, "PREREG_V0_6.json"), encoding="utf-8") as f:
        p = json.load(f)
    if p["grammar_hash"] != grammar.GRAMMAR_HASH:
        raise SystemExit("REFUSED: grammar hash differs from the preregistered v0.4 grammar")
    if p["runtime_hash"] != RUNTIME_HASH:
        raise SystemExit("REFUSED: runtime hash differs")
    return p


def kernel_from_operator_counts(OP, states, weights):
    """Rebuild P using per-operator conditional destinations and a SUPPLIED weight vector.

    With the original weights this reproduces the measured kernel; with any other weight vector it
    is the exact offline counterfactual the brief asks for. No grammar is changed.
    """
    P = {}
    for s in states:
        row = defaultdict(float)
        for op, dests in OP[s].items():
            tot = sum(dests.values())
            if tot == 0:
                continue
            w = weights.get(op, 0.0)
            if w == 0.0:
                continue
            for j, c in dests.items():
                row[j] += w * (c / tot)
        z = math.fsum(row.values())
        P[s] = {j: v / z for j, v in row.items()} if z > 0 else {s: 1.0}
    return P


def _persist(states, P, n, name):
    """Write integer transition counts as soon as a kernel exists.

    The n=12,000 attempt discarded 100 minutes of measurement because the counts were only
    written after the gates. Persisting here means a gate failure never destroys the compute and
    a later higher-power run can pool batches instead of restarting.
    """
    counts = LK.counts_from(P, n)
    with open(os.path.join(HERE, f"COUNTS_{name}_n{n}.json"), "w", encoding="utf-8",
              newline="\n") as f:
        json.dump({"samples_per_state": n,
                   "counts": {repr(list(i)): {repr(list(j)): c for j, c in sorted(row.items())}
                              for i, row in sorted(counts.items())}},
                  f, sort_keys=True, separators=(",", ":"))
        f.write("\n")


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


def main():
    pre = prereg()
    n = pre["kernel"]["samples_per_state"]
    t0 = time.time()
    states, tapes, rules = space.regenerate_states()
    print(f"V0.6 full run | {len(states)} states | n={n:,}/state | grammar "
          f"{grammar.GRAMMAR_HASH[:12]}")

    PA, OPA, NOOPA, ESCA = LK.measure_kernel_parallel(states, n, pre["seed_a"], "K_A")
    print(f"  K_A measured ({time.time()-t0:.0f}s)")
    _persist(states, PA, n, "K_A")
    PB, OPB, NOOPB, ESCB = LK.measure_kernel_parallel(states, n, pre["seed_b"], "K_B")
    print(f"  K_B measured ({time.time()-t0:.0f}s)")
    _persist(states, PB, n, "K_B")

    esc = sum(sum(r.values()) for r in ESCA.values()) + sum(sum(r.values()) for r in ESCB.values())

    tv = sorted(LK.compare(PA, PB, states))
    m = len(tv)
    rep = {"median": tv[m // 2], "mean": statistics.fmean(tv), "p90": tv[int(0.90 * m)],
           "p95": tv[int(0.95 * m)], "p99": tv[min(m - 1, int(0.99 * m))], "max": tv[-1]}
    gate = pre["gates"]["kernel_precision"]
    rep["gate_median_ok"] = rep["median"] <= gate["median_row_tv_max"]
    rep["gate_p95_ok"] = rep["p95"] <= gate["p95_row_tv_max"]
    rep["passed"] = rep["gate_median_ok"] and rep["gate_p95_ok"]
    # edge-presence disagreement
    epd = sum(len(set(PA[s]) ^ set(PB[s])) for s in states)
    rep["edge_presence_disagreements"] = epd
    print(f"  K_A/K_B row TV: median {rep['median']:.5f} p95 {rep['p95']:.5f} max {rep['max']:.5f}"
          f" -> gate {'PASS' if rep['passed'] else 'FAIL'} | edge-presence diffs {epd}")

    result = {"schema_version": "proteus.v0_6_full.v1", "prereg_id": pre["prereg_id"],
              "identities": {"grammar_version": grammar.GRAMMAR_VERSION,
                             "grammar_hash": grammar.GRAMMAR_HASH,
                             "runtime_hash": RUNTIME_HASH,
                             "affordance_hash": AFFORDANCE_HASH,
                             "space_hash": space.space_identity(states)["hash"],
                             "manifest_schema_hash": rules["schema_hash"]},
              "n_states": len(states), "samples_per_state": n,
              "escaped_valid_structural_states": esc,
              "reproducibility": rep}

    if not rep["passed"]:
        result["classification_note"] = "FULL_SPACE_KERNEL_UNDERPOWERED"
        with open(os.path.join(HERE, "RESULT_FULL.json"), "w", encoding="utf-8",
                  newline="\n") as f:
            json.dump(result, f, indent=1, sort_keys=True)
            f.write("\n")
        print("  GATE FAILED -- stopping before any substantive quantity is computed")
        return 3

    # ---- stationary, three methods, on the adjudicated kernel K_A
    piP, mP = EQ.stationary_power(PA, states, tol=pre["gates"]["stationary"]["power_tol"])
    print(f"  stationary power: {mP['iterations']} iters residual {mP['residual_l1']:.3e} "
          f"({time.time()-t0:.0f}s)")
    piG, mG = EQ.stationary_gauss_seidel(PA, states, tol=pre["gates"]["stationary"]["gs_tol"])
    print(f"  stationary gauss-seidel: {mG['iterations']} iters residual "
          f"{mG['residual_l1']:.3e} ({time.time()-t0:.0f}s)")
    piE, mE = EQ.stationary_empirical(PA, states, pre["gates"]["stationary"]["empirical_steps"],
                                      pre["seed_a"])
    agree_PG = EQ.compare_pi(piP, piG, states)
    agree_PE = EQ.compare_pi(piP, piE, states)
    st_gate = (mP["residual_l1"] <= pre["gates"]["stationary"]["residual_l1_max"]
               and agree_PG["l1"] <= pre["gates"]["stationary"]["solver_agreement_l1_max"])
    print(f"  solver agreement power vs GS: L1 {agree_PG['l1']:.3e} | vs empirical L1 "
          f"{agree_PE['l1']:.3e} -> gate {'PASS' if st_gate else 'FAIL'}")

    classes = EQ.communicating_classes(PA, states)
    closed = EQ.closed_classes(PA, classes)
    gap = EQ.spectral_gap(PA, states, piP)

    result["stationary"] = {
        "power": mP, "gauss_seidel": mG, "empirical": mE,
        "agreement_power_vs_gs": agree_PG, "agreement_power_vs_empirical": agree_PE,
        "gate_passed": st_gate,
        "communicating_classes": {"n": len(classes), "n_closed": sum(closed),
                                  "largest": max(len(c) for c in classes),
                                  "transient_states": sum(len(c) for c, cl in zip(classes, closed)
                                                          if not cl)},
        "spectral": gap,
        "min_pi": min(piP.values()), "max_pi": max(piP.values()),
        "entropy_bits": -math.fsum(p * math.log2(p) for p in piP.values() if p > 0),
        "top": [{"state": list(s), "pi": piP[s]}
                for s in sorted(states, key=lambda x: -piP[x])[:20]],
    }
    if not st_gate:
        result["classification_note"] = "STATIONARY_SOLVE_FAILED"
        with open(os.path.join(HERE, "RESULT_FULL.json"), "w", encoding="utf-8",
                  newline="\n") as f:
            json.dump(result, f, indent=1, sort_keys=True)
            f.write("\n")
        return 4

    # ---- currents on K_A and K_B separately, then the noise model
    piB, _mB = EQ.stationary_power(PB, states, tol=pre["gates"]["stationary"]["power_tol"])
    curA = EQ.currents(PA, piP, states)
    curB = EQ.currents(PB, piB, states)
    sA, sB = EQ.current_summary(curA, piP), EQ.current_summary(curB, piB)
    mapB = {(r["i"], r["j"]): r["J"] for r in curB}
    diffs = [abs(r["J"] - mapB.get((r["i"], r["j"]), 0.0)) for r in curA]
    dsort = sorted(diffs)
    noise = {"median": dsort[len(dsort) // 2], "p95": dsort[int(0.95 * len(dsort))],
             "p99": dsort[min(len(dsort) - 1, int(0.99 * len(dsort)))], "max": dsort[-1],
             "rule": pre["gates"]["current"]["material_rule"]}
    thr = noise["p99"] * pre["gates"]["current"]["material_multiplier"]
    material = [r for r in curA if abs(r["J"]) > thr]
    print(f"  currents K_A: total|J| {sA['total_abs']:.4e} max {sA['max_abs']:.4e} | "
          f"K_B total {sB['total_abs']:.4e} | noise p99 {noise['p99']:.3e} thr {thr:.3e} | "
          f"material {len(material)}")

    # ---- detailed balance: global statistic
    fluxes = [(r["f_ij"], r["f_ji"]) for r in curA]
    db_global = math.fsum(abs(a - b) for a, b in fluxes)
    db_rel = db_global / math.fsum(a + b for a, b in fluxes)

    ep = EQ.entropy_production(PA, piP, states)
    epB = EQ.entropy_production(PB, piB, states)

    # entropy production by region and by operator
    by_region = Counter()
    for (i, j), t in ep["_by_edge"]:
        by_region[region(i)] += t
    op_flux = defaultdict(float)
    for s in states:
        for op, dests in OPA[s].items():
            for j, c in dests.items():
                if j != s:
                    op_flux[op] += piP[s] * (c / n)
    ep.pop("_by_edge", None)

    # ---- cycle basis
    cycles, tree_edges = EQ.cycle_basis(PA, states)
    affs = []
    for cyc in cycles:
        a = EQ.cycle_affinity(PA, cyc)
        if a is not None:
            affs.append((abs(a), a, cyc))
    affs.sort(key=lambda t: -t[0])
    aff_vals = [a for _abs, a, _c in affs]
    cyc_stats = {"n_basis_cycles": len(cycles), "n_evaluable": len(affs),
                 "tree_edges": tree_edges,
                 "max_abs_affinity": affs[0][0] if affs else 0.0,
                 "median_abs_affinity": (sorted(abs(x) for x in aff_vals)[len(aff_vals) // 2]
                                         if aff_vals else 0.0),
                 "frac_abs_gt_0p01": (sum(1 for x in aff_vals if abs(x) > 0.01) / len(aff_vals))
                 if aff_vals else 0.0,
                 "witnesses": [{"cycle": [list(s) for s in c], "affinity": a}
                               for _ab, a, c in affs[:10]]}

    # ---- reversible references
    Qadd = EQ.reversible_additive(PA, piP, states)
    curQ = EQ.currents(Qadd, piP, states)
    epQ = EQ.entropy_production(Qadd, piP, states)
    epQ.pop("_by_edge", None)
    cycQ, _ = EQ.cycle_basis(Qadd, states)
    affQ = [abs(EQ.cycle_affinity(Qadd, c) or 0.0) for c in cycQ[:2000]]
    Qmet, tgt = EQ.reversible_metropolis(PA, states)
    piM, mM = EQ.stationary_power(Qmet, states, tol=1e-14)
    curM = EQ.currents(Qmet, piM, states)
    epM = EQ.entropy_production(Qmet, piM, states)
    epM.pop("_by_edge", None)
    ref = {"additive": {"max_abs_current": max((abs(r["J"]) for r in curQ), default=0.0),
                        "total_abs_current": math.fsum(abs(r["J"]) for r in curQ),
                        "sigma": epQ["sigma"], "max_abs_cycle_affinity": max(affQ) if affQ else 0.0,
                        "targets": "the measured stationary distribution of the active kernel"},
           "metropolis_uniform": {"max_abs_current": max((abs(r["J"]) for r in curM), default=0.0),
                                  "total_abs_current": math.fsum(abs(r["J"]) for r in curM),
                                  "sigma": epM["sigma"],
                                  "pi_max_dev_from_uniform": max(abs(piM[s] - tgt[s])
                                                                 for s in states),
                                  "targets": "uniform over the valid states (declared)"}}
    ref_ok = (ref["additive"]["max_abs_current"] <= thr
              and abs(ref["additive"]["sigma"]) <= pre["gates"]["reference"]["sigma_max"]
              and ref["metropolis_uniform"]["max_abs_current"] <= thr)
    print(f"  reference additive max|J| {ref['additive']['max_abs_current']:.2e} sigma "
          f"{ref['additive']['sigma']:.2e} | metropolis max|J| "
          f"{ref['metropolis_uniform']['max_abs_current']:.2e} -> "
          f"{'PASS' if ref_ok else 'FAIL'}")

    # ---- counterfactual operator reweighting (offline; no grammar changed)
    W = dict(zip(grammar.NAMES, grammar.WEIGHTS))
    P_reproduced = kernel_from_operator_counts(OPA, states, W)
    tv_repro = sorted(LK.row_tv(PA[s], P_reproduced[s]) for s in states)
    cf = {"reconstruction_check_median_tv": tv_repro[len(tv_repro) // 2],
          "reconstruction_check_max_tv": tv_repro[-1], "variants": {}}
    variants = {
        "length_balanced": dict(W, insertion=0.0982, deletion=0.0982, duplication=0.0417,
                                unreachable_removal=0.0),
        "no_unreachable_removal": dict(W, unreachable_removal=0.0),
        "no_config_perturbation": dict(W, config_perturbation=0.0),
        "insertion_deletion_equal": dict(W, insertion=0.0990, deletion=0.0990),
    }
    for name, w in variants.items():
        z = sum(w.values())
        w = {k: v / z for k, v in w.items()}
        Pv = kernel_from_operator_counts(OPA, states, w)
        piv, mv = EQ.stationary_power(Pv, states, tol=1e-13)
        cv = EQ.currents(Pv, piv, states)
        ev = EQ.entropy_production(Pv, piv, states)
        ev.pop("_by_edge", None)
        cf["variants"][name] = {"weights": w, "total_abs_current":
                                math.fsum(abs(r["J"]) for r in cv),
                                "max_abs_current": max((abs(r["J"]) for r in cv), default=0.0),
                                "sigma": ev["sigma"], "residual": mv["residual_l1"]}
        print(f"  counterfactual {name:<26} total|J| "
              f"{cf['variants'][name]['total_abs_current']:.4e} sigma "
              f"{cf['variants'][name]['sigma']:.4e}")

    # ---- matched long-run trajectories, active vs reversible additive reference (section 15)
    traj = {}
    steps = pre["gates"]["trajectory_steps"]
    for name, K, pk in (("active", PA, piP), ("reversible_additive", Qadd, piP)):
        occ, meta = EQ.stationary_empirical(K, states, steps, pre["seed_a"] + 77)
        mL = math.fsum(s_[0] * occ[s_] for s_ in states)
        mT = math.fsum(math.log2(s_[1]) * occ[s_] for s_ in states)
        traj[name] = {"steps": steps, "mean_length": mL, "mean_log2_tape": mT,
                      "states_visited": sum(1 for s_ in states if occ[s_] > 0),
                      "tv_vs_pi": 0.5 * math.fsum(abs(occ[s_] - pk[s_]) for s_ in states)}
    traj["occupancy_tv_active_vs_reference"] = None
    print(f"  trajectories {steps:,}: active meanL {traj['active']['mean_length']:.3f} "
          f"log2T {traj['active']['mean_log2_tape']:.3f} | reference meanL "
          f"{traj['reversible_additive']['mean_length']:.3f} "
          f"log2T {traj['reversible_additive']['mean_log2_tape']:.3f}")

    # persist the adjudicated kernels so replay and later analysis need not re-measure
    with open(os.path.join(HERE, "KERNEL_K_A.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"states": [list(s_) for s_ in states], "samples_per_state": n,
                   "counts": {repr(list(i)): {repr(list(j)): int(round(v * n))
                                              for j, v in PA[i].items()} for i in states}},
                  f, sort_keys=True, separators=(",", ":"))
        f.write("\n")

    result.update({
        "trajectories": traj,
        "currents": {"K_A": sA, "K_B": sB,
                     "noise_model": noise, "material_threshold": thr,
                     "n_material": len(material),
                     "material_by_region": dict(Counter(region(r["i"]) for r in material)),
                     "top_edges": [{"i": list(r["i"]), "j": list(r["j"]), "J": r["J"],
                                    "region": region(r["i"])}
                                   for r in sorted(curA, key=lambda r: -abs(r["J"]))[:40]]},
        "detailed_balance": {"global_abs_flux_imbalance": db_global,
                             "relative_imbalance": db_rel,
                             "K_B_global": math.fsum(abs(r["f_ij"] - r["f_ji"]) for r in curB)},
        "entropy_production": {"K_A": ep, "K_B_sigma": epB["sigma"],
                               "by_region": dict(by_region),
                               "operator_outflux_share": {k: v / math.fsum(op_flux.values())
                                                          for k, v in sorted(op_flux.items())}},
        "cycles": cyc_stats,
        "reversible_references": ref, "reference_gate_passed": ref_ok,
        "counterfactual": cf,
        "wall_s": time.time() - t0,
    })
    with open(os.path.join(HERE, "RESULT_FULL.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"  sigma K_A {ep['sigma']:.6e} (K_B {epB['sigma']:.6e}) one-way {ep['one_way_edges']}")
    print(f"  cycles: {cyc_stats['n_evaluable']} basis, max|affinity| "
          f"{cyc_stats['max_abs_affinity']:.4f}")
    print(f"wrote RESULT_FULL.json ({result['wall_s']:.0f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
