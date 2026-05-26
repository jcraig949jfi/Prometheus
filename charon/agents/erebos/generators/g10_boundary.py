"""Generator 10: Boundary.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 2.

Hunts phase transitions: sweeps a threshold θ across a size
invariant (e.g., polynomial degree, conductor, M-value) and posits
"Pattern X survives below θ and fails above θ" -- a binary
regime split.

Erebos Implementation Spec:
- Input / Provenance: Erebos compositions with multi-coord
  composition_payload that includes a SIZE-LIKE numeric field
  (degree, conductor, n_paired, etc.).
- Transformation: pick the size field; propose a candidate
  threshold = median of its observed range; emit "claim holds
  for size < θ, fails for size > θ."
- Output Claim: "Pattern X survives for size_field < θ and
  strictly fails for size_field > θ."
- Falsification Route: focused sampling at the boundary θ ± ε;
  if the verdict transitions smoothly rather than sharply, kill_
  pattern = smooth_degradation.
- Expected Kill Pattern: smooth_degradation (no real phase
  transition; the boundary is sampling-density illusion).
- Loader Feasibility: Tier B. Threshold-sweep + binary-search.
- Reasoning Tier: R3 (phase-transition abstraction) + R5 (causal:
  positing that the size field CAUSES the verdict transition).
"""
from __future__ import annotations

from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


# Fields recognized as "size-like" -- candidates for the threshold
# sweep coordinate. Picked from the actual swarm's payload vocab.
SIZE_LIKE_FIELDS = {
    "degree", "n_paired", "n_total", "conductor", "regulator",
    "cluster_size", "n_samples", "n_full", "n_ablated",
    "permutation_n", "tightened_value", "observed_value",
}


def _pick_size_field(payload: dict) -> Optional[tuple[str, float]]:
    """Find the first numeric size-like field in a payload."""
    for k, v in (payload or {}).items():
        if isinstance(v, bool):
            continue
        if not isinstance(v, (int, float)):
            continue
        if k in SIZE_LIKE_FIELDS:
            return (k, float(v))
    return None


class BoundaryGenerator:
    id = "g10_boundary"
    name = "Boundary"
    spec_phase = 2
    feasibility_tier = "B"
    reasoning_tier = "R3"
    expected_kill_pattern = "smooth_degradation"

    def _candidate_for_row(self, row: dict, state: SwarmState) -> Optional[dict]:
        extras = row.get("extras", {}) or {}
        payload = extras.get("composition_payload", {}) or {}
        picked = _pick_size_field(payload)
        if picked is None:
            return None
        field, value = picked
        rid = row.get("record_id", "")
        key = f"{self.id}|{rid}|{field}"
        if key in state.tried_pairs:
            return None
        return {"field": field, "value": value}

    def applicable(self, state: SwarmState) -> bool:
        for r in state.erebos_self_ledger:
            if self._candidate_for_row(r, state) is not None:
                return True
        return False

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        for r in sorted(
            state.erebos_self_ledger,
            key=lambda x: x.get("emitted_at", ""), reverse=True,
        ):
            cand = self._candidate_for_row(r, state)
            if cand is not None:
                return self._build_claim(r, cand)
        return None

    def _build_claim(self, parent_row: dict, cand: dict) -> ComposedClaim:
        field = cand["field"]
        value = cand["value"]
        # Candidate threshold: half the observed value (rough median
        # proxy when we only have one data point). Real threshold-
        # sweep happens in the composition loader.
        theta_candidate = value / 2.0 if value != 0 else 1.0
        rid = parent_row.get("record_id", "?")
        parent_text = parent_row.get("canonical_claim_text", "")
        parent_gen = parent_row.get("generator_id", "?")

        composed_id = (
            f"EREBOS-G10-boundary_{field}_at_{theta_candidate:.4g}"
            f"-{parent_gen}_{rid[:12]}"
        )

        composition_text = (
            f"Boundary claim {composed_id}: "
            f"the parent claim from `{parent_gen}` "
            f"(\"{parent_text[:200]}\") is hypothesized to exhibit "
            f"a PHASE TRANSITION at threshold θ ≈ {theta_candidate} "
            f"on the size-like coordinate `{field}` (observed "
            f"value: {value}). Specifically: the parent's verdict "
            f"holds for `{field}` < θ and fails for `{field}` > θ. "
            f"If true, this identifies a structural boundary in "
            f"the data; if the verdict transitions smoothly across "
            f"θ instead of sharply, kill_pattern = smooth_degradation "
            f"(no real phase transition; the apparent boundary is "
            f"sampling-density artifact)."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "parent_record_id": rid,
                "parent_generator_id": parent_gen,
                "parent_emitted_at": parent_row.get("emitted_at"),
                "size_field": field,
                "observed_size_value": value,
                "candidate_threshold": theta_candidate,
            },
            transformation_description=(
                f"Detect size-like field `{field}` in parent payload "
                f"(value={value}); propose candidate threshold θ = "
                f"{theta_candidate} (half-value heuristic; real "
                f"threshold-sweep deferred to composition loader)."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Composition-aware loader for G10 would: "
                f"(a) enumerate the parent's data context across "
                f"a range of `{field}` values bracketing θ = "
                f"{theta_candidate}; (b) re-run the parent test at "
                f"each value; (c) check whether the verdict "
                f"transitions sharply (binary jump from PROMOTED "
                f"to REJECTED at the boundary) or smoothly. Smooth "
                f"transition -> kill_pattern = smooth_degradation."
            ),
            expected_kill_pattern="smooth_degradation",
            loader_feasibility_note=(
                "Tier B: threshold-sweep + binary-search via "
                "shared _mahler_composition_helpers + parametric "
                "filtering. Composition loader unbuilt; future v0.13+."
            ),
            parent_record_ids=[rid],
            composition_payload={
                "size_field": field,
                "candidate_threshold": theta_candidate,
                "observed_value": value,
            },
            extras={"sweep_strategy": "half_value_heuristic_v0.12"},
        )
