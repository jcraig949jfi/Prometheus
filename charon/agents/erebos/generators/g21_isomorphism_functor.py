"""Generator 21: Isomorphism / Functor.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 5.

Beyond G07 Analogy (which maps invariant labels): G21 maps the
TRANSFORMATIONS between objects. Given two PROMOTED rows from
different domains that share a battery shape OR a kill_pattern,
hypothesize a functor F whose application to a morphism in Domain A
produces a morphism in Domain B that preserves the battery outcome.

Erebos Implementation Spec:
- Input / Provenance: two PROMOTED rows that
  (a) come from DIFFERENT domains (per G07's detect_domain), AND
  (b) share a battery-shape signature (a kill_pattern, a kill_vector
       overall.tier, or an explicit shared_attack tag).
- Transformation: emit a functor candidate F: Domain_A -> Domain_B
  that maps the parameter-bundle of A's PROMOTED claim to B's
  parameter-bundle, preserving the structural property both
  empirically survive.
- Output Claim: "Functor F : Domain_A -> Domain_B carries the
  transformation f(A) -> A' over to a transformation g(B) -> B';
  both survive the same battery shape <S>."
- Falsification Route: pick a non-trivial morphism in Domain_A (a
  PROMOTED-then-perturbed row), apply F, check whether F(morphism)
  holds in Domain_B's analogous test. If not, kill_pattern =
  functor_breaks.
- Expected Kill Pattern: functor_breaks (the candidate functor is
  not actually structure-preserving).
- Loader Feasibility: Tier C-MVP. Real category-theoretic
  validation requires a full per-domain morphism corpus; v0.13
  emits the conjecture for cross-domain analysis only.
- Reasoning Tier: R7 (cross-domain transfer at the morphism layer,
  one tier above G07's pattern-layer analogy) + R8 (the functor IS
  a conjecture about structure preservation).

DIFFERENTIATION vs G07 Analogy:
- G07 maps invariant NAMES (degree <-> conductor) using a
  hardcoded dictionary.
- G21 maps the TRANSFORMATIONS over those invariants and posits
  structure preservation.
- Both are cross-domain morphism conjectures, but G07 is dictionary-
  lookup level (R7-pattern) and G21 is functor-level (R7-morphism +
  R8-meta). Per feedback_agent_differentiation: overlap is fine;
  layer-of-operation distinguishes them.
"""
from __future__ import annotations

from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)
from charon.agents.erebos.generators.g07_analogy import detect_domain


def _battery_signature(row: dict) -> Optional[str]:
    """Extract a battery-shape signature: shared kill_pattern, or
    kill_vector overall.tier. Returns None if no signature available."""
    kp = row.get("kill_pattern")
    if kp:
        return f"kp:{kp}"
    kv = row.get("kill_vector") or {}
    overall = (kv.get("overall") or {})
    tier = overall.get("tier")
    if tier:
        return f"tier:{tier}"
    return None


def _is_promoted(row: dict) -> bool:
    return (row.get("verdict") or "").upper() == "PROMOTED"


def _domain_of(row: dict) -> Optional[str]:
    return detect_domain(row.get("canonical_claim_text", ""))


class IsomorphismFunctorGenerator:
    id = "g21_isomorphism_functor"
    name = "Isomorphism / Functor"
    spec_phase = 5
    feasibility_tier = "C"
    reasoning_tier = "R7"
    expected_kill_pattern = "functor_breaks"

    def _parent_pool(self, state: SwarmState) -> list[dict]:
        return (
            list(state.stygian_substantive)
            + list(state.pollux_substantive)
            + list(state.erebos_self_ledger)
        )

    def _find_pair(self, state: SwarmState) -> Optional[dict]:
        promoted = [r for r in self._parent_pool(state) if _is_promoted(r)]
        if len(promoted) < 2:
            return None
        # Index by (domain, signature) and search for cross-domain
        # signature matches. Stable iteration: sort by record_id.
        promoted_sorted = sorted(promoted, key=lambda r: r.get("record_id", ""))
        for i, row_a in enumerate(promoted_sorted):
            dom_a = _domain_of(row_a)
            sig_a = _battery_signature(row_a)
            if dom_a is None or sig_a is None:
                continue
            for row_b in promoted_sorted[i + 1:]:
                dom_b = _domain_of(row_b)
                sig_b = _battery_signature(row_b)
                if dom_b is None or sig_b is None:
                    continue
                if dom_a == dom_b:
                    continue  # need cross-domain
                if sig_a != sig_b:
                    continue  # need shared battery signature
                rid_a = row_a.get("record_id", "")
                rid_b = row_b.get("record_id", "")
                key = f"{self.id}|{rid_a}|{rid_b}|{sig_a}"
                if key in state.tried_pairs:
                    continue
                return {
                    "row_a": row_a, "row_b": row_b,
                    "dom_a": dom_a, "dom_b": dom_b,
                    "signature": sig_a,
                }
        return None

    def applicable(self, state: SwarmState) -> bool:
        return self._find_pair(state) is not None

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        pair = self._find_pair(state)
        if pair is None:
            return None
        return self._build_claim(pair)

    def _build_claim(self, pair: dict) -> ComposedClaim:
        row_a: dict = pair["row_a"]
        row_b: dict = pair["row_b"]
        dom_a: str = pair["dom_a"]
        dom_b: str = pair["dom_b"]
        sig: str = pair["signature"]
        rid_a = row_a.get("record_id", "?")
        rid_b = row_b.get("record_id", "?")
        text_a = row_a.get("canonical_claim_text", "")
        text_b = row_b.get("canonical_claim_text", "")

        composed_id = (
            f"EREBOS-G21-functor_{dom_a}_to_{dom_b}"
            f"-{rid_a[:8]}_x_{rid_b[:8]}"
        )

        composition_text = (
            f"Functor claim {composed_id}: "
            f"both parents are PROMOTED and share battery signature "
            f"`{sig}`. Parent A from domain `{dom_a}` "
            f"(\"{text_a[:140]}\") and Parent B from domain `{dom_b}` "
            f"(\"{text_b[:140]}\"). Hypothesis: there exists a "
            f"functor F : `{dom_a}` -> `{dom_b}` such that the "
            f"structural transformation that produced A's PROMOTED "
            f"status carries over (via F) to the transformation that "
            f"produced B's PROMOTED status. Falsification: pick a "
            f"non-trivial morphism in `{dom_a}` (a `{dom_a}`-PROMOTED "
            f"row that fails under one specific perturbation P_A); "
            f"apply F to construct F(P_A) in `{dom_b}`; re-run B's "
            f"test under F(P_A). If B's test does NOT mirror A's "
            f"failure pattern, kill_pattern = functor_breaks (the "
            f"candidate F is not actually structure-preserving)."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "row_a_record_id": rid_a,
                "row_b_record_id": rid_b,
                "row_a_domain": dom_a,
                "row_b_domain": dom_b,
                "shared_battery_signature": sig,
                "row_a_text": text_a[:300],
                "row_b_text": text_b[:300],
            },
            transformation_description=(
                f"Identify two PROMOTED rows from distinct domains "
                f"(`{dom_a}`, `{dom_b}`) sharing battery signature "
                f"`{sig}`; emit functor candidate F : {dom_a} -> "
                f"{dom_b} carrying transformations between objects "
                f"and predicting cross-domain structure preservation. "
                f"This is the morphism-layer analog of G07's pattern-"
                f"layer analogy."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Composition-aware loader (deferred to v0.15+) would: "
                f"(a) enumerate `{dom_a}`-domain morphisms whose "
                f"application to Parent A causes it to flip from "
                f"PROMOTED to REJECTED; "
                f"(b) for each such morphism P_A, construct the "
                f"corresponding `{dom_b}`-domain morphism F(P_A) using "
                f"a per-domain object-translation table; "
                f"(c) apply F(P_A) to Parent B and re-run B's test; "
                f"(d) if B does not flip the same way A flipped, "
                f"kill_pattern = functor_breaks; (e) if B flips "
                f"identically, the functor candidate survives one "
                f"empirical adversarial step (substrate-grade weak "
                f"evidence the analogy is structural)."
            ),
            expected_kill_pattern="functor_breaks",
            loader_feasibility_note=(
                f"Tier C-MVP: Erebos can EMIT the conjecture today; "
                f"falsification requires per-domain morphism enumerators "
                f"(deferred). The shared-battery-signature heuristic is "
                f"a cheap proxy for 'might be functorially related' -- "
                f"most pairings WILL produce functor_breaks under any "
                f"adversarial morphism, which is the expected default."
            ),
            parent_record_ids=[rid_a, rid_b],
            composition_payload={
                "row_a_domain": dom_a,
                "row_b_domain": dom_b,
                "shared_battery_signature": sig,
                "candidate_functor_label": f"F_{dom_a}_to_{dom_b}_v0.13",
            },
            extras={"transfer_type": "morphism_functor_mvp"},
        )
