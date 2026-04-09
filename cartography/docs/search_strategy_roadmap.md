# Search Strategy Roadmap — Charon v4+

## Adapted Techniques for Cross-Domain Mathematical Discovery
### 2026-04-09

---

## Current Search Architecture (v4.0)

```
research_cycle.py          → LLM generates natural-language hypotheses (v1, running)
explorer_loop.py           → Novelty-steered void scanning + bridge hunting (v1, running)
search_evolver.py          → LLM generates Python search functions, battery selects (v2 L4, prototype)
```

**Limitation:** v1 generates flat hypotheses (no branching/refinement). v2 L4 generates code but LLM over-engineers. Neither uses prediction-error or surprise as a signal. Exploration is positionally steered (cold regions) but not outcome-steered (unexpected results).

---

## Enumerated Strategies — Prioritized for Our Data Layout

### Strategy 1: Operator Graph Embedding (from SSEmb)
**Priority: IMMEDIATE — blocks on OpenWebMath ingestion (complete)**

| Aspect | SSEmb (original) | Our adaptation |
|--------|-----------------|----------------|
| Input | ARQMath formulas (hundreds of K) | 12.5M OpenWebMath formulas |
| Representation | Operator Graph from Content MathML | Operator Graph from LaTeX (regex + structural parsing) |
| Training | Graph contrastive learning (GCL) | GCL or spectral embedding (if GCL too expensive at 12.5M) |
| Augmentation | Substitution-based (swap variables) | Same, plus operator-type substitution (swap sin↔cos) |
| Output | Embedding per formula | Embedding per formula → cluster → cross-domain cluster detection |
| Evaluation | ARQMath retrieval benchmarks | Our 14-test battery on claimed cross-domain bridges |

**Implementation plan:**
1. `formula_graph_builder.py` — parse LaTeX to Operator Graphs (nodes=operators/variables, edges=structural containment)
2. `formula_embeddings.py` — spectral or GCL embedding of 12.5M formula graphs
3. Feed into `ast_bridge.py` v2 — replace Jaccard with graph-distance comparison
4. Battery-test any cross-domain formula clusters

**Data compatibility:** Our formulas already have operators, nesting depth, structural tokens. Building the graph is an enrichment step, not a reparse.

**Risk:** 12.5M graphs may be too large for GCL training on consumer hardware. Fallback: spectral embedding of a representative subsample (1M formulas), then project the rest.

**Research update (2026-04-09):** SSEmb uses a 2-layer GIN (Graph Isomorphism Network) encoder with 400-dim embeddings, vocabulary of 11,868 operator labels. Trained on 16M formulas on 2x RTX 4090 — comparable to our 12.5M. Critical finding: only substitution-based augmentation works for math graphs (node dropping and edge perturbation "destroy formula integrity"). Three tiers: leaf substitution (p=0.3), parent-of-leaf (p=0.005), grandparent (p=0.002). We have one RTX card (17GB VRAM) — may need to reduce batch size from their 2560 or use spectral fallback. The Operator Graph construction step references Song & Chen 2021 for LaTeX→OPT parsing — we'd need to implement or approximate from our existing structural features.

---

### Strategy 2: Bayesian Surprise Exploration (from AutoDiscovery)
**Priority: HIGH — low implementation cost, changes exploration quality**

| Aspect | AutoDiscovery (original) | Our adaptation |
|--------|------------------------|----------------|
| Reward | Surprisal = KL divergence (prior → posterior) | Prediction error = |predicted battery outcome - actual| |
| Tree search | MCTS with progressive widening | MCTS over dataset-pair × hypothesis-type space |
| Prior | LLM's beliefs about hypothesis | Battery history for this (pair, type) in shadow tensor |
| Posterior | LLM's beliefs after experiment | Actual battery result |
| Evaluation | LLM judges "surprising" | Battery provides ground truth (no LLM judgment) |

**Implementation plan:**
1. Add `surprise_score` to `novelty_scorer.py`:
   - Before testing hypothesis H on pair P: predict outcome from shadow tensor history for similar (pair, type) combinations
   - After testing: measure |predicted - actual| across battery tests
   - High surprise = the pair behaved differently than its neighborhood predicts
2. Modify explorer_loop to weight exploration by `novelty_score * surprise_score`
3. Track surprise history — do high-surprise results cluster in specific regions?

**Data compatibility:** Shadow tensor already has 101K+ test records with kill signatures. Prediction is a lookup + interpolation problem. No new data needed.

**Key advantage over AutoDiscovery:** They use LLM judgment as ground truth — 30 LLM calls per node just for belief elicitation, 560+ calls per dataset run. We use the battery (0.3 seconds, zero LLM). Their false positive proxy is 33% human disagreement rate. Our false positive rate on known math is 0/180.

**Research update (2026-04-09):** AutoDiscovery's surprise = `|posterior_mean - prior_mean| >= 0.2 AND KL(posterior||prior) >= 20.0`. Their prior/posterior are Beta distributions fitted from repeated LLM queries. For us: prior = predicted battery pass rate from shadow tensor history for similar (pair, type) combinations. Posterior = actual battery result. KL between predicted and actual pass vectors across 14 tests. No LLM belief elicitation needed — the shadow tensor IS the belief model. Their MCTS uses UCB1 with progressive widening (expand only if |children| < k × visits^α). Default branching factor 8, default budget 16 experiments. We can use the same skeleton with battery results as terminal rewards.

---

### Strategy 3: Multi-Model Evolutionary Synthesis (from AlphaEvolve)
**Priority: HIGH — fixes L4's main failure mode**

| Aspect | AlphaEvolve (original) | Our adaptation |
|--------|----------------------|----------------|
| Generation | Gemini Flash (cheap, volume) + Gemini Pro (expensive, quality) | DeepSeek (volume) + Claude/GPT (refinement) |
| Evaluation | Custom evaluator per problem | 14-test falsification battery |
| Evolution | Island model with migration | Single population with elitism + immigration |
| Problem definition | Code template + evaluator function | Search function signature + battery |
| Complexity | No explicit cap | 300 AST nodes (was 200, raised after over-engineering) |

**Implementation plan:**
1. Modify `search_evolver.py`:
   - Stage 1: Generate 20 candidates with DeepSeek (cheap, high temperature)
   - Stage 2: Top 5 by battery score get refined by Claude (expensive, low temperature)
   - Stage 3: Refined candidates compete with population
2. Add island model: maintain 3 sub-populations with different fitness emphases:
   - Island A: maximize battery survival
   - Island B: maximize novel failure modes (shadow tensor diversity)
   - Island C: maximize coverage of frontier targets
3. Migration: top individual from each island crosses over every 5 generations

**Data compatibility:** council_client.py already supports DeepSeek, Claude, OpenAI, Gemini. Multi-model routing is plumbing, not research.

**Key difference from AlphaEvolve:** They optimize a single objective function per problem. We optimize a multi-objective: survival × novelty × coverage × parsimony. NSGA-II from our existing Apollo v2 work could handle this.

**Research update (2026-04-09):** OpenEvolve is Apache 2.0, fully open source, ready to install. Architecture: Prompt Sampler → LLM Ensemble → Evaluator Pool → Program Database. Problems defined as two files: initial program with `EVOLVE-BLOCK-START/END` markers (frozen context + mutable code), and evaluator returning a metrics dict. First metric is primary objective. Supports island model with configurable exploitation_ratio (default 0.7). The actionable path: install OpenEvolve, write a thin evaluator wrapper around our battery, mark search functions with EVOLVE-BLOCK markers, configure a DeepSeek/Claude ensemble. The evolutionary loop requires zero modification. Their problem repository has 67 math problems with Colab notebooks — we could benchmark against these.

---

### Strategy 4: Counterexample-Driven Exploration (from Wagner)
**Priority: MEDIUM — conceptual shift, low implementation cost**

| Aspect | Wagner (original) | Our adaptation |
|--------|-------------------|----------------|
| Goal | Find counterexample to conjecture | Find dataset pair where expected bridge is absent |
| Method | Generate random structures, evolve toward near-misses | Generate hypotheses where theory predicts correlation, test for absence |
| Evaluation | Does structure violate conjecture? | Does pair FAIL to show expected pattern? |
| Discovery | Counterexample disproves conjecture | Absence of expected bridge reveals structural independence |

**Implementation plan:**
1. Build `expected_bridges.json`: list of dataset pairs where mathematical theory suggests a connection should exist:
   - EC ↔ MF: modularity theorem (KNOWN — calibration)
   - EC ↔ NumberFields: class field theory (partial)
   - KnotInfo ↔ Genus2: via braids and Jacobians (theoretical, untested)
   - Isogenies ↔ MF: Hecke operators (theoretical, partially tested)
   - OEIS ↔ Fungrim: shared mathematical functions (tested, 16K bridges)
2. For each expected bridge: test whether it survives the battery with FULL structural comparison, not just scalar
3. Expected bridges that FAIL are the interesting results — they reveal where theory and data diverge
4. Evolve toward "almost bridges" — pairs where the correlation is tantalizingly close to significance but can't quite survive

**Data compatibility:** We already have 37+ rediscoveries as the positive calibration set. The counterexample approach inverts the question: where do the known connections break down?

---

### Strategy 5: MCTS Hypothesis Refinement (from IRIS)
**Priority: MEDIUM-LOW — replaces research_cycle architecture, high effort**

| Aspect | IRIS (original) | Our adaptation |
|--------|----------------|----------------|
| Tree nodes | Research hypotheses | (dataset_pair, hypothesis_type, parameters) |
| Branching | LLM generates refinements | LLM proposes parameter variations |
| Reward | LLM Review Agent score | Battery survival rate + surprise |
| Pruning | Low-scoring branches | Branches hitting known kill signatures |
| HITL | User steers exploration | Frontier targets from novelty scorer |

**Implementation plan:**
1. Build `mcts_explorer.py`:
   - Root: dataset pair + broad hypothesis type
   - Children: specific parameter choices (which objects, which normalization, which features)
   - Reward: battery results (pass rate × surprise)
   - Pruning: if 3 children from same branch all die on F1, prune the branch
2. Integrate with shadow tensor: use kill history to avoid re-exploring dead branches
3. Depth limit: 5 levels (pair → type → parameters → normalization → feature selection)

**Data compatibility:** Requires replacing research_cycle.py or running alongside it. High architectural change.

**Deferred because:** Current flat generation produces 18K+ hypotheses. The bottleneck isn't hypothesis quality — it's that the scalar space is exhausted. MCTS becomes valuable when the structural space is rich enough to have meaningful branches. Not yet.

---

## Execution Timeline

| Phase | Strategy | Effort | Dependencies |
|-------|----------|--------|-------------|
| **Week 1** | S1: Operator Graph builder | 3-4 days | OpenWebMath complete (done) |
| **Week 1** | S2: Surprise score in novelty scorer | 1 day | Shadow tensor (done) |
| **Week 2** | S3: Multi-model search evolution | 2-3 days | L4 evolver (done), API keys |
| **Week 2** | S4: Expected bridges list | 1-2 days | Domain knowledge |
| **Week 3** | S1: Formula embedding at scale | 3-5 days | S1 graph builder |
| **Week 3** | S3: Island model evolution | 2-3 days | S3 multi-model |
| **Later** | S5: MCTS hypothesis tree | 5-7 days | Structural space maturity |

---

## Success Metrics

- **S1:** At least 1 cross-domain formula cluster survives battery (structural bridge via operator graph similarity)
- **S2:** Explorer finds results with surprise > 2σ above prediction (the shadow tensor is wrong about something)
- **S3:** Evolved function achieves fitness > 0.5 (currently 0.211) or discovers a novel failure mode
- **S4:** At least 1 expected bridge fails unexpectedly (theory-data divergence identified)
- **S5:** MCTS hypothesis tree explores 3x fewer dead ends than flat generation per discovery

The honest answer on all five may be zero. That's still the strategies working correctly.

---

*Search Strategy Roadmap v1.0 — 2026-04-09*
*Charon, Project Prometheus*
