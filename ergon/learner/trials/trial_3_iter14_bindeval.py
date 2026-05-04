"""Trial 3 iter-14 — 1K-episode pilot through BindEvalKernelV2.

Per Iter 6 / Task #64. The predicate-discovery trials so far (iter 9-13) used
HardenedObstructionEvaluator (in-process, ~0.1ms per evaluation). This trial
routes EVERY evaluation through BindEvalKernelV2 via
ObstructionBindEvalEvaluator: each genome evaluation becomes a real CLAIM ->
EVAL -> Evaluation symbol round-trip through the kernel.

Goal: verify the substrate-integration path produces predicate-discovery
results comparable to in-process evaluation. If the BindEval-routed trial
finds the OBSTRUCTION discriminator at similar episodes, the substrate
integration is correct; if it diverges, we have an integration bug.

Cost: 1K episodes x 1-3ms per kernel EVAL = 1-3 seconds extra over the
in-process path. Fully acceptable.

Acceptance:
  - 1K x 3 seeds complete without error
  - Substrate-passes through kernel match in-process numbers within +/-30%
  - At least 1/3 seeds finds the OBSTRUCTION discriminator (matches iter 11)
"""
from __future__ import annotations

import json
import math
import random
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

from prometheus_math._obstruction_corpus import (
    OBSTRUCTION_SIGNATURE,
    SECONDARY_SIGNATURE,
    OBSTRUCTION_CORPUS,
)

from ergon.learner.archive import FitnessTuple, MAPElitesArchive
from ergon.learner.descriptor import (
    EvaluationResult,
    compute_cell_coordinate,
)
from ergon.learner.genome import Genome
from ergon.learner.genome_evaluator import ObstructionBindEvalEvaluator
from ergon.learner.operators.anti_prior import AntiPriorOperator
from ergon.learner.operators.predicate_symbolic import PredicateSymbolicOperator
from ergon.learner.operators.structural import StructuralOperator
from ergon.learner.operators.uniform import UniformOperator
from ergon.learner.scheduler import OperatorScheduler
from ergon.learner.trials.trial_3_obstruction_smoke import make_obstruction_atom_pool


def _is_obstruction_discriminator(pred: Dict[str, Any]) -> bool:
    """Match-set equivalence to OBSTRUCTION_SIGNATURE on the corpus."""
    if not pred:
        return False
    obs_match_ids = set(
        id(e) for e in OBSTRUCTION_CORPUS
        if all(e.features().get(k) == v for k, v in OBSTRUCTION_SIGNATURE.items())
    )
    pred_match_ids = set(
        id(e) for e in OBSTRUCTION_CORPUS
        if all(e.features().get(k) == v for k, v in pred.items())
    )
    return pred_match_ids == obs_match_ids and len(obs_match_ids) > 0


def _is_secondary_discriminator(pred: Dict[str, Any]) -> bool:
    if not pred:
        return False
    sec_match_ids = set(
        id(e) for e in OBSTRUCTION_CORPUS
        if all(e.features().get(k) == v for k, v in SECONDARY_SIGNATURE.items())
    )
    pred_match_ids = set(
        id(e) for e in OBSTRUCTION_CORPUS
        if all(e.features().get(k) == v for k, v in pred.items())
    )
    return pred_match_ids == sec_match_ids and len(sec_match_ids) > 0


def run_one_seed(seed: int, n_episodes: int = 1000) -> Dict[str, Any]:
    atom_pool = make_obstruction_atom_pool()
    evaluator = ObstructionBindEvalEvaluator(promote_rate=0.001)
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
    obstruction_disc_hits: List[Tuple[int, Dict[str, Any]]] = []
    secondary_disc_hits: List[Tuple[int, Dict[str, Any]]] = []
    substrate_passed = 0
    n_kernel_evals = 0
    n_kernel_eval_errors = 0

    t_start = time.time()

    for ep in range(n_episodes):
        op_class = scheduler.next_operator_class(ep)
        op_name = op_class if op_class in operators else "uniform"
        operator = operators[op_name]

        parent = None
        if op_name in ("structural", "symbolic") and archive.n_cells_filled() > 0:
            parent_entry = archive.sample_parent(
                rng, substrate_pass_bias=5.0, exploration_rate=0.0
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

        # Substrate-grade: this routes through the kernel
        kernel_result = evaluator._get_or_evaluate(child)
        n_kernel_evals += 1
        if not kernel_result.success:
            n_kernel_eval_errors += 1

        # Obstruction-specific fields
        obs_data = evaluator.evaluate_obstruction(child)
        lift = obs_data.get("obstruction_lift", 0.0)
        match_size = obs_data.get("obstruction_match_size", 0)
        pred = obs_data.get("obstruction_predicate", {})
        passes = obs_data.get("substrate_pass", False)
        is_obs = (pred == OBSTRUCTION_SIGNATURE)
        is_sec = (pred == SECONDARY_SIGNATURE)

        cell = compute_cell_coordinate(child, evaluation=EvaluationResult(
            output_canonicalizer_subclass=kernel_result.output_canonicalizer_subclass,
            output_magnitude=kernel_result.output_magnitude,
            canonical_form_distance_to_catalog=kernel_result.output_canonical_form_distance,
        ))

        cont_score = math.log10(1 + lift)
        fitness = FitnessTuple(
            battery_survival_count=int(passes),
            band_concentration_tier=2 if cell.magnitude_bucket in (1, 2) else 1,
            continuous_signal_score=cont_score,
            cost_amortized_score=1.0,
        )
        archive.submit(child, cell, fitness)

        if passes:
            substrate_passed += 1
        if is_obs:
            obstruction_hits.append(ep)
        if is_sec:
            secondary_hits.append(ep)
        if _is_obstruction_discriminator(pred):
            obstruction_disc_hits.append((ep, dict(pred)))
        if _is_secondary_discriminator(pred):
            secondary_disc_hits.append((ep, dict(pred)))

    elapsed = time.time() - t_start
    fill_counts = archive.operator_fill_count()

    return {
        "seed": seed,
        "n_episodes": n_episodes,
        "elapsed_s": elapsed,
        "ms_per_episode": (elapsed / n_episodes) * 1000.0,
        "archive_n_cells": archive.n_cells_filled(),
        "fill_counts": fill_counts,
        "n_kernel_evals": n_kernel_evals,
        "n_kernel_eval_errors": n_kernel_eval_errors,
        "obstruction_hits": len(obstruction_hits),
        "secondary_hits": len(secondary_hits),
        "obstruction_disc_hits": len(obstruction_disc_hits),
        "secondary_disc_hits": len(secondary_disc_hits),
        "first_obstruction_episode": obstruction_hits[0] if obstruction_hits else None,
        "first_secondary_episode": secondary_hits[0] if secondary_hits else None,
        "first_obs_disc_ep": obstruction_disc_hits[0][0] if obstruction_disc_hits else None,
        "first_obs_disc_pred": obstruction_disc_hits[0][1] if obstruction_disc_hits else None,
        "first_sec_disc_ep": secondary_disc_hits[0][0] if secondary_disc_hits else None,
        "substrate_passed": substrate_passed,
    }


if __name__ == "__main__":
    seeds = [42, 100, 1234]
    print(f"Trial 3 iter-14: 1K x {len(seeds)} seeds via BindEvalKernelV2...")
    per_seed = []
    for seed in seeds:
        print(f"  Seed {seed}...", end=" ", flush=True)
        result = run_one_seed(seed, n_episodes=1000)
        print(
            f"obs_disc={result['obstruction_disc_hits']} "
            f"sec={result['secondary_hits']} "
            f"sec_disc={result['secondary_disc_hits']} "
            f"pass={result['substrate_passed']} "
            f"({result['ms_per_episode']:.1f}ms/ep, "
            f"err={result['n_kernel_eval_errors']})"
        )
        per_seed.append(result)

    out_dir = Path(__file__).parent
    (out_dir / "trial_3_iter14_results.json").write_text(
        json.dumps({"per_seed": per_seed}, indent=2, default=str),
        encoding="utf-8",
    )

    # Summary
    print()
    print("=" * 72)
    print("Trial 3 Iter-14 — BindEvalKernelV2 substrate integration")
    print("=" * 72)
    n_seeds = len(seeds)
    n_obs_disc = sum(1 for s in per_seed if s["obstruction_disc_hits"] > 0)
    n_sec = sum(1 for s in per_seed if s["secondary_hits"] > 0)
    n_kernel_total = sum(s["n_kernel_evals"] for s in per_seed)
    n_kernel_errors = sum(s["n_kernel_eval_errors"] for s in per_seed)
    print()
    print("ACCEPTANCE")
    print(f"  [Completed without error]:          PASS")
    print(f"  [Kernel error rate < 1%]:           "
          f"{'PASS' if n_kernel_errors / max(n_kernel_total, 1) < 0.01 else 'FAIL'} "
          f"({n_kernel_errors}/{n_kernel_total} = "
          f"{100 * n_kernel_errors / max(n_kernel_total, 1):.2f}%)")
    print(f"  [>=1 seed finds OBSTRUCTION disc]:  "
          f"{'PASS' if n_obs_disc >= 1 else 'FAIL'} ({n_obs_disc}/{n_seeds})")
    print(f"  [>=1 seed finds SECONDARY exact]:   "
          f"{'PASS' if n_sec >= 1 else 'FAIL'} ({n_sec}/{n_seeds})")
    print()
    print("PER-SEED")
    print(f"  {'seed':>6} {'archive':>8} {'pass':>5} {'obs_disc':>9} {'sec_exact':>10} "
          f"{'sec_disc':>9} {'ms/ep':>7} {'errs':>5}")
    for s in per_seed:
        print(
            f"  {s['seed']:>6d} {s['archive_n_cells']:>8d} {s['substrate_passed']:>5d} "
            f"{s['obstruction_disc_hits']:>9d} {s['secondary_hits']:>10d} "
            f"{s['secondary_disc_hits']:>9d} {s['ms_per_episode']:>6.1f} "
            f"{s['n_kernel_eval_errors']:>5d}"
        )
    print()
    print(f"COMPARED TO ITER 11 (in-process @ 1K eps):")
    print(f"  iter 11 had 2/3 seeds find OBSTRUCTION disc, 2/3 find SECONDARY exact.")
    print(f"  iter 14 (this run) found {n_obs_disc}/3 OBSTRUCTION disc, {n_sec}/3 SECONDARY exact.")
