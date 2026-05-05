"""Trial 3 5K-episode scaling pilot — does the engine reach OBSTRUCTION exact match?

Per Iter 19 / Task #77. Iter 11 at 1K x 3 seeds achieved:
  - 2/3 seeds: OBSTRUCTION discriminator {n_steps:5, neg_x:4} (2-conjunct, parsimonious)
  - 2/3 seeds: SECONDARY_SIGNATURE exact (2-conjunct: {n_steps:7, has_diag_pos:True})
  - 0/3 seeds: OBSTRUCTION_SIGNATURE exact (4-conjunct)

The question this pilot answers: does scaling 1K -> 5K episodes give the engine
enough combinatorial budget to assemble the full 4-conjunct OBSTRUCTION_SIGNATURE
exactly, or does it remain at the 2-conjunct minimum-discriminator parsimony?

Either result is informative:
  - If 5K reaches exact match: the engine just needs more steps (compute scaling).
  - If 5K stays at discriminator: the engine has found the parsimonious solution
    and is correctly NOT pursuing redundant conjuncts (substrate-grade finding).

Reuses HardenedObstructionEvaluator + Iter 18 weights from trial_3_production_pilot.
"""
from __future__ import annotations

import json
import random
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List

from ergon.learner.trials.trial_3_production_pilot import (
    aggregate,
    format_report,
    run_one_seed,
)


if __name__ == "__main__":
    seeds = [42, 100, 1234]
    n_episodes = 5000
    per_seed = []
    print(f"Trial 3 5K-scaling pilot: {n_episodes} x {len(seeds)} seeds...")
    print("(this should take ~5x longer than the 1K pilot)")
    for seed in seeds:
        print(f"  Seed {seed}...", end=" ", flush=True)
        t0 = time.time()
        result = run_one_seed(seed, n_episodes=n_episodes)
        print(
            f"obstruction={result['obstruction_hits']} "
            f"obs_disc={result['obstruction_discriminator_hits']} "
            f"secondary={result['secondary_hits']} "
            f"sec_disc={result['secondary_discriminator_hits']} "
            f"high_lift={result['n_high_lift']} "
            f"({time.time()-t0:.0f}s)"
        )
        per_seed.append(result)

    agg = aggregate(per_seed)
    out_dir = Path(__file__).parent
    (out_dir / "trial_3_5k_results.json").write_text(
        json.dumps({"per_seed": per_seed, "aggregate": agg},
                   indent=2, default=str), encoding="utf-8"
    )
    report = format_report(per_seed, agg)
    # Patch the title since format_report hard-codes "1000"
    report = report.replace(
        "Trial 3 Production Pilot — 1000 episodes",
        f"Trial 3 5K Scaling Pilot — {n_episodes} episodes",
    )
    (out_dir / "TRIAL_3_5K_SCALING_REPORT.md").write_text(report, encoding="utf-8")
    print()
    print(report)
