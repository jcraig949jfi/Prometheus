# Large-Cardinal Consistency-Strength Encoding — Design (T-2026-05-07-T027)

**Date:** 2026-05-07 (design) → 2026-05-10 (SHIPPED)
**Ticket:** T-2026-05-07-T027 (P2) — **RESOLVED 2026-05-10 mini contract-change window**
**Status:** Design + implementation BOTH SHIPPED. See `prometheus_math/encodings/large_cardinal_consistency.py` (155 lines, 2 frozen dataclasses + 2 closed enums) and `prometheus_math/tests/test_large_cardinal_consistency.py` (27 tests, all passing). Mini-window orthogonal to Aporia Phase-2 5-meta-primitive plan; this primitive is foundations/logic, not in any of the 5 meta categories.

**What landed beyond design:**
- Closed enums `AxiomatizationLang` (informal/lean4/coq/metamath) and `JustificationMethod` (axiomatic_inclusion/interpretation/inner_model/forcing/relative_consistency_proof) — substrate-grade typed-error discipline (no silent fallthrough on unknown values)
- `is_strict` property on `ConsistencyRelation` distinguishes reflexive `Con(T) → Con(T)` (content-empty) from cross-theory implications (substrate-grade)
- 27 tests covering construction, validation (rejection of empty/non-string/unknown-enum inputs), parametrized enum coverage, the design doc's worked example (Magidor 1977 SCH failure), and substrate-integration patterns (chart_id namespace, str-value enum roundtrip)

---

---

## Per HARD-5

Not "set theory" the discipline. The substrate cares about: typed STATEMENTS in a partial-order relation (consistency-strength), where the relation is itself the operator output.

The substrate-grade observation: consistency-strength is a uniform shape — `Con(X) → Con(Y)` is a relation between formal theories. The "large cardinal" framing is metadata; the substrate only needs the relation as an operator output.

---

## Proposed primitive

### `FormalTheory` + `ConsistencyRelation`

```python
@dataclass(frozen=True)
class FormalTheory:
    """A registered formal axiomatic theory. Substrate-grade: a content-
    addressed reference to the theory's axioms (as a list of strings or
    a hash-pointer to a Lean/Coq encoding when available).
    """
    theory_id: str                                  # e.g. "ZFC", "ZFC_plus_measurable_cardinal"
    axioms_hash: str                                # sha256 of axioms encoding
    axiomatization_lang: str                        # "informal", "lean4", "coq", "metamath"
    chart_id: str                                   # "formal_theory:foundations"


@dataclass(frozen=True)
class ConsistencyRelation:
    """The substrate-grade fact 'Con(stronger) implies Con(weaker)'.
    The relation IS the operator output; the substrate is agnostic
    about HOW the implication is established (relative consistency
    proof, model construction, forcing argument).
    """
    stronger: FormalTheory                          # the larger theory
    weaker: FormalTheory                            # the smaller theory
    justification_ref: str                          # ref to proof / construction / forcing
    justification_method: str                       # "relative_consistency_proof", "inner_model",
                                                    # "forcing", "interpretation", "axiomatic_inclusion"
    chart_id: str                                   # "consistency_relation:foundations"
```

### CoordinateChart placement

`formal_theory:foundations` for the registered theories themselves.
`consistency_relation:foundations` for the relations between them.

---

## Worked encoding example — SCH failure relative to measurable cardinal

The Singular Cardinals Hypothesis (SCH) failing is consistent relative to a measurable cardinal (Magidor's theorem):

```python
zfc_meas = FormalTheory(
    theory_id="ZFC + measurable cardinal exists",
    axioms_hash="...",
    axiomatization_lang="informal",
    chart_id="formal_theory:foundations",
)

zfc_neg_sch = FormalTheory(
    theory_id="ZFC + ¬SCH",
    axioms_hash="...",
    axiomatization_lang="informal",
    chart_id="formal_theory:foundations",
)

rel = ConsistencyRelation(
    stronger=zfc_meas,
    weaker=zfc_neg_sch,
    justification_ref="Magidor 1977 SCH failure",
    justification_method="forcing",
    chart_id="consistency_relation:foundations",
)
```

---

## Capability gap status

- Both dataclasses are additive primitives; can ship in a single small module
- Real value comes when paired with a Lean/Coq formalism backend (out of scope here)
- For v1: justification_ref is a free-form citation pointer; later versions can pin to formal-proof artifacts

---

## Cross-references

- `aporia/doctrine/critical_memories.md` HARD-4 (large-cardinal / categorical territory on hunt list) + HARD-5
- `harmonia/memory/architecture/operator_portability_GAP.md` — consistency-strength relations are operator-portability instances (the "operator" is "extends-by-axiom-X" and the chart is the foundation system)

— Techne, 2026-05-07
