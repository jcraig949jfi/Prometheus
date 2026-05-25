"""
Icarus tier ladder -- FROZEN R0-R12 definitions.

Per spec v0.2 sect 5 ("Other accepted changes" #5): tier falsification tests
are versioned and frozen alongside the cycle code. This module is FROZEN --
Icarus must never modify it. Only James does.

The ladder definitions and their falsification tests are the SOURCE OF TRUTH
for tier promotion. Each tier carries a falsification test specification
(human-readable) and a pointer to the concrete test module.

Reference: D:\\Prometheus\\pivot\\reasoning_ladder_v01_2026-05-24.md sect "The ladder"
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TierDef:
    tier_id: str
    name: str
    description: str
    falsification_test: str
    test_module: str  # importable path
    # Tier-promotion gate parameters (per spec v0.2 §"high-ceremony tier promotion")
    promotion_gate_min_cycles: int = 5
    promotion_gate_min_perturbation_trials: int = 100
    promotion_gate_p_threshold: float = 0.01


TIER_LADDER: list[TierDef] = [
    TierDef(
        tier_id="R0",
        name="Pattern response",
        description="Surface form; fails first paraphrase.",
        falsification_test=(
            "Re-test on a paraphrased version. If accuracy drops > 50%, "
            "you're at R0."
        ),
        test_module="tests.test_tier_R0_falsification",
    ),
    TierDef(
        tier_id="R1",
        name="Local operation",
        description="Applies one known operation correctly.",
        falsification_test=(
            "Apply to a structurally-identical problem with variables "
            "renamed. R0 fails this; R1 passes."
        ),
        test_module="tests.test_tier_R1_falsification",
    ),
    TierDef(
        tier_id="R2",
        name="Multi-step execution",
        description="Chains operations when order is supplied.",
        falsification_test=(
            "Insert one irrelevant distractor step. R2 should still "
            "complete; R1 may drop."
        ),
        test_module="tests.test_tier_R2_falsification",
    ),
    TierDef(
        tier_id="R3",
        name="Constraint maintenance",
        description="Tracks multiple constraints; rejects inconsistent candidates.",
        falsification_test=(
            "Inject an inconsistent constraint. R3 should detect; R2 may "
            "produce a contradiction."
        ),
        test_module="tests.test_tier_R3_falsification",
    ),
    TierDef(
        tier_id="R4",
        name="Strategy selection",
        description="Chooses among methods based on problem structure.",
        falsification_test=(
            "Give a problem solvable by >=2 methods. R4 picks a method "
            "appropriate to structure; R3 picks arbitrarily."
        ),
        test_module="tests.test_tier_R4_falsification",
    ),
    TierDef(
        tier_id="R5",
        name="Counterfactual control",
        description="Holds branches; answers 'what changes if X changes'.",
        falsification_test=(
            "Ask 'what would happen if [premise] were reversed?' R5 "
            "maintains branches; R4 collapses to one answer."
        ),
        test_module="tests.test_tier_R5_falsification",
    ),
    TierDef(
        tier_id="R6",
        name="Error detection + local repair",
        description="Finds and fixes a wrong step.",
        falsification_test=(
            "Provide a partially-wrong proof and ask for fix. R6 localizes "
            "the error; R5 may rewrite the whole thing."
        ),
        test_module="tests.test_tier_R6_falsification",
    ),
    TierDef(
        tier_id="R7",
        name="Global plan revision",
        description="Abandons a failing strategy and picks a new one.",
        falsification_test=(
            "Set a problem where the obvious approach fails partway. R7 "
            "abandons and tries new strategy; R6 keeps repairing locally."
        ),
        test_module="tests.test_tier_R7_falsification",
    ),
    TierDef(
        tier_id="R8",
        name="Representation shift",
        description="Re-encodes the problem into a better formalism.",
        falsification_test=(
            "Set a problem easier in a non-default representation. R8 "
            "switches representation; R7 stays in the original."
        ),
        test_module="tests.test_tier_R8_falsification",
    ),
    TierDef(
        tier_id="R9",
        name="Compositional synthesis",
        description="Load-bearing composition that beats any individual part.",
        falsification_test=(
            "Single-primitive baseline test: composition must beat the "
            "best of its constituent primitives by a meaningful margin."
        ),
        test_module="tests.test_tier_R9_falsification",
    ),
    TierDef(
        tier_id="R10",
        name="Epistemic self-modeling",
        description="Knows what it knows / lacks / would need to test.",
        falsification_test=(
            "Set a problem with deliberately ambiguous premises. R10 "
            "identifies the missing variable and asks; R9 picks an "
            "interpretation and proceeds."
        ),
        test_module="tests.test_tier_R10_falsification",
    ),
    TierDef(
        tier_id="R11",
        name="Substrate formation",
        description="Extracts reusable structure from solved and failed attempts.",
        falsification_test=(
            "Solve a sequence of related problems. R11 produces reusable "
            "lemmas / templates / abstractions across the sequence; R10 "
            "solves each independently."
        ),
        test_module="tests.test_tier_R11_falsification",
    ),
    TierDef(
        tier_id="R12",
        name="Open-ended research behavior",
        description="Generates, tests, repairs, accumulates claims under falsification.",
        falsification_test=(
            "Run a sequence of falsification cycles where the system's own "
            "claims are challenged. R12 generates new testable claims that "
            "survive; R11 may stop at first defensible answer."
        ),
        test_module="tests.test_tier_R12_falsification",
    ),
]


_TIER_BY_ID = {t.tier_id: t for t in TIER_LADDER}


def get_tier(tier_id: str) -> TierDef:
    if tier_id not in _TIER_BY_ID:
        raise ValueError(f"unknown tier: {tier_id} (valid: {list(_TIER_BY_ID)})")
    return _TIER_BY_ID[tier_id]


def next_tier(tier_id: str) -> TierDef | None:
    idx = next((i for i, t in enumerate(TIER_LADDER) if t.tier_id == tier_id), -1)
    if idx == -1 or idx + 1 >= len(TIER_LADDER):
        return None
    return TIER_LADDER[idx + 1]


def prior_tier(tier_id: str) -> TierDef | None:
    idx = next((i for i, t in enumerate(TIER_LADDER) if t.tier_id == tier_id), -1)
    if idx <= 0:
        return None
    return TIER_LADDER[idx - 1]


def all_lower_tiers(tier_id: str) -> list[TierDef]:
    """All tiers below tier_id (for regression-test coverage per spec v0.2 #14)."""
    out: list[TierDef] = []
    for t in TIER_LADDER:
        if t.tier_id == tier_id:
            break
        out.append(t)
    return out
