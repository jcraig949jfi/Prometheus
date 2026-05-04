"""Trial 3 iter-13 extended — does 10K eps at rate=0.15 recover both obs exact and sec exact?

Iter 13 (5K eps) showed exploration_rate=0.15 recovers 3/3 SECONDARY but drops to
2/3 OBSTRUCTION exact (was 3/3 at rate=0.0). This extends the budget to 10K to
test if the missing OBSTRUCTION exact emerges with more steps (the hypothesis is
that exploration_rate slows convergence proportionally — so 10K at 0.15 should
match 5K at 0.0 on OBSTRUCTION exact while keeping the 3/3 SECONDARY win).
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from ergon.learner.trials.trial_3_iter13_exploration import (
    run_one_seed_with_exploration,
)
from ergon.learner.trials.trial_3_production_pilot import aggregate, format_report


if __name__ == "__main__":
    seeds = [42, 100, 1234]
    n_episodes = 10000
    rate = 0.15
    print(f"Trial 3 iter-13 extended: {n_episodes} x {len(seeds)} seeds at rate={rate}")

    per_seed = []
    for seed in seeds:
        print(f"  Seed {seed}...", end=" ", flush=True)
        t0 = time.time()
        result = run_one_seed_with_exploration(
            seed, n_episodes=n_episodes, exploration_rate=rate
        )
        print(
            f"obs={result['obstruction_hits']} "
            f"obs_disc={result['obstruction_discriminator_hits']} "
            f"sec={result['secondary_hits']} "
            f"sec_disc={result['secondary_discriminator_hits']} "
            f"({time.time()-t0:.0f}s)"
        )
        per_seed.append(result)

    agg = aggregate(per_seed)
    out_dir = Path(__file__).parent
    (out_dir / "trial_3_iter13_extended_results.json").write_text(
        json.dumps({"per_seed": per_seed, "aggregate": agg, "config": {
            "n_episodes": n_episodes, "exploration_rate": rate,
        }}, indent=2, default=str), encoding="utf-8"
    )

    print()
    print(f"AT 10K eps with rate={rate}:")
    print(f"  OBSTRUCTION exact:   {agg['n_seeds_hit_obstruction']}/3 seeds")
    print(f"  OBSTRUCTION disc:    {agg['n_seeds_hit_obstruction_discriminator']}/3 seeds")
    print(f"  SECONDARY exact:     {agg['n_seeds_hit_secondary']}/3 seeds")
    print(f"  SECONDARY disc:      {agg['n_seeds_hit_secondary_discriminator']}/3 seeds")
    print(f"  First-obs eps:       {agg['first_obstruction_episodes']}")
    print(f"  First-sec eps:       {agg['first_secondary_episodes']}")
    print(f"  Substrate-passed:    {agg['substrate_passed_total']}")
    print(f"  structural/uniform:  {agg['structural_uniform_ratio']:.2f}x")
