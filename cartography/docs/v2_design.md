# Charon v2 — Detailed Design

## Agent: Charon (Claude Code, Opus)
## Date: 2026-04-08
## Status: DESIGN — not yet implemented

---

## Why v2?

v1 proved three things:
1. The scalar layer is empty after prime detrending (z=0.2 max, 96% prime structure)
2. The pipeline works — 180/180 known truths, 37+ rediscoveries, 8 kills in one session
3. The hypothesis generation space (LLM-generated natural language) is exhausted at ~17K hypotheses

v2 changes **what we search**, **how we represent it**, and **what generates the hypotheses**.

### Council input (2026-04-08)

Four models (Gemini, ChatGPT, DeepSeek, Claude) reviewed v1 and proposed upgrades.
After filtering through standing orders (no narrative construction, test simplest first, kills > survivors):

- **Accepted:** structural comparison (ASTs, roots, graphs), precision exploitation, concept embeddings, search function evolution, battery-as-generative-map
- **Deferred:** persistent homology (needs embeddings first), adversarial multi-agent (battery already serves this role), tiered falsification (rigidity is a feature)
- **Killed:** buckyball geometry (narrative construction), executable proof sketches (Lean output too fragile)

---

## Architecture Overview

```
v2 has 4 layers, built sequentially. Each layer's output feeds the next.

LAYER 1: PRECISION AUDIT          (exploit 22K extended terms)
  asymptotic_auditor.py
      |
      v
LAYER 2: STRUCTURAL COMPARISON    (ASTs, roots, graph invariants)
  ast_bridge.py
  root_probes.py
  graph_invariants.py
      |
      v
LAYER 3: CONCEPT GEOMETRY         (embed the 39K concept graph)
  concept_embeddings.py
  novelty_scorer.py
      |
      v
LAYER 4: SEARCH EVOLUTION         (LLM writes search functions, battery selects)
  search_evolver.py
```

Each layer has its own battery gate. Nothing propagates without surviving falsification.

---

## Layer 1: Precision Audit

### Goal
Exploit the 22,338 extended OEIS terms we already have. Compare against published asymptotic estimates. Find where extra precision reveals something the community missed.

### Why this is first
- Zero new code risk. We have the data. We have constant_telescope. This is a comparison job.
- Claude (council) called it "most underexploited asset" and "a weekend project."
- If we find deviations, those are immediately publishable and independently verifiable.

### New tool: `asymptotic_auditor.py`

```
Input:
  - 22K extended sequences (cartography/oeis/data/new_terms/)
  - Published OEIS b-files and metadata (growth rates, asymptotic formulas)

Process:
  1. For each extended sequence:
     a. Compute growth rate from first 15 terms (short-run estimate)
     b. Compute growth rate from all terms (long-run estimate)
     c. If deviation > 2%: flag as "regime change candidate"
  2. For flagged sequences:
     a. Fit polynomial, exponential, and mixed models
     b. Compute AIC/BIC to determine which model wins at full length
     c. Compare against any published asymptotic formula in OEIS metadata
  3. For confirmed deviations:
     a. Run constant_telescope on the DEVIATION SEQUENCE (not raw terms)
     b. Cross-reference deviation pattern against Fungrim formulas
     c. Check if the corrected asymptotic matches a known constant

Output:
  - deviations.jsonl: sequence_id, short_rate, long_rate, delta, best_model, constant_match
  - regime_changes.jsonl: sequences where the asymptotic form itself changes

Battery gate:
  - Every flagged deviation must survive F1 (permutation), F3 (effect size), F13 (growth rate filter)
  - Constant matches must survive constant_telescope's own null (random sequence control)
```

### Estimated effort: 1-2 days
### Dependencies: existing term_extender output, constant_telescope.py
### Risk: deviations may all be rounding/truncation artifacts. That's fine — we log the null.

---

## Layer 2: Structural Comparison

### Goal
Move from scalar correlation to structural isomorphism. Compare shapes, trees, and graphs — not numbers.

### Why this is the core v2 upgrade
- DeepSeek (council): "search for isomorphisms of structure, not correlations"
- Scalars are exhausted. Primes pollute them. But polynomial root distributions, formula syntax trees, and graph spectra are immune to prime detrending.
- We already have the raw data (Jones polynomials, Alexander polynomials, OEIS formulas, Fungrim, mathlib import graph, MMLKG reference graph, isogeny adjacency matrices).

### New tool: `ast_bridge.py`

```
Input:
  - Fungrim formulas (3.1K, with symbolic structure)
  - OEIS formula fields (subset of 394K with explicit formulas)

Process:
  1. Parse formulas into abstract syntax trees (ASTs)
     - Fungrim: already structured (XML/JSON with operators)
     - OEIS: regex + sympy.parsing for standard notation
  2. Extract structural features from each AST:
     - Depth, branching factor, operator frequency vector
     - Subtree hashes (identify recurring subexpressions)
  3. Compute pairwise tree-edit distance (Zhang-Shasha algorithm)
     for cross-domain formula pairs
  4. Cluster by structural similarity (not symbolic identity)
  5. Flag clusters that span multiple datasets

Output:
  - ast_features.jsonl: formula_id, dataset, depth, operators, subtree_hashes
  - cross_domain_clusters.jsonl: cluster_id, members[], edit_distances[]
  - structural_bridges.jsonl: formula pairs with edit_distance < threshold AND different datasets

Battery gate:
  - F1 (permutation): do random formula pairs have similar edit distances? (null distribution)
  - F3 (effect size): is the within-cluster distance meaningfully < between-cluster?
  - NEW F15 (structural null): compare against ASTs from randomly generated expressions of same depth/complexity
```

### New tool: `root_probes.py`

```
Input:
  - KnotInfo: Alexander polynomial coefficients (13K knots, avg 7.5 coefficients)
  - KnotInfo: Jones polynomial coefficients (13K knots, avg 11.8 coefficients)
  - LMFDB EC: a_p coefficient sequences (31K curves, 25 primes each)
  - LMFDB MF: Hecke eigenvalue sequences
  - Genus-2: L-function data (where available)

Process:
  1. Compute polynomial roots (numpy.roots) for each knot polynomial
  2. Compute root DISTRIBUTIONS:
     - Radial distribution (|root| histogram)
     - Angular distribution (arg(root) histogram)
     - Nearest-neighbor spacing distribution (GUE/GOE comparison)
  3. For EC/MF: compute Sato-Tate angle distribution from a_p values
     theta_p = arccos(a_p / (2 * sqrt(p)))
  4. Compare distributions cross-domain:
     - KS test: Alexander root angles vs Sato-Tate angles
     - Wasserstein distance between spacing distributions
     - GUE/GOE fit residuals: do both deviate from RMT in the same direction?

Output:
  - root_distributions.jsonl: object_id, dataset, root_radii, root_angles, spacings
  - cross_domain_comparisons.jsonl: pair, KS_stat, wasserstein, gue_residual_correlation

Battery gate:
  - F1 (permutation): shuffle object labels between datasets
  - F5 (normalization): does the comparison survive under different binning?
  - F12 (partial correlation): partial out degree/dimension/conductor
  - F13 (growth rate): not applicable (distributions, not sequences)
```

### New tool: `graph_invariants.py`

```
Input:
  - Isogeny adjacency matrices (3.2K primes)
  - mathlib import graph (8.5K modules, 1,799 edges)
  - MMLKG reference graph (1.4K articles, 28K edges)
  - OEIS cross-reference graph (335K sources, 1.59M edges)
  - KnotInfo: Dowker codes -> graphs (future, needs parsing)

Process:
  1. For each graph, compute invariants:
     - Spectral gap (lambda_2 of adjacency/Laplacian)
     - Algebraic connectivity (Fiedler value)
     - Degree distribution (power law exponent, if applicable)
     - Clustering coefficient distribution
     - Diameter, average path length
  2. Compare invariant vectors cross-domain:
     - Are spectral gaps correlated across domains at matched parameters?
     - Do degree distributions share the same functional form?
  3. Subgraph matching:
     - Extract ego-graphs (k-hop neighborhoods) around bridge concepts
     - Compare ego-graph structure across domains

Output:
  - graph_features.jsonl: graph_id, dataset, spectral_gap, fiedler, degree_exponent, clustering
  - cross_domain_graph_matches.jsonl: pairs with similar spectral/structural profiles

Battery gate:
  - F9 (simpler explanation): does Erdos-Renyi with same edge density produce same invariants?
  - F1 (permutation): rewire edges randomly, recompute
  - F3 (effect size): is the cross-domain similarity above random-graph baseline?
```

### Estimated effort: 5-7 days for all three tools
### Dependencies: numpy, scipy, networkx, sympy (all installed or trivial)
### Risk: AST parsing for OEIS formulas is messy (free-text). Start with Fungrim (already structured), expand to OEIS formulas that parse cleanly, skip the rest.

---

## Layer 3: Concept Geometry

### Goal
Embed the 39K-concept graph into a vector space. Define distance, density, and novelty computationally. Replace poetic "voids" with measurable coordinates.

### Why this matters
- ChatGPT (council) was right: without embeddings, "void" and "edge" are metaphors, not computable quantities.
- The concept graph has 1.91M links across 16 datasets. That's enough structure for meaningful embeddings.
- Once we have coordinates, we can measure novelty, target exploration, and track coverage.

### New tool: `concept_embeddings.py`

```
Input:
  - Concept index: 39K concepts, 1.91M links, 4,410 bridges (from concept_index.py)

Process:
  1. Build adjacency matrix from concept links
     - Nodes: 39K concepts (nouns + verbs)
     - Edges: co-occurrence in same dataset-object (weighted by frequency)
     - Bridge edges: concepts spanning 2+ datasets get cross-dataset edges
  2. Compute embeddings (two methods, compare):
     a. Spectral: eigenvectors of normalized Laplacian (top-k, k=64 or 128)
     b. Node2Vec: random walks on the concept graph (if spectral is too coarse)
  3. Output: 39K vectors in R^k

Derived quantities:
  - Per-concept: distance to centroid, local density (k=10 neighbors), edge entropy
  - Per-dataset: hull volume in embedding space, overlap with other dataset hulls
  - Per-pair: embedding-space distance between dataset centroids vs actual bridge count

Output:
  - concept_vectors.npy: (39K x k) embedding matrix
  - concept_metadata.jsonl: concept_id, dataset_memberships, centroid_dist, local_density
  - dataset_geometry.jsonl: dataset, hull_volume, centroid, overlap_matrix
```

### New tool: `novelty_scorer.py`

```
Input:
  - concept_vectors.npy (from concept_embeddings.py)
  - Shadow tensor cells (210 cells, 101K+ records)

Process:
  1. For each concept:
     novelty_score = (
       w1 * distance_to_nearest_cluster_center +
       w2 * inverse_local_density +
       w3 * edge_entropy +
       w4 * shadow_tensor_cold_score  # how undertested is this region?
     )
  2. Rank concepts by novelty_score
  3. Map back to dataset pairs: which pairs have the highest concentration
     of high-novelty concepts?
  4. Generate exploration targets: top-N novel concepts that span 2+ datasets
     and have < 5 tests in shadow tensor

Output:
  - novelty_rankings.jsonl: concept_id, novelty_score, components, suggested_probe
  - frontier_targets.jsonl: top 50 highest-novelty cross-dataset concepts
  - exploration_heatmap.json: 21x21 dataset matrix colored by novelty concentration

Integration:
  - explorer_loop.py v2: instead of random void scanning, target frontier_targets
  - research_cycle.py: bias hypothesis generation toward high-novelty regions
```

### Estimated effort: 3-4 days
### Dependencies: scikit-learn (spectral), node2vec package (optional), numpy
### Risk: 39K nodes with 1.91M edges is manageable. Spectral embedding of the Laplacian is O(n^2) for dense, but our graph is sparse — should be fast. If Node2Vec is slow, spectral alone is sufficient.

---

## Layer 4: Search Evolution

### Goal
Stop generating natural-language hypotheses. Start generating Python search functions. Let the battery select the fittest. Survivors seed the next generation.

### Why this is the architecture break
- v1 generates hypotheses in natural language, then searches for evidence. The LLM is the bottleneck and the source of narrative construction.
- v2 Layer 4: the LLM generates *code* — a Python function that takes two datasets and returns a test statistic. The battery evaluates the function. No narrative needed.
- This is the AlphaEvolve pattern: evolve programs, not predictions.

### New tool: `search_evolver.py`

```
Input:
  - Seed population: 10-20 hand-written search functions (extracted from search_engine.py)
  - Concept embeddings (from Layer 3): for targeting underexplored regions
  - Shadow tensor: for rewarding novel failure modes
  - Battery: falsification_battery.py (unchanged)

Process:
  1. GENERATE (LLM call — 1 per generation):
     Prompt: "Given these seed functions and this frontier target,
     write a new Python function that computes a test statistic
     between dataset_a and dataset_b. The function must:
     - Accept two lists of numerical values
     - Return a dict with keys: statistic, p_value, description
     - Use only numpy/scipy (no external data)"
     
  2. VALIDATE (zero-cost):
     a. Syntax check: does it parse? (ast.parse)
     b. Sandbox run: execute on 3 known dataset pairs with known outcomes
     c. Sanity: does it return reasonable types and ranges?
     
  3. TEST (zero-cost):
     a. Run the function on all relevant dataset pairs
     b. Run full 14-test battery on every claimed correlation
     c. Record: which battery tests pass, which fail, kill signature
     
  4. SELECT:
     a. Fitness = (
          battery_survival_score * 0.3 +
          novel_failure_mode_score * 0.3 +   # new kill type in shadow tensor
          frontier_coverage_score * 0.2 +      # tests underexplored regions
          parsimony_score * 0.2                 # shorter functions preferred
        )
     b. Top-K survive to seed next generation
     
  5. MUTATE (LLM call — 1 per generation):
     Prompt: "Here is a search function that scored {fitness}. It failed
     battery test {F_n} because {reason}. Modify it to address that failure
     while preserving what worked."
     
  6. LOOP: generations continue until fitness plateau or budget exhausted

Output:
  - evolved_functions/: Python files, one per surviving function
  - evolution_log.jsonl: generation, function_id, fitness, battery_results, lineage
  - shadow_tensor updates: every test feeds back into the dark matter map

Population management:
  - Max population: 50 functions
  - Elitism: top 5 always survive
  - Immigration: 2 random new functions per generation (exploration)
  - Extinction: functions that fail F1 (permutation null) on ALL pairs are culled
```

### Integration with existing pipeline

```
research_cycle.py (v1)     search_evolver.py (v2)
      |                           |
      v                           v
  LLM generates              LLM generates
  natural-language            Python functions
  hypotheses                      |
      |                           v
      v                      sandbox + battery
  search_engine.py                |
      |                           v
      v                      shadow tensor
  battery                    (same battery,
      |                       same tensor)
      v
  shadow tensor

Both feed the same shadow tensor.
v1 continues running (it's free with explorer_loop).
v2 runs in parallel as a separate evolutionary process.
```

### Estimated effort: 5-7 days
### Dependencies: LLM API (DeepSeek or Claude), ast module (stdlib), existing battery
### Risk: LLM-generated code may be brittle or circular. Mitigations:
  - Sandbox execution with timeout (5s max per function)
  - AST complexity cap (max 50 nodes — forces simplicity)
  - Tautology detection: if the function is equivalent to an existing seed, reject
  - Standing order: no narrative construction. The function either produces a number or it doesn't.

---

## New Battery Tests

v2 adds two tests to the existing 14:

### F15: Structural Null
For AST/tree-based comparisons: generate random expression trees of the same depth and operator distribution. If the cross-domain similarity isn't significantly above this null, kill it.

### F16: Embedding Distance Control
For any claimed bridge between datasets A and B: compute the embedding-space distance between the involved concepts. If the bridge concepts are already close in embedding space (i.e., they share vocabulary), the "discovery" is trivial. Only bridges between distant concepts in embedding space count as novel.

These extend the battery to 16 tests. The gate remains: ALL non-skipped tests must pass.

---

## File Layout

```
cartography/shared/scripts/v2/
  layer1/
    asymptotic_auditor.py      # Compare extended terms vs published estimates
  layer2/
    ast_bridge.py              # Formula AST parsing + tree-edit distance
    root_probes.py             # Polynomial root distribution comparison
    graph_invariants.py        # Spectral gap, Fiedler, degree distributions
  layer3/
    concept_embeddings.py      # Spectral/Node2Vec embedding of concept graph
    novelty_scorer.py          # Novelty = distance + inverse_density + entropy + cold_score
  layer4/
    search_evolver.py          # Evolutionary program synthesis
    evolved_functions/         # Surviving search functions
    sandbox.py                 # Safe execution environment for generated code
  battery_v2.py                # F15 + F16 additions (imports from v1 battery)
```

---

## Execution Plan

| Phase | Layer | Duration | API cost | Prerequisite |
|-------|-------|----------|----------|--------------|
| **Week 1** | Layer 1: Precision Audit | 1-2 days | 0 | existing data |
| **Week 1** | Layer 2a: root_probes.py | 2-3 days | 0 | numpy |
| **Week 2** | Layer 2b: ast_bridge.py | 3-4 days | 0 | sympy |
| **Week 2** | Layer 2c: graph_invariants.py | 2-3 days | 0 | networkx |
| **Week 3** | Layer 3: concept_embeddings + novelty | 3-4 days | 0 | Layer 2 output |
| **Week 3** | F15 + F16 battery additions | 1 day | 0 | Layers 2-3 |
| **Week 4** | Layer 4: search_evolver.py | 5-7 days | LLM tokens | Layers 1-3 |

Total: ~4 weeks. Layers 1-3 are zero API cost. Layer 4 needs LLM tokens.

v1 terminals + explorer_loop continue running throughout.
Every layer's output feeds the shadow tensor.

---

## Success Criteria

1. **Layer 1:** Find >= 1 sequence where published asymptotic is wrong by >2% at extended length. Or: confirm all 22K match (publishable null).
2. **Layer 2:** Find >= 1 cross-domain structural similarity that survives the full 16-test battery. Or: confirm structural layer is also empty (stronger null, publishable).
3. **Layer 3:** Produce a concept embedding where known bridges (modularity theorem, BSD) appear as nearby points, and voids are measurably low-density regions.
4. **Layer 4:** Evolve >= 1 search function that finds a pattern the hand-written functions missed. Or: characterize the failure modes of evolved search (publishable as negative result on program synthesis for discovery).

The honest answer may be zero on all four. That's still v2 working correctly.

---

## What v2 Does NOT Change

- **falsification_battery.py** — the 14-test core is untouched (F15/F16 are additions, not modifications)
- **search_engine.py** — 21 datasets, 56 searches, all remain operational
- **concept_index.py** — the 39K concept layer feeds Layer 3 as input
- **shadow_tensor.py** — receives output from all 4 new layers
- **explorer_loop.py** — v1 loop continues; v2 novelty scorer can optionally steer it
- **research_cycle.py** — v1 LLM hypothesis generation continues in parallel
- **realign.py** — post-change calibration remains mandatory

v2 is additive. v1 keeps running. The shadow tensor is the shared accumulator.

---

*Designed: 2026-04-08, Charon (Opus)*
*Standing orders: explore the unpopular, trust nothing, kill everything, the honest number is zero*
