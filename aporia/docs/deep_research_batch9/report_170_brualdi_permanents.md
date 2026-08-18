# Deep Research Report #170: Brualdi-Style Extremals for Permanents of (0,1)-Matrices

**Target Agent:** Ergon
**Front:** Combinatorics (Batch 9, Tier 2)
**Date:** 2026-04-26
**Doctrine:** feedback_tensor_first, feedback_domains_are_docstrings, feedback_assume_wrong

## 1. Problem Statement

Let A be an n × n (0,1)-matrix with exactly k ones in each row and each column (a k-regular bipartite biadjacency matrix). The **Schrijver-Valiant lower bound**, proved by Schrijver (1998), states

  perm(A) ≥ ((k-1)^(k-1) / k^(k-2))^n = (k!/k^k)^n · k^n  (asymptotic form),

with equality asymptotically achieved by random k-regular bipartite graphs. The **open question** is the exact characterization of equality and near-equality cases at finite n: for k ≥ 3, the family of (0,1)-matrices saturating the Schrijver bound (or coming within an explicit gap) is not classified. For k = 2 the equality structure reduces to disjoint-cycle covers and is essentially understood; for k ≥ 3 only sporadic constructions (cyclic shift matrices, incidence matrices of small designs) are known to be near-extremal, and no structural theorem rules out an unrecognised family. The Brualdi-style problem is: identify, at LMFDB-tractable n, the full set of equality / near-equality matrices and determine whether they form a single structural region or several.

## 2. Literature

- **Brualdi (1966), "Combinatorial Matrix Theory"** — foundational monograph defining the extremal program for permanents on (0,1)-matrices with prescribed row/column sums.
- **Van der Waerden (1926); Egorychev (1981); Falikman (1981)** — perm(A) ≥ n!/n^n on doubly stochastic matrices, with equality iff A = J_n/n.
- **Brègman (1973)** — sharp upper bound perm(A) ≤ ∏_i (r_i!)^(1/r_i) with explicit equality structure (block-diagonal of all-ones).
- **Schrijver (1998)** — lower bound for k-regular bipartite (0,1)-matrices, refining Falikman.
- **Linial-Samorodnitsky-Wigderson (2000)** — deterministic e^n approximation via matrix scaling; supplies the algorithmic frame.
- **Csikvári, Lin, Gurvits (2014–2022)** — recent stable-polynomial / Lorentzian sharpenings of the Schrijver bound and partial extremal characterisations at small k.
- **Brualdi-Newman (1965)** — companion conjecture on permanents of tournament matrices, providing a parallel testbed.

## 3. Computational Handle

Exact permanent computation is feasible at the scale this problem requires. **Ryser's formula** runs in O(n · 2^n) and handles dense (0,1)-matrices to n ≤ 30 on a single core; **Glynn's formula** is comparable. For k-regular bipartite graphs the matrix is sparse with kn ones, and structured-permanent specialisations (Cifuentes-Parrilo, Huber-Law) push reachable n to ≈ 40 for k ≤ 5. Equality-case enumeration is limited not by perm() cost but by the number of k-regular bipartite graphs on n + n vertices: nauty/bliss enumerate these to n ≈ 14 (k=3) and n ≈ 20 (k=2). Sympy + NumPy + a small C extension for Ryser are sufficient; no GPU required.

## 4. Test Design

**Step 1.** Enumerate all k-regular bipartite graphs on n + n vertices (nauty `genbg`) for (n, k) ∈ {(10,2),(10,3),(12,2),(12,3),(15,2),(15,3),(15,4)}. Compute perm(A) by Ryser. Record the empirical minimum and the multiset of minimisers.

**Step 2.** Structural classification of minimisers: block decomposition, automorphism group order (via nauty), girth of the underlying bipartite graph, eigenvalue spectrum. Tag each by isomorphism class.

**Step 3.** Extension search: for each minimiser at (n, k), attempt graph-theoretic lifts (graph products, vertex doubling, voltage assignments) to (2n, k) and (n, k+1). Test whether the lifted matrix remains an equality / near-equality case. Detection of a stable family across k is the strongest positive outcome.

**Step 4.** Megethos signature: encode (log perm, n, k, |Aut|, girth, spectral gap) as a six-vector per matrix and run the standard tensor-first dissection. Cross-link to combinatorial-design region (#168 MOLS, #169 Hadamard); shared regular-bipartite substrate predicts overlap if any.

## 5. Falsification

Quantitative thresholds for publishable outcomes:

- **Equality case outside conjectured family** at n ≤ 15, k ≤ 4 → direct counterexample to the implicit Schrijver-tight characterisation; publishable.
- **Closed characterisation theorem** for equality cases at k = 3 (e.g. "all minimisers are cyclic-shift composites") with proof at n ≤ 15 and stable extension to n = 18 → publishable structural result.
- **Structural-impossibility lemma**: bipartite graphs with girth < g cannot be Schrijver-tight for k ≥ k₀ → narrows the equality family, publishable as a lemma.
- **Negative outcome**: minimiser set is structurally amorphous (no |Aut| concentration, no spectral pattern) → kill the Brualdi-tight structural hypothesis at this scale; record as a calibrated kill.

Assume-wrong default: the cyclic-shift family is **not** the answer until enumeration confirms it.

## 6. Budget

Ergon, ~6 hours total. Ryser enumeration over the (n, k) grid (~2 h, parallelisable across cores). Structural classification with nauty + spectral computation (~2 h). Megethos six-vector dissection and cross-link to #168/#169 (~1 h). Writeup with extremal table and one figure (~1 h). NumPy + sympy + nauty CLI; no external services.

## 7. Expected Outcome

Empirical map of permanent extremals across (n, k) ∈ [10,15] × [2,4]: complete minimiser list, automorphism-group histogram, spectral fingerprint. Primary deliverable is the **structural region** of doubly-regular bipartite graphs that saturate Schrijver — a region currently described only by sporadic examples in the literature. Secondary deliverable: a Megethos signature linking permanent extremals to the combinatorial-design extremals of #168 (MOLS) and #169 (Hadamard); shared regular-bipartite substrate makes cross-linkage the natural prediction, and absence of cross-linkage is itself a calibrated negative. Calibration role: this brief sits in the well-understood end of the extremal-counting axis, providing ground truth before Ergon scales to the harder open conjectures of Brègman-tight upper-extremals and Brualdi-Newman tournament permanents.

**Word count: 778**
