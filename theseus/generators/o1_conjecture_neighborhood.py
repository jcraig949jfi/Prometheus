"""O1 — conjecture-neighborhood generator (real, Stage 15).

Emits claims of the form:

    Theorem T with assumption A relaxed via OPERATOR ⇒ conclusion C'

Real implementation (Stage 15): a curated catalog of ≥ 5 theorems,
each with multiple hypotheses. A registry of ≥ 5 perturbation
OPERATORS that mechanically transform one hypothesis to a related-
but-weakened form. The generator iterates (theorem × hypothesis ×
operator) cross-product, emitting one record per applicable
perturbation.

Distinguished from stub: stub hand-coded N records each with a
hand-written perturbation. Real version applies operators
SYSTEMATICALLY across the catalog, generating combinatorially
more records and exercising the SHAPE (hypothesis perturbation)
not the content.

Plan: pivot/techne_5gen_plan_2026-05-27.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Callable

from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.base import Generator, GeneratorStatus, GeneratorRole


# ---------------------------------------------------------------------------
# Theorem catalog
# ---------------------------------------------------------------------------
# Each theorem: id, statement, ordered list of hypotheses (each tagged
# with a "kind" so perturbation operators know which hypotheses they
# apply to), conclusion.
# ---------------------------------------------------------------------------


THEOREM_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "mazur_torsion",
        "statement": (
            "An elliptic curve over Q has torsion subgroup isomorphic "
            "to one of 15 specific finite abelian groups"
        ),
        "hypotheses": [
            {"kind": "field_of_definition", "text": "E defined over Q"},
            {"kind": "field_of_consideration",
             "text": "torsion subgroup considered over Q"},
        ],
        "conclusion": "torsion subgroup ∈ {Z/n, Z/2×Z/2n} for specific n",
    },
    {
        "id": "faltings_finiteness",
        "statement": (
            "A curve of genus ≥ 2 over a number field has finitely "
            "many K-rational points"
        ),
        "hypotheses": [
            {"kind": "object_type", "text": "C smooth projective curve"},
            {"kind": "numeric_threshold", "text": "genus(C) ≥ 2"},
            {"kind": "field_of_definition", "text": "K a number field"},
        ],
        "conclusion": "C(K) is finite",
    },
    {
        "id": "sato_tate_non_cm",
        "statement": (
            "For a non-CM elliptic curve E over Q, the normalized "
            "Frobenius angles equidistribute according to the "
            "Sato-Tate (sin²) measure"
        ),
        "hypotheses": [
            {"kind": "object_property", "text": "E non-CM"},
            {"kind": "field_of_definition", "text": "E defined over Q"},
        ],
        "conclusion": "Frobenius angles distributed as sin² on [0, π]",
    },
    {
        "id": "manin_drinfeld",
        "statement": (
            "Cusps of modular curve X_0(N) generate a finite subgroup "
            "of the Jacobian"
        ),
        "hypotheses": [
            {"kind": "object_type", "text": "X_0(N) modular curve of level N"},
            {"kind": "divisor_type", "text": "degree-0 cusp divisors"},
        ],
        "conclusion": "cusp divisor classes are torsion in Jac(X_0(N))",
    },
    {
        "id": "fermat_last_theorem",
        "statement": (
            "For n > 2, the equation x^n + y^n = z^n has no nontrivial "
            "integer solutions"
        ),
        "hypotheses": [
            {"kind": "numeric_threshold", "text": "n > 2"},
            {"kind": "ring", "text": "x, y, z ∈ Z"},
            {"kind": "object_property", "text": "x, y, z all nonzero"},
        ],
        "conclusion": "no such (x, y, z) exists",
    },
    {
        "id": "fundamental_theorem_arithmetic",
        "statement": (
            "Every integer n > 1 has a unique factorization into primes"
        ),
        "hypotheses": [
            {"kind": "numeric_threshold", "text": "n > 1"},
            {"kind": "ring", "text": "n ∈ Z"},
        ],
        "conclusion": "n = p_1^a_1 · ... · p_k^a_k unique up to ordering",
    },
    {
        "id": "modularity_theorem",
        "statement": (
            "Every elliptic curve over Q is modular (associated to a "
            "weight-2 newform of level N=conductor)"
        ),
        "hypotheses": [
            {"kind": "field_of_definition", "text": "E defined over Q"},
            {"kind": "object_type", "text": "E elliptic curve"},
        ],
        "conclusion": "∃ newform f of level conductor(E) with L(E,s) = L(f,s)",
    },
]


# ---------------------------------------------------------------------------
# Perturbation operators
# ---------------------------------------------------------------------------
# Each operator: id, applicable_kinds (set of hypothesis kinds it can
# mutate), apply_fn(hypothesis_text) → perturbed_text, conjectured_effect.
# ---------------------------------------------------------------------------


def _op_extend_field_to_qbar(text: str) -> str:
    return (text.replace("over Q", "over Q-bar")
                .replace("Q a number field", "Q-bar (algebraic closure)"))


def _op_extend_field_to_local(text: str) -> str:
    return text.replace("over Q", "over Q_p (p-adic)")


def _op_weaken_numeric_threshold(text: str) -> str:
    return (text.replace("≥ 2", "≥ 1")
                .replace("> 2", "> 1")
                .replace("> 1", "> 0"))


def _op_strengthen_numeric_threshold(text: str) -> str:
    return text.replace("≥ 2", "≥ 3").replace("> 2", "> 3")


def _op_remove_object_property(text: str) -> str:
    if "non-CM" in text:
        return text.replace("non-CM", "with CM")
    if "all nonzero" in text:
        return text.replace("all nonzero", "possibly zero")
    if "smooth projective" in text:
        return text.replace("smooth projective", "singular")
    return f"NOT ({text})"


def _op_change_ring_to_rationals(text: str) -> str:
    return text.replace("∈ Z", "∈ Q")


def _op_change_ring_to_padics(text: str) -> str:
    return text.replace("∈ Z", "∈ Z_p (p-adic integers)")


def _op_change_object_type_to_higher_genus(text: str) -> str:
    if "elliptic curve" in text.lower():
        return text.replace("elliptic curve", "curve of genus 2")
    if "X_0(N)" in text:
        return text.replace("X_0(N)", "X_1(N)")
    return text + " (higher-dimensional analog)"


def _op_change_divisor_degree(text: str) -> str:
    return text.replace("degree-0", "arbitrary-degree")


PERTURBATION_OPERATORS: List[Dict[str, Any]] = [
    {
        "id": "extend_field_to_algebraic_closure",
        "applicable_kinds": {"field_of_definition", "field_of_consideration"},
        "apply_fn": _op_extend_field_to_qbar,
        "conjectured_effect": (
            "classification may open up — more objects become admissible"
        ),
        "perturbation_strength": "moderate",
    },
    {
        "id": "extend_field_to_local",
        "applicable_kinds": {"field_of_definition"},
        "apply_fn": _op_extend_field_to_local,
        "conjectured_effect": (
            "local properties replace global; arithmetic information changes"
        ),
        "perturbation_strength": "qualitative",
    },
    {
        "id": "weaken_numeric_threshold",
        "applicable_kinds": {"numeric_threshold"},
        "apply_fn": _op_weaken_numeric_threshold,
        "conjectured_effect": (
            "conclusion may fail in the newly-admitted boundary cases"
        ),
        "perturbation_strength": "destroys_conclusion",
    },
    {
        "id": "strengthen_numeric_threshold",
        "applicable_kinds": {"numeric_threshold"},
        "apply_fn": _op_strengthen_numeric_threshold,
        "conjectured_effect": (
            "conclusion strengthens but applies to fewer objects"
        ),
        "perturbation_strength": "moderate",
    },
    {
        "id": "remove_object_property",
        "applicable_kinds": {"object_property"},
        "apply_fn": _op_remove_object_property,
        "conjectured_effect": (
            "removing the discriminating property usually breaks "
            "the conclusion's structure"
        ),
        "perturbation_strength": "destroys_conclusion",
    },
    {
        "id": "change_ring_to_Q",
        "applicable_kinds": {"ring"},
        "apply_fn": _op_change_ring_to_rationals,
        "conjectured_effect": (
            "moving from Z to Q usually trivializes integer-arithmetic "
            "conclusions"
        ),
        "perturbation_strength": "destroys_conclusion",
    },
    {
        "id": "change_ring_to_padic",
        "applicable_kinds": {"ring"},
        "apply_fn": _op_change_ring_to_padics,
        "conjectured_effect": (
            "p-adic version preserves some structure but loses unique "
            "factorization in the limit"
        ),
        "perturbation_strength": "qualitative",
    },
    {
        "id": "change_object_type",
        "applicable_kinds": {"object_type"},
        "apply_fn": _op_change_object_type_to_higher_genus,
        "conjectured_effect": (
            "higher-genus / dimension analogs typically need replaced "
            "machinery; conclusion form changes"
        ),
        "perturbation_strength": "qualitative",
    },
    {
        "id": "change_divisor_degree",
        "applicable_kinds": {"divisor_type"},
        "apply_fn": _op_change_divisor_degree,
        "conjectured_effect": (
            "removing degree-0 restriction usually breaks the torsion "
            "conclusion"
        ),
        "perturbation_strength": "delicate",
    },
]


class O1ConjectureNeighborhoodGenerator(Generator):
    generator_id = "o1"
    claim_kind = ClaimKind.CONJECTURE_NEIGHBORHOOD.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    def __init__(self, batch_id: str) -> None:
        super().__init__(batch_id)
        # Pre-compute (theorem × hypothesis × operator) applications.
        self._queue: List[Dict[str, Any]] = []
        for thm in THEOREM_CATALOG:
            for h_idx, hyp in enumerate(thm["hypotheses"]):
                for op in PERTURBATION_OPERATORS:
                    if hyp["kind"] not in op["applicable_kinds"]:
                        continue
                    perturbed = op["apply_fn"](hyp["text"])
                    if perturbed == hyp["text"]:
                        continue  # operator was a no-op for this text
                    self._queue.append({
                        "theorem": thm,
                        "hypothesis_index": h_idx,
                        "original_hypothesis": hyp,
                        "operator": op,
                        "perturbed_hypothesis_text": perturbed,
                    })
        self._cursor = 0

    def description(self) -> str:
        return (
            f"o1: conjecture-neighborhood (real) — "
            f"{len(THEOREM_CATALOG)} theorems × "
            f"{len(PERTURBATION_OPERATORS)} operators "
            f"= {len(self._queue)} applicable (theorem, hypothesis, operator) "
            f"triples"
        )

    def next(self) -> Optional[TheseusRecord]:
        if self._cursor >= len(self._queue):
            return None
        item = self._queue[self._cursor]
        self._cursor += 1
        self.attempts += 1

        thm = item["theorem"]
        op = item["operator"]
        orig_hyp = item["original_hypothesis"]
        h_idx = item["hypothesis_index"]
        pert_text = item["perturbed_hypothesis_text"]

        canonical = (
            f"O1_NEIGHBORHOOD[{thm['id']}/{op['id']}] "
            f"perturb hypothesis #{h_idx} ('{orig_hyp['text']}') "
            f"→ '{pert_text}' ⇒ {op['conjectured_effect']}"
        )
        record_id = TheseusRecord.compute_record_id(canonical, self.generator_id)
        self.emitted.append(record_id)

        return TheseusRecord(
            record_id=record_id,
            generator_id=self.generator_id,
            batch_id=self.batch_id,
            emitted_at=datetime.now(timezone.utc).isoformat(),
            claim_kind=self.claim_kind,
            claim_payload={
                "source_theorem": thm["id"],
                "theorem_statement": thm["statement"],
                "original_hypotheses": [h["text"] for h in thm["hypotheses"]],
                "perturbed_hypothesis_index": h_idx,
                "perturbed_hypothesis": pert_text,
                "perturbation_operator": op["id"],
                "perturbation_strength": op["perturbation_strength"],
                "conjectured_conclusion_change": op["conjectured_effect"],
                "logical_form": "hypothesis_perturbation",
            },
            canonical_claim_text=canonical,
            verdict=Verdict.UNVERIFIED.value,
        )
