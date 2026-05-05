"""prometheus_math.demo_withheld_benchmark — §6.2.5 calibration pilot.

CLI driver for the withheld-rediscovery benchmark. Partitions
Mossinghoff's snapshot 80/20, runs REINFORCE on DiscoveryEnv with the
withheld pipeline, reports per-seed and aggregate rediscovery rates.

Usage::

    python -m prometheus_math.demo_withheld_benchmark \\
        --episodes 1000 --seeds 3 --holdout 0.2 --partition-seed 42

The output is the calibration estimate for §6.2's open-discovery
pilot's expected rate. If REINFORCE rediscovers k of N withheld
entries in M episodes/seed across S seeds, then ~k/(M*S) is a
plausible per-episode lower bound on §6.2's discovery rate (lower
because §6.2 has no withheld-target lift; the agent has to find
genuinely new sub-Lehmer polynomials).
"""
from __future__ import annotations

import argparse
import sys
import time
from typing import List

from .withheld_benchmark import (
    WithheldPartition,
    WithheldResult,
    partition_mossinghoff,
    run_withheld_pilot,
)


def _print_partition(p: WithheldPartition) -> None:
    print("=" * 72)
    print("WITHHELD-REDISCOVERY BENCHMARK (§6.2.5)")
    print("=" * 72)
    print(f"  Mossinghoff snapshot:   {p.n_visible + p.n_withheld} entries")
    print(f"  Visible (kept):         {p.n_visible}")
    print(f"  Withheld (held-out):    {p.n_withheld}")
    print(f"  Partition seed:         {p.partition_seed}")
    print()
    print("  Withheld M-values (first 10):")
    for i, (_, m) in enumerate(p.withheld_set[:10]):
        print(f"    [{i:3d}] M = {m:.10f}")
    if p.n_withheld > 10:
        print(f"    ... and {p.n_withheld - 10} more.")


def _print_result(r: WithheldResult, episodes_per_seed: int, seeds: int) -> None:
    print()
    print("-" * 72)
    print("RESULT")
    print("-" * 72)
    print(f"  Episodes per seed:           {episodes_per_seed}")
    print(f"  Seeds:                       {seeds}")
    print(f"  Total episode budget:        {episodes_per_seed * seeds}")
    print()
    print("  Per-seed rediscovery counts:")
    for s, info in sorted(r.by_seed.items()):
        print(
            f"    seed={s}:  rediscovered={info['rediscovery_count']:3d}/"
            f"{r.n_withheld}  promoted={info['promote_count']:3d}"
        )
    print()
    print("  Aggregate (union across seeds):")
    print(
        f"    withheld_rediscovery_count = "
        f"{r.withheld_rediscovery_count}/{r.n_withheld}"
    )
    print(
        f"    withheld_rediscovery_rate  = "
        f"{r.withheld_rediscovery_rate:.4f}"
    )
    print(
        f"    withheld_PROMOTE_count     = "
        f"{r.withheld_PROMOTE_count}/{r.n_withheld}"
    )
    print(
        f"    withheld_PROMOTE_rate      = {r.withheld_PROMOTE_rate:.4f}"
    )
    if r.withheld_rediscovery_count > 0:
        eps = r.episodes_per_rediscovery
        print(f"    episodes_per_rediscovery   = {eps:.1f}")
        per_1000 = 1000.0 / eps
        print(
            f"    extrapolated rate per 1000 episodes = "
            f"{per_1000:.3f} rediscoveries"
        )
    else:
        print(
            f"    episodes_per_rediscovery   = inf "
            f"(no rediscoveries; upper bound on rate is "
            f"~1/{episodes_per_seed * seeds})"
        )

    print()
    print("CALIBRATION INTERPRETATION (§6.2.5)")
    print("-" * 72)
    rate = r.withheld_rediscovery_rate
    if r.withheld_rediscovery_count == 0:
        print(
            "  The agent rediscovered 0 of {} withheld entries. This sets a\n"
            "  per-1000-episode upper bound for §6.2's open-discovery rate at\n"
            "  ~1/{} episodes. If §6.2 produces sub-Lehmer hits faster than\n"
            "  this, those hits are very likely numerical artifacts, not\n"
            "  genuine discoveries.".format(
                r.n_withheld, episodes_per_seed * seeds
            )
        )
    else:
        print(
            f"  The agent rediscovered {r.withheld_rediscovery_count} of "
            f"{r.n_withheld} withheld entries\n"
            f"  ({rate * 100:.1f}%). This is the system's discovery-shape\n"
            f"  capability measured against KNOWN ground truth. Use it as a\n"
            f"  realistic upper bound for §6.2's open-discovery rate; novel\n"
            f"  discoveries (no withheld-target hint) should fire LESS often."
        )


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--episodes",
        type=int,
        default=1000,
        help="Episodes per seed (default 1000)",
    )
    parser.add_argument(
        "--seeds",
        type=int,
        default=3,
        help="Number of random seeds (default 3)",
    )
    parser.add_argument(
        "--holdout",
        type=float,
        default=0.2,
        help="Fraction of Mossinghoff entries to withhold (default 0.2)",
    )
    parser.add_argument(
        "--partition-seed",
        type=int,
        default=42,
        help="Random seed for the partition itself (default 42)",
    )
    parser.add_argument(
        "--agent",
        choices=["reinforce", "random"],
        default="reinforce",
        help="Which agent to drive the env (default reinforce)",
    )
    args = parser.parse_args(argv)

    partition = partition_mossinghoff(
        holdout_fraction=args.holdout, seed=args.partition_seed
    )
    _print_partition(partition)

    seeds = tuple(range(int(args.seeds)))
    print()
    print(
        f"  Running {args.agent} pilot: "
        f"{args.episodes} episodes × {len(seeds)} seeds = "
        f"{args.episodes * len(seeds)} total episodes..."
    )
    t0 = time.perf_counter()
    result = run_withheld_pilot(
        partition,
        n_episodes=args.episodes,
        seeds=seeds,
        agent=args.agent,
    )
    elapsed = time.perf_counter() - t0
    print(f"  Pilot complete in {elapsed:.1f}s.")

    _print_result(result, args.episodes, len(seeds))

    return 0


if __name__ == "__main__":
    sys.exit(main())
