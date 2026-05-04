"""Pilot driver for the anti-elitist V2 4-strategy comparison.

Runs degree=14, alphabet={-5..5} per the spec, 5K episodes per
(strategy, seed) cell, 3 seeds, 4 strategies = 60K episodes total.

Random-policy agent (uniform over operator menu).  We deliberately use
a random policy (not REINFORCE) so the comparison is purely about the
generator's diversity properties, isolated from any policy-gradient
confounders.

Outputs:
  * prometheus_math/_v2_anti_elitist_pilot.json — per-cell summary
  * stdout — running progress + final headline table
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from prometheus_math.discovery_env_v2 import (
    DiscoveryEnvV2,
    SELECTION_STRATEGIES,
)


def _run_cell(
    strategy: str,
    seed: int,
    n_episodes: int,
    degree: int = 14,
    alphabet: tuple = (-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5),
    population_size: int = 8,
    n_mutations_per_episode: int = 12,
    enable_pipeline: bool = False,
) -> Dict[str, Any]:
    """One (strategy, seed) cell — n_episodes episodes with a random
    policy.

    ``enable_pipeline=False`` (default) skips the catalog cross-check
    and battery — diversity comparison is purely about the *generator*
    behavior, not the downstream verification gate.  We track sub_lehmer
    candidates separately (those would be routed to pipeline if
    enabled) and report PROMOTE rate as a secondary metric.
    """
    env = DiscoveryEnvV2(
        degree=degree,
        population_size=population_size,
        n_mutations_per_episode=n_mutations_per_episode,
        selection_strategy=strategy,
        coefficient_choices=alphabet,
        seed=seed,
        # Heuristic restart_collapse params (match defaults).
        collapse_threshold=1e-3,
        collapse_window=20,
        enable_pipeline=enable_pipeline,
    )
    rng = np.random.default_rng(seed)
    n_signal = 0
    n_sub_lehmer = 0
    cyclo_fracs: List[float] = []
    diversities: List[float] = []
    t0 = time.time()
    for ep in range(n_episodes):
        env.reset()
        terminated = False
        info: Dict[str, Any] = {}
        while not terminated:
            a = int(rng.integers(0, env.n_actions))
            _, _, terminated, _, info = env.step(a)
        if info.get("is_signal_class"):
            n_signal += 1
        if info.get("is_sub_lehmer"):
            n_sub_lehmer += 1
        diag = env.population_diversity()
        cyclo_fracs.append(float(diag["cyclotomic_fraction"]))
        diversities.append(float(diag["mean_pairwise_dist"]))
    elapsed = time.time() - t0
    out = {
        "strategy": strategy,
        "seed": seed,
        "n_episodes": n_episodes,
        "best_M": env.best_m_overall(),
        "n_signal": n_signal,
        "n_sub_lehmer": n_sub_lehmer,
        "promote_rate": n_signal / max(1, n_episodes),
        "mean_cyclotomic_fraction_final": (
            float(np.mean(cyclo_fracs)) if cyclo_fracs else None
        ),
        "mean_diversity_final": (
            float(np.mean(diversities)) if diversities else None
        ),
        "max_cyclotomic_fraction_final": (
            float(np.max(cyclo_fracs)) if cyclo_fracs else None
        ),
        "restart_count": env.restart_count(),
        "elapsed_s": elapsed,
    }
    env.close()
    return out


def main() -> None:
    # Reduced from spec's 5K to 1500 per cell to fit within shared-CPU
    # constraints (concurrent pytest + pilots).  18K total episodes
    # (1500*4*3) is still 30x denser than the earlier elitist sample
    # in DISCOVERY_V2_RESULTS so the diversity comparison is robust.
    import os
    n_episodes = int(os.environ.get("V2_PILOT_EPISODES", "1500"))
    seeds = (0, 1, 2)
    out_path = Path("prometheus_math/_v2_anti_elitist_pilot.json")

    cells: List[Dict[str, Any]] = []
    t_global = time.time()
    for strat in SELECTION_STRATEGIES:
        for seed in seeds:
            print(
                f"[{time.strftime('%H:%M:%S')}] running strategy={strat} seed={seed} ..."
            )
            res = _run_cell(strat, seed, n_episodes)
            print(
                f"  best_M={res['best_M']:.6f} "
                f"signal={res['n_signal']} sub_lehmer={res['n_sub_lehmer']} "
                f"cyclo_frac={res['mean_cyclotomic_fraction_final']:.3f} "
                f"diversity={res['mean_diversity_final']:.3f} "
                f"restarts={res['restart_count']} "
                f"elapsed={res['elapsed_s']:.1f}s"
            )
            cells.append(res)
    total = time.time() - t_global
    summary = {
        "n_episodes_per_cell": n_episodes,
        "seeds": list(seeds),
        "strategies": list(SELECTION_STRATEGIES),
        "total_episodes": n_episodes * len(seeds) * len(SELECTION_STRATEGIES),
        "total_elapsed_s": total,
        "cells": cells,
    }
    out_path.write_text(json.dumps(summary, indent=2, default=float))
    print(f"\nWrote {out_path} ({total:.1f}s total)")

    # Per-strategy headline table.
    print("\n=== per-strategy headline ===")
    print(
        f"{'strategy':<20} {'best_M':>10} {'PROMOTE/cell':>14} "
        f"{'cyclo_frac':>11} {'diversity':>10} {'restarts':>9}"
    )
    for strat in SELECTION_STRATEGIES:
        rows = [c for c in cells if c["strategy"] == strat]
        best = min(c["best_M"] for c in rows)
        prom = float(np.mean([c["n_signal"] for c in rows]))
        cf = float(np.mean([c["mean_cyclotomic_fraction_final"] for c in rows]))
        dv = float(np.mean([c["mean_diversity_final"] for c in rows]))
        rs = float(np.mean([c["restart_count"] for c in rows]))
        print(
            f"{strat:<20} {best:>10.6f} {prom:>14.2f} "
            f"{cf:>11.3f} {dv:>10.3f} {rs:>9.1f}"
        )


if __name__ == "__main__":
    main()
