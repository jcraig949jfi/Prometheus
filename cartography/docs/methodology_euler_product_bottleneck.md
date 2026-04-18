# Methodology Note — The Euler-Product Bottleneck at k ≥ 3

**Written by:** Harmonia_M2_sessionC, 2026-04-18
**Scope:** Documents why the Keating-Snaith CFKRS comparison (W1, T1) stalls at `k ≥ 3` for both rank-0 (SO_even) and rank-1 (SO_odd) families, and what data / compute would unblock it. Filed so future workers don't repeat the diagnostic.

---

## The symptom

Empirical moment ratios `R_k(X) = M_k(X) / (log X)^{k(k±1)/2}` at decades `10^3..10^6`:

- **Rank 0** (W1 commit `6a69cc8c`): k=1,2 converge cleanly to CFKRS shape (empirical/theory ratio 0.62 → 1.00 monotone). k=3 non-monotone mid-decade overshoot. k=4 ratio decreases from 3.18 — wrong sign of correction.
- **Rank 1 under correct exponent `k(k+1)/2`** (T1 commit `b081990c`): k=1,2 CALIBRATION_CONFIRMED (same 5-10% second-largest-decade deviation, monotone). k=3 max deviation 37% non-monotone. k=4 max deviation 199%. Same structure as rank-0 exactly.

The pattern is **not a rank / family failure** — it's a shared bottleneck that clicks in at `k ≥ 3`.

## Root cause

My CFKRS comparison deflates by a *proxy* arithmetic factor: I force `R_k / a_proxy(k) = 1` at the largest decade and check shape convergence from below. That is correct for `k = 1, 2` where:

- The arithmetic factor `a_E(k)` is close to its Euler-product value from just the first few primes
- The leading `(log X)^{k(k-1)/2}` dominates the curve's leading-term structure
- The shape test is only sensitive to the first-order sub-leading `1/log X` correction, which the proxy captures

At `k ≥ 3`:

- The arithmetic factor `a_E(k) = ∏_p (1 - 1/p)^{k²} · E[|L_p(1,E)|^{2k}]` contains a `(1 - 1/p)^{k²}` factor that is numerically small and depends sensitively on the full prime product
- Truncating to the first 25 primes (W4's coverage) captures only ~70-87% of the product's magnitude (Pearson 0.87, Spearman 0.95 — W4 commit `1c08e40e`)
- The remaining 13-30% of the factor is *structured* (not just noise) because large primes in the tail enter `a(k)` through their rare appearance as bad primes and as slow-decaying contributions to the Euler sum
- At `k ≥ 3` the moment is dominated by the **upper tail** of `leading_term`, where a small number of curves contribute disproportionately. These curves' exact `a_E(k)` values are exactly the ones mis-estimated by truncation

Proxy-calibration by forcing `R_k / a_proxy(k) = 1` at largest decade then converts this into a shape-convergence check, but the shape itself becomes distorted when the proxy is biased upward (rank-0 k=4 ratio decreases rather than approaching 1 from below).

## What's required to unblock

**Data:**

1. **Full Dirichlet coefficients** for each EC L-function out to `n ≥ 10^5` primes. Would let us compute the Euler product to sufficient precision that per-curve `a_E(k)` is accurate to 1% at `k = 3, 4`.
   - **Blocked by:** `lmfdb.public.lfunc_lfunctions.dirichlet_coefficients` is NULL for the elliptic-curve rows we care about (W4 diagnostic)
   - `euler_factors` column covers only primes `p ≤ 97` (first 25 primes)

2. **Alternative data source:** compute `a_p` per curve directly from the Weierstrass equation via Hasse bound + reduction mod p, then assemble local `L_p` factors. Feasible with PARI/Sage per-curve but 2M curves × 10^5 primes = 2×10^11 operations → multi-day compute on a single node.

**Compute:**

3. **Family-average `a(k)`** (rather than per-curve): if we can compute the ensemble-average arithmetic factor for the SO_even / SO_odd families separately at `k = 3, 4`, deflating by the family-average isolates pure RMT and the shape test becomes clean. Sub-problem: need to evaluate the family-average explicitly from the conjectural CFKRS recipe, which involves a specific Dirichlet series that converges slowly at `k = 3, 4`.

4. **Numerical Monte Carlo on SO(2N) / SO(2N+1)**: simulate `det(A)^k / (log T)^{k(k-1)/2}` on Haar-random orthogonal matrices at `N = log(conductor) / 2π`, then compare to empirical moments directly. Bypasses the analytical Euler product by turning the RMT side into a pure numerical artifact. **Viable with 10⁵ MC samples**; already demonstrated as a tool in W5 commit `9afc3036`.

## Status

- **k=1, k=2**: calibrated via proxy at both rank 0 (SO_even) and rank 1 (SO_odd). CFKRS confirmed to within 5-10% deviation, approach-from-below, sub-leading B-coefficient at correct negative sign with z ≤ −2.
- **k=3, k=4**: FRONTIER until one of the three unblockers above is in place.

**Recommendation:** option 4 (numerical MC on SO) is the cheapest unblocker — entirely tool-side, no LMFDB data changes. Option 3 (family-average analytical `a(k)`) is the cleanest. Option 1 (Dirichlet coefficients) is the most thorough but requires upstream LMFDB data work.

## Catalog cross-references

- `P052` (microscope prime decontamination) — related: P052 proxy-detrends on prime features but doesn't compute the full `a_E(k)`
- `P103` (modular degree, DERIVABLE-NOT-STORED) — same general class of "computable-per-curve but not in our mirror" quantities
- `P035` (Kodaira, DERIVABLE-NOT-STORED) — another

Pattern: **3 of our last 15 proposed catalog entries have hit the same "requires per-curve Magma/Sage compute" bottleneck.** The materialization backlog is the real instrument-level gap; worth raising to Mnemosyne/Koios as a single infra task that would unblock multiple specimens simultaneously.

## Not doing today

- Do NOT raise `a_E(k)` truncation limit from 25 primes to larger — the euler_factors column simply does not contain more primes for these L-functions
- Do NOT implement per-curve Magma compute without James / Mnemosyne / Koios sign-off — 2M curves × 10⁵ primes is a large compute and storage commitment
- Do NOT report `k ≥ 3` CFKRS results as "frontier finding" — the FRONTIER tag means "unblockable data / compute gap", not "novel structural signal"

---

*End of note. Filed as methodology for future workers picking up the Keating-Snaith thread. Companion commit references: W1 `6a69cc8c`, W4 `1c08e40e`, T1 `b081990c`.*
