"""Generator 2: Contrast Generator.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 1 (Tier S).

Erebos Implementation Spec:
- Input / Provenance: A REJECTED Stygian claim whose battery sub-
  tests showed high variance (the rejection wasn't uniform across
  the dataset). Currently rare because Stygian REJECTED requires a
  loader that returns clean PASS/FAIL on F1-F23 sub-tests; we relax
  to any REJECTED OR UNVERIFIED Stygian row paired with a categorical
  binary split available from the dataset metadata.
- Transformation: Splits the dataset via a binary categorical
  variable (Salem-class vs non-Salem from Mossinghoff; CM vs non-CM
  from BSD; even vs odd degree). Hypothesizes that survival rate
  diverges between groups by a margin > delta.
- Output Claim: 'Survival rate of Claim C in Group A != Survival
  rate of Claim C in Group B by margin > delta'.
- Falsification Route: Permutation test (Stygian shuffles group
  labels N=1000 times; observed divergence compared to shuffled
  distribution).
- Expected Kill Pattern: 'permutation_null' (observed difference
  indistinguishable from shuffled labels).
- Loader Feasibility: EASY (Tier S).

Binary-split catalog (Charon swarm v0.8):
  - BL-C-001 Lehmer/Mahler: Salem-class vs non-Salem (from
    Mossinghoff catalog `salem_class` flag).
  - BL-C-002 BSD: CM vs non-CM (from BSD rich dataset `cm` flag),
    or rank-0 vs rank-1+, or signD=+1 vs signD=-1.
  - Other BL-C-* (no loader yet): falls back to Mossinghoff-based
    Salem vs non-Salem as a generic-stand-in split (loader feasibility
    note flags this as 'compromise split until problem-specific
    categorical is mapped').
"""
from __future__ import annotations

from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)

# Per-problem binary splits. Empty value means 'no problem-specific
# split known; fall back to generic Salem vs non-Salem.'
PROBLEM_BINARY_SPLITS: dict[str, dict] = {
    "BL-C-001": {
        "split_name": "salem_vs_non_salem",
        "group_a_label": "Salem-class polynomials (from Mossinghoff salem_class=True)",
        "group_b_label": "non-Salem polynomials",
        "data_filter_hint": "filter Mossinghoff catalog by salem_class flag",
    },
    "BL-C-002": {
        "split_name": "cm_vs_non_cm",
        "group_a_label": "CM elliptic curves (from BSD rich cm=1)",
        "group_b_label": "non-CM elliptic curves (cm=0)",
        "data_filter_hint": "filter bsd_rich entries by rich.cm field",
    },
    "BL-C-003": {
        "split_name": "salem_vs_non_salem",
        "group_a_label": "Salem-class Mahler polynomials",
        "group_b_label": "non-Salem polynomials",
        "data_filter_hint": "Mossinghoff salem_class flag",
    },
    "BL-C-004": {
        "split_name": "salem_vs_non_salem",
        "group_a_label": "Salem-class polynomials (Schinzel-Zassenhaus follow-on)",
        "group_b_label": "non-Salem polynomials",
        "data_filter_hint": "Mossinghoff salem_class flag",
    },
}

# Generic split used when no problem-specific split is registered
GENERIC_BINARY_SPLIT = {
    "split_name": "even_vs_odd_degree",
    "group_a_label": "even-degree mathematical objects",
    "group_b_label": "odd-degree mathematical objects",
    "data_filter_hint": "filter source dataset by degree parity (works for any polynomial/representation domain)",
}

# Statistical parameters
PERMUTATION_N = 1000
SURVIVAL_RATE_MARGIN_DELTA = 0.10  # hypothesized divergence threshold


def _is_substantive_for_contrast(row: dict) -> bool:
    """Contrast needs claims with battery sub-test results, not pure
    short-circuit UNVERIFIED rows. We accept REJECTED (clean kill --
    perfect contrast input) OR UNVERIFIED-with-real-tests
    (POSSIBLE/INCONCLUSIVE verdicts where sub-tests fired)."""
    verdict = row.get("verdict")
    if verdict not in ("REJECTED", "UNVERIFIED"):
        return False
    kp = row.get("kill_pattern") or ""
    if kp.endswith("_pending") or kp.endswith("_loader_pending") or kp.endswith("_skipped"):
        return False
    # Must have real kill_vector tests (not None)
    kv = row.get("kill_vector")
    if not kv or not isinstance(kv, dict):
        return False
    if not kv.get("tests"):
        return False
    return True


class ContrastGenerator:
    id = "g02_contrast"
    name = "Contrast Generator"
    spec_phase = 1
    feasibility_tier = "S"
    expected_kill_pattern = "permutation_null"

    def applicable(self, state: SwarmState) -> bool:
        candidates = [
            r for r in state.stygian_substantive
            if _is_substantive_for_contrast(r)
        ]
        if not candidates:
            return False
        # At least one candidate must be uncomposed against contrast
        for c in candidates:
            key = f"{self.id}|{c.get('record_id','')}"
            if key not in state.tried_pairs:
                return True
        return False

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        candidates = sorted(
            [
                r for r in state.stygian_substantive
                if _is_substantive_for_contrast(r)
            ],
            key=lambda r: r.get("emitted_at", ""), reverse=True,
        )
        chosen = None
        for c in candidates:
            key = f"{self.id}|{c.get('record_id','')}"
            if key not in state.tried_pairs:
                chosen = c
                break
        if chosen is None:
            return None
        return self._build_claim(chosen, state)

    def _build_claim(self, s_row: dict, state: SwarmState) -> ComposedClaim:
        problem_id = (s_row.get("claim_payload") or {}).get("problem_id", "?")
        s_claim = s_row.get("canonical_claim_text", "")
        split = PROBLEM_BINARY_SPLITS.get(problem_id, GENERIC_BINARY_SPLIT)
        is_generic = problem_id not in PROBLEM_BINARY_SPLITS

        composed_id = f"EREBOS-G02-{problem_id}-x-{split['split_name']}"
        composition_text = (
            f"Contrast-claim {composed_id}: "
            f"the survival rate of the Stygian claim on `{problem_id}` "
            f"(\"{s_claim[:200]}\") is hypothesized to DIVERGE between "
            f"two binary-split groups: "
            f"Group A = {split['group_a_label']}; "
            f"Group B = {split['group_b_label']}. "
            f"Specifically: |survival_rate(A) - survival_rate(B)| > "
            f"{SURVIVAL_RATE_MARGIN_DELTA}. "
            f"If TRUE, the kill is structured by the categorical (rank, "
            f"CM-class, Salem-class, etc.) rather than uniformly "
            f"distributed -- the categorical is a load-bearing confound "
            f"or moderator of the claim's domain of validity."
        )
        if is_generic:
            composition_text += (
                f" NOTE: no problem-specific split registered for "
                f"{problem_id}; using generic even-vs-odd-degree split "
                f"as a Tier-S stand-in until problem-specific binary "
                f"is mapped."
            )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "stygian_record_id": s_row.get("record_id"),
                "stygian_problem_id": problem_id,
                "stygian_verdict": s_row.get("verdict"),
                "stygian_kill_pattern": s_row.get("kill_pattern"),
                "split_name": split["split_name"],
                "is_generic_split": is_generic,
            },
            transformation_description=(
                f"Split parent dataset by binary categorical "
                f"`{split['split_name']}`; compute per-group survival "
                f"rate of the parent claim; hypothesize divergence > "
                f"{SURVIVAL_RATE_MARGIN_DELTA}."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Permutation test: Stygian shuffles the group A/B "
                f"labels N={PERMUTATION_N} times. For each shuffle, "
                f"recomputes the survival-rate divergence. Observed "
                f"divergence is rejected as 'permutation_null' if it "
                f"falls within the central 95% of the shuffled "
                f"distribution. Compositon-aware Stygian loader needed: "
                f"must support per-group sub-sampling + survival-rate "
                f"computation. v0.11+ loader work."
            ),
            expected_kill_pattern="permutation_null",
            loader_feasibility_note=(
                f"EASY (Tier S): {split['data_filter_hint']}. "
                f"Permutation null is local computation, no new battery "
                f"primitives required. Composition-aware Stygian loader "
                f"must implement per-group sub-sampling, which is a "
                f"straightforward addition to the existing distribution "
                f"mode."
            ),
            parent_record_ids=[s_row.get("record_id", "")],
            composition_payload={
                "stygian_claim_text": s_claim,
                "split_metadata": split,
                "permutation_n": PERMUTATION_N,
                "margin_delta": SURVIVAL_RATE_MARGIN_DELTA,
            },
            extras={"is_generic_split": is_generic},
        )
