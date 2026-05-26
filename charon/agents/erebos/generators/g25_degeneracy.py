"""Generator 25: Degeneracy / Trivial-Case.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 5 + research
notes pivot/erebos_g25_degeneracy_research_2026-05-26.md.

Sanity-check / boundary-case generator. Takes a complex composed
claim and asks: does it trivially hold (or elegantly zero out)
when the underlying object collapses to its simplest state?

Erebos Implementation Spec:
- Input / Provenance: An Erebos composition whose parent problem
  is in the DEGENERATE_REGISTRY.
- Transformation: Substitute the parent problem's object with the
  registered degenerate-state (rank=0 / degree=1 / unknot / etc.).
- Output Claim: "Complex Relation R must trivially hold (or
  elegantly zero out) for Degenerate State D."
- Falsification Route: Run claim exclusively on degenerate objects.
- Expected Kill Pattern: division_by_zero_or_type_error (proving
  the logic wasn't generalized properly).
- Loader Feasibility: EASY (Tier A in Charon-state because the
  registry needs curation per-domain).
- Reasoning Tier: R6 (self-correction) + R1 (rule execution at
  boundary).

Cheap-and-fast preliminary filter per the spec: catches over-
specialized compositions before wasting compute on full battery
runs.
"""
from __future__ import annotations

from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


# Per-problem-id (or per-domain-hint) degenerate states.
# Hand-curated. Grows as new Stygian loaders ship.
DEGENERATE_REGISTRY: dict[str, dict] = {
    "BL-C-001": {
        "name": "degree_1_polynomial",
        "description": "Linear polynomial; Mahler measure is just |leading coefficient|; trivially exceeds Lehmer bound 1.176 for any non-cyclotomic integer poly.",
        "state": {"degree": 1, "salem_class": False, "cyclotomic": False},
        "trivial_holds_reason": "M(P) = |a_1| >= 1 for monic poly; Lehmer's bound only meaningful for higher degree.",
    },
    "BL-C-002": {
        "name": "rank_0_curve",
        "description": "Rank-0 elliptic curve; BSD predicts L(E,1) != 0 and the rank distribution claim trivializes (rank IS 0 by selection).",
        "state": {"rank": 0, "torsion": "trivial"},
        "trivial_holds_reason": "Selection on rank=0 makes any rank-distribution claim tautological.",
    },
    "BL-C-003": {
        "name": "degree_1_polynomial",
        "description": "Linear polynomial as degenerate Mahler-spectrum input.",
        "state": {"degree": 1},
        "trivial_holds_reason": "Same as BL-C-001 -- linear case is trivially above any non-trivial spectrum claim.",
    },
    "BL-C-004": {
        "name": "degree_1_polynomial",
        "description": "Linear polynomial for Schinzel-Zassenhaus follow-on.",
        "state": {"degree": 1},
        "trivial_holds_reason": "Dimitrov bound exp(log2/(4*deg)) is trivially > 1 for deg=1.",
    },
}


class DegeneracyGenerator:
    id = "g25_degeneracy"
    name = "Degeneracy / Trivial-Case"
    spec_phase = 5
    feasibility_tier = "A"
    reasoning_tier = "R6"
    expected_kill_pattern = "division_by_zero_or_type_error"

    def _extract_parent_problem_id(self, row: dict) -> Optional[str]:
        """Look in the Erebos row's nested input_provenance for the
        original parent Stygian problem_id. Falls back to scanning
        extras + claim_payload for any 'BL-C-NNN' key."""
        extras = row.get("extras", {}) or {}
        provenance = extras.get("input_provenance", {}) or {}
        # Try direct
        for key in ("stygian_problem_id", "parent_problem_id"):
            v = provenance.get(key)
            if isinstance(v, str) and v.startswith("BL-C-"):
                return v
        # claim_payload.composed_id often contains BL-C-NNN
        cp = row.get("claim_payload", {}) or {}
        composed = cp.get("composed_id") or ""
        if isinstance(composed, str):
            for token in composed.split("-"):
                if token.startswith("BL-C-"):
                    # Actually we have "BL", "C", "NNN"; reassemble
                    pass
            # Simpler: regex-match the embedded BL-C-NNN
            import re
            m = re.search(r"BL-C-\d+", composed)
            if m:
                return m.group(0)
        return None

    def applicable(self, state: SwarmState) -> bool:
        for r in state.erebos_self_ledger:
            problem_id = self._extract_parent_problem_id(r)
            if problem_id and problem_id in DEGENERATE_REGISTRY:
                key = f"{self.id}|{r.get('record_id', '')}"
                if key not in state.tried_pairs:
                    return True
        return False

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        candidates = sorted(
            [
                r for r in state.erebos_self_ledger
                if self._extract_parent_problem_id(r) in DEGENERATE_REGISTRY
            ],
            key=lambda r: r.get("emitted_at", ""), reverse=True,
        )
        for r in candidates:
            key = f"{self.id}|{r.get('record_id', '')}"
            if key in state.tried_pairs:
                continue
            return self._build_claim(r)
        return None

    def _build_claim(self, parent_row: dict) -> ComposedClaim:
        problem_id = self._extract_parent_problem_id(parent_row)
        degen = DEGENERATE_REGISTRY[problem_id]
        parent_composed_id = (parent_row.get("claim_payload") or {}).get("composed_id", "?")
        parent_plugin_id = (parent_row.get("claim_payload") or {}).get("plugin_id", "?")
        parent_claim = parent_row.get("canonical_claim_text", "")

        composed_id = (
            f"EREBOS-G25-degenerate-{problem_id}-to-{degen['name']}"
        )

        composition_text = (
            f"Degeneracy claim {composed_id}: "
            f"the parent claim `{parent_composed_id}` (plugin "
            f"`{parent_plugin_id}`: \"{parent_claim[:200]}\") "
            f"must trivially hold (or elegantly zero out, or produce "
            f"a typed exception) when restricted to the degenerate "
            f"state `{degen['name']}` ({degen['description']}). "
            f"Predicted: {degen['trivial_holds_reason']}. "
            f"If the claim instead throws division_by_zero, type-error, "
            f"or contradiction at the degenerate boundary, the parent "
            f"composition's logic was not properly generalized -- the "
            f"complex form is over-fitted to non-degenerate inputs."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "parent_record_id": parent_row.get("record_id"),
                "parent_composed_id": parent_composed_id,
                "parent_plugin_id": parent_plugin_id,
                "parent_emitted_at": parent_row.get("emitted_at"),
                "parent_problem_id": problem_id,
                "degenerate_state_name": degen["name"],
                "degenerate_state_dict": degen["state"],
            },
            transformation_description=(
                f"Substitute parent claim's object with the "
                f"registered degenerate state for `{problem_id}`: "
                f"`{degen['name']}` (constraints: {degen['state']}). "
                f"Boundary-case-test discipline (DNA Tier R6 self-"
                f"correction)."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Composition-aware Stygian loader for G25 runs the "
                f"parent claim exclusively on objects satisfying "
                f"`{degen['state']}` (the degenerate restriction). "
                f"If any of: division-by-zero exception, type error, "
                f"or contradictory verdict (battery says PROMOTED on a "
                f"trivially-true claim) occurs, the parent composition's "
                f"generalization was unsound. Composition-aware Stygian "
                f"loader (task #37) required for actual execution; "
                f"currently short-circuits with "
                f"stygian_erebos_composed_loader_pending."
            ),
            expected_kill_pattern="division_by_zero_or_type_error",
            loader_feasibility_note=(
                f"EASY (Tier A): trivial restricted-dataset construction "
                f"via the existing dataset accessor "
                f"(prometheus_math.databases.{problem_id.split('-')[-1]} "
                f"or analogue). Registry needs hand curation per "
                f"new domain but each entry is small."
            ),
            parent_record_ids=[parent_row.get("record_id", "")],
            composition_payload={
                "degenerate_state_dict": degen["state"],
                "degenerate_state_name": degen["name"],
                "degenerate_state_description": degen["description"],
                "trivial_holds_reason": degen["trivial_holds_reason"],
                "parent_problem_id": problem_id,
            },
            extras={"degenerate_registry_source": "g25_v0.9_curated"},
        )
