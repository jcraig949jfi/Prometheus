# Deep Research Report #159: Erdős Minimum Overlap Problem

**Target Agent:** Ergon
**Date:** 2026-04-26
**Front:** Erdős corpus expansion (Batch 9 Tier 1)
**Structural region:** additive combinatorics / extremal set theory (corpus tag: Erdős, bibliography only)

## 1. Problem Statement

For each n, partition [1, 2n] into two equal-sized sets A, B with |A| = |B| = n and A ∪ B = [1, 2n]. Define the overlap function f_{A,B}(k) = |A ∩ (B + k)| for integer shifts k, and let

  M_n = min_{(A,B)} max_k f_{A,B}(k).

Erdős (1955) conjectured M_n / n → c for some explicit constant c ≈ 0.42. The exact value of c remains open. Best known unconditional bounds place c ∈ [≈0.379, ≈0.443] from interleaved work by Newman, Hofmann, Liu–Sárközy, and Belov–Konyagin. The structural region is interesting because the extremal partitions appear to inherit near-arithmetic-progression form, putting the problem at the intersection of additive combinatorics and discrepancy theory. For Prometheus the empirical M_n sequence is a candidate operator-natural constant: a clean univariate signal we can feed into the unified-tensor build (`feedback_tensor_first`) without heavy preprocessing.

## 2. Literature

- **Erdős (1955)** *Some remarks on number theory* — original conjecture and trivial bounds.
- **Newman (1959, 1963)** — early upper bound c ≤ ~0.475 via explicit construction.
- **Swinnerton-Dyer / Moser correspondence (1960s)** — small-n exact values.
- **Hofmann (1980s)** — exact computations of M_n up to n ≈ 15 by direct enumeration.
- **Liu and Sárközy (1990s)** — improved analytic upper bounds via Fourier-analytic averaging.
- **Belov and Konyagin (1990s, 2000s)** — sharpened lower bound to ≈ 0.379 via character-sum methods.
- **Erdős–Graham *Old and New Problems and Results in Combinatorial Number Theory* (1980)** — problem #29.
- **Bloom catalog** (`erdosproblems.com/40`) — current canonical tracking entry.

## 3. Computational Handle

Direct enumeration of subsets A ⊂ [1, 2n] with |A| = n is C(2n, n), tractable to n ≈ 25 with symmetry-breaking (fix 1 ∈ A) and DP over the prefix-counting state. SDP / LP relaxations give upper bounds for n up to ≈ 50 by relaxing f_{A,B}(k) to a real-valued autocorrelation. Constraint-programming solvers (OR-tools, MiniZinc) handle n ≈ 30–40 in hours of wall time on Skullport. The optimal A appears to concentrate near {1, 4, 5, 8, 9, …}-type quasi-periodic patterns, suggesting the extremizer has sub-Sidon arithmetic structure.

## 4. Test Design

**Step 1.** Replicate Hofmann at n ≤ 25 by direct DP enumeration. Output: exact M_n table, store at `aporia/mathematics/erdos_overlap/M_n_exact.json`.

**Step 2.** Extend to n = 30–40 using parallel CP-SAT on Skullport (8-core), seeded from Step 1 extremizers. Record both M_n and any tied extremizers.

**Step 3.** Extract structural signature of each extremizer: gap sequence, autocorrelation, Fourier spectrum on Z/2nZ. Compare against Sidon, B_2[g], and arithmetic-progression families.

**Step 4.** Compute the Megethos signature M(M_n / n − c) for candidate c ∈ {0.379, 0.40, 0.4146, 0.42, 0.443} per `project_megethos`; the operator-natural c should display the cleanest scaling exponent and lowest Megethos residual. Cross-reference with V5 strategy bank (`aporia/mathematics/v5_discovery_shortlist.json`) for any sequence already showing the same exponent.

## 5. Falsification

- **Lower-bound kill:** if Step 2 produces certified M_n / n > 0.42 for any n in 30–40, the commonly quoted c ≈ 0.42 ceiling is dead and the Belov–Konyagin lower bound becomes the new floor for c.
- **Upper-bound sharpening:** any explicit construction giving M_n / n < 0.40 at n ≥ 35 contradicts Liu–Sárközy's published constant and is publishable on its own.
- **Structural kill:** if extremizers fail to converge to a single arithmetic-combinatorial family (e.g., split into two equally good non-isomorphic structural classes), the "near-AP" folklore is wrong.
- **Megethos null:** if no candidate c gives a Megethos residual below the all-c baseline by ≥ 2σ, the constant is not operator-natural and the tensor link is vacuous — kill the cross-domain claim immediately (`feedback_assume_wrong`).

## 6. Budget

Ergon ~6 hours total. Enumeration code (~2h) reusing patterns from `ergon/gap_k_scan.py` and `ergon/cm_gap_k_scan.py`. Parallelized run on Skullport for n up to 35 (~2h compute, dispatched as a batched script per `feedback_rhea_scripts`). Structural / Megethos analysis (~1h) using existing tooling under `aporia/mathematics/`. Writeup and JSON artifact emission (~1h). No new tools required; Sage and Python with OR-tools suffice.

## 7. Expected Outcome

Sharper numerical bounds on M_n / n for n in the 25–40 window; a structural-signature vector for each extremizer suitable for ingestion into the unified tensor as a row in the additive-combinatorics structural region. Either (a) a tight new numerical bound that survives the Megethos null and earns a row in `aporia/mathematics/v5_discovery_shortlist.json`, or (b) a clean kill of the 0.42 folklore constant. Secondary payoff: cross-link to the extremal Sidon-set literature already adjacent to Megethos, opening a candidate bridge between Erdős-type minimum problems and the operator-natural-constant catalog.

**Word count: 760**
