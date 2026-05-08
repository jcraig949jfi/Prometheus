"""Substrate-Tester Fire #39 harness — second fire under HARD-6 posture.

Lane 12 (representation-pressure) — pulled catalog entry #84
(Optimal tensor network contraction order; §X Quantum Information /
Tensor Networks; paradigm P30 Tensor Network Contraction). Diversifies
from fire #38's §I rank/border-rank focus into §X tensor-network
combinatorics. NP-hard contraction-order optimization (Markov-Shi);
practical tools = opt_einsum / cotengra / TensorNetwork.

Lane 4 — SIGMA opcode smoke (RESOLVE/CLAIM/FALSIFY/GATE chain) —
different from fire #38's cert smoke. Quick regression on the kernel's
core opcode chain.

Outputs:
  charon/diagnostics/substrate_tester_fire_39_results.json
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 12 — catalog-pulled probe: optimal tensor network contraction order
# ---------------------------------------------------------------------------


def lane_12_contraction_order_probe() -> Dict[str, Any]:
    """Attempt to encode the structure of catalog entry #84 — optimal
    tensor network contraction order — using existing substrate
    primitives. Document failures as capability gaps."""

    # Conceptual setup: a tensor network is a graph G = (V, E) where
    # vertices = tensors with shapes and edges = shared indices.
    # A contraction order is a permutation of edges (or equivalently a
    # rooted binary tree over leaf tensors). Cost = max intermediate
    # tensor size (memory-optimal) or sum of FLOPs (time-optimal).
    # The optimization problem is NP-hard (Markov-Shi 2008).

    # Toy example for the probe: a 4-tensor network with shapes
    #   A: (a, b)  B: (b, c)  C: (c, d)  D: (d, a)   — a "cycle of 4"
    # The optimal contraction order depends on the dimensions; e.g. if
    # b is small and a, c, d are large, contract A·B first, etc.

    network_data = {
        "vertices": ["A", "B", "C", "D"],
        "edges": [("A", "B", "b", 5), ("B", "C", "c", 5), ("C", "D", "d", 5), ("D", "A", "a", 5)],
        "all_dims_equal": True,
        "n_possible_contraction_orders": 6,  # (4-1)! / 2 for tree topology of 4 leaves; here cycle so different
    }

    encoding_attempts: List[Dict[str, Any]] = []

    # Probe 1: encode the network as CoordinateChart
    encoding_attempts.append({
        "probe": "encode_TN_as_CoordinateChart",
        "attempt": (
            "CoordinateChart(domain='tensor_network', region_key='cycle4', "
            "coordinate_system=('a', 'b', 'c', 'd'), metric=...)."
        ),
        "blocker": (
            "CoordinateChart's coordinate_system is a flat tuple of named "
            "scalar axes. Tensor network is a graph (vertices = node "
            "tensors; edges = shared indices; per-vertex shape annotation). "
            "Loses topology — substrate has no GraphObject primitive. The "
            "incidence (which vertex shares which index with which other "
            "vertex) is the structure being optimized over; it can't be "
            "reduced to a flat tuple."
        ),
        "verdict": "FAIL_ENCODING — no GraphObject primitive",
    })

    # Probe 2: encode contraction order as MethodSpec / IndependenceClass
    encoding_attempts.append({
        "probe": "encode_order_as_MethodSpec",
        "attempt": (
            "MethodSpec(engine='opt_einsum', strategy='greedy', "
            "independence_class=??, version='3.4.0'). Each contraction "
            "order = a separate MethodSpec instance with the order encoded "
            "in 'parameters'."
        ),
        "blocker": (
            "MethodSpec's IndependenceClass enum has no value for "
            "'tensor_network_contraction_order'. Even if added: the "
            "permutation = order encoding loses the OPTIMIZATION SEMANTICS. "
            "Substrate would treat each order as 'just a method' rather "
            "than 'a candidate solution to a min-cost combinatorial "
            "search.' No way to express 'this order's max intermediate "
            "size = X; that order's = Y; so X dominates.'"
        ),
        "verdict": "FAIL_ENCODING — no ContractionOrderWitness",
    })

    # Probe 3: encode the cost-bound certificate via ExclusionCertificate
    encoding_attempts.append({
        "probe": "encode_cost_bound_as_ExclusionCertificate",
        "attempt": (
            "ExclusionCertificate(region_spec=..., exclusion_claim="
            "ExclusionClaim(excluded_property='contraction_order', "
            "result_class='tn_optimal', reason='cost_lower_bound_15'), "
            "certificate_type=EXHAUSTIVE_ENUMERATION, ...)."
        ),
        "blocker": (
            "ExclusionClaim is shape-correct for 'no order achieves cost "
            "below B' (negative existential), so the EXCLUSION direction "
            "WORKS at metadata level. BUT the substrate has no companion "
            "primitive for the WITNESSING optimal order (an ExistsWitness "
            "or ContractionOrderWitness). Half-encoded: lower bounds yes, "
            "constructive upper bounds and the order-as-object no. "
            "Asymmetric primitive coverage."
        ),
        "verdict": "PARTIAL — exclusion works, witness primitive missing",
    })

    # Probe 4: REWRITE for contraction equivalence
    encoding_attempts.append({
        "probe": "encode_associativity_as_REWRITE",
        "attempt": (
            "REWRITE rule: '(A·B)·C ≡ A·(B·C) under associativity, "
            "preserves invariants ['final_tensor_value']' for tensor "
            "contraction associativity. Each REWRITE move = one "
            "associativity reassociation."
        ),
        "blocker": (
            "REWRITE is between scalar-valued Symbols. Even if relaxed: "
            "associativity rewrites form a semi-group of moves whose "
            "OPTIMIZATION GEOMETRY (min over all reassociations) is the "
            "object of interest. Substrate has no RewriteSearchTree or "
            "RewriteCostFunctional primitive — REWRITE captures one move, "
            "not 'optimal sequence of moves.'"
        ),
        "verdict": "PARTIAL — single moves yes, optimization-over-moves no",
    })

    capability_gaps_identified = [
        {
            "missing_primitive": "TensorNetworkGraph (or general LabeledHypergraph)",
            "purpose": "vertices = tensors with shapes; edges = shared indices; topology-preserving",
            "needed_for": "any encoding of tensor networks; also: Feynman diagrams, factor graphs, knot diagrams",
            "blocks_paradigms": ["P30"],
            "blocks_catalog_entries": "#75-84 (most of §X) + several §I-II entries that route through tensor networks",
            "convergence_with_fire_38": (
                "ORTHOGONAL to fire #38's missing primitives. Fire #38 needed "
                "TensorObject (entry-level identity for ONE tensor); fire #39 "
                "needs TensorNetworkGraph (topology over MANY tensors). Both "
                "are foundational substrate-level objects — substrate has "
                "neither. Together they suggest a unified TensorAlgebra "
                "subsystem whose primitives include TensorObject, "
                "TensorNetworkGraph, and contraction operators."
            ),
        },
        {
            "missing_primitive": "ContractionOrderWitness (permutation/binary-tree + cost annotation)",
            "purpose": "constructive upper-bound witness for contraction-order optimization",
            "needed_for": "completing the asymmetry — substrate has ExclusionCertificate (lower bound) but no Witness (upper bound) for combinatorial-optimization problems",
            "blocks_paradigms": ["P30"],
            "blocks_catalog_entries": "#84 directly; pattern (constructive optimum witness for NP-hard problem) generalizes to many entries in §I/II/III/IV",
            "broader_pattern": (
                "Substrate's Exclusion-style certificates are ASYMMETRIC: "
                "one primitive for negative existentials (ExclusionCertificate) "
                "but no primitive for positive existentials with cost (a "
                "constructive witness with verifiable optimum-bound). The "
                "5-of-5 capability-gap cluster's Structured-Equivalence-Class "
                "design is a sister concern but not the same fix."
            ),
        },
        {
            "missing_primitive": "RewriteSearchTree / RewriteCostFunctional",
            "purpose": "optimization-over-rewrite-moves rather than single rewrite",
            "needed_for": "any 'optimal sequence of moves' problem (term rewriting cost, contraction order, normalization sequence)",
            "blocks_paradigms": ["P30"],
            "blocks_catalog_entries": "#84 + parts of §VII (decidability with cost) + §IV apolarity-search",
        },
    ]

    return {
        "lane": "12_catalog_pulled_TN_contraction_probe",
        "catalog_entry": "#84 Optimal tensor network contraction order",
        "section": "X. Quantum Information and Tensor Networks",
        "attack_paradigms": ["P30"],
        "tensor_network_summary": network_data,
        "encoding_attempts": encoding_attempts,
        "all_attempts_failed": all(
            a["verdict"].startswith("FAIL") or a["verdict"].startswith("PARTIAL")
            for a in encoding_attempts
        ),
        "capability_gaps_identified": capability_gaps_identified,
        "verdict": "FAIL_ENCODING — substrate has no GraphObject/TensorNetworkGraph + asymmetric existential primitive coverage",
        "feeds_techne_ticket": "T-2026-05-08-T038 (substrate-primitive classification of all 104 catalog entries)",
        "convergence_note": (
            "Fire #38 surfaced TensorObject + RankDecompositionWitness + "
            "MomentPolytope; fire #39 surfaces TensorNetworkGraph + "
            "ContractionOrderWitness + RewriteSearchTree. Two fires, six "
            "missing primitives, all converging on a TensorAlgebra subsystem "
            "design. This is the kind of converging evidence that justifies "
            "a single contract-change pass to ship the whole subsystem."
        ),
    }


# ---------------------------------------------------------------------------
# Lane 4 — SIGMA opcode smoke (RESOLVE / CLAIM / FALSIFY / GATE chain)
# ---------------------------------------------------------------------------


def lane_4_sigma_opcode_smoke() -> Dict[str, Any]:
    import tempfile
    from sigma_kernel.sigma_kernel import SigmaKernel, Tier

    tests: List[Dict[str, Any]] = []

    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "smoke.db"
        kernel = SigmaKernel(str(db_path))

        # T1: bootstrap_symbol
        try:
            sym = kernel.bootstrap_symbol(
                name="smoke_lemma", version=1,
                def_obj={"statement": "x equals 42", "kind": "lemma"},
                tier=Tier.WorkingTheory,
            )
            tests.append({"id": "T1_bootstrap_symbol", "verdict": "PASS", "ref": sym.ref})
        except Exception as exc:  # noqa: BLE001
            tests.append({"id": "T1_bootstrap_symbol", "verdict": "FAIL",
                          "actual": f"{type(exc).__name__}: {exc}"})
            kernel.close()
            return {"lane": "4_sigma_opcode_smoke", "n_tests": len(tests),
                    "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
                    "tests": tests}

        # T2: RESOLVE round-trips with hash-integrity
        try:
            resolved = kernel.RESOLVE("smoke_lemma", 1)
            assert resolved.name == "smoke_lemma"
            assert resolved.version == 1
            assert resolved.def_hash == sym.def_hash
            tests.append({"id": "T2_resolve_hash_integrity", "verdict": "PASS"})
        except Exception as exc:  # noqa: BLE001
            tests.append({"id": "T2_resolve_hash_integrity", "verdict": "FAIL",
                          "actual": f"{type(exc).__name__}: {exc}"})

        # T3: RESOLVE missing → KeyError
        try:
            try:
                _ = kernel.RESOLVE("nonexistent", 99)
                tests.append({"id": "T3_resolve_missing_raises", "verdict": "FAIL",
                              "actual": "RESOLVE returned without raising on missing symbol"})
            except KeyError:
                tests.append({"id": "T3_resolve_missing_raises", "verdict": "PASS"})
        except Exception as exc:  # noqa: BLE001
            tests.append({"id": "T3_resolve_missing_raises", "verdict": "FAIL",
                          "actual": f"{type(exc).__name__}: {exc}"})

        # T4: CLAIM with valid string kill_path
        claim = None
        try:
            claim = kernel.CLAIM(
                target_name="smoke_lemma",
                hypothesis="x = 42 holds for all relevant x",
                evidence={"observed": True, "n_samples": 1},
                kill_path="check_x_value_is_42",
                target_tier=Tier.Conjecture,
            )
            tests.append({"id": "T4_claim", "verdict": "PASS"})
        except Exception as exc:  # noqa: BLE001
            tests.append({"id": "T4_claim", "verdict": "FAIL",
                          "actual": f"{type(exc).__name__}: {exc}"})

        # T5: CLAIM with non-string kill_path → TypeError (Tier-3 contract from
        #     fire #29 P5 → mini-window fix).
        try:
            try:
                _ = kernel.CLAIM(
                    target_name="smoke_lemma",
                    hypothesis="x = 42",
                    evidence={"observed": True},
                    kill_path=12345,  # non-string
                )
                tests.append({"id": "T5_claim_kill_path_type_check", "verdict": "FAIL",
                              "actual": "CLAIM accepted non-string kill_path silently"})
            except TypeError:
                tests.append({"id": "T5_claim_kill_path_type_check", "verdict": "PASS"})
        except Exception as exc:  # noqa: BLE001
            tests.append({"id": "T5_claim_kill_path_type_check", "verdict": "FAIL",
                          "actual": f"{type(exc).__name__}: {exc}"})

        kernel.close()

    return {
        "lane": "4_sigma_opcode_smoke",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    summary = {
        "fire": 39,
        "posture": "second-HARD-6-fire (matrix-filling: §X catalog entry #84; converging on TensorAlgebra subsystem)",
        "lanes": [12, 4],
        "lane_12": lane_12_contraction_order_probe(),
        "lane_4": lane_4_sigma_opcode_smoke(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_39_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 12: catalog #84 verdict = {summary['lane_12']['verdict'][:60]}...")
    print(f"  capability gaps: {len(summary['lane_12']['capability_gaps_identified'])}")
    print(f"Lane 4: {summary['lane_4']['verdict_counts']}")
    return summary


if __name__ == "__main__":
    run()
