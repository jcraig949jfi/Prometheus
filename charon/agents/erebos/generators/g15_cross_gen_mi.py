"""Generator 15: Cross-Generator Mutual-Information Generator.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 3.
Inverse of Hecate's existing audit: when Hecate's cross-generator
MI signal is high enough to suggest shared structure, G15
hypothesizes the latent confound L driving the convergence.

Erebos Implementation Spec:
- Input / Provenance: Hecate's latest cross-generator canonical
  patterns list (state.hecate_crossgen_canonical), plus
  the cross-gen MI z-score from the latest gradient archaeology
  artifact.
- Transformation: when ≥ MIN_CROSSGEN_PATTERNS canonical patterns
  appear cross-generator, emit "the cross-gen convergence is
  driven by Latent Confound L = <shared structural feature>."
- Output Claim: "Failures in Family A and Family B are isomorphic;
  driven by Latent Confound L (the shared canonical patterns)."
- Falsification Route: control for L by stratifying the kill_ledger
  on the shared pattern names; re-compute cross-gen MI within
  strata. If the in-strata MI is preserved, L was NOT the driver.
- Expected Kill Pattern: uncorrelated_residual_failures (the
  generators are actually exploring orthogonal spaces; the
  cross-gen MI signal was instrument circularity, not real
  convergence).
- Loader Feasibility: HARD (Tier B in Charon-state). Operates on
  swarm metadata, not on math objects; the falsification route
  requires Hecate to re-run with strata.
- Reasoning Tier: R5 (causal: positing L as the cause of
  convergence) + R6 (self-correction: checking the swarm's own
  measurement convergence).
"""
from __future__ import annotations

from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


# Threshold: need >= this many cross-generator canonical patterns
# for G15 to fire. Below this, the convergence signal is too thin
# to hypothesize a single latent confound.
MIN_CROSSGEN_PATTERNS = 2


class CrossGenMIGenerator:
    id = "g15_cross_gen_mi"
    name = "Cross-Generator Mutual-Information"
    spec_phase = 3
    feasibility_tier = "B"
    reasoning_tier = "R5"
    expected_kill_pattern = "uncorrelated_residual_failures"

    def applicable(self, state: SwarmState) -> bool:
        if len(state.hecate_crossgen_canonical) < MIN_CROSSGEN_PATTERNS:
            return False
        # Use the sorted-tuple of crossgen patterns as the tried key
        key = f"{self.id}|{','.join(sorted(state.hecate_crossgen_canonical))}"
        return key not in state.tried_pairs

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        if not self.applicable(state):
            return None
        crossgen = sorted(state.hecate_crossgen_canonical)
        # Hypothesize the SHARED component as the latent confound name.
        # Heuristic: the longest common substring across the cross-gen
        # patterns. For the v0.11 swarm the canonical patterns share
        # tokens like 'relation' / 'detrended_correlation' / 'method_'.
        latent_name = _longest_common_token(crossgen) or "shared_pattern"

        composed_id = f"EREBOS-G15-latent_{latent_name}-cgkps_{len(crossgen)}"

        composition_text = (
            f"Cross-generator MI claim {composed_id}: "
            f"Hecate's cross-generator audit currently surfaces "
            f"{len(crossgen)} canonical patterns appearing under "
            f">= 2 distinct generator_ids: {crossgen[:5]}. G15 "
            f"hypothesizes that this convergence is DRIVEN by a "
            f"single Latent Confound L = `{latent_name}` (the "
            f"shared structural token across the cross-gen patterns). "
            f"That is: the apparent multi-generator agreement is "
            f"NOT independent evidence; both generators are reacting "
            f"to the same underlying feature L of the kill-ledger "
            f"data. Falsification: stratify the kill_ledger by L "
            f"and re-compute MI; if cross-gen signal persists "
            f"within strata, L was NOT the driver (kill_pattern = "
            f"uncorrelated_residual_failures)."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "hecate_crossgen_patterns": crossgen,
                "n_crossgen_patterns": len(crossgen),
                "hypothesized_latent_confound": latent_name,
            },
            transformation_description=(
                f"Detect Hecate's cross-gen canonical pattern set; "
                f"extract longest-common-token across patterns as "
                f"the latent-confound hypothesis; emit the L-driven "
                f"convergence claim."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Composition-aware Stygian loader for G15 would: "
                f"(a) re-read the kill_ledger; (b) partition records "
                f"by whether canonical kill_pattern matches the "
                f"latent confound `{latent_name}`; (c) re-compute "
                f"Hecate-style MI(kill_pattern, generator_id) within "
                f"each partition; (d) if within-partition MI is still "
                f"significant, L was NOT the driver -- kill_pattern = "
                f"uncorrelated_residual_failures. Loader is currently "
                f"unbuilt; G15 emits the latent-confound hypothesis "
                f"as substrate, Hecate's own audit cycle can verify "
                f"by post-hoc stratification."
            ),
            expected_kill_pattern="uncorrelated_residual_failures",
            loader_feasibility_note=(
                "Tier B in Charon-state. The composition loader is "
                "Hecate-MI-aware: it would invoke Hecate's _analyze "
                "with a stratified record set. Doable but requires "
                "deeper Hecate coupling than v0.11 currently supports."
            ),
            parent_record_ids=[],  # G15 operates on swarm-meta, no parent record
            composition_payload={
                "hypothesized_latent_confound": latent_name,
                "crossgen_pattern_set": crossgen,
                "n_crossgen": len(crossgen),
            },
            extras={"swarm_meta_only": True},
        )


def _longest_common_token(patterns: list[str]) -> Optional[str]:
    """Heuristic: split each pattern on '_'; intersect token sets;
    return longest-length common token. None if intersection empty."""
    if not patterns:
        return None
    token_sets = [set(p.split("_")) for p in patterns]
    common = set.intersection(*token_sets) if token_sets else set()
    if not common:
        return None
    return max(common, key=len)
