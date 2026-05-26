"""Generator 12: Invariant Substitution.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 3 + research
notes pivot/erebos_g12_invariant_substitution_research_2026-05-26.md.

Brute-force mutation of internal nodes of a claim. Swaps Invariant
A for Invariant A' based on a curated similarity matrix.

Erebos Implementation Spec:
- Input / Provenance: Any baseline claim (Stygian / Pollux / Erebos)
  whose canonical_claim_text mentions a KNOWN_INVARIANT.
- Transformation: Pick highest-similarity off-diagonal substitution
  (excluding already-tried).
- Output Claim: "Relation R holds for [substituted invariant]
  instead of the original [invariant]."
- Falsification Route: Standard battery on the substituted claim.
- Expected Kill Pattern: syntactic_or_semantic_failure.
- Loader Feasibility: EASY (Tier A in Charon-state because the
  matrix needs curation but the substitution is mechanical).
- Reasoning Tier: R3 (abstraction) + R7 (cross-domain transfer
  when substitution crosses domains).
"""
from __future__ import annotations

import re
from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


# All invariants we recognize. Substitution only fires on parent
# claims containing one of these as a whole word.
KNOWN_INVARIANTS: set[str] = {
    # Mahler-measure-adjacent
    "mahler_measure", "degree", "salem_class", "smyth_extremal",
    "cyclotomic", "cyclotomic_flag",
    # BSD / elliptic-curve
    "rank", "conductor", "regulator", "L1", "tamagawa_product",
    "torsion", "cm_flag", "cm", "real_period", "sha_an",
    # Pollux pair-shape (handled as same-domain substitution
    # within Pollux's coordinate space)
    "corr_raw", "corr_norm", "n_paired",
}

# Symmetric similarity matrix. Score in [0, 1]. Hand-curated v0.9
# MVP per pivot/erebos_g12_invariant_substitution_research_2026-05-26.md
# Stored as a dict with frozenset keys for symmetry.
_SIM_RAW: dict[tuple[str, str], float] = {
    # Mahler domain
    ("mahler_measure", "degree"): 0.30,
    ("mahler_measure", "salem_class"): 0.20,
    ("mahler_measure", "smyth_extremal"): 0.30,
    ("mahler_measure", "cyclotomic_flag"): 0.40,
    ("degree", "salem_class"): 0.50,
    ("degree", "smyth_extremal"): 0.40,
    ("degree", "cyclotomic_flag"): 0.60,
    ("salem_class", "smyth_extremal"): 0.70,
    ("salem_class", "cyclotomic_flag"): 0.40,
    ("smyth_extremal", "cyclotomic_flag"): 0.30,
    # BSD domain
    ("rank", "conductor"): 0.30,
    ("rank", "regulator"): 0.70,
    ("rank", "L1"): 0.70,
    ("rank", "tamagawa_product"): 0.20,
    ("rank", "torsion"): 0.30,
    ("rank", "cm_flag"): 0.50,
    ("rank", "cm"): 0.50,
    ("rank", "real_period"): 0.40,
    ("rank", "sha_an"): 0.50,
    ("conductor", "regulator"): 0.20,
    ("conductor", "L1"): 0.30,
    ("conductor", "tamagawa_product"): 0.50,
    ("conductor", "torsion"): 0.20,
    ("conductor", "cm_flag"): 0.30,
    ("conductor", "real_period"): 0.20,
    ("conductor", "sha_an"): 0.20,
    ("regulator", "L1"): 0.60,
    ("regulator", "tamagawa_product"): 0.20,
    ("regulator", "real_period"): 0.40,
    ("regulator", "sha_an"): 0.40,
    ("L1", "tamagawa_product"): 0.30,
    ("L1", "real_period"): 0.40,
    ("L1", "sha_an"): 0.50,
    ("tamagawa_product", "torsion"): 0.40,
    ("tamagawa_product", "real_period"): 0.20,
    ("torsion", "cm_flag"): 0.50,
    ("torsion", "cm"): 0.50,
    ("cm_flag", "cm"): 1.00,  # synonym
    ("real_period", "sha_an"): 0.20,
    # Pollux pair-shape (intra-Pollux coordinate substitution)
    ("corr_raw", "corr_norm"): 0.60,
    ("corr_raw", "n_paired"): 0.10,
    ("corr_norm", "n_paired"): 0.10,
}


def _sim(a: str, b: str) -> float:
    """Symmetric similarity lookup. 1.0 on diagonal; 0.0 if no
    registered pair (cross-domain substitution defaults to 0)."""
    if a == b:
        return 1.0
    if (a, b) in _SIM_RAW:
        return _SIM_RAW[(a, b)]
    if (b, a) in _SIM_RAW:
        return _SIM_RAW[(b, a)]
    return 0.0


def find_invariants_in_text(text: str) -> set[str]:
    """Return set of KNOWN_INVARIANTS appearing as whole-word tokens
    in the text."""
    found = set()
    text_lower = (text or "").lower()
    for inv in KNOWN_INVARIANTS:
        # Whole-word match (allow underscores in token chars)
        pattern = r"\b" + re.escape(inv.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found.add(inv)
    return found


def pick_best_substitution(
    original: str, tried_targets: set[str]
) -> Optional[tuple[str, float]]:
    """Among all KNOWN_INVARIANTS, return (best_target, similarity)
    that hasn't been tried for this original. None if no candidate."""
    best: Optional[tuple[str, float]] = None
    for target in KNOWN_INVARIANTS:
        if target == original:
            continue
        if target in tried_targets:
            continue
        sim = _sim(original, target)
        if sim <= 0:
            continue
        if best is None or sim > best[1]:
            best = (target, sim)
    return best


class InvariantSubstitutionGenerator:
    id = "g12_invariant_substitution"
    name = "Invariant Substitution"
    spec_phase = 3
    feasibility_tier = "A"
    reasoning_tier = "R3"
    expected_kill_pattern = "syntactic_or_semantic_failure"

    def _parent_pool(self, state: SwarmState) -> list[dict]:
        """All substantive rows the substitution can operate on
        (Stygian + Pollux + Erebos self-ledger)."""
        return (
            list(state.stygian_substantive)
            + list(state.pollux_substantive)
            + list(state.erebos_self_ledger)
        )

    def _candidate_for_row(
        self, row: dict, state: SwarmState
    ) -> Optional[tuple[str, str, float]]:
        """Find first uncomposed (original, target) substitution pair
        for this parent row. Returns (original_invariant,
        target_invariant, similarity) or None."""
        text = row.get("canonical_claim_text", "")
        invariants = find_invariants_in_text(text)
        if not invariants:
            return None
        rid = row.get("record_id", "")
        for original in sorted(invariants):
            # Pre-extract tried targets for this (rid, original)
            tried_targets = set()
            for k in state.tried_pairs:
                if k.startswith(f"{self.id}|{rid}|{original}|"):
                    tried_targets.add(k.split("|")[-1])
            pick = pick_best_substitution(original, tried_targets)
            if pick is not None:
                target, sim = pick
                return (original, target, sim)
        return None

    def applicable(self, state: SwarmState) -> bool:
        for r in self._parent_pool(state):
            if self._candidate_for_row(r, state) is not None:
                return True
        return False

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        # Newest first across the combined pool
        pool = sorted(
            self._parent_pool(state),
            key=lambda r: r.get("emitted_at", ""), reverse=True,
        )
        for r in pool:
            cand = self._candidate_for_row(r, state)
            if cand is not None:
                return self._build_claim(r, cand)
        return None

    def _build_claim(
        self, parent_row: dict, cand: tuple[str, str, float]
    ) -> ComposedClaim:
        original, target, sim = cand
        parent_id = parent_row.get("record_id", "?")
        parent_gen = parent_row.get("generator_id", "?")
        parent_claim = parent_row.get("canonical_claim_text", "")

        composed_id = (
            f"EREBOS-G12-sub_{original}_to_{target}-from_{parent_gen}_{parent_id[:12]}"
        )

        composition_text = (
            f"Invariant-substitution claim {composed_id}: "
            f"in the parent claim from generator `{parent_gen}` "
            f"(\"{parent_claim[:200]}\"), substitute the invariant "
            f"`{original}` with `{target}` (similarity score "
            f"{sim:.2f}). The hypothesis is that the parent claim's "
            f"relation -- whatever it was -- is also valid (or "
            f"fails interestingly) for `{target}` in place of "
            f"`{original}`. If the substitution produces a "
            f"syntactic / semantic failure, the original invariant "
            f"was load-bearing (the relation is not fungible over "
            f"the invariant family). If the substituted claim "
            f"survives, the original invariant was decorative -- "
            f"the relation is genuinely about the abstraction the "
            f"two invariants share."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "parent_record_id": parent_id,
                "parent_generator_id": parent_gen,
                "parent_emitted_at": parent_row.get("emitted_at"),
                "original_invariant": original,
                "substituted_invariant": target,
                "similarity_score": sim,
                "invariants_present_in_parent": sorted(
                    find_invariants_in_text(parent_claim)
                ),
            },
            transformation_description=(
                f"Substitute `{original}` -> `{target}` (similarity "
                f"{sim:.2f}) in parent claim text. AST-style "
                f"node-swap MVP; uses curated similarity matrix per "
                f"erebos_g12_invariant_substitution_research_2026-05-26.md."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Standard Stygian battery on the substituted claim. "
                f"Composition-aware loader rebuilds the parent's data "
                f"context with `{original}` replaced by `{target}` "
                f"(requires invariant-mapping table per domain). "
                f"If battery produces type errors or unsupported-operation "
                f"failures, kill_pattern = syntactic_or_semantic_failure. "
                f"If battery produces a clean PROMOTED/REJECTED verdict, "
                f"the substitution succeeded -- substrate-grade evidence "
                f"that the parent relation is fungible over the {original}/"
                f"{target} pair. Composition-aware loader (task #37) "
                f"required for actual execution; currently short-circuits."
            ),
            expected_kill_pattern="syntactic_or_semantic_failure",
            loader_feasibility_note=(
                f"EASY (Tier A): substitution table is mechanical; the "
                f"loader needs a per-domain mapping from invariant name "
                f"to dataset accessor (e.g., 'rank' -> "
                f"bsd_rich entries.base.rank; 'regulator' -> "
                f"entries.rich.regulator). Per-domain mappings curated "
                f"as the loader ships."
            ),
            parent_record_ids=[parent_id],
            composition_payload={
                "original_invariant": original,
                "substituted_invariant": target,
                "similarity_score": sim,
            },
            extras={
                "matrix_version": "g12_v0.9_mvp",
            },
        )
