"""Generator 24: Symmetry / Twist.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 5.

Applies a symmetry transformation (most simply: a sign-flip /
x -> -x substitution on polynomials) and posits that an invariant
(Mahler measure) is conserved.

For polynomial claims: the substitution x -> -x preserves Mahler
measure exactly (because |P(-x)| roots are -roots, same absolute
values). G24's claim: "Mahler measure is conserved under x -> -x
substitution across the catalog."

If the catalog data is RIGHT (Mahler.py implementation is correct),
this claim trivially holds; G24's expected_kill_pattern (symmetry
breaking) becomes evidence of an instrument bug in the data,
not a substrate-level finding. Substrate-grade meta-finding.

If the catalog data has any subtle bug, G24 will surface it.

Erebos Implementation Spec:
- Input / Provenance: a confirmed-surviving claim involving Mahler
  measure (parent: BL-C-001, BL-C-003, BL-C-004 or any
  Erebos composition referencing these).
- Transformation: apply x -> -x to each polynomial; compute Mahler
  measure of twisted poly; compare to original.
- Output Claim: "Mahler measure is conserved under x -> -x for
  all entries in the Mossinghoff non-cyclotomic catalog."
- Falsification Route: enumerate twisted polynomials; compute
  Mahler via existing techne.lib.mahler_measure; check equality
  within numerical tolerance.
- Expected Kill Pattern: symmetry_breaking (any entry whose
  twisted Mahler differs from original signals catalog corruption
  or implementation bug).
- Loader Feasibility: Tier A. PARI is available via mahler.py.
- Reasoning Tier: R3 (abstraction: structural symmetry preserves
  invariant) + R7 (cross-form transfer: original-form vs twisted-
  form is a domain change).
"""
from __future__ import annotations

from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


# Mahler-related parent indicators (BL-C-* problems that test
# Mahler measure or related polynomial invariants).
MAHLER_PARENT_INDICATORS = {"BL-C-001", "BL-C-003", "BL-C-004",
                            "mahler", "lehmer", "salem"}


class SymmetryTwistGenerator:
    id = "g24_symmetry_twist"
    name = "Symmetry / Twist"
    spec_phase = 5
    feasibility_tier = "A"
    reasoning_tier = "R3"
    expected_kill_pattern = "symmetry_breaking"

    def _has_mahler_context(self, text: str) -> bool:
        text_lower = (text or "").lower()
        return any(ind.lower() in text_lower for ind in MAHLER_PARENT_INDICATORS)

    def _parent_pool(self, state: SwarmState) -> list[dict]:
        """G24 needs a Mahler-context parent. Search Stygian +
        Erebos ledgers for any claim referencing Mahler / Lehmer /
        Salem / BL-C-00[134]."""
        out = []
        for r in (list(state.stygian_substantive) + list(state.erebos_self_ledger)):
            if self._has_mahler_context(r.get("canonical_claim_text", "")):
                out.append(r)
        return out

    def _candidate_for_row(self, row: dict, state: SwarmState) -> Optional[dict]:
        rid = row.get("record_id", "")
        key = f"{self.id}|{rid}|x_to_minus_x"
        if key in state.tried_pairs:
            return None
        return {"transformation": "x_to_minus_x"}

    def applicable(self, state: SwarmState) -> bool:
        for r in self._parent_pool(state):
            if self._candidate_for_row(r, state) is not None:
                return True
        return False

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        pool = sorted(
            self._parent_pool(state),
            key=lambda r: r.get("emitted_at", ""), reverse=True,
        )
        for r in pool:
            cand = self._candidate_for_row(r, state)
            if cand is not None:
                return self._build_claim(r, cand)
        return None

    def _build_claim(self, parent_row: dict, cand: dict) -> ComposedClaim:
        rid = parent_row.get("record_id", "?")
        parent_text = parent_row.get("canonical_claim_text", "")
        parent_gen = parent_row.get("generator_id", "?")

        composed_id = (
            f"EREBOS-G24-symmetry_x_to_minus_x"
            f"-{parent_gen}_{rid[:12]}"
        )

        composition_text = (
            f"Symmetry-twist claim {composed_id}: "
            f"the parent claim from `{parent_gen}` "
            f"(\"{parent_text[:200]}\") references a Mahler-measure "
            f"context. The symmetry-twist hypothesis: Mahler measure "
            f"is conserved under the substitution `x -> -x` applied "
            f"to every polynomial in the catalog. Equivalently: for "
            f"each P(x) in Mossinghoff, M(P(x)) == M(P(-x)) within "
            f"numerical tolerance. This is a structural-symmetry "
            f"claim grounded in the resultant-product definition of "
            f"M (changing sign of roots leaves |roots| invariant)."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "parent_record_id": rid,
                "parent_generator_id": parent_gen,
                "parent_emitted_at": parent_row.get("emitted_at"),
                "transformation": "polynomial_x_to_minus_x",
                "invariant_under_test": "mahler_measure",
            },
            transformation_description=(
                "Apply x -> -x to each polynomial in the Mossinghoff "
                "catalog; recompute Mahler measure via techne.lib or "
                "prometheus_math.databases.mahler accessors; compare "
                "to original M within numerical tolerance."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                "Composition-aware Stygian loader enumerates entries "
                "in prometheus_math.databases.mahler.all_below(2.0); "
                "for each, applies x -> -x to the coeffs array (negate "
                "odd-index entries); recomputes M; compares to original "
                "with tolerance 1e-9. Any divergence > tolerance "
                "indicates symmetry_breaking -- either a polynomial-"
                "specific anomaly OR a catalog-data bug. Both are "
                "substrate-grade observations."
            ),
            expected_kill_pattern="symmetry_breaking",
            loader_feasibility_note=(
                "Tier A: PARI is already in repo (prometheus_math/"
                "databases/mahler.py uses it). Composition loader "
                "would call techne.lib.mahler_measure on each twisted "
                "coeff array. ~150 LOC."
            ),
            parent_record_ids=[rid],
            composition_payload={
                "transformation": "x_to_minus_x",
                "invariant_under_test": "mahler_measure",
                "tolerance": 1e-9,
            },
            extras={"symmetry_type": "sign_flip_of_indeterminate"},
        )
