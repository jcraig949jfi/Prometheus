# Mutation Testing Baseline

_Generated: 2026-05-09 14:00:19 UTC_
_Per inbox ticket T-2026-05-07-T014 (prometheus_math/mutation_testing.py)_

## Summary

- **Target files:** 1
  - `sigma_kernel\coordinate_chart.py`
- **Test command:** `"C:\Users\jcrai\AppData\Local\Programs\Python\Python311\python.exe" -m pytest sigma_kernel/tests/ -q --no-header -x`
- **Total mutations proposed:** 10
- **Killed (caught by tests):** 3
- **Survived (test gap):** 7
- **Errored (mutation broke loader):** 0
- **Skipped (operator anchor mismatch):** 0
- **Mutation score (killed / (killed + survived)):** 0.300
- **Elapsed:** 201.1s

## Top Surviving Mutations (test-gap candidates)

Each survivor is a mutation that did NOT cause any test failure — i.e. the test suite has no assertion that would catch this specific change. Each is a candidate for a new test.

| # | site | operator | original -> mutated |
|---|---|---|---|
| 1 | `coordinate_chart.py:92` | `off_by_one_int` | `3` -> `4` |
| 2 | `coordinate_chart.py:185` | `return_constant_None` | `return self.canonicalize(point)` -> `return None` |
| 3 | `coordinate_chart.py:273` | `return_constant_None` | `return self.canonicalization.apply(point)` -> `return None` |
| 4 | `coordinate_chart.py:283` | `return_constant_None` | `return float(self.metric(ca, cb))` -> `return None` |
| 5 | `coordinate_chart.py:287` | `return_constant_None` | `return bool(self.admissible_region(point))` -> `return None` |
| 6 | `coordinate_chart.py:303` | `off_by_one_int` | `1` -> `2` |
| 7 | `coordinate_chart.py:308` | `return_constant_None` | `return domain, region_key` -> `return None` |

## Caveats

1. **Coarse docstring filter.** Lines starting with ``"""`` or ``'''`` are treated as docstring boundaries; multi-line docstrings + edge cases (e.g. raw strings, f-strings spanning lines) may produce false-positive mutations inside string literals. A future ticket should switch to AST-level analysis.
2. **Operator coverage is initial-set only.** Four operators are shipped in this baseline (comparison_flip, boolean_not, return_constant_None, off_by_one_int). Strong mutation testing warrants more (literal_constant_swap, exception_swallow, loop_bound_drop). Future ticket can extend the operator set.
3. **Per-mutation pytest cost dominates.** Each mutation runs the configured test command in a fresh subprocess. With PARI/CVXPY startup adding ~5s per invocation, a baseline run of N mutations takes roughly N x (5s + scoped-test-time). Scope the test command tightly when extending the corpus.
