# Mutation Testing Baseline

_Generated: 2026-05-09 03:58:18 UTC_
_Per inbox ticket T-2026-05-07-T014 (prometheus_math/mutation_testing.py)_

## Summary

- **Target files:** 1
  - `sigma_kernel\triangulation_protocol.py`
- **Test command:** `"C:\Users\jcrai\AppData\Local\Programs\Python\Python311\python.exe" -m pytest sigma_kernel/tests/test_frozen_invariance.py sigma_kernel/tests/test_frozen_baseline_manifest.py sigma_kernel/tests/test_enum_validation_2026_05_08.py sigma_kernel/tests/test_claim_kill_path_typing_2026_05_08.py -q --no-header -x`
- **Total mutations proposed:** 10
- **Killed (caught by tests):** 5
- **Survived (test gap):** 5
- **Errored (mutation broke loader):** 0
- **Skipped (operator anchor mismatch):** 0
- **Mutation score (killed / (killed + survived)):** 0.500
- **Elapsed:** 201.9s

## Top Surviving Mutations (test-gap candidates)

Each survivor is a mutation that did NOT cause any test failure — i.e. the test suite has no assertion that would catch this specific change. Each is a candidate for a new test.

| # | site | operator | original -> mutated |
|---|---|---|---|
| 1 | `triangulation_protocol.py:149` | `return_constant_None` | `return INDEPENDENCE_TO_METHOD_CLASS[key]` -> `return None` |
| 2 | `triangulation_protocol.py:281` | `comparison_flip` | `==` -> `!=` |
| 3 | `triangulation_protocol.py:292` | `comparison_flip` | `!=` -> `==` |
| 4 | `triangulation_protocol.py:292` | `return_constant_None` | `return self.method_class != MethodClass.EXPLORATORY` -> `return None` |
| 5 | `triangulation_protocol.py:388` | `comparison_flip` | `<` -> `>` |

## Caveats

1. **Coarse docstring filter.** Lines starting with ``"""`` or ``'''`` are treated as docstring boundaries; multi-line docstrings + edge cases (e.g. raw strings, f-strings spanning lines) may produce false-positive mutations inside string literals. A future ticket should switch to AST-level analysis.
2. **Operator coverage is initial-set only.** Four operators are shipped in this baseline (comparison_flip, boolean_not, return_constant_None, off_by_one_int). Strong mutation testing warrants more (literal_constant_swap, exception_swallow, loop_bound_drop). Future ticket can extend the operator set.
3. **Per-mutation pytest cost dominates.** Each mutation runs the configured test command in a fresh subprocess. With PARI/CVXPY startup adding ~5s per invocation, a baseline run of N mutations takes roughly N x (5s + scoped-test-time). Scope the test command tightly when extending the corpus.
