# Cartography — Cross-Domain Mathematical Discovery Pipeline

## Project Prometheus — April 2026

---

## What This Is

An autonomous pipeline for discovering structural connections between mathematical datasets. Ingests data from 21 sources spanning 1M+ mathematical objects, builds a concept bridge layer, tests hypotheses with a 14-test falsification battery, and maps the landscape of what we've explored and what we've killed.

**Current status: zero novel cross-domain discoveries.** The pipeline validates known mathematics at 100% (180/180 calibration tests), has produced 22,338 new OEIS terms, identified 41 verified asymptotic corrections, and killed 9 false discoveries. The scalar correlation layer between datasets is definitively empty after prime detrending — 96% of all apparent cross-dataset structure is shared prime factorization. Structural comparison tools (formula ASTs, polynomial root distributions, graph spectral analysis) are operational but have not yet yielded surviving bridges.

---

## Datasets

| Dataset | Objects | Source |
|---------|---------|--------|
| OEIS | 394K sequences | oeis.org |
| LMFDB EC | 31K elliptic curves | lmfdb.org |
| LMFDB MF | 102K modular forms | lmfdb.org |
| Genus-2 | 66K curves | lmfdb.org |
| KnotInfo | 13K knots | indiana.edu/~knotinfo |
| NumberFields | 9.1K fields | lmfdb.org |
| mathlib | 8.5K modules | github.com/leanprover-community/mathlib4 |
| Fungrim | 3.1K formulas | fungrim.org |
| Isogenies | 3.2K primes | lmfdb.org |
| SmallGroups | 2.4K orders | GAP SmallGrp library |
| FindStat | 1,993 statistics | findstat.org |
| Metamath | 46K theorems | set.mm |
| Materials | 1K+ crystals | materialsproject.org |
| ANTEDB | 244 theorems | Tao et al. |
| MMLKG | 1.4K articles | Mizar library |
| Space Groups | 230 | Bilbao Crystallographic Server |
| Polytopes | 1.2K | polyDB |
| pi-Base | 220 spaces | pi-base.org |
| Maass | 300 forms | lmfdb.org |
| Lattices | 21 | Literature |
| OpenAlex | 10K concepts | openalex.org |

**Corpus data:** 5M+ mathematical formulas from OpenWebMath (HuggingFace), with structural features extracted (operators, nesting depth, domain classification).

---

## Architecture

The pipeline has two layers of tools built on top of a shared data and testing infrastructure.

### Core Infrastructure
- **Search engine** — 21 datasets, 56 search functions, DuckDB backend
- **Concept index** — 39K concepts (24K nouns + 15K verbs), 1.91M links across 16 datasets, 4,410 cross-dataset bridges
- **Falsification battery** — 14 computational kill tests, no LLM in the loop. Permutation null, subset stability, effect size, confound sweep, normalization sensitivity, base rate, dose-response, direction consistency, simpler explanation, outlier sensitivity, cross-validation, partial correlation, growth rate filter, phase shift.
- **Shadow tensor** — 210 dataset-pair cells, 101K+ test records. Every test, every kill mode, every near-miss. The dark matter map of what we've explored.
- **Research memory** — 18K+ hypotheses fingerprinted and deduplicated

### Scalar Layer Tools (v1, complete)
- `research_cycle.py` — LLM-driven hypothesis generation, 1 API call per cycle
- `explorer_loop.py` — Zero-cost autonomous exploration, novelty-steered
- `void_scanner.py` / `bridge_hunter.py` / `map_elites.py` — Diversity-driven bin filling
- `microscope.py` — 3-layer prime decontamination (detrend + filter + normalize)
- `term_extender.py` — OEIS term factory (22K terms, zero mismatches)
- `constant_telescope.py` — Inverse symbolic identification (39 constants x 68K sequences)
- `realign.py` — Post-data-change calibration (inventory + concepts + tensors + 180-test battery)

### Structural Layer Tools (v2, operational)
- `asymptotic_auditor.py` — Compare extended sequences against published growth rate estimates
- `ast_bridge.py` — Formula structural comparison via operator feature vectors
- `root_probes.py` — Polynomial root distribution comparison (knot polynomials vs Sato-Tate angles)
- `graph_invariants.py` — Spectral gap, algebraic connectivity, degree sequences across 53 graphs + battery testing
- `formula_graph_builder.py` — LaTeX → Operator Tree parser (17K/sec, 99.996% success)
- `expected_bridges.py` — Theory-predicted bridge testing (12 bridges, 3 tiers)
- `findstat_probes.py` — Cold territory mapping (10 zero-test pairs)
- `openwebmath_ingest.py` — Corpus ingestion from HuggingFace (5M+ formulas)
- `concept_embeddings.py` — Spectral embedding of concept graph into R^64
- `novelty_scorer.py` — 5-component novelty: centroid distance + density + entropy + cold + Bayesian surprise
- `search_evolver.py` — Evolutionary synthesis of search functions (LLM generates code, battery selects)
- `battery_sweep.py` — Batch falsification across all tool outputs

---

## Results

### Definitive findings
- **The scalar layer is empty.** After removing shared prime factorization, zero cross-dataset correlation survives at any significance level across all 210 dataset pairs. Highest z=0.2.
- **180/180 known truth calibration.** The battery correctly validates modularity theorem (z=72), Deuring mass formula (z=93), BSD small-prime signature, Heegner numbers, Euler relation for polytopes, class number variation by degree, and 33 other known results.
- **41 asymptotic regime changes survive the battery.** Extended lattice walk sequences show growth rate shifts of 2-84% between early and late terms. These represent genuine corrections to published estimates.

### Negative results
- Formula AST comparison across Fungrim modules: killed by F13 (growth rate artifact — operator count correlates with Jaccard regardless of domain).
- Polynomial root angle distributions (knot vs elliptic curve): killed by correct interpretation. z=137 measured distributional *distance*, not similarity. The distributions occupy opposite ends of [0, pi].
- Graph spectral comparison (mathlib imports vs OEIS cross-refs): r=0.91 correlation, but only 6 scalar features per graph. Insufficient for battery testing. Degree sequence data needed.
- FindStat cold-pair probes: 18/22 killed. 1 rediscovery (Alexander degree vs crossing number — known theorem). 3 survivors on N=17 samples (below battery sensitivity).
- Expected bridges: 12 theory-predicted connections tested across 3 tiers. **Tier 1 (calibration): 0/4 survive scalar battery** — modularity theorem, class field theory, isogeny reduction all killed at scalar level. These are known truths, confirming that known bridges are structural, not scalar. Tier 3: Maass↔MF level distributions survive (10/14 tests pass).
- Graph degree sequences: 4/10 cross-domain pairs survive battery (isogeny graphs at primes 947, 2311, 2887, 4013 vs mathlib/MMLKG).
- Formula parsing: 12.5M LaTeX formulas parsed to operator trees at 17K/sec, 99.996% success. Operator vocabulary: multiply, subscript, eq, power, add, frac, sum, int, sin. Tree depths up to 44.

### Production output
- **22,338 new OEIS terms** — 1,422 sequences extended by dynamic programming. Zero mismatches against known terms. Queued for submission.
- **41 verified regime changes** — asymptotic corrections surviving full 14-test battery.
- **68,770 sleeping beauties** — high-entropy, low-connectivity OEIS sequences identified and characterized.
- **5M+ formula features** — structural fingerprints from OpenWebMath corpus.
- **Shadow tensor** — 210 cells, 101K+ test records mapping every hypothesis tested and how it died.

---

## Known Limitations

### Data representation
- OEIS embedding is dominated by growth rate. Sequences with similar combinatorial structure but different growth rates appear distant. A formula-structure or cross-reference embedding would be more informative.
- mathlib dependency graph uses file-level imports (1,799 edges). Declaration-level extraction via LeanDojo would yield 3M+ edges and much richer graph structure.
- FindStat cached data contains metadata only (collection names, statistic counts), not computed statistic values on actual combinatorial objects.

### Geometric
- Cross-dataset landscapes are not geometrically aligned (RSA p=0.52 between OEIS and mathlib). Only topologically connected through shared objects. Global distance metrics do not transfer across domains; only local bridges work.
- Concept embedding captures co-occurrence structure but not semantic meaning. Two concepts connected through the same dataset are "close" even if mathematically unrelated.
- Persistent homology and curvature analysis deferred. Require stable, detrended embeddings to avoid rediscovering prime structure in topology.

### Statistical
- The 14-test battery has limited sensitivity at small sample sizes (N<20). Three FindStat survivors at N=17 are likely artifacts that the battery cannot distinguish from signal.
- Hypothesis generation by LLM tends toward narrative construction. The concept layer and search evolution partially address this but don't eliminate it.
- AI-to-AI feedback loops amplify narrative. Two AIs agreeing something is exciting is not evidence — it's correlated bias.

### Search
- Search evolution (Layer 4) has not yet produced a function that outperforms hand-written seeds. LLMs generate overly complex functions that fail complexity validation. Prompt engineering partially addresses this.
- The explorer loop previously tested 172 unique hypotheses 282,000 times (no dedup). Fixed, but illustrates that zero-cost exploration without memory is pure waste.

---

## Kill Log

Nine false discoveries, each one improving the pipeline:

| # | Claim | How it died | Battery improvement |
|---|-------|-------------|---------------------|
| 1 | Feigenbaum constant in OEIS sequence | Parity artifact at 29 terms | Min 40 terms for constant matching |
| 2 | Second Feigenbaum match | Order-3 recurrence | Same |
| 3 | Polytope f-vector near-misses | Small-integer confound | Added integer null generators |
| 4 | NF-SmallGroups distributional match | z-normalization artifact | Added F5 (normalization sensitivity) |
| 5 | LMFDB-Maass MI=0.382 | Sparse histogram binning bias | Added random-pairing null for MI |
| 6 | KnotInfo-LMFDB 679 revivals | Sort-then-truncate bug | Fixed subsample ordering |
| 7 | Isogenies-Maass MI=0.109 | Deterministic data + sorted-rank | Verify residual variance > 0 |
| 8 | NF-KnotInfo log-fractional-part | Dissolved at full resolution | Resolution check before claiming |
| 9 | Root probe z=137 | Measured distance not similarity | Added interpretation gate |

---

## Roadmap

### Near-term (v4.1)
- [ ] Structural fingerprint embedding on 5M+ formula corpus (UMAP/spectral on operator features)
- [ ] Wire formula embeddings into cross-domain comparison at scale
- [ ] Rerun search evolution with constrained prompts (15-line max, parsimony-weighted fitness)
- [ ] Submit 22K OEIS terms and 41 regime change corrections
- [ ] Store full degree sequences in graph_invariants for proper battery testing

### Medium-term
- [ ] Ingest ARQMath formula datasets (millions of indexed formulas from arXiv/MathOverflow)
- [ ] Ingest S2ORC citation graph for large-scale graph comparison
- [ ] Extract declaration-level mathlib dependencies via LeanDojo (1.8K → 3M+ edges)
- [ ] Build OEIS embedding from cross-references and formula structure instead of raw terms
- [ ] Compute FindStat statistics on actual combinatorial objects for value-level probing
- [ ] Persistent homology on detrended concept embedding

### Open questions
- Do structural isomorphisms exist between mathematical domains at the level of formula syntax, polynomial roots, or graph spectra? (Current answer: not found, but structural tools are new.)
- Can evolutionary program synthesis discover search strategies that humans miss? (Current answer: inconclusive — LLM-generated functions don't yet outperform hand-written seeds.)
- Is the geometric misalignment between mathematical landscapes fundamental, or an artifact of our embedding representation? (Current evidence: RSA fails globally, but local bridges succeed.)
- What is the right representation for mathematical objects in a cross-domain discovery system? (Current approach: scalars are dead, operators/verbs are promising, formulas-as-trees untested at scale.)

---

## Running the Pipeline

```bash
# Launch 8 terminals + explorer
run_charon_8terminals.bat

# Post-data-change calibration (MANDATORY)
cd cartography/shared/scripts
python realign.py

# Structural tools
cd cartography/shared/scripts/v2
python layer1/asymptotic_auditor.py
python layer2/ast_bridge.py
python layer2/root_probes.py
python layer2/graph_invariants.py
python layer2/openwebmath_ingest.py --max-docs 6400000
python layer3/concept_embeddings.py --k 64
python layer3/novelty_scorer.py --top 50
python layer4/search_evolver.py --dry-run
python battery_sweep.py
```

---

## Lessons Learned

1. **Primes are the atmosphere.** Strip them before testing any cross-dataset correlation.
2. **Sorted-rank correlation is useless.** Any two monotone arrays give rho~1.0.
3. **Z-normalization erases information.** Any two near-uniform sequences match.
4. **MI on sparse histograms is biased upward.** Use random-pairing null.
5. **Sort THEN truncate**, not truncate then sort.
6. **29 terms is not enough** for constant matching. Need 40+.
7. **When two AIs agree something is exciting**, reach for the battery, not the champagne.
8. **Every kill is a discovery** for the shadow tensor.
9. **Deterministic data has zero stochastic content.** Verify residual variance > 0.
10. **The honest number is zero.** Report it.
11. **z-scores measure distance from null, not similarity.** Read what you're testing.
12. **Small samples evade the battery.** Always check N before trusting a survivor.
13. **Symbol bags are not syntax trees.** Jaccard on operator sets is killed by growth rate artifacts.
14. **LLMs over-engineer.** Demand brevity. Complexity caps in the prompt, not just the validator.

---

### Recent Results (v5.0, 2026-04-09)
- **34 signature extractors** built and fired (operadic, symmetry, convexity, Newton polytope, mod-p, p-adic, Galois, tropical, Morse, fractional derivatives, spectral, phase space, info-theoretic, resurgence, recursion operator, and 19 more)
- **The Rosetta Stone:** cross-domain operadic skeleton distribution maps mathematical universals — a translation layer between symbolic math and human conceptual organization (5,424 cross-domain clusters)
- **Algebraic DNA in OEIS:** recursion operator extraction finds 269 family clusters including Collatz (A006370) sharing characteristic polynomial with 2 other sequences, and 4 Erdos problems sharing recurrences with non-Erdos families
- **61 verified structural isomorphisms** (same skeleton, different outputs at 5 test points), 9 matching on 5/7 independent lenses
- **OpenEvolve integration:** fitness 0.551, 2.6x over homegrown evolver
- **47,066 modular form congruences** detected by systematic Hecke eigenvalue comparison. 10 mod-11 congruences, 6 at levels where 11 does not divide the level.
- **Full congruence graph:** 981 congruences across ell={5,7,11} from 94,497 pairs. 242 independent coprime+irreducible instances at 162 levels, all Sturm-verified with irreducibility proved. Mod-5: 190 at 126 levels. Mod-7: 50 at 34 levels. Mod-11: 2 at 2 levels. Zero for ell>=13. Twist deduplication separates functorial from intrinsic multiplicity. First systematic mapping of the fiber structure {newforms} -> {mod-ell representations} across the LMFDB weight-2 database.
- **Genus-2 frontier (GSp_4):** 42 candidate mod-3 congruences between USp(4) genus-2 curves at coprime conductors. Degree-4 Hasse squeeze kills ell>=5. Heuristic (24 primes, ~10^{-23} random probability) but not theorem-level (Sturm bound ~10^9).
- **12 kills, 3 discoveries + 1 frontier** (Rosetta Stone + algebraic DNA + GL_2 congruence fiber map + GSp_4 candidates)

---

*Born: Project Prometheus, March 2026. Pipeline v5.0, April 2026.*
*21 datasets. 39K concepts. 34 signature lenses. 14-test battery. 12 kills. 3 discoveries. 981 congruences. 242 independent verified instances of mod-ell multiplicity at 162 levels. 31,073/31,073 modularity detection. 27M parsed formula trees. 269 algebraic family clusters. The ferryman found the Rosetta Stone while looking for bridges, detected the modularity theorem structurally, and mapped the fiber structure of the eigenform-to-representation reduction across the full LMFDB weight-2 database.*
