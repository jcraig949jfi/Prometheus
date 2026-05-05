"""prometheus_math.demo_sigma_env_learn — learned-vs-random demo CLI.

Runs ``compare_random_vs_learned`` on the default Lehmer / Mahler-measure
env and prints a results table. Optionally saves a learning-curve plot.

Run::

    python -m prometheus_math.demo_sigma_env_learn --steps 10000 --seeds 3

This is the acceptance test for §4.4 of pivot/techne.md: prove the
reward signal is *learnable*, not merely well-formed. A positive lift
with low p-value means a contextual-bandit-class agent can pick out
the high-reward actions from random baseline; a flat or negative lift
means the env is too easy or the reward too noisy and the framework
needs work.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from .sigma_env import SigmaMathEnv
from .sigma_env_ppo import (
    compare_random_vs_learned,
    learning_curve_plot,
    train_ppo,
)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=10000)
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument(
        "--objective",
        type=str,
        default="minimize_mahler_measure",
        choices=["minimize_mahler_measure", "riemann_zeros"],
    )
    parser.add_argument(
        "--learner",
        type=str,
        default="reinforce",
        choices=["reinforce", "ppo"],
    )
    parser.add_argument("--lr", type=float, default=0.05,
                        help="REINFORCE learning rate (ignored for ppo)")
    parser.add_argument("--max-steps", type=int, default=200,
                        help="env max_steps per episode (auto-resets are common)")
    parser.add_argument("--plot", type=str, default=None,
                        help="optional path to save learning-curve PNG")
    parser.add_argument("--json", type=str, default=None,
                        help="optional path to save JSON of summary")
    args = parser.parse_args(argv)

    objective = args.objective
    max_steps = args.max_steps

    def env_factory() -> SigmaMathEnv:
        return SigmaMathEnv(objective=objective, max_steps=max_steps)

    learner_kwargs = {}
    if args.learner == "reinforce":
        learner_kwargs["lr"] = args.lr

    print(f"=== SigmaMathEnv learning baseline ===")
    print(f"  objective:  {objective}")
    print(f"  learner:    {args.learner}")
    print(f"  steps:      {args.steps}")
    print(f"  seeds:      {args.seeds}")
    print(f"  max_steps:  {max_steps}")
    if args.learner == "reinforce":
        print(f"  lr:         {args.lr}")
    print()

    result = compare_random_vs_learned(
        env_factory,
        n_steps=args.steps,
        n_seeds=args.seeds,
        learner=args.learner,
        learner_kwargs=learner_kwargs,
    )

    if result.get("skipped"):
        print(f"[SKIPPED] {result.get('reason')}")
        if args.learner == "ppo":
            print()
            print("Falling back to REINFORCE (numpy-only, no SB3 dependency)...")
            result = compare_random_vs_learned(
                env_factory,
                n_steps=args.steps,
                n_seeds=args.seeds,
                learner="reinforce",
                learner_kwargs={"lr": args.lr},
            )
            if result.get("skipped"):
                print(f"[SKIPPED again] {result.get('reason')}")
                return 1

    print(f"{'agent':<10}  {'mean':>10}  {'std':>10}  {'per-seed':<40}")
    print("-" * 80)
    rmeans = ", ".join(f"{m:.2f}" for m in result["random_means"])
    lmeans = ", ".join(f"{m:.2f}" for m in result["learned_means"])
    print(f"{'random':<10}  {result['random_mean']:>10.3f}  {result['random_std']:>10.3f}  [{rmeans}]")
    print(f"{result['learner']:<10}  {result['learned_mean']:>10.3f}  {result['learned_std']:>10.3f}  [{lmeans}]")
    print()
    print(f"lift     = {result['lift']:+.4f}  (= (learned - random) / |random|)")
    print(f"p-value  = {result['p_value']:.4g}  (Welch's t, H1: learned > random)")
    print()

    verdict_lines = []
    if result["p_value"] < 0.05 and result["lift"] > 0.05:
        verdict_lines.append(f"VERDICT: learning beats random at {args.steps} steps (p < 0.05, lift > 5%).")
        verdict_lines.append("The reward signal is LEARNABLE.")
    elif result["lift"] > 0:
        verdict_lines.append(f"VERDICT: learning improves over random at {args.steps} steps (lift={result['lift']:+.3f}),")
        verdict_lines.append(f"but signal not statistically significant at this seed budget (p={result['p_value']:.3g}).")
        verdict_lines.append("Try more seeds or more steps.")
    else:
        verdict_lines.append(f"VERDICT: no learning observed at {args.steps} steps (lift={result['lift']:+.3f}).")
        verdict_lines.append("Likely cause: env too easy (random already finds high-reward actions),")
        verdict_lines.append("or reward signal dominated by noise. Increase max_steps, lower lr, or")
        verdict_lines.append("rebalance the action table to include more low-reward distractors.")
    for line in verdict_lines:
        print(line)
    print()

    if args.plot:
        out = learning_curve_plot(result, args.plot)
        if out:
            print(f"plot saved: {out}")
        else:
            print(f"plot SKIPPED (matplotlib missing or run was skipped)")

    if args.json:
        # Strip non-JSON-serializable arrays before dumping.
        summary = {
            k: v for k, v in result.items()
            if k not in {"rewards_random_curve", "rewards_learned_curve",
                          "random_curve_std", "learned_curve_std"}
        }
        with open(args.json, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"summary json saved: {args.json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
