"""Astraea MVP v2 — the cleaned-up kick of the routing thesis.

Changes from v1 (per `pivot/astraea_charter_2026-05-30.md` §7):
  1. All falsifiers are autocorr-dependent. None is a threshold of a cheap
     feature — closes the v1 feature-label tautology that gave F_skew/F_balance
     perfect-accuracy via threshold-of-self.
  2. Targeted mutation is ROUTER-GUIDED GREEDY BIT SELECTION: try every bit
     flip, pick the one that reduces the top-predicted falsifier's
     probability most. No hand-coded directional fixes. The router's
     predictions ARE the signal.
  3. Thresholds calibrated to MEDIAN of a random sample so trigger rate ≈
     0.5 per falsifier (Risk 2 calibration gate from v1 lessons).

If lift survives v2, the thesis has a real positive datapoint on a clean test.
If lift collapses but info-gain stays positive → R4 (back-edge / loop) is the
binding constraint. If info-gain collapses → R3 (cheap features don't carry
autocorr-failure signal). Either branch is substrate-grade.
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
EXPLORATION_EPS = 0.2
SEED = 20260530
OUT = rf"D:\Prometheus\harmonia\tmp\_astraea_mvp_v2_n{N}.json"

# ---------------- autocorr-dependent falsifier inputs ----------------
def compute_autocorr_quantities(s):
    """All falsifier inputs require autocorr O(n^2). The router must predict
    these from cheap features, NOT from a thresholded function of itself."""
    n = len(s)
    C = np.array([int(np.dot(s[:n - k], s[k:])) for k in range(1, n)])
    k_star = n // 3                                 # specific-lag peak
    n_low = max(1, n // 4)                          # low-lag window
    n_high_start = max(1, 3 * n // 4)               # high-lag window
    return {
        "P":       float(np.max(np.abs(C))) / n,
        "C_kstar": float(abs(C[k_star - 1])) / n,
        "E_low":   float(np.sum(C[:n_low] ** 2)) / (n * n * n_low),
        "E_high":  float(np.sum(C[n_high_start:] ** 2)) / (n * n * max(1, n - n_high_start)),
    }

def apply_thresholds(q, thr):
    return {
        "F_peak":     (q["P"]       > thr["P"],       q["P"]),
        "F_lag_k":    (q["C_kstar"] > thr["C_kstar"], q["C_kstar"]),
        "F_low_lag":  (q["E_low"]   > thr["E_low"],   q["E_low"]),
        "F_high_lag": (q["E_high"]  > thr["E_high"],  q["E_high"]),
    }

FALSIFIERS = ["F_peak", "F_lag_k", "F_low_lag", "F_high_lag"]

# ---------------- cheap features (O(n), no autocorr) ----------------
def cheap_features(s):
    """Cheap features. INCLUDES balance and skew_defect because they're cheap
    structural quantities and (crucially) NONE of the v2 falsifiers is a
    threshold of these features. If they correlate with autocorr labels via
    math, that's signal, not tautology."""
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
        "skew_defect": skew_defect(s),
        "run_entropy": run_entropy(s),
        "n_runs": float(len(runs)),
        "max_run": float(runs.max()),
        "mean_run": float(runs.mean()),
        "std_run": float(runs.std()),
        "n_pp": float(bg[(1, 1)]),
        "n_mm": float(bg[(-1, -1)]),
        "transitions": float(bg[(1, -1)] + bg[(-1, 1)]),
        "first_run": float(runs[0]),
        "last_run": float(runs[-1]),
    }
FEAT_NAMES = list(cheap_features(np.ones(N)).keys())

# ---------------- calibration ----------------
def calibrate_thresholds(rng, n_samples=1000):
    """Set thresholds at the median of the empirical distribution so each
    falsifier triggers ~50%."""
    qs = []
    for _ in range(n_samples):
        s = random_seq(N, rng) if rng.random() < 0.6 else random_mutate(random_seq(N, rng), rng)
        qs.append(compute_autocorr_quantities(s))
    return {k: float(np.median([q[k] for q in qs])) for k in ("P", "C_kstar", "E_low", "E_high")}

# ---------------- data generation ----------------
def gen_dataset(n_samples, rng, thr):
    X, Y, fits = [], [], []
    for _ in range(n_samples):
        s = random_seq(N, rng) if rng.random() < 0.6 else random_mutate(random_seq(N, rng), rng)
        feat = cheap_features(s)
        q = compute_autocorr_quantities(s)
        fal = apply_thresholds(q, thr)
        X.append([feat[k] for k in FEAT_NAMES])
        Y.append([int(fal[k][0]) for k in FALSIFIERS])
        E = autocorr_energy(s)
        fits.append((N * N) / (2 * E) if E > 0 else float("inf"))
    return np.array(X), np.array(Y, dtype=int), np.array(fits)

# ---------------- router ----------------
class AstraeaV2Router:
    def __init__(self, clfs): self.clfs = clfs
    def predict_one(self, s, lab):
        x = np.array([[cheap_features(s)[k] for k in FEAT_NAMES]])
        return float(self.clfs[lab].predict_proba(x)[0, 1])
    def predict_all(self, s):
        x = np.array([[cheap_features(s)[k] for k in FEAT_NAMES]])
        return {lab: float(c.predict_proba(x)[0, 1]) for lab, c in self.clfs.items()}

def make_astraea_v2_mutate(router, eps=EXPLORATION_EPS):
    """Router-guided GREEDY BIT SELECTION. For each possible single-bit flip,
    query the router; pick the flip that most reduces the top-predicted
    falsifier's probability. NO hand-coded directional fixes — the router IS
    the only treatment."""
    def astraea_v2_mutate(s, rng):
        if rng.random() < eps:
            return random_mutate(s, rng)
        probas = router.predict_all(s)
        target = max(probas, key=probas.get)
        p_now = probas[target]
        clf = router.clfs[target]
        best_i, best_p = None, p_now
        for i in range(len(s)):
            child = s.copy(); child[i] *= -1
            x = np.array([[cheap_features(child)[k] for k in FEAT_NAMES]])
            new_p = float(clf.predict_proba(x)[0, 1])
            if new_p < best_p:
                best_p, best_i = new_p, i
        if best_i is None:
            return random_mutate(s, rng)
        c = s.copy(); c[best_i] *= -1
        return c
    return astraea_v2_mutate

# =========================== driver ===========================
def main():
    rng = np.random.default_rng(SEED)
    print(f"=== Astraea MVP v2 — LABS n={N} ===")
    print("v2 changes: (1) all falsifiers autocorr-dependent (no tautology)")
    print("            (2) targeted_mutate = router-guided greedy bit selection (no hand-coded fixes)")
    print("            (3) thresholds calibrated to median (~50% trigger rate per falsifier)")
    rec = {"n": N, "n_train": N_TRAIN, "n_evals_loop": N_EVALS_LOOP, "eps": EXPLORATION_EPS}

    # Phase 0 — calibration
    print("\n=== Phase 0: calibrate thresholds to median ===")
    thr = calibrate_thresholds(rng)
    print(f"  thresholds: {dict((k, round(v, 5)) for k, v in thr.items())}")
    rec["thresholds"] = thr

    # Phase 1 — generate
    print("\n=== Phase 1: generate training data ===")
    t0 = time.time()
    X, Y, F = gen_dataset(N_TRAIN, rng, thr)
    print(f"  X shape: {X.shape}  Y shape: {Y.shape}  ({time.time()-t0:.1f}s)")
    trig_rates = Y.mean(axis=0)
    print("  trigger rates:", {lab: round(float(trig_rates[i]), 3) for i, lab in enumerate(FALSIFIERS)})
    failed_gate = [lab for i, lab in enumerate(FALSIFIERS)
                   if trig_rates[i] < 0.05 or trig_rates[i] > 0.95]
    print(f"  calibration gate (5%-95%): {'PASS' if not failed_gate else 'FAIL: ' + str(failed_gate)}")
    survivors = (Y.sum(axis=1) == 0).sum()
    print(f"  survivors (no falsifier triggered): {survivors}/{len(Y)} = {survivors/len(Y):.3f}")
    rec["phase1"] = {"trigger_rates": {lab: float(trig_rates[i]) for i, lab in enumerate(FALSIFIERS)},
                     "survivor_frac": float(survivors / len(Y))}

    # Phase 2 — label-label orthogonality
    print("\n=== Phase 2: falsifier-label correlation (Risk 3) ===")
    Cm = np.corrcoef(Y.T)
    print("            " + " ".join(f"{lab[:8]:>9s}" for lab in FALSIFIERS))
    for i, lab in enumerate(FALSIFIERS):
        print(f"{lab:11s} " + " ".join(f"{Cm[i,j]:9.3f}" for j in range(len(FALSIFIERS))))
    collin = [(FALSIFIERS[i], FALSIFIERS[j], round(float(Cm[i,j]),3))
              for i in range(len(FALSIFIERS)) for j in range(i + 1, len(FALSIFIERS))
              if abs(Cm[i,j]) > 0.7]
    print(f"  collinear pairs (|corr|>0.7): {collin if collin else 'none'}")
    rec["phase2"] = {"corr": Cm.tolist(), "collinear_pairs": collin}

    # Phase 3 — train classifiers
    print("\n=== Phase 3: train per-falsifier classifier; report info-gain (Risk 1+2) ===")
    Xtr, Xte, Ytr, Yte = train_test_split(X, Y, test_size=0.2, random_state=42)
    clfs, accs, gains = {}, {}, {}
    for i, lab in enumerate(FALSIFIERS):
        clf = GradientBoostingClassifier(n_estimators=80, max_depth=3, random_state=42)
        clf.fit(Xtr, Ytr[:, i])
        if len(np.unique(Ytr[:, i])) < 2:
            acc = 1.0; H_base = 0.0; H_clf = 0.0; gain = 0.0
        else:
            proba = clf.predict_proba(Xte)
            pred = clf.predict(Xte)
            acc = float(accuracy_score(Yte[:, i], pred))
            p = float(Ytr[:, i].mean())
            H_base = -(p * math.log(p + 1e-12) + (1 - p) * math.log(1 - p + 1e-12))
            H_clf = float(log_loss(Yte[:, i], np.clip(proba[:, 1], 1e-6, 1 - 1e-6), labels=[0, 1]))
            gain = H_base - H_clf
        clfs[lab] = clf; accs[lab] = acc; gains[lab] = gain
        print(f"  {lab:11s} acc={acc:.3f}  base_H={H_base:.3f}  clf_H={H_clf:.3f}  info_gain={gain:+.3f}")
    rec["phase3"] = {"accuracy": accs, "info_gain": gains}

    print("\n  feature importances (top-3) per falsifier:")
    for lab in FALSIFIERS:
        imp = clfs[lab].feature_importances_
        top = sorted(zip(FEAT_NAMES, imp), key=lambda kv: -kv[1])[:3]
        print(f"    {lab:11s}: " + ", ".join(f"{k}={v:.2f}" for k, v in top))

    # Phase 4 — closed-loop bake-off
    print("\n=== Phase 4: closed-loop bake-off (Risk 4) ===")
    router = AstraeaV2Router(clfs)
    AX = ("skew_defect", "run_entropy")
    common = dict(fitness=merit_factor, descriptor=labs_descriptor, axes=AX, init=random_seq)

    t0 = time.time()
    r_rand = map_elites(N, random_mutate, rng=np.random.default_rng(SEED + 100),
                        n_evals=N_EVALS_LOOP, **common)
    t_rand = time.time() - t0
    t0 = time.time()
    r_astr = map_elites(N, make_astraea_v2_mutate(router),
                        rng=np.random.default_rng(SEED + 100),
                        n_evals=N_EVALS_LOOP, **common)
    t_astr = time.time() - t0
    print(f"  random arm   : best_F={r_rand['best_merit_factor']:.3f}  "
          f"coverage={r_rand['coverage']:.3f}  ({t_rand:.1f}s)")
    print(f"  astraea v2   : best_F={r_astr['best_merit_factor']:.3f}  "
          f"coverage={r_astr['coverage']:.3f}  ({t_astr:.1f}s)")
    lift_F = r_astr["best_merit_factor"] - r_rand["best_merit_factor"]
    lift_cov = r_astr["coverage"] - r_rand["coverage"]
    print(f"  LIFT best_F  : {lift_F:+.3f}   LIFT coverage: {lift_cov:+.3f}")
    rec["phase4"] = {"random": {k: r_rand[k] for k in ("best_merit_factor","coverage","cells_filled")},
                     "astraea": {k: r_astr[k] for k in ("best_merit_factor","coverage","cells_filled")},
                     "lift_best_F": float(lift_F), "lift_coverage": float(lift_cov)}

    # Failure-shape verdict
    print("\n=== HEADLINE: loop-closure verdict + failure-shape diagnostic ===")
    mean_gain = float(np.mean(list(gains.values())))
    if lift_F > 0.1:
        verdict = "POSITIVE"
        print(f"  LIFT POSITIVE ({lift_F:+.3f})  -> v2 routing thesis has a real positive datapoint")
        print(f"                                  (n=1 seed; needs replication + multi-seed audit).")
    elif lift_F > -0.1:
        verdict = "TIED"
        print(f"  LIFT ~ZERO ({lift_F:+.3f})  -> routing thesis NOT supported on this slice.")
    else:
        verdict = "NEGATIVE"
        print(f"  LIFT NEGATIVE ({lift_F:+.3f})  -> routing biases the wrong way (Goodhart hint).")
    print(f"  mean info_gain: {mean_gain:+.3f}")
    print("\n  failure-shape branches:")
    if mean_gain > 0.05 and lift_F < 0.1:
        print("    (a) info-gain > 0, lift ~0 -> Risk 4 BINDING: classifier learns the failure axis,")
        print("        but feeding the prediction into mutation doesn't transfer. Back-edge design")
        print("        is the next problem; greedy-bit-selection may be the wrong loop closure.")
    if mean_gain <= 0.05:
        print("    (b) info-gain ~0 -> Risk 3 BINDING: cheap combinatorial features don't predict")
        print("        autocorr-dependent failures. Basis itself needs re-examination.")
    if lift_F > 0.1 and mean_gain > 0.05:
        print("    (c) both positive -> the load-bearing claim holds on this slice: cheap features")
        print("        predict expensive labels, AND that prediction driving mutation lifts search.")
    rec["headline"] = {"verdict": verdict, "lift_best_F": float(lift_F),
                       "lift_coverage": float(lift_cov), "mean_info_gain": mean_gain}

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)
    print(f"\nwrote {OUT}")

if __name__ == "__main__":
    main()
