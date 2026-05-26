"""Generator 17: Causal-Intervention.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 4.

Moves from Pearl's Rung 1 (observation) to Rung 2 (intervention).
Takes a survived correlation between A and B; defines a synthetic
data-munging intervention designed to SEVER the link; predicts
that under intervention, A and B should decouple.

Erebos Implementation Spec:
- Input / Provenance: PROMOTED claims with a correlation-shaped
  composition_payload (corr_raw, corr_norm fields from Pollux or
  G02+G04 chains).
- Transformation: define an intervention shape (label-shuffle,
  group-permutation, etc.); predict the correlation should
  vanish under the intervention.
- Output Claim: "Intervention I = <shuffle/permute X> will sever
  the link between A and B; correlation should drop below 0.10."
- Falsification Route: apply the intervention exactly to the
  parent data; recompute the correlation; if observed remains
  above threshold, intervention was flawed (and we learn that A↔B
  is robust to that intervention -- substrate signal).
- Expected Kill Pattern: correlation_survives_intervention
  (intervention was flawed; A↔B is more structural than expected).
- Loader Feasibility: Tier B; needs causal-inference primitives
  but can MVP via numpy shuffles.
- Reasoning Tier: R5 (Pearl Rung 2 explicit) + R8 (conjecture
  about decoupling).
"""
from __future__ import annotations

from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


# Correlation-shaped fields signal Pollux-style or G02+G04-style
# parent claims that G17 can intervene on.
CORRELATION_FIELDS = {
    "corr_raw", "corr_norm", "pollux_corr_raw", "pollux_corr_norm",
    "observed_divergence", "spearman", "pearson",
}

# Intervention threshold: under successful intervention, the
# correlation should drop below this absolute value.
DECOUPLING_THRESHOLD = 0.10


def _find_correlation_field(row: dict) -> Optional[tuple[str, float]]:
    extras = row.get("extras", {}) or {}
    sources = [
        extras.get("composition_payload", {}) or {},
        row.get("kill_vector", {}) if isinstance(row.get("kill_vector"), dict) else {},
        row.get("claim_payload", {}) or {},
    ]
    for src in sources:
        for k, v in src.items():
            if isinstance(v, bool):
                continue
            if not isinstance(v, (int, float)):
                continue
            if k in CORRELATION_FIELDS and abs(v) > DECOUPLING_THRESHOLD:
                return (k, float(v))
    return None


class CausalInterventionGenerator:
    id = "g17_causal_intervention"
    name = "Causal Intervention"
    spec_phase = 4
    feasibility_tier = "B"
    reasoning_tier = "R5"
    expected_kill_pattern = "correlation_survives_intervention"

    def _candidate_for_row(self, row: dict, state: SwarmState) -> Optional[dict]:
        if row.get("verdict") not in ("PROMOTED", "UNVERIFIED"):
            return None
        found = _find_correlation_field(row)
        if found is None:
            return None
        field, value = found
        rid = row.get("record_id", "")
        key = f"{self.id}|{rid}|{field}"
        if key in state.tried_pairs:
            return None
        return {"field": field, "value": value}

    def _parent_pool(self, state: SwarmState) -> list[dict]:
        return (
            list(state.pollux_substantive)
            + list(state.erebos_self_ledger)
            + list(state.stygian_substantive)
        )

    def applicable(self, state: SwarmState) -> bool:
        for r in self._parent_pool(state):
            if self._candidate_for_row(r, state) is not None:
                return True
        return False

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        for r in sorted(
            self._parent_pool(state),
            key=lambda x: x.get("emitted_at", ""), reverse=True,
        ):
            cand = self._candidate_for_row(r, state)
            if cand is not None:
                return self._build_claim(r, cand)
        return None

    def _build_claim(self, parent_row: dict, cand: dict) -> ComposedClaim:
        field = cand["field"]
        value = cand["value"]
        rid = parent_row.get("record_id", "?")
        parent_text = parent_row.get("canonical_claim_text", "")
        parent_gen = parent_row.get("generator_id", "?")

        # Define the intervention shape — label/index shuffle
        # within the parent's data context.
        intervention = "permute_indices_within_group"

        composed_id = (
            f"EREBOS-G17-intervene_{intervention}_on_{field}"
            f"-{parent_gen}_{rid[:12]}"
        )

        composition_text = (
            f"Causal-intervention claim {composed_id}: "
            f"the parent claim from `{parent_gen}` "
            f"(\"{parent_text[:200]}\") established a correlation "
            f"`{field}` = {value} (PROMOTED-class signal). The "
            f"interventional hypothesis: applying intervention I = "
            f"`{intervention}` (Pearl Rung 2 do-operator) to the "
            f"underlying data should SEVER the A↔B link; the "
            f"correlation should drop to |{field}| < "
            f"{DECOUPLING_THRESHOLD}. If the correlation SURVIVES "
            f"the intervention (|{field}| > "
            f"{DECOUPLING_THRESHOLD} after I), the intervention "
            f"was flawed (kill_pattern = "
            f"correlation_survives_intervention) AND the A↔B "
            f"link is more structurally robust than the parent "
            f"correlation suggested -- substrate-grade signal "
            f"either way."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "parent_record_id": rid,
                "parent_generator_id": parent_gen,
                "parent_emitted_at": parent_row.get("emitted_at"),
                "correlation_field": field,
                "observed_correlation": value,
                "intervention_type": intervention,
                "decoupling_threshold": DECOUPLING_THRESHOLD,
            },
            transformation_description=(
                f"Identify correlation field `{field}` = {value} in "
                f"parent payload; define intervention I = "
                f"`{intervention}`; predict post-intervention |"
                f"correlation| < {DECOUPLING_THRESHOLD}."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Composition-aware loader for G17 would: "
                f"(a) re-extract the parent's data context; "
                f"(b) apply intervention `{intervention}` "
                f"(numpy permutation within indexed groups); "
                f"(c) recompute the correlation; (d) compare to "
                f"the {DECOUPLING_THRESHOLD} decoupling threshold. "
                f"If correlation persists above threshold, "
                f"kill_pattern = correlation_survives_intervention."
            ),
            expected_kill_pattern="correlation_survives_intervention",
            loader_feasibility_note=(
                "Tier B: numpy permutation + correlation "
                "recomputation. Standard causal-inference pipeline. "
                "Composition loader achievable in ~150 LOC for the "
                "Pollux-correlation case."
            ),
            parent_record_ids=[rid],
            composition_payload={
                "correlation_field": field,
                "observed_correlation": value,
                "intervention_type": intervention,
                "decoupling_threshold": DECOUPLING_THRESHOLD,
            },
            extras={"pearl_rung": 2},
        )
