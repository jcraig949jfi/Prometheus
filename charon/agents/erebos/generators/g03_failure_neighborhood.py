"""Generator 3: Failure-Neighborhood (arithmetic-operator weakening).

Per pivot/erebos_g03_failure_neighborhood_research_2026-05-26.md
+ pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 1.

Sister to G13 (logical-predicate weakening). G03 focuses on
ARITHMETIC comparison operators: =, <, >, <=, >=, !=. Walks them
downward (toward more permissive) to find the largest still-true
relaxation.

Erebos Implementation Spec:
- Input / Provenance: REJECTED claim text containing a detectable
  arithmetic comparison.
- Transformation: substitute the strictest detected comparison
  with one step weaker per arithmetic ladder.
- Output Claim: "Original failed at <strict_op>; weakened to
  <weak_op> may still hold."
- Falsification Route: Stygian battery on weakened claim.
- Expected Kill Pattern: boundary_collapse (weakened too permissive;
  trivially true for random pairs).
- Loader Feasibility: Tier B (string-substitution MVP).
- Reasoning Tier: R3 (abstraction by relaxing exact-comparison
  to interval-comparison).
"""
from __future__ import annotations

import re
from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


# Arithmetic-comparison ladder.
# Order: strictest -> weakest. G03 walks downward by one rank.
ARITHMETIC_LADDER: list[dict] = [
    # rank 5: exact arithmetic equality
    {"rank": 5, "name": "arith_equality",
     "regex": r"(?<![<>=!])=(?!=)|\b(equals?|is equal to)\b",
     "human": "= (exact)", "weakened_replacement": "within tolerance epsilon"},
    # rank 4: strict inequality
    {"rank": 4, "name": "arith_strict_inequality",
     "regex": r"<(?!=)|>(?!=)|\b(strictly less than|strictly greater than)\b",
     "human": "< or > (strict)", "weakened_replacement": "<= or >= (non-strict)"},
    # rank 3: non-strict inequality
    {"rank": 3, "name": "arith_nonstrict_inequality",
     "regex": r"<=|>=|\b(at most|at least|less than or equal|greater than or equal)\b",
     "human": "<= or >= (non-strict)", "weakened_replacement": "bounded by constant K"},
    # rank 2: bounded by constant
    {"rank": 2, "name": "arith_bounded",
     "regex": r"\b(bounded by|bounded above by|bounded below by)\b",
     "human": "bounded by K", "weakened_replacement": "asymptotically bounded"},
    # rank 1: asymptotic / O()
    {"rank": 1, "name": "arith_asymptotic",
     "regex": r"\bO\(|\bo\(|\bbig-O\b|\bbig O\b|\basymptotic|\basymptotically\b",
     "human": "asymptotic / O()", "weakened_replacement": "exists (trivially)"},
]


def find_strictest_arith(text: str) -> Optional[dict]:
    """Scan text for arithmetic operators; return the highest-rank
    one detected. None if no match."""
    text_lower = (text or "").lower()
    matched = []
    for tier in ARITHMETIC_LADDER:
        if re.search(tier["regex"], text_lower):
            matched.append(tier)
    if not matched:
        return None
    return max(matched, key=lambda t: t["rank"])


def arith_below(tier: dict) -> Optional[dict]:
    """Return the tier one rank weaker, or None if at bottom."""
    target_rank = tier["rank"] - 1
    for t in ARITHMETIC_LADDER:
        if t["rank"] == target_rank:
            return t
    return None


class FailureNeighborhoodGenerator:
    id = "g03_failure_neighborhood"
    name = "Failure Neighborhood"
    spec_phase = 1
    feasibility_tier = "B"
    reasoning_tier = "R3"
    expected_kill_pattern = "boundary_collapse"

    def _parent_pool(self, state: SwarmState) -> list[dict]:
        """G03 prefers REJECTED Stygian rows (have a kill direction)
        + REJECTED Erebos compositions."""
        out = []
        for r in (list(state.stygian_substantive) + list(state.erebos_self_ledger)):
            if r.get("verdict") == "REJECTED":
                out.append(r)
        return out

    def _candidate_for_row(self, row: dict, state: SwarmState) -> Optional[dict]:
        text = row.get("canonical_claim_text", "")
        cur = find_strictest_arith(text)
        if cur is None:
            return None
        weaker = arith_below(cur)
        if weaker is None:
            return None
        rid = row.get("record_id", "")
        key = f"{self.id}|{rid}|{cur['name']}->{weaker['name']}"
        if key in state.tried_pairs:
            return None
        return {"current": cur, "weaker": weaker}

    def applicable(self, state: SwarmState) -> bool:
        for r in self._parent_pool(state):
            if self._candidate_for_row(r, state) is not None:
                return True
        return False

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        pool = sorted(
            self._parent_pool(state),
            key=lambda r: r.get("emitted_at", ""), reverse=True,
        )
        for r in pool:
            cand = self._candidate_for_row(r, state)
            if cand is not None:
                return self._build_claim(r, cand)
        return None

    def _build_claim(self, parent_row: dict, cand: dict) -> ComposedClaim:
        cur = cand["current"]
        weaker = cand["weaker"]
        rid = parent_row.get("record_id", "?")
        parent_text = parent_row.get("canonical_claim_text", "")
        parent_gen = parent_row.get("generator_id", "?")

        composed_id = (
            f"EREBOS-G03-weaken_{cur['name']}_to_{weaker['name']}"
            f"-{parent_gen}_{rid[:12]}"
        )

        composition_text = (
            f"Failure-neighborhood claim {composed_id}: "
            f"the parent claim from `{parent_gen}` "
            f"(\"{parent_text[:200]}\") was REJECTED using arithmetic "
            f"operator `{cur['human']}` (rank {cur['rank']}). The "
            f"failure-neighborhood version weakens this to "
            f"`{weaker['human']}` (rank {weaker['rank']}; replacement "
            f"`{cur['weakened_replacement']}`). Hypothesis: the "
            f"weakened relation either (a) holds trivially for random "
            f"pairs (boundary_collapse -- the relaxation went too far), "
            f"or (b) holds non-trivially at the same boundary -- "
            f"evidence that the kill_pattern indicated a strictness "
            f"issue, not absence of structure."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "parent_record_id": rid,
                "parent_generator_id": parent_gen,
                "parent_emitted_at": parent_row.get("emitted_at"),
                "parent_kill_pattern": parent_row.get("kill_pattern"),
                "current_arith_op": cur["name"],
                "current_rank": cur["rank"],
                "weakened_arith_op": weaker["name"],
                "weakened_rank": weaker["rank"],
            },
            transformation_description=(
                f"Detect strictest arithmetic operator in parent text "
                f"(`{cur['name']}` rank {cur['rank']}); descend one "
                f"rank to `{weaker['name']}`; emit weakened candidate-"
                f"claim. Sister to G13 logical-predicate weakening; "
                f"G03 operates on arithmetic comparisons specifically."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Stygian battery on the weakened claim. "
                f"Composition-aware loader substitutes "
                f"`{cur['weakened_replacement']}` for the strict "
                f"operator; re-runs the parent's test. If the weakened "
                f"version trivially passes (boundary_collapse), the "
                f"relaxation was too aggressive. If it produces a "
                f"meaningful PROMOTED/REJECTED verdict, the weakened "
                f"form may be the maximal-true neighborhood of the "
                f"original failed claim."
            ),
            expected_kill_pattern="boundary_collapse",
            loader_feasibility_note=(
                "Tier B: string substitution at the arithmetic-operator "
                "level. Future v0.12+ AST mutation gives more rigorous "
                "support but the string-substitution MVP suffices for "
                "current claim formats."
            ),
            parent_record_ids=[rid],
            composition_payload={
                "current_arith_op": cur["name"],
                "weakened_arith_op": weaker["name"],
                "weakened_replacement_text": cur["weakened_replacement"],
                "arith_ladder_version": "v0.11",
            },
            extras={"direction": "weaken_arithmetic"},
        )
