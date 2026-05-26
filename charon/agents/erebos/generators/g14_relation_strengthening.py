"""Generator 14: Relation-Strengthening (predicate-lattice ascent).

Per pivot/erebos_g14_relation_strengthening_research_2026-05-27.md.
Inverse of G13; shares the predicate lattice from _predicate_lattice.py.

Erebos Implementation Spec:
- Input / Provenance: A PROMOTED or substantively-UNVERIFIED claim
  whose text contains a detectable predicate at lattice-rank <= 4.
- Transformation: Walk one rank UP the predicate lattice; emit the
  parent claim with the predicate strengthened.
- Output Claim: "Parent's relation, sharpened: the predicate
  strengthens from <rank N> to <rank N+1>."
- Falsification Route: Standard Stygian battery on strengthened
  claim.
- Expected Kill Pattern: predicate_strengthened_past_truth
  (the strengthened version fails; the weaker version was maximal-
  true).
- Loader Feasibility: Tier A.
- Reasoning Tier: R8 (open-ended conjecture formation: sharper
  hypothesis is a stronger conjecture).
"""
from __future__ import annotations

from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)
from charon.agents.erebos.generators._predicate_lattice import (
    find_weakest_predicate,
    tier_above,
)


class RelationStrengtheningGenerator:
    id = "g14_relation_strengthening"
    name = "Relation Strengthening"
    spec_phase = 3
    feasibility_tier = "A"
    reasoning_tier = "R8"
    expected_kill_pattern = "predicate_strengthened_past_truth"

    def _parent_pool(self, state: SwarmState) -> list[dict]:
        """G14 prefers PROMOTED claims (surviving). Pollux PROMOTED
        + Erebos compositions + any Stygian substantive row."""
        return (
            list(state.pollux_substantive)
            + list(state.erebos_self_ledger)
            + list(state.stygian_substantive)
        )

    def _candidate_for_row(self, row: dict, state: SwarmState) -> Optional[dict]:
        text = row.get("canonical_claim_text", "")
        cur = find_weakest_predicate(text)
        if cur is None:
            return None
        stronger = tier_above(cur)
        if stronger is None:
            return None  # already at strongest
        rid = row.get("record_id", "")
        key = f"{self.id}|{rid}|{cur.canonical_name}->{stronger.canonical_name}"
        if key in state.tried_pairs:
            return None
        return {"current": cur, "stronger": stronger}

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
        stronger = cand["stronger"]
        rid = parent_row.get("record_id", "?")
        parent_text = parent_row.get("canonical_claim_text", "")
        parent_gen = parent_row.get("generator_id", "?")

        composed_id = (
            f"EREBOS-G14-strengthen_{cur.canonical_name}_to_{stronger.canonical_name}-{parent_gen}_{rid[:12]}"
        )

        composition_text = (
            f"Relation-strengthening claim {composed_id}: "
            f"the parent claim from generator `{parent_gen}` "
            f"(\"{parent_text[:200]}\") uses predicate "
            f"`{cur.human_form}` (rank {cur.rank}). The strengthened "
            f"version replaces this with `{stronger.human_form}` "
            f"(rank {stronger.rank}). Hypothesis: the strengthened "
            f"version (a) still holds at the same boundary -- "
            f"evidence the parent claim was unnecessarily weak; or "
            f"(b) fails at the strengthened threshold -- evidence "
            f"the parent's weaker predicate was the maximal-true form."
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
                "strengthened_predicate_rank": stronger.rank,
                "strengthened_predicate_name": stronger.canonical_name,
            },
            transformation_description=(
                f"Detect weakest predicate in parent text "
                f"(`{cur.canonical_name}` rank {cur.rank}); ascend "
                f"one rank to `{stronger.canonical_name}` rank "
                f"{stronger.rank}; emit strengthened candidate-claim."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Stygian battery on the strengthened claim. "
                f"Composition-aware loader applies "
                f"`{cur.strengthening_replacement}` -> "
                f"`{stronger.strengthening_replacement}` to parent's "
                f"predicate context. If the strengthened version "
                f"fails on objects the parent claim passed, kill_pattern "
                f"= predicate_strengthened_past_truth. Currently "
                f"short-circuits at stygian_erebos_composed_loader_pending."
            ),
            expected_kill_pattern="predicate_strengthened_past_truth",
            loader_feasibility_note=(
                "EASY (Tier A): symmetric to G13 string-substitution "
                "in the opposite direction. Composition-aware loader "
                "reuses G13 infrastructure with opposite direction flag."
            ),
            parent_record_ids=[rid],
            composition_payload={
                "current_predicate": cur.canonical_name,
                "strengthened_predicate": stronger.canonical_name,
                "current_rank": cur.rank,
                "strengthened_rank": stronger.rank,
                "predicate_lattice_version": "v0.9",
            },
            extras={"direction": "strengthen"},
        )
