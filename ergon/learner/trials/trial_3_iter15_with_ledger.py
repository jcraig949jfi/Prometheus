"""Trial 3 iter-15 — predicate trial with promotion ledger persistence.

Per Iter 7 / Task #65. Same engine as iter 14 (BindEvalKernelV2 path) but
every substrate-PASS event is recorded to a PromotionLedger JSONL file.
This is the artifact that makes Ergon's discoveries visible to other
agents (Charon, Aporia, Harmonia).

Acceptance:
  - 1K x 3 seeds complete without error
  - Ledger contains >= 100 substrate-PASS records (well below ~700/seed seen
    in iter 14, so a low bar — we want to validate persistence works)
  - Reading the ledger back via load_jsonl preserves all records
  - unique_predicates() finds at least 5 distinct predicates
"""
from __future__ import annotations

import json
import math
import random
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

from prometheus_math._obstruction_corpus import (
    OBSTRUCTION_CORPUS,
    OBSTRUCTION_SIGNATURE,
    SECONDARY_SIGNATURE,
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
from ergon.learner.promotion_ledger import PromotionLedger
from ergon.learner.scheduler import OperatorScheduler
from ergon.learner.trials.trial_3_obstruction_smoke import make_obstruction_atom_pool


def _is_obstruction_discriminator(pred: Dict[str, Any]) -> bool:
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


def run_one_seed_with_ledger(
    seed: int,
    n_episodes: int,
    ledger: PromotionLedger,
    kernel_binding_name: str,
) -> Dict[str, Any]:
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

        kernel_result = evaluator._get_or_evaluate(child)
        n_kernel_evals += 1
        if not kernel_result.success:
            n_kernel_eval_errors += 1

        obs_data = evaluator.evaluate_obstruction(child)
        lift = obs_data.get("obstruction_lift", 0.0)
        match_size = obs_data.get("obstruction_match_size", 0)
        pred = obs_data.get("obstruction_predicate", {})
        passes = obs_data.get("substrate_pass", False)

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

        # Record substrate-PASS events to the ledger
        if passes:
            substrate_passed += 1
            ledger.append(
                seed=seed,
                episode=ep,
                genome_content_hash=child.content_hash(),
                operator_class=op_name,
                predicate=pred,
                lift=lift,
                match_size=match_size,
                kernel_binding_name=kernel_binding_name,
                is_obstruction_exact=(pred == OBSTRUCTION_SIGNATURE),
                is_secondary_exact=(pred == SECONDARY_SIGNATURE),
                is_obstruction_discriminator=_is_obstruction_discriminator(pred),
                is_secondary_discriminator=_is_secondary_discriminator(pred),
            )

    elapsed = time.time() - t_start
    return {
        "seed": seed,
        "n_episodes": n_episodes,
        "elapsed_s": elapsed,
        "substrate_passed": substrate_passed,
        "archive_n_cells": archive.n_cells_filled(),
        "n_kernel_evals": n_kernel_evals,
        "n_kernel_eval_errors": n_kernel_eval_errors,
    }


if __name__ == "__main__":
    out_dir = Path(__file__).parent
    ledger_path = out_dir / "ledgers" / "trial_3_iter15_promotion_ledger.jsonl"
    # Truncate ledger file before run (for reproducibility)
    if ledger_path.exists():
        ledger_path.unlink()
    ledger = PromotionLedger(path=ledger_path, trial_name="trial_3_iter15")

    seeds = [42, 100, 1234]
    n_episodes = 1000
    kernel_binding_name = "ergon_execute_obstruction_genome"

    print(f"Trial 3 iter-15: {n_episodes} x {len(seeds)} seeds with ledger persistence...")
    per_seed = []
    for seed in seeds:
        print(f"  Seed {seed}...", end=" ", flush=True)
        result = run_one_seed_with_ledger(
            seed, n_episodes, ledger, kernel_binding_name
        )
        print(
            f"pass={result['substrate_passed']} "
            f"archive={result['archive_n_cells']} "
            f"errs={result['n_kernel_eval_errors']} "
            f"({result['elapsed_s']:.1f}s)"
        )
        per_seed.append(result)

    counts = ledger.n_promoted_by_class()
    unique = ledger.unique_predicates()

    print()
    print("=" * 72)
    print("Trial 3 Iter-15 — promotion ledger results")
    print("=" * 72)
    print()
    print("ACCEPTANCE")
    print(f"  [Completed without error]:           PASS")
    print(f"  [Ledger >= 100 records]:             "
          f"{'PASS' if ledger.n_records() >= 100 else 'FAIL'} "
          f"({ledger.n_records()})")
    print(f"  [Round-trip via load_jsonl]:         ", end="")
    reload = PromotionLedger.load_jsonl(ledger_path)
    if reload.n_records() == ledger.n_records():
        print(f"PASS ({reload.n_records()})")
    else:
        print(f"FAIL ({reload.n_records()} != {ledger.n_records()})")
    print(f"  [unique_predicates >= 5]:            "
          f"{'PASS' if len(unique) >= 5 else 'FAIL'} ({len(unique)})")
    print()
    print(f"PROMOTION CLASSIFICATION")
    for k, v in counts.items():
        print(f"  {k:>40s}: {v:>5d}")
    print()
    print(f"Ledger written to: {ledger_path}")
    print(f"Total records: {ledger.n_records()}")
    print(f"Unique predicates: {len(unique)}")
    print()

    # Show top-5 most-frequent unique predicates
    top5 = sorted(unique, key=lambda u: -u["n_occurrences"])[:5]
    print("TOP-5 MOST-FREQUENT UNIQUE PREDICATES")
    for u in top5:
        print(
            f"  n_occ={u['n_occurrences']:>3d} lift={u['lift']:>6.2f} "
            f"m={u['match_size']:>2d}  {u['predicate']}"
        )

    # Save summary alongside ledger
    summary_path = out_dir / "TRIAL_3_ITER15_LEDGER_REPORT.md"
    summary_path.write_text(
        "# Trial 3 Iter-15 — Promotion Ledger Report\n\n"
        f"- Total substrate-PASS records: {ledger.n_records()}\n"
        f"- Unique predicates: {len(unique)}\n"
        f"- Classification: {counts}\n\n"
        "## Top-5 most-frequent predicates\n\n"
        + "\n".join(
            f"- n_occ={u['n_occurrences']}, lift={u['lift']:.2f}, "
            f"match={u['match_size']}, predicate={u['predicate']}"
            for u in top5
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\nSummary: {summary_path}")
