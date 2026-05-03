"""prometheus_math.demo_four_counts -- §6.2 + §6.4 pilot CLI driver.

Runs the unified four-counts harness on `DiscoveryEnv`, comparing
uniform-random null sampling (the §6.2 null + §6.4 non-LLM mutation
source) against contextual REINFORCE (the §6.2 LLM-driven agent).

Usage::

    python -m prometheus_math.demo_four_counts --episodes 1000 --seeds 3

For dev cycles use 1000 episodes (not 10K -- keeps runtime under 5 min);
the spec target is 10K but acceptance is the COMPARISON SHAPE, not the
absolute count.

Honest framing: at 1000 episodes both PROMOTE rates may be 0 (the +100
sub-Lehmer band is empirically unreachable per Lehmer's conjecture).
That is STILL informative -- it bounds the discovery rate from above.
The harness's job is to surface that bound, not to manufacture
significance.

Interpretation key:
  - random_null PROMOTE > 0 and REINFORCE PROMOTE = 0   -> LLM prior too tight
  - REINFORCE PROMOTE >> random_null PROMOTE  (sig)     -> prior well-tuned
  - both = 0                                            -> joint upper bound;
                                                            need 10K episodes
                                                            or different env
                                                            knobs (action set,
                                                            band width, battery
                                                            tightness)
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import List

from .discovery_env import DiscoveryEnv
from .four_counts_pilot import (
    compare_conditions,
    print_pilot_table,
    run_random_null,
    run_reinforce_agent,
)


def _build_env_factory(degree: int, cost_seconds: float):
    def _factory():
        return DiscoveryEnv(
            degree=degree,
            kernel_db_path=":memory:",
            cost_seconds=cost_seconds,
            log_discoveries=True,
            enable_pipeline=True,
        )

    return _factory


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--episodes",
        type=int,
        default=1000,
        help="Episodes per (condition, seed) cell.  Spec target: 10K. "
        "Default 1000 keeps the dev loop under 5 min.",
    )
    parser.add_argument(
        "--seeds",
        type=int,
        default=3,
        help="Number of seeds (variance estimate).  Welch t-test needs >= 2.",
    )
    parser.add_argument("--degree", type=int, default=10)
    parser.add_argument("--lr", type=float, default=0.05)
    parser.add_argument("--entropy-coef", type=float, default=0.05)
    parser.add_argument(
        "--cost-seconds", type=float, default=0.5, help="Per-EVAL budget"
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default=None,
        help="Optional path to write the comparison JSON",
    )
    args = parser.parse_args(argv)

    env_factory = _build_env_factory(args.degree, args.cost_seconds)
    seeds = list(range(args.seeds))
    lr = args.lr
    entropy_coef = args.entropy_coef

    cb = {
        "random_null": (
            lambda env_factory_, n_episodes_, seed_: run_random_null(
                env_factory_, n_episodes_, seed_
            )
        ),
        "reinforce_agent": (
            lambda env_factory_, n_episodes_, seed_: run_reinforce_agent(
                env_factory_,
                n_episodes_,
                seed_,
                lr=lr,
                entropy_coef=entropy_coef,
            )
        ),
    }

    print("=" * 78)
    print(
        f"FOUR-COUNTS PILOT  degree={args.degree}  episodes={args.episodes}"
        f"  seeds={seeds}"
    )
    print("=" * 78)
    t0 = time.perf_counter()
    out = compare_conditions(
        env_factory,
        n_episodes=args.episodes,
        seeds=seeds,
        condition_callables=cb,
    )
    elapsed = time.perf_counter() - t0
    print(f"\n[total elapsed: {elapsed:.1f}s]\n")

    print_pilot_table(out)

    # Per-condition kill_pattern breakdowns.
    print("\nKill-pattern breakdown by condition:")
    for label, info in out["per_condition"].items():
        print(f"\n  [{label}]")
        all_kp: dict[str, int] = {}
        for r in info["results"]:
            for k, v in r.by_kill_pattern.items():
                all_kp[k] = all_kp.get(k, 0) + v
        if not all_kp:
            print("    (no kill patterns recorded)")
            continue
        # Top 8.
        for k, v in sorted(all_kp.items(), key=lambda kv: -kv[1])[:8]:
            print(f"    {k:<60}{v:>6}")

    # Honest interpretation block.
    print("\n" + "-" * 78)
    print("HONEST INTERPRETATION")
    print("-" * 78)
    rn = out["per_condition"]["random_null"]["promote_rate_mean"]
    re = out["per_condition"]["reinforce_agent"]["promote_rate_mean"]
    if rn == 0 and re == 0:
        print(
            f"  Both PROMOTE rates are 0 across {args.episodes} episodes x "
            f"{args.seeds} seeds.\n"
            f"  This is a JOINT UPPER BOUND on discovery rate at this config:\n"
            f"  the action space + prior + battery jointly admit fewer than\n"
            f"  ~ 1 / ({args.episodes * args.seeds}) sub-Lehmer survivors.\n"
            f"  Per spec §6.2: 'a useful joint upper bound' -- still informative.\n"
            f"  Next moves: scale to 10K episodes; widen action set; loosen\n"
            f"  battery; or look at the catalog-hit + claim rates as proxy\n"
            f"  signals (rediscovery is the calibration-grade observable)."
        )
    elif re > rn:
        print(
            f"  REINFORCE PROMOTE rate ({re:.4f}) > random ({rn:.4f}).\n"
            f"  Per §6.4: this suggests the LLM prior is WELL-TUNED to the\n"
            f"  search problem (the prior amplifies signal-class survival).\n"
            f"  Significance: see Welch t-test p-value above."
        )
    else:
        print(
            f"  random_null PROMOTE rate ({rn:.4f}) >= REINFORCE ({re:.4f}).\n"
            f"  Per §6.4: this suggests the LLM prior is TOO TIGHT -- the\n"
            f"  prior is concentrating on a bad region.  Loosen entropy_coef,\n"
            f"  raise lr, or rebuild the policy class."
        )
    print("-" * 78)

    # Optional JSON dump (drop FourCountsResult objects -- not JSON-serializable
    # without a converter).
    if args.json_out:
        serialisable = {
            "n_episodes": out["n_episodes"],
            "n_seeds": out["n_seeds"],
            "annotation": out["annotation"],
            "per_condition": {
                label: {
                    "promote_rate_mean": info["promote_rate_mean"],
                    "promote_rate_std": info["promote_rate_std"],
                    "promote_rates": info["promote_rates"],
                    "catalog_hit_rate_mean": info["catalog_hit_rate_mean"],
                    "claim_rate_mean": info["claim_rate_mean"],
                }
                for label, info in out["per_condition"].items()
            },
            "pairwise": {
                f"{a}__vs__{b}": v for (a, b), v in out["pairwise"].items()
            },
        }
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(serialisable, f, indent=2)
        print(f"\n[wrote JSON to {args.json_out}]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
