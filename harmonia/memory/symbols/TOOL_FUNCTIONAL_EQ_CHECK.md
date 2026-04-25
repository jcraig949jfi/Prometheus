---
name: TOOL_FUNCTIONAL_EQ_CHECK
type: tool
version: 1
tier: 1
language: python
interface: functional_eq_check(obj, precision=100, threshold_log10=-8) -> dict
also:
  - fe_residual(obj, precision=100) -> int
dependencies: [cypari]
complexity: lfuninit is O(sqrt(conductor) * precision); lfuncheckfeq adds constant factor
tested_against: zeta (residual ~10^-60); EC 11.a1, 37.a1, 389.a1, 5077.a1, 66.b1 (residual <= 10^-60); 11 assertions
failure_modes:
  - lfuncheckfeq returns negative log_10 of residual. Positive / near-zero value means FE is NOT satisfied.
  - Default threshold_log10 = -8 is very loose but catches outright FE failures. For stringent audits raise precision and tighten threshold.
  - Precision dominates runtime. Default 100 bits is fast for conductor < 10^5; raise for larger conductor curves.
  - Accepts EC ainvs, integer 1 (zeta), PARI expr string, or pre-built cypari Gen. No support yet for modular forms / Hecke characters — pass raw PARI lfuncreate via string.
requested_by: Charon
forged_date: 2026-04-22
forged_by: Techne
paradigms: [P03, P08]
references:
  - REQ-013
  - Report #17 (L-function validation)
---

# TOOL_FUNCTIONAL_EQ_CHECK — verify L-function functional equation

```python
from techne.lib.functional_eq_check import functional_eq_check, fe_residual

functional_eq_check(1)                     # Riemann zeta
# {'residual_log10': -61, 'satisfies': True, 'kind': 'zeta', ...}

functional_eq_check([0, 0, 1, -1, 0])      # 37.a1
# {'residual_log10': -68, 'satisfies': True,
#  'kind': 'elliptic_curve', 'conductor': 37, 'degree': 2}

fe_residual([0, 0, 1, -1, 0])              # -68  (very clean)
```

## What this tests

For a completed L-function Λ(s) = (gamma factor) * L(s), the functional
equation is  Λ(s) = ε · Λ(w - s)  where w is the motivic weight and ε is
the root number. PARI's `lfuncheckfeq` evaluates both sides numerically
and returns the log_10 of the residual — a (strongly) negative number
means the FE holds to that precision.

## When to use

- **L-function validation** (Report #17): before expensive downstream
  computation on an L-function, confirm FE holds to rule out bad
  Dirichlet coefficients or miscomputed gamma factors.
- **Cross-checking custom L-data**: if you construct an L-function from
  raw Dirichlet coefficients + gamma factors, the FE check is the first
  non-trivial sanity test.
- **Numerical audit of LMFDB L-functions**: verify stored Dirichlet
  coefficients match the claimed functional equation.

## When NOT to use

- You want to COMPUTE L-values, not check FE: use `lfun(L, s)` directly.
- Very large conductor (> 10^8) at high precision: budget runtime.
- You need the FE for a specific non-standard L-function: construct via
  `lfuncreate` and pass the Gen directly.
