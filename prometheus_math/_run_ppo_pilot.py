"""prometheus_math._run_ppo_pilot -- four-counts pilot, path B (PPO).

Runs random_null vs REINFORCE vs PPO at degree=10, default
``coefficient_choices`` (-3..3), reward_shape='step', 10K episodes x
3 seeds each. Captures per-seed PROMOTE/SHADOW/catalog-hit/Salem-band
counts and pickles the rich structure to JSON for the markdown writer.

This is the path-B test from the Apr-29 triple-#3: is REINFORCE+linear-
policy too weak even at the calibrated configuration, or is the +100
sub-Lehmer band genuinely empty (Lehmer's conjecture)?
"""
from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from prometheus_math.discovery_env import DiscoveryEnv
from prometheus_math.four_counts_pilot import (
    FourCountsResult,
    compare_conditions,
    run_ppo_agent,
    run_random_null,
    run_reinforce_agent,
)


def _env_factory():
    return DiscoveryEnv(degree=10, reward_shape="step")


def _serialize_result(r: FourCountsResult) -> Dict[str, Any]:
    return {
        "condition_label": r.condition_label,
        "total_episodes": r.total_episodes,
        "catalog_hit_count": r.catalog_hit_count,
        "claim_into_kernel_count": r.claim_into_kernel_count,
        "promote_count": r.promote_count,
        "shadow_catalog_count": r.shadow_catalog_count,
        "rejected_count": r.rejected_count,
        "by_kill_pattern": dict(r.by_kill_pattern),
        "elapsed_seconds": r.elapsed_seconds,
        "seed": r.seed,
        "promote_rate": r.promote_rate,
        "catalog_hit_rate": r.catalog_hit_rate,
        "claim_rate": r.claim_rate,
    }


def _salem_count(by_kp: Dict[str, int]) -> int:
    """Tally upstream:salem_cluster bucket (Salem-band proxy)."""
    return int(by_kp.get("upstream:salem_cluster", 0))


def main(n_episodes: int = 10_000, seeds: List[int] = [0, 1, 2]) -> None:
    out_path = Path(__file__).parent / "four_counts_ppo_run.json"
    log_path = Path(__file__).parent / "four_counts_ppo_run.log"

    print(f"[ppo-pilot] n_episodes={n_episodes} seeds={seeds}")
    print(f"[ppo-pilot] env: degree=10, ±3, reward_shape='step'")
    print(f"[ppo-pilot] arms: random_null, reinforce_agent, ppo_agent")

    cb = {
        "random_null": lambda f, n, s: run_random_null(f, n, s),
        "reinforce_agent": lambda f, n, s: run_reinforce_agent(
            f, n, s, lr=0.05, entropy_coef=0.05
        ),
        "ppo_agent": lambda f, n, s: run_ppo_agent(f, n, s),
    }

    t_total = time.perf_counter()
    out = compare_conditions(
        _env_factory,
        n_episodes=n_episodes,
        seeds=seeds,
        condition_callables=cb,
    )
    total_elapsed = time.perf_counter() - t_total

    # Build the JSON dump.
    dump: Dict[str, Any] = {
        "n_episodes": n_episodes,
        "seeds": seeds,
        "total_elapsed_seconds": total_elapsed,
        "env": {
            "degree": 10,
            "coefficient_choices": [-3, -2, -1, 0, 1, 2, 3],
            "reward_shape": "step",
        },
        "per_condition": {},
        "pairwise": {},
    }
    for label, info in out["per_condition"].items():
        results = info["results"]
        dump["per_condition"][label] = {
            "promote_rate_mean": info["promote_rate_mean"],
            "promote_rate_std": info["promote_rate_std"],
            "promote_rates": info["promote_rates"],
            "catalog_hit_rate_mean": info["catalog_hit_rate_mean"],
            "claim_rate_mean": info["claim_rate_mean"],
            "results": [_serialize_result(r) for r in results],
            "salem_total": sum(
                _salem_count(r.by_kill_pattern) for r in results
            ),
            "salem_per_seed": [
                _salem_count(r.by_kill_pattern) for r in results
            ],
        }
    for (a, b), info in out["pairwise"].items():
        dump["pairwise"][f"{a}__vs__{b}"] = {
            "p_value": info["p_value"],
            "lift": info["lift"],
            "winner": info["winner"],
            "mean_a": info["mean_a"],
            "mean_b": info["mean_b"],
        }

    out_path.write_text(json.dumps(dump, indent=2, default=str))
    print(f"[ppo-pilot] wrote {out_path}")
    print(f"[ppo-pilot] total elapsed = {total_elapsed:.1f}s")

    # Quick stdout table.
    print("=" * 78)
    print(f"FOUR-COUNTS PILOT path B (PPO)  n={n_episodes} per cell  seeds={seeds}")
    print("=" * 78)
    print(
        f"{'condition':<22}"
        f"{'PROMOTE':>10}{'SHADOW':>10}{'cat-hit':>10}"
        f"{'salem':>10}{'elapsed':>10}"
    )
    print("-" * 78)
    for label, info in dump["per_condition"].items():
        promote = sum(r["promote_count"] for r in info["results"])
        shadow = sum(r["shadow_catalog_count"] for r in info["results"])
        cathit = sum(r["catalog_hit_count"] for r in info["results"])
        salem = info["salem_total"]
        elapsed = sum(r["elapsed_seconds"] for r in info["results"])
        print(
            f"{label:<22}{promote:>10}{shadow:>10}{cathit:>10}"
            f"{salem:>10}{elapsed:>9.1f}s"
        )
    print("-" * 78)

    # Per-seed for ppo
    print("\nper-seed (ppo_agent):")
    for r in dump["per_condition"]["ppo_agent"]["results"]:
        salem = _salem_count(r["by_kill_pattern"])
        print(
            f"  seed={r['seed']}  promote={r['promote_count']}  "
            f"shadow={r['shadow_catalog_count']}  cat={r['catalog_hit_count']}"
            f"  salem={salem}  elapsed={r['elapsed_seconds']:.1f}s"
        )

    print("\nSHADOW_CATALOG entries:")
    total_shadow = sum(
        sum(r["shadow_catalog_count"] for r in info["results"])
        for info in dump["per_condition"].values()
    )
    if total_shadow == 0:
        print("  (none across all arms x seeds)")
    else:
        for label, info in dump["per_condition"].items():
            for r in info["results"]:
                if r["shadow_catalog_count"] > 0:
                    print(
                        f"  {label} seed={r['seed']}: "
                        f"shadow_catalog_count={r['shadow_catalog_count']}"
                    )


if __name__ == "__main__":
    import sys

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000
    main(n_episodes=n, seeds=[0, 1, 2])
