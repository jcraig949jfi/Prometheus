# p-adic L-function Value Encoding — Design (T-2026-05-07-T025)

**Date:** 2026-05-07 (contract-change window dispatch)
**Ticket:** T-2026-05-07-T025 (P1)
**Status:** Design landed; impl deferred (depends on multi-precision contract change per T029).

---

## Per HARD-5

Not "p-adic L-function" the discipline. The substrate cares about: an object representable as a value in Q_p (the p-adic numbers) with an explicit precision metadata `O(p^N)` and a parameterizing operator output.

The key substrate-grade observation: p-adic precision is INTRINSIC to the object, not a runtime detail. Encoding via `float` discards it entirely. Per T029 audit, this is the canonical case for the multi-precision contract change.

---

## Proposed primitive

### `PadicValue` + `PadicPrecisionMetadata`

```python
@dataclass(frozen=True)
class PadicValue:
    """A p-adic number with intrinsic precision metadata.

    Substrate canon: represented as (p, digits_modulo_p_to_N, N).
    Reconstruction: value = sum(digits[i] * p**i for i in range(N)).
    """
    prime: int                                 # p
    digits_modulo_p_to_N: Tuple[int, ...]      # canonical digit expansion
    precision_N: int                           # value is exact modulo p**N
    valuation: int                             # p-adic valuation; sign is by convention
    chart_id: str                              # "padic_value:p_<p>:precision_<N>"


@dataclass(frozen=True)
class PadicLFunctionValue:
    """An L-function value evaluated at a special point in the p-adic
    domain. Carries the source L-function identifier + evaluation point
    + the typed PadicValue output.
    """
    l_function_id: str                          # e.g. "kubota_leopoldt:Q:p_5"
    evaluation_point: str                       # "(s=0)" or "(s=-1)" etc.
    value: PadicValue                           # the operator output
    operator_id: str                            # registered operator
    chart_id: str                               # padic_l_function:family_X:p_p
```

### CoordinateChart placement

`padic_value:p_<p>:precision_<N>` for the fundamental p-adic objects.
`padic_l_function:family_<F>:p_<p>` for L-function values, parameterized by family (cyclotomic, Iwasawa, etc.) and prime.

---

## Worked encoding example — Kubota-Leopoldt p-adic L-function at s=0 for p=5

```python
val = PadicValue(
    prime=5,
    digits_modulo_p_to_N=(2, 4, 1, 3, 0, 2, 1, 4),  # 8 digits = O(5^8) precision
    precision_N=8,
    valuation=0,
    chart_id="padic_value:p_5:precision_8",
)

l_val = PadicLFunctionValue(
    l_function_id="kubota_leopoldt:Q:p_5",
    evaluation_point="(s=0)",
    value=val,
    operator_id="kubota_leopoldt_eval_at_zero",
    chart_id="padic_l_function:cyclotomic:p_5",
)
```

---

## Capability gap status

- `PadicValue` requires the multi-precision contract change (T029) to integrate cleanly with `KillComponent.margin`
- Until then, can ship as a standalone dataclass with string-serialized digit tuples (followed by the T029 follow-up to wire margin → PadicValue conversion)
- Substrate-side primitive lands now (additive); operator-side L-function evaluators are caller infrastructure

---

## Cross-references

- `prometheus_math/MULTIPRECISION_AUDIT.md` — explicit T029 dependency
- `harmonia/memory/architecture/operator_portability_GAP.md` (T030 — p-adic↔archimedean operator portability is a future high-value certificate)
- `aporia/doctrine/critical_memories.md` HARD-4 (p-adic deep level on hunt list) + HARD-5

— Techne, 2026-05-07
