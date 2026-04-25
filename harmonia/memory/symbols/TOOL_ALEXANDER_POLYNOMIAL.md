---
name: TOOL_ALEXANDER_POLYNOMIAL
type: tool
version: 1
tier: 1
language: python
interface: alexander_polynomial(knot) -> dict
also:
  - alexander_coeffs(knot) -> list[int]
dependencies: [snappy, knot_floer_homology]
complexity: dominated by HFK computation; O(c!) worst case for c crossings, typically fine up to c=14
tested_against: knotinfo standard Alexander polynomials 3_1, 4_1, 5_1, 5_2, 6_1, 7_4; 11 assertions
failure_modes:
  - Input must be a knot (1-component link); multi-component links use a different Alexander polynomial convention (not supported).
  - Non-alternating knots with high crossings may be slow.
requested_by: Ergon
forged_date: 2026-04-22
forged_by: Techne
paradigms: [P18]
references:
  - REQ-002 (closed — HFK already covers this, tool is thin wrapper)
  - Report #6 (L-space filter on 13K knots)
---

# TOOL_ALEXANDER_POLYNOMIAL — Alexander polynomial of a knot

```python
from techne.lib.alexander_polynomial import alexander_polynomial, alexander_coeffs

alexander_coeffs('3_1')           # [1, -1, 1]  (t - 1 + t^{-1})
alexander_coeffs('4_1')           # [-1, 3, -1] (-t + 3 - t^{-1})

alexander_polynomial('5_2')
# {'coeffs_by_grading': [(-1, 2), (0, -3), (1, 2)],
#  'coeffs': [2, -3, 2], 'degree': 1, 'is_unit': False,
#  'determinant': 7}
```

## Why a separate tool (REQ-002 "closed" with note)

The `knot_floer_homology` Python package returns HFK bigraded ranks directly;
the Alexander polynomial is the graded Euler characteristic:

    Δ_K(t) = sum_a (sum_m (-1)^m rank HFK_hat(a, m)) t^a

This tool is a thin wrapper that computes Δ from the HFK output — so any
researcher already using HFK (Ergon's 12,965-knot pipeline) gets Δ free.

## When to use

- **L-space filter** (Report #6): Δ_K determines L-space candidate status.
  `knot_floer_homology.pd_to_hfk` returns `L_space_knot` directly, but Δ
  is a useful cross-check and identifies thin knots.
- **Determinant stratification**: |Δ_K(-1)| is a classical invariant;
  `alexander_polynomial(K)['determinant']` gives it in one call.
- **Unknot filter**: Δ = 1 iff the knot is potentially unknotted (necessary
  but not sufficient — Alexander can't distinguish the unknot from conway/KT).

## When NOT to use

- Multi-component link: Alexander polynomial is multi-variate; not supported.
- You want the full HFK invariants: call `knot_floer_homology.pd_to_hfk`
  directly and extract more than just Δ.
