"""Generator 9: Projection-Collapse.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 2 + research
notes pivot/erebos_g09_projection_collapse_research_2026-05-26.md.

Occam's Razor generator. Takes a complex Erebos composition and
posits the entire claim's predictive power reduces to a single
high-variance coordinate.

Erebos Implementation Spec:
- Input / Provenance: An Erebos composition row (g01/g02/etc.)
  with multi-field composition_payload.
- Transformation: Isolates the single highest-variance (or
  highest-absolute-magnitude as MVP proxy) coordinate; emits
  candidate-claim that this coordinate alone captures >95% of
  predictive power.
- Output Claim: ">95% of Complex Claim C's predictive power is
  captured by the single variable T."
- Falsification Route: Ablation -- drop T, check residual
  predictive power.
- Expected Kill Pattern: residual_survival (the complex claim IS
  genuinely complex).
- Loader Feasibility: EASY (Tier S). Pure column drop.
- Reasoning Tier: R3 (abstraction) + R6 (Occam self-correction).
"""
from __future__ import annotations

from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


# Minimum payload coordinate count to apply G09 (single-coord
# parent claims have nothing to project onto).
MIN_PAYLOAD_COORDS = 2

# Predicted predictive-power capture threshold (in the candidate
# claim text). Empirical -- 95% is conventional Occam threshold.
CAPTURE_THRESHOLD = 0.95


def _extract_numeric_fields(payload: dict) -> dict[str, float]:
    """Pull only numeric (int/float, non-bool) fields from a
    composition_payload. Bool excluded -- it would dominate any
    'variance' picker trivially."""
    out: dict[str, float] = {}
    for k, v in (payload or {}).items():
        if isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            out[k] = float(v)
    return out


class ProjectionCollapseGenerator:
    id = "g09_projection_collapse"
    name = "Projection-Collapse"
    spec_phase = 2
    feasibility_tier = "S"
    reasoning_tier = "R3"
    expected_kill_pattern = "residual_survival"

    def applicable(self, state: SwarmState) -> bool:
        for r in state.erebos_self_ledger:
            extras = r.get("extras", {}) or {}
            payload = extras.get("composition_payload", {}) or {}
            numeric = _extract_numeric_fields(payload)
            if len(numeric) >= MIN_PAYLOAD_COORDS:
                key = f"{self.id}|{r.get('record_id', '')}"
                if key not in state.tried_pairs:
                    return True
        return False

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        candidates = sorted(
            [
                r for r in state.erebos_self_ledger
                if len(_extract_numeric_fields(
                    (r.get("extras", {}) or {}).get("composition_payload", {}) or {}
                )) >= MIN_PAYLOAD_COORDS
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
        extras = parent_row.get("extras", {}) or {}
        payload = extras.get("composition_payload", {}) or {}
        numeric = _extract_numeric_fields(payload)
        # MVP picker: pick the field with maximum absolute magnitude
        # as a variance proxy. Real per-cohort variance estimation
        # requires accumulating multiple parent rows of the same
        # plugin_id; defer to v0.10+.
        chosen = max(numeric, key=lambda k: abs(numeric[k]))
        chosen_value = numeric[chosen]
        other_fields = sorted([k for k in numeric if k != chosen])

        # Parent claim metadata for the output text
        parent_composed_id = (parent_row.get("claim_payload") or {}).get("composed_id", "?")
        parent_plugin_id = (parent_row.get("claim_payload") or {}).get("plugin_id", "?")
        parent_claim = parent_row.get("canonical_claim_text", "")

        composed_id = f"EREBOS-G09-collapse_to-{chosen}-from-{parent_composed_id}"

        composition_text = (
            f"Projection-collapse claim {composed_id}: "
            f">={int(CAPTURE_THRESHOLD * 100)}% of the predictive power "
            f"of the parent claim `{parent_composed_id}` (from plugin "
            f"`{parent_plugin_id}`: \"{parent_claim[:200]}\") "
            f"is captured by the single high-magnitude coordinate "
            f"`{chosen}` (value: {chosen_value}). The other "
            f"{len(other_fields)} coordinates ({', '.join(other_fields)}) "
            f"are hypothesized to be decorative -- removing them "
            f"should not meaningfully reduce predictive power. "
            f"This is the Occam-razor / Tier-R3 abstraction move: "
            f"if the complex composition's structure compresses to one "
            f"coordinate, the composition's apparent complexity was "
            f"artifact, not signal."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "parent_record_id": parent_row.get("record_id"),
                "parent_composed_id": parent_composed_id,
                "parent_plugin_id": parent_plugin_id,
                "parent_emitted_at": parent_row.get("emitted_at"),
                "n_numeric_coords": len(numeric),
                "chosen_coord": chosen,
                "chosen_value": chosen_value,
                "other_coords": other_fields,
            },
            transformation_description=(
                f"Extract numeric fields from parent composition_payload "
                f"({len(numeric)} found); pick max-absolute-magnitude as "
                f"variance proxy (chosen: `{chosen}`); hypothesize "
                f">={CAPTURE_THRESHOLD} predictive-power capture by this "
                f"single coordinate alone."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Ablation. Composition-aware Stygian loader drops the "
                f"`{chosen}` coordinate from the parent's predictive "
                f"context; battery re-runs on the remaining "
                f"{len(other_fields)} coordinates. If the residual battery "
                f"verdict shows ANY survival > random-baseline, this "
                f"projection-collapse claim is killed by residual_survival. "
                f"Composition-aware Stygian loader (task #37) required "
                f"for actual execution; currently short-circuits with "
                f"stygian_erebos_composed_loader_pending."
            ),
            expected_kill_pattern="residual_survival",
            loader_feasibility_note=(
                "EASY (Tier S): pure column drop. The composition-aware "
                "Stygian loader for G09 needs only to omit one named "
                "coordinate from the parent's data context and re-run "
                "the original test shape. No new battery primitives."
            ),
            parent_record_ids=[parent_row.get("record_id", "")],
            composition_payload={
                "chosen_coord": chosen,
                "chosen_value": chosen_value,
                "other_coords": other_fields,
                "n_numeric_coords": len(numeric),
                "capture_threshold": CAPTURE_THRESHOLD,
            },
            extras={
                "variance_picker": "max_absolute_magnitude_mvp",
                "parent_plugin_id": parent_plugin_id,
            },
        )
