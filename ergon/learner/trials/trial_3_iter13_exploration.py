"""Trial 3 iter-13 — does exploration_rate=0.25 recover SECONDARY in seed 1234?

Per Iter 12 mode-collapse finding (Task #78). At 5K eps with substrate_pass_bias=5.0:
  - 3/3 seeds find OBSTRUCTION exact (good)
  - 2/3 seeds find SECONDARY exact — seed 1234 misses it (bad)

The hypothesis: bias=5.0 concentrates descendants around the first substrate-passing
parent's territory, starving exploration of unrelated regions. Fix: exploration_rate
parameter (default 0.0, set to 0.25 here) makes 25% of parent samples bypass the
bias and pick uniformly from all filled cells.

Acceptance: 3/3 seeds find BOTH OBSTRUCTION and SECONDARY at 5K eps.
"""
from __future__ import annotations

import json
import math
import random
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

from prometheus_math._obstruction_corpus import (
    OBSTRUCTION_CORPUS,
    OBSTRUCTION_SIGNATURE,
    SECONDARY_SIGNATURE,
)
from prometheus_math.obstruction_env import evaluate_predicate

from ergon.learner.archive import FitnessTuple, MAPElitesArchive
from ergon.learner.descriptor import (
    EvaluationResult,
    compute_cell_coordinate,
)
from ergon.learner.genome import Genome
from ergon.learner.operators.anti_prior import AntiPriorOperator
from ergon.learner.operators.predicate_symbolic import PredicateSymbolicOperator
from ergon.learner.operators.structural import StructuralOperator
from ergon.learner.operators.uniform import UniformOperator
from ergon.learner.scheduler import OperatorScheduler
from ergon.learner.trials.trial_3_obstruction_smoke import (
    genome_to_predicate,
    make_obstruction_atom_pool,
)
from ergon.learner.trials.trial_3_production_pilot import (
    HardenedObstructionEvaluator,
    aggregate,
    format_report,
)


def run_one_seed_with_exploration(
    seed: int,
    n_episodes: int = 5000,
    exploration_rate: float = 0.25,
) -> Dict[str, Any]:
    """Mirror of trial_3_production_pilot.run_one_seed but parameterizes
    exploration_rate on archive.sample_parent."""
    atom_pool = make_obstruction_atom_pool()
    evaluator = HardenedObstructionEvaluator()
    archive = MAPElitesArchive()
    rng = random.Random(seed)

    custom_weights = {
        "structural": 0.65,
        "symbolic": 0.15,
        "uniform": 0.05,
        "structured_null": 0.05,
        "anti_prior": 0.10,
    }
    scheduler = OperatorScheduler(operator_weights=custom_weights, seed=seed)

    operators = {
        "structural": StructuralOperator(),
        "symbolic": PredicateSymbolicOperator(),
        "uniform": UniformOperator(n_atoms_distribution=(1, 4)),
        "structured_null": UniformOperator(n_atoms_distribution=(2, 4)),
        "anti_prior": AntiPriorOperator(),
    }

    obstruction_hits: List[int] = []
    secondary_hits: List[int] = []
    obstruction_discriminator_hits: List[Tuple[int, Dict[str, Any]]] = []
    secondary_discriminator_hits: List[Tuple[int, Dict[str, Any]]] = []
    substrate_passed = 0
    high_lift_predicates: List[Dict[str, Any]] = []

    t_start = time.time()

    for ep in range(n_episodes):
        op_class = scheduler.next_operator_class(ep)
        op_name = op_class if op_class in operators else "uniform"
        operator = operators[op_name]

        parent = None
        if op_name in ("structural", "symbolic") and archive.n_cells_filled() > 0:
            parent_entry = archive.sample_parent(
                rng,
                substrate_pass_bias=5.0,
                exploration_rate=exploration_rate,  # NEW Iter 13b
            )
            if parent_entry is not None:
                parent = archive.get_genome(parent_entry.content_hash)

        child = operator.mutate(parent, rng, atom_pool)
        child = Genome(
            nodes=child.nodes,
            target_predicate=child.target_predicate,
            mutation_operator_class=op_name,  # type: ignore[arg-type]
            parent_hash=child.parent_hash,
            metadata=dict(child.metadata),
        )

        eval_data = evaluator._evaluate_genome(child)

        cell = compute_cell_coordinate(child, evaluation=EvaluationResult(
            output_canonicalizer_subclass=eval_data["canonicalizer_subclass"],
            output_magnitude=eval_data["magnitude"],
            canonical_form_distance_to_catalog=eval_data["canonical_form_distance"],
        ))

        cont_score = math.log10(1 + eval_data["lift"])

        fitness = FitnessTuple(
            battery_survival_count=int(eval_data["substrate_pass"]),
            band_concentration_tier=2 if cell.magnitude_bucket in (1, 2) else 1,
            continuous_signal_score=cont_score,
            cost_amortized_score=1.0,
        )

        archive.submit(child, cell, fitness)

        if eval_data["substrate_pass"]:
            substrate_passed += 1
        if eval_data["is_obstruction"]:
            obstruction_hits.append(ep)
        if eval_data["is_secondary"]:
            secondary_hits.append(ep)
        if eval_data.get("is_obstruction_discriminator"):
            obstruction_discriminator_hits.append((ep, eval_data["predicate"]))
        if eval_data.get("is_secondary_discriminator"):
            secondary_discriminator_hits.append((ep, eval_data["predicate"]))
        if eval_data["lift"] >= 5.0 and eval_data["match_group_size"] >= 3:
            high_lift_predicates.append({
                "episode": ep,
                "lift": eval_data["lift"],
                "match_size": eval_data["match_group_size"],
                "predicate": eval_data["predicate"],
                "operator": op_name,
            })

    elapsed = time.time() - t_start
    fill_counts = archive.operator_fill_count()

    first_obstruction = obstruction_hits[0] if obstruction_hits else None
    first_secondary = secondary_hits[0] if secondary_hits else None

    return {
        "seed": seed,
        "n_episodes": n_episodes,
        "exploration_rate": exploration_rate,
        "elapsed_s": elapsed,
        "archive_n_cells": archive.n_cells_filled(),
        "fill_counts": fill_counts,
        "obstruction_hits": len(obstruction_hits),
        "secondary_hits": len(secondary_hits),
        "obstruction_discriminator_hits": len(obstruction_discriminator_hits),
        "secondary_discriminator_hits": len(secondary_discriminator_hits),
        "first_obstruction_episode": first_obstruction,
        "first_secondary_episode": first_secondary,
        "first_obstruction_discriminator_ep": (
            obstruction_discriminator_hits[0][0]
            if obstruction_discriminator_hits else None
        ),
        "first_obstruction_discriminator_pred": (
            obstruction_discriminator_hits[0][1]
            if obstruction_discriminator_hits else None
        ),
        "first_secondary_discriminator_ep": (
            secondary_discriminator_hits[0][0]
            if secondary_discriminator_hits else None
        ),
        "first_secondary_discriminator_pred": (
            secondary_discriminator_hits[0][1]
            if secondary_discriminator_hits else None
        ),
        "substrate_passed": substrate_passed,
        "n_high_lift": len(high_lift_predicates),
        "top_high_lift": sorted(
            high_lift_predicates, key=lambda x: -x["lift"]
        )[:5],
    }


if __name__ == "__main__":
    seeds = [42, 100, 1234]
    n_episodes = 5000

    # Sweep exploration_rate to characterize the effect
    rates_to_test = [0.0, 0.15, 0.25]

    all_results: Dict[str, Any] = {}
    for rate in rates_to_test:
        print(f"\nExploration rate {rate:.2f}:")
        per_seed = []
        for seed in seeds:
            print(f"  Seed {seed}...", end=" ", flush=True)
            result = run_one_seed_with_exploration(
                seed, n_episodes=n_episodes, exploration_rate=rate
            )
            print(
                f"obs={result['obstruction_hits']} "
                f"obs_disc={result['obstruction_discriminator_hits']} "
                f"sec={result['secondary_hits']} "
                f"sec_disc={result['secondary_discriminator_hits']} "
                f"({result['elapsed_s']:.0f}s)"
            )
            per_seed.append(result)

        agg = aggregate(per_seed)
        all_results[f"rate_{rate:.2f}"] = {
            "per_seed": per_seed,
            "aggregate": agg,
        }

    out_dir = Path(__file__).parent
    (out_dir / "trial_3_iter13_results.json").write_text(
        json.dumps(all_results, indent=2, default=str), encoding="utf-8"
    )

    # Concise comparison report
    lines = [
        "=" * 72,
        f"Trial 3 Iter-13 — exploration_rate sweep at {n_episodes} episodes",
        "=" * 72,
        "",
        f"{'rate':>6} {'obs/3':>6} {'obs_disc/3':>11} {'sec/3':>6} {'sec_disc/3':>11} "
        f"{'archive':>9} {'pass_total':>11} {'struct/unif':>12}",
    ]
    for rate in rates_to_test:
        agg = all_results[f"rate_{rate:.2f}"]["aggregate"]
        lines.append(
            f"  {rate:>4.2f} "
            f"{agg['n_seeds_hit_obstruction']:>4d}/3 "
            f"{agg['n_seeds_hit_obstruction_discriminator']:>9d}/3 "
            f"{agg['n_seeds_hit_secondary']:>4d}/3 "
            f"{agg['n_seeds_hit_secondary_discriminator']:>9d}/3 "
            f"{agg['archive_size_mean']:>9.0f} "
            f"{agg['substrate_passed_total']:>11d} "
            f"{agg['structural_uniform_ratio']:>11.2f}x"
        )
    lines.append("")
    lines.append("ACCEPTANCE: rate=0.25 should give 3/3 on BOTH obstruction and secondary")
    lines.append("")

    # Per-seed for the best rate
    best_rate = 0.25
    if f"rate_{best_rate:.2f}" in all_results:
        lines.append(f"PER-SEED at rate={best_rate}")
        lines.append(
            f"  {'seed':>6} {'archive':>8} {'pass':>5} {'high-lift':>10} "
            f"{'1st-obs':>8} {'1st-sec':>8} {'1st-obs-disc':>13}"
        )
        for s in all_results[f"rate_{best_rate:.2f}"]["per_seed"]:
            lines.append(
                f"  {s['seed']:>6d} {s['archive_n_cells']:>8d} "
                f"{s['substrate_passed']:>5d} {s['n_high_lift']:>10d} "
                f"{str(s['first_obstruction_episode']):>8} "
                f"{str(s['first_secondary_episode']):>8} "
                f"{str(s['first_obstruction_discriminator_ep']):>13}"
            )

    report = "\n".join(lines)
    (out_dir / "TRIAL_3_ITER13_REPORT.md").write_text(report, encoding="utf-8")
    print()
    print(report)
