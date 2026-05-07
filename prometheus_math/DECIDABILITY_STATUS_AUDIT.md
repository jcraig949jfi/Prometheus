# CanonicalizationProtocol `decidability_status` Defaults — Audit

**Date:** 2026-05-07 (contract-change window dispatch)
**Ticket:** T-2026-05-07-T021 (P2)
**Auditor:** Techne
**Verdict:** **SAFE — no hardening needed.** Document the existing behavior and close the ticket.

---

## TL;DR

`decidability_status` is a **required field** on `CanonicalizationProtocol` with **no default value** at the dataclass level and an **explicit validator** in `__post_init__` that raises `ValueError` on any value outside `VALID_DECIDABILITY = ("decidable", "undecidable", "conditional")`.

There is **no silent-fallback path** for missing or null inputs. The ticket's worry — "what happens when decidability_status is missing? Is the default explicit or implicit? Is the default safe?" — resolves cleanly: missing input is **statically a TypeError** at construction (Python's required-keyword discipline), and any string outside the three allowed values raises `ValueError` at runtime via the validator. Both paths are loud. The substrate's "loud-fail-on-typo" discipline is already in effect for this field.

---

## Audit reproducer

```python
from sigma_kernel.coordinate_chart import CanonicalizationProtocol

# Case 1: missing decidability_status → TypeError at construction
# (dataclass required field; Python catches before __post_init__)
try:
    CanonicalizationProtocol(
        impl="stub",
        choice_dependencies=(),
        version="1.0.0",
    )  # raises TypeError: missing 1 required positional argument
except TypeError as e:
    print(f"missing: {e}")

# Case 2: invalid decidability_status → ValueError at __post_init__
try:
    CanonicalizationProtocol(
        impl="stub",
        decidability_status="UNDECIDED",  # not in VALID_DECIDABILITY
        choice_dependencies=(),
        version="1.0.0",
    )  # raises ValueError: decidability_status must be one of ...
except ValueError as e:
    print(f"invalid: {e}")

# Case 3: None decidability_status → ValueError at __post_init__
try:
    CanonicalizationProtocol(
        impl="stub",
        decidability_status=None,  # type: ignore
        choice_dependencies=(),
        version="1.0.0",
    )
except ValueError as e:
    print(f"None: {e}")
```

All three paths raise. No silent default. No silent UNDECIDED.

---

## Comparison to ST003 / T018 silent-sentinel pattern

| Field | Default | Missing/invalid behavior | Pattern |
|---|---|---|---|
| `decidability_status` | NO default — required field | TypeError (missing) / ValueError (invalid) | LOUD-FAIL ✓ |
| `get_raw_invariant_keys` (pre-2026-05-07) | `("__unregistered__",)` sentinel | Silent sentinel return | SILENT-DEGRADATION ✗ (FIXED in T018 batch) |
| `method_class_for_independence_class` (pre-2026-05-07) | `MethodClass.EXPLORATORY` | Silent fallback | SILENT-DEGRADATION ✗ (FIXED in T018 batch) |

`decidability_status` is in the LOUD-FAIL column already. No structural change needed.

---

## Existing test coverage

The Fire-#7 fuzzer (`prometheus_math/tests/test_canonicalization_fuzz.py`) already exercises this:

- `TestProtocolDataclassValidation::test_invalid_decidability_status_raises_value_error` — Hypothesis-generated invalid strings, ~200 examples
- `TestProtocolDataclassValidation::test_valid_inputs_construct_successfully` — Hypothesis-generated valid combinations, ~200 examples covering the 3 valid `decidability_status` values

Coverage is sufficient; no test additions in this audit.

---

## What this audit does NOT change

No code changes. Pure doc artifact closing T-2026-05-07-T021 with the SAFE verdict.

---

## Cross-references

- `sigma_kernel/coordinate_chart.py` lines 80-99 — `DecidabilityStatus` literal + `VALID_DECIDABILITY` tuple + docstring rationale
- `sigma_kernel/coordinate_chart.py` lines 162-167 — `__post_init__` validator that raises ValueError
- `prometheus_math/tests/test_canonicalization_fuzz.py` — fuzzer covering valid + invalid input space
- `aporia/meta/queue/techne_inbox.jsonl#T-2026-05-07-T021` — original ticket
- `prometheus_math/SILENT_SENTINEL_AUDIT.md` (T018 sister) — establishes the loud-fail-on-typo discipline this audit confirms is already in place for `decidability_status`

---

*Audit closed SAFE. — Techne, 2026-05-07*
