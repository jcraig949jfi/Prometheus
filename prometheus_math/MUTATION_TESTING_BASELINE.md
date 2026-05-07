# Mutation Testing Baseline

_Generated: 2026-05-07 11:08:01 UTC_
_Per inbox ticket T-2026-05-07-T014 (prometheus_math/mutation_testing.py)_

## Summary

- **Target files:** 1
  - `sigma_kernel\method_spec.py`
- **Test command:** `python -m pytest sigma_kernel/test_method_spec.py -q --tb=no`
- **Total mutations proposed:** 23
- **Killed (caught by tests):** 20
- **Survived (test gap):** 3
- **Errored (mutation broke loader):** 0
- **Skipped (operator anchor mismatch):** 0
- **Mutation score (killed / (killed + survived)):** 0.870
- **Elapsed:** 75.4s

## Top Surviving Mutations (test-gap candidates)

Each survivor is a mutation that did NOT cause any test failure — i.e. the test suite has no assertion that would catch this specific change. Each is a candidate for a new test.

| # | site | operator | original -> mutated |
|---|---|---|---|
| 1 | `method_spec.py:211` | `boolean_not` | `True` -> `False` |
| 2 | `method_spec.py:371` | `comparison_flip` | `<` -> `>` |
| 3 | `method_spec.py:371` | `comparison_flip` | `>` -> `<` |

## Caveats

1. **Coarse docstring filter.** Lines starting with ``"""`` or ``'''`` are treated as docstring boundaries; multi-line docstrings + edge cases (e.g. raw strings, f-strings spanning lines) may produce false-positive mutations inside string literals. A future ticket should switch to AST-level analysis.
2. **Operator coverage is initial-set only.** Four operators are shipped in this baseline (comparison_flip, boolean_not, return_constant_None, off_by_one_int). Strong mutation testing warrants more (literal_constant_swap, exception_swallow, loop_bound_drop). Future ticket can extend the operator set.
3. **Per-mutation pytest cost dominates.** Each mutation runs the configured test command in a fresh subprocess. With PARI/CVXPY startup adding ~5s per invocation, a baseline run of N mutations takes roughly N x (5s + scoped-test-time). Scope the test command tightly when extending the corpus.
