"""prometheus_math.mock_theta_pilot -- 3-algorithm pilot for MockThetaEnv.

Mirrors ``modular_form_pilot`` but on the mock-theta corpus. Total
budget per the task spec: 5K episodes x 3 seeds x 3 algorithms =
45K episodes. Plus a held-out test eval per seed per trained agent.

Outputs:
    prometheus_math/_mock_theta_pilot.json   (full numerics)
    stdout summary suitable for MOCK_THETA_RESULTS.md.
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
    """One-sided Welch t-test p-value: H1 = mean(a) > mean(b)."""
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
        return float(0.5 * (1.0 - math.erf(max(t, 0.0) / math.sqrt(2.0))))


def _eval_test_split_random(test_corpus, n_episodes: int, seed: int) -> float:
    from prometheus_math.mock_theta_env import MockThetaEnv
    env = MockThetaEnv(corpus=test_corpus, split="all", seed=seed)
    rng = np.random.default_rng(seed)
    rs = []
    for _ in range(n_episodes):
        env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        a = int(rng.integers(0, env.n_bins()))
        _, r, _, _, _ = env.step(a)
        rs.append(r)
    env.close()
    return float(np.asarray(rs).mean()) if rs else 0.0


def _eval_test_split_reinforce(test_corpus, W, b, n_episodes: int, seed: int) -> float:
    from prometheus_math.mock_theta_env import MockThetaEnv
    env = MockThetaEnv(corpus=test_corpus, split="all", seed=seed)
    rng = np.random.default_rng(seed)
    rs = []
    for _ in range(n_episodes):
        obs, _info = env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        logits = W @ obs + b
        a = int(np.argmax(logits))
        _, r, _, _, _ = env.step(a)
        rs.append(r)
    env.close()
    return float(np.asarray(rs).mean()) if rs else 0.0


def _eval_test_split_ppo(
    test_corpus, W1, b1, Wp, bp, n_episodes: int, seed: int
) -> float:
    from prometheus_math.mock_theta_env import MockThetaEnv
    env = MockThetaEnv(corpus=test_corpus, split="all", seed=seed)
    rng = np.random.default_rng(seed)
    rs = []
    for _ in range(n_episodes):
        obs, _info = env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        h_pre = obs @ W1.T + b1
        h_act = np.maximum(h_pre, 0.0)
        logits = h_act @ Wp.T + bp
        a = int(np.argmax(logits))
        _, r, _, _, _ = env.step(a)
        rs.append(r)
    env.close()
    return float(np.asarray(rs).mean()) if rs else 0.0


def run_pilot(
    *,
    n_episodes: int = 5000,
    n_seeds: int = 3,
    test_n_episodes: int = 1000,
    out_path: Path = Path("prometheus_math") / "_mock_theta_pilot.json",
) -> Dict[str, Any]:
    from prometheus_math import _mock_theta_corpus
    from prometheus_math.mock_theta_env import (
        MockThetaEnv,
        train_random,
        train_reinforce,
        train_ppo,
    )

    ok, reason = _mock_theta_corpus.is_available()
    if not ok:
        print(f"mock-theta corpus unavailable: {reason}", file=sys.stderr)
        return {"error": reason}

    print("Loading corpus...")
    corpus = _mock_theta_corpus.load_mock_theta_corpus()
    summary = _mock_theta_corpus.corpus_summary(corpus)
    source = _mock_theta_corpus.last_load_source()
    print(f"Corpus source: {source}")
    print(f"Corpus summary: {summary}")

    train, test = _mock_theta_corpus.split_train_test(
        corpus, train_frac=0.7, seed=42
    )
    print(f"Train/test split: {len(train)} / {len(test)}")

    results: Dict[str, Any] = {
        "corpus": summary,
        "corpus_source": source,
        "train_size": len(train),
        "test_size": len(test),
        "n_episodes": n_episodes,
        "n_seeds": n_seeds,
    }

    random_means: List[float] = []
    reinforce_means: List[float] = []
    ppo_means: List[float] = []
    test_random: List[float] = []
    test_reinforce: List[float] = []
    test_ppo: List[float] = []
    pred_count_history: Dict[str, List[List[int]]] = {
        "random": [], "reinforce": [], "ppo": [],
    }

    for s in range(n_seeds):
        seed = 17 + s * 1009
        print(f"\n--- seed {s} (rng_seed={seed}) ---")

        env = MockThetaEnv(corpus=train, split="all", seed=seed)
        t0 = time.time()
        r_out = train_random(env, n_episodes=n_episodes, seed=seed)
        env.close()
        random_means.append(r_out["mean_reward"])
        pred_count_history["random"].append(r_out["pred_counts"])
        print(f"  random   : mean={r_out['mean_reward']:.2f}  "
              f"acc={r_out['accuracy']:.3f}  ({time.time()-t0:.1f}s)")

        env = MockThetaEnv(corpus=train, split="all", seed=seed)
        t0 = time.time()
        l_out = train_reinforce(
            env, n_episodes=n_episodes, lr=0.02, seed=seed,
        )
        env.close()
        reinforce_means.append(l_out["mean_reward"])
        pred_count_history["reinforce"].append(l_out["pred_counts"])
        print(f"  REINFORCE: mean={l_out['mean_reward']:.2f}  "
              f"acc={l_out['accuracy']:.3f}  ({time.time()-t0:.1f}s)")

        env = MockThetaEnv(corpus=train, split="all", seed=seed)
        t0 = time.time()
        p_out = train_ppo(
            env, n_episodes=n_episodes, lr=0.005, hidden=32, seed=seed,
        )
        env.close()
        ppo_means.append(p_out["mean_reward"])
        pred_count_history["ppo"].append(p_out["pred_counts"])
        print(f"  PPO       : mean={p_out['mean_reward']:.2f}  "
              f"acc={p_out['accuracy']:.3f}  ({time.time()-t0:.1f}s)")

        t_n = min(test_n_episodes, max(200, len(test) * 4))
        rand_t = _eval_test_split_random(
            test, n_episodes=t_n, seed=seed + 100000
        )
        lrn_t = _eval_test_split_reinforce(
            test, W=l_out["policy_W_final"], b=l_out["policy_b_final"],
            n_episodes=t_n, seed=seed + 200000,
        )
        ppo_t = _eval_test_split_ppo(
            test, W1=p_out["policy_W1_final"], b1=p_out["policy_b1_final"],
            Wp=p_out["policy_Wp_final"], bp=p_out["policy_bp_final"],
            n_episodes=t_n, seed=seed + 300000,
        )
        test_random.append(rand_t)
        test_reinforce.append(lrn_t)
        test_ppo.append(ppo_t)
        print(f"  TEST eval: random={rand_t:.2f}  "
              f"REINFORCE(argmax)={lrn_t:.2f}  PPO(argmax)={ppo_t:.2f}")

    rand_arr = np.asarray(random_means)
    lrn_arr = np.asarray(reinforce_means)
    ppo_arr = np.asarray(ppo_means)
    t_rand_arr = np.asarray(test_random)
    t_lrn_arr = np.asarray(test_reinforce)
    t_ppo_arr = np.asarray(test_ppo)

    rand_mean = float(rand_arr.mean())
    lrn_mean = float(lrn_arr.mean())
    ppo_mean = float(ppo_arr.mean())

    p_lrn_vs_rand = _welch_one_sided(lrn_arr, rand_arr)
    p_ppo_vs_rand = _welch_one_sided(ppo_arr, rand_arr)
    p_test_lrn_vs_rand = _welch_one_sided(t_lrn_arr, t_rand_arr)
    p_test_ppo_vs_rand = _welch_one_sided(t_ppo_arr, t_rand_arr)

    print("\n========== SUMMARY ==========")
    print(f"TRAIN: random   mean={rand_mean:.2f}  per-seed={rand_arr.tolist()}")
    print(f"TRAIN: REINFORCE mean={lrn_mean:.2f}  per-seed={lrn_arr.tolist()}")
    print(f"TRAIN: PPO       mean={ppo_mean:.2f}  per-seed={ppo_arr.tolist()}")
    print(f"  REINFORCE vs random: lift "
          f"{(lrn_mean - rand_mean) / max(abs(rand_mean), 1e-9):+.3f}x  "
          f"p={p_lrn_vs_rand:.4g}")
    print(f"  PPO vs random      : lift "
          f"{(ppo_mean - rand_mean) / max(abs(rand_mean), 1e-9):+.3f}x  "
          f"p={p_ppo_vs_rand:.4g}")
    print(f"TEST : random       mean={float(t_rand_arr.mean()):.2f}")
    print(f"TEST : REINFORCE    mean={float(t_lrn_arr.mean()):.2f}  "
          f"p_vs_random={p_test_lrn_vs_rand:.4g}")
    print(f"TEST : PPO          mean={float(t_ppo_arr.mean()):.2f}  "
          f"p_vs_random={p_test_ppo_vs_rand:.4g}")

    results.update({
        "random_means": rand_arr.tolist(),
        "reinforce_means": lrn_arr.tolist(),
        "ppo_means": ppo_arr.tolist(),
        "random_mean": rand_mean,
        "reinforce_mean": lrn_mean,
        "ppo_mean": ppo_mean,
        "p_value_reinforce_vs_random": float(p_lrn_vs_rand),
        "p_value_ppo_vs_random": float(p_ppo_vs_rand),
        "test_random_means": t_rand_arr.tolist(),
        "test_reinforce_means": t_lrn_arr.tolist(),
        "test_ppo_means": t_ppo_arr.tolist(),
        "test_random_mean": float(t_rand_arr.mean()),
        "test_reinforce_mean": float(t_lrn_arr.mean()),
        "test_ppo_mean": float(t_ppo_arr.mean()),
        "p_value_test_reinforce_vs_random": float(p_test_lrn_vs_rand),
        "p_value_test_ppo_vs_random": float(p_test_ppo_vs_rand),
        "pred_count_history": pred_count_history,
    })
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nWrote pilot summary to {out_path}")
    return results


def main() -> int:
    out = run_pilot()
    return 0 if "error" not in out else 2


if __name__ == "__main__":
    raise SystemExit(main())
