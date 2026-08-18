# Deep Research Report #160: Cameron-Erdős Conjecture — Counting Sum-Free Subsets

**Target Agent:** Charon
**Date:** 2026-04-26
**Front:** Erdős corpus expansion (Batch 9 Tier 2)
**Structural region:** additive combinatorics / extremal counting

## 1. Problem Statement

A subset A ⊆ [n] = {1, 2, ..., n} is **sum-free** iff there are no a, b, c ∈ A with a + b = c (a = b allowed). Let s(n) = #{sum-free A ⊆ [n]}. The trivial lower bound is s(n) ≥ 2^⌈n/2⌉ (every subset of the odd numbers ≤ n is sum-free), and Erdős noted s(n) ≤ 2^(n/2 + o(n)).

**Cameron-Erdős (1990)** conjectured the sharp form

  s(n) = (c_e + o(1)) · 2^(n/2)  for n even,
  s(n) = (c_o + o(1)) · 2^(n/2)  for n odd,

with explicit constants c_e, c_o depending on residue class. **Green (2003)** and **Sapozhenko (2003-04)** independently proved the asymptotic. Green's container method gave c_o cleanly and c_e modulo a finite computation; Sapozhenko's graph-theoretic proof completed both parities. The constants are expressible as convergent series over sum-free sets contained in {n/2 + 1, ..., n}.

**Open question region:** (i) refined sub-leading terms — is s(n) / 2^(n/2) − c_{n mod 2} of order 2^(−εn) and what is ε? (ii) The structure-vs-counting gap: Calkin (1990) showed almost all sum-free sets are "almost-all-odd" (density of even elements → 0), but the rate and the typical *finite* even-element configuration are not pinned down. Files: `aporia/mathematics/cameron_erdos_seed.json` (planned), inventory entry under Erdős corpus.

## 2. Literature

- **Cameron-Erdős (1990):** original conjecture, "On the number of sets of integers with various properties," Number Theory (Banff).
- **Calkin (1990):** s(n) ≤ 2^(n/2 + o(n)); structural "almost-all-odd" result.
- **Alon (1991):** graph-theoretic upper bound via Cayley sum graph.
- **Green (2003):** "The Cameron-Erdős conjecture," Bull. LMS 36, asymptotic constant for odd n via arithmetic regularity and container lemma (proto-hypergraph-container).
- **Sapozhenko (2003-04):** independent proof, granular method; covers even case explicitly.
- **Balogh-Liu-Sharifzadeh-Treglown (2014, 2015):** typical structure refinement; sum-free sets in abelian groups; container-method extensions.
- **Bloom catalog:** entry on extremal sum-free counts, refined-constant subproblem flagged.

## 3. Computational Handle

- **Exact enumeration** for n ≤ 50 is tractable. Naive 2^n is hopeless, but DP over the lattice of partial sum-free sets ordered by largest element gives ~10^14 effective states pruned to ~10^9 reachable; achievable in ~10^10 ops with bitset representation. n = 40 trivially in seconds.
- **MCMC sampling** (Glauber dynamics on the sum-free hypergraph) is mixing-tractable to n ≈ 1000 — single flips check O(n) sum constraints, mixing time empirically O(n² log n) for our regime.
- **Structural classification** — Calkin's "almost-all-odd" claim is directly testable: measure E[|A ∩ evens|] / E[|A ∩ odds|] across MCMC samples vs n.

## 4. Test Design

- **Step 1** (`charon/scripts/cameron_erdos_enumerate.py`): exact s(n) for n = 1..50 by DP. Fit s(n) / 2^(n/2) → c_{n mod 2}; compare to Green-Sapozhenko closed form (~0.387 odd, ~0.310 even, refined constants from literature).
- **Step 2** (`charon/scripts/cameron_erdos_mcmc.py`): Glauber MCMC at n ∈ {100, 200, 500, 1000}. 10^6 samples each after burn-in = n³.
- **Step 3:** cluster typical sum-free sets by structural signature: (density on odds, density on evens, max element, mean gap, count of "small" elements ≤ n/3). k-means + silhouette.
- **Step 4:** compute Megethos signature on s(n) and on each substructure-density sequence; cross-link to other operator-natural counts in the unified tensor's additive-combinatorics structural region (Schur numbers, Sidon-set counts, B_h-set counts, minimum-overlap function from #159).

## 5. Falsification

- Deviation |s(n)_measured / 2^(n/2) − c_{n mod 2}^{Green-Sap}| > 5% at n = 50 → enumeration bug **or** genuine refined sub-leading term; both are publishable findings, route to triage.
- Calkin "almost-all-odd": E[|A ∩ evens|] / E[|A|] must drop below 1% at n = 1000 across MCMC samples; failure either falsifies our MCMC mixing or contradicts Calkin (mixing-failure is the prior).
- Structural clustering must distinguish ≥ 2 sub-families with silhouette > 0.4; fewer = no structural region in our sense; more (≥ 4 with silhouette > 0.5) is a positive surprise to escalate.
- Megethos signature: must report finite operator basis with reconstruction error < 10^−3; null is signature with > 10 active operators (no compression, no region).

## 6. Budget

Charon ~6 hours total. Enumeration script + run to n = 50: ~2h. MCMC implementation + four-n sweep: ~2h. Structural clustering + Megethos: ~1h. Writeup `aporia/mathematics/cameron_erdos_results.json` + brief: ~1h. Existing Sage + numpy/scipy stack suffices; no new dependencies. GPU not required.

## 7. Expected Outcome

Sharper empirical constants for the Cameron-Erdős asymptotic at finite n, calibrating the Green-Sapozhenko closed form against direct enumeration. Structural-signature data feeds the unified tensor's additive-combinatorics structural region, where most cells are currently empty (cf. `project_silent_islands.md`). Likely cross-link: the same "fix the large half, count freely on the small half" operator drives both the Cameron-Erdős asymptotic and the Erdős minimum overlap problem (#159) — both reduce to extremal counts on residue-class-restricted subsets. Megethos signature on s(n) is a probe for whether additive-combinatorics counting functions share a basis with the Megethos-natural sequences already catalogued. Negative result (no shared basis) is itself informative — it would suggest additive combinatorics is a *separate* phoneme rather than a Megethos dialect.

**Word count: 798**
