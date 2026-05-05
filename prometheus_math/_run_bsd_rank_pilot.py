"""Pilot run: random vs REINFORCE on BSDRankEnv (1000 episodes x 3 seeds).

Captures mean reward per arm, lift, and a one-sided Welch t-test
p-value. Prints a JSON summary suitable for BSD_RANK_RESULTS.md.
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np


def _welch_one_sided(a: np.ndarray, b: np.ndarray) -> float:
    """One-sided Welch t-test p-value: H1 = mean(a) > mean(b).

    Uses scipy if available, normal-approx otherwise.
    """
    if a.size < 2 or b.size < 2:
        return float("nan")
    ma, mb = float(a.mean()), float(b.mean())
    va, vb = float(a.var(ddof=1)), float(b.var(ddof=1))
    se = math.sqrt(va / a.size + vb / b.size) if (va > 0 or vb > 0) else 1e-12
    t = (ma - mb) / max(se, 1e-12)
    df = (
        (va / a.size + vb / b.size) ** 2
        / max(
            (va / a.size) ** 2 / max(a.size - 1, 1)
            + (vb / b.size) ** 2 / max(b.size - 1, 1),
            1e-30,
        )
    )
    try:
        from scipy.stats import t as student_t
        return float(1.0 - student_t.cdf(t, df=df))
    except Exception:
        # Normal approximation
        return float(0.5 * (1.0 - math.erf(max(t, 0.0) / math.sqrt(2.0))))


def main() -> int:
    from prometheus_math import _bsd_corpus
    from prometheus_math.bsd_rank_env import (
        BSDRankEnv,
        train_random_bsd,
        train_majority_bsd,
        train_reinforce_bsd,
    )

    ok, reason = _bsd_corpus.is_available()
    if not ok:
        print(f"BSD corpus unavailable: {reason}", file=sys.stderr)
        return 2

    n_episodes = 1000
    n_seeds = 3
    n_total = 1000
    conductor_max = 20000

    print(f"Loading corpus (n_total={n_total}, conductor_max={conductor_max})...")
    corpus = _bsd_corpus.load_bsd_corpus(
        n_total=n_total, seed=42, conductor_max=conductor_max
    )
    summary = _bsd_corpus.corpus_summary(corpus)
    print(f"Corpus: {summary}")

    train, test = _bsd_corpus.split_train_test(corpus, train_frac=0.7, seed=42)
    print(f"Train/test split: {len(train)} / {len(test)}")

    results: Dict[str, Any] = {
        "corpus": summary,
        "train_size": len(train),
        "test_size": len(test),
        "n_episodes": n_episodes,
        "n_seeds": n_seeds,
    }

    random_means: List[float] = []
    majority_means: List[float] = []
    reinforce_means: List[float] = []
    train_eval_random: List[float] = []
    train_eval_reinforce: List[float] = []
    test_eval_random: List[float] = []
    test_eval_reinforce: List[float] = []
    pred_count_history: List[List[int]] = []

    for s in range(n_seeds):
        seed = 17 + s * 1009
        print(f"\n--- seed {s} (rng_seed={seed}) ---")
        # Random baseline on train split.
        e = BSDRankEnv(corpus=train, split="all", seed=seed)
        t0 = time.time()
        r = train_random_bsd(e, n_episodes=n_episodes, seed=seed)
        e.close()
        random_means.append(r["mean_reward"])
        train_eval_random.append(r["mean_reward"])
        print(f"  random : mean={r['mean_reward']:.2f}  acc={r['accuracy']:.3f}  "
              f"({time.time()-t0:.1f}s)")

        # Majority class baseline.
        e = BSDRankEnv(corpus=train, split="all", seed=seed)
        t0 = time.time()
        m = train_majority_bsd(e, n_episodes=n_episodes, seed=seed)
        e.close()
        majority_means.append(m["mean_reward"])
        print(f"  major0 : mean={m['mean_reward']:.2f}  acc={m['accuracy']:.3f}  "
              f"({time.time()-t0:.1f}s)")

        # REINFORCE on train split.
        e = BSDRankEnv(corpus=train, split="all", seed=seed)
        t0 = time.time()
        ln = train_reinforce_bsd(
            e, n_episodes=n_episodes, lr=0.05, seed=seed,
        )
        e.close()
        reinforce_means.append(ln["mean_reward"])
        train_eval_reinforce.append(ln["mean_reward"])
        pred_count_history.append(ln["pred_counts"])
        print(f"  REINFORCE: mean={ln['mean_reward']:.2f}  acc={ln['accuracy']:.3f}  "
              f"pred_counts={ln['pred_counts']}  ({time.time()-t0:.1f}s)")

        # Held-out test evaluation: re-use the trained policy by replaying
        # the policy on test split with a frozen W,b. The simplest way is
        # to wrap a deterministic eval by hand: argmax of W@obs+b.
        W = ln["policy_W_final"]
        b = ln["policy_b_final"]
        e = BSDRankEnv(corpus=test, split="all", seed=seed + 100000)
        rng = np.random.default_rng(seed + 100000)
        n_test_ep = min(n_episodes, len(test) * 4)  # multiple passes ok
        rs_test = []
        for _ in range(n_test_ep):
            obs, _info = e.reset(seed=int(rng.integers(0, 2**31 - 1)))
            logits = W @ obs + b
            a = int(np.argmax(logits))  # deterministic eval
            _, rr, _, _, _ = e.step(a)
            rs_test.append(rr)
        e.close()
        rs_test_arr = np.asarray(rs_test, dtype=np.float64)
        test_mean = float(rs_test_arr.mean()) if rs_test_arr.size else 0.0
        test_eval_reinforce.append(test_mean)

        # Also do a random-baseline eval on test for comparison.
        e = BSDRankEnv(corpus=test, split="all", seed=seed + 200000)
        rng = np.random.default_rng(seed + 200000)
        rs_test_r = []
        for _ in range(n_test_ep):
            obs, _info = e.reset(seed=int(rng.integers(0, 2**31 - 1)))
            a = int(rng.integers(0, 5))
            _, rr, _, _, _ = e.step(a)
            rs_test_r.append(rr)
        e.close()
        rs_test_r_arr = np.asarray(rs_test_r, dtype=np.float64)
        test_eval_random.append(float(rs_test_r_arr.mean()) if rs_test_r_arr.size else 0.0)
        print(f"  TEST eval: random={test_eval_random[-1]:.2f}, "
              f"reinforce(argmax)={test_mean:.2f}")

    rand_arr = np.asarray(random_means)
    maj_arr = np.asarray(majority_means)
    lrn_arr = np.asarray(reinforce_means)
    test_rand_arr = np.asarray(test_eval_random)
    test_lrn_arr = np.asarray(test_eval_reinforce)

    rand_mean = float(rand_arr.mean())
    maj_mean = float(maj_arr.mean())
    lrn_mean = float(lrn_arr.mean())

    lift_lrn_over_rand = (lrn_mean - rand_mean) / max(abs(rand_mean), 1e-9)
    lift_lrn_over_maj = (lrn_mean - maj_mean) / max(abs(maj_mean), 1e-9)
    p_rand = _welch_one_sided(lrn_arr, rand_arr)
    p_maj = _welch_one_sided(lrn_arr, maj_arr)

    test_lift = (float(test_lrn_arr.mean()) - float(test_rand_arr.mean())) / max(
        abs(float(test_rand_arr.mean())), 1e-9
    )
    p_test = _welch_one_sided(test_lrn_arr, test_rand_arr)

    print("\n========== SUMMARY ==========")
    print(f"Random   : mean={rand_mean:.2f}  per-seed={rand_arr.tolist()}")
    print(f"Majority0: mean={maj_mean:.2f}  per-seed={maj_arr.tolist()}")
    print(f"REINFORCE: mean={lrn_mean:.2f}  per-seed={lrn_arr.tolist()}")
    print(f"Lift learned vs random   = {lift_lrn_over_rand:+.3f}  (p={p_rand:.4g})")
    print(f"Lift learned vs majority = {lift_lrn_over_maj:+.3f}  (p={p_maj:.4g})")
    print(f"Test (held-out): random={float(test_rand_arr.mean()):.2f}  "
          f"reinforce(argmax)={float(test_lrn_arr.mean()):.2f}  "
          f"lift={test_lift:+.3f}  p={p_test:.4g}")

    results.update({
        "random_means": rand_arr.tolist(),
        "majority_means": maj_arr.tolist(),
        "reinforce_means": lrn_arr.tolist(),
        "random_mean": rand_mean,
        "majority_mean": maj_mean,
        "reinforce_mean": lrn_mean,
        "lift_learned_over_random": float(lift_lrn_over_rand),
        "lift_learned_over_majority": float(lift_lrn_over_maj),
        "p_value_learned_vs_random": float(p_rand),
        "p_value_learned_vs_majority": float(p_maj),
        "pred_count_history": pred_count_history,
        "test_eval_random_means": test_rand_arr.tolist(),
        "test_eval_reinforce_means": test_lrn_arr.tolist(),
        "test_lift": float(test_lift),
        "p_value_test_learned_vs_random": float(p_test),
    })
    out_path = Path("prometheus_math") / "_bsd_rank_pilot_run.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nWrote pilot summary to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
