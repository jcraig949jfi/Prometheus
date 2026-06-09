"""Astraea MVP v3 — three fixes from v2 + 3-seed replication.

Changes from v2 (lessons from `pivot/astraea_charter_2026-05-30.md` §6):

  1. **Trusted-set audit.** After training, drop any falsifier whose holdout
     info-gain ≤ TRUSTED_THRESH (default 0.02). The router does NOT route on
     classifiers it can't beat the marginal baseline on — "the router should
     know what it doesn't know." Untrusted axes get the random-mutate fallback,
     not noisy routing.

  2. **Stochastic falsifier targeting.** Replace v2's argmax(probas) with
     categorical sampling weighted by predicted probabilities. Concentration
     (Goodhart, R2) was partially binding in v2 because greedy-pick-max routes
     ALL non-exploration mutations toward the single top-predicted axis.
     Stochastic targeting preserves coverage while still biasing toward likely
     triggers.

  3. **Confidence-conditional fallback.** If max(trusted predicted probability)
     < CONFIDENCE_THRESH (default 0.5), the router is uncertain — fall back to
     random mutation rather than committing to a possibly-wrong target.

  4. **3-seed replication.** Random and Astraea arms both run on seeds
     [SEED+100, +200, +300]; report mean lift ± std lift. Robust-to-seed test.

  5. **Telemetry per mutation.** Logs which target was sampled, confidence,
     whether router fell back. Audit at end: did routing-active mutations
     differ from fallback in outcome?

If lift survives v3 with mean - std > 0 across 3 seeds, the thesis has a
replicated positive datapoint on a clean test. If coverage no longer regresses
under stochastic targeting, R2 is closable. If lift collapses to ~0 under the
trusted-set audit, the predictable subset alone isn't enough to drive
generation — and that's substrate-grade information.
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
from harmonia.runners.astraea_mvp_v2 import (
    N, FALSIFIERS, FEAT_NAMES, cheap_features,
    compute_autocorr_quantities, apply_thresholds,
    calibrate_thresholds, gen_dataset,
)

# ---------------- v3 config ----------------
N_TRAIN = 3000
N_EVALS_LOOP = 5000
EXPLORATION_EPS = 0.2
TRUSTED_THRESH = 0.02          # info-gain floor for inclusion in routing
CONFIDENCE_THRESH = 0.5        # max(predicted prob) below this -> random fallback
SEEDS = [100, 200, 300]        # 3-seed replication (added to base SEED)
SEED = 20260530
OUT = rf"D:\Prometheus\harmonia\tmp\_astraea_mvp_v3_n{N}.json"

# ---------------- router ----------------
class AstraeaV3Router:
    def __init__(self, clfs, trusted):
        self.clfs = clfs
        self.trusted = trusted              # list of falsifier names with info-gain > thresh
    def predict_trusted(self, s):
        if not self.trusted:
            return {}
        x = np.array([[cheap_features(s)[k] for k in FEAT_NAMES]])
        return {lab: float(self.clfs[lab].predict_proba(x)[0, 1]) for lab in self.trusted}

def make_astraea_v3_mutate(router, telemetry, eps=EXPLORATION_EPS,
                           conf_thresh=CONFIDENCE_THRESH):
    def astraea_v3_mutate(s, rng):
        # ε-greedy exploration
        if rng.random() < eps or not router.trusted:
            telemetry["explore"] += 1
            return random_mutate(s, rng)
        probas = router.predict_trusted(s)
        max_p = max(probas.values())
        # Confidence-conditional fallback
        if max_p < conf_thresh:
            telemetry["low_conf_fallback"] += 1
            return random_mutate(s, rng)
        # Stochastic target sampling (weighted by predicted prob)
        labels = list(probas.keys())
        weights = np.array([probas[l] for l in labels])
        weights = weights / weights.sum()
        target = labels[int(rng.choice(len(labels), p=weights))]
        telemetry["target_counts"][target] = telemetry["target_counts"].get(target, 0) + 1
        clf = router.clfs[target]
        p_now = probas[target]
        # Greedy bit selection toward reducing target's predicted probability
        best_i, best_p = None, p_now
        for i in range(len(s)):
            child = s.copy(); child[i] *= -1
            x = np.array([[cheap_features(child)[k] for k in FEAT_NAMES]])
            new_p = float(clf.predict_proba(x)[0, 1])
            if new_p < best_p:
                best_p, best_i = new_p, i
        if best_i is None:
            telemetry["no_improvement_fallback"] += 1
            return random_mutate(s, rng)
        telemetry["routed"] += 1
        c = s.copy(); c[best_i] *= -1
        return c
    return astraea_v3_mutate

# =========================== driver ===========================
def train_router(rng, thr):
    X, Y, _ = gen_dataset(N_TRAIN, rng, thr)
    Xtr, Xte, Ytr, Yte = train_test_split(X, Y, test_size=0.2, random_state=42)
    clfs, gains, accs = {}, {}, {}
    for i, lab in enumerate(FALSIFIERS):
        clf = GradientBoostingClassifier(n_estimators=80, max_depth=3, random_state=42)
        clf.fit(Xtr, Ytr[:, i])
        if len(np.unique(Ytr[:, i])) < 2:
            acc, H_base, H_clf, gain = 1.0, 0.0, 0.0, 0.0
        else:
            proba = clf.predict_proba(Xte); pred = clf.predict(Xte)
            acc = float(accuracy_score(Yte[:, i], pred))
            p = float(Ytr[:, i].mean())
            H_base = -(p * math.log(p + 1e-12) + (1 - p) * math.log(1 - p + 1e-12))
            H_clf = float(log_loss(Yte[:, i], np.clip(proba[:, 1], 1e-6, 1 - 1e-6), labels=[0, 1]))
            gain = H_base - H_clf
        clfs[lab] = clf; gains[lab] = gain; accs[lab] = acc
    return clfs, gains, accs

def main():
    rng = np.random.default_rng(SEED)
    print(f"=== Astraea MVP v3 — LABS n={N}, 3-seed replication ===")
    print("v3 fixes: trusted-set audit + stochastic targeting + confidence-conditional fallback")
    rec = {"n": N, "n_train": N_TRAIN, "n_evals_loop": N_EVALS_LOOP,
           "eps": EXPLORATION_EPS, "trusted_thresh": TRUSTED_THRESH,
           "confidence_thresh": CONFIDENCE_THRESH, "seeds": SEEDS}

    # Phase 0 — calibrate thresholds
    print("\n=== Phase 0: calibrate thresholds ===")
    thr = calibrate_thresholds(rng)
    print(f"  thresholds: {dict((k, round(v, 5)) for k, v in thr.items())}")

    # Phase 1 — train + audit trusted set (Risk 3 fix)
    print("\n=== Phase 1: train classifiers + audit trusted set ===")
    clfs, gains, accs = train_router(rng, thr)
    trusted = [lab for lab in FALSIFIERS if gains[lab] > TRUSTED_THRESH]
    untrusted = [lab for lab in FALSIFIERS if lab not in trusted]
    print(f"  per-falsifier info-gain:")
    for lab in FALSIFIERS:
        flag = "  TRUSTED" if lab in trusted else "  --- dropped (info-gain ≤ thresh)"
        print(f"    {lab:11s} info_gain={gains[lab]:+.3f}  acc={accs[lab]:.3f}{flag}")
    print(f"  trusted set: {trusted}")
    print(f"  untrusted (dropped): {untrusted}")
    rec["info_gain"] = gains
    rec["trusted"] = trusted
    rec["untrusted"] = untrusted

    if not trusted:
        print("\nNO TRUSTED FALSIFIERS — router cannot route. v3 reduces to random.")
        rec["headline"] = {"verdict": "NO_ROUTING", "trusted_empty": True}
        with open(OUT, "w", encoding="utf-8") as f: json.dump(rec, f, indent=2)
        return

    # Phase 2 — 3-seed replication bake-off
    print(f"\n=== Phase 2: bake-off across {len(SEEDS)} seeds ===")
    AX = ("skew_defect", "run_entropy")
    common = dict(fitness=merit_factor, descriptor=labs_descriptor, axes=AX, init=random_seq)

    seed_results = []
    for seed_off in SEEDS:
        seed = SEED + seed_off
        print(f"\n  --- seed {seed} ---")
        # Random arm
        t0 = time.time()
        r_rand = map_elites(N, random_mutate, rng=np.random.default_rng(seed),
                            n_evals=N_EVALS_LOOP, **common)
        t_rand = time.time() - t0
        # Astraea arm (fresh telemetry per seed)
        telemetry = {"explore": 0, "low_conf_fallback": 0, "routed": 0,
                     "no_improvement_fallback": 0, "target_counts": {}}
        router = AstraeaV3Router(clfs, trusted)
        t0 = time.time()
        r_astr = map_elites(N, make_astraea_v3_mutate(router, telemetry),
                            rng=np.random.default_rng(seed),
                            n_evals=N_EVALS_LOOP, **common)
        t_astr = time.time() - t0
        lift_F = r_astr["best_merit_factor"] - r_rand["best_merit_factor"]
        lift_cov = r_astr["coverage"] - r_rand["coverage"]
        print(f"    random : best_F={r_rand['best_merit_factor']:.3f}  cov={r_rand['coverage']:.3f}  ({t_rand:.1f}s)")
        print(f"    astraea: best_F={r_astr['best_merit_factor']:.3f}  cov={r_astr['coverage']:.3f}  ({t_astr:.1f}s)")
        print(f"    LIFT   : best_F {lift_F:+.3f}  coverage {lift_cov:+.3f}")
        print(f"    telemetry: routed={telemetry['routed']}  explore={telemetry['explore']}  "
              f"low_conf_fb={telemetry['low_conf_fallback']}  no_improv_fb={telemetry['no_improvement_fallback']}")
        if telemetry["target_counts"]:
            print(f"    target distribution: {telemetry['target_counts']}")
        seed_results.append({
            "seed": seed, "lift_F": float(lift_F), "lift_cov": float(lift_cov),
            "random_best_F": float(r_rand["best_merit_factor"]),
            "astraea_best_F": float(r_astr["best_merit_factor"]),
            "random_cov": float(r_rand["coverage"]),
            "astraea_cov": float(r_astr["coverage"]),
            "telemetry": telemetry,
            "wall_random": t_rand, "wall_astraea": t_astr,
        })
    rec["seed_results"] = seed_results

    # Aggregate across seeds
    lifts_F = np.array([s["lift_F"] for s in seed_results])
    lifts_cov = np.array([s["lift_cov"] for s in seed_results])
    print(f"\n=== HEADLINE: replicated across {len(SEEDS)} seeds ===")
    print(f"  lift best_F : mean={lifts_F.mean():+.3f}  std={lifts_F.std():.3f}  "
          f"per-seed=[{', '.join(f'{l:+.3f}' for l in lifts_F)}]")
    print(f"  lift coverage: mean={lifts_cov.mean():+.3f}  std={lifts_cov.std():.3f}  "
          f"per-seed=[{', '.join(f'{l:+.3f}' for l in lifts_cov)}]")

    robust_lift = lifts_F.mean() - lifts_F.std()
    if robust_lift > 0:
        verdict = "ROBUST_LIFT"
        print(f"  VERDICT: mean - std = {robust_lift:+.3f} > 0  -> lift is robust to seed")
        print("           v3 has a replicated positive datapoint for the routing thesis.")
    elif lifts_F.mean() > 0:
        verdict = "FRAGILE_LIFT"
        print(f"  VERDICT: mean +{lifts_F.mean():.3f}, std {lifts_F.std():.3f}, "
              f"mean-std {robust_lift:+.3f}  -> lift exists but seed-fragile")
    else:
        verdict = "NO_LIFT"
        print(f"  VERDICT: mean {lifts_F.mean():+.3f} -> no positive lift even with v3 fixes")

    # Coverage diagnostic
    if lifts_cov.mean() > -0.02:
        print(f"  coverage: stochastic targeting recovered niche coverage "
              f"(mean Δcov = {lifts_cov.mean():+.3f})")
    else:
        print(f"  coverage: still regressing ({lifts_cov.mean():+.3f}) — R2 still partially binding")
    rec["headline"] = {"verdict": verdict,
                       "lift_F_mean": float(lifts_F.mean()), "lift_F_std": float(lifts_F.std()),
                       "lift_cov_mean": float(lifts_cov.mean()), "lift_cov_std": float(lifts_cov.std()),
                       "robust_lift": float(robust_lift)}

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)
    print(f"\nwrote {OUT}")

if __name__ == "__main__":
    main()
