"""Trial 3 ObstructionEnv smoke test — cross-domain replication.

Per Iteration 3 of MVP build (queued from Iter 2's BindEvalKernelV2
success). Charon's ObstructionEnv (commit d339dc45) is a synthetic-but-
genuinely-open OBSTRUCTION_SHAPE pattern detection problem. The task:
discover a conjunctive predicate over OEIS-shaped feature vectors
(n_steps, neg_x, has_diag_neg, etc.) whose held-out predictive lift
matches the planted A149* signature.

This integration redefines the genome's atoms as predicate-conjuncts
rather than arsenal callables. A genome's nodes encode `(feature, value)`
pairs; the genome interpretation conjuncts them into a predicate dict;
the evaluator scores the predicate's lift on the synthetic corpus.

Goal: prove the engine architecture is domain-agnostic — same scheduler,
same MAP-Elites archive, same trivial-pattern detector — but a
different atom-pool + evaluator yields signal in a different problem
class.

Acceptance:
  - 100 episodes complete without error
  - At least one episode produces a predicate matching OBSTRUCTION_SIGNATURE
    (= {n_steps: 5, neg_x: 4, has_diag_neg: True}) — the planted target
  - structural-class fills > uniform-class fills (selection pressure works
    in this domain too)
"""
from __future__ import annotations

import json
import random
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import obstruction_env primitives
from prometheus_math.obstruction_env import (
    OBSTRUCTION_CORPUS,
    OBSTRUCTION_SIGNATURE,
    SECONDARY_SIGNATURE,
    evaluate_predicate,
)

from ergon.learner.archive import FitnessTuple, MAPElitesArchive
from ergon.learner.descriptor import (
    CellCoordinate,
    EvaluationResult,
    compute_cell_coordinate,
)
from ergon.learner.genome import Genome, NodeRef
from ergon.learner.operators.structural import StructuralOperator
from ergon.learner.operators.symbolic import SymbolicOperator
from ergon.learner.operators.uniform import UniformOperator
from ergon.learner.scheduler import OperatorScheduler


# ---------------------------------------------------------------------------
# Obstruction atom pool — feature/value conjuncts as atoms
# ---------------------------------------------------------------------------


def make_obstruction_atom_pool() -> Dict[str, Dict[str, Any]]:
    """Atom pool for predicate-discovery genomes.

    Each atom is callable_ref of form 'predicate:<feature>=<value>'.
    Args are unused (the atom IS the conjunct). Genomes consist of
    multiple such atoms; the genome's interpretation conjuncts them
    into a predicate dict.
    """
    pool = {}
    NUMERIC_FEATURES = ("n_steps", "neg_x", "pos_x", "neg_y", "pos_y", "neg_z", "pos_z")
    BOOL_FEATURES = ("has_diag_neg", "has_diag_pos")

    # Numeric features: values 0-7
    for feat in NUMERIC_FEATURES:
        for v in range(8):
            cref = f"predicate:{feat}={v}"
            pool[cref] = {
                "arity": 0, "arg_types": (), "return_type": "predicate_conjunct",
                "cost_tier": 1, "arg_samplers": (),
            }

    # Bool features: True/False
    for feat in BOOL_FEATURES:
        for v in (False, True):
            cref = f"predicate:{feat}={v}"
            pool[cref] = {
                "arity": 0, "arg_types": (), "return_type": "predicate_conjunct",
                "cost_tier": 1, "arg_samplers": (),
            }
    return pool


def genome_to_predicate(genome: Genome) -> Dict[str, Any]:
    """Interpret a genome's atoms as a conjunctive predicate.

    Each node's callable_ref of form 'predicate:<feature>=<value>' becomes
    a {feature: value} entry. If the same feature appears multiple times,
    the LAST occurrence wins (consistent with how ObstructionEnv applies
    its action sequence).
    """
    pred: Dict[str, Any] = {}
    for node in genome.nodes:
        cref = node.callable_ref
        if not cref.startswith("predicate:"):
            continue
        body = cref[len("predicate:"):]
        if "=" not in body:
            continue
        feat, val_str = body.split("=", 1)
        # Parse value
        if val_str == "True":
            val: Any = True
        elif val_str == "False":
            val = False
        else:
            try:
                val = int(val_str)
            except ValueError:
                val = val_str
        pred[feat] = val
    return pred


# ---------------------------------------------------------------------------
# ObstructionEvaluator — wraps evaluate_predicate as engine evaluator
# ---------------------------------------------------------------------------


class ObstructionEvaluator:
    """Evaluator that scores genomes via predicate lift on the synthetic corpus."""

    LIFT_PROMOTE_THRESHOLD = 1.5  # lift >= 1.5 → substrate-PASS

    def __init__(self, corpus=None):
        self.corpus = corpus if corpus is not None else OBSTRUCTION_CORPUS
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _evaluate_genome(self, genome: Genome) -> Dict[str, Any]:
        ch = genome.content_hash()
        if ch in self._cache:
            return self._cache[ch]

        pred = genome_to_predicate(genome)
        pred_eval = evaluate_predicate(pred, self.corpus)

        lift = pred_eval["lift"]
        # Substrate-PASS if lift >= threshold AND match-group non-trivial
        passes = (
            lift >= self.LIFT_PROMOTE_THRESHOLD
            and pred_eval["match_group_size"] >= 2
        )

        # Magnitude: scale the lift into log-magnitude for the descriptor
        # axis 4. Lift 1.0 → log_mag 0; lift 50 → log_mag ~1.7. Use
        # log10(1 + lift) for safety on lift=0 cases.
        import math
        log_mag = math.log10(1 + lift) * 7  # scaled for descriptor diversity

        # Canonicalizer subclass — derived from which features the predicate uses
        feats = sorted(pred.keys())
        if not feats:
            subclass = "group_quotient"
        elif "has_diag_neg" in feats or "has_diag_pos" in feats:
            subclass = "variety_fingerprint"
        elif any(f.startswith("neg_") for f in feats):
            subclass = "ideal_reduction"
        else:
            subclass = "partition_refinement"

        # Distance to OBSTRUCTION_SIGNATURE: count of feature mismatches
        sig_distance = 0.0
        for k, v in OBSTRUCTION_SIGNATURE.items():
            if pred.get(k) != v:
                sig_distance += 1
        # Plus extra features in pred not in signature
        for k in pred.keys():
            if k not in OBSTRUCTION_SIGNATURE:
                sig_distance += 0.5

        # Kill verdicts
        if passes:
            verdicts = {"F1": "CLEAR", "F6": "CLEAR", "F9": "CLEAR", "F11": "CLEAR"}
        else:
            # Pick a random kill-test to be the BLOCK reason
            block_test = ("F1", "F6", "F9", "F11")[hash(ch) % 4]
            verdicts = {"F1": "CLEAR", "F6": "CLEAR", "F9": "CLEAR", "F11": "CLEAR"}
            verdicts[block_test] = "BLOCK"

        # Bonus check: did we hit the planted obstruction signature exactly?
        is_obstruction = (pred == OBSTRUCTION_SIGNATURE)
        is_secondary = (pred == SECONDARY_SIGNATURE)

        out = {
            "predicate": pred,
            "lift": lift,
            "match_group_size": pred_eval["match_group_size"],
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

    # Engine duck-typed interface
    def evaluate(self, genome: Genome) -> Dict[str, str]:
        return self._evaluate_genome(genome)["kill_verdicts"]

    def evaluate_magnitude(self, genome: Genome) -> float:
        return self._evaluate_genome(genome)["magnitude"]

    def evaluate_canonicalizer_subclass(self, genome: Genome) -> str:
        return self._evaluate_genome(genome)["canonicalizer_subclass"]

    def evaluate_canonical_form_distance(self, genome: Genome) -> float:
        return self._evaluate_genome(genome)["canonical_form_distance"]


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------


def run_smoke_test(n_episodes: int = 100, seed: int = 42) -> Dict[str, Any]:
    """Run a small predicate-discovery pilot."""
    print(f"=== Trial 3 ObstructionEnv smoke test: n={n_episodes}, seed={seed} ===")

    atom_pool = make_obstruction_atom_pool()
    evaluator = ObstructionEvaluator()
    archive = MAPElitesArchive()
    rng = random.Random(seed)
    scheduler = OperatorScheduler(seed=seed)

    operators = {
        "structural": StructuralOperator(),
        "symbolic": SymbolicOperator(),
        "uniform": UniformOperator(n_atoms_distribution=(1, 4)),
    }

    obstructions_found = []
    secondaries_found = []
    high_lift_episodes = []
    substrate_passed = 0

    t_start = time.time()

    # Build some seed genomes for parent sampling
    from ergon.learner.operators.base import fresh_genome

    for episode_idx in range(n_episodes):
        op_class = scheduler.next_operator_class(episode_idx)
        # Map operator class to one of the 3 we instantiated; default to uniform
        op_name = op_class if op_class in operators else "uniform"
        operator = operators[op_name]

        # Sample parent
        parent = None
        if op_name in ("structural", "symbolic") and archive.n_cells_filled() > 0:
            cells = list(archive.cells.keys())
            chosen = rng.choice(cells)
            parent = archive.get_genome(archive.cells[chosen].content_hash)

        # Mutate
        child = operator.mutate(parent, rng, atom_pool)
        # Force-tag the operator class in case operator-class default doesn't match
        child = Genome(
            nodes=child.nodes,
            target_predicate=child.target_predicate,
            mutation_operator_class=op_name,  # type: ignore[arg-type]
            parent_hash=child.parent_hash,
            metadata=dict(child.metadata),
        )

        # Evaluate
        eval_data = evaluator._evaluate_genome(child)

        # Compute cell coordinate
        cell = compute_cell_coordinate(child, evaluation=EvaluationResult(
            output_canonicalizer_subclass=eval_data["canonicalizer_subclass"],
            output_magnitude=eval_data["magnitude"],
            canonical_form_distance_to_catalog=eval_data["canonical_form_distance"],
        ))

        # Fitness
        fitness = FitnessTuple(
            battery_survival_count=int(eval_data["substrate_pass"]),
            band_concentration_tier=2 if cell.magnitude_bucket in (1, 2) else 1,
            cost_amortized_score=1.0,
        )

        archive.submit(child, cell, fitness)

        if eval_data["substrate_pass"]:
            substrate_passed += 1
        if eval_data["is_obstruction"]:
            obstructions_found.append(episode_idx)
        if eval_data["is_secondary"]:
            secondaries_found.append(episode_idx)
        if eval_data["lift"] >= 5.0:
            high_lift_episodes.append({
                "episode": episode_idx,
                "lift": eval_data["lift"],
                "predicate": eval_data["predicate"],
                "operator": op_name,
            })

    elapsed = time.time() - t_start

    fill_counts = archive.operator_fill_count()
    structural = fill_counts.get("structural", 0)
    uniform = fill_counts.get("uniform", 0)

    return {
        "n_episodes": n_episodes,
        "seed": seed,
        "elapsed_s": elapsed,
        "archive_n_cells": archive.n_cells_filled(),
        "substrate_passed": substrate_passed,
        "obstructions_found": obstructions_found,
        "secondaries_found": secondaries_found,
        "n_high_lift": len(high_lift_episodes),
        "top_high_lift": sorted(high_lift_episodes, key=lambda x: -x["lift"])[:5],
        "fill_counts": fill_counts,
        "structural_uniform_ratio": structural / max(uniform, 1),
        "evaluator_cache_size": len(evaluator._cache),
        "obstruction_signature": OBSTRUCTION_SIGNATURE,
        "acceptance": {
            "completed_without_error": True,
            "obstruction_found_at_least_once": len(obstructions_found) > 0,
            "structural_beats_uniform": structural > uniform,
        },
    }


def format_report(results: Dict[str, Any]) -> str:
    a = results["acceptance"]
    lines = [
        "=" * 72,
        f"Trial 3 ObstructionEnv Smoke Test ({results['n_episodes']} episodes)",
        "=" * 72,
        "",
        "ACCEPTANCE",
        f"  [Completed without error]:           {'PASS' if a['completed_without_error'] else 'FAIL'}",
        f"  [Found OBSTRUCTION_SIGNATURE]:       {'PASS' if a['obstruction_found_at_least_once'] else 'FAIL'}",
        f"  [structural > uniform fills]:        {'PASS' if a['structural_beats_uniform'] else 'FAIL'}",
        "",
        f"OBSTRUCTION_SIGNATURE target: {results['obstruction_signature']}",
        f"  Found at episodes: {results['obstructions_found'][:5]}{'...' if len(results['obstructions_found'])>5 else ''}",
        f"  ({len(results['obstructions_found'])} hits in {results['n_episodes']} episodes)",
        "",
        f"SECONDARY_SIGNATURE hits: {len(results['secondaries_found'])}",
        f"HIGH-LIFT EPISODES (lift >= 5.0): {results['n_high_lift']}",
    ]
    if results["top_high_lift"]:
        lines.append("  Top 5 by lift:")
        for ep in results["top_high_lift"]:
            lines.append(
                f"    ep {ep['episode']:3d} ({ep['operator']:12s}): "
                f"lift={ep['lift']:.2f} predicate={ep['predicate']}"
            )

    lines += [
        "",
        f"Archive cells filled: {results['archive_n_cells']}",
        f"Substrate-PASSED:     {results['substrate_passed']} (lift >= 1.5 with match-group >= 2)",
        f"structural / uniform: {results['structural_uniform_ratio']:.2f}x",
        f"Elapsed:              {results['elapsed_s']:.2f}s ({results['n_episodes']/results['elapsed_s']:.0f} eps/sec)",
        "",
        "FILL COUNTS BY OPERATOR",
    ]
    for op, count in sorted(results["fill_counts"].items()):
        lines.append(f"  {op:18s}: {count:4d}")
    return "\n".join(lines)


if __name__ == "__main__":
    results = run_smoke_test(n_episodes=200, seed=42)
    out_dir = Path(__file__).parent
    (out_dir / "trial_3_obstruction_smoke_results.json").write_text(
        json.dumps(results, indent=2, default=str), encoding="utf-8"
    )
    report = format_report(results)
    (out_dir / "TRIAL_3_OBSTRUCTION_SMOKE_REPORT.md").write_text(report, encoding="utf-8")
    print()
    print(report)
