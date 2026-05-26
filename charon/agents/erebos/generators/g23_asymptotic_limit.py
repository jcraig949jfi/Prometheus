"""Generator 23: Asymptotic Limit.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 5.

Hypothesizes that error / failure rate in a Mahler-like
catalog scales as O(1/N) where N is object complexity (degree,
conductor, etc.) -- "noise vanishes at infinity."

Erebos Implementation Spec:
- Input / Provenance: Stygian or Erebos rows with a "mostly-true"
  verdict pattern (UNVERIFIED with kill_vector showing partial
  pass).
- Transformation: identify the complexity field (degree, conductor,
  n_samples); propose the error term scales as O(1/complexity).
- Output Claim: "The failure rate of <pattern> scales as O(1/N)
  where N is <complexity_field>."
- Falsification Route: sample objects at exponentially larger N;
  plot observed error vs theoretical 1/N curve; if error stays
  constant or grows, asymptotic decay is wrong.
- Expected Kill Pattern: error_term_does_not_decay.
- Loader Feasibility: Tier B; needs high-compute loaders for
  extreme-N samples.
- Reasoning Tier: R3 (asymptotic abstraction) + R5 (causal:
  positing N controls the error scale).
"""
from __future__ import annotations

from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


# Fields recognized as "complexity-like" — natural N's for
# asymptotic decay hypotheses.
COMPLEXITY_FIELDS = {
    "degree", "conductor", "n_paired", "n_samples",
    "cluster_size", "n_full", "n_total",
}


def _pick_complexity_field(payload: dict) -> Optional[tuple[str, float]]:
    for k, v in (payload or {}).items():
        if isinstance(v, bool):
            continue
        if not isinstance(v, (int, float)):
            continue
        if k in COMPLEXITY_FIELDS and v > 0:
            return (k, float(v))
    return None


class AsymptoticLimitGenerator:
    id = "g23_asymptotic_limit"
    name = "Asymptotic Limit"
    spec_phase = 5
    feasibility_tier = "B"
    reasoning_tier = "R3"
    expected_kill_pattern = "error_term_does_not_decay"

    def _candidate_for_row(self, row: dict, state: SwarmState) -> Optional[dict]:
        # Prefer UNVERIFIED rows (real battery output with mixed
        # signal) — those have actual error patterns to extrapolate.
        if row.get("verdict") not in ("UNVERIFIED", "REJECTED"):
            return None
        extras = row.get("extras", {}) or {}
        payload = extras.get("composition_payload", {}) or {}
        # Also try input_provenance for parent-side complexity fields
        prov = extras.get("input_provenance", {}) or {}
        for src in (payload, prov):
            picked = _pick_complexity_field(src)
            if picked is None:
                continue
            field, value = picked
            rid = row.get("record_id", "")
            key = f"{self.id}|{rid}|{field}"
            if key not in state.tried_pairs:
                return {"field": field, "value": value}
        return None

    def _parent_pool(self, state: SwarmState) -> list[dict]:
        return list(state.erebos_self_ledger) + list(state.stygian_substantive)

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
        parent_verdict = parent_row.get("verdict", "?")

        composed_id = (
            f"EREBOS-G23-asymptotic_O_1_over_{field}-{parent_gen}_{rid[:12]}"
        )

        composition_text = (
            f"Asymptotic-limit claim {composed_id}: "
            f"the parent claim from `{parent_gen}` "
            f"(\"{parent_text[:200]}\") was {parent_verdict} at "
            f"observed `{field}` = {value}. Hypothesis: the parent's "
            f"failure rate (or fuzzy verdict mass) scales as "
            f"O(1/{field}) -- i.e., the noise in the parent's "
            f"verdict vanishes as {field} grows. Equivalently: at "
            f"sufficiently large {field}, the parent claim's verdict "
            f"transitions to PROMOTED unambiguously. Falsification: "
            f"sample objects at {field} >> {value} and check the "
            f"observed error vs expected 1/{field} curve; if error "
            f"stays constant or grows, kill_pattern = error_term_"
            f"does_not_decay (asymptotic hypothesis was wrong)."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "parent_record_id": rid,
                "parent_generator_id": parent_gen,
                "parent_emitted_at": parent_row.get("emitted_at"),
                "parent_verdict": parent_verdict,
                "complexity_field": field,
                "observed_value": value,
                "predicted_scaling": f"O(1/{field})",
            },
            transformation_description=(
                f"Detect complexity-like field `{field}` (value={value}); "
                f"propose asymptotic decay: failure_rate ∝ 1/{field}. "
                f"Composition loader would sample at exponentially "
                f"increasing {field} values and fit the decay curve."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Composition-aware loader extends the parent's data "
                f"sample to {field} values 10x, 100x, 1000x the "
                f"observed {value}; computes failure rate at each "
                f"scale; fits log-log slope; if slope >= 0 (no "
                f"decay or growth), kill_pattern = error_term_does_"
                f"not_decay. If slope ≈ -1, asymptotic hypothesis "
                f"confirmed."
            ),
            expected_kill_pattern="error_term_does_not_decay",
            loader_feasibility_note=(
                "Tier B: requires high-compute extreme-value sampling. "
                "For Mossinghoff degree extension, PARI already in "
                "repo can compute Mahler measures for high-degree "
                "polynomials. v0.13+ loader work."
            ),
            parent_record_ids=[rid],
            composition_payload={
                "complexity_field": field,
                "observed_value": value,
                "predicted_scaling": f"O(1/{field})",
                "predicted_slope_loglog": -1.0,
            },
            extras={"asymptotic_form": "inverse_linear"},
        )
