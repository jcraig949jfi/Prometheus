"""Trial 3 iter-28 — Ergon canonical pipeline against the REAL a149 corpus.

Per Iter 28 / Task #92. Per frontier verdict: highest-leverage move is to
run Ergon against Charon's ACTUAL a149_obstruction corpus, not the synthetic
mirror. Multi-restart at uniform=5% (deep assembly) AND uniform=30% (broad
coverage) per iter 27 finding.

Substrate-grade observation already from corpus loading:
  - Charon's hand-crafted signature {n_steps:5, neg_x:4, pos_x:1, has_diag_neg:True}
    matches the 5 anchor sequences A149074, A149081, A149082, A149089, A149090
  - But the corpus has SIX unanimous-kill records, not five!
  - A149499 is unanimous-kill with features {n_steps:5, neg_x:3, pos_x:2,
    neg_y:3, pos_y:2, neg_z:3, pos_z:2, has_diag_neg:True, has_diag_pos:True}
  - It's a 6th anchor Charon's manual signature_match misses.

Goal: does Ergon discover (a) Charon's existing signature, AND (b) a predicate
explaining why A149499 is also unanimous-killed?

Substrate-pass criterion adjusted for real corpus: lift>=2.0 (vs 1.5 synthetic),
match_size>=3. Real baseline kill rate is ~3.9% so a lift=2 predicate has
matched_kill_rate~7.8% — modest but meaningful.
"""
from __future__ import annotations

import json
import math
import random
import time
from pathlib import Path
from typing import Any, Dict, List

from ergon.learner.archive import FitnessTuple, MAPElitesArchive
from ergon.learner.descriptor import EvaluationResult, compute_cell_coordinate
from ergon.learner.genome import Genome
from ergon.learner.operators.anti_prior import AntiPriorOperator
from ergon.learner.operators.predicate_symbolic import PredicateSymbolicOperator
from ergon.learner.operators.structural import StructuralOperator
from ergon.learner.operators.uniform import UniformOperator
from ergon.learner.promotion_ledger import PromotionLedger
from ergon.learner.scheduler import OperatorScheduler
from ergon.learner.trials._a149_real_corpus import (
    UNANIMOUS_BATTERY,
    corpus_summary,
    load_a149_real_corpus,
)
from ergon.learner.trials.trial_3_obstruction_smoke import (
    genome_to_predicate, make_obstruction_atom_pool,
)


# Charon's hand-crafted signature for reference
CHARON_SIGNATURE = {
    "n_steps": 5, "neg_x": 4, "pos_x": 1, "has_diag_neg": True,
}

# A149499 — the outlier 6th unanimous-kill
A149499_FEATURES = {
    "n_steps": 5, "neg_x": 3, "pos_x": 2, "neg_y": 3, "pos_y": 2,
    "neg_z": 3, "pos_z": 2, "has_diag_neg": True, "has_diag_pos": True,
}


def _matches(feats: Dict[str, Any], pred: Dict[str, Any]) -> bool:
    return all(feats.get(k) == v for k, v in pred.items())


def evaluate_predicate_on_a149(pred: Dict[str, Any], corpus) -> Dict[str, Any]:
    """Evaluate a predicate against the real a149 corpus.

    Returns lift / match_size / kill_rates. Uses kill_verdict=True
    (any battery test fired) as the positive class.
    """
    if not pred:  # empty predicate matches all
        n = len(corpus)
        n_kill = sum(1 for e in corpus if e.kill_verdict)
        return {
            "match_group_size": n, "matched_kill_rate": n_kill / n,
            "baseline_kill_rate": 0.0, "lift": 1.0,
            "lift_excess": 0.0, "n_corpus": n,
        }
    matches = [e for e in corpus if _matches(e.features(), pred)]
    nonmatches = [e for e in corpus if not _matches(e.features(), pred)]
    n_match = len(matches)
    n_non = len(nonmatches)
    matched_kr = (sum(1 for e in matches if e.kill_verdict) / n_match) if n_match else 0.0
    baseline_kr = (sum(1 for e in nonmatches if e.kill_verdict) / n_non) if n_non else 0.0
    lift = (matched_kr / baseline_kr) if baseline_kr > 0 else (
        float("inf") if matched_kr > 0 else 0.0
    )
    return {
        "match_group_size": n_match, "matched_kill_rate": matched_kr,
        "baseline_kill_rate": baseline_kr, "lift": lift,
        "lift_excess": max(0.0, lift - 1.0), "n_corpus": len(corpus),
    }


def _is_charon_disc(pred: Dict[str, Any], corpus) -> bool:
    """Match-set equivalence to Charon's hand-crafted signature."""
    if not pred:
        return False
    charon_ids = {id(e) for e in corpus if _matches(e.features(), CHARON_SIGNATURE)}
    pred_ids = {id(e) for e in corpus if _matches(e.features(), pred)}
    return pred_ids == charon_ids and len(charon_ids) > 0


def _captures_a149499(pred: Dict[str, Any]) -> bool:
    """Does this predicate match A149499 (the 6th unanimous-kill outlier)?"""
    if not pred:
        return False
    return _matches(A149499_FEATURES, pred)


def run_one_seed_on_a149(
    seed: int, n_episodes: int, corpus, weights: Dict[str, float],
    ledger: PromotionLedger, kernel_binding_name: str,
    exploration_rate: float = 0.15,
) -> Dict[str, Any]:
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
    cache: Dict[str, Dict[str, Any]] = {}
    substrate_passed = 0
    charon_exact = charon_disc = a149499_capture = 0
    high_lift_predicates: List[Dict[str, Any]] = []
    t_start = time.time()
    LIFT_PROMOTE = 2.0  # adjusted for real corpus
    MIN_MATCH = 3
    for ep in range(n_episodes):
        op_class = scheduler.next_operator_class(ep)
        op_name = op_class if op_class in operators else "uniform"
        operator = operators[op_name]
        parent = None
        if op_name in ("structural", "symbolic") and archive.n_cells_filled() > 0:
            pe = archive.sample_parent(
                rng, substrate_pass_bias=5.0, exploration_rate=exploration_rate,
            )
            if pe is not None:
                parent = archive.get_genome(pe.content_hash)
        child = operator.mutate(parent, rng, atom_pool)
        child = Genome(
            nodes=child.nodes, target_predicate=child.target_predicate,
            mutation_operator_class=op_name, parent_hash=child.parent_hash,
            metadata=dict(child.metadata),
        )
        ch = child.content_hash()
        if ch in cache:
            d = cache[ch]
        else:
            pred = genome_to_predicate(child)
            pe = evaluate_predicate_on_a149(pred, corpus)
            lift = pe["lift"]
            ms = pe["match_group_size"]
            passes = (lift >= LIFT_PROMOTE and ms >= MIN_MATCH and lift != float("inf"))
            d = {"predicate": pred, "lift": lift, "match_size": ms,
                 "matched_kill_rate": pe["matched_kill_rate"], "passes": passes}
            cache[ch] = d
        pred = d["predicate"]
        # Synthetic descriptor inputs
        feats = sorted(pred.keys())
        if not feats: subclass = "group_quotient"
        elif "has_diag_neg" in feats or "has_diag_pos" in feats: subclass = "variety_fingerprint"
        elif any(f.startswith("neg_") for f in feats): subclass = "ideal_reduction"
        else: subclass = "partition_refinement"
        magnitude = 10.0 ** (math.log10(1 + min(d["lift"], 100.0)) * 7)
        cell = compute_cell_coordinate(child, evaluation=EvaluationResult(
            output_canonicalizer_subclass=subclass,
            output_magnitude=magnitude,
            canonical_form_distance_to_catalog=float(len(pred)),
        ))
        cont_score = math.log10(1 + min(d["lift"], 100.0))
        fitness = FitnessTuple(
            battery_survival_count=int(d["passes"]),
            band_concentration_tier=2 if cell.magnitude_bucket in (1, 2) else 1,
            continuous_signal_score=cont_score, cost_amortized_score=1.0,
        )
        archive.submit(child, cell, fitness)
        if d["passes"]:
            substrate_passed += 1
            is_ch_exact = (pred == CHARON_SIGNATURE)
            is_ch_disc = _is_charon_disc(pred, corpus)
            captures_499 = _captures_a149499(pred)
            if is_ch_exact: charon_exact += 1
            if is_ch_disc: charon_disc += 1
            if captures_499: a149499_capture += 1
            ledger.append(
                seed=seed, episode=ep,
                genome_content_hash=child.content_hash(),
                operator_class=op_name, predicate=pred,
                lift=d["lift"], match_size=d["match_size"],
                kernel_binding_name=kernel_binding_name,
                is_obstruction_exact=is_ch_exact,
                is_secondary_exact=False,
                is_obstruction_discriminator=is_ch_disc,
                is_secondary_discriminator=captures_499,
                extra={"matched_kill_rate": d["matched_kill_rate"]},
            )
            if d["lift"] >= 5.0 and d["match_size"] >= 3:
                high_lift_predicates.append({
                    "ep": ep, "lift": d["lift"], "match_size": d["match_size"],
                    "matched_kill_rate": d["matched_kill_rate"],
                    "predicate": dict(pred), "operator": op_name,
                })
    elapsed = time.time() - t_start
    return {
        "seed": seed, "n_episodes": n_episodes, "weights": weights,
        "elapsed_s": elapsed, "substrate_passed": substrate_passed,
        "archive_n_cells": archive.n_cells_filled(),
        "charon_exact": charon_exact, "charon_disc": charon_disc,
        "a149499_capture": a149499_capture,
        "n_high_lift": len(high_lift_predicates),
        "top_high_lift": sorted(high_lift_predicates, key=lambda x: -x["lift"])[:5],
    }


if __name__ == "__main__":
    out_dir = Path(__file__).parent
    ledger_dir = out_dir / "ledgers"
    ledger_dir.mkdir(parents=True, exist_ok=True)

    print("Loading real a149 corpus...")
    corpus = load_a149_real_corpus()
    summary = corpus_summary(corpus)
    print(f"  {summary['n_total']} records, {summary['n_kill_any']} killed by >=1 test")
    print(f"  unanimous-kill: {summary['n_unanimous_kill']}, partial: {summary['n_partial_kill']}")
    print(f"  baseline kill rate: {summary['baseline_kill_rate']:.4f}")
    print()

    seeds = [42, 100, 1234]
    n_episodes = 5000
    kernel_binding_name = "ergon_a149_real_corpus_eval"

    weight_configs = {
        "u05_canonical": {  # iter 18 weights — combinatorial assembly
            "structural": 0.65, "symbolic": 0.15, "uniform": 0.05,
            "structured_null": 0.05, "anti_prior": 0.10,
        },
        "u30_broad": {  # iter 26 weights — feature subspace coverage
            "structural": 0.40, "symbolic": 0.15, "uniform": 0.30,
            "structured_null": 0.05, "anti_prior": 0.10,
        },
    }

    all_results: Dict[str, List[Dict[str, Any]]] = {}
    for cfg_name, weights in weight_configs.items():
        ledger_path = ledger_dir / f"trial_3_iter28_a149_{cfg_name}_ledger.jsonl"
        if ledger_path.exists():
            ledger_path.unlink()
        manifest = {
            "weights": weights,
            "exploration_rate": 0.15,
            "n_episodes": n_episodes,
            "n_seeds": len(seeds),
            "evaluator": "in-process_predicate_eval",
            "corpus_id": "a149_real_v1",
            "lift_threshold": 2.0,
            "min_match_size": 3,
        }
        ledger = PromotionLedger(
            path=ledger_path,
            trial_name=f"trial_3_iter28_a149_{cfg_name}",
            regime_manifest=manifest,
        )
        print(f"Config: {cfg_name}  weights={weights}")
        per_seed = []
        for seed in seeds:
            print(f"  Seed {seed}...", end=" ", flush=True)
            r = run_one_seed_on_a149(
                seed, n_episodes, corpus, weights, ledger, kernel_binding_name
            )
            print(
                f"charon_ex={r['charon_exact']} ch_disc={r['charon_disc']} "
                f"a149499_cap={r['a149499_capture']} pass={r['substrate_passed']} "
                f"high_lift={r['n_high_lift']} ({r['elapsed_s']:.1f}s)"
            )
            per_seed.append(r)
        all_results[cfg_name] = per_seed

    # Save results
    (out_dir / "trial_3_iter28_a149_results.json").write_text(
        json.dumps(all_results, indent=2, default=str), encoding="utf-8"
    )

    # Aggregate report
    print()
    print("=" * 78)
    print("Trial 3 Iter-28 — Ergon vs REAL a149 corpus (5K eps x 3 seeds, multi-restart)")
    print("=" * 78)
    print()
    print(f"  {'config':>20} {'CHARON_ex':>10} {'CHARON_disc':>12} {'A149499_cap':>12} {'pass':>6}")
    for cfg_name, per_seed in all_results.items():
        ce = sum(1 for s in per_seed if s["charon_exact"] > 0)
        cd = sum(1 for s in per_seed if s["charon_disc"] > 0)
        a4 = sum(1 for s in per_seed if s["a149499_capture"] > 0)
        ps = sum(s["substrate_passed"] for s in per_seed)
        print(f"  {cfg_name:>20} {ce:>8d}/3 {cd:>10d}/3 {a4:>10d}/3 {ps:>6d}")

    # Show top high-lift predicates from each config
    print()
    print("TOP HIGH-LIFT PREDICATES PER CONFIG (lift >= 5)")
    for cfg_name, per_seed in all_results.items():
        all_high = []
        for s in per_seed:
            all_high.extend(s["top_high_lift"])
        all_high.sort(key=lambda x: -x["lift"])
        # Dedupe by predicate
        seen = set()
        uniq = []
        for h in all_high:
            key = tuple(sorted(h["predicate"].items()))
            if key not in seen:
                seen.add(key)
                uniq.append(h)
        print(f"  {cfg_name}:")
        for h in uniq[:5]:
            print(f"    lift={h['lift']:.2f}, match={h['match_size']}, "
                  f"kr={h['matched_kill_rate']:.3f}, predicate={h['predicate']}")
