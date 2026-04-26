---
name: TOOL_LLL_REDUCTION
type: tool
version: 1
tier: 1
language: python
interface: lll(basis) -> np.ndarray
also:
  - lll_with_transform(basis) -> (R, T)
  - shortest_vector_lll(basis) -> np.ndarray
  - lll_gram(gram) -> np.ndarray
dependencies: [cypari, numpy]
complexity: O(n^4 log^2 B) where n = dim, B = max entry
tested_against: skewed-lattice reduction, determinant preservation, unimodular transform, Gram matrix input
failure_modes:
  - Approximate SVP only ||b_1|| <= 2^((n-1)/2) * lambda_1. For exact SVP use fpylll.
  - Integer lattices only; for rational or real vectors use mpmath.lindep (PSLQ).
  - CONVENTION ROWS equal basis vectors (math convention). PARI uses columns internally; tool transposes.
requested_by: Ergon
forged_date: 2026-04-22
forged_by: Techne
paradigms: [P05, P10, P17]
references:
  - REQ-018
  - Report #32 (Lattice problems, ideal lattices)
---

# TOOL_LLL_REDUCTION — Lenstra-Lenstra-Lovasz lattice basis reduction

```python
from techne.lib.lll_reduction import (
    lll, lll_with_transform, shortest_vector_lll, lll_gram,
)
import numpy as np

B = [[1, 1, 1], [0, 1, 0], [0, 0, 1000000]]
R = lll(B)
# rows of R are the reduced basis (shorter vectors first)

R, T = lll_with_transform(B)
# R = T @ B, T unimodular (det = +/- 1)

shortest_vector_lll(B)
# the shortest row of R (approximate shortest lattice vector)

# Gram-matrix version when you don't have explicit coordinates
lll_gram([[1, 0, 0], [0, 4, 0], [0, 0, 9]])
```

## When to use

- **Ideal lattices** (Report #32): find short principal ideals, test equivalence.
- **PSLQ/integer relations on small reals**: scale to integers, apply LLL.
- **Basis reduction for cryptographic-style problems**: subset-sum knapsacks,
  SVP/CVP preliminary reduction.
- **When you need a short basis, not the shortest**: LLL is polynomial-time and
  practical; SVP is exponential.

## When NOT to use

- Real-number relation finding: use `mpmath.lindep` (PSLQ) instead.
- You need the PROVABLY shortest vector: this is approximate; use fpylll's SVP.
- Very high dimension (n > 100) with tight bounds: consider BKZ or progressive
  BKZ (fpylll) rather than plain LLL.
- Your basis is already reduced: tool will return it unchanged — no harm, but
  no speedup either.
