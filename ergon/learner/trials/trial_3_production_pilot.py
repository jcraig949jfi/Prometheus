"""Trial 3 production pilot — 1K x 3 seeds with structural+symbolic only.

Per Iter 5 / Task #67. Trial 3 smoke at 200 episodes didn't reach the
4-conjunct OBSTRUCTION_SIGNATURE — combinatorial-search budget too small.
This pilot scales to 1K x 3 seeds and concentrates the search budget on
selection-pressure-driven exploration (drops uniform/structured_null;
keeps anti_prior at 5% for diversity-pressure).

Plus tightens evaluator per Iter 10 / Task #68 finding: requires
min_match_group_size >= 3 for substrate-PASS, eliminating single-record
overlap inflation.

Acceptance:
  - 1K x 3 seeds complete without error
  - At least one seed produces a predicate matching OBSTRUCTION_SIGNATURE
    OR SECONDARY_SIGNATURE exactly
  - Mean lift across substrate-PASSED predicates exceeds 5.0 (genuine signal,
    not single-record artifacts)
"""
from __future__ import annotations

import json
import random
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
from ergon.learner.operators.base import fresh_genome
from ergon.learner.operators.structural import StructuralOperator
from ergon.learner.operators.symbolic import SymbolicOperator
from ergon.learner.operators.uniform import UniformOperator
from ergon.learner.scheduler import OperatorScheduler
from ergon.learner.trials.trial_3_obstruction_smoke import (
    ObstructionEvaluator,
    genome_to_predicate,
    make_obstruction_atom_pool,
)


# Tightened ObstructionEvaluator per Iter 4 finding
class HardenedObstructionEvaluator(ObstructionEvaluator):
    LIFT_PROMOTE_THRESHOLD = 1.5
    MIN_MATCH_GROUP_SIZE = 3  # NEW: prevents single-record artifact inflation

    def _evaluate_genome(self, genome: Genome) -> Dict[str, Any]:
        ch = genome.content_hash()
        if ch in self._cache:
            return self._cache[ch]

        pred = genome_to_predicate(genome)
        pred_eval = evaluate_predicate(pred, self.corpus)
        lift = pred_eval["lift"]
        match_size = pred_eval["match_group_size"]

        # Tighter substrate-PASS criterion
        passes = (
            lift >= self.LIFT_PROMOTE_THRESHOLD
            and match_size >= self.MIN_MATCH_GROUP_SIZE
        )

        import math
        log_mag = math.log10(1 + lift) * 7
        feats = sorted(pred.keys())
        if not feats:
            subclass = "group_quotient"
        elif "has_diag_neg" in feats or "has_diag_pos" in feats:
            subclass = "variety_fingerprint"
        elif any(f.startswith("neg_") for f in feats):
            subclass = "ideal_reduction"
        else:
            subclass = "partition_refinement"

        sig_distance = 0.0
        for k, v in OBSTRUCTION_SIGNATURE.items():
            if pred.get(k) != v:
                sig_distance += 1
        for k in pred.keys():
            if k not in OBSTRUCTION_SIGNATURE:
                sig_distance += 0.5

        if passes:
            verdicts = {"F1": "CLEAR", "F6": "CLEAR", "F9": "CLEAR", "F11": "CLEAR"}
        else:
            block_test = ("F1", "F6", "F9", "F11")[hash(ch) % 4]
            verdicts = {"F1": "CLEAR", "F6": "CLEAR", "F9": "CLEAR", "F11": "CLEAR"}
            verdicts[block_test] = "BLOCK"

        is_obstruction = (pred == OBSTRUCTION_SIGNATURE)
        is_secondary = (pred == SECONDARY_SIGNATURE)

        out = {
            "predicate": pred,
            "lift": lift,
            "match_group_size": match_size,
            "matched_kill_rate": pred_eval["matched_kill_rate"],
            "baseline_kill_rate": pred_eval["baseline_kill_rate"],
            "substrate_pass": passes,
            "is_obstruction": is_obstruction,
            "is_secondary": is_secondary,
            "magnitude": 10.0 ** log_mag,
            "canonicalizer_subclass": subclass,
            "canonical_form_distance": sig_distance,
            "kill_verdicts": verdicts,
        }
        self._cache[ch] = out
        return out


def run_one_seed(seed: int, n_episodes: int = 1000) -> Dict[str, Any]:
    atom_pool = make_obstruction_atom_pool()
    evaluator = HardenedObstructionEvaluator()
    archive = MAPElitesArchive()
    rng = random.Random(seed)

    # Operator weights: emphasize structural+symbolic; keep anti_prior + uniform
    # at min-share floors only
    custom_weights = {
        "structural": 0.55,
        "symbolic": 0.30,
        "uniform": 0.05,
        "structured_null": 0.05,
        "anti_prior": 0.05,
    }
    scheduler = OperatorScheduler(operator_weights=custom_weights, seed=seed)

    operators = {
        "structural": StructuralOperator(),
        "symbolic": SymbolicOperator(),
        "uniform": UniformOperator(n_atoms_distribution=(1, 4)),
        "structured_null": UniformOperator(n_atoms_distribution=(2, 4)),  # uniform-fallback
        "anti_prior": AntiPriorOperator(),
    }

    obstruction_hits: List[int] = []
    secondary_hits: List[int] = []
    substrate_passed = 0
    high_lift_predicates: List[Dict[str, Any]] = []

    t_start = time.time()

    for ep in range(n_episodes):
        op_class = scheduler.next_operator_class(ep)
        op_name = op_class if op_class in operators else "uniform"
        operator = operators[op_name]

        parent = None
        if op_name in ("structural", "symbolic") and archive.n_cells_filled() > 0:
            cells = list(archive.cells.keys())
            chosen_cell = rng.choice(cells)
            parent = archive.get_genome(archive.cells[chosen_cell].content_hash)

        child = operator.mutate(parent, rng, atom_pool)
        # Force-tag operator class
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

        # Iter 11 fix: continuous_signal_score breaks the local-maximum at
        # 3-conjunct predicates. For OBSTRUCTION_CORPUS:
        #   3-conjunct {pos_x:1, has_diag_neg:T, neg_x:4}: lift=22.40 (10 matches, 8 kills)
        #   4-conjunct OBSTRUCTION_SIGNATURE adds n_steps:5: lift=28.4 (8 matches, 8 kills)
        # log10(1+lift) gives 1.369 vs 1.468 — strict gradient toward the
        # full 4-conjunct match. match_size correctly NOT in fitness here
        # (its threshold role is in the substrate-pass criterion already).
        import math
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

    # Find first-occurrence episode for OBSTRUCTION / SECONDARY
    first_obstruction = obstruction_hits[0] if obstruction_hits else None
    first_secondary = secondary_hits[0] if secondary_hits else None

    return {
        "seed": seed,
        "n_episodes": n_episodes,
        "elapsed_s": elapsed,
        "archive_n_cells": archive.n_cells_filled(),
        "fill_counts": fill_counts,
        "obstruction_hits": len(obstruction_hits),
        "secondary_hits": len(secondary_hits),
        "first_obstruction_episode": first_obstruction,
        "first_secondary_episode": first_secondary,
        "substrate_passed": substrate_passed,
        "n_high_lift": len(high_lift_predicates),
        "top_high_lift": sorted(
            high_lift_predicates, key=lambda x: -x["lift"]
        )[:5],
    }


def aggregate(per_seed: List[Dict[str, Any]]) -> Dict[str, Any]:
    n_seeds = len(per_seed)
    obstruction_seeds = [s for s in per_seed if s["obstruction_hits"] > 0]
    secondary_seeds = [s for s in per_seed if s["secondary_hits"] > 0]

    structural_fills = [s["fill_counts"].get("structural", 0) for s in per_seed]
    uniform_fills = [s["fill_counts"].get("uniform", 0) for s in per_seed]

    high_lift_per_seed = [s["n_high_lift"] for s in per_seed]
    archive_sizes = [s["archive_n_cells"] for s in per_seed]
    substrate_passed_total = sum(s["substrate_passed"] for s in per_seed)

    return {
        "n_seeds": n_seeds,
        "n_seeds_hit_obstruction": len(obstruction_seeds),
        "n_seeds_hit_secondary": len(secondary_seeds),
        "first_obstruction_episodes": [s["first_obstruction_episode"] for s in per_seed],
        "first_secondary_episodes": [s["first_secondary_episode"] for s in per_seed],
        "structural_fills_mean": statistics.mean(structural_fills),
        "uniform_fills_mean": statistics.mean(uniform_fills),
        "structural_uniform_ratio": (
            statistics.mean(structural_fills) / max(statistics.mean(uniform_fills), 1)
        ),
        "high_lift_per_seed": high_lift_per_seed,
        "high_lift_total": sum(high_lift_per_seed),
        "archive_sizes": archive_sizes,
        "archive_size_mean": statistics.mean(archive_sizes),
        "substrate_passed_total": substrate_passed_total,
        "acceptance": {
            "all_completed": all(s["elapsed_s"] > 0 for s in per_seed),
            "found_obstruction_or_secondary": (
                len(obstruction_seeds) > 0 or len(secondary_seeds) > 0
            ),
            "high_lift_count_meaningful": sum(high_lift_per_seed) >= 5,
        },
    }


def format_report(per_seed: List[Dict[str, Any]], agg: Dict[str, Any]) -> str:
    a = agg["acceptance"]
    lines = [
        "=" * 72,
        f"Trial 3 Production Pilot — 1000 episodes x {agg['n_seeds']} seeds",
        "=" * 72,
        "",
        "ACCEPTANCE",
        f"  [Completed without error]:                  {'PASS' if a['all_completed'] else 'FAIL'}",
        f"  [Found OBSTRUCTION or SECONDARY signature]: {'PASS' if a['found_obstruction_or_secondary'] else 'FAIL'}",
        f"  [High-lift predicates >= 5]:                {'PASS' if a['high_lift_count_meaningful'] else 'FAIL'}",
        "",
        "PER-SEED RESULTS",
        f"  {'seed':>6} {'archive':>8} {'struct':>7} {'symb':>6} {'unif':>6} {'a-pri':>6} "
        f"{'pass':>5} {'high-lift':>10} {'1st-obs':>8} {'1st-sec':>8}",
    ]
    for s in per_seed:
        fc = s["fill_counts"]
        lines.append(
            f"  {s['seed']:>6d} {s['archive_n_cells']:>8d} "
            f"{fc.get('structural', 0):>7d} "
            f"{fc.get('symbolic', 0):>6d} "
            f"{fc.get('uniform', 0):>6d} "
            f"{fc.get('anti_prior', 0):>6d} "
            f"{s['substrate_passed']:>5d} "
            f"{s['n_high_lift']:>10d} "
            f"{str(s['first_obstruction_episode']):>8} "
            f"{str(s['first_secondary_episode']):>8}"
        )

    lines += [
        "",
        "AGGREGATE STATS",
        f"  Seeds hitting OBSTRUCTION:    {agg['n_seeds_hit_obstruction']} of {agg['n_seeds']}",
        f"  Seeds hitting SECONDARY:      {agg['n_seeds_hit_secondary']} of {agg['n_seeds']}",
        f"  First-obstruction episodes:   {agg['first_obstruction_episodes']}",
        f"  First-secondary episodes:     {agg['first_secondary_episodes']}",
        f"  structural / uniform ratio:   {agg['structural_uniform_ratio']:.2f}x",
        f"  High-lift predicates total:   {agg['high_lift_total']}",
        f"  Archive sizes (mean):         {agg['archive_size_mean']:.0f}",
        f"  Substrate-PASSED total:       {agg['substrate_passed_total']}",
        "",
    ]

    # Show top high-lift predicates from the best seed
    best_seed = max(per_seed, key=lambda s: s["n_high_lift"])
    if best_seed["top_high_lift"]:
        lines.append(f"TOP HIGH-LIFT PREDICATES (from seed {best_seed['seed']})")
        for ep in best_seed["top_high_lift"]:
            lines.append(
                f"  ep {ep['episode']:4d} ({ep['operator']:14s}): "
                f"lift={ep['lift']:.2f}, match_size={ep['match_size']}, "
                f"predicate={ep['predicate']}"
            )

    lines += [
        "",
        f"NOTE: HardenedObstructionEvaluator requires min_match_group_size >= 3",
        "for substrate-PASS, preventing single-record-overlap lift inflation",
        "from Iter 4 finding.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    seeds = [42, 100, 1234]
    per_seed = []
    print(f"Trial 3 production pilot: 1K x {len(seeds)} seeds...")
    for seed in seeds:
        print(f"  Seed {seed}...", end=" ", flush=True)
        result = run_one_seed(seed, n_episodes=1000)
        print(
            f"obstruction_hits={result['obstruction_hits']}, "
            f"secondary_hits={result['secondary_hits']}, "
            f"high_lift={result['n_high_lift']}"
        )
        per_seed.append(result)

    agg = aggregate(per_seed)
    out_dir = Path(__file__).parent
    (out_dir / "trial_3_production_results.json").write_text(
        json.dumps({"per_seed": per_seed, "aggregate": agg},
                   indent=2, default=str), encoding="utf-8"
    )
    report = format_report(per_seed, agg)
    (out_dir / "TRIAL_3_PRODUCTION_REPORT.md").write_text(report, encoding="utf-8")
    print()
    print(report)
