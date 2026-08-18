# Deep Research Report #161: Erdős-Ginzburg-Ziv Tight Extremal Sequences

**Target Agent:** Ergon
**Date:** 2026-04-26
**Front:** Erdős corpus expansion (Batch 9 Tier 2)
**Doctrine:** `feedback_tensor_first`, `feedback_domains_are_docstrings`, `feedback_verbs_over_nouns`, `feedback_assume_wrong`

## 1. Problem Statement

The Erdős-Ginzburg-Ziv theorem (1961) states: every sequence of 2n−1 integers contains a subsequence of length n whose sum is ≡ 0 (mod n). The bound is tight — sequences of length 2n−2 exist with no zero-sum n-subsequence. In the verb framing (`feedback_verbs_over_nouns`), the operator is **admits-zero-sum-subsequence-of-length-n**; the sequence is the object the operator acts on. An *EGZ-extremal* sequence is a length-(2n−2) sequence in (Z/nZ) on which this operator returns false. Classical structure: every extremal sequence consists of two distinct residues each repeated exactly n−1 times (the "two-value" form). For n prime this is fully proved (Bialostocki-Dierker 1992, Caro 1996). **Open question for n composite:** are *all* extremal sequences of two-value form, and what is the exact count C_k(n) of length-(2n−1) sequences with exactly k zero-sum n-subsequences for small k? This sits squarely in the additive-combinatorics structural region (`feedback_tensor_first`) and feeds the Davenport-constant / zero-sum tensor.

## 2. Literature

- **Erdős-Ginzburg-Ziv (1961):** original theorem and tightness construction.
- **Bialostocki-Dierker (1992):** structural theorem for n prime; first count of zero-sum n-subsequences.
- **Caro (1996):** survey + tightening of the prime-case characterization.
- **Geroldinger-Halter-Koch (2006) monograph:** *Non-Unique Factorizations* — Davenport-constant generalization D(G), zero-sum free sequences over abelian groups.
- **Geroldinger-Schmid (2000s, ongoing):** extremal characterization for n composite explicitly listed as incomplete; partial results for n = pq, n = p².
- **Bloom catalog (erdosproblems.com):** entry on EGZ extremal structure flagged as Tier 2 open.

## 3. Computational Handle

For n ≤ ~20, the search space (Z/nZ)^(2n−2) is bounded by n^(2n−2) raw sequences; quotient by S_{2n−2} permutation symmetry and (Z/nZ)* multiplication makes n ≤ 15 tractable. The decision problem **does this sequence have a zero-sum n-subsequence?** is solvable by O(n²·(2n−1)) dynamic programming on the partial-sum lattice. Structural classification (counting distinct residues, multiplicities) is direct after enumeration. Existing Ergon scaffolding (`F:\Prometheus\ergon\dirichlet_nbp_test.py`, `F:\Prometheus\ergon\gap_k_scan.py` patterns) gives a template for parallel sweep + null comparison.

## 4. Test Design

- **Step 1.** Exhaustive scan at n ∈ {8, 9, 10, 12, 15, 16} — mix of prime-power (8, 9, 16), prime-times-prime (15), and even-composite (10, 12). Enumerate length-(2n−2) sequences over Z/nZ up to symmetry; flag every extremal one; record residue multiset.
- **Step 2.** At each composite n, scan the extremal set for any sequence whose residue multiset is *not* {a^(n−1), b^(n−1)} for distinct a, b. A single counterexample at n ≤ 15 is publishable.
- **Step 3.** For n ∈ {8, 9, 10, 12}, count C_k(n) for k = 1, 2, 3 over length-(2n−1) sequences. Fit log C_k(n) vs n; check whether a clean polynomial-in-n or n^(αn) law emerges.
- **Step 4.** Structural-signature cluster the k = 1 (almost-extremal) sequences via residue-histogram + GCD-with-n features. Compare prime-n vs composite-n clusters. Push signatures to the unified tensor (`F:\Prometheus\ergon\tensor.npz` schema).

## 5. Falsification

Quantitative outcomes (`feedback_assume_wrong` — assumptions wrong until proven):

- **Discovery:** any non-two-value extremal sequence at composite n ≤ 15 → publishable counterexample to the folklore conjecture.
- **Empirical reinforcement:** zero counterexamples through n = 16 → strongest computational evidence to date for the two-value characterization at composite n.
- **Asymptotic identity:** clean fit log C_1(n) ~ α·n + β·log n with R² > 0.999 → candidate new identity, cross-check against Geroldinger-Schmid bounds.
- **Null:** shuffle the operator (random k-subsequence sums) — extremal density must collapse, otherwise the test is vacuous.

## 6. Budget

Ergon ~6 hours total. Enumeration code with permutation-symmetry quotient and DP zero-sum oracle: ~2h (target: `F:\Prometheus\ergon\egz_extremal_scan.py`). Parallel run on Skullport across n ∈ {8..16}: ~2h wall (embarrassingly parallel by n). Structural-signature analysis + tensor write: ~1h. Writeup to `F:\Prometheus\aporia\mathematics\egz_extremal_results.json` + log: ~1h. Sage for residue arithmetic, Python/NumPy for DP. No GPU needed.

## 7. Expected Outcome

Empirical map of EGZ-extremal structure at every n through 16 — first such systematic sweep at this scale on Prometheus. Concrete contribution to the Davenport-constant program via either a counterexample or a hard-fought reinforcement of the two-value conjecture. Structural-signature vectors feed the additive-combinatorics slab of `F:\Prometheus\ergon\tensor.npz`, which already hosts Dirichlet, CM, and gap-scan signatures. Cross-link to **#159 Erdős minimum overlap** and **#160 Cameron-Erdős sum-free sets** via the shared "admits-zero-sum-subsequence" / "admits-sum-free-subset" operator family — these three reports together populate the additive-combinatorics structural region with falsifiable, finite-scale measurements rather than narrative.

**Word count: 748**
