# Prometheus — Open Bugs

Tracked issues found by property-based testing and other audits. Each
entry: location, reproduction, expected vs actual, status.

## techne/lib/lll_reduction.py

### B-LLL-001: rank-deficient input crashes with IndexError

**File:** `techne/lib/lll_reduction.py`
**Reporter:** Techne property test suite (project #6)
**Date:** 2026-04-22

When `lll(B)` is called on a rank-deficient (singular) integer basis,
PARI's qflll returns a transformation matrix sized to the rank, not to
the original number of input vectors. The wrapper's
`_pari_mat_cols_to_rows(reduced, d, n)` then attempts to read column
`j = n-1` of a matrix that only has `rank < n` columns and crashes
with `IndexError: column index out of range` (raised from cypari).

**Repro:**
```python
import numpy as np
from prometheus_math.number_theory import lll
B = np.array([[1, 2, 3], [2, 4, 6], [0, 0, 1]], dtype=int)  # row 1 = 2*row 0
lll(B)   # IndexError
```

**Expected:** either (a) a basis with leading zero rows reflecting the
rank deficiency, or (b) a clear `ValueError("input basis is rank-deficient")`.

**Suggested fix:** detect the case in `lll()` by reading
`pari.matrank(M)` first, or pad/extend the qflll output with zero
columns to recover the n×d expected shape, then sort zero rows to the
top per the LLL convention.

**Test:** `test_lll_singular_basis` in
`prometheus_math/tests/test_number_theory_properties.py` documents this
failure (currently xfailed pending fix).

---

## techne/lib/galois_group.py

### B-GAL-001: degree-10 cyclotomic galois fails on missing galdata file

**File:** `techne/lib/galois_group.py`
**Reporter:** Techne property test suite (project #6)
**Date:** 2026-04-22

The bundled cypari does not ship with the `galdata` add-on for PARI's
polgalois beyond degree ~7. A `polgalois(Phi_11)` call fails with:

```
PariError: polgalois: error opening galois file:
  `/d/a/CyPari/CyPari/libcache/pari/share/pari/galdata/COS10_45_43'
```

**Expected:** a clear `RuntimeError("PARI galdata package required for
polgalois on degree N>=8; install via gp2c-install pari-galdata")`.

**Workaround in tests:** restrict cyclotomic Galois tests to degree <= 7.
The doc-claim "polgalois supports degree <= 11" needs to be tightened
to "<= 7 in default builds; <=11 with galdata add-on installed".

**Suggested fix:** in `galois_group`, catch the PariError with `'galois
file'` substring and re-raise as `RuntimeError` with install instruction.

---

## techne/lib/lll_reduction.py

### B-LLL-002: 1×1 lattice raises PariError "incorrect type in qflll (t_VEC)"

**File:** `techne/lib/lll_reduction.py`
**Reporter:** Techne edge-case gallery (project #41)
**Date:** 2026-04-22

A 1×1 lattice (single basis vector) cannot be reduced — `qflll` rejects
the column matrix because cypari serializes a 1×1 PARI matrix as a
`t_VEC` rather than a `t_MAT`.

**Repro:**
```python
import prometheus_math as pm
pm.number_theory.lll([[5]])
# cypari._pari.PariError: incorrect type in qflll (t_VEC)
```

**Expected:** A 1×1 lattice has trivial LLL reduction — return the same
vector (up to sign), since a singleton basis is already optimal.

**Suggested fix:** special-case `n == 1` in `lll()` /
`lll_with_transform()` to return the input unchanged (or with sign-fixed
to positive convention). Equivalent fix: coerce single-column to
`[[5];]` in `_to_pari_mat_cols`.

**Test:** `TestLLLEdges::test_1x1_lattice` in
`prometheus_math/tests/test_edge_cases.py` currently asserts the
PariError as documented behavior. Flip the assertion to compare the
reduced single vector when fixed.
