---
name: TOOL_SMITH_NORMAL_FORM
type: tool
version: 1
tier: 1
language: python
interface: smith_normal_form(M) -> np.ndarray
also:
  - invariant_factors(M) -> list[int]
  - abelian_group_structure(M) -> dict
dependencies: [numpy, sympy]
complexity: O(m n^2 log^2(max_entry)) via sympy; slow in practice for n > 30
tested_against: Cohen-style worked example, triangle boundary map (H_0=Z, H_1=Z), Z/4 x Z/6 reduction to Z/2 x Z/12; 22 assertions
failure_modes:
  - sympy backend slow for matrices > 30x30; expect seconds. Large simplicial complexes need Tier 2 PARI matsnf (12-50x faster in benchmarks).
  - No validation that input is integer; floats will be coerced with potential silent loss.
requested_by: Ergon
forged_date: 2026-04-22
forged_by: Techne
paradigms: [P05, P15]
references:
  - REQ-015
  - Report #53 (Homology of simplicial complexes)
---

# TOOL_SMITH_NORMAL_FORM — Smith normal form of an integer matrix

```python
from techne.lib.smith_normal_form import (
    smith_normal_form, invariant_factors, abelian_group_structure,
)

# Invariant factors (ascending, d_1 | d_2 | ... | d_r, zeros dropped)
invariant_factors([[2, 4, 4], [-6, 6, 12], [10, -4, -16]])
# [2, 6, 12]

# Abelian group presentation -> structure
abelian_group_structure([[4, 0], [0, 6]])
# {'torsion': [2, 12], 'free_rank': 0, 'trivial_factors': 0, 'presentation_shape': (2, 2)}

# Homology: boundary map B_1 of a triangle gives H_0 = Z
B1 = [[-1, 0, 1], [1, -1, 0], [0, 1, -1]]
abelian_group_structure(B1)['free_rank']  # 1 (H_0 = Z, one connected component)
```

## When to use

- **Integer homology**: `abelian_group_structure(B_k)` where B_k is the boundary
  matrix from C_k to C_{k-1} gives torsion + free rank of the image cokernel,
  i.e. H_{k-1} of the subcomplex (after combining with ker B_{k-1}).
- **Classification of finitely generated abelian groups**: given any presentation
  matrix, get the canonical decomposition into cyclic factors.
- **Lattice index computation**: the product of invariant factors equals the
  determinant (up to sign) of a full-rank integer matrix.

## When NOT to use

- You have a large simplicial complex (n > 30): sympy is slow. Use PARI matsnf
  directly or wait for Tier 2 promotion.
- You only need rank: np.linalg.matrix_rank is much faster.
- Matrix has non-integer entries: this tool is Z-only.
