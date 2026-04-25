---
name: TOOL_CLASS_NUMBER
type: tool
version: 1
tier: 1
language: python
interface: class_number(polynomial) -> int
also:
  - class_group(polynomial) -> dict
  - regulator_nf(polynomial) -> float
dependencies: [cypari]
complexity: O(|disc|^(1/2)) heuristic under GRH; unbounded unconditionally
tested_against: LMFDB nf_fields + Cohen Advanced Number Theory tables; 32/32
failure_modes:
  - For |disc| > 2^50 PARI assumes GRH (call bnfcertify to verify)
  - Polynomial must be irreducible; no validation performed by the tool
  - Non-monic polynomials accepted but semantics are for the field K = Q[x]/(f)
requested_by: Harmonia
forged_date: 2026-04-22
forged_by: Techne
paradigms: [P02, P18]
references:
  - REQ-010
  - Report #11 (Greenberg screening)
  - Report #18 (Cohen-Lenstra test)
---

# TOOL_CLASS_NUMBER — Class number of a number field

```python
from techne.lib.class_number import class_number, class_group, regulator_nf

class_number('x^2+5')        # 2
class_number([1, 0, 5])       # 2  (same: coeffs descending)
class_number('x^2+163')       # 1  (Heegner)

class_group('x^2+23')
# {'h': 3, 'structure': [3], 'is_cyclic': True,
#  'disc': -23, 'signature': (0, 1), 'degree': 2}

regulator_nf('x^2-2')         # 0.8813735870... = log(1+sqrt(2))
```

## When to use

- **Cohen-Lenstra heuristics**: scan class numbers across a family of NFs, check the class-group distribution matches Cohen-Lenstra predictions.
- **Iwasawa lambda/mu screening**: class number at the base drives the Z_p-extension growth law; class_group() gives you the p-part directly from `structure`.
- **Greenberg conjecture tests**: totally-real fields where the p-part of the class number is expected to stabilize.
- **Quick NF fingerprints**: `class_group` returns (h, structure, disc, signature, degree) in one call — enough for most stratification tasks.

## When NOT to use

- You only need h for Q(sqrt(d)): use a formula-based implementation; bnfinit is expensive.
- You have the NF polynomial in PARI already: call `bnf.no` directly, don't pay the wrap.
- You need rigorous h for |disc| > 2^50: this tool uses GRH by default.

## Validated against

LMFDB `nf_fields.class_number` for quadratic, cubic, and select quartic fields; Cohen *Advanced Topics in Computational Number Theory* tables.
