"""prometheus_math.sigma_env demo — random agent over the substrate.

Runs a random-action agent against the Lehmer-Mahler-measure env for
``--steps`` steps and prints reward + best-M-found progress. Proves the
RL loop closes end-to-end: arsenal_meta -> BIND -> EVAL -> falsification
-> reward -> agent -> next action.

Run::

    python -m prometheus_math.demo_sigma_env --steps 30 --seed 0

Default: 30 steps, seed 0. The default action table contains Lehmer's
polynomial, so within ~30 random pulls a random agent should hit the
high-reward action at least once and trip the +100 / target-hit branch.
"""
from __future__ import annotations

import argparse
import sys

import numpy as np

from .sigma_env import SigmaMathEnv


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--objective",
        type=str,
        default="minimize_mahler_measure",
        choices=["minimize_mahler_measure", "riemann_zeros"],
    )
    args = parser.parse_args(argv)

    env = SigmaMathEnv(
        objective=args.objective,
        max_steps=args.steps,
        seed=args.seed,
    )
    obs, info = env.reset()
    rng = np.random.default_rng(args.seed)
    n_actions = info["n_actions"]
    print(f"env reset: n_actions={n_actions} objective={args.objective}")
    table = env.action_table()
    print("action table:")
    for row in table:
        print(f"  [{row.op_id:2d}] {row.callable_ref.split(':')[-1]:30s}  {row.arg_label}")

    cum_reward = 0.0
    best_value = None
    best_arg = None
    n_terminated = 0
    print()
    print(f"{'step':>4} {'action':>6} {'reward':>8} {'best_M':>10} {'arg_label':<30}")
    for step in range(args.steps):
        a = int(rng.integers(0, n_actions))
        obs, r, terminated, truncated, info = env.step(a)
        cum_reward += r
        v = info.get("output_value")
        if (
            args.objective == "minimize_mahler_measure"
            and isinstance(v, (int, float))
            and 1.0 <= v < 1e6
            and (best_value is None or v < best_value)
        ):
            best_value = float(v)
            best_arg = info["arg_label"]
        best_str = f"{best_value:.4f}" if best_value is not None else "  --  "
        print(
            f"{step:>4d} {a:>6d} {r:>8.2f} {best_str:>10s} {info['arg_label']:<30}"
        )
        if terminated:
            n_terminated += 1
            print(f"  -> terminated at step {step} (target hit)")
            obs, info = env.reset(seed=args.seed + 1 + n_terminated)
            n_actions = info["n_actions"]

    print()
    print(f"cumulative reward: {cum_reward:.2f}")
    if best_value is not None:
        print(f"best M found:      {best_value:.6f} (via {best_arg!r})")
    print(f"terminations:      {n_terminated}")

    # Substrate growth.
    k = env.kernel()
    cur = k.conn.execute("SELECT COUNT(*) FROM bindings")
    n_b = cur.fetchone()[0]
    cur = k.conn.execute("SELECT COUNT(*) FROM evaluations")
    n_e = cur.fetchone()[0]
    print(f"substrate state:   {n_b} bindings, {n_e} evaluations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
