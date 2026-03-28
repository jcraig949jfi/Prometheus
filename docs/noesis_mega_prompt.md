# Noesis Mega-Prompt — Autonomous 30-Hour Exploration Sprint

*For the Noesis engineer session. This is a self-contained work package. Read it fully before starting.*

---

## Executive Summary (read this first, details below)

**What:** Build and run a continuous tensor-based exploration engine with 25 competing search strategies.

**Starting point:** Operation tensor validated at 555 ops, beating random on quality. Phase 1A/1B done.

**Three phases:**
1. **Load data** (1-2h): Finish embedder, download OEIS, optional organism wraps
2. **Build engine** (2-3h): Daemon + quality scoring + MAP-Elites grid + islands + lineage + watchdog
3. **Run tournament** (14-30h): 25 strategies compete. Adaptive allocation. Abort if nothing beats random after 500 cycles.

**Decision tree:**
- Strategies working? → Keep running, extend to 24-30h
- Nothing beats random after 500 cycles + no improving trends? → Abort, report diagnosis
- TT error > 20%? → Abort, data broke compression

**Sacred rules:** Random baseline never dies. Abort honestly. Checkpoint everything. No LLM in the loop (except Strategy 25, sparingly). Log everything to DuckDB.

**Dream result:** A composition emerges that implements construct-then-check (operation B verifies/revises operation A's output) without being told to look for it.

---

## Current State (from prior session — DO NOT REDO)

The operation tensor is validated at 555 operations. The type compatibility fix and library wrapping are DONE. These results are your starting point:

```
┌──────────────────┬────────────────┬────────────┬──────────────┐
│     Strategy     │ Execution Rate │ Mean Score │ Success Rate │
├──────────────────┼────────────────┼────────────┼──────────────┤
│ Random           │ 20%            │ 0.112      │ 0.469        │
├──────────────────┼────────────────┼────────────┼──────────────┤
│ Random+Types     │ 81%            │ 0.457      │ 0.474        │
├──────────────────┼────────────────┼────────────┼──────────────┤
│ Tensor (concept) │ 9%             │ 0.050      │ 0.419        │
├──────────────────┼────────────────┼────────────┼──────────────┤
│ Tensor+Types     │ 31%            │ 0.146      │ 0.241        │
├──────────────────┼────────────────┼────────────┼──────────────┤
│ OpTensor         │ 80%            │ 0.464      │ 0.502        │
└──────────────────┴────────────────┴────────────┴──────────────┘
```

Key facts:
- **555 operations** across 18 hand-crafted + 474 auto-wrapped organisms
- **88,977 scored chains** (141x more than the 628 we had at 81 operations)
- **OpTensor wins on quality**: 0.464 vs 0.457 mean score, 0.502 vs 0.474 success rate
- The concept-level tensor is confirmed useless for chain selection (9% execution)
- Type awareness is essential (Random 20% → Random+Types 81%)
- The operation tensor matches Random+Types on execution rate and beats it on quality

**What's already done (skip these):**
- Library wrapping (474 auto-wrapped ops) ✓
- Type compatibility matrix ✓
- Operation tensor with 555 ops ✓
- Experiment validation at scale ✓

**What remains from Phase 1:**
- Finish mass embedder (resume from checkpoint 2500, 734 remaining)
- Download and embed OEIS sequences (start with 10K)
- Rosetta Code (if time permits)

## Mission

Build and run Noesis — a continuously running tensor-based exploration engine that searches the space of computable concept compositions at tensor speed. The operation tensor is validated. Now build the loop, run a tournament of search strategies, and deliver results.

**Time budget:** ~30 hours. Abort if no strategy beats random baseline after 500 cycles.

**Autonomy level:** High. Make implementation decisions. If something isn't working, pivot. Document what you tried and why you changed course. The goal is discovering what works, not implementing a spec.

---

## Engineer Q&A (answers to pre-start questions)

1. **Mass embedder:** Run as-is with `--resume`. It has its own blacklist/timeout. If it hangs >30 min, kill and move on. Not blocking.
2. **OEIS download:** Yes, use curl or WebFetch. You have permission. One-time data fetch is fine.
3. **DuckDB:** Create a fresh `organisms/noesis_state.duckdb`. Don't reuse the embedder's DB.
4. **Subprocess isolation:** Full subprocess (`maxtasksperchild=1`). Crash-proof over speed. A segfault at hour 14 is unacceptable.
5. **Strategy count:** Incremental. Build core 6, start the tournament, add strategies while it runs. Don't build all 27 upfront.
6. **pyribs:** MAP-Elites from scratch. Simpler, fewer deps, fits numpy/DuckDB stack. pyribs is reference, not runtime dependency.
7. **Wall-clock:** Internal `time.monotonic()` tracking with self-terminate. Checkpoint and produce final report at hour limit. Don't rely on external kill.

---

## Phase 1: Data Loading (1-2 hours)

**1A and 1B are DONE.** 474 auto-wrapped ops are wired in. Operation tensor has 555 operations. Skip to 1C.

### 1C. Finish mass embedder

Resume from checkpoint 2500 (734 remaining of 2,970). Quick task. If it hangs >30 min, kill and move on.

```
cd f:\Prometheus
python organisms/mass_embedder.py --resume
```

### 1D. Download and embed OEIS sequences

The Online Encyclopedia of Integer Sequences has 390,000+ sequences. Each sequence is a computable function: input n, output a(n).

**Start small:** Download the first 10,000 sequences via the OEIS API or bulk file. Each sequence becomes a callable: `lambda n: sequence_values[n]`. Embed using the universal embedder's probe battery (`organisms/universal_embedder.py`).

**OEIS bulk data:** https://oeis.org/stripped.gz (~30MB) contains all sequences as plaintext. Each line is `A-number, comma-separated values`. Parse this.

**If 10K works and embeds in reasonable time**, scale to 50K, then 100K. Don't try to do all 390K in Phase 1 — validate the pipeline first.

**IMPORTANT: OEIS sequences are lookup tables, not computations.** `lambda n: values[n]` embeds differently from real computational organisms because the behavioral fingerprint reflects the sequence values, not any computational process. When OEIS organisms compose with real operations (FFT, prime sieve), the chain is doing computation on precomputed data, not composing computations. Monitor whether OEIS-involving chains have systematically different quality profiles from pure-computation chains. If OEIS chains dominate the archive because lookup tables never overflow or NaN, that's an artifact, not a discovery.

**Use a distinct semantic type for OEIS outputs:** Tag them as `oeis_integer` or `oeis_scalar`, NOT `integer` or `scalar`. This prevents the type system from blindly piping OEIS lookup outputs into prime sieves or other heavy operations that would create expensive chains running on static data. OEIS outputs should only compose with operations that explicitly accept `oeis_integer` or with a type coercion that's logged as such. Also tag with `source="oeis"` and `sequence_id` in metadata.

**Storage:** Zarr for embeddings (append to existing `embedded_library.zarr`), DuckDB for metadata.

### 1E. Download Rosetta Code algorithms (if time permits)

Rosetta Code has ~1,000 programming tasks with implementations in 50+ languages. The Python implementations are directly wrappable as organisms. Scrape the Python solutions, wrap as operations, embed.

This is lower priority than 1A-1C. Skip if Phase 1 is running long.

### 1F. Optional additional organisms (if time permits)

If these packages are installed, auto-wrap these high-value functions:
- `sympy.simplify`, `sympy.diff`, `sympy.integrate`, `sympy.solve` — symbolic transforms, bridge symbolic ↔ numeric
- `networkx.pagerank`, `networkx.betweenness_centrality`, `networkx.community.louvain_communities` — graph structural descriptors
- `sklearn.decomposition.PCA.fit_transform` — dimensionality reduction (if sklearn installed)
- `pandas.Series.rolling` — windowed statistics (if pandas installed)

These add diversity in transformation types (symbolic, graph-structural, statistical) that the auto-wrapper may have missed. Only do this if they wrap cleanly with the existing type-inference. Don't spend more than 30 minutes.

### Phase 1 verification
After loading, report:
- Total operations in the operation tensor (should be 555+ already, more with OEIS and optional wraps)
- Total embeddings in Zarr (target: 10,000+ after OEIS)
- Tensor build time and TT reconstruction error at new scale
- If reconstruction error exceeds 15%, increase TT rank

---

## Phase 2: Build the Exploration Engine (2-3 hours)

### 2A. The continuous loop daemon

Build `organisms/noesis_daemon.py`:

```python
# Pseudocode — implement properly
while cycles < max_cycles:
    # 1. Select strategy for this cycle
    strategy = tournament.select_strategy()

    # 2. Strategy proposes chains
    chains = strategy.propose(batch_size=100)

    # 3. Execute chains
    results = [execute_chain(chain) for chain in chains]

    # 4. Score results (quality, not just binary success)
    scored = [score_quality(r) for r in results]

    # 5. Record to DuckDB
    db.record(scored, strategy=strategy.name, cycle=cycle)

    # 6. Update exploration map
    exploration_map.update(scored)

    # 7. Update strategy performance
    tournament.update(strategy, scored)

    # 8. Checkpoint every 10 cycles
    if cycle % 10 == 0:
        checkpoint()

    # 9. Abort check
    if tournament.should_abort():
        break

    cycle += 1
```

**CLI:**
```
python organisms/noesis_daemon.py --hours 30 --batch-size 100
python organisms/noesis_daemon.py --resume  # Continue from checkpoint
python organisms/noesis_daemon.py --report  # Print results without running
```

**Crash safety:** Checkpoint to DuckDB every 10 cycles. On restart, detect existing state and resume. Windows may reboot for updates.

**Memory leak protection (CRITICAL for 20-hour runs):** Running hundreds of math libraries (sympy, networkx, scipy) in a continuous loop WILL accumulate memory leaks. Isolate `execute_chain()` calls in a `multiprocessing.Pool` with `maxtasksperchild=1`. Each chain execution gets a fresh subprocess that dies after one task. If a sympy calculus operation hangs or leaks, the child process dies instead of taking down the daemon. Monitor RSS memory of the main process every 50 cycles — if it exceeds 80% of available RAM, force a garbage collection cycle (`gc.collect()`) and log a warning. If it exceeds 90%, graceful checkpoint and restart.

**Real-time crack logging:** When a chain exceeds quality > 0.5, immediately append its details to `organisms/cracks_live.jsonl` (one JSON object per line). Include the full sub-chain structure (each operation with organism name, operation name, input type, output type) so we can grep for "construct → check" patterns later without digging through DuckDB. Don't wait for the final report.

**Degenerate loop detection:** If a strategy proposes the same chain (by operation set hash) more than 3 times in 50 cycles, blacklist that chain for that strategy. If a strategy's proposal uniqueness drops below 50% (more than half its proposals are duplicates), force it into exploration mode for 20 cycles. This prevents strategies from getting stuck in a loop proposing the same chains.

### 2B. Quality scoring

Every executed chain gets a quality score, not just pass/fail:

1. **Execution score** (0 or 1): Did it run without crashing, NaN, Inf, or enormous output?
2. **Novelty score** (0-1): Embed the output using the universal embedder. Compute cosine distance from all previously seen outputs. High distance = high novelty.
3. **Structure score** (0-1): Output dimensionality / input dimensionality. Chains that preserve or increase structure beat chains that collapse to scalar.
4. **Diversity score** (0-1): How different is this chain's organism set from recently tested chains? Penalize testing the same organism pairs repeatedly.

5. **Compression gain** (0-1): Does the chain simplify representation? `compression = max(0, (input_entropy - output_entropy) / input_entropy)` where entropy is computed via `zlib.compress()` length as proxy. Chains that discover structure (reduce entropy) score high. Chains that add noise (increase entropy) score zero. This directly measures whether a composition found a simplification — the core signal for search acceleration.
6. **Cheapness penalty** (0-1, subtracted): Detects trivial compositions. Heuristics: constant-time outputs (no dependence on input variation), lookup-table behavior (output doesn't change with input perturbation), zero transformation depth. `cheapness = 0.5 * constant_output + 0.3 * low_input_sensitivity + 0.2 * zero_compute_depth`. This prevents OEIS lookup tables and identity-like operations from dominating the archive.
7. **Dead-end penalty** (0-1, subtracted): If the output type can't feed into ANY other operation in the library, the chain produces a "dead end" — its output can't be used in further compositions. Penalize dead-end outputs because they don't contribute to building longer chains. `dead_end = 1.0 if output_type has zero compatible downstream operations, else 0.0`. This rewards "fertile" outputs that enable further composition.

**Combined:** `quality = 0.25 * execution + 0.25 * novelty + 0.15 * structure + 0.15 * diversity + 0.15 * compression - 0.05 * cheapness - 0.05 * dead_end`

**Note on weights:** These are initial guesses, not gospel. Execution is binary (0 or 1) while the others are continuous (0-1), so execution dominates in practice — any non-executing chain caps at ~0.35 max quality. That's probably correct (non-executing chains SHOULD score low), but check: if the quality distribution is degenerate (all scores clustered near 0.3 or 0.7 with nothing in between), adjust weights to spread the distribution. The goal is meaningful discrimination between compositions, not a specific score range. You have autonomy to change these.

**Dynamic execution weight:** Once the archive's overall execution baseline surpasses 50% success rate, scale the execution weight down from 0.25 to 0.10. At that point, most chains execute — execution is no longer the discriminating signal. The continuous scores (novelty, compression, structure) should dominate the ranking to prevent strategies from gaming the system with "does nothing but passes type checks" chains.

A "crack" is a chain with quality > 0.5.

### 2C. MAP-Elites grid

Implement a behavioral descriptor grid (inspired by OpenELM/pyribs). Each composition gets mapped to a cell based on:

- **Axis 1:** Chain length (2, 3, 4, 5 operations)
- **Axis 2:** Output complexity (scalar=0, array=1, matrix=2, structure=3)
- **Axis 3:** Organism diversity (how many different organisms in the chain / chain length)

Grid shape: 4 × 4 × 4 = 64 cells. Each cell holds the highest-quality composition for that behavioral niche. The grid maintains diversity by design — you can't fill a cell by being good at a different niche.

**QD score** = sum of all filled cell qualities. This is the metric that measures overall exploration progress.

### 2D. Island architecture

Implement 4 islands (inspired by FunSearch/OpenEvolve):

- Each island runs its own search strategy
- Each island maintains its own MAP-Elites grid
- Every 50 cycles: migrate the best composition from the strongest island to the weakest
- Every 200 cycles: if an island's velocity (cracks/cycle) is zero, reset it and reseed from the strongest island's top 5 compositions

### 2E. Lineage tracking

Every composition records in DuckDB:
- `chain_id`: unique identifier
- `parent_id`: if derived from mutation/crossover of a prior chain (NULL for de novo)
- `strategy`: which search strategy produced it
- `island`: which island
- `cycle`: when
- `quality`: combined score
- `organisms`: which organisms involved
- `output_hash`: for dedup
- `failure_mode`: if failed — type_error, overflow, nan, timeout, empty_output (classified)

This enables post-hoc analysis: which strategies produce the deepest lineage trees? Which organisms appear most in successful lineages?

**Compositional reuse tracking:** After every 100 cycles, scan successful chains for shared sub-chains. If operation pair (A→B) appears in 5+ high-quality chains, it's a **building block** — a proto-algorithm that other compositions reuse. Track reuse counts per operation pair. High-reuse pairs are the most valuable discoveries because they're compositional primitives, not one-off successes. Report the top 20 most-reused sub-chains in the final deliverable.

### Phase 2 verification
- Run the daemon for 10 cycles with 2 strategies (random baseline + tensor top-K)
- Verify: DuckDB has records, MAP-Elites grid has entries, lineage table populated
- Verify: checkpoint saves and resumes correctly
- Verify: quality scores distribute reasonably (not all 0 or all 1)

---

## Phase 3: Strategy Tournament (14+ hours)

### The Strategies

Implement as many of these as time allows. At minimum: strategies 1-6. Strategies 7-12 are high-value extensions. Strategies 13-18 are advanced — implement if the basics are working and time permits.

**Recommended implementation order:** 1 (control), 2 (tensor baseline), 3 (frontier), 5 (epsilon-greedy), 6 (temperature anneal), 8 (failure geometry), 13 (curiosity), 14 (NSLC), 17 (surprise admission). These give the best coverage of the strategy hierarchy with minimum implementation effort. Add 7 (islands), 12 (resets), 15 (CMA-ME), 16 (differential evolution) if the basics are producing results.

#### Strategy 1: Random Baseline (CONTROL)
Uniform random sampling of type-compatible operation pairs. No tensor guidance. This is the floor — every other strategy must beat this or it's useless.

#### Strategy 2: Tensor Top-K
Score all operation pairs using the operation tensor's combined score (novelty × complementarity × resonance × type_compatibility). Take the top-K. Execute. This is the current approach that showed 37% vs 25%.

#### Strategy 3: Frontier Seeking
Maintain an exploration map of tested operation pairs. Score = tensor_score × (1 - exploration_density). Heavily favor operation pairs in unexplored regions of the tensor. Go where nobody's been.

#### Strategy 4: Framed Traversal (5 sub-strategies)
Apply 5 bias vectors to the operation feature matrix before scoring:
- **Unbiased**: weights = 1.0 everywhere (same as Strategy 2)
- **Devil's advocate**: boost falsifiability, surprise; suppress determinism, stability
- **Occam**: boost compression, computability; suppress emergence, cross_domain
- **Boundary**: boost boundary_sensitivity, robustness; suppress abstraction
- **Efficiency**: boost compression, parallelism, optimization; suppress emergence

Each frame is a sub-strategy that gets its own performance tracking. Rotate through frames or allocate based on performance.

#### Strategy 5: Exploit/Explore (Epsilon-Greedy)
80% of the time: use tensor top-K (exploit known good regions). 20% of the time: random sampling (explore unknown regions). Simple but effective baseline for balancing exploration and exploitation.

#### Strategy 6: Temperature-Annealed Cluster Selection (from FunSearch)
1. Cluster all operations by embedding similarity (k-means, k=20 clusters)
2. Score each cluster by the mean quality of compositions involving its members
3. Apply softmax with temperature: `P(cluster) = softmax(cluster_scores / T)`
4. Temperature starts high (T=2.0, explore) and anneals down (T=0.5, exploit) over a period
5. Periodically reset temperature to escape local optima (reset every 200 cycles)

Sample from selected cluster, then form chains with operations from other clusters (cross-cluster composition).

#### Strategy 7: Island-MAP-Elites Hybrid (from OpenEvolve)
Each island has:
- Its own MAP-Elites grid (4×4×4)
- Its own search bias (one island explores long chains, one explores high-diversity chains, one explores novel outputs, one exploits known-good regions)
- Migration every 50 cycles: best composition from strongest island copies to weakest
- Reset every 200 cycles if velocity = 0

#### Strategy 8: Failure-Geometry Guided (from CodeEvolve)
Track failure modes per tensor region:
- Type errors → the operation pair can't connect (skip future attempts)
- Overflow → the combination amplifies (try with smaller inputs or different operations from same organisms)
- NaN → numerical instability at domain boundary (interesting — flag for analysis)
- Timeout → computation explodes (cap and move on)
- Empty output → chain produces nothing (skip)

Use failure patterns to adjust search: boost regions with interesting failures (NaN at domain boundaries), suppress regions with boring failures (type errors).

#### Strategy 9: Novelty Seeking (from OpenELM behavioral descriptors)
Score = embedding distance of output from ALL previously seen outputs. Completely ignores tensor scores. Purely chases novel outputs. This tests whether novelty alone is a good fitness signal.

#### Strategy 10: Longest Chain Explorer
Focus on chains of length 3, 4, 5+ operations. Standard strategies favor 2-operation chains because they're most likely to execute. This strategy specifically targets deeper compositions. Higher failure rate but potentially richer discoveries.

#### Strategy 11: Bridge Building
1. Cluster all operations into behavioral groups using embeddings
2. Identify the most distant cluster pairs (highest embedding distance between centroids)
3. Search for chains that START in one cluster and END in another
4. These are cross-domain bridges — the compositions that connect distant fields

#### Strategy 12: Periodic Island Reset (from FunSearch)
Run 4 islands with different strategies. Every 100 cycles:
- Rank islands by QD score (sum of MAP-Elites grid qualities)
- Bottom 2 islands: wipe their grids, reseed with top 10 compositions from top 2 islands
- Top 2 islands: continue undisturbed
- This creates a generational bottleneck that eliminates weak strategies

#### Strategy 13: Curiosity-Driven Exploration (from Go-Explore / intrinsic motivation)
Score = tensor_score + curiosity_bonus, where curiosity_bonus = inverse of visit density in behavioral descriptor space. The exploration map already tracks which tensor regions have been visited. Compositions that open up NEW regions of the behavioral space are rewarded even if their immediate output is mediocre — because they expand the frontier.

This directly implements the "search for acceleration" principle: a mediocre composition that unlocks an unexplored region is more valuable than a good composition in a saturated region.

Implementation: maintain a visit count per MAP-Elites cell. `curiosity_bonus = 1.0 / (1 + visit_count[cell])`. Add to tensor score before selection.

#### Strategy 14: Novelty Search with Local Competition (from NSLC / Lehman & Stanley)
Pure novelty search (Strategy 9) ignores quality. NSLC combines both: within a behavioral neighborhood, compete on quality; across neighborhoods, reward novelty.

Implementation:
1. For each new composition, find its K nearest neighbors in embedding space
2. Novelty = mean distance to K neighbors
3. Local quality rank = rank of this composition's quality among its K neighbors
4. NSLC score = 0.5 * novelty + 0.5 * (1 - local_rank / K)

This prevents the archive from collapsing to a single high-quality region while maintaining quality pressure within each region.

#### Strategy 15: CMA-ME (Covariance Matrix Adaptation MAP-Elites)
Adapt CMA-ES (already used in Ignis) to MAP-Elites. Instead of random mutations, the emitter learns the covariance structure of successful mutations per niche and proposes new candidates along the learned directions.

Powerful for Noesis because tensor features have correlated structure — concepts similar in one dimension tend to be similar in others. CMA-ME learns those correlations and exploits them for directed search.

Implementation: Use the CMA-ES from `evosax` or `EvoTorch` (both in vault/repos). Each MAP-Elites cell with enough history gets its own covariance matrix. New proposals are sampled from the learned distribution. Cells with too few samples fall back to isotropic mutation.

This is heavier to implement. Skip if time is short — it's most valuable at higher density (500+ operations).

#### Strategy 16: Differential Evolution
Takes three existing compositions from the archive:
1. Compute a difference vector between compositions A and B (in operation feature space)
2. Add the weighted difference to composition C: `D = C + F * (A - B)` where F ∈ [0.5, 1.0]
3. Map the resulting feature vector to the nearest actual operations
4. Execute the derived chain

This implicitly learns the geometry of the successful region — the difference vector captures "what makes A different from B" and applies that transformation to C. It's analogical reasoning applied to the search process.

Implementation: Represent each chain as a concatenation of its operations' feature vectors. Compute differences in feature space. Find nearest real operations to the perturbed vector via cosine similarity.

#### Strategy 17: Surprise-Based Archive Admission (from AURORA)
Train a simple predictor (linear regression or small MLP) that maps tensor features to expected behavioral descriptors (output type, dimensionality, execution time, etc.). Compositions that VIOLATE the prediction get admitted to the archive because they reveal structure the model doesn't yet understand.

This is FEP applied to the search process — minimize surprise about the search space by seeking out compositions that surprise you most. The predictor improves as more compositions are tested, so what counts as "surprising" evolves over time. Early on, everything is surprising. Later, only genuinely novel structure triggers admission.

Implementation:
1. After every 100 compositions, retrain the predictor on (features → behavioral descriptors)
2. For each new composition, predict its behavioral descriptor
3. Surprise = L2 distance between predicted and actual descriptor
4. If surprise > threshold: admit to archive regardless of quality
5. Threshold anneals upward as the predictor improves

**Cold-start provision:** Don't activate surprise-based admission until the predictor has been trained on 500+ compositions and achieves R² > 0.3 on a holdout set. Before that threshold, the predictor is garbage and everything looks "surprising" — the archive would fill with random noise. Fall back to quality-based admission during cold start.

**This strategy is architecturally important.** It closes the recursive loop described in Layer 4 of the Noesis doc — the system learns a model of its own search space and then deliberately violates that model to discover what it doesn't know yet. Surprise minimization about the search space, applied to the search process itself.

#### Strategy 18: Two-Step Validation Search (targeting the dream result)
Explicitly search for construct-then-check compositions:
1. Take a high-scoring single-operation result (the "construct" step)
2. Search for a second operation that, when applied to the first's output, IMPROVES it: reduces entropy, stabilizes variance, filters noise, or corrects errors
3. Score bonus if the two-step chain outperforms the single step on quality metrics

Implementation: for each top-50 single-operation result, try all type-compatible second operations. Score the pair. If pair > single by >10%, that's a construct-check chain.

**This directly targets the dream result.** If the search independently discovers that verification/revision operations improve construction operations, it has rediscovered the forge survivor architecture without any knowledge of the ejection circuit or the convergence theory.

#### Strategy 19: Mutation of Successful Chains (local optimization)
Take the highest-quality chain from the archive. Randomly replace ONE operation with a type-compatible alternative (from the same organism family or from a random organism). Execute the mutated chain. If it scores higher, it replaces the parent in the archive.

This is simple local hill-climbing. It complements the global strategies (frontier, novelty, curiosity) by refining what's already working. Low implementation cost, often surprisingly effective.

Variant: replace one operation with the nearest neighbor in embedding space (similar behavior, slightly different). This produces small perturbations that explore the neighborhood of known-good chains.

#### Strategy 20: Chain-Length Annealing
Start by focusing on length-2 chains (highest success rate). Gradually increase the proportion of length-3, 4, 5 as the MAP-Elites grid fills.

Annealing schedule tied to QD score:
- QD < 10 filled cells: 80% length-2, 20% length-3
- QD 10-30: 50% length-2, 30% length-3, 20% length-4
- QD > 30: 30% length-2, 30% length-3, 25% length-4, 15% length-5

This ensures the archive builds a solid foundation of short, reliable chains before attempting deeper compositions that are more likely to fail.

#### Strategy 21: Building-Block Reuse Emitter (tests the meta-observation)
Every 50 cycles, scan DuckDB for the top-20 most-reused sub-chains (from the reuse tracking). Treat each high-reuse PAIR (A→B) as a single "super-organism" and force it into new chains as the first two steps. Then append a third operation from the general pool.

This is literally "exploit the discovered primitives" at the strategy level. If the system has found that (entropy → filter) is a building block, this strategy asks: "what ELSE can we do after entropy → filter?" It's the tournament version of the construct-then-check dream — building on what works.

Only activate after 200+ cycles when there's enough reuse data to be meaningful.

#### Strategy 22: Failure-as-Feature Surprise Emitter (mining domain boundaries)
For NaN/overflow/timeout failures (the INTERESTING ones, not type errors), create a temporary mutation pool of the failing operations. For the next 10 proposals, sample ONLY from that pool but with perturbed input distributions (scale inputs by 0.1× to 10×).

This turns domain-boundary explosions into deliberate exploration. An overflow at the boundary between chaos theory and signal processing might become a valid result at a different scale. Costs almost nothing and directly tests whether the system can mine signal from failures.

#### Strategy 23: Cross-Organism-Family Bridge Emitter
At startup, precompute the 18 organism families' centroid embeddings. Every cycle, identify the most distant pair of families that still have zero high-quality chains between them. Bias 20% of proposals toward cross-family chains connecting those two families.

Pure "force the cross-domain bet." Trivial to implement with the existing embedding code. The tensor already knows which families are distant — this strategy explicitly targets the gaps.

#### Strategy 24: Archive Hall-of-Fame Local Search
Maintain a fixed-size (50) elite archive of the highest-quality chains ever seen. Each cycle, pick one at random, replace exactly one operation with its nearest neighbor in embedding space (or same organism family). Propose the mutant.

Simplest possible "refine what already works." Like Strategy 19 (mutation) but with a global elite list. Often outperforms fancy strategies in early regimes when the archive is sparse.

#### Strategy 25: Autoencoder Bottleneck Search (discover algorithmic compression)
Search for chains of length 3 that follow a strict dimensionality pattern: High → Low → High. The first operation reduces dimensionality (matrix → scalar, array → scalar). The second transforms the compressed representation. The third expands back (scalar → array, scalar → matrix).

Score a massive bonus if the final output closely reconstructs the initial input after passing through the low-dimensional bottleneck. If the system finds this, it has discovered an algorithmic autoencoder — a composition that compresses and reconstructs through a bottleneck, preserving structure.

Implementation: filter for chains where dim(output_1) < dim(input_1) AND dim(output_3) ≈ dim(input_1). Reconstruction quality = 1 - normalized_distance(input_1, output_3).

#### Strategy 26: Type-Coercion Bridge Search (cross invalid boundaries)
Take a high-quality chain, but intentionally break ONE type compatibility constraint (e.g., force a matrix into an operation expecting a probability distribution). Then search for a SINGLE intermediary operation that bridges that specific type mismatch — an operation that accepts the "wrong" type and produces the "right" type.

This turns type failures into explicit search targets. If a bridge is found, it reveals a hidden connection between domains that the type system declared incompatible. These are the compositions that surprise experts.

Implementation: for each type-incompatible pair with high tensor score, enumerate all operations that could bridge (accept type A, produce type B). Test the three-step chain: op_A → bridge → op_B.

**Implementation note:** Strategies 21-26 are late-game optimizations. Implement them AFTER the core strategies (1-6) + MAP-Elites + islands are rock-solid and running. They're only valuable once the archive already has signal. If the tournament is still basically random after 500 cycles, these won't save it.

#### Strategy 27: Inspiration Crossover (from CodeEvolve — requires LLM)
Take 2-3 high-quality chains. Present them to an LLM: "These chains work well. Chain A does entropy→filter. Chain B does prime→autocorrelation. Propose a new chain that combines their strengths." Execute the LLM's suggestion.

**This is the ONLY strategy that uses an LLM.** It's expensive (API call per attempt). Run it sparingly — only on the top 10 compositions, once per 100 cycles. The LLM sits outside the loop.

**API configuration:**
- Credentials are in `agents/eos/.env` — load with `dotenv` or read directly
- Key: `NVIDIA_API_KEY` environment variable
- Endpoint: `NVIDIA_API_ENDPOINT` (https://integrate.api.nvidia.com/v1) — OpenAI-compatible
- Model: `NVIDIA_MODEL` (nvidia/nemotron-3-super-120b-a12b — 120B, free tier)
- Use `openai.OpenAI(base_url=endpoint, api_key=key)` — standard OpenAI SDK works
- See `agents/nous/src/nous.py` line 297+ for working call pattern with exponential backoff on rate limits
- **Rate limit discipline:** NVIDIA throttles agentic access. Max 1 call per 10 seconds. If rate-limited, back off exponentially. Do NOT hammer the API.

If the API is unavailable or rate-limited to uselessness, skip this strategy entirely. The other 26 strategies don't need it.

### Architectural Note: Ask-Tell Emitter Pattern

The core design constraint is that the exploration loop runs at tensor speed with no LLM blocking. Use the **ask-tell pattern** from pyribs (`vault/repos/pyribs/`):

- **Emitters** propose chains using different strategies (some tensor-guided, some random, some mutation-based)
- **Evaluator** executes and scores chains
- **Scheduler** collects results, updates the shared archive, reallocates emitter budgets

This decouples proposal from evaluation. Emitters write proposed chains, the evaluation loop reads and scores them, results update the tensor state. No blocking, no synchronization bottleneck. Each strategy is an emitter. The tournament scheduler manages them.

If implementing full ask-tell is too heavy, a simple round-robin over strategy objects works for the prototype. But the ask-tell pattern is the right long-term architecture.

### The Meta-Observation

Every strategy in this tournament implements construct-then-check at the meta level:
- Emitters CONSTRUCT candidate chains
- The evaluator CHECKS them against quality and diversity criteria
- The tournament CONSTRUCTS search strategies (via allocation)
- Lineage tracing CHECKS whether strategies are generative

This is the same invariant that appeared in the forge survivors, the ejection circuit analysis, and the Noesis framing mechanism. It's construct-then-check all the way down. If the tournament produces a strategy that itself implements construct-then-check at the composition level, that's the recursive discovery described in the "dream result" section below.

### Tournament Mechanics

**Allocation:** Each strategy starts with equal allocation (100 chains / N strategies per cycle). After every 50 cycles, reallocate:
- Strategies with cracks/cycle > 2× average: double their allocation
- Strategies with cracks/cycle < 0.5× average: halve their allocation
- Strategies with zero cracks after 300 cycles AND no improving trend: kill them, redistribute to winners
- Random baseline always keeps its allocation (it's the control)

**Logging:** Every cycle, log to DuckDB:
```sql
INSERT INTO tournament_log (cycle, strategy, chains_tested, chains_executed,
    cracks, mean_quality, max_quality, qd_score, wall_time_ms, strategy_dna)
```

The `strategy_dna` column stores a JSON blob of the emitter's current hyperparameters (temperature, exploration ratio, mutation rate, target chain length, etc.). This enables post-hoc analysis: "which temperature schedule produced the highest QD acceleration?" and potentially evolving the strategies themselves in a second pass.

**Sub-score histograms:** Every 50 cycles, log the distribution of each quality sub-score (execution, novelty, structure, diversity, compression, cheapness, dead_end) across all chains tested in that window. This reveals whether execution is still dominating or whether the continuous scores are actually spreading the distribution. If all 7 sub-scores cluster near the same value, the weights need adjustment.

**Abort conditions:**
- NO strategy beats random baseline after 500 cycles **AND** no strategy shows a monotonically improving trend over its last 200 cycles → ABORT, report. (Some strategies invest early and pay off late — temperature annealing needs a full anneal cycle, CMA-ME needs history to learn covariance. A strategy that's losing to random but getting better every 50 cycles deserves more time.)
- Total cracks across ALL strategies is zero after 1000 chains tested → ABORT, report
- TT reconstruction error exceeds 20% after data loading → ABORT, report (data is breaking compression)
- Wall-clock time exceeds 20 hours → see "what to do if everything works" below

**What to do if everything works:**
If the tournament is actively producing cracks at hour 18, **extend to 24 hours** before final report. If strategies are still differentiating (no clear winner yet but multiple strategies improving), **extend to 30 hours**. Document the decision and why you extended. The worst outcome is prematurely terminating a productive run — checkpoint and continue is always better than checkpoint and stop if there's signal.

**Checkpoint:** Every 50 cycles, save full state:
- Tournament allocations and performance history
- All MAP-Elites grids (per island if using islands)
- Exploration map
- DuckDB is the checkpoint (it's transactional)
- On resume: reload tournament state, continue from last cycle

### Phase 3 verification (continuous)
Every 100 cycles, print a status line:
```
[Cycle 300] Best: temperature_anneal (0.47 cracks/cycle) | Worst: longest_chain (0.02) | QD: 23/64 cells | Total cracks: 142 | Random baseline: 0.15 cracks/cycle
```

---

## Deliverables

After the run completes (or aborts), produce a report at `organisms/noesis_tournament_report.json`:

```json
{
  "run_metadata": {
    "start_time": "...",
    "end_time": "...",
    "total_cycles": 1234,
    "total_chains_tested": 123400,
    "abort_reason": null
  },
  "data_loading": {
    "operations_in_tensor": 555,
    "oeis_sequences_embedded": 10000,
    "tt_rank": 10,
    "tt_reconstruction_error": 0.089,
    "tensor_build_time_s": 0.5
  },
  "strategy_leaderboard": [
    {
      "name": "temperature_anneal",
      "total_cracks": 142,
      "cracks_per_cycle": 0.47,
      "mean_quality": 0.62,
      "execution_rate": 0.41,
      "unique_outputs": 89,
      "final_allocation_pct": 25
    }
  ],
  "map_elites": {
    "cells_filled": 23,
    "total_cells": 64,
    "qd_score": 14.7,
    "best_cell": {"coords": [2,3,1], "quality": 0.89, "chain": "..."}
  },
  "top_50_compositions": [...],
  "failure_geometry": {
    "type_error": {"count": 4500, "hot_regions": [...]},
    "overflow": {"count": 890, "hot_regions": [...]},
    "nan": {"count": 234, "hot_regions": [...]},
    "timeout": {"count": 56, "hot_regions": [...]}
  },
  "density_report": {
    "pre_loading_ops": 81,
    "post_loading_ops": 555,
    "cracks_per_op_pre": 0.12,
    "cracks_per_op_post": 0.08,
    "did_density_help": true
  },
  "lineage": {
    "deepest_tree_depth": 5,
    "most_productive_strategy": "frontier_seeking",
    "most_productive_organism_pair": ["signal_processing", "prime_theory"]
  },
  "recommendation": "temperature_anneal with island resets"
}
```

Also produce a human-readable summary at `organisms/noesis_tournament_summary.md`.

---

## Key Files to Read First

Before starting, read these to understand the existing system:

| File | What It Contains |
|------|-----------------|
| `docs/continuous_exploration_loop.md` | Full Noesis architecture, experimental results, challenges |
| `docs/unified_theory_convergence.md` | Why this work matters — the convergence theory |
| `organisms/base.py` | MathematicalOrganism base class — `.execute(op_name, input)` |
| `organisms/__init__.py` | `ALL_ORGANISMS` list (18 organisms) |
| `organisms/concept_tensor.py` | 95 concepts × 30D features, scoring functions |
| `organisms/tensor_navigator.py` | TT decomposition, top-K, diversity cap, reconstruction diagnostics |
| `organisms/universal_embedder.py` | 240D behavioral fingerprinting |
| `organisms/experiment_tensor_vs_random.py` | The experiment that proved operation tensor > concept tensor |
| `organisms/generated/` | 474 auto-wrapped library operations |
| `organisms/mass_embedder.py` | Mass embedding pipeline with checkpoint/resume |

---

## Critical Rules

1. **No LLM in the main loop.** The exploration loop is pure tensor + execution. The only exception is Strategy 13 (Inspiration Crossover), which calls the LLM sparingly and outside the loop.

2. **No Coeus/Nous data in the tensor.** The feature matrix comes from `get_feature_matrix()` only. Exploration map is populated by real composition outcomes, not Nous hypotheses. The tensor was recently decontaminated — don't re-contaminate it.

3. **All organisms use `.execute(op_name, input)`** to run operations. Not `.get_operation()`.

4. **Use semantic types**, not Python types. `probability_distribution`, `scalar`, `array`, `matrix`, `integer`, `adjacency_matrix`, `graph`.

5. **Checkpoint everything.** Windows may reboot. The daemon must resume cleanly.

6. **Random baseline is sacred.** Never remove it. Every strategy is measured against it. If nothing beats random, that's the result — don't hide it.

7. **Abort honestly.** If the tournament isn't producing cracks, stop and report. 20 hours of zero-result cycling is worse than a 2-hour abort with a clear diagnosis.

8. **Log everything to DuckDB.** Every chain tested, every score, every failure mode, every strategy allocation change. The analysis is as valuable as the discoveries.

---

## What Success Looks Like

**Minimum viable result:** At least one strategy consistently beats random baseline by >20% on cracks per cycle, with statistical confidence (100+ cycles for both).

**Good result:** 3+ strategies beat random. MAP-Elites grid has 20+ filled cells. Top compositions include cross-domain chains (operations from different organism families). Failure geometry reveals actionable patterns.

**Great result:** The tournament self-organizes — adaptive allocation concentrates on winning strategies, island resets prune losers, QD score grows monotonically. The system discovered a composition that surprises us (we didn't predict it from the tensor scores). Lineage analysis shows multi-generation improvement (children of good chains are better than their parents).

**The dream:** A composition emerges that implements construct-then-check — two operations where the second verifies or revises the first's output. This would be the tensor engine independently rediscovering the architecture that the forge survivors require. If that happens, capture it carefully. It's the most important result in the project.
