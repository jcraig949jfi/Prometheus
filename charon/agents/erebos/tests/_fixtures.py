"""Shared test fixtures for Erebos generator plugin tests.

Per DNA P3 (TDD-first). Each generator test imports from here for
common inputs (sample Stygian rows, sample Pollux rows, sample
Hecate crossgen patterns).
"""
from __future__ import annotations

from charon.agents.erebos.generators._base import SwarmState


# Minimal substantive Stygian rows for testing
def sample_stygian_rows() -> list[dict]:
    return [
        {
            "record_id": "stygian_test_001",
            "canonical_claim_text": (
                "BL-C-001 / Lehmer's conjecture: M(P) >= M_Lehmer "
                "for non-cyclotomic monic integer polynomials."
            ),
            "verdict": "UNVERIFIED",
            "kill_pattern": None,
            "kill_vector": {
                "tests": {
                    "F15": {"verdict": "DEVIATES_FROM_LOGNORMAL"},
                    "F16": {"verdict": "SIGNIFICANTLY_DIFFERENT"},
                    "F18": {"verdict": "STABLE"},
                    "F20": {"verdict": "REPRESENTATION_DEPENDENT"},
                },
                "overall": {"verdict": "POSSIBLE", "tier": "A"},
            },
            "generator_id": "stygian",
            "emitted_at": "2026-05-26T00:00:00+00:00",
            "claim_payload": {"problem_id": "BL-C-001"},
            "extras": {},
        },
        {
            "record_id": "stygian_test_002",
            "canonical_claim_text": "BL-C-002 / BSD rank distribution",
            "verdict": "REJECTED",
            "kill_pattern": "stygian_f17_failed",
            "kill_vector": {
                "tests": {
                    "F15": {"verdict": "DEVIATES_FROM_LOGNORMAL"},
                    "F17": {"verdict": "SUSPECT"},
                    "F24": {"verdict": "STABLE"},
                },
                "overall": {"verdict": "FAIL", "tier": "A"},
            },
            "generator_id": "stygian",
            "emitted_at": "2026-05-26T00:01:00+00:00",
            "claim_payload": {"problem_id": "BL-C-002"},
            "extras": {},
        },
    ]


def sample_pollux_rows() -> list[dict]:
    return [
        {
            "record_id": "pollux_test_001",
            "canonical_claim_text": (
                "Pollux scan deg10_vs_deg12: spearman raw=1.0, "
                "normalized=-0.22"
            ),
            "verdict": "REJECTED",
            "kill_pattern": "pollux_sign_flips_under_normalization",
            "kill_vector": {
                "corr_raw": 1.0,
                "corr_norm": -0.22,
                "n_paired": 50,
            },
            "generator_id": "pollux",
            "emitted_at": "2026-05-26T00:02:00+00:00",
            "claim_payload": {"pair_name": "deg10_vs_deg12"},
            "extras": {
                "subset_a_desc": "Mossinghoff degree-10",
                "subset_b_desc": "Mossinghoff degree-12",
            },
        },
        {
            "record_id": "pollux_test_002",
            "canonical_claim_text": (
                "Pollux scan salem_vs_pisot: spearman raw=0.9, "
                "normalized=0.85"
            ),
            "verdict": "PROMOTED",
            "kill_pattern": "pollux_correlation_survives_normalization",
            "kill_vector": {
                "corr_raw": 0.9,
                "corr_norm": 0.85,
                "n_paired": 100,
            },
            "generator_id": "pollux",
            "emitted_at": "2026-05-26T00:03:00+00:00",
            "claim_payload": {"pair_name": "salem_vs_pisot"},
            "extras": {
                "subset_a_desc": "Mossinghoff Salem-class",
                "subset_b_desc": "Mossinghoff non-Salem",
            },
        },
    ]


def sample_crossgen_patterns() -> list[str]:
    return [
        "method_triangulated_reject",
        "detrended_correlation_below_threshold",
        "relation_equal_violated",
        "hunter_found_counterexample",
    ]


def baseline_swarm_state() -> SwarmState:
    """A SwarmState that exercises all four input sources, with
    nothing in tried_pairs."""
    return SwarmState(
        stygian_substantive=sample_stygian_rows(),
        pollux_substantive=sample_pollux_rows(),
        hecate_crossgen_canonical=sample_crossgen_patterns(),
        erebos_self_ledger=[],
        tried_pairs=set(),
        tick_counter=1,
    )


def empty_swarm_state() -> SwarmState:
    """All-empty state for testing applicable() False cases."""
    return SwarmState()
