"""Phase 5: multi-target training as a follow-up to v4's transfer kill.

Question: does training the GA on a fitness signal averaged across
multiple target tensors produce genomes that transfer to a held-out
target? Or is target-value coupling fatal regardless of training scheme?

Setup:
  Target A — original sin/cos/poly (rank 3). Used in all prior phases.
  Target C — same family, different coefficients: sin(3pi*x/N) + cos(3pi*x/N) + linear poly. Rank 3.
  Target B — Legendre-like, rank 4. HELD OUT.

Conditions:
  5A baseline:   fitness = val on A only.   Same budget as 5B.
  5B multi:      fitness = mean(val_A, val_C).   Train signal sees A and C.

After each, evaluate top-10 on the held-out target B.
Diagnostic: correlate val_B against count of F-aware ops in the genome.

Hypothesis: 5B elites have lower val_B than 5A elites (multi-target
training improves transfer). Falsifiable in either direction.
"""

import json
import os
import random
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

# Make sure the cross operator is enabled in the base module
os.environ.setdefault("ENABLE_CROSS", "1")
import evolve_tt_v4 as base

HERE = Path(__file__).parent


def build_target_C():
    ks = np.arange(base.N, dtype=float)
    phi1 = np.sin(3 * np.pi * ks / base.N)
    phi2 = np.cos(3 * np.pi * ks / base.N)
    phi3 = ks / (base.N - 1)
    T = np.zeros((base.N,) * base.D)
    for phi in (phi1, phi2, phi3):
        outer = phi
        for _ in range(base.D - 1):
            outer = np.multiply.outer(outer, phi)
        T = T + outer
    return T


def build_target_B():
    ks = np.arange(base.N, dtype=float)
    x = 2 * ks / (base.N - 1) - 1
    g1 = x
    g2 = 0.5 * (3 * x ** 2 - 1)
    g3 = 0.5 * (5 * x ** 3 - 3 * x)
    g4 = 0.125 * (35 * x ** 4 - 30 * x ** 2 + 3)
    T = np.zeros((base.N,) * base.D)
    for g in (g1, g2, g3, g4):
        outer = g
        for _ in range(base.D - 1):
            outer = np.multiply.outer(outer, g)
        T = T + outer
    return T


T_A = base.build_target()
T_C = build_target_C()
T_B = build_target_B()


def F_arrays(T):
    Xt, Xv = base.X_TRAIN, base.X_VAL
    return (T[Xt[:, 0], Xt[:, 1], Xt[:, 2], Xt[:, 3], Xt[:, 4], Xt[:, 5]],
            T[Xv[:, 0], Xv[:, 1], Xv[:, 2], Xv[:, 3], Xv[:, 4], Xv[:, 5]])


F_TRAIN_A, F_VAL_A = F_arrays(T_A)
F_TRAIN_C, F_VAL_C = F_arrays(T_C)
F_TRAIN_B, F_VAL_B = F_arrays(T_B)
NORMS = {
    "A": (float(np.linalg.norm(F_TRAIN_A)), float(np.linalg.norm(F_VAL_A))),
    "C": (float(np.linalg.norm(F_TRAIN_C)), float(np.linalg.norm(F_VAL_C))),
    "B": (float(np.linalg.norm(F_TRAIN_B)), float(np.linalg.norm(F_VAL_B))),
}
print(f"Norms (val): A={NORMS['A'][1]:.3f} C={NORMS['C'][1]:.3f} "
      f"B={NORMS['B'][1]:.3f}")


# Capture the ORIGINAL deterministic evaluator BEFORE any monkey-patching.
_ORIGINAL_EVALUATE = base.evaluate


def eval_on(genome, ft, fv, ftn, fvn):
    saved = (base.F_TRAIN, base.F_VAL, base.F_TRAIN_NORM, base.F_VAL_NORM)
    base.F_TRAIN, base.F_VAL = ft, fv
    base.F_TRAIN_NORM, base.F_VAL_NORM = ftn, fvn
    try:
        return _ORIGINAL_EVALUATE(genome)
    finally:
        base.F_TRAIN, base.F_VAL, base.F_TRAIN_NORM, base.F_VAL_NORM = saved


def eval_multi(genome):
    """Mean fitness across A and C."""
    rA = eval_on(genome, F_TRAIN_A, F_VAL_A, *NORMS["A"])
    rC = eval_on(genome, F_TRAIN_C, F_VAL_C, *NORMS["C"])
    if rA is None or rC is None:
        return None
    rank_A, tr_A, va_A, _ = rA
    rank_C, tr_C, va_C, _ = rC
    return max(rank_A, rank_C), (tr_A + tr_C) / 2.0, (va_A + va_C) / 2.0, None


def make_evaluator(mode):
    if mode == "A_only":
        return lambda g: eval_on(g, F_TRAIN_A, F_VAL_A, *NORMS["A"])
    if mode == "AC_avg":
        return eval_multi
    raise ValueError(mode)


def run_phase(mode, pop, gens, label):
    saved_eval = base.evaluate
    base.evaluate = make_evaluator(mode)
    try:
        base.rng = np.random.default_rng(base.SEED)
        random.seed(base.SEED)
        print(f"\n--- Running {label} ({mode}) ---", flush=True)
        return base.run(pop_size=pop, gens=gens, log_every=5)
    finally:
        base.evaluate = saved_eval


def f_aware_count(genome):
    return sum(1 for op in genome if op[0] in ("fit", "grad", "cross"))


def transfer_eval(genome):
    rA = eval_on(genome, F_TRAIN_A, F_VAL_A, *NORMS["A"])
    rB = eval_on(genome, F_TRAIN_B, F_VAL_B, *NORMS["B"])
    rC = eval_on(genome, F_TRAIN_C, F_VAL_C, *NORMS["C"])
    return rA, rB, rC


def analyze(archive, label):
    print(f"\n{'='*70}")
    print(f"TRANSFER ANALYSIS: {label}")
    print(f"{'='*70}")
    cells = list(archive.values())
    top10 = sorted(cells, key=lambda c: c["val_err"])[:10]

    rows = []
    for i, t in enumerate(top10):
        rA, rB, rC = transfer_eval(t["genome"])
        if rA is None or rB is None or rC is None:
            continue
        _, _, va_A, _ = rA
        _, _, va_B, _ = rB
        _, _, va_C, _ = rC
        n_aware = f_aware_count(t["genome"])
        ops = [op[0] for op in t["genome"]]
        print(f"  #{i+1:<2} len={len(ops):<2} F={n_aware} "
              f"val_A={va_A:.2e} val_C={va_C:.2e} val_B={va_B:.2e} "
              f"ops={ops}")
        rows.append({"rank": i+1, "len": len(ops), "n_F_aware": n_aware,
                     "val_A": va_A, "val_B": va_B, "val_C": va_C, "ops": ops})

    if rows:
        n_B_meaningful = sum(1 for r in rows if r["val_B"] < 0.5)
        n_C_meaningful = sum(1 for r in rows if r["val_C"] < 0.5)
        med_B = float(np.median([r["val_B"] for r in rows]))
        med_C = float(np.median([r["val_C"] for r in rows]))
        med_A = float(np.median([r["val_A"] for r in rows]))
        print(f"\n  Median val_A: {med_A:.2e}")
        print(f"  Median val_C: {med_C:.2e}  (val_B < 0.5: {n_C_meaningful}/{len(rows)})")
        print(f"  Median val_B: {med_B:.2e}  (val_B < 0.5: {n_B_meaningful}/{len(rows)})")
        if len(rows) > 3:
            naw = np.array([r["n_F_aware"] for r in rows])
            vb = np.array([r["val_B"] for r in rows])
            rho, pv = spearmanr(naw, vb)
            print(f"  Spearman(n_F_aware, val_B): rho={rho:+.2f} p={pv:.3f}")
            l = np.array([r["len"] for r in rows])
            rho2, pv2 = spearmanr(l, vb)
            print(f"  Spearman(length,    val_B): rho={rho2:+.2f} p={pv2:.3f}")
    return rows


if __name__ == "__main__":
    pop = int(os.environ.get("POP", 20))
    gens = int(os.environ.get("GENS", 20))

    print(f"Config: POP={pop} GENS={gens}")
    print(f"Operators: {base.OP_NAMES}")

    print(f"\n{'#'*70}")
    print("# PHASE 5A: baseline, train on A only")
    print(f"{'#'*70}")
    arc_5A, _ = run_phase("A_only", pop, gens, "5A")
    rows_5A = analyze(arc_5A, "Phase 5A (train on A only)")

    print(f"\n{'#'*70}")
    print("# PHASE 5B: multi-target, train on (A+C)/2")
    print(f"{'#'*70}")
    arc_5B, _ = run_phase("AC_avg", pop, gens, "5B")
    rows_5B = analyze(arc_5B, "Phase 5B (train on A+C)")

    print(f"\n{'='*70}")
    print("COMPARISON 5A vs 5B (all medians over top-10)")
    print(f"{'='*70}")
    if rows_5A and rows_5B:
        med_5A = {k: float(np.median([r[k] for r in rows_5A]))
                  for k in ("val_A", "val_B", "val_C")}
        med_5B = {k: float(np.median([r[k] for r in rows_5B]))
                  for k in ("val_A", "val_B", "val_C")}
        print(f"  val_A: 5A={med_5A['val_A']:.2e}  "
              f"5B={med_5B['val_A']:.2e}")
        print(f"  val_C: 5A={med_5A['val_C']:.2e}  "
              f"5B={med_5B['val_C']:.2e}")
        print(f"  val_B: 5A={med_5A['val_B']:.2e}  "
              f"5B={med_5B['val_B']:.2e}  "
              f"5A/5B={med_5A['val_B']/max(med_5B['val_B'],1e-15):.2f}x")
        print()
        if med_5B["val_B"] < 0.8 * med_5A["val_B"]:
            print("  >>> Multi-target training IMPROVED transfer to B")
        elif med_5B["val_B"] > 1.25 * med_5A["val_B"]:
            print("  >>> Multi-target training HURT transfer to B")
        else:
            print("  >>> No meaningful difference in transfer to B")

    out = {
        "config": {"pop": pop, "gens": gens},
        "norms": NORMS,
        "phase_5A": rows_5A,
        "phase_5B": rows_5B,
    }
    with open(HERE / "phase_5.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved: {HERE / 'phase_5.json'}")
