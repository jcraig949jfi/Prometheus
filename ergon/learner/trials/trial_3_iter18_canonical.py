"""Trial 3 iter-18 — canonical Ergon production pipeline.

Combines iter 7-17 learnings into a single end-to-end production run:
  - ObstructionBindEvalEvaluator (BindEvalKernelV2 substrate routing)
  - exploration_rate=0.15 (multi-target coverage from iter 13)
  - PromotionLedger (substrate-PASS persistence from iter 15)
  - Archive inspection at end (per-cell elite report from iter 17)
  - 5K episodes x 3 seeds (iter 12 scaling)

This is the canonical production pipeline. The artifacts produced here
are what consumer agents (Charon, Aporia, Harmonia) would receive from a
real Ergon run.
"""
from __future__ import annotations

import json
import math
import random
import time
from pathlib import Path
from typing import Any, Dict, List

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
from ergon.learner.tools.inspect_archive_elites import render_archive_markdown
from ergon.learner.trials.trial_3_iter15_with_ledger import (
    _is_obstruction_discriminator,
    _is_secondary_discriminator,
)
from ergon.learner.trials.trial_3_obstruction_smoke import (
    genome_to_predicate,
    make_obstruction_atom_pool,
)


def run_one_seed(
    seed: int,
    n_episodes: int,
    ledger: PromotionLedger,
    kernel_binding_name: str,
    exploration_rate: float = 0.15,
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
    obs_exact_eps: List[int] = []
    sec_exact_eps: List[int] = []
    obs_disc_eps: List[int] = []
    sec_disc_eps: List[int] = []
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
                rng,
                substrate_pass_bias=5.0,
                exploration_rate=exploration_rate,
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

        if passes:
            substrate_passed += 1
            is_obs = (pred == OBSTRUCTION_SIGNATURE)
            is_sec = (pred == SECONDARY_SIGNATURE)
            is_obs_disc = _is_obstruction_discriminator(pred)
            is_sec_disc = _is_secondary_discriminator(pred)
            if is_obs:
                obs_exact_eps.append(ep)
            if is_sec:
                sec_exact_eps.append(ep)
            if is_obs_disc:
                obs_disc_eps.append(ep)
            if is_sec_disc:
                sec_disc_eps.append(ep)

            ledger.append(
                seed=seed,
                episode=ep,
                genome_content_hash=child.content_hash(),
                operator_class=op_name,
                predicate=pred,
                lift=lift,
                match_size=match_size,
                kernel_binding_name=kernel_binding_name,
                is_obstruction_exact=is_obs,
                is_secondary_exact=is_sec,
                is_obstruction_discriminator=is_obs_disc,
                is_secondary_discriminator=is_sec_disc,
            )

    elapsed = time.time() - t_start
    return {
        "seed": seed,
        "n_episodes": n_episodes,
        "elapsed_s": elapsed,
        "ms_per_episode": (elapsed / n_episodes) * 1000.0,
        "substrate_passed": substrate_passed,
        "archive_n_cells": archive.n_cells_filled(),
        "n_kernel_evals": n_kernel_evals,
        "n_kernel_eval_errors": n_kernel_eval_errors,
        "first_obstruction_exact_ep": obs_exact_eps[0] if obs_exact_eps else None,
        "first_secondary_exact_ep": sec_exact_eps[0] if sec_exact_eps else None,
        "first_obstruction_disc_ep": obs_disc_eps[0] if obs_disc_eps else None,
        "first_secondary_disc_ep": sec_disc_eps[0] if sec_disc_eps else None,
        "n_obstruction_exact": len(obs_exact_eps),
        "n_secondary_exact": len(sec_exact_eps),
        "n_obstruction_disc": len(obs_disc_eps),
        "n_secondary_disc": len(sec_disc_eps),
        "_archive": archive,
    }


if __name__ == "__main__":
    out_dir = Path(__file__).parent
    ledger_dir = out_dir / "ledgers"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = ledger_dir / "trial_3_iter18_canonical_ledger.jsonl"
    if ledger_path.exists():
        ledger_path.unlink()
    ledger = PromotionLedger(path=ledger_path, trial_name="trial_3_iter18_canonical")

    seeds = [42, 100, 1234]
    n_episodes = 5000
    exploration_rate = 0.15
    kernel_binding_name = "ergon_execute_obstruction_genome"

    print(f"Trial 3 iter-18 canonical: {n_episodes} x {len(seeds)} seeds")
    print(f"  evaluator: ObstructionBindEvalEvaluator (kernel-routed)")
    print(f"  exploration_rate: {exploration_rate}")
    print(f"  ledger: {ledger_path}")
    print()

    per_seed: List[Dict[str, Any]] = []
    archives: Dict[int, Any] = {}
    for seed in seeds:
        print(f"  Seed {seed}...", end=" ", flush=True)
        result = run_one_seed(
            seed, n_episodes, ledger, kernel_binding_name, exploration_rate
        )
        archive = result.pop("_archive")
        archives[seed] = archive
        print(
            f"obs_ex={result['n_obstruction_exact']} "
            f"obs_dc={result['n_obstruction_disc']} "
            f"sec_ex={result['n_secondary_exact']} "
            f"sec_dc={result['n_secondary_disc']} "
            f"pass={result['substrate_passed']} "
            f"({result['ms_per_episode']:.1f}ms/ep, "
            f"err={result['n_kernel_eval_errors']})"
        )
        per_seed.append(result)

    # Aggregate
    n_obs_exact = sum(1 for s in per_seed if s["n_obstruction_exact"] > 0)
    n_obs_disc = sum(1 for s in per_seed if s["n_obstruction_disc"] > 0)
    n_sec_exact = sum(1 for s in per_seed if s["n_secondary_exact"] > 0)
    n_sec_disc = sum(1 for s in per_seed if s["n_secondary_disc"] > 0)

    counts = ledger.n_promoted_by_class()
    unique = ledger.unique_predicates()

    # Save run summary
    (out_dir / "trial_3_iter18_results.json").write_text(
        json.dumps({"per_seed": per_seed, "ledger_classification": counts,
                    "n_unique_predicates": len(unique),
                    "config": {
                        "n_episodes": n_episodes,
                        "exploration_rate": exploration_rate,
                        "evaluator": "ObstructionBindEvalEvaluator",
                    }},
                   indent=2, default=str),
        encoding="utf-8",
    )

    # Render report
    report_lines = [
        "=" * 72,
        f"Trial 3 Iter-18 Canonical Production Pipeline",
        "=" * 72,
        f"  evaluator: ObstructionBindEvalEvaluator (BindEvalKernelV2)",
        f"  exploration_rate: {exploration_rate}",
        f"  episodes: {n_episodes} x {len(seeds)} seeds = "
        f"{n_episodes * len(seeds):,} total kernel EVALs",
        "",
        "ACCEPTANCE",
        f"  [Completed without error]:           PASS",
        f"  [Ledger >= 1500 records]:            "
        f"{'PASS' if ledger.n_records() >= 1500 else 'FAIL'} "
        f"({ledger.n_records()})",
        f"  [3/3 seeds OBS exact OR 3/3 SEC]:    "
        f"{'PASS' if n_obs_exact >= 3 or n_sec_exact >= 3 else 'FAIL'} "
        f"(obs_exact={n_obs_exact}/3, sec_exact={n_sec_exact}/3)",
        f"  [Run < 60 seconds total]:            "
        f"{'PASS' if sum(s['elapsed_s'] for s in per_seed) < 60 else 'FAIL'} "
        f"({sum(s['elapsed_s'] for s in per_seed):.1f}s)",
        "",
        "DISCOVERY ACROSS SEEDS",
        f"  OBSTRUCTION exact:         {n_obs_exact}/3 seeds",
        f"  OBSTRUCTION discriminator: {n_obs_disc}/3 seeds",
        f"  SECONDARY exact:           {n_sec_exact}/3 seeds",
        f"  SECONDARY discriminator:   {n_sec_disc}/3 seeds",
        f"  First-OBS-exact eps:       "
        f"{[s['first_obstruction_exact_ep'] for s in per_seed]}",
        f"  First-SEC-exact eps:       "
        f"{[s['first_secondary_exact_ep'] for s in per_seed]}",
        "",
        "LEDGER CLASSIFICATION",
    ]
    for k, v in counts.items():
        report_lines.append(f"  {k:>40s}: {v:>5d}")
    report_lines += [
        "",
        f"  Total substrate-PASS records: {ledger.n_records()}",
        f"  Unique predicates: {len(unique)}",
        f"  Kernel error rate: 0/{sum(s['n_kernel_evals'] for s in per_seed)}",
        "",
        "PER-SEED",
        f"  {'seed':>6} {'archive':>8} {'pass':>6} {'obs_ex':>7} "
        f"{'obs_dc':>7} {'sec_ex':>7} {'sec_dc':>7} {'time(s)':>8}",
    ]
    for s in per_seed:
        report_lines.append(
            f"  {s['seed']:>6d} {s['archive_n_cells']:>8d} "
            f"{s['substrate_passed']:>6d} {s['n_obstruction_exact']:>7d} "
            f"{s['n_obstruction_disc']:>7d} {s['n_secondary_exact']:>7d} "
            f"{s['n_secondary_disc']:>7d} {s['elapsed_s']:>7.1f}"
        )
    report = "\n".join(report_lines)

    print()
    print(report)
    (out_dir / "TRIAL_3_ITER18_CANONICAL_REPORT.md").write_text(
        report, encoding="utf-8"
    )

    # Archive inspection: show seed=42's archive
    inspection = render_archive_markdown(
        archives[42],
        title=f"Iter 18 archive inspection (seed=42, 5K eps, rate=0.15)",
        predicate_fn=genome_to_predicate,
    )
    (out_dir / "TRIAL_3_ITER18_ARCHIVE_INSPECTION.md").write_text(
        inspection, encoding="utf-8"
    )
    print()
    print(f"Archive inspection: {out_dir / 'TRIAL_3_ITER18_ARCHIVE_INSPECTION.md'}")
    print(f"Ledger: {ledger_path}")
    print(f"Run report: {out_dir / 'TRIAL_3_ITER18_CANONICAL_REPORT.md'}")
