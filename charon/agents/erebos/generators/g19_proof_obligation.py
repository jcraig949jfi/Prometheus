"""Generator 19: Proof-Obligation.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 4.

Takes a complex Erebos composition (a claim assembled from 2+
parent rows) and emits a logical-dependency graph: the macro
claim C is true IFF each sub-claim C_i is independently true.
Falsifying any sub-claim takes the parent down with it.

Erebos Implementation Spec:
- Input / Provenance: an Erebos self-ledger row with >= 2 distinct
  parent_record_ids. The parents become the proof obligations.
- Transformation: restate the parent's claim as a conjunction over
  its source claims; emit the conjunction as the proof-obligation
  graph.
- Output Claim: "Composed claim C (composed_id=<X>) holds iff each
  of [parent_1, parent_2, ...] independently holds. Falsifying any
  parent falsifies C."
- Falsification Route: independently re-test each parent. The first
  parent that flips to REJECTED kills the composed claim. If all
  parents stay PROMOTED but C is REJECTED, the conjunction is
  insufficient (kill_pattern = composition_glue_needed).
- Expected Kill Pattern: sub_claim_falsified (the modal failure
  mode; the macro fails because a sub-obligation fails).
- Loader Feasibility: Tier C-HARD (full Lean integration). Tier B-MVP
  is achievable: just verify each parent's verdict is still PROMOTED
  in the live ledger; if any parent has flipped, the composition is
  no longer valid.
- Reasoning Tier: R8 (a proof obligation IS a conjecture about
  decomposability) + R3 (logical structure / dependency graph).

DIFFERENTIATION:
- G22 Subgraph/Clique extracts a master property unifying many
  parents.
- G19 inverts: decomposes one composition into its prerequisite
  obligations.
- They are dual operations over the parent-graph.
"""
from __future__ import annotations

from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


MIN_PARENTS = 2  # need at least this many distinct parents to decompose


def _erebos_row_with_parents(row: dict) -> Optional[list[str]]:
    """Extract parent_record_ids from an Erebos self-ledger row's
    extras. Returns None if fewer than MIN_PARENTS distinct parents."""
    extras = row.get("extras") or {}
    # Two common spots: 'parent_record_ids' top-level field, or
    # nested in 'composition_payload'.
    ids = (
        extras.get("parent_record_ids")
        or (extras.get("composition_payload") or {}).get("parent_record_ids")
        or []
    )
    if not isinstance(ids, (list, tuple)):
        return None
    distinct = sorted(set(str(i) for i in ids if i))
    if len(distinct) < MIN_PARENTS:
        return None
    return distinct


def _lookup_parent_in_state(parent_rid: str, state: SwarmState) -> Optional[dict]:
    """Find a row in any pool with matching record_id."""
    for pool in (
        state.stygian_substantive,
        state.pollux_substantive,
        state.erebos_self_ledger,
    ):
        for r in pool:
            if r.get("record_id") == parent_rid:
                return r
    return None


class ProofObligationGenerator:
    id = "g19_proof_obligation"
    name = "Proof Obligation"
    spec_phase = 4
    feasibility_tier = "C"
    reasoning_tier = "R8"
    expected_kill_pattern = "sub_claim_falsified"

    def _candidate(self, row: dict, state: SwarmState) -> Optional[dict]:
        parents = _erebos_row_with_parents(row)
        if parents is None:
            return None
        rid = row.get("record_id", "")
        key = f"{self.id}|{rid}|{','.join(parents)}"
        if key in state.tried_pairs:
            return None
        # Look up each parent's current verdict in the live state.
        parent_states = []
        for prid in parents:
            p = _lookup_parent_in_state(prid, state)
            parent_states.append({
                "parent_record_id": prid,
                "current_verdict": (p or {}).get("verdict") or "UNKNOWN",
                "current_kill_pattern": (p or {}).get("kill_pattern"),
                "found_in_state": p is not None,
            })
        return {"parents": parents, "parent_states": parent_states}

    def applicable(self, state: SwarmState) -> bool:
        for r in state.erebos_self_ledger:
            if self._candidate(r, state) is not None:
                return True
        return False

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        for r in sorted(
            state.erebos_self_ledger,
            key=lambda x: x.get("emitted_at", ""), reverse=True,
        ):
            cand = self._candidate(r, state)
            if cand is not None:
                return self._build_claim(r, cand)
        return None

    def _build_claim(self, parent_row: dict, cand: dict) -> ComposedClaim:
        rid = parent_row.get("record_id", "?")
        parent_text = parent_row.get("canonical_claim_text", "")
        parent_gen = parent_row.get("generator_id", "?")
        parents: list[str] = cand["parents"]
        parent_states: list[dict] = cand["parent_states"]

        # Detect already-falsified sub-obligations
        already_falsified = [
            ps for ps in parent_states
            if ps["current_verdict"] == "REJECTED"
        ]

        composed_id = (
            f"EREBOS-G19-proof_obligation_{rid[:12]}_n{len(parents)}"
        )

        falsified_note = ""
        if already_falsified:
            falsified_ids = ", ".join(
                ps["parent_record_id"] for ps in already_falsified
            )
            falsified_note = (
                f" NOTE: {len(already_falsified)} sub-obligation(s) "
                f"[{falsified_ids}] are ALREADY REJECTED in the live "
                f"ledger -- the macro claim should be REJECTED by "
                f"transitivity."
            )

        composition_text = (
            f"Proof-obligation claim {composed_id}: "
            f"the parent composed-claim from `{parent_gen}` "
            f"(\"{parent_text[:200]}\") is structurally equivalent to "
            f"the conjunction over its {len(parents)} parent "
            f"obligations [{', '.join(parents)}]. Falsifying any one "
            f"obligation falsifies the macro claim. Falsification: "
            f"independently re-test each parent's current verdict in "
            f"the ledger; the first REJECTED parent kills the macro. "
            f"If all parents stay PROMOTED but the macro is REJECTED, "
            f"the conjunction is insufficient (composition_glue_needed). "
            f"Expected modal failure: sub_claim_falsified.{falsified_note}"
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "parent_record_id": rid,
                "parent_generator_id": parent_gen,
                "parent_verdict": parent_row.get("verdict"),
                "n_obligations": len(parents),
                "obligation_parent_ids": parents,
                "obligation_current_states": parent_states,
                "n_already_falsified": len(already_falsified),
            },
            transformation_description=(
                f"Identify {len(parents)} parent obligations in the "
                f"composed claim's lineage; emit the conjunction over "
                f"them as an explicit dependency graph; look up each "
                f"parent's current verdict in the live state for "
                f"already-falsified sub-obligations."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Composition-aware loader (Tier B-MVP path) would: "
                f"(a) for each obligation parent_id, re-read its "
                f"latest verdict in the current ledger; "
                f"(b) if any has flipped to REJECTED since the macro "
                f"was emitted, the macro is now invalid by "
                f"transitivity (kill_pattern = sub_claim_falsified); "
                f"(c) if all parents remain PROMOTED but the macro is "
                f"REJECTED in independent testing, kill_pattern = "
                f"composition_glue_needed (the conjunction omitted "
                f"a hidden glue assumption). Tier C-HARD path adds "
                f"Lean integration to extract formal proof obligations "
                f"rather than just verdict transitivity."
            ),
            expected_kill_pattern="sub_claim_falsified",
            loader_feasibility_note=(
                f"Tier B-MVP: ledger-transitivity check; tractable in "
                f"v0.13. Tier C-HARD: Lean / formal-logic integration "
                f"to extract genuine proof obligations vs verdict "
                f"transitivity. Defer Lean to v0.15+."
            ),
            parent_record_ids=[rid] + parents,
            composition_payload={
                "n_obligations": len(parents),
                "obligation_parent_ids": parents,
                "n_already_falsified": len(already_falsified),
                "decomposition_method": "ledger_transitivity_v0.13",
            },
            extras={"obligation_type": "conjunction"},
        )
