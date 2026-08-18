# Report 187 — Frankl Union-Closed Sets Conjecture

Aporia Problem #187 | Domain: extremal combinatorics | Date: 2026-04-28
Doctrine: feedback_tensor_first, feedback_calibration_anchors_in_depth

## 1. Problem Statement

Frankl (1979) conjectured: for any finite family F of sets, |F| >= 2, that is closed under union (A, B in F implies A union B in F, with F not equal to {empty}), there exists an element x of the ground set lying in at least |F|/2 members of F. Equivalently, in the dual intersection-closed formulation, some element lies in at most |F|/2 sets. Despite a half-century of effort, the constant 1/2 resisted any constant-fraction lower bound until Gilmer (Nov 2022) used a sharp entropy / approximate-independence argument to prove an element appears in at least 0.01·|F| sets. Within weeks, Chase-Lovett, Sawin, Alweiss-Huang-Sellke, and Pebody pushed the constant to (3 - sqrt 5)/2 ~ 0.38197. Cambie (2023) reached ~0.38198, Yu (2023) ~0.38234, and Liu (2024+) ~0.38334. The ceiling 1/2 stands open. The substrate question: across union-closed families generated from canonical structures, can we compute maximum element-frequency exactly and stratify by family class?

## 2. Literature

- Frankl (1979) — original conjecture stated in problem session, Univ Paris.
- Reimer (2003) — established that average set size >= log_2|F| / 2; verified by exhaustion for all union-closed families with |F| <= 46 and ground set n <= 11.
- Bosnjak-Markovic (2008), Vuckovic-Zivkovic (2017) — extended exhaustive verification to |F| <= 50, n <= 12; 100% confirm 1/2 bound.
- Gilmer (Nov 2022, arXiv 2211.09055) — first constant-fraction bound 0.01·|F| via entropy of biased coin flips on the family.
- Chase-Lovett (Dec 2022, arXiv 2211.11689) — (3 - sqrt 5)/2 ~ 0.38197 via refined entropy with optimal p.
- Sawin (Dec 2022) — independent reconstruction; same constant; clarifies barrier at 0.38197 for the pure entropy method.
- Cambie (2023, arXiv 2301.13167) — 0.38198 via correlation refinement.
- Yu (2023) — 0.38234. Liu (2024+) — 0.38334 via three-set correlations.
- Karpas (2017), Knill (1994) — earlier conditional results: 1/2 holds when |F| >= 2^(n - O(log n)) or when smallest set size <= 2.

## 3. Computational Handle / Corpus

For ground set sizes n in {6, 8, 10, 12, 14}, generate union-closed families:

(a) **Downward-closures of random monotone Boolean f:{0,1}^n -> {0,1}**: sample monotone f via Dedekind enumeration for n <= 8, MCMC for n > 8; take F = {S : f(S) = 1}, then close under union.
(b) **Boolean lattice intervals** [A, B] = {S : A subset S subset B} for random pairs A subset B in 2^[n].
(c) **Steiner triple system upward-closures**: for n in {7, 9, 13, 15} take a Steiner triple system, generate F as the union-closure of the blocks. (n=15 only if memory budget allows; PATTERN_VRAM_TRUNCATION_ARTIFACT.)
(d) **Pyramid families**: F = {[1..k] : 1 <= k <= n} union {S} for chosen S; the canonical Frankl-tight construction.

PATTERN_VRAM_TRUNCATION_ARTIFACT: enumeration of 2^n subsets caps at n=14 (16384 subsets, ~3 GB family bitmap on dense storage). Beyond n=14 we sample, not enumerate; declare cap explicitly in metadata.

## 4. Test Design

1. **Generate** N_a = 1000 families per (class, n) cell for classes (a),(b); exhaustive enumeration for class (d); all designs of given parameters for class (c). Encode each family as a uint16 / uint32 bitmask vector for n <= 32.
2. **Verify union-closure** via O(|F|^2) check; reject and re-sample if violated (sanity gate, expected failure rate 0 by construction).
3. **Compute element-frequency vector** v_x = |{S in F : x in S}| for each x in [n]; record rho(F) = max_x v_x / |F|.
4. **Stratify** by (class, n, |F|) into bins; report mean, median, min, p05, p95 of rho(F) per stratum; flag any family with rho < 0.5 (would counterexample) and any with rho < 0.6 (Frankl-tight regime).
5. **Cross-check** Gilmer-Chase-Lovett bound 0.38197 and Liu bound 0.38334: for each stratum report fraction of families saturating each tier; compute empirical infimum of rho across all generated families.

Output tensor: shape (class, n, |F|-bin, statistic) -> rho. Persist as techne calibration anchor under signature `extremal_set.union_closed.element_frequency`.

## 5. Falsification

- **Calibration anchor**: Reimer's exhaustive enumeration for n <= 11 gives ground truth distribution of rho across all union-closed families; substrate must reproduce these to <1e-9 in distribution.
- **PATTERN_BASE_RATE_NEGLECT**: every reported statistic carries (n_families_in_stratum, generation_method); never quote rho averages without n. Pyramid stratum is single-family per n, not statistical.
- **Null**: random subset families closed under union by construction (downward-closure of random antichains) versus structured (Steiner, intervals) — non-overlapping rho distributions would indicate family-class is a real stratifier rather than artifact.
- **PATTERN_VRAM_TRUNCATION_ARTIFACT**: enumeration cutoff at n=14 declared; any n > 14 result is sampled and labeled.

## 6. Budget

Ergon ~6 hours single-machine. Breakdown: 1.5h enumeration + bitmask infrastructure for n <= 12; 2.5h sampling/closure for n=13,14; 0.5h Steiner system construction (existing libraries); 1h stratified statistics + tensor persistence; 0.5h calibration vs Reimer ground truth. No GPU required; pure CPU bitmask ops.

## 7. Expected Outcome

Per feedback_calibration_anchors_in_depth, the deliverable is a calibration anchor in the extremal-set-system region of the substrate tensor — currently under-populated relative to L-functions and modular forms. Two concrete expectations: (i) confirms 0.5 bound holds across ~10^5 generated families (no counterexample expected; Frankl is widely believed true); (ii) reveals the empirical infimum of rho on canonical families, distinguishing classes where rho clusters near 0.5 (pyramid-like, tight) from classes where rho ~ 0.7-0.9 (Steiner upward-closures, intervals). If empirical infimum on a structured class falls below 0.5 we have refuted Frankl with explicit witness — extraordinary outcome; if infimum sits at 0.5 with measure-zero saturation by pyramid-class, this provides the substrate's first quantitative map of where Frankl-tightness lives, a structural hypothesis the entropy-method literature does not currently produce. Result feeds feedback_tensor_first by adding a populated cell to the extremal-combinatorics axis of the unified signature-keyed tensor.

Word count: ~770
