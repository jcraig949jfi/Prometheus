# Gemini Deep Research Prompts — 2026-04-28

**Purpose:** Paste-ready prompts for Gemini Deep Research (Plus-plan ~20/day token bucket). Each fills a substrate-cold or literature-recency-sensitive slot from Batch 10. Order is priority — fire top to bottom, expect 10-15 min per report.

**Why these, not random Batch 11 picks:** Claude subagent drafts (the 17 already in `aporia/docs/deep_research_batch10/`) are weakest at (a) very-recent arXiv (last ~3 months), (b) operator-algebra and math-physics literature where the canonical references are obscure, and (c) deferred slots that were never drafted at all. Gemini DR's web grounding is the right tool for exactly these cases.

**Doctrine for the user when reviewing returned reports:**
- Ground-truth check: does Gemini cite recent (≤2024) papers we can verify exist?
- Bridge-narrative check: if Gemini frames the problem as "connecting field X to field Y," that's exhaust talk — what's the substrate-relevant operator?
- Calibration-anchor check: does the report give us labeled (true positive) cases we could ingest into `aporia/calibration/battery_calibration.jsonl`?

---

## Wave A — Deferred from Batch 10 (highest priority; never drafted)

### Prompt 1 — #189 Effros-Marechal completeness in operator spaces

```
Write a deep research report on the open structural-completeness question for the Effros-Marechal class of operator spaces. Specifically:

1. State the precise open question: across the lattice of operator spaces under completely-bounded isomorphism, which sub-region is "Effros-Marechal complete," and what is the current best partial classification (Pisier 2003 onward, recent extensions through 2024)?

2. Survey the literature, citing concrete papers with DOIs or arXiv IDs:
   - Effros-Ruan and Effros-Marechal foundational work
   - Pisier's "Operator Spaces" framework
   - Recent (2022-2024) progress on cb-isomorphism invariants
   - Any computational catalogues of explicit operator spaces

3. Identify the empirical handle: what discrete invariants (Haagerup tensor norm, exact constant, OS_k constants, factorization through specific Hilbert spaces) can be computed for explicit examples like c_0, ℓ_p, S_p, OH, MIN, MAX, R+C?

4. Propose 3-5 specific computational tests that would densify calibration anchors in this region (current substrate coverage: zero).

5. Avoid bridge-narrative framing — discuss "operator behavior in the structural region of completely-bounded morphism space," not "bridges between functional analysis and X."

Target: 800-1500 words. Prefer concrete invariants and citations over speculation.
```

### Prompt 2 — #191 Bose-Einstein condensation rigorous (math-only framing)

```
Write a deep research report on the open mathematical question of rigorous Bose-Einstein condensation for interacting Bose gases — strictly the MATHEMATICAL/measure-theoretic problem, not the physics.

CONSTRAINT: Treat this as a problem about measure-theoretic limits of N-particle ground states on the cube [0,L]^3 as N, L → ∞ at fixed density. DO NOT discuss physical interpretation, experimental observation, photon condensates, or thermodynamic phenomenology. Extract the math; leave the physics as docstring.

1. State precisely the open mathematical question: existence of off-diagonal long-range order (ODLRO) for the one-particle reduced density matrix γ^(1) of the N-particle ground state of the Bose-Hubbard or hard-sphere Bose gas in the thermodynamic limit, in dimension d=3.

2. Survey the literature with citations:
   - Lieb-Seiringer-Yngvason (2002+) — ground state energy via Gross-Pitaevskii
   - Lieb-Seiringer (2006) — ODLRO for the trapped case
   - Robinson-Friedrich-Yau (2018+) — recent progress on the homogeneous case
   - Boccato-Brennecke-Cenatiempo-Schlein (2020+) — sharp Bogoliubov bounds
   - Any 2023-2024 progress (especially the homogeneous gas)

3. Identify computational handles: what discrete approximations (lattice Bose-Hubbard at small system size, exact diagonalization at N≤14, DMRG bond-dim spectra) produce labeled true-positive ODLRO cases that could anchor calibration?

4. Propose 3-5 empirical tests on small lattice systems where ODLRO can be exhaustively verified.

5. Use "structural region of N-particle ground state space" framing. Forbid bridge-narrative.

Target: 800-1500 words.
```

### Prompt 3 — #193 Razborov-Smolensky monotone circuit lower bounds (empirical)

```
Write a deep research report on the open empirical/structural question of how Razborov-Smolensky monotone circuit lower bound techniques behave on explicit Boolean function families at small scale.

1. State the precise question: across explicit Boolean functions (clique-detect, perfect-matching, bipartite-perfect-matching, GEN, st-CONN, parity, threshold, MAJ, IP_n inner product mod 2), what is the empirical landscape of (monotone circuit size, AC^0[mod p] size, approximate-degree, communication complexity) at n ≤ 12, and how cleanly do the Razborov-Smolensky lower bounds saturate?

2. Survey literature with citations:
   - Razborov 1985 (CLIQUE monotone lower bound)
   - Smolensky 1987 (mod-p polynomial method)
   - Tardos 1988 (matching is exponentially harder than CLIQUE in monotone)
   - Recent (2022-2024) work on lifting theorems, polynomial-method extensions, and barriers
   - Limaye-Srinivasan-Tavenas 2022 superpoly lower bound

3. Identify empirical handles: BDD packages, SAT-based lower bound certification, explicit symmetric polynomial families.

4. Propose 3-5 tests: compute polynomial approximation degree for n ≤ 14 inputs across the function families above, stratify, identify where Razborov-Smolensky bounds are tight vs slack.

5. Forbid bridge-narrative; use "operator behavior in the AC^0[mod p] structural region of Boolean function space" framing.

Target: 800-1500 words.
```

---

## Wave B — Re-runs of substrate-cold Tier 3 picks (literature-recency boost)

### Prompt 4 — #180 Beauville-Voisin K3 Chow ring (recency-boosted)

```
Write a deep research report on recent (2022-2024) progress on Beauville-Voisin's distinguished zero-cycle class on K3 surfaces and Beauville's splitting conjecture for hyperkähler varieties.

Focus areas:
1. State the open question precisely: which hyperkähler deformation types admit the conjectured multiplicative bigrading on CH^*(X)_Q?
2. Specifically catalog 2022-2024 progress: Pavic-Shen-Yin, Vial, Voisin, Negut, and any new cases beyond Hilbert schemes of K3, generalized Kummer, OG6, OG10.
3. Catalog computational data: explicit Picard lattices in LMFDB or Brandhorst-Hofmann tables for K3s with ρ ≥ 8; Mukai-vector orbits.
4. Propose 3-5 empirical tests that would build calibration anchors in this currently-zero-coverage substrate region.

Forbid bridge-narrative; frame as "operator behavior in the K3-Picard-rank-≥8 structural region of motivic-cohomology space."

Target: 800-1500 words.
```

### Prompt 5 — #188 Property Γ in II_1 factors (recency-boosted)

```
Write a deep research report on the current empirical landscape of Property Γ in II_1 factors, focusing on (a) which non-amenable group factors have been recently classified (Γ vs not-Γ) and (b) what computable invariants stratify them.

1. Survey literature with citations:
   - Murray-von Neumann 1943
   - Connes 1976 (uniqueness of injective II_1)
   - Voiculescu free entropy dimension δ
   - Popa deformation/rigidity 2006-2024
   - Ozawa solid factors 2004
   - Recent (2022-2024) work on Property Γ for HNN extensions, surface group factors, lattices in higher-rank Lie groups, wreath products

2. Catalog ~30 explicit groups with their Property Γ status from the literature.

3. Identify computable invariants: free entropy dimension δ (where lower bounds exist), L²-Betti numbers β_1^(2)(G), word growth, amenability bit, cost.

4. Propose 3-5 empirical tests: cluster groups in (δ, β_1^(2), growth) space, check if cluster purity beats the amenability baseline, identify groups where Γ-status is computationally undetermined.

Forbid bridge-narrative.

Target: 800-1500 words.
```

### Prompt 6 — #190 Yang-Mills mass gap (lattice-only, math framing)

```
Write a deep research report on the lattice gauge theory transfer-matrix spectral gap, treating it strictly as a question about eigenvalue ratios of a finite real sparse self-adjoint operator on group-valued link configurations.

CONSTRAINT: Do NOT discuss the Clay continuum problem, do NOT speculate about OS axioms, do NOT use words like "confinement" or "mass" except as docstring. Extract the math: transfer-matrix construction, eigenvalue gap Δ(β, L, G), area-law slope σ(β), how these scale with lattice size L and inverse coupling β.

1. State the precise lattice question: for SU(2) and SU(3) on 4^4 to 16^4 periodic lattices, with Wilson action at coupling β, what is the spectral gap Δ as a function of (G, L, β)?

2. Survey literature with citations: Wilson 1974, Kogut-Susskind 1975, Lüscher 1982-84 (rigorous transfer-matrix construction), Lucini-Teper-Wenger 2004 (glueball spectra), recent (2022-2024) high-precision lattice computations including FLAG reviews.

3. Identify the calibration anchors: SU(3) glueball/torelon ratios at standard β values from Lucini-Teper.

4. Propose 3-5 tests on small lattices.

Forbid bridge-narrative; forbid physical interpretation in body text. Math-only.

Target: 800-1500 words.
```

### Prompt 7 — #192 PIT derandomization barriers (recency-boosted)

```
Write a deep research report on the current state of polynomial identity testing (PIT) derandomization for restricted arithmetic circuit classes, focusing on (a) the Limaye-Srinivasan-Tavenas 2022 superpolynomial lower bound for constant-depth circuits and (b) any 2023-2024 follow-up progress on PIT for restricted classes.

1. State the precise question: what is the current frontier for deterministic poly-time PIT on (a) depth-3 SPS bounded top fan-in, (b) depth-4 SPSP, (c) read-once oblivious ABPs (ROABPs), (d) multilinear circuits, and how does Kabanets-Impagliazzo 2003 still gate the general case?

2. Survey literature with citations: Schwartz-Zippel 1979-80, Kabanets-Impagliazzo 2003, Agrawal-Vinay 2008, Saxena-Seshadhri 2013, Forbes-Shpilka 2018+, Bhargava-Saraf-Volkovich 2018+, Limaye-Srinivasan-Tavenas 2022, Andrews-Forbes 2022+.

3. Identify the computational handle: explicit polynomial families (Vandermonde, det, perm, IMM, NW polynomials, elementary symmetric) and their partial-derivative / shifted-partial complexity measures.

4. Propose 3-5 empirical tests at small n ≤ 12 that build calibration anchors in algebraic complexity (currently zero substrate coverage).

Forbid bridge-narrative.

Target: 800-1500 words.
```

---

## Workflow

1. Paste prompt into Gemini Deep Research one at a time.
2. When it returns (~10-15 min), save to `aporia/docs/deep_research_batch10/gemini_dr_{NN}_{slug}.md` (use `gemini_dr_` prefix to distinguish from Claude-subagent drafts).
3. Compare side-by-side with the Claude draft (where one exists). Flag where Gemini caught literature the Claude draft missed; flag where Claude was tighter on the substrate framing. The diff is calibration data on both pipelines.
4. If a Gemini report contains a NEW open empirical question or a NEW labeled true-positive case, ingest into `aporia/calibration/battery_calibration.jsonl`.

---

*Aporia, 2026-04-28. Pairs with `aporia/docs/deep_research_batch10/`. Recurring agent `aporia-batch-deep-research-daily` will not duplicate Gemini DR work — it stays inside Claude subagent budget.*
