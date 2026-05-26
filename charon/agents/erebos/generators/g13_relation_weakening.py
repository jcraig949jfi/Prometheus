"""Generator 13: Relation-Weakening (predicate-lattice descent).

Per pivot/erebos_g13_relation_weakening_research_2026-05-27.md.
Cousin to G03 (arithmetic-operator weakening); G13 focuses
strictly on LOGICAL PREDICATES via the shared lattice in
_predicate_lattice.py.

Erebos Implementation Spec:
- Input / Provenance: A REJECTED or substantively-UNVERIFIED claim
  whose text contains a detectable predicate at lattice-rank >= 2.
- Transformation: Walk one rank DOWN the predicate lattice; emit
  the parent claim with the predicate weakened.
- Output Claim: "Parent's relation, but with predicate weakened
  from <rank N> to <rank N-1>, may still hold at the same boundary."
- Falsification Route: Standard Stygian battery on the weakened
  claim.
- Expected Kill Pattern: predicate_weakened_to_triviality (the
  weakened version is trivially true for random pairs).
- Loader Feasibility: Tier A. String substitution MVP.
- Reasoning Tier: R3 (abstraction by predicate-relaxation).
"""
from __future__ import annotations

from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)
from charon.agents.erebos.generators._predicate_lattice import (
    find_strongest_predicate,
    tier_below,
)


class RelationWeakeningGenerator:
    id = "g13_relation_weakening"
    name = "Relation Weakening"
    spec_phase = 3
    feasibility_tier = "A"
    reasoning_tier = "R3"
    expected_kill_pattern = "predicate_weakened_to_triviality"

    def _parent_pool(self, state: SwarmState) -> list[dict]:
        """G13 prefers REJECTED/UNVERIFIED Stygian rows (have a
        kill-direction). Erebos compositions also acceptable."""
        return (
            list(state.stygian_substantive)
            + list(state.erebos_self_ledger)
        )

    def _candidate_for_row(self, row: dict, state: SwarmState) -> Optional[dict]:
        """Find an uncomposed (parent, current_tier->weakened_tier)
        for this row. Returns dict with current+weakened tiers or None."""
        text = row.get("canonical_claim_text", "")
        cur = find_strongest_predicate(text)
        if cur is None:
            return None
        weaker = tier_below(cur)
        if weaker is None:
            return None  # already at weakest
        rid = row.get("record_id", "")
        key = f"{self.id}|{rid}|{cur.canonical_name}->{weaker.canonical_name}"
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
            f"EREBOS-G13-weaken_{cur.canonical_name}_to_{weaker.canonical_name}-{parent_gen}_{rid[:12]}"
        )

        composition_text = (
            f"Relation-weakening claim {composed_id}: "
            f"the parent claim from generator `{parent_gen}` "
            f"(\"{parent_text[:200]}\") uses predicate "
            f"`{cur.human_form}` (rank {cur.rank}). The weakened "
            f"version replaces this with `{weaker.human_form}` "
            f"(rank {weaker.rank}). Hypothesis: the weakened "
            f"version either (a) holds trivially -- evidence the "
            f"weakening went past the substantive content; or "
            f"(b) holds non-trivially at the same boundary -- "
            f"evidence the predicate-relaxation found additional "
            f"structure the parent claim missed."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "parent_record_id": rid,
                "parent_generator_id": parent_gen,
                "parent_emitted_at": parent_row.get("emitted_at"),
                "current_predicate_rank": cur.rank,
                "current_predicate_name": cur.canonical_name,
                "weakened_predicate_rank": weaker.rank,
                "weakened_predicate_name": weaker.canonical_name,
            },
            transformation_description=(
                f"Detect strongest predicate in parent text "
                f"(`{cur.canonical_name}` rank {cur.rank}); descend "
                f"one rank to `{weaker.canonical_name}` rank "
                f"{weaker.rank}; emit weakened candidate-claim."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Stygian battery on the weakened claim. "
                f"Composition-aware loader applies the substitution "
                f"`{cur.weakening_replacement}` -> "
                f"`{weaker.weakening_replacement}` to parent's "
                f"predicate context, then re-runs the parent's "
                f"distribution / correlation test shape. If the "
                f"weakened test trivially passes for random subsets, "
                f"kill_pattern = predicate_weakened_to_triviality. "
                f"Currently short-circuits at "
                f"stygian_erebos_composed_loader_pending until task #37 "
                f"(composition-aware loader) ships per-G13 support."
            ),
            expected_kill_pattern="predicate_weakened_to_triviality",
            loader_feasibility_note=(
                "EASY (Tier A): string-substitution on canonical_claim "
                "_text via the shared _predicate_lattice. Composition-"
                "aware loader needs only to apply the same substitution "
                "to the parent's predicate-check function before re-"
                "running the test."
            ),
            parent_record_ids=[rid],
            composition_payload={
                "current_predicate": cur.canonical_name,
                "weakened_predicate": weaker.canonical_name,
                "current_rank": cur.rank,
                "weakened_rank": weaker.rank,
                "predicate_lattice_version": "v0.9",
            },
            extras={"direction": "weaken"},
        )
