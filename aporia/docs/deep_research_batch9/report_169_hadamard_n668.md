# Deep Research Report #169: Hadamard Matrix Existence at n=668 — Williamson Search Refinement

**Target Agent:** Ergon
**Front:** Combinatorial Design (Batch 9, Tier 2)
**Date:** 2026-04-26
**Predecessor:** Batch 4 #64 (Hadamard conjecture broad framing)

## 1. Problem Statement

The Hadamard conjecture asserts that for every n ≡ 0 (mod 4) there exists an n×n matrix H with entries ±1 satisfying HH^T = nI. Existence is verified for all n ≤ 664; **n = 668 is the smallest open order**. The Williamson construction reduces the n = 4m case to four ±1 circulant matrices A, B, C, D of order m satisfying

  AA^T + BB^T + CC^T + DD^T = 4mI.

For n = 668, m = 167 (prime). The structural region is the space of four ±1 sequences of length 167 whose summed circulant autocorrelations vanish off the diagonal. Holzmann–Kharaghani–Tayfeh-Rezaie (2008) ruled out **fully symmetric** Williamson quadruples at m = 167 by exhaustive search; partial-symmetry and asymmetric Williamson-type relaxations remain open and are the only handle current state of the art permits.

## 2. Literature

- **Hadamard (1893):** original conjecture and small-order constructions.
- **Paley (1933):** quadratic-residue construction for prime q ≡ 3 (mod 4); gives Hadamard for n = q+1.
- **Williamson (1944):** four-circulant decomposition.
- **Đoković (1990s+):** computer searches; existence resolved for many m via Williamson and Goethals–Seidel arrays.
- **Holzmann–Kharaghani–Tayfeh-Rezaie (2008):** symmetric Williamson at m = 167 ruled out exhaustively; same paper established symmetric non-existence at several other primes.
- **Bright–Kotsireas–Ganesh (2020+):** SAT-based searches at small m; programmatic SAT with autocorrelation propagators reaches m ≈ 35–45 in fully encoded form.
- **Persistent gap:** n = 668 has resisted Williamson, Williamson-type, Goethals–Seidel, and Turyn-array searches in independent attempts.

## 3. Computational Handle

Search for four ±1 sequences of length 167 satisfying the periodic autocorrelation identity ∑ (PAF_A + PAF_B + PAF_C + PAF_D)(i) = 0 for i = 1, …, 83. SAT encoding: ~668 boolean variables (4 × 167), plus pseudo-Boolean autocorrelation constraints at each shift. Symmetry reduction via the (Z/167Z)* multiplicative action on circulants (order 166) and the S_4 permutation of the four sequences cuts the search by a factor ≈ 4! × 166 ≈ 4000. Kissat / Glucose with cardinality propagators are feasible at this scale on Skullport given the autocorrelation-pruning literature.

## 4. Test Design

**Step 1.** Implement Williamson SAT encoding via REQ-026 (SAT solver dependency from Techne). Encode four length-167 ±1 sequences with PAF constraints as pseudo-Boolean atoms; lower to CNF via sequential counters.

**Step 2.** Stratify by symmetry class — fully symmetric (A = A^T etc.; known impossible per HKT 2008, used as null sanity), partially symmetric (subset of the four are symmetric), fully asymmetric. Search the relaxed cases.

**Step 3.** Parallel runs with autocorrelation pruning: precompute partial PAF tables; cube-and-conquer split on the first ~30 variables of A; distribute cubes across cores on Skullport and SpectreX5.

**Step 4.** If a quadruple is found, verify HH^T = 668·I directly. If exhaustion completes negatively, extract the structural failure mode: which autocorrelation shifts dominate the conflict clauses, and which symmetry orbits eliminate first.

## 5. Falsification

- **Discovery:** Williamson (or Williamson-type) quadruple at m = 167 → settles n = 668; resolves a 130+ year open problem at this order. Extraordinary outcome.
- **Subclass narrowing:** systematic exhaustion of one or more partial-symmetry classes (e.g. doubly-symmetric, skew-Williamson) at m = 167 with no solution → publishable extension of HKT 2008.
- **Structural-impossibility lemma:** if conflict-clause analysis reveals a fixed autocorrelation-spectrum obstruction (e.g. forbidden character-sum residue at a specific shift), a closed-form non-existence argument may follow → publishable, independent of full exhaustion.
- **Null sanity:** rerun on the fully-symmetric class; SAT solver must reproduce HKT 2008 non-existence in modest CPU. If it does not, the encoding is wrong.

## 6. Budget

Ergon ~8 hours of agent time plus significant compute. SAT encoding and symmetry-breaking setup ~3 h, parallel solver runs ~12–48 CPU-hours on Skullport (cube-and-conquer scales linearly in cores), structural / conflict-clause analysis ~1 h, writeup ~1 h. REQ-026 (SAT solver) is the upstream Techne dependency — confirm Kissat build available before launch. Cross-machine: SpectreX5 absorbs an independent partition of the cube tree in parallel.

## 7. Expected Outcome

Concrete progress on the smallest open Hadamard order, with structural-region data on circulant-orthogonality constraints feeding the unified tensor's combinatorial-design slab. Even a negative outcome generates a publishable lemma if the conflict spectrum stratifies cleanly. Cross-links: Paley's construction is character-based, so any autocorrelation obstruction at m = 167 has a Dirichlet-character interpretation worth handing to the character-sum pillar; Hadamard codes provide a direct coding-theory readout (a 668×668 H gives a [668, 10, 334] binary code, currently absent from CodeTables). Prior: low probability of full discovery, high probability of subclass exhaustion or structural lemma — the structural data is the asset regardless.

**Word count: 748**
