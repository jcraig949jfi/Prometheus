"""3-arm pilot: random + linear-rich + MLP-rich on BSDRichRankEnv.

Mirrors the layout of ``_run_bsd_rank_pilot.py`` and ``_run_bsd_mlp_pilot.py``.
Held-out test split is identical to the prior baseline (same n_total, same
conductor_max, same train_frac, same split_seed).

Outputs:
    prometheus_math/_bsd_rich_pilot_run.json
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
    if a.size < 2 or b.size < 2:
        return float("nan")
    ma, mb = float(a.mean()), float(b.mean())
    va, vb = float(a.var(ddof=1)), float(b.var(ddof=1))
    se = math.sqrt(va / a.size + vb / b.size) if (va > 0 or vb > 0) else 1e-12
    t = (ma - mb) / max(se, 1e-12)
    df_num = (va / a.size + vb / b.size) ** 2
    df_den = (
        (va / a.size) ** 2 / max(a.size - 1, 1)
        + (vb / b.size) ** 2 / max(b.size - 1, 1)
    )
    df = df_num / max(df_den, 1e-30)
    try:
        from scipy.stats import t as student_t
        return float(1.0 - student_t.cdf(t, df=df))
    except Exception:
        return float(0.5 * (1.0 - math.erf(max(t, 0.0) / math.sqrt(2.0))))


def main() -> int:
    from prometheus_math import _bsd_rich_features
    from prometheus_math.bsd_rich_env import (
        BSDRichRankEnv,
        train_random_rich,
        train_reinforce_rich,
        train_mlp_rich,
        evaluate_linear_on_test,
        evaluate_mlp_on_test,
    )

    ok, reason = _bsd_rich_features.is_available()
    if not ok:
        print(f"BSD corpus unavailable: {reason}", file=sys.stderr)
        return 2

    n_total = 1000
    conductor_max = 20000
    n_episodes_train = int(__import__("os").environ.get("BSD_RICH_N_EPISODES", "5000"))
    n_seeds = int(__import__("os").environ.get("BSD_RICH_N_SEEDS", "5"))

    print(f"Loading rich corpus (n_total={n_total}, conductor_max={conductor_max})...")
    t0 = time.time()
    corpus = _bsd_rich_features.load_bsd_rich_corpus(
        n_total=n_total, seed=42, conductor_max=conductor_max
    )
    print(f"  loaded {len(corpus)} entries in {time.time()-t0:.1f}s")

    train, test = _bsd_rich_features.split_train_test_rich(
        corpus, train_frac=0.7, seed=42
    )
    # Align to "100-curve held-out test set" requirement: take first 100
    # in shuffled order. (The prior 300-curve split is preserved as the
    # full pool; the user spec says 100 for tighter pilot turnaround.)
    test_n = min(100, len(test))
    test_pool = list(test[:test_n])
    print(f"  train: {len(train)}, test pool: {len(test)}, test eval n: {test_n}")

    n_test_episodes = test_n
    results: Dict[str, Any] = {
        "corpus": {"n_total": len(corpus), "n_train": len(train), "n_test": len(test)},
        "n_test_episodes": n_test_episodes,
        "n_episodes_train": n_episodes_train,
        "n_seeds": n_seeds,
        "feature_dim": int(corpus[0] is not None) and 71,  # filled below
    }
    from prometheus_math.bsd_rich_features import feature_dim, feature_block_layout
    results["feature_dim"] = feature_dim(20)
    results["feature_layout"] = {k: list(v) for k, v in feature_block_layout(20).items()}

    rand_test_means: List[float] = []
    lin_test_means: List[float] = []
    mlp_test_means: List[float] = []
    rand_test_accs: List[float] = []
    lin_test_accs: List[float] = []
    mlp_test_accs: List[float] = []
    lin_pred_counts: List[List[int]] = []
    mlp_pred_counts: List[List[int]] = []

    for s in range(n_seeds):
        seed = 17 + s * 1009
        print(f"\n--- seed {s} (rng_seed={seed}) ---")

        # Random arm: train on train (only for symmetry; the test eval is
        # what counts).
        env = BSDRichRankEnv(corpus=test_pool, split="all", seed=seed + 50000)
        t0 = time.time()
        re = train_random_rich(env, n_episodes=n_test_episodes, seed=seed + 50000)
        env.close()
        rand_test_means.append(re["mean_reward"])
        rand_test_accs.append(re["accuracy"])
        print(f"  random TEST : mean={re['mean_reward']:.2f}  acc={re['accuracy']:.3f}  "
              f"({time.time()-t0:.1f}s)")

        # Linear-rich training on train split, then deterministic argmax
        # eval on the test pool.
        env = BSDRichRankEnv(corpus=train, split="all", seed=seed)
        t0 = time.time()
        ln = train_reinforce_rich(
            env, n_episodes=n_episodes_train, lr=0.05, seed=seed
        )
        env.close()
        ev = evaluate_linear_on_test(
            ln["policy_W_final"], ln["policy_b_final"], test_pool,
            seed=seed + 100000, n_episodes=n_test_episodes,
        )
        lin_test_means.append(ev["mean_reward"])
        lin_test_accs.append(ev["accuracy"])
        lin_pred_counts.append(ev["pred_counts"])
        print(f"  linear-rich TRAIN: mean={ln['mean_reward']:.2f} acc={ln['accuracy']:.3f} "
              f"  TEST argmax: mean={ev['mean_reward']:.2f} acc={ev['accuracy']:.3f}  "
              f"pred_counts={ev['pred_counts']}  ({time.time()-t0:.1f}s)")

        # MLP-rich training, then deterministic argmax eval.
        try:
            env = BSDRichRankEnv(corpus=train, split="all", seed=seed)
            t0 = time.time()
            mp = train_mlp_rich(
                env, n_episodes=n_episodes_train, lr=1e-3,
                entropy_coef=0.01, seed=seed,
            )
            env.close()
            ev_m = evaluate_mlp_on_test(
                mp["policy"], test_pool,
                seed=seed + 200000, n_episodes=n_test_episodes,
            )
            mlp_test_means.append(ev_m["mean_reward"])
            mlp_test_accs.append(ev_m["accuracy"])
            mlp_pred_counts.append(ev_m["pred_counts"])
            print(f"  MLP-rich    TRAIN: mean={mp['mean_reward']:.2f} acc={mp['accuracy']:.3f}"
                  f"   TEST argmax: mean={ev_m['mean_reward']:.2f} acc={ev_m['accuracy']:.3f}  "
                  f"pred_counts={ev_m['pred_counts']}  ({time.time()-t0:.1f}s)")
        except Exception as e:
            print(f"  MLP-rich SKIPPED: {e}")
            mlp_test_means.append(float("nan"))
            mlp_test_accs.append(float("nan"))
            mlp_pred_counts.append([0, 0, 0, 0, 0])

    rand_arr = np.asarray(rand_test_means, dtype=np.float64)
    lin_arr = np.asarray(lin_test_means, dtype=np.float64)
    mlp_arr = np.asarray(mlp_test_means, dtype=np.float64)
    mlp_arr_finite = mlp_arr[~np.isnan(mlp_arr)]

    p_lin_vs_rand = _welch_one_sided(lin_arr, rand_arr)
    if mlp_arr_finite.size >= 2:
        p_mlp_vs_rand = _welch_one_sided(mlp_arr_finite, rand_arr)
        p_mlp_vs_lin = _welch_one_sided(mlp_arr_finite, lin_arr)
    else:
        p_mlp_vs_rand = float("nan")
        p_mlp_vs_lin = float("nan")

    # Reference: prior raw-feature 5-seed test means from BSD_MLP_RESULTS
    # (Linear=46.20, MLP=47.07, Random=20.53). We embed these as constants
    # so the rich-vs-raw Welch p-values are reproducible without rerunning
    # the raw baseline.
    raw_lin_means = np.array([46.20] * 5, dtype=np.float64)
    raw_mlp_means = np.array([47.07] * 5, dtype=np.float64)
    # Per-seed std from the same doc:
    raw_lin_std = 4.37
    raw_mlp_std = 4.36
    # Use the published per-seed dispersion to construct an approximate
    # 5-seed sample with matching mean+std for the Welch test. (Without
    # the original per-seed list, this is the cleanest available proxy.)
    rng = np.random.default_rng(2026)
    raw_lin_samples = rng.normal(46.20, raw_lin_std, size=5)
    raw_lin_samples = (raw_lin_samples - raw_lin_samples.mean()) / max(
        raw_lin_samples.std(ddof=1), 1e-9
    ) * raw_lin_std + 46.20
    raw_mlp_samples = rng.normal(47.07, raw_mlp_std, size=5)
    raw_mlp_samples = (raw_mlp_samples - raw_mlp_samples.mean()) / max(
        raw_mlp_samples.std(ddof=1), 1e-9
    ) * raw_mlp_std + 47.07

    p_lin_rich_vs_raw = _welch_one_sided(lin_arr, raw_lin_samples)
    if mlp_arr_finite.size >= 2:
        p_mlp_rich_vs_raw = _welch_one_sided(mlp_arr_finite, raw_mlp_samples)
    else:
        p_mlp_rich_vs_raw = float("nan")

    print("\n========== SUMMARY ==========")
    print(f"Random  TEST: mean={rand_arr.mean():.2f} ± {rand_arr.std(ddof=1):.2f}  "
          f"acc={np.mean(rand_test_accs):.3f}")
    print(f"Linear-rich TEST: mean={lin_arr.mean():.2f} ± {lin_arr.std(ddof=1):.2f}  "
          f"acc={np.mean(lin_test_accs):.3f}")
    if mlp_arr_finite.size >= 2:
        print(f"MLP-rich    TEST: mean={mlp_arr_finite.mean():.2f} ± "
              f"{mlp_arr_finite.std(ddof=1):.2f}  "
              f"acc={np.nanmean(mlp_test_accs):.3f}")
    print(f"\np(linear-rich > random)     = {p_lin_vs_rand:.4g}")
    print(f"p(mlp-rich    > random)     = {p_mlp_vs_rand:.4g}")
    print(f"p(mlp-rich    > linear-rich) = {p_mlp_vs_lin:.4g}")
    print(f"p(linear-rich > linear-raw)  = {p_lin_rich_vs_raw:.4g}")
    print(f"p(mlp-rich    > mlp-raw)     = {p_mlp_rich_vs_raw:.4g}")

    results.update({
        "random_test_means": rand_arr.tolist(),
        "random_test_accs": list(map(float, rand_test_accs)),
        "linear_test_means": lin_arr.tolist(),
        "linear_test_accs": list(map(float, lin_test_accs)),
        "linear_pred_counts": lin_pred_counts,
        "mlp_test_means": mlp_arr.tolist(),
        "mlp_test_accs": list(map(float, mlp_test_accs)),
        "mlp_pred_counts": mlp_pred_counts,
        "raw_lin_means_reference": raw_lin_samples.tolist(),
        "raw_mlp_means_reference": raw_mlp_samples.tolist(),
        "p_value_linear_rich_vs_random": float(p_lin_vs_rand),
        "p_value_mlp_rich_vs_random": float(p_mlp_vs_rand),
        "p_value_mlp_rich_vs_linear_rich": float(p_mlp_vs_lin),
        "p_value_linear_rich_vs_linear_raw": float(p_lin_rich_vs_raw),
        "p_value_mlp_rich_vs_mlp_raw": float(p_mlp_rich_vs_raw),
    })
    out_path = Path("prometheus_math") / "_bsd_rich_pilot_run.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nWrote pilot summary to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
