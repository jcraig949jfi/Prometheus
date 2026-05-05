"""Trial 3 iter-25 — 3-target synthetic corpus generalization test.

Per Iter 25 / Task #89. Validates the iter 13 substrate-grade claim that
exploration_rate is a multi-target coverage dial. The OBSTRUCTION corpus
has 2 planted signatures (OBSTRUCTION + SECONDARY); this trial extends
to 3 by planting a TARGET_C signature in z-axis features (orthogonal to
OBSTRUCTION's x-axis and SECONDARY's n_steps/has_diag_pos).

If the iter 13 finding generalizes:
  - rate=0.0 should miss TARGET_C in at least 1 seed (mode-collapse around
    whichever target the bias-favored parents land on first)
  - rate=0.15 should enable 3/3 seeds to find ALL 3 targets at sufficient
    episodes
  - rate=0.25 may oversample exploration and slow per-target convergence

The corpus is generated inline (no modification to prometheus_math). It
uses the same CorpusEntry dataclass as the OBSTRUCTION corpus so all
the existing infrastructure (evaluate_predicate, ObstructionBindEval-
Evaluator stub) works unchanged.
"""
from __future__ import annotations

import json
import math
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from prometheus_math._obstruction_corpus import CorpusEntry
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


# ============================================================================
# Three-target synthetic corpus
# ============================================================================

TARGET_A = {"n_steps": 5, "neg_x": 4, "pos_x": 1, "has_diag_neg": True}
TARGET_B = {"n_steps": 7, "has_diag_pos": True}
TARGET_C = {"neg_z": 4, "pos_z": 4}

CORPUS_SEED = 20260504


def _matches(features: Dict[str, Any], pred: Dict[str, Any]) -> bool:
    return all(features.get(k) == v for k, v in pred.items())


def _make_target_a(rng: random.Random) -> CorpusEntry:
    return CorpusEntry(
        n_steps=5, neg_x=4, pos_x=1,
        neg_y=rng.randint(0, 4), pos_y=rng.randint(0, 4),
        neg_z=rng.choice([0, 1, 2, 3, 5]),  # never 4 (so doesn't accidentally match C)
        pos_z=rng.choice([0, 1, 2, 3, 5]),
        has_diag_neg=True, has_diag_pos=rng.random() < 0.3,
        kill_verdict=True,
    )


def _make_target_b(rng: random.Random) -> CorpusEntry:
    return CorpusEntry(
        n_steps=7,
        neg_x=rng.randint(0, 5), pos_x=rng.randint(0, 5),
        neg_y=rng.randint(0, 4), pos_y=rng.randint(0, 4),
        neg_z=rng.choice([0, 1, 2, 3, 5]),
        pos_z=rng.choice([0, 1, 2, 3, 5]),
        has_diag_neg=rng.random() < 0.3, has_diag_pos=True,
        kill_verdict=True,
    )


def _make_target_c(rng: random.Random) -> CorpusEntry:
    """Forces neg_z=4 AND pos_z=4. Other features force-disqualify A and B."""
    # Force n_steps != 5 AND != 7 so doesn't accidentally start matching A or B
    n_steps = rng.choice([3, 4, 6])
    return CorpusEntry(
        n_steps=n_steps,
        neg_x=rng.randint(0, 5), pos_x=rng.randint(0, 5),
        neg_y=rng.randint(0, 4), pos_y=rng.randint(0, 4),
        neg_z=4, pos_z=4,
        has_diag_neg=rng.random() < 0.3, has_diag_pos=rng.random() < 0.3,
        kill_verdict=True,
    )


def _make_nonmatch(rng: random.Random, noise_kill_prob: float) -> CorpusEntry:
    """Generate a record that matches none of A, B, C.

    Strategy:
      - For n_steps=5: neg_x ∈ {0,1,2,3,5} (excludes A)
      - For n_steps=7: has_diag_pos=False (excludes B)
      - For all: NOT (neg_z=4 AND pos_z=4) (excludes C)
    """
    while True:
        n_steps = rng.choice([3, 3, 4, 4, 5, 6, 6, 7])
        if n_steps == 5:
            neg_x = rng.choice([0, 1, 2, 3, 5])
            pos_x = rng.randint(0, 5)
            has_diag_neg = rng.random() < 0.3
            has_diag_pos = rng.random() < 0.3
        elif n_steps == 7:
            neg_x = rng.randint(0, 5)
            pos_x = rng.randint(0, 5)
            has_diag_neg = rng.random() < 0.3
            has_diag_pos = False
        else:
            neg_x = rng.randint(0, 5)
            pos_x = rng.randint(0, 5)
            has_diag_neg = rng.random() < 0.3
            has_diag_pos = rng.random() < 0.3
        # z-axis: force NOT (4, 4) to exclude C
        neg_z = rng.randint(0, 5)
        pos_z = rng.randint(0, 5)
        if neg_z == 4 and pos_z == 4:
            # would match C; resample one of them
            if rng.random() < 0.5:
                neg_z = rng.choice([0, 1, 2, 3, 5])
            else:
                pos_z = rng.choice([0, 1, 2, 3, 5])
        entry = CorpusEntry(
            n_steps=n_steps,
            neg_x=neg_x, pos_x=pos_x,
            neg_y=rng.randint(0, 4), pos_y=rng.randint(0, 4),
            neg_z=neg_z, pos_z=pos_z,
            has_diag_neg=has_diag_neg, has_diag_pos=has_diag_pos,
            kill_verdict=(rng.random() < noise_kill_prob),
        )
        feats = entry.features()
        if not _matches(feats, TARGET_A) and not _matches(feats, TARGET_B) and not _matches(feats, TARGET_C):
            return entry
        # else loop


def build_three_target_corpus(
    seed: int = CORPUS_SEED,
    n_total: int = 200,
    n_a: int = 8,
    n_b: int = 4,
    n_c: int = 4,
    noise_kill_prob: float = 0.015,
) -> List[CorpusEntry]:
    rng = random.Random(seed)
    entries = []
    for _ in range(n_a):
        entries.append(_make_target_a(rng))
    for _ in range(n_b):
        entries.append(_make_target_b(rng))
    for _ in range(n_c):
        entries.append(_make_target_c(rng))
    n_noise = n_total - n_a - n_b - n_c
    for _ in range(n_noise):
        entries.append(_make_nonmatch(rng, noise_kill_prob))
    rng.shuffle(entries)
    return entries


# ============================================================================
# Trial loop
# ============================================================================


def _is_target_a_disc(pred: Dict[str, Any], corpus: List[CorpusEntry]) -> bool:
    if not pred:
        return False
    a_ids = {id(e) for e in corpus if _matches(e.features(), TARGET_A)}
    pred_ids = {id(e) for e in corpus if _matches(e.features(), pred)}
    return pred_ids == a_ids and len(a_ids) > 0


def _is_target_b_disc(pred: Dict[str, Any], corpus: List[CorpusEntry]) -> bool:
    if not pred:
        return False
    b_ids = {id(e) for e in corpus if _matches(e.features(), TARGET_B)}
    pred_ids = {id(e) for e in corpus if _matches(e.features(), pred)}
    return pred_ids == b_ids and len(b_ids) > 0


def _is_target_c_disc(pred: Dict[str, Any], corpus: List[CorpusEntry]) -> bool:
    if not pred:
        return False
    c_ids = {id(e) for e in corpus if _matches(e.features(), TARGET_C)}
    pred_ids = {id(e) for e in corpus if _matches(e.features(), pred)}
    return pred_ids == c_ids and len(c_ids) > 0


def run_one_seed(
    seed: int,
    n_episodes: int,
    corpus: List[CorpusEntry],
    exploration_rate: float = 0.15,
) -> Dict[str, Any]:
    atom_pool = make_obstruction_atom_pool()
    archive = MAPElitesArchive()
    rng = random.Random(seed)

    custom_weights = {
        "structural": 0.65, "symbolic": 0.15,
        "uniform": 0.05, "structured_null": 0.05, "anti_prior": 0.10,
    }
    scheduler = OperatorScheduler(operator_weights=custom_weights, seed=seed)
    operators = {
        "structural": StructuralOperator(),
        "symbolic": PredicateSymbolicOperator(),
        "uniform": UniformOperator(n_atoms_distribution=(1, 4)),
        "structured_null": UniformOperator(n_atoms_distribution=(2, 4)),
        "anti_prior": AntiPriorOperator(),
    }

    a_exact: List[int] = []
    b_exact: List[int] = []
    c_exact: List[int] = []
    a_disc: List[int] = []
    b_disc: List[int] = []
    c_disc: List[int] = []
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
            mutation_operator_class=op_name,  # type: ignore[arg-type]
            parent_hash=child.parent_hash,
            metadata=dict(child.metadata),
        )
        ch = child.content_hash()
        if ch in cache:
            obs_data = cache[ch]
        else:
            pred = genome_to_predicate(child)
            pred_eval = evaluate_predicate(pred, corpus)
            lift = pred_eval["lift"]
            match_size = pred_eval["match_group_size"]
            passes = (lift >= 1.5 and match_size >= 3)
            obs_data = {
                "predicate": pred, "lift": lift,
                "match_size": match_size, "substrate_pass": passes,
            }
            cache[ch] = obs_data

        pred = obs_data["predicate"]
        passes = obs_data["substrate_pass"]
        lift = obs_data["lift"]

        # Build a synthetic CellCoordinate input
        feats = sorted(pred.keys())
        if not feats:
            subclass = "group_quotient"
        elif "has_diag_neg" in feats or "has_diag_pos" in feats:
            subclass = "variety_fingerprint"
        elif any(f.startswith("neg_") for f in feats):
            subclass = "ideal_reduction"
        else:
            subclass = "partition_refinement"
        magnitude = 10.0 ** (math.log10(1 + lift) * 7)
        sig_dist = float(len(pred))

        cell = compute_cell_coordinate(child, evaluation=EvaluationResult(
            output_canonicalizer_subclass=subclass,
            output_magnitude=magnitude,
            canonical_form_distance_to_catalog=sig_dist,
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
            if pred == TARGET_A:
                a_exact.append(ep)
            if pred == TARGET_B:
                b_exact.append(ep)
            if pred == TARGET_C:
                c_exact.append(ep)
            if _is_target_a_disc(pred, corpus):
                a_disc.append(ep)
            if _is_target_b_disc(pred, corpus):
                b_disc.append(ep)
            if _is_target_c_disc(pred, corpus):
                c_disc.append(ep)

    elapsed = time.time() - t_start
    return {
        "seed": seed, "n_episodes": n_episodes,
        "exploration_rate": exploration_rate,
        "elapsed_s": elapsed,
        "archive_n_cells": archive.n_cells_filled(),
        "substrate_passed": substrate_passed,
        "a_exact": len(a_exact), "b_exact": len(b_exact), "c_exact": len(c_exact),
        "a_disc": len(a_disc), "b_disc": len(b_disc), "c_disc": len(c_disc),
        "first_a_exact_ep": a_exact[0] if a_exact else None,
        "first_b_exact_ep": b_exact[0] if b_exact else None,
        "first_c_exact_ep": c_exact[0] if c_exact else None,
        "first_a_disc_ep": a_disc[0] if a_disc else None,
        "first_b_disc_ep": b_disc[0] if b_disc else None,
        "first_c_disc_ep": c_disc[0] if c_disc else None,
    }


if __name__ == "__main__":
    seeds = [42, 100, 1234]
    n_episodes = 10000  # iter 13 confirmed 10K reaches 3/3 at rate=0.15
    rates = [0.0, 0.15, 0.25]

    corpus = build_three_target_corpus()
    print(f"Three-target corpus: {len(corpus)} records")
    print(f"  TARGET_A matches: {sum(1 for e in corpus if _matches(e.features(), TARGET_A))}")
    print(f"  TARGET_B matches: {sum(1 for e in corpus if _matches(e.features(), TARGET_B))}")
    print(f"  TARGET_C matches: {sum(1 for e in corpus if _matches(e.features(), TARGET_C))}")
    print()

    all_results: Dict[str, List[Dict[str, Any]]] = {}
    for rate in rates:
        print(f"Exploration rate {rate}:")
        per_seed = []
        for seed in seeds:
            print(f"  Seed {seed}...", end=" ", flush=True)
            result = run_one_seed(seed, n_episodes, corpus, rate)
            print(
                f"A={result['a_disc']}/{result['a_exact']} "
                f"B={result['b_disc']}/{result['b_exact']} "
                f"C={result['c_disc']}/{result['c_exact']} "
                f"pass={result['substrate_passed']} "
                f"({result['elapsed_s']:.1f}s)"
            )
            per_seed.append(result)
        all_results[f"rate_{rate:.2f}"] = per_seed

    # Aggregate report
    print()
    print("=" * 78)
    print(f"Trial 3 Iter-25 — 3-target generalization test (10K eps x 3 seeds)")
    print("=" * 78)
    print()
    print(f"{'rate':>6} {'A/3':>5} {'B/3':>5} {'C/3':>5} "
          f"{'A_disc/3':>9} {'B_disc/3':>9} {'C_disc/3':>9} "
          f"{'cov/9':>7}")
    for rate in rates:
        per_seed = all_results[f"rate_{rate:.2f}"]
        a_seeds = sum(1 for s in per_seed if s["a_exact"] > 0)
        b_seeds = sum(1 for s in per_seed if s["b_exact"] > 0)
        c_seeds = sum(1 for s in per_seed if s["c_exact"] > 0)
        ad = sum(1 for s in per_seed if s["a_disc"] > 0)
        bd = sum(1 for s in per_seed if s["b_disc"] > 0)
        cd = sum(1 for s in per_seed if s["c_disc"] > 0)
        coverage = ad + bd + cd
        print(
            f"{rate:>6.2f} {a_seeds:>3d}/3 {b_seeds:>3d}/3 {c_seeds:>3d}/3 "
            f"{ad:>7d}/3 {bd:>7d}/3 {cd:>7d}/3 "
            f"{coverage:>5d}/9"
        )

    out_dir = Path(__file__).parent
    (out_dir / "trial_3_iter25_results.json").write_text(
        json.dumps(all_results, indent=2, default=str), encoding="utf-8"
    )
    print()
    print("ACCEPTANCE")
    rate_015 = all_results["rate_0.15"]
    a_015 = sum(1 for s in rate_015 if s["a_disc"] > 0)
    b_015 = sum(1 for s in rate_015 if s["b_disc"] > 0)
    c_015 = sum(1 for s in rate_015 if s["c_disc"] > 0)
    rate_0 = all_results["rate_0.00"]
    c_0 = sum(1 for s in rate_0 if s["c_disc"] > 0)
    print(f"  [rate=0.15: 3/3 seeds find ALL 3 targets]:  "
          f"{'PASS' if a_015 == 3 and b_015 == 3 and c_015 == 3 else 'FAIL'} "
          f"(A={a_015}/3, B={b_015}/3, C={c_015}/3)")
    print(f"  [rate=0: misses TARGET_C in >=1 seed]:      "
          f"{'PASS' if c_0 < 3 else 'FAIL (means rate=0 surprisingly works for 3-target too)'} "
          f"(C={c_0}/3 at rate=0)")
