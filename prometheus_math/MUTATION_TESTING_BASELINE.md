# Mutation Testing Baseline

_Generated: 2026-05-09 17:44:07 UTC_
_Per inbox ticket T-2026-05-07-T014 (prometheus_math/mutation_testing.py)_

## Summary

- **Target files:** 1
  - `sigma_kernel\operator_portability.py`
- **Test command:** `"C:\Users\jcrai\AppData\Local\Programs\Python\Python311\python.exe" -m pytest sigma_kernel/tests/ -q --no-header -x`
- **Total mutations proposed:** 10
- **Killed (caught by tests):** 10
- **Survived (test gap):** 0
- **Errored (mutation broke loader):** 0
- **Skipped (operator anchor mismatch):** 0
- **Mutation score (killed / (killed + survived)):** 1.000
- **Elapsed:** 200.6s

## Survivors

**No survivors.** Every proposed mutation was killed by the test suite. The current test coverage of the target file(s) is adequate against this operator set.

## Caveats

1. **Coarse docstring filter.** Lines starting with ``"""`` or ``'''`` are treated as docstring boundaries; multi-line docstrings + edge cases (e.g. raw strings, f-strings spanning lines) may produce false-positive mutations inside string literals. A future ticket should switch to AST-level analysis.
2. **Operator coverage is initial-set only.** Four operators are shipped in this baseline (comparison_flip, boolean_not, return_constant_None, off_by_one_int). Strong mutation testing warrants more (literal_constant_swap, exception_swallow, loop_bound_drop). Future ticket can extend the operator set.
3. **Per-mutation pytest cost dominates.** Each mutation runs the configured test command in a fresh subprocess. With PARI/CVXPY startup adding ~5s per invocation, a baseline run of N mutations takes roughly N x (5s + scoped-test-time). Scope the test command tightly when extending the corpus.
