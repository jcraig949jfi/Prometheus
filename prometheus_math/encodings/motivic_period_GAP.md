# Motivic Period + Conjectural Identity Encoding — Design (T-2026-05-07-T028)

**Date:** 2026-05-07 (contract-change window dispatch)
**Ticket:** T-2026-05-07-T028 (P2)
**Status:** Design landed; impl deferred (depends on multi-precision contract change per T029).

---

## Per HARD-5

Not "motivic periods" the discipline. The substrate cares about: an object that IS a transcendental number with TWO operator-outputs (computed via two different methods) plus a conjectural-identity verdict that they agree to N digits.

The substrate-grade primitive is the **conjectural identity** — a typed pair of operator-outputs with a precision-tagged equality verdict. Motivic periods are one instance; differential-equation-vs-integral identities are another; volume-conjecture instances are another.

---

## Proposed primitive

### `TranscendentalValue` + `ConjecturalIdentity`

```python
@dataclass(frozen=True)
class TranscendentalValue:
    """A transcendental number computed via a specific method, with
    intrinsic precision metadata. Per T029 multi-precision audit, the
    value is string-encoded high-precision (mpmath.mpf serialization)
    with explicit precision_dps."""
    value_string: str                              # mpmath.mpf serialization
    precision_dps: int                             # decimal places of precision
    computation_method_id: str                     # registered method that produced this
    chart_id: str                                  # "transcendental_value"


@dataclass(frozen=True)
class ConjecturalIdentity:
    """A conjectural equality between two TranscendentalValues
    computed via DIFFERENT methods. The substrate records the
    conjectured equality as an explicit fact + the empirical
    high-precision agreement.
    """
    value_a: TranscendentalValue
    value_b: TranscendentalValue
    conjectured_relation: str                      # "equality", "rational_multiple", "integer_linear_combination"
    empirical_agreement_dps: int                    # digits of agreement observed
    proof_status: str                               # "conjectural", "proven", "refuted"
    proof_reference: Optional[str]                 # if proven or refuted
    chart_id: str                                  # "conjectural_identity:transcendental"
```

### CoordinateChart placement

`transcendental_value` for the values themselves.
`conjectural_identity:transcendental` for the typed-pair relations.

---

## Worked encoding example — Apéry's constant ζ(3) via two methods

Apéry's irrationality proof for ζ(3) is one of the cleanest motivic-period instances. Two independent methods compute ζ(3): direct series + Apéry's continued fraction.

```python
direct = TranscendentalValue(
    value_string="1.2020569031595942853997381615114499907649862923404988817922715553418382057863130901864558736093352581...",
    precision_dps=100,
    computation_method_id="zeta_direct_series_n_10000",
    chart_id="transcendental_value",
)

apery = TranscendentalValue(
    value_string="1.2020569031595942853997381615114499907649862923404988817922715553418382057863130901864558736093352581...",
    precision_dps=100,
    computation_method_id="apery_continued_fraction_n_500",
    chart_id="transcendental_value",
)

identity = ConjecturalIdentity(
    value_a=direct,
    value_b=apery,
    conjectured_relation="equality",
    empirical_agreement_dps=100,            # full agreement at 100 dps
    proof_status="proven",                   # Apéry 1979 — actually proven
    proof_reference="Apery 1979 irrationality proof",
    chart_id="conjectural_identity:transcendental",
)
```

For genuinely conjectural identities (e.g., Zagier's conjectures on multiple zeta values, or unproven motivic period equalities), the same primitive applies with `proof_status="conjectural"`.

---

## Capability gap status

- Both dataclasses are additive
- Hard dependency on T029 multi-precision contract change for substrate-grade integration with KillComponent.margin (precision tags currently stored as string serialization sidesteps the contract gap)
- v1 ships standalone; v2 wires margin → TranscendentalValue conversion when the multi-precision sister field exists

---

## Cross-references

- `prometheus_math/MULTIPRECISION_AUDIT.md` — T029 dependency
- `aporia/doctrine/critical_memories.md` HARD-4 (categorical/cohomological/motivic territory) + HARD-5
- `harmonia/memory/architecture/operator_portability_GAP.md` — different-method-same-value transports ARE operator-portability instances (the operator is "compute period via method X" and the regions are the method registries)

— Techne, 2026-05-07
