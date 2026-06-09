"""Astraea MVP — kick the tires of the routing thesis.

A buildable end-to-end first slice that exercises ALL FIVE structural risks from
`pivot/astraea_charter_2026-05-30.md` on the existing LABS harness, before any
real-substrate commitment. Throw-away-grade by design.

Architecture (per charter §3, §4):
  Phase 1 — Generate (cheap_features, multi-falsifier KillVector) pairs.
            (Addresses Risk 5: training data is properly instrumented from the
            start, not the legacy 1-component artifact.)
  Phase 2 — Audit the FALSIFIER-LABEL correlation matrix — measure the basis
            the router routes among.
            (Addresses Risk 3: never route on an unmeasured basis.)
  Phase 3 — Train a tiny per-falsifier GradientBoostingClassifier on cheap
            features (no LLM in the deciding seat).
            (Addresses Risk 1.)
            Report per-falsifier accuracy + INFORMATION GAIN vs marginal base
            rate (not raw kill-rate accuracy — Risk 2: kill-rate-greedy
            objective concentrates).
  Phase 4 — Closed-loop bake-off: feed Astraea predictions back as a prior on
            the mutation operator, re-run MAP-Elites, compare random vs
            Astraea-biased on downstream best-F + coverage.
            (Addresses Risk 4: the only load-bearing question is whether the
            routing improves *generation*. Anything else is autopsy.)

If Phase 4 lift is zero / negative, the failure shape itself diagnoses which
risk dominated:
  - info-gain high, lift zero  → classifier learns but the loop is broken (R4)
  - info-gain zero             → cheap features don't carry the signal (R3/R5)
  - lift negative              → biased mutation is anti-correlated (R2 Goodhart)
"""
from __future__ import annotations
import json, math, os, time
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, log_loss
from sklearn.model_selection import train_test_split

from harmonia.runners.graded_qd_harness import (
    autocorr_energy, merit_factor, peak_sidelobe,
    skew_defect, run_entropy,
    random_seq, random_mutate, labs_descriptor, map_elites,
)

# ---------------- config ----------------
N = 37
N_TRAIN = 3000
N_EVALS_LOOP = 5000
EXPLORATION_EPS = 0.2          # Risk 2: explicit exploration injection
SEED = 20260530
OUT = rf"D:\Prometheus\harmonia\tmp\_astraea_mvp_n{N}.json"

# ---------------- falsifier definitions ----------------
# Four falsifiers chosen so they test distinct failure modes; orthogonality is
# MEASURED in Phase 2, not asserted.
def falsifier_outputs(s):
    n = len(s); E = autocorr_energy(s)
    F = (n * n) / (2.0 * E) if E > 0 else float("inf")
    P = peak_sidelobe(s)
    sk = skew_defect(s)
    bal = abs(int(s.sum())) / n
    return {
        "F_peak":    (P > 0.25, P),                 # peak sidelobe failure
        "F_skew":    (sk > 0.4, sk),                # skew-asymmetry failure
        "F_balance": (bal > 0.2, bal),              # DC imbalance failure
        "F_energy":  (F < 3.0, max(F, 0.0)),        # global merit-factor failure
    }, F, P, sk, bal

FALSIFIERS = ["F_peak", "F_skew", "F_balance", "F_energy"]

# ---------------- cheap features (O(n), NO autocorrelation) ----------------
def cheap_features(s):
    n = len(s); sums = int(s.sum())
    runs, cur = [], 1
    for i in range(1, n):
        if s[i] == s[i - 1]:
            cur += 1
        else:
            runs.append(cur); cur = 1
    runs.append(cur); runs = np.array(runs)
    bg = {(1,1):0,(1,-1):0,(-1,1):0,(-1,-1):0}
    for i in range(n - 1):
        bg[(int(s[i]), int(s[i + 1]))] += 1
    return {
        "balance": abs(sums) / n,
        "sum_sign": float(np.sign(sums)),
        "skew_defect_cheap": skew_defect(s),    # cheap, doesn't use autocorr
        "run_entropy_cheap": run_entropy(s),
        "n_runs": float(len(runs)),
        "max_run": float(runs.max()),
        "mean_run": float(runs.mean()),
        "n_pp": float(bg[(1, 1)]),
        "n_mm": float(bg[(-1, -1)]),
        "transitions": float(bg[(1, -1)] + bg[(-1, 1)]),
    }
FEAT_NAMES = list(cheap_features(np.ones(N)).keys())

# ---------------- Phase 1: generate training data ----------------
def gen_dataset(n_samples, rng):
    X, Y, fits = [], [], []
    for _ in range(n_samples):
        # mix random + perturbations from random parents for descriptor diversity
        s = random_seq(N, rng) if rng.random() < 0.6 else random_mutate(random_seq(N, rng), rng)
        feat = cheap_features(s)
        fal, F, _, _, _ = falsifier_outputs(s)
        X.append([feat[k] for k in FEAT_NAMES])
        Y.append([int(fal[k][0]) for k in FALSIFIERS])
        fits.append(F)
    return np.array(X), np.array(Y, dtype=int), np.array(fits)

# ---------------- Phase 4: Astraea-biased mutation ----------------
class AstraeaRouter:
    """Non-LLM learned router: per-falsifier predicted-trigger probability.
    Deciding seat is sklearn GradientBoosting; NO LLM in this seat (Risk 1)."""
    def __init__(self, clfs):
        self.clfs = clfs
    def predict_proba(self, s):
        x = np.array([[cheap_features(s)[k] for k in FEAT_NAMES]])
        return {lab: float(c.predict_proba(x)[0, 1]) for lab, c in self.clfs.items()}

def targeted_mutate(s, target, rng):
    """Targeted mutation conditional on predicted kill axis. Hand-coded for
    the MVP; the production version would LEARN this mapping. The point of
    the MVP is whether routing-informed-mutation beats random AT ALL."""
    n = len(s)
    if target == "F_balance":
        sgn = int(np.sign(s.sum()))
        cands = np.where(s == sgn)[0]
        if len(cands) > 0:
            i = int(rng.choice(cands)); c = s.copy(); c[i] *= -1; return c
    elif target == "F_skew":
        m = (n - 1) // 2
        for i in range(1, m + 1):
            if s[m + i] != ((-1) ** i) * s[m - i]:
                c = s.copy(); c[m + i] *= -1; return c
    elif target == "F_peak":
        # heuristic: identify a bit that participates in the worst-lag pair
        best_k, best_c = 1, 0
        for k in range(1, n):
            c = abs(int(np.dot(s[:n - k], s[k:])))
            if c > best_c: best_c, best_k = c, k
        # flip a random bit in the overlap region for worst k
        i = int(rng.integers(0, n - best_k))
        c = s.copy(); c[i] *= -1; return c
    # F_energy and fallback -> random
    return random_mutate(s, rng)

def make_astraea_mutate(router, eps=EXPLORATION_EPS):
    def astraea_mutate(s, rng):
        if rng.random() < eps:                  # Risk 2: explicit exploration
            return random_mutate(s, rng)
        probas = router.predict_proba(s)
        target = max(probas, key=probas.get)    # highest-probability trigger
        return targeted_mutate(s, target, rng)
    return astraea_mutate

# =========================== driver ===========================
def main():
    rng = np.random.default_rng(SEED)
    print(f"=== Astraea MVP — LABS n={N}, n_train={N_TRAIN}, n_evals_loop={N_EVALS_LOOP}, "
          f"exploration_eps={EXPLORATION_EPS} ===\n")
    rec = {"n": N, "n_train": N_TRAIN, "n_evals_loop": N_EVALS_LOOP, "eps": EXPLORATION_EPS}

    # Phase 1 — generate properly-instrumented KillVector training data
    print("=== Phase 1: generate multi-falsifier training data (Risk 5) ===")
    t0 = time.time()
    X, Y, F = gen_dataset(N_TRAIN, rng)
    print(f"  X shape: {X.shape}  Y shape: {Y.shape}  ({time.time()-t0:.1f}s)")
    trig_rates = Y.mean(axis=0)
    print("  trigger rates:", {lab: round(float(trig_rates[i]), 3) for i, lab in enumerate(FALSIFIERS)})
    survivors = (Y.sum(axis=1) == 0).sum()
    print(f"  survivors (no falsifier triggered): {survivors}/{len(Y)} = {survivors/len(Y):.3f}")
    rec["phase1"] = {"trigger_rates": {lab: float(trig_rates[i]) for i, lab in enumerate(FALSIFIERS)},
                     "survivor_frac": float(survivors / len(Y))}

    # Phase 2 — measure the basis the router routes AMONG (Risk 3)
    print("\n=== Phase 2: falsifier-label correlation (the routing basis) (Risk 3) ===")
    Cm = np.corrcoef(Y.T)
    print("        " + " ".join(f"{lab[:7]:>9s}" for lab in FALSIFIERS))
    for i, lab in enumerate(FALSIFIERS):
        print(f"{lab:9s} " + " ".join(f"{Cm[i,j]:9.3f}" for j in range(len(FALSIFIERS))))
    collin = [(FALSIFIERS[i], FALSIFIERS[j], round(float(Cm[i,j]),3))
              for i in range(len(FALSIFIERS)) for j in range(i+1, len(FALSIFIERS))
              if abs(Cm[i,j]) > 0.7]
    print(f"  collinear pairs (|corr|>0.7): {collin if collin else 'none'}")
    rec["phase2"] = {"corr": Cm.tolist(), "collinear_pairs": collin}

    # Phase 3 — train non-LLM router; measure info-gain not just accuracy (Risk 1+2)
    print("\n=== Phase 3: train per-falsifier classifier; report info-gain (Risk 1 + 2) ===")
    Xtr, Xte, Ytr, Yte = train_test_split(X, Y, test_size=0.2, random_state=42)
    clfs, accs, gains, baselines = {}, {}, {}, {}
    for i, lab in enumerate(FALSIFIERS):
        clf = GradientBoostingClassifier(n_estimators=80, max_depth=3, random_state=42)
        clf.fit(Xtr, Ytr[:, i])
        pred = clf.predict(Xte)
        if len(np.unique(Ytr[:, i])) < 2:
            acc = 1.0; H_base = 0.0; H_clf = 0.0; gain = 0.0
        else:
            proba = clf.predict_proba(Xte)
            acc = float(accuracy_score(Yte[:, i], pred))
            p = float(Ytr[:, i].mean())
            H_base = -(p * math.log(p + 1e-12) + (1 - p) * math.log(1 - p + 1e-12))
            # use clipped proba so log_loss is well-defined
            H_clf = float(log_loss(Yte[:, i], np.clip(proba[:, 1], 1e-6, 1 - 1e-6), labels=[0, 1]))
            gain = H_base - H_clf
        clfs[lab] = clf; accs[lab] = acc; gains[lab] = gain; baselines[lab] = H_base
        print(f"  {lab:9s}  acc={acc:.3f}  base_H={H_base:.3f}  clf_H={H_clf:.3f}  "
              f"info_gain={gain:+.3f}  (positive = router learns)")
    rec["phase3"] = {"accuracy": accs, "info_gain": gains, "baseline_entropy": baselines}

    # Feature importances (cheap diagnostic — which features the router relies on)
    print("\n  feature importances by falsifier:")
    for lab in FALSIFIERS:
        imp = clfs[lab].feature_importances_
        top = sorted(zip(FEAT_NAMES, imp), key=lambda kv: -kv[1])[:3]
        print(f"    {lab}: " + ", ".join(f"{k}={v:.2f}" for k, v in top))

    # Phase 4 — load-bearing test: does the loop close? (Risk 4)
    print("\n=== Phase 4: closed-loop bake-off — random vs Astraea-biased (Risk 4) ===")
    router = AstraeaRouter(clfs)
    AX = ("skew_defect", "run_entropy")
    common = dict(fitness=merit_factor, descriptor=labs_descriptor, axes=AX, init=random_seq)
    # SAME seed both arms -> matched initial conditions
    rng_r = np.random.default_rng(SEED + 100)
    rng_a = np.random.default_rng(SEED + 100)
    t0 = time.time()
    r_rand = map_elites(N, random_mutate, rng=rng_r, n_evals=N_EVALS_LOOP, **common)
    t_rand = time.time() - t0
    t0 = time.time()
    r_astr = map_elites(N, make_astraea_mutate(router), rng=rng_a, n_evals=N_EVALS_LOOP, **common)
    t_astr = time.time() - t0
    print(f"  random arm   : best_F={r_rand['best_merit_factor']:.3f}  "
          f"coverage={r_rand['coverage']:.3f}  ({t_rand:.1f}s)")
    print(f"  astraea arm  : best_F={r_astr['best_merit_factor']:.3f}  "
          f"coverage={r_astr['coverage']:.3f}  ({t_astr:.1f}s)")
    lift_F = r_astr["best_merit_factor"] - r_rand["best_merit_factor"]
    lift_cov = r_astr["coverage"] - r_rand["coverage"]
    print(f"  LIFT best_F  : {lift_F:+.3f}   LIFT coverage: {lift_cov:+.3f}")
    rec["phase4"] = {"random": {k: r_rand[k] for k in ("best_merit_factor","coverage","cells_filled")},
                     "astraea": {k: r_astr[k] for k in ("best_merit_factor","coverage","cells_filled")},
                     "lift_best_F": float(lift_F), "lift_coverage": float(lift_cov)}

    # Headline + failure-shape diagnostic (per failure-signature doctrine)
    print("\n=== HEADLINE: loop-closure verdict + failure-shape diagnostic ===")
    mean_gain = float(np.mean(list(gains.values())))
    if lift_F > 0.1:
        print(f"  LIFT POSITIVE ({lift_F:+.3f})  -> loop closed on this slice (n=1 seed).")
    elif lift_F > -0.1:
        print(f"  LIFT ~ZERO ({lift_F:+.3f})  -> no measurable closure.")
    else:
        print(f"  LIFT NEGATIVE ({lift_F:+.3f})  -> routing biases the WRONG way (Goodhart hint).")
    if mean_gain > 0.05 and lift_F < 0.1:
        print(f"  DIAGNOSTIC: info_gain mean={mean_gain:+.3f} but lift~0  -> Risk 4: classifier "
              f"learns the failure axis but the loop into mutation is broken (autopsy).")
    if mean_gain <= 0.05:
        print(f"  DIAGNOSTIC: info_gain mean={mean_gain:+.3f}  -> Risk 3/5: cheap features don't "
              f"carry the signal, or the basis is collinear.")
    if any(round(v[2], 3) is not None and abs(v[2]) > 0.7 for v in collin):
        print(f"  DIAGNOSTIC: collinear falsifier pairs present {collin}  -> basis was a costume.")
    rec["headline"] = {"lift_best_F": float(lift_F), "lift_coverage": float(lift_cov),
                       "mean_info_gain": mean_gain}

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)
    print(f"\nwrote {OUT}")

if __name__ == "__main__":
    main()
