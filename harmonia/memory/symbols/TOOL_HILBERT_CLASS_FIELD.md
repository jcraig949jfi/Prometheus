---
name: TOOL_HILBERT_CLASS_FIELD
type: tool
version: 1
tier: 1
language: python
interface: hilbert_class_field(polynomial) -> dict
also:
  - class_field_tower(polynomial, max_depth=5) -> dict
dependencies: [cypari]
complexity: dominated by bnfinit; exponential in discriminant for deep towers
tested_against: Q(sqrt(-5)) (h=2, HCF disc 400), Q(i) (trivial), Q(sqrt(-23)) (h=3, HCF deg 6), Q(sqrt(-47)) (h=5, depth 1); 8 assertions
failure_modes:
  - Tower may be infinite (Golod-Shafarevich) — default max_depth=5 caps. Check 'capped' field.
  - PARI assumes GRH for class numbers with |disc| > 2^50. Iterated HCF may amplify GRH dependence.
  - bnfinit of HCF can be very slow for h > 10; consider class_field_tower(max_depth=1) for quick tower-start checks.
  - Variable priority base poly uses y, HCF polys use x. Internally swapped; caller doesn't see this.
  - Class-number guard default max_class_number=50. hilbert_class_field raises ValueError for h > 50 because bnrclassfield typically exceeds 4 GB PARI stack. Example 2.0.7751.1 has h=110 (HCF degree 220); override with max_class_number=200 at your own memory risk. class_field_tower returns aborted=True in the output dict rather than raising, useful for bulk H15 scans.
requested_by: Aporia
forged_date: 2026-04-22
forged_by: Techne
paradigms: [P02, P18]
references:
  - Aporia H15 ADE-tower spec 1776890501219-0
  - Report #11 (Greenberg screening)
---

# TOOL_HILBERT_CLASS_FIELD — Hilbert class field and tower depth

```python
from techne.lib.hilbert_class_field import hilbert_class_field, class_field_tower

hilbert_class_field('x^2+5')
# {'abs_poly': 'x^4 + 3*x^2 + 1', 'rel_poly': 'x^2 + 1',
#  'degree_rel': 2, 'degree_abs': 4, 'disc': 400,
#  'class_number_K': 2, 'is_trivial': False}

class_field_tower('x^2+5', max_depth=3)
# {'depth': 1, 'terminates': True, 'capped': False,
#  'poly_sequence': ['x^2+5', 'x^4 + 3*x^2 + 1'],
#  'class_number_sequence': [2, 1],
#  'degree_sequence': [2, 4],
#  'disc_sequence': [-20, 400]}
```

## Why this tool exists — Aporia H15

Aporia's H15 (NF Tower Termination ADE vs non-ADE) requires computing the
class-field-tower depth per number field. That needs:

1. `bnfinit` → class number  (already have `class_number`)
2. `bnrinit` + `bnrclassfield` → HCF polynomial  (this tool)
3. Iterate until h=1 or depth cap  (`class_field_tower`)
4. `polgalois` → bin as ADE vs non-ADE  (already have `galois_group`)

With this tool shipped the H15 toolchain is complete.

## Warning: Golod-Shafarevich

Not every class field tower terminates. Golod-Shafarevich inequality shows
that fields with many small primes ramified can have infinite towers. The
`capped=True` flag indicates non-termination within the budget; infinite
vs finite cannot be decided in bounded time. For H15 analysis, treat capped
towers as a separate stratum, not "tower depth > max_depth".

## When to use

- **H15 ADE tower depth**: iterate until termination, bin by Galois group.
- **Greenberg screening**: class groups at each level of the tower.
- **Iwasawa lambda/mu**: the class-field tower is adjacent to (but distinct
  from) the Z_p-extension — use when you want the full unramified-abelian
  story, not just the pro-p cyclotomic piece.

## When NOT to use

- You only need h_K: use `class_number` (faster, no HCF computation).
- Field has large discriminant (|disc| > 10^8) — bnfinit is slow; profile first.
