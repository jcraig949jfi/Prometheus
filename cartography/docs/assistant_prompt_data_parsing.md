# Assistant Task: Data Parsing for Blocked Tests
## Machine: Either M1 or M2
## Priority: HIGH — unblocks 19 tests across both machines

---

## Context

Project Prometheus has a cross-domain mathematical discovery pipeline. We've run 55+ tests through a 27-test falsification battery. 19 tests are blocked on data parsing issues — the raw data exists but isn't in the format our scripts expect. Your job is to fix the data, not run tests.

**Do NOT run any tests or analysis.** Just parse/transform the data files and confirm they're correct.

**Read `CLAUDE.md` at the repo root for security rules (never read key files).**

---

## Task 1: Parse knot polynomial strings into coefficient arrays

**Location:** `cartography/knots/data/knots.json`
**Problem:** 12,965 knots have `alexander`, `conway`, `jones` as polynomial STRING representations (e.g., `"t^2 - 3t + 1"`), but the `alex_coeffs`, `jones_coeffs`, `conway_coeffs` fields are EMPTY (0/12,965 populated). Our test scripts need coefficient arrays.

**What to do:**
1. Read `knots.json`, examine the `alexander`, `conway`, `jones` string fields to understand the polynomial format
2. Write a parser that converts each polynomial string into a list of integer coefficients (e.g., `"t^2 - 3t + 1"` → `[1, -3, 1]`)
3. Populate `alex_coeffs`, `jones_coeffs`, `conway_coeffs` for every knot that has the string representation
4. Write the updated `knots.json` back (same location, same structure, just with populated coefficient arrays)
5. Print a summary: how many knots got each type of coefficients populated

**Watch out for:** Different polynomial variable names (t, q, z), negative signs, missing terms, Laurent polynomials (negative powers), fractional coefficients in Jones polynomials.

**Validation:** After parsing, verify that for knots where `determinant` is known, `|Alexander(-1)| == determinant` (this is a mathematical identity and should hold for 100% of knots).

**Unblocks:** 9 knot tests on M1 (Alexander entropy, Alexander recurrence, Conway moments, knot det→Alexander enrichment, Jones mod-p, and more)

---

## Task 2: Fix polytope file path

**Location:** `cartography/polytopes/data/`
**Problem:** Scripts look for `polytopes.json` but the actual file is `Polytopes_Combinatorial_01Polytopes.json` with uppercase keys (`F_VECTOR`, `N_VERTICES`, `DIM`, `N_FACETS`, `N_EDGES`). There are also `Matroids_SelfDual.json` and `Matroids_Small.json`.

**What to do:**
1. Create `cartography/polytopes/data/polytopes.json` that normalizes the data:
   - Read `Polytopes_Combinatorial_01Polytopes.json` (100 polytopes)
   - Write a new `polytopes.json` with lowercase keys: `f_vector`, `n_vertices`, `dimension` (renamed from `DIM`), `n_facets`, `n_edges`
   - Keep the original files untouched
2. Print summary: how many polytopes, dimension range, whether f_vectors are present

**Unblocks:** 2 polytope tests (C27 f-vector F24, Euler characteristic)

---

## Task 3: Parse Fungrim git repo into JSON

**Location:** `cartography/fungrim/data/` — contains a cloned git repo but no parsed JSON
**Problem:** Scripts expect `fungrim_formulas.json` with fields like `type`, `symbols`, `module`. The raw Fungrim data is in the git repo format.

**What to do:**
1. Explore the Fungrim git repo structure in `cartography/fungrim/data/` (look for `.py`, `.json`, or XML files that define formulas)
2. The Fungrim project (https://fungrim.org) stores formulas as Python objects. Look for files like `formulas/*.py` or a database export
3. Parse into a JSON array of objects, each with: `id`, `type` (equation/definition/etc), `symbols` (list of math symbols used), `module` (which topic area), `formula_text` (string representation)
4. Write to `cartography/fungrim/data/fungrim_formulas.json`
5. Print summary: how many formulas, how many modules, how many unique symbols

**If the git repo doesn't contain parseable formula data:** Check `C:\prometheus_share\cartography\fungrim\` for a pre-parsed version that may exist on the share.

**Unblocks:** 7 Fungrim/formal math tests on M1 (symbol count, pi/zeta concentration, module structure, later-formula growth)

---

## Task 4: Build Maass Fricke join

**Location:** `cartography/maass/data/`
**Problem:** Two Maass files with incompatible ID schemes:
- `maass_forms_full.json` — 300 forms, has `maass_label` and `fricke_eigenvalue`
- `maass_with_coefficients.json` — 14,995 forms, has `maass_id` and `coefficients`
- Zero overlap on label/id fields

**What to do:**
1. Load both files
2. Join on `(level, spectral_parameter)` — both files have these fields. Use approximate matching on spectral_parameter (within 1e-6) since floating point may differ slightly
3. For each matched pair, add `fricke_eigenvalue` to the coefficients record
4. Write `maass_with_fricke.json` — same structure as `maass_with_coefficients.json` but with `fricke_eigenvalue` field added where available
5. Print summary: how many of 14,995 got Fricke values, how many +1 vs -1

**Unblocks:** 1 Maass Fricke test

---

## Task 5: Check NIST per-element JSONs for spectral config data

**Location:** `cartography/physics/data/nist_asd/`
**Problem:** `all_elements.json` has 99 elements but spectral lines lack `configuration` (electron config) fields. There are also per-element files like `Ac_levels.json`, `Ag_levels.json`, etc.

**What to do:**
1. Read one per-element file (e.g., `Fe_levels.json`) and examine its structure
2. Check if it has spectral line data with electron configuration (`conf`, `configuration`, `term`, etc.)
3. If yes: write a script that reads all per-element files and produces `nist_spectral_with_config.json` — a flat array of `{element, Z, wavelength, configuration, term}` records
4. If no: report what fields ARE available and whether config enrichment (C1) can be tested with what we have

**Unblocks:** 1 NIST test (C1 config enrichment)

---

## Where to put results

- Updated `knots.json` → `cartography/knots/data/knots.json` (overwrite in place)
- New `polytopes.json` → `cartography/polytopes/data/polytopes.json`
- New `fungrim_formulas.json` → `cartography/fungrim/data/fungrim_formulas.json`
- New `maass_with_fricke.json` → `cartography/maass/data/maass_with_fricke.json`
- New `nist_spectral_with_config.json` → `cartography/physics/data/nist_asd/nist_spectral_with_config.json`

**Commit with message:** `Data parsing: populate knot coefficients, normalize polytopes, parse Fungrim, join Maass Fricke, extract NIST config`

**Push when done** so both machines can pull the fixed data.
