"""prometheus_math.encodings.large_cardinal_consistency — minimal
formal-theory + consistency-strength relation primitives.

Per inbox ticket T-2026-05-07-T027 (P2). Mini contract-change window
2026-05-10 (orthogonal to Aporia Phase-2 5-meta-primitive plan; this
primitive is foundations/logic, not in any of the 5 meta categories).

Design doc: ``prometheus_math/encodings/large_cardinal_consistency_GAP.md``.

Per HARD-5: this module's substrate-grade observation is the
``ConsistencyRelation`` shape — a typed implication ``Con(stronger) ->
Con(weaker)``. The "large cardinal" framing is metadata; the substrate
only needs the relation as an operator output. The same ``ConsistencyRelation``
primitive applies to forcing-extension relations, inner-model
constructions, axiomatic-inclusion (subset) relations, and
representation-via-interpretation.

Per HARD-4 + critical_memories.md: large-cardinal / categorical
foundations is on the substrate's hunt list for under-explored
mathematical territory. This primitive enables the substrate to ingest
foundations-level results without a domain-specific encoding pass.

Two additive frozen dataclasses; can ship in a single small module.
Real value comes when paired with a Lean/Coq formalism backend (out of
scope here; ``axiomatization_lang`` field reserves the slot).

Cross-references
----------------
- Design: ``prometheus_math/encodings/large_cardinal_consistency_GAP.md``
- HARD-4 (calibration anchors in foundations / set theory)
- HARD-5 (relation IS the operator output; "large cardinal" is metadata)
- Sister primitive: ``OperatorOutputSequence`` in maass_form_hecke.py
  (same additive-encoding pattern)
"""
from __future__ import annotations

import enum
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Vocabulary (closed enums so the substrate's certifying-weight discipline
# can attach methods to specific kinds — avoids silent fallthrough on
# unknown justification methods).
# ---------------------------------------------------------------------------


class AxiomatizationLang(str, enum.Enum):
    """The encoding of a FormalTheory's axioms.

    INFORMAL is the default; substrate accepts citation-pointer
    justifications without a formal proof artifact. The other values
    reserve slots for Lean / Coq / Metamath integration when those
    backends become available.
    """
    INFORMAL = "informal"
    LEAN4 = "lean4"
    COQ = "coq"
    METAMATH = "metamath"


class JustificationMethod(str, enum.Enum):
    """How a ConsistencyRelation is established.

    - AXIOMATIC_INCLUSION: weaker theory's axioms are a subset of stronger's
    - INTERPRETATION: weaker is interpretable in stronger
    - INNER_MODEL: stronger constructs an inner model satisfying weaker
    - FORCING: stronger establishes weaker via forcing extension
    - RELATIVE_CONSISTENCY_PROOF: free-form citation pointer
    """
    AXIOMATIC_INCLUSION = "axiomatic_inclusion"
    INTERPRETATION = "interpretation"
    INNER_MODEL = "inner_model"
    FORCING = "forcing"
    RELATIVE_CONSISTENCY_PROOF = "relative_consistency_proof"


VALID_AXIOMATIZATION_LANGS = tuple(m.value for m in AxiomatizationLang)
VALID_JUSTIFICATION_METHODS = tuple(m.value for m in JustificationMethod)


# ---------------------------------------------------------------------------
# FormalTheory — registered axiomatic theory
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FormalTheory:
    """A registered formal axiomatic theory.

    Substrate-grade: a content-addressed reference to the theory's
    axioms (as a hash-pointer). Whether the axioms are encoded
    informally, in Lean4, in Coq, or in Metamath is metadata
    (``axiomatization_lang``); the substrate-grade identity is
    ``(theory_id, axioms_hash)``.

    Attributes
    ----------
    theory_id : str
        Human-readable name. Examples: ``"ZFC"``,
        ``"ZFC_plus_measurable_cardinal"``, ``"PA"``,
        ``"ZFC_plus_neg_SCH"``.
    axioms_hash : str
        sha256 of the axioms encoding (or canonical reference to a
        registered axiomatization). Substrate uses this for content-
        addressed identity; two FormalTheory instances with the same
        ``axioms_hash`` are considered the SAME theory regardless of
        ``theory_id`` differences.
    axiomatization_lang : str
        One of ``VALID_AXIOMATIZATION_LANGS``. ``INFORMAL`` accepts a
        citation pointer; LEAN4/COQ/METAMATH reserve slots for formal-
        proof backends.
    chart_id : str
        ``"formal_theory:foundations"`` — substrate-side coordinate
        chart for foundations-level objects.
    """
    theory_id: str
    axioms_hash: str
    axiomatization_lang: str
    chart_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.theory_id, str) or not self.theory_id:
            raise ValueError(
                f"theory_id must be a non-empty string; got {self.theory_id!r}"
            )
        if not isinstance(self.axioms_hash, str) or not self.axioms_hash:
            raise ValueError(
                f"axioms_hash must be a non-empty string; got {self.axioms_hash!r}"
            )
        if self.axiomatization_lang not in VALID_AXIOMATIZATION_LANGS:
            raise ValueError(
                f"axiomatization_lang must be one of "
                f"{VALID_AXIOMATIZATION_LANGS}; got {self.axiomatization_lang!r}"
            )
        if not isinstance(self.chart_id, str) or not self.chart_id:
            raise ValueError(
                f"chart_id must be a non-empty string; got {self.chart_id!r}"
            )


# ---------------------------------------------------------------------------
# ConsistencyRelation — Con(stronger) -> Con(weaker)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ConsistencyRelation:
    """The substrate-grade fact 'Con(stronger) implies Con(weaker)'.

    The relation IS the operator output; the substrate is agnostic
    about HOW the implication is established (relative consistency
    proof, model construction, forcing argument, axiomatic inclusion,
    interpretation).

    Per HARD-5: same ``ConsistencyRelation`` primitive covers all of:
    relative consistency strength of large cardinals, forcing extensions
    yielding new theories, inner-model constructions, axiomatic inclusion
    (e.g. ``ZFC <= ZFC + V=L``), and representation-via-interpretation.

    Attributes
    ----------
    stronger : FormalTheory
        The larger / proves-more theory.
    weaker : FormalTheory
        The smaller / proves-less theory. ``Con(stronger) → Con(weaker)``
        is the substrate's claim.
    justification_ref : str
        Free-form citation pointer (paper, theorem statement, formal
        proof artifact). When ``stronger.axiomatization_lang`` is
        LEAN4/COQ/METAMATH, this can pin to a specific theorem in the
        formalism; INFORMAL allows any string.
    justification_method : str
        One of ``VALID_JUSTIFICATION_METHODS``. Closed enum so the
        substrate's epistemic-explicitness discipline can attach
        certifying weight per method.
    chart_id : str
        ``"consistency_relation:foundations"``.
    """
    stronger: FormalTheory
    weaker: FormalTheory
    justification_ref: str
    justification_method: str
    chart_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.stronger, FormalTheory):
            raise TypeError(
                f"stronger must be FormalTheory; got "
                f"{type(self.stronger).__name__}"
            )
        if not isinstance(self.weaker, FormalTheory):
            raise TypeError(
                f"weaker must be FormalTheory; got {type(self.weaker).__name__}"
            )
        if not isinstance(self.justification_ref, str) or not self.justification_ref:
            raise ValueError(
                f"justification_ref must be a non-empty string; got "
                f"{self.justification_ref!r}"
            )
        if self.justification_method not in VALID_JUSTIFICATION_METHODS:
            raise ValueError(
                f"justification_method must be one of "
                f"{VALID_JUSTIFICATION_METHODS}; got "
                f"{self.justification_method!r}"
            )
        if not isinstance(self.chart_id, str) or not self.chart_id:
            raise ValueError(
                f"chart_id must be a non-empty string; got {self.chart_id!r}"
            )
        # Self-loop check: a theory does not strictly imply its own
        # consistency (that would be Gödel-suspicious at minimum). Not
        # enforced as an error (the substrate is permissive at write)
        # but the equality is suspicious enough that it could be flagged
        # by a downstream linter.

    @property
    def is_strict(self) -> bool:
        """True iff ``stronger`` and ``weaker`` are different theories
        (non-trivial relation). Same theory on both sides is the
        reflexive case (Con(T) → Con(T)) which is structurally valid
        but content-empty."""
        return self.stronger.axioms_hash != self.weaker.axioms_hash


__all__ = [
    "AxiomatizationLang",
    "JustificationMethod",
    "VALID_AXIOMATIZATION_LANGS",
    "VALID_JUSTIFICATION_METHODS",
    "FormalTheory",
    "ConsistencyRelation",
]
