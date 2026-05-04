"""Trial 3 iter-27 — uniform=30% on OBSTRUCTION (2-target) corpus.

Per Iter 26 finding: uniform=30% achieves 9/9 coverage on the 3-target
synthetic corpus. This trial tests whether the new weight choice also
performs at-or-above iter 18's uniform=5% baseline on the OBSTRUCTION
(2-target) corpus.

If yes: uniform=30% is a substrate-grade default — strictly improved.
If no: weight choice is corpus-dependent (trade-off).

Reuses iter 18's canonical pipeline (BindEvalKernelV2 routing + ledger
persistence) but with bumped uniform weight.

Acceptance: 2/3 OBS exact + 3/3 SEC exact (matching iter 18's numbers)
at uniform=30%.
"""
from __future__ import annotations

import json
import math
import random
import time
from pathlib import Path
from typing import Any, Dict, List

from prometheus_math._obstruction_corpus import (
    OBSTRUCTION_CORPUS, OBSTRUCTION_SIGNATURE, SECONDARY_SIGNATURE,
)

from ergon.learner.archive import FitnessTuple, MAPElitesArchive
from ergon.learner.descriptor import EvaluationResult, compute_cell_coordinate
from ergon.learner.genome import Genome
from ergon.learner.genome_evaluator import ObstructionBindEvalEvaluator
from ergon.learner.operators.anti_prior import AntiPriorOperator
from ergon.learner.operators.predicate_symbolic import PredicateSymbolicOperator
from ergon.learner.operators.structural import StructuralOperator
from ergon.learner.operators.uniform import UniformOperator
from ergon.learner.promotion_ledger import PromotionLedger
from ergon.learner.scheduler import OperatorScheduler
from ergon.learner.trials.trial_3_iter15_with_ledger import (
    _is_obstruction_discriminator, _is_secondary_discriminator,
)
from ergon.learner.trials.trial_3_obstruction_smoke import make_obstruction_atom_pool


def run_one_seed(
    seed: int, n_episodes: int, weights: Dict[str, float],
    ledger: PromotionLedger, kernel_binding_name: str,
    exploration_rate: float = 0.15,
) -> Dict[str, Any]:
    atom_pool = make_obstruction_atom_pool()
    evaluator = ObstructionBindEvalEvaluator(promote_rate=0.001)
    archive = MAPElitesArchive()
    rng = random.Random(seed)
    scheduler = OperatorScheduler(operator_weights=weights, seed=seed)
    operators = {
        "structural": StructuralOperator(),
        "symbolic": PredicateSymbolicOperator(),
        "uniform": UniformOperator(n_atoms_distribution=(1, 4)),
        "structured_null": UniformOperator(n_atoms_distribution=(2, 4)),
        "anti_prior": AntiPriorOperator(),
    }
    obs_exact_eps: List[int] = []
    sec_exact_eps: List[int] = []
    obs_disc_eps: List[int] = []
    sec_disc_eps: List[int] = []
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
                rng, substrate_pass_bias=5.0, exploration_rate=exploration_rate,
            )
            if parent_entry is not None:
                parent = archive.get_genome(parent_entry.content_hash)
        child = operator.mutate(parent, rng, atom_pool)
        child = Genome(
            nodes=child.nodes,
            target_predicate=child.target_predicate,
            mutation_operator_class=op_name,
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
            continuous_signal_score=cont_score, cost_amortized_score=1.0,
        )
        archive.submit(child, cell, fitness)
        if passes:
            substrate_passed += 1
            is_obs = (pred == OBSTRUCTION_SIGNATURE)
            is_sec = (pred == SECONDARY_SIGNATURE)
            is_obs_disc = _is_obstruction_discriminator(pred)
            is_sec_disc = _is_secondary_discriminator(pred)
            if is_obs: obs_exact_eps.append(ep)
            if is_sec: sec_exact_eps.append(ep)
            if is_obs_disc: obs_disc_eps.append(ep)
            if is_sec_disc: sec_disc_eps.append(ep)
            ledger.append(
                seed=seed, episode=ep,
                genome_content_hash=child.content_hash(),
                operator_class=op_name, predicate=pred,
                lift=lift, match_size=match_size,
                kernel_binding_name=kernel_binding_name,
                is_obstruction_exact=is_obs, is_secondary_exact=is_sec,
                is_obstruction_discriminator=is_obs_disc,
                is_secondary_discriminator=is_sec_disc,
            )
    elapsed = time.time() - t_start
    return {
        "seed": seed, "n_episodes": n_episodes, "weights": weights,
        "elapsed_s": elapsed,
        "ms_per_episode": (elapsed / n_episodes) * 1000.0,
        "substrate_passed": substrate_passed,
        "archive_n_cells": archive.n_cells_filled(),
        "n_kernel_evals": n_kernel_evals,
        "n_kernel_eval_errors": n_kernel_eval_errors,
        "n_obstruction_exact": len(obs_exact_eps),
        "n_secondary_exact": len(sec_exact_eps),
        "n_obstruction_disc": len(obs_disc_eps),
        "n_secondary_disc": len(sec_disc_eps),
        "first_obs_exact_ep": obs_exact_eps[0] if obs_exact_eps else None,
        "first_sec_exact_ep": sec_exact_eps[0] if sec_exact_eps else None,
    }


if __name__ == "__main__":
    out_dir = Path(__file__).parent
    ledger_dir = out_dir / "ledgers"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = ledger_dir / "trial_3_iter27_uniform30_ledger.jsonl"
    if ledger_path.exists():
        ledger_path.unlink()
    ledger = PromotionLedger(path=ledger_path, trial_name="trial_3_iter27_uniform30")

    seeds = [42, 100, 1234]
    n_episodes = 5000
    kernel_binding_name = "ergon_execute_obstruction_genome"

    iter18_baseline = {  # for reference, copied from iter 18
        "structural": 0.65, "symbolic": 0.15, "uniform": 0.05,
        "structured_null": 0.05, "anti_prior": 0.10,
    }
    bumped_uniform_30 = {
        "structural": 0.40, "symbolic": 0.15, "uniform": 0.30,
        "structured_null": 0.05, "anti_prior": 0.10,
    }

    print(f"Trial 3 iter-27: uniform=30% on OBSTRUCTION (2-target) at 5K x 3 seeds")
    print(f"  Comparison: iter 18 baseline (uniform=5%) on same corpus")
    print()
    print("Running uniform=30%...")
    per_seed = []
    for seed in seeds:
        print(f"  Seed {seed}...", end=" ", flush=True)
        result = run_one_seed(
            seed, n_episodes, bumped_uniform_30, ledger, kernel_binding_name
        )
        print(
            f"obs_ex={result['n_obstruction_exact']} "
            f"obs_dc={result['n_obstruction_disc']} "
            f"sec_ex={result['n_secondary_exact']} "
            f"sec_dc={result['n_secondary_disc']} "
            f"pass={result['substrate_passed']} "
            f"({result['elapsed_s']:.1f}s)"
        )
        per_seed.append(result)

    n_obs_exact = sum(1 for s in per_seed if s["n_obstruction_exact"] > 0)
    n_obs_disc = sum(1 for s in per_seed if s["n_obstruction_disc"] > 0)
    n_sec_exact = sum(1 for s in per_seed if s["n_secondary_exact"] > 0)
    n_sec_disc = sum(1 for s in per_seed if s["n_secondary_disc"] > 0)

    out = out_dir / "trial_3_iter27_results.json"
    out.write_text(
        json.dumps({"per_seed": per_seed, "weights": bumped_uniform_30,
                    "ledger_n_records": ledger.n_records()},
                   indent=2, default=str), encoding="utf-8"
    )

    print()
    print("=" * 78)
    print("Trial 3 Iter-27 — uniform=30% on OBSTRUCTION corpus")
    print("=" * 78)
    print()
    print(f"{'metric':>30} {'iter18 (u=5%)':>15} {'iter27 (u=30%)':>16}")
    # iter 18 numbers (from existing report)
    iter18_numbers = {"obs_exact": 2, "obs_disc": 3, "sec_exact": 3, "sec_disc": 3}
    iter27_numbers = {"obs_exact": n_obs_exact, "obs_disc": n_obs_disc,
                      "sec_exact": n_sec_exact, "sec_disc": n_sec_disc}
    for k in ("obs_exact", "obs_disc", "sec_exact", "sec_disc"):
        print(f"{k+' /3 seeds':>30} {iter18_numbers[k]:>13d}/3 {iter27_numbers[k]:>14d}/3")
    print()
    print(f"  Total ledger records: {ledger.n_records()}")
    print()
    print("ACCEPTANCE")
    obs_match = n_obs_exact >= 2
    sec_match = n_sec_exact >= 3
    print(f"  [obs_exact >= 2/3 (matches iter 18)]:   {'PASS' if obs_match else 'FAIL'}")
    print(f"  [sec_exact >= 3/3 (matches iter 18)]:   {'PASS' if sec_match else 'FAIL'}")
    print()
    if obs_match and sec_match:
        print("  CONCLUSION: uniform=30% matches or exceeds iter 18 numbers on")
        print("  OBSTRUCTION corpus. Combined with iter 26's 9/9 on 3-target,")
        print("  uniform=30% is a substrate-grade weight default upgrade.")
    else:
        print("  CONCLUSION: uniform=30% trades 2-target perf for 3-target")
        print("  coverage. Weight choice is corpus-dependent.")
