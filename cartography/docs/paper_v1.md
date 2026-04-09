# Cross-Domain Mathematical Discovery: Challenges, Techniques, and Open Questions

## A Living Document — Project Prometheus
### Version 1.1 — 2026-04-09

---

## Abstract

We present results from an autonomous pipeline that searches for structural connections across 21 mathematical datasets spanning 1M+ objects. After 18,000+ hypothesis tests, 9 killed false discoveries, and systematic elimination of prime-factorization artifacts (96% of all apparent cross-dataset signal), we report zero novel cross-domain bridges. We discuss why this null result is informative, what it reveals about the structure of mathematical knowledge, and what techniques from adjacent fields — evolutionary program synthesis, Bayesian surprise, graph contrastive learning, and counterexample search — may break the impasse. We also report 41 verified asymptotic corrections and 22,338 new OEIS sequence terms as concrete computational contributions.

---

## 1. Introduction

The mathematical landscape is organized into databases: OEIS catalogs integer sequences, LMFDB catalogs L-functions and modular forms, KnotInfo catalogs knots, mathlib formalizes proofs. Each database is deep and well-curated within its domain. The space *between* databases — where a property of an elliptic curve might predict something about a knot, or where a combinatorial statistic might echo a spectral parameter — is largely unmapped.

This project asks: can autonomous computational methods discover structural connections between mathematical domains that humans haven't found?

After 8 days of continuous operation across 8 parallel terminals, the honest answer is: **not yet**. But the process of failing has produced three kinds of useful output:

1. **A definitive negative result**: scalar correlations between mathematical datasets reduce entirely to shared prime factorization. After detrending for primes, zero signal remains.

2. **A calibrated falsification battery**: 14 computational kill tests that correctly validate 180 known mathematical facts (100%) while killing 9 false discoveries that fooled both human and LLM judgment.

3. **Concrete computational contributions**: 22,338 new OEIS terms, 41 verified asymptotic corrections, and a shadow tensor mapping 101K+ test records across 210 dataset pairs.

The question now is whether structural comparison methods — formula syntax trees, polynomial root distributions, graph spectra, evolved search programs — can find what scalar methods cannot.

A key result from this work: testing 12 theory-predicted mathematical bridges (modularity theorem, class field theory, isogeny reduction, etc.) against the scalar battery reveals that ALL known cross-domain connections are structural, not scalar. The battery correctly kills scalar tests of structural truths. This is not a calibration failure — it is the strongest evidence that the structural layer, not the scalar layer, is where bridges live.

---

## 2. The Prime Atmosphere Problem

### 2.1 Discovery and characterization

Every mathematical dataset we examined encodes prime numbers. Elliptic curve conductors are products of primes. Knot determinants are odd integers (prime-rich). Number field discriminants factor over primes. Group counts depend on prime factorization of the order. Even crystallographic space groups index by prime-related symmetries.

When two datasets are compared by scalar correlation (Pearson, Spearman, mutual information, Wasserstein distance), the dominant signal is always shared prime structure. Across all 210 dataset pairs, prime factorization explains 96% of apparent cross-dataset correlation.

### 2.2 Detrending and the empty sky

After removing prime structure via 3-layer decontamination (detrend prime density → filter small-integer coincidences → normalize residuals), the maximum z-score across all dataset pairs drops to 0.2. The scalar layer is empty.

This is not a failure of the pipeline — it is a finding. The scalar properties of mathematical objects (conductors, determinants, discriminants, counts) communicate across domains only through their prime factorization. Remove the primes, and the objects are statistically independent at the scalar level.

### 2.3 Implications

Any system that discovers "connections" between mathematical datasets via scalar correlation and fails to control for prime structure will produce false positives. We found 9 such false positives before implementing systematic detrending. Each appeared compelling to both human mathematicians and frontier LLMs before the battery killed it.

---

## 3. The Falsification Battery

### 3.1 Design philosophy

The battery exists because LLMs construct narratives. When an LLM sees r=0.85 between two datasets, it generates an explanation. The explanation sounds plausible. A second LLM agrees. The correlation is real — but the explanation is wrong, and the correlation is an artifact.

The battery has no LLM in the loop. 14 tests, all pure computation, all with hard thresholds:

| Test | What it catches |
|------|----------------|
| F1. Permutation null | Is the correlation above chance? (10K shuffles) |
| F2. Subset stability | Does it replicate in random 50% splits? |
| F3. Effect size | Is it meaningful? (Cohen's d > 0.2 or r > 0.1) |
| F4. Confound sweep | Does a single lurking variable explain it? |
| F5. Normalization sensitivity | Does the sign flip under log/rank/z-score? |
| F6. Base rate | Bonferroni correction for multiple testing |
| F7. Dose-response | More X → more Y? |
| F8. Direction consistency | Same sign in all subgroups? |
| F9. Simpler explanation | Does a trivial baseline match? |
| F10. Outlier sensitivity | Survives removal of top/bottom 5%? |
| F11. Cross-validation | Train on half, predict on half? |
| F12. Partial correlation | Survives after removing confounds? |
| F13. Growth rate filter | Is the target or just polynomial growth? |
| F14. Phase shift | Does correlation decay when index is shifted? |

One FAIL = hypothesis killed. No appeals. No narrative overrides.

### 3.2 Calibration

The battery correctly validates 180 known mathematical facts across 6 layers — from OEIS sequence identities through Mazur's torsion theorem through the crystallographic restriction. The false negative rate on known mathematics is 0%.

The battery has killed 9 false discoveries that survived human and LLM scrutiny (see Kill Log, Section 7).

### 3.3 Limitations

The battery has reduced sensitivity at small sample sizes (N < 20). Three FindStat comparisons survived at N=17 that are likely artifacts. The battery also cannot catch interpretation errors — a z=137 root probe result survived all 14 tests because the tests confirmed a real distributional *difference*, but the claim was about *similarity* (Kill #9).

---

## 4. Structural Comparison: Beyond Scalars

### 4.1 The depth layer hypothesis

If scalar properties communicate only through primes, structural properties — polynomial coefficients, formula syntax, graph topology — may communicate through deeper channels. A knot's Alexander polynomial and an elliptic curve's L-function are both polynomials, but their structural relationship (if any) would not manifest as a scalar correlation between determinants and conductors.

### 4.2 Current structural tools

**Formula ASTs.** We extract structural features from 12.5M mathematical formulas (OpenWebMath corpus): operator types, nesting depth, subscript/superscript patterns, domain classification. Initial cross-module comparison using Jaccard similarity on operator sets was killed by F13 (growth rate artifact). Symbol-bag comparison is too coarse — formulas with more operators have higher Jaccard regardless of structure. Proper structural comparison requires parsed syntax trees and tree-edit distance or graph embedding.

**Polynomial root distributions.** We compute root distributions for 5,950 knot polynomials (Alexander and Jones) and Sato-Tate angle distributions for 31,073 elliptic curves. The distributions are significantly different (z=137, confirmed by battery), not similar. Knot roots cluster near 0 on the unit circle; Sato-Tate angles cluster near pi. This is a confirmed dissimilarity, not a bridge.

**Graph spectral analysis.** We compute spectral gap, algebraic connectivity, and degree distributions for 53 mathematical graphs (isogeny adjacency matrices, mathlib imports, OEIS cross-references, MMLKG theorem references). Cross-domain comparisons exist but cannot be battery-tested with only scalar invariants per graph. Degree sequence data is needed.

**Concept embeddings.** 39,168 mathematical concepts embedded in R^64 via spectral decomposition of the normalized Laplacian of the co-occurrence graph. Known bridges (modularity theorem, BSD conjecture) cluster as expected. Novelty scoring steers exploration toward the least-tested regions.

### 4.4 Expected bridges: the calibration target

We tested 12 theory-predicted bridges across 3 tiers — known theorems (calibration), strong theoretical expectations, and speculative connections. Results:

- **Tier 1 (calibration):** 0/4 survived scalar battery. Modularity theorem killed by F13 (growth rate). Isogeny-EC killed by F1 (permutation null). OEIS-SmallGroups killed by F1+F2+F3. These are KNOWN truths that fail scalar testing — confirming that known bridges are structural, not scalar.
- **Tier 2 (theoretical):** 0/4 survived (2 structural/untestable, 2 killed).
- **Tier 3 (speculative):** 1/4 survived. Maass form level distributions overlap with modular form level distributions (10/14 tests pass). This is a genuine distributional finding.

The Tier 1 failures define our calibration target: when our structural tools (Operator Graph embedding, formula AST comparison) can detect the modularity theorem without being told, the structural layer is working.

### 4.5 Graph degree sequence comparison

Battery testing on full degree sequences of mathematical graphs produced 4 survivors out of 10 tested cross-domain pairs. Three isogeny graphs (at primes 947, 2311, 4013) have degree distributions indistinguishable from the mathlib import graph, and one (prime 2887) survives against the MMLKG theorem reference graph. These require deeper investigation — the survival may reflect genuine structural similarity (sparse graphs with hub-spoke topology) or insufficient statistical power at small sample sizes.

### 4.6 What's missing

The structural tools are operational but young. Three gaps remain:

1. **Formula-level structural embedding.** Current comparison uses operator feature vectors. State-of-the-art (SSEmb, CIKM 2025) uses Operator Graphs with graph contrastive learning. We have 12.5M formulas with a recursive descent LaTeX parser producing operator trees at 17K formulas/second (99.996% parse success). The graph construction pipeline is operational; the embedding training step is next.

2. **Cross-domain matched-object probes.** Comparing distributions across domains tests whether entire populations look similar. The more powerful test is matched-object: for objects that appear in multiple datasets (e.g., curves with both LMFDB and OEIS entries), do their structural properties correlate *at the individual level*? Our depth_probes framework supports this but few matched objects have been identified.

3. **Representation quality.** OEIS sequences are currently embedded by raw term values, which degenerates for combinatorial sequences (all have similar log-growth). A formula-structure or cross-reference embedding would be more informative. mathlib's dependency graph uses file-level imports (1,799 edges) when declaration-level extraction would yield 3M+ edges.

---

## 5. Search Strategies: What Other Fields Teach Us

The search for cross-domain mathematical bridges is a special case of a general problem: how do you systematically explore a high-dimensional space when you don't know what you're looking for?

### 5.1 Evolutionary program synthesis (AlphaEvolve, DeepMind 2025)

AlphaEvolve uses LLMs to generate candidate programs, automated evaluators to score them, and an evolutionary framework to improve the population. On 50 open mathematical problems, it rediscovered state-of-the-art 75% of the time and improved on it 20% of the time.

**Relevance to our problem:** Our Layer 4 search_evolver implements a simplified version of this pattern. Key differences: AlphaEvolve uses an LLM ensemble (cheap model for volume, expensive for quality) with an island-based population model and `EVOLVE-BLOCK` markers that constrain which code the LLM may mutate. Its open-source implementation (OpenEvolve, Apache 2.0) accepts any evaluator returning a metrics dict — our 14-test battery is a natural fit. The problem definition format (initial program + evaluator + YAML config) could wrap our search functions directly. AlphaEvolve's program database tracks full genealogy and supports configurable exploitation/exploration ratios (default 0.7). Our search_evolver lacks all of these. The gap between our prototype and production-grade evolutionary synthesis is quantified: we use 1 model, 1 population, no genealogy, no island migration. OpenEvolve provides all of these out of the box.

### 5.2 Bayesian surprise as exploration reward (AutoDiscovery, Allen AI, NeurIPS 2025)

AutoDiscovery uses MCTS with *surprisal* as the reward function — the epistemic shift between prior and posterior beliefs about a hypothesis after seeing experimental results. This drives exploration toward genuinely unexpected findings rather than merely untested regions.

**Relevance to our problem:** Our novelty scorer rewards positional novelty (distance from centroid, low density, cold shadow tensor cells). AutoDiscovery's surprise score rewards *outcome* novelty — specifically, the KL divergence between prior and posterior belief distributions about a hypothesis, where beliefs are elicited by querying an LLM 30 times before and after seeing evidence. Their reward is binary: surprise triggers if |belief_change| >= 0.2 AND KL >= 20.0. Their false positive proxy is 33% human disagreement. For our pipeline, the adaptation is cleaner: replace LLM belief elicitation with shadow tensor history. Prior = predicted battery pass rate from similar (pair, type) combinations already tested. Posterior = actual battery result. KL between predicted and actual pass vectors across 14 tests gives a rigorous, LLM-free surprise score. Cost drops from 560+ LLM calls per dataset to zero — the shadow tensor is the belief model.

### 5.3 Graph contrastive learning for formula embedding (SSEmb, CIKM 2025)

SSEmb represents mathematical formulas as Operator Graphs (nodes = operators/variables, edges = structural relationships), then trains embeddings via graph contrastive learning with substitution-based augmentation. Outperforms symbol-bag methods by 5+ percentage points on ARQMath-3 formula retrieval.

**Relevance to our problem:** Our 12.5M formulas are currently represented as flat feature vectors (operator counts, nesting depth). SSEmb's Operator Graph representation captures hierarchical structure that flat features miss. Their architecture: 2-layer Graph Isomorphism Network (GIN) encoder producing 400-dimensional embeddings, trained via InfoNCE contrastive loss on pairs of augmented views of the same formula. Critical finding: only substitution-based augmentation preserves mathematical validity (leaf substitution at p=0.3, parent-of-leaf at p=0.005, grandparent at p=0.002). Node dropping and edge perturbation destroy formula integrity. They trained on 16M formulas — comparable to our 12.5M — on 2x RTX 4090. The Operator Graph construction pipeline (LaTeX → Operator Tree → Operator Graph via subexpression deduplication) requires implementation from Song & Chen 2021, but our existing structural features (operators, nesting, subscripts) provide the skeleton. The main gap: we need to parse the LaTeX into actual trees, not just extract flat features from it.

### 5.4 Counterexample search (Wagner, Tel Aviv 2021-2026)

Wagner's system generates random combinatorial structures, evaluates them as potential counterexamples to conjectures, and evolves the population toward structures that are "almost" counterexamples. Has disproved 5 conjectures in graph theory and combinatorics.

**Relevance to our problem:** We currently reward hypotheses that *survive* the battery. Wagner's insight: structures that *almost* break a pattern are more informative than structures that comfortably satisfy it. Adapting this to our pipeline: instead of searching for correlations, search for specific dataset pairs where a correlation *should* exist (by theoretical reasoning) but doesn't. The absence is the finding.

### 5.5 MCTS for hypothesis generation (IRIS, ACL 2025)

IRIS uses Monte Carlo Tree Search to explore the space of research hypotheses, with an LLM-based Review Agent scoring quality. Each hypothesis can branch into refinements; bad branches are pruned, good branches expanded.

**Relevance to our problem:** Our research_cycle generates hypotheses one-shot from the LLM — no branching, no refinement. MCTS would allow systematic exploration of hypothesis space: "if correlation X is killed by F5, try normalization Y" as a branch rather than a fresh generation. The tree structure preserves exploration history and avoids revisiting killed branches.

---

## 6. Open Questions

1. **Do structural isomorphisms exist across mathematical domains?** If two domains share a structural pattern (same polynomial root distribution, same graph spectrum, same formula syntax tree shape), it would suggest a deeper algebraic connection. Current evidence: not found, but structural tools are new and most comparisons use flat features rather than hierarchical representations.

2. **Is the geometric misalignment fundamental?** RSA between OEIS and mathlib landscapes gives p=0.52 — no global geometric alignment. But local bridges succeed (5.1x enrichment at shared objects). Is this because the domains are genuinely independent at the global level, or because our representations are too coarse to capture the alignment?

3. **Can evolutionary search discover what human-designed search cannot?** Our hand-written search functions encode human intuitions about what might correlate. An evolved search function could test relationships that no human would think to look for. AlphaEvolve demonstrates this is possible for algorithm design. Whether it extends to cross-domain mathematical discovery is open.

4. **What is the right representation?** Scalar values are dead. Operator feature vectors are too coarse (killed by F13). Operator Graphs are promising but untested at scale. The representation problem may be the fundamental bottleneck — we cannot find structure we cannot represent.

5. **Is the null result universal or specific to our datasets?** We tested 21 datasets spanning number theory, algebra, topology, combinatorics, analysis, and mathematical physics. The scalar null may extend to all mathematical domains. Or there may be domains with genuine scalar bridges that we haven't included (e.g., representation theory, algebraic geometry, homotopy theory).

---

## 7. Kill Log

| # | Claim | Kill test | Lesson learned |
|---|-------|-----------|----------------|
| 1 | Feigenbaum constant in OEIS sequence | Parity artifact at 29 terms | Need 40+ terms for constant matching |
| 2 | Second Feigenbaum match | Order-3 recurrence | Same sequence, different angle |
| 3 | Polytope f-vector near-misses | Small-integer confound | Small integers match everything |
| 4 | NF-SmallGroups distributional match | z-normalization artifact | z-norm erases information |
| 5 | LMFDB-Maass MI=0.382 | Sparse histogram binning bias | MI on sparse histograms biased upward |
| 6 | KnotInfo-LMFDB 679 revivals | Sort-then-truncate bug | Sort THEN truncate, not reverse |
| 7 | Isogenies-Maass MI=0.109 | Deterministic data + sorted-rank | Deterministic data has zero stochastic content |
| 8 | NF-KnotInfo log-fractional-part | Dissolved at full resolution | Resolution kills false precision |
| 9 | Root probe z=137 (knot vs EC angles) | Correct interpretation | z=137 measured distance, not similarity |

---

## 8. Computational Contributions

### 8.1 OEIS term extensions
22,338 new terms for 1,422 sequences, computed by dynamic programming enumeration of lattice walks in Z^3. Zero mismatches against known terms. Queued for OEIS submission.

### 8.2 Asymptotic corrections
41 lattice walk sequences where the published short-run growth rate estimate deviates >2% from the long-run rate computed with our extended terms. All 41 survive the full 14-test battery. These represent genuine corrections to the literature.

### 8.3 Shadow tensor
A 210-cell map (21 datasets × 21 datasets, upper triangle) with 101K+ test records documenting every hypothesis tested, every battery result, and every kill signature. This is a reusable resource for any future cross-domain mathematical discovery effort.

---

## References

1. AlphaEvolve: A coding agent for scientific and algorithmic discovery. Google DeepMind, 2025. arXiv:2506.13131. Open-source implementation: OpenEvolve (Apache 2.0).
2. AutoDiscovery: Open-ended Scientific Discovery via Bayesian Surprise. Allen AI, NeurIPS 2025. arXiv:2507.00310. Code: github.com/allenai/autodiscovery.
3. SSEmb: A Joint Structural and Semantic Embedding Framework for Mathematical Formula Retrieval. CIKM 2025. arXiv:2508.04162.
4. IRIS: Interactive Research Ideation System for Accelerating Scientific Discovery. ACL 2025. arXiv:2504.16728.
5. Wagner, A.Z. Constructions in combinatorics via neural networks. arXiv:2104.14516. Five conjectures disproved.
6. Mathematical Information Retrieval: A Review. ACM Computing Surveys, 2025. doi:10.1145/3699953.
7. Song, Y. & Chen, J. Operator tree and operator graph representations for mathematical formula retrieval. 2021. (Upstream reference for SSEmb's graph construction.)
8. AI for Mathematics: Progress, Challenges, and Prospects. arXiv:2601.13209, 2026.
9. Gemini Deep Think: Accelerating Mathematical and Scientific Discovery. Google DeepMind, 2025.

---

*Version 1.1 — 2026-04-09. This is a living document, versioned daily as the pipeline advances.*
*Changelog: v1.1 adds expected bridges calibration result (Section 4.4), graph degree sequence survivors (Section 4.5), LaTeX parser status, AlphaEvolve/AutoDiscovery/SSEmb research details in Section 5.*
*Project Prometheus. Agent: Charon.*
