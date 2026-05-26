"""Generator 1: Intersection Composer.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 1.

Was Erebos's MVP (v0.7); factored into plugin form in v0.8.

Erebos Implementation Spec:
- Input / Provenance: Two substantive (PROMOTED or UNVERIFIED-with-
  battery-output) claims from Stygian + Pollux ledgers.
- Transformation: Extracts the subject of Claim A and applies the
  constraint/filter of Claim B; surfaces Hecate cross-gen patterns
  as context.
- Output Claim: 'Pattern X (from A) holds when restricted to Subset
  Y (from B)'.
- Falsification Route: Stygian samples objects exclusively within
  Subset Y and runs the standard battery for Pattern X.
- Expected Kill Pattern: 'base_rate_failure' (the pattern holds no
  better in Subset Y than in the global population).
- Loader Feasibility: EASY (charon-state: Tier S).
"""
from __future__ import annotations

from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


class IntersectionGenerator:
    id = "g01_intersection"
    name = "Intersection Composer"
    spec_phase = 1
    feasibility_tier = "S"
    reasoning_tier = "R3"  # DNA P10: abstraction (MDL compression of two claims)
    expected_kill_pattern = "base_rate_failure"

    def applicable(self, state: SwarmState) -> bool:
        if not state.stygian_substantive or not state.pollux_substantive:
            return False
        # At least one (S, P) pair must be uncomposed
        for s in state.stygian_substantive:
            for p in state.pollux_substantive:
                key = f"{self.id}|{s.get('record_id','')}|{p.get('record_id','')}"
                if key not in state.tried_pairs:
                    return True
        return False

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        # Pick highest-priority uncomposed pair (newest first)
        s_sorted = sorted(
            state.stygian_substantive,
            key=lambda r: r.get("emitted_at", ""), reverse=True,
        )
        p_sorted = sorted(
            state.pollux_substantive,
            key=lambda r: r.get("emitted_at", ""), reverse=True,
        )
        for s in s_sorted:
            for p in p_sorted:
                key = f"{self.id}|{s.get('record_id','')}|{p.get('record_id','')}"
                if key in state.tried_pairs:
                    continue
                return self._build_claim(s, p, state)
        return None

    def _build_claim(
        self, s_row: dict, p_row: dict, state: SwarmState
    ) -> ComposedClaim:
        s_claim = s_row.get("canonical_claim_text", "")
        s_problem_id = (s_row.get("claim_payload") or {}).get("problem_id", "?")
        p_pair_name = (p_row.get("claim_payload") or {}).get("pair_name", "?")
        p_subset_a = (p_row.get("extras") or {}).get("subset_a_desc", "?")
        p_subset_b = (p_row.get("extras") or {}).get("subset_b_desc", "?")
        crossgen = state.hecate_crossgen_canonical[:5] if state.hecate_crossgen_canonical else []

        composed_id = f"EREBOS-G01-{s_problem_id}-x-{p_pair_name}"
        composition_text = (
            f"Composed intersection-claim {composed_id}: "
            f"The structural claim from Stygian's substantive verdict on "
            f"`{s_problem_id}` (\"{s_claim[:200]}\") is hypothesized to "
            f"hold when restricted to the Pollux-PROMOTED subset pair "
            f"`{p_pair_name}` (subset A: {p_subset_a}; subset B: "
            f"{p_subset_b}). The substantive test is whether the "
            f"restricted-subset version of the Stygian claim survives "
            f"its own v10 battery -- if yes, the intersection is "
            f"non-trivial and the two parent observations have a "
            f"shared structural basis. If no, the intersection is "
            f"coincidental and the parent verdicts were independent."
        )
        if crossgen:
            composition_text += (
                f" Hecate cross-generator context: top canonical patterns "
                f"this tick: {crossgen}."
            )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "stygian_record_id": s_row.get("record_id"),
                "stygian_problem_id": s_problem_id,
                "pollux_record_id": p_row.get("record_id"),
                "pollux_pair_name": p_pair_name,
                "hecate_crossgen_patterns": crossgen,
            },
            transformation_description=(
                "Extract subject from Stygian claim; restrict to Pollux "
                "PROMOTED pair's subset(s); attach Hecate crossgen context."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                "Stygian samples objects exclusively within the Pollux "
                "subset and runs the standard battery for the Stygian "
                "claim's distribution / correlation shape. "
                "Composition-aware loader (v0.11+) required for actual "
                "execution; until then, claim short-circuits with "
                "stygian_erebos_composed_loader_pending."
            ),
            expected_kill_pattern="base_rate_failure",
            loader_feasibility_note=(
                "EASY (Tier S): reuses parent Stygian + Pollux loaders "
                "with compounded SQL/JSON filter. The composition-aware "
                "loader needs only to intersect the two parent value "
                "sets, no new battery primitives required."
            ),
            parent_record_ids=[
                s_row.get("record_id", ""),
                p_row.get("record_id", ""),
            ],
            composition_payload={
                "stygian_claim_text": s_claim,
                "pollux_corr_raw": (p_row.get("kill_vector") or {}).get("corr_raw"),
                "pollux_corr_norm": (p_row.get("kill_vector") or {}).get("corr_norm"),
                "pollux_subset_a": (p_row.get("claim_payload") or {}).get("subset_a"),
                "pollux_subset_b": (p_row.get("claim_payload") or {}).get("subset_b"),
            },
            extras={"crossgen_context": crossgen},
        )
