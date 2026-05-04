"""Pilot run: MLP REINFORCE vs linear REINFORCE vs random on BSDRankEnv.

Mirrors ``_run_bsd_rank_pilot.py`` but adds an MLP backend and a 6-cell
hyperparameter sweep (LR x entropy_coef = 3 x 2). Captures everything
the team review's #6 refinement asked for:

    - per-cell test mean accuracy + std across 5 seeds
    - Welch one-sided p-value vs random
    - Welch one-sided p-value vs linear-REINFORCE
    - relative lift vs each baseline

Re-runs the linear REINFORCE arm too (same seeds) so the regression
check stays sharp. Writes JSON + prints a table.
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np


def main() -> int:
    from prometheus_math import _bsd_corpus
    from prometheus_math.bsd_rank_env import (
        BSDRankEnv,
        train_random_bsd,
        train_reinforce_bsd,
    )
    from prometheus_math.bsd_rank_mlp import (
        DEFAULT_HIDDEN,
        evaluate_mlp_on_corpus,
        hyperparameter_sweep,
        welch_one_sided,
    )

    ok, reason = _bsd_corpus.is_available()
    if not ok:
        print(f"BSD corpus unavailable: {reason}", file=sys.stderr)
        return 2

    n_total = 1000
    conductor_max = 20000
    n_episodes = 5000        # MLP training budget
    n_seeds = 5              # 5 seeds per cell
    n_seeds_linear = 5       # also re-run linear with 5 seeds for parity

    print(f"Loading corpus (n_total={n_total}, conductor_max={conductor_max})...")
    corpus = _bsd_corpus.load_bsd_corpus(
        n_total=n_total, seed=42, conductor_max=conductor_max
    )
    summary = _bsd_corpus.corpus_summary(corpus)
    print(f"Corpus: {summary}")

    train, test = _bsd_corpus.split_train_test(corpus, train_frac=0.7, seed=42)
    print(f"Train/test split: {len(train)} / {len(test)}")

    n_test = len(test)
    n_test_eval = n_test  # 1 pass through test set per evaluation

    # ----------------------------------------------------------------
    # 1) Linear REINFORCE regression check (5 seeds, same setup)
    # ----------------------------------------------------------------
    print("\n=== Linear REINFORCE (regression check, 5 seeds) ===")
    linear_test_means: List[float] = []
    linear_test_accs: List[float] = []
    linear_test_rewards_per_seed: List[np.ndarray] = []
    for s in range(n_seeds_linear):
        seed = int(17 + s * 1009)
        t0 = time.time()
        env = BSDRankEnv(corpus=train, split="all", seed=seed)
        ln = train_reinforce_bsd(
            env, n_episodes=n_episodes, lr=0.05, seed=seed,
        )
        env.close()
        # Eval argmax on test split (one pass through test).
        W = ln["policy_W_final"]
        b = ln["policy_b_final"]
        e_test = BSDRankEnv(corpus=test, split="all", seed=seed + 100000)
        rng = np.random.default_rng(seed + 100000)
        rs_test = np.zeros(n_test_eval, dtype=np.float64)
        n_correct_test = 0
        for t in range(n_test_eval):
            obs, _info = e_test.reset(seed=int(rng.integers(0, 2**31 - 1)))
            logits = W @ obs + b
            a = int(np.argmax(logits))
            _, rr, _, _, info = e_test.step(a)
            rs_test[t] = rr
            if info.get("hit"):
                n_correct_test += 1
        e_test.close()
        linear_test_means.append(float(rs_test.mean()))
        linear_test_accs.append(float(n_correct_test / n_test_eval))
        linear_test_rewards_per_seed.append(rs_test)
        print(f"  seed {seed}: test_mean={linear_test_means[-1]:.2f} "
              f"acc={linear_test_accs[-1]:.3f} ({time.time()-t0:.1f}s)")

    linear_summary = {
        "test_means": linear_test_means,
        "test_accs": linear_test_accs,
        "mean_grand": float(np.mean(linear_test_means)),
        "std_grand": float(np.std(linear_test_means, ddof=1))
        if len(linear_test_means) > 1 else 0.0,
        "acc_mean": float(np.mean(linear_test_accs)),
        "acc_std": float(np.std(linear_test_accs, ddof=1))
        if len(linear_test_accs) > 1 else 0.0,
    }
    print(
        f"  LINEAR test mean reward: {linear_summary['mean_grand']:.2f} "
        f"+/- {linear_summary['std_grand']:.2f}, acc {linear_summary['acc_mean']:.3f}"
    )

    # ----------------------------------------------------------------
    # 2) Random baseline on test (5 seeds, single pass through test)
    # ----------------------------------------------------------------
    print("\n=== Random baseline on test (5 seeds) ===")
    random_test_means: List[float] = []
    random_test_accs: List[float] = []
    random_test_rewards_per_seed: List[np.ndarray] = []
    for s in range(n_seeds):
        seed = int(17 + s * 1009 + 200000)
        e = BSDRankEnv(corpus=test, split="all", seed=seed)
        out = train_random_bsd(e, n_episodes=n_test_eval, seed=seed)
        e.close()
        random_test_means.append(out["mean_reward"])
        random_test_accs.append(out["accuracy"])
        random_test_rewards_per_seed.append(out["rewards"])
        print(f"  seed {seed}: test_mean={out['mean_reward']:.2f} "
              f"acc={out['accuracy']:.3f}")
    random_summary = {
        "test_means": random_test_means,
        "test_accs": random_test_accs,
        "mean_grand": float(np.mean(random_test_means)),
        "std_grand": float(np.std(random_test_means, ddof=1))
        if len(random_test_means) > 1 else 0.0,
        "acc_mean": float(np.mean(random_test_accs)),
        "acc_std": float(np.std(random_test_accs, ddof=1))
        if len(random_test_accs) > 1 else 0.0,
    }
    print(
        f"  RANDOM test mean reward: {random_summary['mean_grand']:.2f} "
        f"+/- {random_summary['std_grand']:.2f}, acc {random_summary['acc_mean']:.3f}"
    )

    # ----------------------------------------------------------------
    # 3) MLP 6-cell hyperparameter sweep (5 seeds per cell)
    # ----------------------------------------------------------------
    print("\n=== MLP REINFORCE 6-cell sweep (5 seeds per cell) ===")
    print(f"  Hidden: {DEFAULT_HIDDEN}, n_episodes/cell={n_episodes}")
    t0_sweep = time.time()
    progress: List[Dict[str, Any]] = []

    def _on_progress(info):
        progress.append(info)
        print(f"  cell lr={info['lr']:g} ec={info['entropy_coef']:g} "
              f"seed={info['seed']}: train={info['train_mean']:.2f} "
              f"test={info['test_mean']:.2f}")

    sweep = hyperparameter_sweep(
        train_corpus=train,
        test_corpus=test,
        env_cls=BSDRankEnv,
        n_episodes=n_episodes,
        n_seeds=n_seeds,
        learning_rates=(1e-3, 5e-4, 1e-4),
        entropy_coefs=(0.01, 0.001),
        hidden=DEFAULT_HIDDEN,
        base_seed=17,
        n_test_episodes=n_test_eval,
        progress_callback=_on_progress,
    )
    print(f"\n  Sweep time: {time.time()-t0_sweep:.1f}s")

    print("\n  Per-cell summary (test mean reward +/- std):")
    print("    {:>8}  {:>10}  {:>14}  {:>14}".format(
        "lr", "ent_coef", "test_mean", "test_acc"))
    for cell in sweep["cells"]:
        print(
            "    {:>8g}  {:>10g}  {:>6.2f} +/- {:>4.2f}  {:>5.3f} +/- {:>5.3f}".format(
                cell["lr"], cell["entropy_coef"],
                cell["test_mean_grand"], cell["test_std_grand"],
                cell["test_acc_mean"], cell["test_acc_std"],
            )
        )

    best = sweep["best_cell"]
    print(
        f"\n  BEST cell: lr={best['lr']} ec={best['entropy_coef']}: "
        f"test_mean={best['test_mean_grand']:.2f} +/- {best['test_std_grand']:.2f}, "
        f"acc {best['test_acc_mean']:.3f} +/- {best['test_acc_std']:.3f}"
    )

    # ----------------------------------------------------------------
    # 4) Statistical comparison: best MLP vs random, vs linear
    # ----------------------------------------------------------------
    best_cell_full = max(
        sweep["cells"], key=lambda c: c["test_mean_grand"]
    )
    mlp_test_means_arr = np.asarray(best_cell_full["test_means"])
    rand_arr = np.asarray(random_test_means)
    lin_arr = np.asarray(linear_test_means)

    p_mlp_vs_random = welch_one_sided(mlp_test_means_arr, rand_arr)
    p_mlp_vs_linear = welch_one_sided(mlp_test_means_arr, lin_arr)

    rand_mean = float(rand_arr.mean()) if rand_arr.size else 0.0
    lin_mean = float(lin_arr.mean()) if lin_arr.size else 0.0
    mlp_mean = float(mlp_test_means_arr.mean()) if mlp_test_means_arr.size else 0.0
    lift_vs_random = (mlp_mean - rand_mean) / max(abs(rand_mean), 1e-9)
    lift_vs_linear = (mlp_mean - lin_mean) / max(abs(lin_mean), 1e-9)

    print("\n========== COMPARISON SUMMARY ==========")
    print(f"Random  test mean: {rand_mean:.2f} +/- {random_summary['std_grand']:.2f} "
          f"(acc {random_summary['acc_mean']:.3f})")
    print(f"Linear  test mean: {lin_mean:.2f} +/- {linear_summary['std_grand']:.2f} "
          f"(acc {linear_summary['acc_mean']:.3f})")
    print(f"MLP     test mean: {mlp_mean:.2f} +/- {best['test_std_grand']:.2f} "
          f"(acc {best['test_acc_mean']:.3f})")
    print(f"Lift MLP vs random : {lift_vs_random:+.4f}  p={p_mlp_vs_random:.4g}")
    print(f"Lift MLP vs linear : {lift_vs_linear:+.4f}  p={p_mlp_vs_linear:.4g}")

    # ----------------------------------------------------------------
    # 5) Persist results
    # ----------------------------------------------------------------
    results: Dict[str, Any] = {
        "corpus": summary,
        "train_size": len(train),
        "test_size": len(test),
        "n_episodes": n_episodes,
        "n_seeds": n_seeds,
        "n_test_episodes": n_test_eval,
        "linear_summary": linear_summary,
        "linear_test_means": linear_test_means,
        "random_summary": random_summary,
        "random_test_means": random_test_means,
        "sweep": sweep,
        "best_cell_full": {
            "lr": best_cell_full["lr"],
            "entropy_coef": best_cell_full["entropy_coef"],
            "test_means": best_cell_full["test_means"],
            "test_accs": best_cell_full["test_accs"],
            "test_mean_grand": best_cell_full["test_mean_grand"],
            "test_std_grand": best_cell_full["test_std_grand"],
            "test_acc_mean": best_cell_full["test_acc_mean"],
            "test_acc_std": best_cell_full["test_acc_std"],
        },
        "comparison": {
            "rand_mean": rand_mean,
            "linear_mean": lin_mean,
            "mlp_mean": mlp_mean,
            "lift_mlp_vs_random": float(lift_vs_random),
            "lift_mlp_vs_linear": float(lift_vs_linear),
            "p_mlp_vs_random": float(p_mlp_vs_random),
            "p_mlp_vs_linear": float(p_mlp_vs_linear),
        },
    }
    out_path = Path("prometheus_math") / "_bsd_rank_mlp_pilot.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nWrote pilot summary to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
