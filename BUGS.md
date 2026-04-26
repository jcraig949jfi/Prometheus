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

---

## techne/lib/knot_shape_field.py

### B-TOPO-001: 7_5 algdep false-fit slips past coefficient-height guard

**File:** `techne/lib/knot_shape_field.py`
**Reporter:** Techne property test suite (project #32)
**Date:** 2026-04-25

`knot_shape_field('7_5', bits_prec=300)` returns a degree-6 polynomial
with coefficient heights of ~10^140 and a discriminant of ~10^5300.
The published invariant trace field of 7_5 has degree 4 with much
smaller coefficients (Neumann-Reid table).

The two-guard logic in `_shape_from_poly_verify` (max-coefficient
height capped at `bits_prec/4` bits, plus tightened tolerance
`10^(-bits_prec*0.15)`) does NOT reject this fit because at
bits_prec=300 the cap is ~75 bits ≈ 10^22, but PARI's algdep returns
a polynomial whose first verified coefficient happens to fall just
below the threshold or the algdep call iterates through a sequence
that hits a candidate before our checks fire.

Raising bits_prec to 500 reproduces the bug at the same degree,
suggesting the issue is structural rather than a precision shortfall.

**Repro:**
```python
from prometheus_math.topology import knot_shape_field
r = knot_shape_field('7_5', bits_prec=300, max_deg=8)
print(r['degree'], abs(r['disc']))  # 6, ~5300-digit number
```

**Expected:** Either the documented iTrF (degree ~4 per Neumann-Reid)
or a clean ValueError.

**Suggested fix:** Tighten the coefficient-height cap (try
`max_coeff_bits = bits_prec // 8`) and re-survey the small-knot
table to confirm correct fields are still recovered. Alternatively,
ensure low degrees are tried first (they already are) but reject
even the first low-degree fit if its coefficient growth pattern
exceeds a multiplicative-factor bound between successive coefficients.

**Test:** `test_property_shape_field_disc_bounded` in
`prometheus_math/tests/test_topology_properties.py`. The test xfails
the 7_5 case explicitly; it remains a regression check for every
other knot in the table.

**Tracking:** Added to PROJECT_BACKLOG_1000.md as project #32f
(7_5 algdep fix).

---

## prometheus_math/elliptic_curves.py

### B-COMP-001: faltings_height drifts from LMFDB on disc<0 curves [RESOLVED 2026-04-25]

**File:** `techne/lib/faltings_height.py` (re-exported via `pm.elliptic_curves.faltings_height`)
**Reporter:** Composition test gallery (project #42)
**Date:** 2026-04-25
**Resolved:** 2026-04-25 (Cremona/LMFDB label-convention confusion in the test, not a math bug)

**Root cause (re-investigated 2026-04-25):** The `faltings_height`
function is mathematically correct. The mismatch was a
**Cremona/LMFDB label-convention** confusion in the test data:

  - Cremona label `11a1` has ainvs `[0,-1,1,-10,-20]`
  - LMFDB label `11.a1` has ainvs `[0,-1,1,-7820,-263580]`  (= Cremona's `11a3`)

The test was sending Cremona's `11a1` ainvs to `faltings_height` and
comparing the result to LMFDB's `11.a1` row -- two different curves in
the same isogeny class, related by a 5-isogeny (the index-5 sublattice
exactly accounts for the 0.8047 = log(5)/2 + small correction
discrepancy).

`faltings_height([0,-1,1,-10,-20]) = -0.30801` is the correct
Faltings height for that curve and matches LMFDB's `11.a2` row
(`faltings_height = -0.30801`). When called on the LMFDB `11.a1`
ainvs `[0,-1,1,-7820,-263580]`, the function returns +0.49671 to
10+ decimals, matching LMFDB.

**Fix:** the composition test
`test_faltings_height_matches_lmfdb_authority` in
`prometheus_math/tests/test_composition_gallery.py` now queries LMFDB
for the ainvs by label rather than hard-coding a Cremona-style ainvs
table -- making the test self-consistent. xfail removed; all five
parametrized curves pass.

**Original symptom (kept for reference):**

For 11.a1 ([0,-1,1,-10,-20], disc = -161051 < 0) our `faltings_height`
returns -0.30801, but LMFDB ec_curvedata.faltings_height stores
+0.49671. The discrepancy is exactly 0.80472 = log(2*pi)/2 - 0.115
or consistent with a missing real-period doubling that applies only
when disc < 0 (E(R) has 2 components vs 1 for disc>0).

**Repro:**
```python
from prometheus_math.elliptic_curves import faltings_height
from prometheus_math.databases import lmfdb
our = faltings_height([0,-1,1,-10,-20])  # -0.30801
lmfdb_h = lmfdb.elliptic_curves(label="11.a1", limit=1)[0]["faltings_height"]
print(our - lmfdb_h)  # -0.80472
```

Four other curves with disc>0 (37.a1, 43.a1, 53.a1, 389.a1) match
LMFDB to 10+ decimals, isolating the bug to the disc<0 case. This is
exactly the "Off-by-2 from real-period convention" failure documented
in `techne/skills/math-tdd.md` Failure Modes #2.

**Expected:** match LMFDB on disc<0 curves to 1e-3 (the same tolerance
that passes for disc>0 curves).

**Suggested fix:** in `faltings_height`, after computing `o1, o2 = ellperiods(E)`,
check `disc = E[11]`. If `disc < 0`, the standard "real period"
convention uses `Omega = 2*Re(o1)` (or equivalently `o2`) rather than
`|o1|`. The Faltings height formula needs to reference Omega, not the
first raw period.

**Test:** `test_faltings_height_matches_lmfdb_authority[11.a1-ainvs0]`
in `prometheus_math/tests/test_composition_gallery.py` is xfailed
with B-COMP-001 reference. The other four curves remain green.

**Tracking:** queued as fix item under #42 in PROJECT_BACKLOG_1000.md.

---

## prometheus_math edge-case consistency gaps (Project #41 gallery)

The following bugs were surfaced by the systematic 5-edge sweep in
`prometheus_math/tests/test_edge_case_gallery.py`. They are minor
consistency issues — the operations DO reject malformed input, but
through the wrong error type and/or with misleading messages. The
gallery tests pass by accepting either error type.

### B-EDGE-001: class_number(empty-string) raises PariError, not ValueError [RESOLVED 2026-04-25]

**File:** `techne/lib/class_number.py`
**Reporter:** Project #41 gallery
**Date:** 2026-04-25
**Resolved:** 2026-04-25 — `_coerce_poly` now rejects empty/whitespace strings with `ValueError("class_number: empty polynomial input")` before PARI dispatch.

`class_number([])` correctly raises `ValueError("empty polynomial")`,
but `class_number("")` (empty string) falls through to PARI and
raises `PariError("too few arguments")`. The wrapper should validate
empty strings the same way it validates empty lists.

**Repro:**
```python
import prometheus_math as pm
pm.number_theory.class_number("")  # PariError: too few arguments
```

**Expected:** `ValueError("empty polynomial string")` matching the
list-form behaviour.

**Suggested fix:** add `if isinstance(p, str) and not p.strip(): raise
ValueError("empty polynomial string")` at the top of `class_number()`
before the PARI call.

**Test:** `TestClassNumberGallery::test_empty_string_raises` in
`prometheus_math/tests/test_edge_case_gallery.py` (currently passes by
accepting both ValueError and PariError).

---

### B-EDGE-002: class_number(constant-poly) raises PariError, not ValueError [RESOLVED 2026-04-25]

**File:** `techne/lib/class_number.py`
**Reporter:** Project #41 gallery
**Date:** 2026-04-25
**Resolved:** 2026-04-25 — degree-0 inputs (single-coefficient lists) are now rejected with `ValueError("class_number: input is not a number-field polynomial (degree must be >= 1)")` before PARI dispatch.

`class_number([5])` (degree-0 polynomial = constant 5) raises
`PariError("bnfinit: incorrect type in checknf [please apply nfinit()]
(t_INT)")`. The wrapper should reject degree-0 inputs explicitly.

**Repro:**
```python
import prometheus_math as pm
pm.number_theory.class_number([5])  # PariError checknf
```

**Expected:** `ValueError("polynomial must have degree >= 1")`.

**Suggested fix:** check `len(coeffs) < 2` before constructing the
PARI polynomial.

**Test:** `TestClassNumberGallery::test_singleton_constant_polynomial_raises`.

---

### B-EDGE-003: galois_group(empty-string) raises PariError, not ValueError [RESOLVED 2026-04-25]

**File:** `techne/lib/galois_group.py`
**Reporter:** Project #41 gallery
**Date:** 2026-04-25
**Resolved:** 2026-04-25 — `_coerce_poly` now rejects empty/whitespace strings and degree-0 lists with `ValueError("galois_group: empty polynomial input")` before PARI dispatch.

Mirror of B-EDGE-001 in galois_group. `galois_group([])` raises
ValueError correctly, but `galois_group("")` falls through to PARI.

**Repro:**
```python
import prometheus_math as pm
pm.number_theory.galois_group("")  # PariError
```

**Expected:** `ValueError("empty polynomial string")`.

**Suggested fix:** mirror the list-form check at string-input parse
time.

**Test:** `TestGaloisGroupGallery::test_empty_string_raises`.

---

### B-EDGE-004: lll(empty-list) error message is misleading [RESOLVED 2026-04-25]

**File:** `techne/lib/lll_reduction.py`
**Reporter:** Project #41 gallery
**Date:** 2026-04-25
**Resolved:** 2026-04-25 — both `lll` and `lll_with_transform` now validate empty inputs and shape mismatches up front with `ValueError("lll_reduction: empty basis (need at least one row)")`.

`lll([])` raises `ValueError("not enough values to unpack (expected 2,
got 1)")`. The error type is correct but the message is a Python
unpacking artefact, not a description of the error.

**Repro:**
```python
import prometheus_math as pm
pm.number_theory.lll([])  # ValueError with confusing message
```

**Expected:** `ValueError("lll: empty basis (need at least one row)")`.

**Suggested fix:** add an explicit `if not basis: raise ValueError(...)`
guard before the shape unpacking line.

**Test:** `TestLLLGallery::test_empty_raises`.

---

### B-EDGE-005: hyperbolic_volume(empty-string) raises OSError, not ValueError [RESOLVED 2026-04-25]

**File:** `techne/lib/hyperbolic_volume.py`
**Reporter:** Project #41 gallery
**Date:** 2026-04-25
**Resolved:** 2026-04-25 — `_load_manifold` now validates empty knot identifiers and empty PD code lists at the wrapper layer with `ValueError("hyperbolic_volume: empty knot identifier")` before constructing the snappy manifold.

`hyperbolic_volume("")` raises `OSError("The manifold file  was not
found.")` (a snappy IOError). Empty input should be a wrapper-level
ValueError, not a downstream file-system error.

**Repro:**
```python
import prometheus_math as pm
pm.topology.hyperbolic_volume("")  # OSError from snappy
```

**Expected:** `ValueError("hyperbolic_volume: empty knot identifier")`.

**Suggested fix:** validate the input string before constructing the
snappy manifold.

**Test:** `TestHyperbolicVolumeGallery::test_empty_raises`.

---

### B-EDGE-006: iwasawa.lambda_mu(empty-string) raises PariError, not ValueError [RESOLVED 2026-04-25]

**File:** `prometheus_math/iwasawa.py`
**Reporter:** Project #41 gallery
**Date:** 2026-04-25
**Resolved:** 2026-04-25 — `_coerce_poly` (shared by `lambda_mu`, `cyclotomic_zp_extension`, `p_class_group_part`, etc.) now rejects empty/whitespace strings and degree-0 lists with `ValueError("lambda_mu: empty polynomial input")` before PARI dispatch.

`lambda_mu("", p)` raises `PariError("too few arguments")` rather
than a clean `ValueError`. The p-validation path correctly rejects
non-prime / negative p with ValueError; the polynomial-validation
path is missing.

**Repro:**
```python
import prometheus_math as pm
pm.iwasawa.lambda_mu("", 5)  # PariError
```

**Expected:** `ValueError("lambda_mu: empty polynomial string")`.

**Test:** `TestLambdaMuGallery::test_empty_string_raises`.

---

