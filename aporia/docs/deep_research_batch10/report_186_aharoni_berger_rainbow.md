# Deep Research Report #186: Aharoni-Berger Rainbow Matching Conjecture — Calibrated Success-Rate Map

**Target Agent:** Ergon
**Date:** 2026-04-28
**Front:** Extremal graph / hypergraph combinatorics (Batch 10)
**Doctrine:** `feedback_tensor_first`; `feedback_calibration_anchors_in_depth`; PATTERN_BASE_RATE_NEGLECT; PATTERN_VRAM_TRUNCATION_ARTIFACT.

## 1. Problem Statement

Aharoni-Berger (2009) conjectured: given n bipartite graphs G_1, ..., G_n on the common vertex set [n] ⊔ [n], each carrying a perfect matching M_i, there exists a **rainbow perfect matching** — a perfect matching of [n] ⊔ [n] using at most one edge from each M_i. The conjecture is *distinct* from (a) the Latin transversal problem (Ryser-Brualdi-Stein: every n × n Latin square has a transversal of size n − 1, conjecturally n when n is odd), which is the special case where each M_i is the i-th row of a fixed Latin square and edges are entries; and (b) the rainbow Hamilton cycle conjectures of Erdős-Spencer / Bal-Frieze, which concern Hamiltonicity rather than matching. Aharoni-Berger sits between these: more general than Latin transversals (the M_i need not be rows of a single Latin square), more constrained than rainbow Hamilton cycles. The full conjecture for finite n remains open; only asymptotic versions are settled.

## 2. Literature

- **Aharoni-Berger (2009, *Electron. J. Combin.*):** original conjecture, motivated by Ryser-type Latin transversal problems and matroid intersection.
- **Pokrovskiy (2018, *J. Combin. Theory B*):** asymptotic version — rainbow matching of size n − o(n) always exists; o(n) term not made fully explicit.
- **Kim-Kühn-Lichev-Lo-Methuku (2024+, arXiv):** rainbow matching of size (1 − ε)n with explicit ε(n) decreasing in n; uses absorbers + nibble.
- **Joos-Kim (2020, *Bull. London Math. Soc.*):** rainbow matchings in graphs with bounded edge-multiplicity; relevant for Latin-square-derived families.
- **Aharoni-Berger-Chudnovsky-Howard-Seymour (2017):** matroid extension and partial bipartite-graph results at small n.
- **Erdős-Ginzburg-Ziv (1961, classical):** zero-sum versions of rainbow problems; calibration analogue for "edge from each color class" intuition.
- **Drisko (1998):** every 2n − 1 perfect matchings on K_{n,n} admit a rainbow matching — the bipartite tight constant for the *2n − 1* version, predecessor to Aharoni-Berger's *n*.
- **Keevash-Pokrovskiy-Sudakov-Yepremyan (2022):** rainbow structures in random and quasi-random hypergraphs.

## 3. Computational Handle / Corpus

A test instance is an n-tuple (G_1, ..., G_n) of bipartite graphs on [n] ⊔ [n], each with a designated perfect matching M_i. Three corpus families: (a) **Latin-square-derived** — pick a random Latin square L of order n via Jacobson-Matthews MCMC, set M_i = i-th row of L (each row is a permutation, hence a perfect matching of K_{n,n}); (b) **random k-regular bipartite** via networkx.bipartite.random_graph with k ∈ {3, 5, ⌊n/2⌋, n}, then extract any perfect matching for M_i via Hopcroft-Karp; (c) **structured / near-extremal** — KnotInfo-style families where each G_i is a small perturbation of a fixed canonical matching (perfect-matching pencils, near-Drisko configurations with 2n − 2 instead of 2n − 1 matchings). Decision problem: *does (G_1, ..., G_n, M_1, ..., M_n) admit a rainbow perfect matching?* Encodable as SAT with ~n³ variables (one Boolean per (i, edge_in_M_i, position) triple after pruning), ~n^4 clauses; tractable on Skullport for n ≤ 18 (PATTERN_VRAM_TRUNCATION_ARTIFACT — declare hard cap n = 18; beyond this Kissat memory exceeds 64 GB on dense Latin instances).

## 4. Test Design

**Step 1.** Generate corpus: for each n ∈ [3, 18] (16 values), produce 10 Latin-square instances + 10 random-k-regular instances (k ∈ {3, 5, ⌊n/2⌋, n}, 2-3 per k per n) + 10 near-extremal structured instances. Total: 16 × 30 = **480 instances**, plus a deterministic anchor set of 20 small-n exhaustive cases (n ∈ {3, 4, 5}, all isomorphism classes of (G_i, M_i) tuples) = **500 instance families**, the upfront denominator.

**Step 2.** For each instance, SAT-encode the rainbow-matching decision via TOOL_SAT_SOLVER (REQ-026, just shipped, Kissat backend). Variable x_{i,e} = 1 if edge e from M_i is selected; constraints: at most one e per i, exactly one selected edge incident to each vertex of [n] ⊔ [n]. Record SAT/UNSAT + solve time.

**Step 3.** Stratify by (a) graph density (k = 3, 5, ⌊n/2⌋, n), (b) family (Latin / random / near-extremal), (c) n. Per-stratum success rate = SAT count / n_instances in stratum (denominators: Latin 160, random 160, near-extremal 160, anchor 20 — explicitly declared, PATTERN_BASE_RATE_NEGLECT).

**Step 4.** Calibration anchor check: for n ∈ {3, 4, 5} the conjecture is verified by exhaustion (Aharoni-Berger original + Drisko); these instances **must** return SAT. Any UNSAT in the anchor set kills the pipeline, not the math.

**Step 5.** Cross-reference: compare empirical success rate at each n against Pokrovskiy (n − o(n) translated to expected SAT-density curve) and Kim et al. (1 − ε)n. If observed rate diverges from Pokrovskiy projection by ≥10% in any stratum, flag for second pass.

## 5. Falsification

- **Pipeline kill:** any UNSAT among the 20 calibration-anchor instances (n ≤ 5) → SAT encoding bug; Aharoni-Berger is verified here.
- **Substrate confirmation:** ≥95% SAT across the 480 main instances → empirical Aharoni-Berger holds in tested range; calibration anchor accepted.
- **Structural separation:** Latin-derived stratum success rate diverges from random-k-regular stratum by ≥15% at any fixed n → publishable structural finding (suggests Latin and random sit in different hardness classes for Aharoni-Berger, refining Drisko's bipartite picture).
- **Counterexample candidate:** any UNSAT in the near-extremal stratum for n ≥ 6 → re-verify with independent solver (Glucose); if confirmed and instance is genuinely valid, this is a candidate counterexample to Aharoni-Berger and routes immediately to Charon for kill-or-confirm.
- **Null:** permute the M_i labels uniformly at random; SAT/UNSAT outcome must be invariant (each M_i still contributes one edge regardless of label).

## 6. Budget

Ergon ~6 hours. Corpus generation 1h; SAT encoding + parallelized solve on Skullport (500 instances, n ≤ 18, median estimated <20s, tail to ~5min on near-extremal n=18 with Kissat 8-way) 2.5h; stratified analysis + calibration-anchor verification 1h; cross-reference against Pokrovskiy / Kim curves 0.5h; writeup + tensor ingestion 1h.

## 7. Expected Outcome

Per `feedback_calibration_anchors_in_depth`, each confirmed SAT in the n ∈ [3, 18] range becomes a **calibration anchor** in the extremal-rainbow region of the substrate's combinatorics tensor — a high-confidence positive that anchors structural-class measurements where the asymptotic theorems of Pokrovskiy and Kim et al. provide no finite-n guarantee. Prior expectation: ≥95% SAT (conjecture believed true; Drisko's 2n − 1 bound is loose). Primary value is the **stratified success-rate surface**: density × family × n. If Latin-derived and random k-regular strata show the predicted ≥15% separation, the substrate gains its first quantitative hardness gradient between Latin-transversal-flavored and generic-bipartite-flavored rainbow problems — directly feeding `feedback_tensor_first`. Secondary outcome: if a near-extremal instance returns UNSAT and survives independent re-verification, it is a candidate Aharoni-Berger counterexample and routes to Charon. Either way, the artifact is durable and the kills (if any) are the most valuable output.

Word count: 770
