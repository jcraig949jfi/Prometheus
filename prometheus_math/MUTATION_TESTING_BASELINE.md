# Mutation Testing Baseline

_Generated: 2026-05-09 01:24:02 UTC_
_Per inbox ticket T-2026-05-07-T014 (prometheus_math/mutation_testing.py)_

## Summary

- **Target files:** 1
  - `sigma_kernel\exclusion_certificate.py`
- **Test command:** `"C:\Users\jcrai\AppData\Local\Programs\Python\Python311\python.exe" -m pytest sigma_kernel/tests/test_frozen_invariance.py sigma_kernel/tests/test_frozen_baseline_manifest.py sigma_kernel/tests/test_enum_validation_2026_05_08.py sigma_kernel/tests/test_claim_kill_path_typing_2026_05_08.py -q --no-header -x`
- **Total mutations proposed:** 10
- **Killed (caught by tests):** 3
- **Survived (test gap):** 7
- **Errored (mutation broke loader):** 0
- **Skipped (operator anchor mismatch):** 0
- **Mutation score (killed / (killed + survived)):** 0.300
- **Elapsed:** 292.3s

## Top Surviving Mutations (test-gap candidates)

Each survivor is a mutation that did NOT cause any test failure — i.e. the test suite has no assertion that would catch this specific change. Each is a candidate for a new test.

| # | site | operator | original -> mutated |
|---|---|---|---|
| 1 | `exclusion_certificate.py:262` | `off_by_one_int` | `0` -> `1` |
| 2 | `exclusion_certificate.py:335` | `comparison_flip` | `==` -> `!=` |
| 3 | `exclusion_certificate.py:337` | `off_by_one_int` | `3` -> `4` |
| 4 | `exclusion_certificate.py:348` | `off_by_one_int` | `3` -> `4` |
| 5 | `exclusion_certificate.py:348` | `off_by_one_int` | `3` -> `4` |
| 6 | `exclusion_certificate.py:451` | `return_constant_None` | `return self.strength in NEGATIVE_SPACE_FEEDING_STRENGTHS` -> `return None` |
| 7 | `exclusion_certificate.py:468` | `boolean_not` | `True` -> `False` |

## Caveats

1. **Coarse docstring filter.** Lines starting with ``"""`` or ``'''`` are treated as docstring boundaries; multi-line docstrings + edge cases (e.g. raw strings, f-strings spanning lines) may produce false-positive mutations inside string literals. A future ticket should switch to AST-level analysis.
2. **Operator coverage is initial-set only.** Four operators are shipped in this baseline (comparison_flip, boolean_not, return_constant_None, off_by_one_int). Strong mutation testing warrants more (literal_constant_swap, exception_swallow, loop_bound_drop). Future ticket can extend the operator set.
3. **Per-mutation pytest cost dominates.** Each mutation runs the configured test command in a fresh subprocess. With PARI/CVXPY startup adding ~5s per invocation, a baseline run of N mutations takes roughly N x (5s + scoped-test-time). Scope the test command tightly when extending the corpus.
