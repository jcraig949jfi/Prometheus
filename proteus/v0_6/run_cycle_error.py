"""Measurement-error analysis of the cycle-affinity statistic (completion directive §3).

    python proteus/v0_6/run_cycle_error.py

The dual analysis showed that the LARGEST cycle affinity on K_A (+3.0007) reads +0.3178 on K_B
for the same cycle. That is a winner's curse: selecting the extreme on one kernel and reading it
on the other shows how much of the extreme was sampling noise. Reporting max|affinity| as a
finding would therefore be claim inflation, and this script measures the error instead of
asserting it.

NO NEW STATISTIC. Cycle affinity is the preregistered quantity; this is its error decomposition
across the two independently measured kernels, which is what §3 of the directive requires.

Cycle affinity is a function of P alone, so no stationary solve is needed and this is cheap.

Method. With A = T + e_A and B = T + e_B, T the true affinity and e independent noise of equal
scale s:

    Var(A - B) = 2 s^2                    =>  s = sd(A - B) / sqrt(2)
    Var(T)     = Var((A+B)/2) - s^2 / 2
    predicted corr(A,B)      = Var(T) / (Var(T) + s^2)
    predicted P(same sign)   = 1 - arccos(rho) / pi     (bivariate normal)

The predictions are then compared against the OBSERVED correlation and sign agreement. If they
match, the error model is doing real work rather than being asserted.
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


def load_counts(name, n):
    with open(os.path.join(HERE, f"COUNTS_{name}_n{n}.json"), encoding="utf-8") as f:
        d = json.load(f)
    return {tuple(json.loads(i)): {tuple(json.loads(j)): c for j, c in row.items()}
            for i, row in d["counts"].items()}


def normalise(counts):
    P = {}
    for i, row in counts.items():
        z = math.fsum(row.values())
        P[i] = {j: c / z for j, c in row.items()} if z > 0 else {i: 1.0}
    return P


def main():
    with open(os.path.join(HERE, "PREREG_V0_6.json"), encoding="utf-8") as f:
        pre = json.load(f)
    if pre["grammar_hash"] != grammar.GRAMMAR_HASH:
        print("REFUSING: grammar hash mismatch")
        return 6
    n = pre["kernel"]["samples_per_state"]
    states, _t, _r = space.regenerate_states()
    cA, cB = load_counts("K_A", n), load_counts("K_B", n)
    PA, PB = normalise(cA), normalise(cB)
    Pp = normalise({i: {j: cA[i].get(j, 0) + cB[i].get(j, 0)
                        for j in set(cA[i]) | set(cB.get(i, {}))} for i in cA})

    cycles, _tree = EQ.cycle_basis(PA, states)
    A, B, Pl, lens = [], [], [], []
    for c in cycles:
        a, b, p = EQ.cycle_affinity(PA, c), EQ.cycle_affinity(PB, c), EQ.cycle_affinity(Pp, c)
        if a is None or b is None or p is None:
            continue
        A.append(a)
        B.append(b)
        Pl.append(p)
        lens.append(len(c))
    n_c = len(A)
    diff = [a - b for a, b in zip(A, B)]
    s = statistics.stdev(diff) / math.sqrt(2.0)
    mean_ab = [(a + b) / 2 for a, b in zip(A, B)]
    var_T = max(0.0, statistics.variance(mean_ab) - s * s / 2.0)
    rho_pred = var_T / (var_T + s * s) if (var_T + s * s) > 0 else 0.0
    rho_obs = statistics.correlation(A, B)
    sign_pred = 1.0 - math.acos(max(-1.0, min(1.0, rho_pred))) / math.pi
    sign_obs = sum(1 for a, b in zip(A, B) if (a > 0) == (b > 0)) / n_c

    # winner's curse, both directions
    def curse(sel, oth, k):
        idx = sorted(range(n_c), key=lambda i: -abs(sel[i]))[:k]
        return {"k": k,
                "mean_abs_on_selecting_kernel": statistics.fmean(abs(sel[i]) for i in idx),
                "mean_abs_on_other_kernel": statistics.fmean(abs(oth[i]) for i in idx),
                "shrinkage": 1 - (statistics.fmean(abs(oth[i]) for i in idx)
                                  / statistics.fmean(abs(sel[i]) for i in idx))}

    # per-edge noise implied by the accumulated cycle noise
    mean_len = statistics.fmean(lens)
    out = {
        "schema_version": "proteus.v0_6_cycle_error.v1",
        "n_cycles": n_c, "mean_cycle_length": mean_len,
        "min_cycle_length": min(lens), "max_cycle_length": max(lens),
        "observed": {
            "sd_K_A": statistics.stdev(A), "sd_K_B": statistics.stdev(B),
            "mean_abs_K_A": statistics.fmean(abs(x) for x in A),
            "mean_abs_K_B": statistics.fmean(abs(x) for x in B),
            "mean_abs_pooled": statistics.fmean(abs(x) for x in Pl),
            "max_abs_K_A": max(abs(x) for x in A), "max_abs_K_B": max(abs(x) for x in B),
            "correlation": rho_obs, "sign_agreement": sign_obs,
            "sd_of_difference": statistics.stdev(diff),
            "median_abs_difference": sorted(abs(x) for x in diff)[n_c // 2]},
        "error_model": {
            "noise_sd_per_cycle": s,
            "implied_noise_sd_per_edge": s / math.sqrt(mean_len),
            "true_affinity_sd": math.sqrt(var_T),
            "signal_to_noise": math.sqrt(var_T) / s if s > 0 else None,
            "predicted_correlation": rho_pred, "observed_correlation": rho_obs,
            "correlation_prediction_error": abs(rho_pred - rho_obs),
            "predicted_sign_agreement": sign_pred, "observed_sign_agreement": sign_obs,
            "sign_prediction_error": abs(sign_pred - sign_obs)},
        "winners_curse": {
            "top1_K_A_value": max(A, key=abs),
            "top1_same_cycle_on_K_B": B[max(range(n_c), key=lambda i: abs(A[i]))],
            "select_on_A_read_on_B": [curse(A, B, k) for k in (1, 10, 100, 500)],
            "select_on_B_read_on_A": [curse(B, A, k) for k in (1, 10, 100, 500)]},
        "interpretation": (
            "Individual cycle affinities on a spanning-tree basis are NOT reliable: each cycle "
            "accumulates per-edge sampling error over hundreds of edges. The affinity "
            "DISTRIBUTION nevertheless carries real signal, and the error model's predicted "
            "correlation and sign agreement are checked against the observed values. Entropy "
            "production is the basis-independent statistic and is what this pass leans on."),
    }
    with open(os.path.join(HERE, "RESULT_CYCLE_ERROR.json"), "w", encoding="utf-8",
              newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    o, m = out["observed"], out["error_model"]
    print(f"cycles {n_c}, mean length {mean_len:.1f} (min {min(lens)}, max {max(lens)})")
    print(f"  noise sd/cycle {m['noise_sd_per_cycle']:.4f}  -> per edge "
          f"{m['implied_noise_sd_per_edge']:.5f}")
    print(f"  true affinity sd {m['true_affinity_sd']:.4f}  S/N "
          f"{m['signal_to_noise']:.2f}")
    print(f"  correlation predicted {m['predicted_correlation']:.4f} observed "
          f"{rho_obs:.4f}  (error {m['correlation_prediction_error']:.4f})")
    print(f"  sign agree predicted {m['predicted_sign_agreement']:.4f} observed "
          f"{sign_obs:.4f}  (error {m['sign_prediction_error']:.4f})")
    print(f"  WINNER'S CURSE: top cycle on K_A {out['winners_curse']['top1_K_A_value']:+.4f} "
          f"reads {out['winners_curse']['top1_same_cycle_on_K_B']:+.4f} on K_B")
    for r in out["winners_curse"]["select_on_A_read_on_B"]:
        print(f"    top {r['k']:>3} by |A|: mean|A| {r['mean_abs_on_selecting_kernel']:.4f} "
              f"-> mean|B| {r['mean_abs_on_other_kernel']:.4f}  shrinkage "
              f"{100*r['shrinkage']:.1f}%")
    print("wrote RESULT_CYCLE_ERROR.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
