"""D003-04 analysis (NOT RUN by its author -- the worker could not execute code).

Two computations the question needs and the repository does not contain:

  PART A  MINIMUM DETECTABLE CURRENT (Harmonia ruling P-1) for the V0.5 primary geometry
          (124 states, 50,000 samples/state). A known cyclic current of amplitude eps is
          injected into the reversible reference Q; the perturbed kernel is then SAMPLED
          (multinomial, samples/state as in run_kernel.py) twice, independently, and passed
          through the SAME floor logic as run_kernel.py lines 126-138. MDC = smallest eps whose
          injected edges are recovered above the floor in >= 95% of replicates. Also
          applies the P-2 floor guard.

  PART B  OPERATIONAL CONSEQUENCE UNDER SELECTION. At zero selection the active kernel P and its
          reversible reference Q share pi by construction (V0.6 packet section M(i)), so no
          stationary comparison between them can show bias. Under selection they need not:
          for a reversible mutation kernel the SSWM stationary law is pi_mut * g(f); for a
          non-reversible one it is not. We build the SSWM chain M_ij = P_ij * fix(f_j - f_i)
          (and the same for Q) for preregistered fitness slopes on genome length, and compare
          stationary mean length and TV. The noise scale is the same statistic computed
          between the two independent kernel samples P_A and P_B.

Inputs (by repo path @ b960d1a42600e17128f6270282b30e8e6abb5086):
  proteus/v0_5/kernel.py            measure_kernel, stationary, currents, reversible_reference
  proteus/v0_5/PREREG_V0_5.json     seed, primary_tapes, primary_max_len, primary_samples
  proteus/v0_5/RESULT_KERNEL_primary.json   cross-check: floor 4.156e-05, 166 above, sigma 9.975e-03

Run from the repo root in a NON-canonical workspace (proteus.workspace refusal guard applies).

DECISION RULES (fixed here, before any run):
  A. Report MDC (in units of |J| per edge). A profile reading is then DETECTED / NOT_DETECTED_ABOVE(MDC)
     / INDETERMINATE (floor == 0 or seed_B == seed_A). If MDC > 1.4418e-03-scale residual currents
     (V0.6 no_unreachable_removal) the instrument cannot certify profiles as comparable at that level.
  B. For each slope s: delta_L = |E_sel(P)[L] - E_sel(Q)[L]|, noise_L = |E_sel(P_A)[L] - E_sel(P_B)[L]|.
     CONSEQUENTIAL if delta_L > 3 * noise_L AND delta_L >= 1 instruction at any slope;
     NEGLIGIBLE if delta_L <= noise_L at every slope; otherwise INDETERMINATE.
     This is a mutation-selection-equilibrium statement, not a campaign-horizon one (see REPORT).
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

ROOT = os.getcwd()
sys.path.insert(0, ROOT)
from proteus.v0_5 import kernel as K  # noqa: E402  (read-only use)

EPS_GRID = [1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 3e-6]
N_REP = 20
SLOPES = [-0.05, -0.02, -0.01, 0.0, 0.01, 0.02, 0.05]   # fitness per instruction of length
POP_N = 100                                              # SSWM effective population size


def load_prereg():
    with open(os.path.join(ROOT, "proteus", "v0_5", "PREREG_V0_5.json"), encoding="utf-8") as f:
        return json.load(f)


def floor_logic(cur, cur2):
    """Verbatim semantics of run_kernel.py 126-138."""
    c2 = {(tuple(r["i"]), tuple(r["j"])): r["J"] for r in cur2}
    noise = [abs(r["J"] - c2.get((tuple(r["i"]), tuple(r["j"])), 0.0)) for r in cur]
    return (max(noise) if noise else 0.0), c2


def sample_kernel(Pexact, states, ns, rng):
    out = {}
    for s in states:
        ks = list(Pexact[s].keys())
        ps = np.clip(np.array([Pexact[s][k] for k in ks], dtype=float), 0, None)
        ps = ps / ps.sum()
        cnt = rng.multinomial(ns, ps)
        out[s] = {k: c / ns for k, c in zip(ks, cnt) if c > 0}
    return out


def inject_cycles(Q, states, pi, eps):
    """Add a circulating current on edge-disjoint directed 3-cycles found on Q's support.
    Injection is in FLUX units: pi_x dQ_xy = +eps, pi_y dQ_yx = -eps (self-loops absorb the
    row change), so each injected edge carries J = 2*eps and pi is preserved exactly because
    every cycle node is head of one leg and tail of another."""
    Qp = {i: dict(r) for i, r in Q.items()}
    idx = set(states)
    injected = []
    used = set()
    for a in states:
        for b in list(Q[a]):
            if b == a or b not in idx:
                continue
            for c in list(Q[b]):
                if c in (a, b) or c not in idx or a not in Q[c]:
                    continue
                key = frozenset((a, b, c))
                if key in used or any(frozenset(e) in {frozenset(x) for x in injected}
                                      for e in ((a, b), (b, c), (c, a))):
                    continue
                legs = [(a, b), (b, c), (c, a)]
                ok = all(Qp[x].get(y, 0) * pi[x] > 2 * eps and Qp[y].get(x, 0) * pi[y] > 2 * eps
                         for x, y in legs)
                if not ok:
                    continue
                for x, y in legs:
                    Qp[x][y] += eps / pi[x]
                    Qp[y][x] -= eps / pi[y]
                used.add(key)
                injected.extend(legs)
    for i in Qp:
        s = sum(v for j, v in Qp[i].items() if j != i)
        Qp[i][i] = 1.0 - s
    return Qp, injected


def part_a(P, states, ns, seed):
    pi, _, _ = K.stationary(P, states)
    Q = K.reversible_reference(P, pi, states)
    rows = []
    for eps in EPS_GRID:
        Qp, inj = inject_cycles(Q, states, pi, eps)
        if not inj:
            rows.append({"eps": eps, "n_injected_edges": 0})
            continue
        hits = []
        floors = []
        for rep in range(N_REP):
            rA = np.random.default_rng([seed, int(eps * 1e9), rep, 0])
            rB = np.random.default_rng([seed, int(eps * 1e9), rep, 1])
            PA, PB = sample_kernel(Qp, states, ns, rA), sample_kernel(Qp, states, ns, rB)
            piA, _, _ = K.stationary(PA, states)
            piB, _, _ = K.stationary(PB, states)
            cA, cB = K.currents(PA, piA, states), K.currents(PB, piB, states)
            floor, _ = floor_logic(cA, cB)
            if floor == 0.0:
                hits.append(None)          # P-2: INDETERMINATE
                continue
            byk = {(tuple(r["i"]), tuple(r["j"])): r["J"] for r in cA}
            got = [abs(byk.get((x, y), byk.get((y, x), 0.0))) > floor for x, y in inj]
            hits.append(sum(got) / len(got))
            floors.append(floor)
        valid = [h for h in hits if h is not None]
        rows.append({"eps": eps, "n_injected_edges": len(inj),
                     "mean_fraction_recovered_above_floor": float(np.mean(valid)) if valid else None,
                     "frac_reps_all_recovered_ge_0.95": float(np.mean([h >= 0.95 for h in valid])) if valid else None,
                     "median_floor": float(np.median(floors)) if floors else None,
                     "n_indeterminate": hits.count(None)})
    detect = [r["eps"] for r in rows if (r.get("frac_reps_all_recovered_ge_0.95") or 0) >= 0.95]
    return {"rows": rows, "MDC_flux_units": min(detect) if detect else None}


def fix_prob(ds):
    if abs(ds) < 1e-12:
        return 1.0 / POP_N
    return (1 - math.exp(-2 * ds)) / (1 - math.exp(-2 * POP_N * ds))


def sswm(P, states, slope):
    M = {}
    for i in states:
        row = {}
        for j, p in P[i].items():
            if j != i:
                row[j] = p * POP_N * fix_prob(slope * (j[0] - i[0]))
        s = sum(row.values())
        if s > 1:
            row = {k: v / s for k, v in row.items()}
            s = 1.0
        row[i] = 1 - s
        M[i] = row
    pi, _, _ = K.stationary(M, states)
    return pi


def part_b(PA, PB, states):
    piA, _, _ = K.stationary(PA, states)
    QA = K.reversible_reference(PA, piA, states)
    out = []
    for s in SLOPES:
        a, b, q = sswm(PA, states, s), sswm(PB, states, s), sswm(QA, states, s)
        mL = lambda d: sum(st[0] * p for st, p in d.items())  # noqa: E731
        tv = lambda x, y: 0.5 * sum(abs(x[k] - y[k]) for k in states)  # noqa: E731
        out.append({"slope": s, "meanL_active": mL(a), "meanL_reversible_ref": mL(q),
                    "delta_L": abs(mL(a) - mL(q)), "noise_L": abs(mL(a) - mL(b)),
                    "tv_active_vs_ref": tv(a, q), "tv_A_vs_B": tv(a, b)})
    cons = any(r["delta_L"] > 3 * r["noise_L"] and r["delta_L"] >= 1 for r in out)
    negl = all(r["delta_L"] <= r["noise_L"] for r in out)
    return {"rows": out, "verdict": "CONSEQUENTIAL" if cons else ("NEGLIGIBLE" if negl else "INDETERMINATE")}


def main():
    pre = load_prereg()
    kc = pre["kernel"]
    states = K.state_space(tuple(kc["primary_tapes"]), kc["primary_max_len"])
    ns = kc["primary_samples"]
    PA, _, _ = K.measure_kernel(states, ns, pre["seed"], "primary.A")
    PB, _, _ = K.measure_kernel(states, ns, pre["seed"] + 1, "primary.B")
    res = {"n_states": len(states), "samples_per_state": ns,
           "part_a_mdc": part_a(PA, states, ns, pre["seed"]),
           "part_b_selection": part_b(PA, PB, states)}
    print(json.dumps(res, indent=1, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
