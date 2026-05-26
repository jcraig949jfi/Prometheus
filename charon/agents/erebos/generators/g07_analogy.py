"""Generator 7: Analogy.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 2.

Cross-domain morphism: translates a pattern from Domain A (e.g.,
Mahler/polynomials) to Domain B (e.g., knots, elliptic curves)
using a hardcoded analogy dictionary.

Erebos Implementation Spec:
- Input / Provenance: Stygian or Erebos rows referencing
  invariants from Domain A.
- Transformation: apply analogy dictionary A → B; emit "the same
  pattern holds with B-invariants substituted for A-invariants."
- Output Claim: "Structural analogue of <pattern> in Domain B
  using mapped invariants."
- Falsification Route: run the same battery shape on Domain B's
  dataset.
- Expected Kill Pattern: metaphor_collapse (analogy is poetic
  but mathematically incoherent; type errors or random noise).
- Loader Feasibility: Tier C-MVP. Tiny hardcoded dictionary; full
  category-theoretic mapping deferred to G21 Isomorphism.
- Reasoning Tier: R7 (cross-domain transfer is R7 by definition) +
  R3 (abstraction).

MVP dictionary (v0.12 — small, hand-curated; expand in future
iterations):

  Mahler domain          ↔ Knot domain
  -------------          ↔ -----------
  degree                 ↔ crossing_number
  mahler_measure         ↔ log_alexander_root
  salem_class            ↔ alternating_class

  Mahler domain          ↔ BSD elliptic-curve domain
  -------------          ↔ -------------------------
  degree                 ↔ conductor
  mahler_measure         ↔ regulator
  cyclotomic_flag        ↔ cm_flag

These pairings are EDUCATED GUESSES; the falsification flow tests
each empirically. Metaphor-collapse is the expected default
outcome for most pairings.
"""
from __future__ import annotations

from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


# Analogy dictionary v0.12.
# Each tuple: (source_domain, source_invariant) -> (target_domain, target_invariant)
ANALOGY_MAP: dict[tuple[str, str], tuple[str, str]] = {
    # Mahler → Knot
    ("mahler", "degree"): ("knot", "crossing_number"),
    ("mahler", "mahler_measure"): ("knot", "log_alexander_root"),
    ("mahler", "salem_class"): ("knot", "alternating_class"),
    # Mahler → BSD elliptic curves
    ("mahler", "degree"): ("bsd", "conductor"),
    ("mahler", "mahler_measure"): ("bsd", "regulator"),
    ("mahler", "cyclotomic_flag"): ("bsd", "cm_flag"),
    # Knot → BSD
    ("knot", "crossing_number"): ("bsd", "conductor"),
}

# Detection of domain from parent text. Hard-coded indicator
# tokens.
DOMAIN_INDICATORS = {
    "mahler": ["mahler", "lehmer", "salem", "BL-C-001", "BL-C-003", "BL-C-004"],
    "knot": ["knot", "crossing_number", "alexander", "jones"],
    "bsd": ["BSD", "BL-C-002", "elliptic", "rank", "conductor", "regulator"],
}


def detect_domain(text: str) -> Optional[str]:
    """Identify which domain a claim text references."""
    text_lower = (text or "").lower()
    for dom, indicators in DOMAIN_INDICATORS.items():
        for ind in indicators:
            if ind.lower() in text_lower:
                return dom
    return None


class AnalogyGenerator:
    id = "g07_analogy"
    name = "Analogy"
    spec_phase = 2
    feasibility_tier = "C"  # MVP tier; full category-theory in G21
    reasoning_tier = "R7"
    expected_kill_pattern = "metaphor_collapse"

    def _candidate_for_row(self, row: dict, state: SwarmState) -> Optional[dict]:
        text = row.get("canonical_claim_text", "")
        source_dom = detect_domain(text)
        if source_dom is None:
            return None
        # Find ANY analogy entry whose source matches the detected
        # domain
        candidates = [
            (src, tgt) for src, tgt in ANALOGY_MAP.items()
            if src[0] == source_dom
        ]
        if not candidates:
            return None
        rid = row.get("record_id", "")
        for src, tgt in candidates:
            key = f"{self.id}|{rid}|{src}->{tgt}"
            if key not in state.tried_pairs:
                return {"source": src, "target": tgt}
        return None

    def _parent_pool(self, state: SwarmState) -> list[dict]:
        return (
            list(state.stygian_substantive)
            + list(state.erebos_self_ledger)
            + list(state.pollux_substantive)
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
        src_dom, src_inv = cand["source"]
        tgt_dom, tgt_inv = cand["target"]
        rid = parent_row.get("record_id", "?")
        parent_text = parent_row.get("canonical_claim_text", "")
        parent_gen = parent_row.get("generator_id", "?")

        composed_id = (
            f"EREBOS-G07-analogy_{src_dom}_{src_inv}_to_{tgt_dom}_{tgt_inv}"
            f"-{parent_gen}_{rid[:12]}"
        )

        composition_text = (
            f"Analogy claim {composed_id}: "
            f"the parent claim from `{parent_gen}` "
            f"(\"{parent_text[:200]}\") operates in the `{src_dom}` "
            f"domain over invariant `{src_inv}`. The cross-domain "
            f"analogue posits the same structural pattern in the "
            f"`{tgt_dom}` domain with `{src_inv}` -> `{tgt_inv}`. "
            f"This is an educated guess (v0.12 hardcoded "
            f"dictionary); falsification expected to produce "
            f"`metaphor_collapse` for most pairings. PROMOTED would "
            f"be substrate-grade evidence the analogy is structural, "
            f"not merely poetic."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "parent_record_id": rid,
                "parent_generator_id": parent_gen,
                "parent_emitted_at": parent_row.get("emitted_at"),
                "source_domain": src_dom,
                "source_invariant": src_inv,
                "target_domain": tgt_dom,
                "target_invariant": tgt_inv,
            },
            transformation_description=(
                f"Detect parent domain (`{src_dom}`); look up analogy "
                f"dictionary v0.12; substitute source invariant "
                f"`{src_inv}` with target invariant `{tgt_inv}` in "
                f"the target domain `{tgt_dom}`."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Composition-aware loader (future v0.14+) would: "
                f"(a) re-run the parent's test shape on a `{tgt_dom}`-"
                f"domain dataset (e.g., bsd_rich for BSD, "
                f"prometheus_math.databases.knots for knot domain); "
                f"(b) substitute references to `{src_inv}` with "
                f"`{tgt_inv}`; (c) check whether the analogous claim "
                f"survives or fails. Type errors / structural "
                f"incoherence -> kill_pattern = metaphor_collapse."
            ),
            expected_kill_pattern="metaphor_collapse",
            loader_feasibility_note=(
                "Tier C-MVP: requires cross-domain dataset accessors "
                "and per-domain claim-test translation. v0.14+ work. "
                "Full category-theoretic mapping with explicit "
                "functorial structure is G21 Isomorphism territory."
            ),
            parent_record_ids=[rid],
            composition_payload={
                "source_domain": src_dom,
                "source_invariant": src_inv,
                "target_domain": tgt_dom,
                "target_invariant": tgt_inv,
                "dictionary_version": "v0.12_mvp",
            },
            extras={"transfer_type": "domain_morphism_mvp"},
        )
