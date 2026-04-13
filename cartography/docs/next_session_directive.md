# Next Session Directive
## The zeros. Nothing else until the zeros are right.

---

## What's done

- 40-test battery (F1-F38 + 5 interpretation layers)
- 17 kills proving invariant-level cross-domain structure is illusory
- 10 negative dimensions carved (ordinal, magnitude, distributional, preprocessing, engineering, tautology, prime, partial-correlation, trivial baseline, raw-data)
- 7 known theorems at 100.000% on 3.8M objects
- TT-Cross bonds survive Megethos removal (tensor-level structure is real)
- EC-Maass GL(2) shared structure confirmed (2 extra channels, known math)
- ZERO novel cross-domain bridges at invariant level

## What's next (in order)

### Step 1: Unfold the L-function zeros

The 120K stored zeros in `charon/data/charon.duckdb` (table: `object_zeros`) are RAW — not normalized by the smooth zero density.

**Unfolding formula:** For the n-th zero gamma_n of an EC L-function at conductor N:
- Smooth counting function: N(T) = (T/2pi) * log(NT/(2pi*e)) + O(1)
- Unfolded zero: theta_n = N(gamma_n) (maps to uniform spacing under GUE)
- Normalized gap: s_n = theta_{n+1} - theta_n (should follow Wigner surmise under GUE)

**Data source:** `object_zeros` table has `zeros_vector` (JSON array of imaginary parts), `conductor` (for the smooth density), `n_zeros_stored`, `root_number`, `analytic_rank`.

**Stratify by:**
- root_number (+1 vs -1) → SO(even) vs SO(odd) symmetry
- analytic_rank (0 vs 1 vs 2+) → central zero behavior
- conductor range (finite-size effects)

**Success criterion:** Unfolded gap variance = 0.180 ± 0.005 (GUE) for rank-0 EC with root_number=+1 (SO(even) family). This is the 7th theorem at 100.000%.

### Step 2: Build the spectral feature set

From properly unfolded zeros, compute per-object features:
- First 10 normalized gaps (s_1 through s_10)
- Gap variance, skewness, kurtosis
- Nearest-neighbor spacing ratio (r_n = min(s_n, s_{n+1}) / max(s_n, s_{n+1}))
- Number variance Sigma_2(L) for L = 0.5, 1.0, 2.0
- Delta_3 rigidity statistic

These are the "spectral phonemes" — derived from the zeros themselves, not from invariants.

### Step 3: Test spectral transport (the F26 test)

Replace invariant-based features with zero-derived features in the TT-Cross coupling. If cross-domain bond dimension increases, the zeros are a BETTER representation of the primitive than the invariants. If it decreases, even the zeros are incomplete projections.

**The key comparison:**
- TT-Cross bond (invariant features, Megethos-zeroed): rank 2 for EC-Maass
- TT-Cross bond (spectral features): rank ???
- If rank increases: the spectral level sees MORE of the primitive
- If rank stays same: the spectral level sees DIFFERENT aspects, not more
- If rank decreases: the invariants were actually closer (unlikely)

### Step 4: The spectral tail residual

Only after Steps 1-3. The 0.05 ARI residual from zeros 5-19 has survived 16 OLD kill tests. It has never faced:
- F24 permutation-calibrated eta²
- F33 rank-sort null
- F36 partial-correlation strengthening null
- F38 raw-data verification
- The full 40-test battery

If it survives the upgraded battery, it's the first genuine finding that outlasted every artifact we could construct. If it doesn't, it was the 18th kill.

## What NOT to do

- Do NOT explore more invariant-level cross-domain claims (exhausted)
- Do NOT add more battery tests until F33-F38 are implemented
- Do NOT chase new domains (chemistry, finance, source code) until the zeros are calibrated
- Do NOT trust any zero-spacing statistics computed on raw (unfolded) zeros

## Data locations

- L-function zeros: `charon/data/charon.duckdb`, table `object_zeros` (120K objects)
- Live Postgres: 3.8M EC with full data (M1 has connection)
- Maass coefficients: `cartography/maass/data/maass_with_coefficients.json` (14,995 forms)
- 919K non-EC newforms: accessible via Postgres `modular_forms` table

## The bar

3.8 million objects. 100.000% on six theorems. The seventh theorem (Montgomery-Odlyzko / GUE) must match this precision before anything else proceeds.
