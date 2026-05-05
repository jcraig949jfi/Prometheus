"""Trial 3 iter-26 — bumped uniform weight test for TARGET_C recovery.

Per Iter 25 finding: seed 100 never finds TARGET_C across rate=0/0.15/0.25.
Hypothesis: structural operator extends existing genomes (path-dependent
exploration bias). Once parents converge on x-axis features (A) or
n_steps+diag (B), descendants stay in those feature subspaces. z-axis
features (TARGET_C) get attention only from uniform/anti_prior/structured_null.

This trial bumps uniform weight from 5% → 30% (taking from structural's 65%).
If seed 100 finds TARGET_C at the bumped weights, the root-cause hypothesis
is validated.

Acceptance: at bumped weights, seed 100 finds TARGET_C at 10K eps.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from ergon.learner.trials.trial_3_iter25_three_targets import (
    TARGET_A, TARGET_B, TARGET_C,
    _is_target_a_disc, _is_target_b_disc, _is_target_c_disc,
    _matches, build_three_target_corpus,
)


def run_one_seed_with_weights(
    seed: int,
    n_episodes: int,
    corpus,
    weights: Dict[str, float],
    exploration_rate: float = 0.15,
) -> Dict[str, Any]:
    """Mirror of iter 25's run_one_seed but with custom weights."""
    import math
    import random
    from prometheus_math.obstruction_env import evaluate_predicate
    from ergon.learner.archive import FitnessTuple, MAPElitesArchive
    from ergon.learner.descriptor import EvaluationResult, compute_cell_coordinate
    from ergon.learner.genome import Genome
    from ergon.learner.operators.anti_prior import AntiPriorOperator
    from ergon.learner.operators.predicate_symbolic import PredicateSymbolicOperator
    from ergon.learner.operators.structural import StructuralOperator
    from ergon.learner.operators.uniform import UniformOperator
    from ergon.learner.scheduler import OperatorScheduler
    from ergon.learner.trials.trial_3_obstruction_smoke import (
        genome_to_predicate, make_obstruction_atom_pool,
    )

    atom_pool = make_obstruction_atom_pool()
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
    a_exact = b_exact = c_exact = 0
    a_disc = b_disc = c_disc = 0
    first_c_disc_ep = None
    substrate_passed = 0
    cache: Dict[str, Dict[str, Any]] = {}
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
        ch = child.content_hash()
        if ch in cache:
            d = cache[ch]
        else:
            pred = genome_to_predicate(child)
            pe = evaluate_predicate(pred, corpus)
            d = {
                "predicate": pred, "lift": pe["lift"],
                "match_size": pe["match_group_size"],
                "passes": pe["lift"] >= 1.5 and pe["match_group_size"] >= 3,
            }
            cache[ch] = d
        pred = d["predicate"]
        feats = sorted(pred.keys())
        if not feats:
            subclass = "group_quotient"
        elif "has_diag_neg" in feats or "has_diag_pos" in feats:
            subclass = "variety_fingerprint"
        elif any(f.startswith("neg_") for f in feats):
            subclass = "ideal_reduction"
        else:
            subclass = "partition_refinement"
        magnitude = 10.0 ** (math.log10(1 + d["lift"]) * 7)
        cell = compute_cell_coordinate(child, evaluation=EvaluationResult(
            output_canonicalizer_subclass=subclass,
            output_magnitude=magnitude,
            canonical_form_distance_to_catalog=float(len(pred)),
        ))
        cont_score = math.log10(1 + d["lift"])
        fitness = FitnessTuple(
            battery_survival_count=int(d["passes"]),
            band_concentration_tier=2 if cell.magnitude_bucket in (1, 2) else 1,
            continuous_signal_score=cont_score,
            cost_amortized_score=1.0,
        )
        archive.submit(child, cell, fitness)
        if d["passes"]:
            substrate_passed += 1
            if pred == TARGET_A: a_exact += 1
            if pred == TARGET_B: b_exact += 1
            if pred == TARGET_C: c_exact += 1
            if _is_target_a_disc(pred, corpus): a_disc += 1
            if _is_target_b_disc(pred, corpus): b_disc += 1
            if _is_target_c_disc(pred, corpus):
                c_disc += 1
                if first_c_disc_ep is None:
                    first_c_disc_ep = ep
    elapsed = time.time() - t_start
    return {
        "seed": seed,
        "weights": weights,
        "n_episodes": n_episodes,
        "elapsed_s": elapsed,
        "a_disc": a_disc, "b_disc": b_disc, "c_disc": c_disc,
        "a_exact": a_exact, "b_exact": b_exact, "c_exact": c_exact,
        "substrate_passed": substrate_passed,
        "first_c_disc_ep": first_c_disc_ep,
        "archive_n_cells": archive.n_cells_filled(),
    }


if __name__ == "__main__":
    seeds = [42, 100, 1234]
    n_episodes = 10000
    corpus = build_three_target_corpus()

    # Weights to test
    weight_configs = {
        "baseline": {  # iter 18 weights for reference
            "structural": 0.65, "symbolic": 0.15,
            "uniform": 0.05, "structured_null": 0.05, "anti_prior": 0.10,
        },
        "bumped_uniform_30": {  # iter 26 candidate
            "structural": 0.40, "symbolic": 0.15,
            "uniform": 0.30, "structured_null": 0.05, "anti_prior": 0.10,
        },
        "bumped_uniform_15": {  # intermediate
            "structural": 0.55, "symbolic": 0.15,
            "uniform": 0.15, "structured_null": 0.05, "anti_prior": 0.10,
        },
    }

    all_results: Dict[str, List[Dict[str, Any]]] = {}
    print(f"3-target corpus: {len(corpus)} records ({sum(1 for e in corpus if _matches(e.features(), TARGET_C))} TARGET_C matches)")
    print()
    for cfg_name, weights in weight_configs.items():
        print(f"Config: {cfg_name}  weights={weights}")
        per_seed = []
        for seed in seeds:
            print(f"  Seed {seed}...", end=" ", flush=True)
            result = run_one_seed_with_weights(
                seed, n_episodes, corpus, weights, exploration_rate=0.15
            )
            print(
                f"A={result['a_disc']} B={result['b_disc']} C={result['c_disc']} "
                f"first_C={result['first_c_disc_ep']} ({result['elapsed_s']:.1f}s)"
            )
            per_seed.append(result)
        all_results[cfg_name] = per_seed

    # Aggregate report
    print()
    print("=" * 78)
    print(f"Trial 3 Iter-26 — bumped uniform weight test (10K eps x 3 seeds, rate=0.15)")
    print("=" * 78)
    print()
    print(f"{'config':>20} {'A/3':>5} {'B/3':>5} {'C/3':>5} {'cov/9':>7} {'seed_100_C':>11}")
    for cfg_name, per_seed in all_results.items():
        a_n = sum(1 for s in per_seed if s["a_disc"] > 0)
        b_n = sum(1 for s in per_seed if s["b_disc"] > 0)
        c_n = sum(1 for s in per_seed if s["c_disc"] > 0)
        s100 = next(s for s in per_seed if s["seed"] == 100)
        s100_c = "FOUND" if s100["c_disc"] > 0 else "missed"
        print(
            f"{cfg_name:>20} {a_n:>3d}/3 {b_n:>3d}/3 {c_n:>3d}/3 "
            f"{a_n+b_n+c_n:>5d}/9 {s100_c:>11}"
        )

    out = Path(__file__).parent / "trial_3_iter26_results.json"
    out.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print()
    print("ACCEPTANCE")
    bumped_30 = all_results["bumped_uniform_30"]
    s100_bumped = next(s for s in bumped_30 if s["seed"] == 100)
    found = s100_bumped["c_disc"] > 0
    print(f"  [Seed 100 finds TARGET_C at uniform=0.30]:  "
          f"{'PASS' if found else 'FAIL'} ({'found at ep ' + str(s100_bumped['first_c_disc_ep']) if found else 'not found'})")
