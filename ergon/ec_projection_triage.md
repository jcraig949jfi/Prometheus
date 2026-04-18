# EC L-function Zero Projections — Open Projection Triage

**Source:** `cartography/docs/harvest_ec_lfunc_zero_projections.md` (Harmonia Path 4 harvest)
**Date:** 2026-04-15
**Triaged by:** Ergon

## Summary Table

| # | Open Projection | Data Available? | Difficulty | Scientific Value | Verdict |
|---|---|---|---|---|---|
| 1 | Projection by reduction type at bad primes | Partial — need local computation from ainvs | Medium | High | TESTABLE with work |
| 2 | Projection by Atkin-Lehner eigenvalue pattern | NO — not in ec_curvedata; need per-prime w_p | Hard | High | BLOCKED without new data |
| 3 | Projection by isogeny class size | YES — class_size in ec_curvedata | Easy | Medium | READY NOW |
| 4 | Projection by Tamagawa product | NO — only in g2c_curves, not ec_curvedata | Medium | High | TESTABLE with computation |
| 5 | Projection by Sha order (BSD-predicted) | YES — sha in ec_curvedata | Easy | High | READY NOW |
| 6 | Murmuration correlation | YES — rank + conductor in ec_curvedata | Medium | High | TESTABLE |
| 7 | Compound stratification (rank x CM x w) | YES — rank, cm, signD in ec_curvedata | Easy | Medium | READY NOW |
| 8 | Murmuration of zeros (1st zero vs conductor) | Partial — need positive_zeros from lfunc (342GB, slow) | Hard | High | TESTABLE but expensive |

**Ready now: 3 | Testable with work: 3 | Blocked: 1 | Testable but expensive: 1**

---

## Data Inventory

### ec_curvedata (3,824,372 curves)

Available columns (53 total): id, Clabel, lmfdb_label, Ciso, lmfdb_iso, regulator, ainvs, jinv, min_quad_twist_ainvs, iso_nlabel, Cnumber, lmfdb_number, cm, num_bad_primes, optimality, manin_constant, torsion, rank, analytic_rank, signD, class_deg, class_size, min_quad_twist_disc, faltings_index, faltings_ratio, isogeny_degrees, nonmax_primes, torsion_structure, torsion_primes, sha_primes, conductor, nonmax_rad, num_int_pts, sha, bad_primes, degree, semistable, potential_good_reduction, absD, faltings_height, stable_faltings_height, elladic_images, modell_images, adelic_level, adelic_index, adelic_genus, modm_images, abc_quality, szpiro_ratio, serre_invariants, intrinsic_torsion, squarefree_disc

**Rank distribution:** rank 0: 1,404,510 | rank 1: 1,887,132 | rank 2: 493,291 | rank 3: 37,334 | rank 4: 2,086 | rank 5: 19

### lfunc_lfunctions (~1.74M EC/Q L-functions, 24M total)

- `positive_zeros`: stored as JSON string arrays (e.g. `[0.474, 1.083, ...]`), confirmed populated for EC/Q origins
- Indexed on: origin (enables EC/Q prefix filter), conductor, degree, order_of_vanishing
- **WARNING:** 342GB table. Full scans are infeasible. Must use indexed queries.

### Missing tables

- `ec_localdata` — does NOT exist in our mirror. Would contain per-prime Tamagawa numbers and reduction type.
- `ec_mwbsd` — does NOT exist. Would contain BSD invariants consolidated.
- Tamagawa product only in `g2c_curves` (genus 2), not elliptic curves.

---

## Detailed Triage

### 1. Projection by reduction type at bad primes

**What:** Stratify zero statistics by whether each bad prime has split multiplicative, nonsplit multiplicative, or additive reduction.

**Data needed:** For each curve, the reduction type at each bad prime p | N.

**Do we have it?** Partially. ec_curvedata has `bad_primes`, `ainvs`, `conductor`, `semistable`, and `potential_good_reduction`. The reduction type can be computed from the a-invariants using Tate's algorithm. We do NOT have it pre-computed — ec_localdata is absent from our mirror.

**Computation required:**
1. Implement Tate's algorithm or use SageMath to classify reduction type from ainvs for each bad prime.
2. Join with zeros from lfunc_lfunctions via label matching.
3. Compute 1-level density or nearest-neighbor spacing stratified by reduction type partition.

**Difficulty:** Medium. Tate's algorithm is standard but running it on 3.8M curves x multiple bad primes is nontrivial. Could use SageMath batch processing. The zero-join step adds cost.

**Scientific value:** High. This is genuinely open — no RMT prediction for how reduction type at bad primes affects zero distribution. Direct connection to local-global phenomena.

**Verdict:** TESTABLE. Priority candidate. Start with semistable-only curves (boolean already available) as a quick first cut before full Tate classification.

---

### 2. Projection by Atkin-Lehner eigenvalue pattern

**What:** Stratify zero densities by the joint pattern of local Atkin-Lehner eigenvalues w_p at each prime p | N.

**Data needed:** The eigenvalue w_p = +1 or -1 at each p | N. The product gives the global root number, but the individual pattern matters.

**Do we have it?** NO. ec_curvedata stores `signD` (related to global sign) but not per-prime Atkin-Lehner eigenvalues. The modular forms table (`mf_newforms`) has `atkin_lehner_eigenvals` but linking EC curves to their associated newforms requires label-matching infrastructure we don't have pre-built. The lfunc table has `root_number` (global only).

**Computation required:**
1. Either: compute w_p from ainvs via local Neron model data, OR
2. Build EC-to-newform label mapping and pull from mf_newforms.
3. Then stratify zero statistics by the full w_p pattern vector.

**Difficulty:** Hard. Computing individual w_p requires local arithmetic at each bad prime. Alternative route via mf_newforms requires a label crosswalk that doesn't exist in our schema.

**Scientific value:** High. The Atkin-Lehner pattern encodes arithmetic structure beyond the global root number. Interaction between local eigenvalues and zero distribution is unexplored.

**Verdict:** BLOCKED without new data or significant computation. Defer unless we add ec_localdata to the mirror or build the newform crosswalk.

---

### 3. Projection by isogeny class size

**What:** Stratify zero statistics by the number of curves in each isogeny class.

**Data needed:** `class_size` (number of curves in the isogeny class) per curve, plus zeros.

**Do we have it?** YES. `class_size` is a column in ec_curvedata. Values typically range from 1 to ~8 for most classes.

**Computation required:**
1. Join ec_curvedata.lmfdb_label with lfunc_lfunctions.origin to get zeros per curve.
2. Group by class_size.
3. Compute zero spacing statistics (1-level density or gap distribution) per group.

**Difficulty:** Easy. Data is ready, join is straightforward via indexed origin column.

**Scientific value:** Medium. Isogeny class size reflects the structure of the isogeny graph, and its interaction with zero distribution has no classical prediction. However, class size is correlated with conductor and rank, so careful detrending needed.

**Verdict:** READY NOW. Good first target — low cost, clear signal-or-null outcome. Already covered by P100 in Prometheus catalog.

---

### 4. Projection by Tamagawa product

**What:** Stratify zero statistics by the Tamagawa product (product of local Tamagawa numbers c_p over all bad primes).

**Data needed:** Tamagawa numbers c_p at each bad prime, or their product.

**Do we have it?** NO in ec_curvedata. The column exists in `g2c_curves` (genus 2) but not for elliptic curves. ec_localdata (which would store per-prime Tamagawa numbers) is absent from our mirror.

**Computation required:**
1. Compute Tamagawa numbers from ainvs using Tate's algorithm (same algorithm as projection #1, different output).
2. Take the product over all bad primes.
3. Join with zeros and stratify.

**Difficulty:** Medium. Same computation as #1 (Tate's algorithm), so these two projections share infrastructure. If we do one, we get the other nearly free.

**Scientific value:** High. The Tamagawa product appears in the BSD formula. Testing whether it correlates with zero distribution beyond what BSD predicts is a genuine open question. Could connect to the F011 rank-0 residual finding.

**Verdict:** TESTABLE. Pair with projection #1 — same Tate algorithm computation yields both reduction type and Tamagawa numbers.

---

### 5. Projection by Sha order (BSD-predicted)

**What:** Stratify zero statistics by the analytic order of Sha (Shafarevich-Tate group).

**Data needed:** `sha` per curve, plus zeros.

**Do we have it?** YES. `sha` is in ec_curvedata (BSD-predicted value). Distribution is heavily concentrated at sha=1 but with meaningful tails.

**Computation required:**
1. Join ec_curvedata with lfunc_lfunctions on label/origin.
2. Bin by sha value (1, 4, 9, 16, 25, ...).
3. Compute zero statistics per bin.

**Difficulty:** Easy. Data and join infrastructure are ready.

**Scientific value:** High. Sha is the most mysterious arithmetic invariant. Whether it modulates zero distribution beyond what's predicted by rank alone is a genuine frontier question. Directly relevant to F011 rank-0 residual.

**Verdict:** READY NOW. High-priority target. Already flagged as P038 in catalog.

---

### 6. Murmuration correlation

**What:** The He-Radziwill-Soundararajan (2023) discovery: correlation between a_p values and analytic rank exhibits unexpected oscillatory structure as a function of conductor window.

**Data needed:** `rank` and `conductor` from ec_curvedata. Also need a_p values for each curve at many primes p (not stored in ec_curvedata).

**Do we have it?** Partially. Rank and conductor are available. The a_p values must be computed from the a-invariants, which requires evaluating the curve at each prime — a significant computation for 3.8M curves across many primes.

**Computation required:**
1. For each curve, compute a_p for primes p up to some bound (e.g., p < 10000).
2. Compute the murmuration correlation function: avg(a_p) over curves in conductor windows, stratified by rank.
3. Compare with the He-Radziwill-Soundararajan prediction.

**Difficulty:** Medium. Computing a_p for millions of curves at thousands of primes is CPU-intensive but parallelizable. SageMath or PARI/GP can do this. The statistical analysis is straightforward once a_p values exist.

**Scientific value:** High. Murmurations are a 2023 discovery with active research. Reproducing and extending the finding with our 3.8M curve dataset (likely the largest attempted) would be scientifically valuable. Already covered by P023.

**Verdict:** TESTABLE. Consider sampling: start with conductor windows where we have dense coverage.

---

### 7. Compound stratification (rank x CM x w)

**What:** Joint sub-family zero statistics when stratifying simultaneously by rank, CM status, and root number.

**Data needed:** `rank`, `cm`, `signD` (proxy for root number), plus zeros.

**Do we have it?** YES. All three stratification variables are in ec_curvedata.

**Computation required:**
1. Create combined bins (e.g., rank=0, CM=yes, sign=+1).
2. Join with lfunc_lfunctions for zeros.
3. Compute 1-level density or gap statistics per combined bin.
4. Test whether compound stratification reveals structure beyond marginal stratifications.

**Difficulty:** Easy. All data available, standard statistical computation.

**Scientific value:** Medium. The compound effect is the scientific question — does joint conditioning reveal structure invisible to marginal conditioning? This is well-motivated but may just confirm existing single-variable projections. Gets interesting at rank >= 2 where individual projections are already open.

**Verdict:** READY NOW. Low-hanging fruit. Leverage existing P023 + P025 infrastructure.

---

### 8. Murmuration of zeros (1st zero vs conductor)

**What:** He-Lee (2024): the mean height of the first zero above the central point oscillates as a function of conductor. Extension of murmuration from a_p correlations to zero heights.

**Data needed:** First positive zero height per curve + conductor.

**Do we have it?** Partially. `positive_zeros` in lfunc_lfunctions contains zero arrays including the first zero. `conductor` is in both tables. But querying 1.74M EC L-functions from the 342GB lfunc table is expensive and slow.

**Computation required:**
1. Extract first zero from positive_zeros for all EC/Q L-functions (massive I/O on 342GB table).
2. Bin by conductor windows.
3. Compute mean first-zero height per window.
4. Look for oscillatory structure and compare with He-Lee prediction.

**Difficulty:** Hard. The main bottleneck is I/O: extracting positive_zeros from lfunc_lfunctions for ~1.74M EC rows on a 342GB table with no origin index on... wait, there IS an origin index. So filtering to EC/Q is index-assisted, but parsing 1.74M JSON arrays of zeros is still heavy.

**Scientific value:** High. This is a 2024 result, extremely fresh. Confirming or extending it with LMFDB's full conductor range would be a significant contribution. Not yet catalogued in Prometheus.

**Verdict:** TESTABLE but expensive. Start with a conductor-range subsample (e.g., N < 100000) to prototype. Full computation may take hours.

---

## Recommended Execution Order

1. **Projection 3 (isogeny class size)** — Ready now, easy, fast sanity check
2. **Projection 5 (Sha order)** — Ready now, easy, high scientific value
3. **Projection 7 (compound rank x CM x w)** — Ready now, easy, extends existing work
4. **Projection 8 (murmuration of zeros)** — Start subsample prototype while above run
5. **Projections 1+4 (reduction type + Tamagawa)** — Bundle together, share Tate algorithm
6. **Projection 6 (murmuration correlation)** — Needs a_p computation, medium effort
7. **Projection 2 (Atkin-Lehner pattern)** — Blocked until data gap resolved

## Infrastructure Notes

- **Zero-join pattern:** All projections need ec_curvedata joined with lfunc_lfunctions. Build a reusable join once: `lfunc_lfunctions.origin = 'EllipticCurve/Q/' || ec_curvedata.lmfdb_label`. The origin index makes this feasible.
- **Tate algorithm batch:** Projections 1 and 4 share the same computation. Implement once, extract both reduction type and Tamagawa numbers.
- **ec_localdata gap:** Our LMFDB mirror is missing ec_localdata. Adding this single table would unblock projections 1, 2, and 4 without any local computation. Check if it's available in the LMFDB dump.
