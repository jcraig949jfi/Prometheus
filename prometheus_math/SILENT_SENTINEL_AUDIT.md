# Silent-Sentinel Pattern Audit — `sigma_kernel/` + `prometheus_math/`

**Date:** 2026-05-07 (contract-change window dispatch)
**Ticket:** T-2026-05-07-T018 (P1) — sister to T-2026-05-06-ST003
**Auditor:** Techne
**Scope:** All `get_*` / `*_for_*` / `*_to_*` lookup functions in `sigma_kernel/` and `prometheus_math/` (excluding tests). Classification: **raises-on-unregistered (good)** vs **silent-sentinel (bad — fix in-place per dispatch instructions)**.

---

## TL;DR

11 lookup functions audited. **2 are silent-sentinel (BAD; fixed in this dispatch).** 7 are explicit `Optional[X]` contracts (GOOD; standard Python pattern). 1 already raises explicitly (GOOD). 1 is a pytest-flow function (skip-with-message; out of scope).

The 2 BAD patterns are the same epistemic shape as ST003 — a silent fall-back to a "valid-looking" sentinel value that masks a registration / typo / unregistered-class gap and propagates downstream as silent degradation.

---

## Classification matrix

| File:line | Function | Pattern | Classification | Action |
|---|---|---|---|---|
| `prometheus_math/learner_corpus.py:123` | `get_raw_invariant_keys(domain)` | Returns `("__unregistered__",)` tuple on unknown domain | **BAD (ST003)** | Fix → raise `KeyError` |
| `sigma_kernel/triangulation_protocol.py:100` | `method_class_for_independence_class(ic)` | Returns `MethodClass.EXPLORATORY` on unknown IC | **BAD (sister-of-ST003)** | Fix → raise `KeyError` |
| `sigma_kernel/coordinate_chart.py:451` | `get_chart(chart_id)` | `Optional[CoordinateChart]`; docstring "Returns None if absent" | GOOD (explicit Optional contract) | None |
| `sigma_kernel/coordinate_chart.py:457` | `lookup_chart(domain, region_key)` | `Optional[CoordinateChart]`; docstring "Returns None if absent" | GOOD (explicit Optional) | None |
| `sigma_kernel/exclusion_certificate.py:600` | `get_certificate(certificate_id)` | `Optional[ExclusionCertificate]`; docstring "Returns None if absent" | GOOD (explicit Optional) | None |
| `sigma_kernel/caveats.py:describe` | `describe(token)` | `Optional[str]`; docstring "or None" | GOOD (explicit Optional) | None |
| `prometheus_math/arsenal_meta.py:105` | `get_meta(callable_ref_or_fn)` | `Optional[ArsenalMeta]`; docstring "Look up metadata" | GOOD (explicit Optional) | None |
| `prometheus_math/stability_adapters.py:618` | `margin_unit_to_falsifier_type(unit)` | `Optional[FalsifierType]` | GOOD (explicit Optional; None-checked upfront) | None |
| `prometheus_math/statistics_distributions.py:516` | `get_family(name_or_family)` | Raises `ValueError("unknown distribution family: ...")` on unknown | GOOD (explicit raise) | None |
| `prometheus_math/_oeis_prefix_extension.py:380` | `get_deviation_record(seq_id, name, data)` | Returns `(record, source_tag)`; "source" field documents resolution path | GOOD (typed source-tag protocol; not a fake sentinel) | None |
| `prometheus_math/_obstruction_corpus_live.py:510` | `get_corpus_or_skip(...)` | Pytest-flow skip-with-message pattern | OUT OF SCOPE (test-fixture; not a substrate getter) | None |

---

## The two BAD patterns — why they're sister-of-ST003

### Pattern 1: `get_raw_invariant_keys` (learner_corpus)

**Current:**
```python
def get_raw_invariant_keys(domain: str) -> Tuple[str, ...]:
    """Return the registered raw-invariant feature list for a domain.
    Falls back to ``("__unregistered__",)`` for unknown domains so the
    emission shape is always well-defined; consumers can detect
    unregistered domains via this sentinel."""
    return RAW_INVARIANTS_PER_DOMAIN.get(domain, ("__unregistered__",))
```

**Problem:** A typo (`"bsd-rank"` instead of `"bsd_rank"`) returns a 1-tuple of a fake feature name. Downstream (`stub_emit_from_legacy_ledger`, `emit_from_substrate`) treats it as a real feature list, looks up `"__unregistered__"` in record dicts, gets `None`, and produces an emission with all-None `raw_invariants` — visually valid but content-empty.

**Fix:** Raise `KeyError(f"unregistered domain {domain!r}; registered: {list(RAW_INVARIANTS_PER_DOMAIN)}")` on missing.

### Pattern 2: `method_class_for_independence_class` (triangulation_protocol)

**Current:**
```python
def method_class_for_independence_class(ic: str) -> MethodClass:
    """Defaults to EXPLORATORY (conservative; cannot certify) for unknown
    independence_classes."""
    ...
    return INDEPENDENCE_TO_METHOD_CLASS.get(key, MethodClass.EXPLORATORY)
```

**Problem:** A typo or new-but-unregistered IC (e.g., `"sage_modular_form"` not yet in registry) silently classifies as `EXPLORATORY` — which means TriangulationProtocol will treat this method as **unable to certify** for INCONCLUSIVE→LOCAL_LEMMA upgrades. The caller's verification path silently loses certifying weight without any warning. A genuinely proof-bearing new method that nobody added to the registry would be silently rejected from triangulation.

**Argued counter:** "Exploratory is the safe default" — true epistemically, but it MASKS a registration gap. The substrate's discipline is loud-fail-on-typo (per ST003 fix); it's NOT "silently downgrade to safe default while pretending nothing's wrong."

**Fix:** Raise `KeyError(f"unregistered independence_class {ic!r}; registered: {list(INDEPENDENCE_TO_METHOD_CLASS)}")`. Force callers to register their independence_class explicitly. The IndependenceClass enum already has an `UNKNOWN` value for callers who genuinely don't know — passing UNKNOWN is the explicit way to opt into "cannot certify" semantics. Anything else should be registered.

---

## What this audit does NOT change

- The 7 explicit-`Optional[X]` getters stay as-is. They follow Python's standard pattern (dict.get vs dict[key]); callers know to handle None. Renaming them or adding raise-variants is out of scope.
- `get_corpus_or_skip` is a pytest-flow primitive, not a substrate getter; out of scope.
- New silent-sentinel patterns introduced after this audit will need their own ticket.

---

## Migration impact

Two existing tests will need updates after the Tier 1 batch fixes (current tests assert the OLD silent-sentinel behavior):

1. `prometheus_math/test_learner_corpus.py::test_per_domain_raw_invariant_registry_unknown_domain_returns_sentinel` — currently asserts `keys == ("__unregistered__",)`. Will be replaced with `test_per_domain_raw_invariant_registry_unknown_domain_raises` asserting `KeyError`.
2. `sigma_kernel/test_triangulation_protocol.py::test_method_class_for_unknown_independence_class_is_exploratory` + `test_method_class_for_arbitrary_unregistered_string_is_exploratory` — currently assert `EXPLORATORY` return. Will be replaced with `test_method_class_for_unknown_independence_class_raises`.

These test updates are part of the contract-change Tier 1 batch.

---

## Cross-references

- T-2026-05-06-ST003 (substrate-tester:lane-4) — original silent-sentinel finding
- T-2026-05-07-T018 (this audit)
- `aporia/meta/pressure_appliers/CONTRACT_CHANGE_WINDOW_TECHNE_2026-05-07.md` — dispatch authorization
- `aporia/doctrine/critical_memories.md` HARD-2 — anti-conventional discipline (silent-degradation is the conventional reflex; loud-fail is the substrate-grade discipline)

---

*Audit complete. 2 in-place fixes queued for Tier 1 batch. — Techne, 2026-05-07*
