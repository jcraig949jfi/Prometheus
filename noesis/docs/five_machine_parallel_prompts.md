# ═══════════════════════════════════════════════════════════════════════
# MACHINE 1: HUB MINING — Layer 2 Expansion
# Target: 34 → 100+ impossibility hubs
# ═══════════════════════════════════════════════════════════════════════

## Context

You are expanding a structural analysis database that maps how civilizations respond to mathematical impossibility. Every proven impossibility theorem is a "hub" — a row in a matrix where columns are damage operators (how the impossibility gets resolved). The database currently has 34 hubs. Your job is to find more.

### The 11 Primitives
```
MAP, COMPOSE, REDUCE, EXTEND, COMPLETE, LIMIT,
SYMMETRIZE, BREAK_SYMMETRY, DUALIZE, LINEARIZE, STOCHASTICIZE
```

### The 9 Damage Operators
| Operator | Meaning | Primitive Form |
|----------|---------|----------------|
| DISTRIBUTE | Spread error evenly | SYMMETRIZE |
| CONCENTRATE | Localize error | BREAK_SYMMETRY |
| TRUNCATE | Remove problematic region | REDUCE |
| EXPAND | Add structure/resources | EXTEND |
| RANDOMIZE | Convert error → probability | STOCHASTICIZE |
| HIERARCHIZE | Move failure up a level | DUALIZE + EXTEND |
| PARTITION | Split domain | BREAK_SYMMETRY + COMPOSE |
| QUANTIZE | Force continuous onto discrete grid | MAP + TRUNCATE |
| INVERT | Reverse structural direction | DUALIZE + MAP |

### Current Hub Inventory (34 hubs — DO NOT DUPLICATE)
```
FORCED_SYMMETRY_BREAK, BINARY_DECOMP_RECOMP, CROSS_DOMAIN_DUALITY,
PHYSICAL_SYMMETRY_CONSTRUCTION, RECURSIVE_SELF_SIMILAR,
CALENDAR_INCOMMENSURABILITY, ARROW_SOCIAL_CHOICE, GODEL_INCOMPLETENESS,
HEISENBERG_UNCERTAINTY, CAP_THEOREM, MAP_PROJECTION,
HALTING_PROBLEM, SHANNON_CAPACITY, NYQUIST_LIMIT, CARNOT_LIMIT,
BODE_SENSITIVITY, NO_CLONING_THEOREM, CRYSTALLOGRAPHIC_RESTRICTION,
FITTS_HICK_SPEED_ACCURACY, IMPOSSIBLE_TRINITY,
QUINTIC_INSOLVABILITY, HAIRY_BALL_THEOREM, RUNGE_PHENOMENON,
SEN_LIBERAL_PARADOX, GIBBARD_SATTERTHWAITE,
GOODHART_LAW, FOUNDATIONAL_IMPOSSIBILITY, BORSUK_ULAM,
NO_FREE_LUNCH, BIAS_VARIANCE_TRADEOFF, MYERSON_SATTERTHWAITE,
RICE_THEOREM, AMDAHL_LAW, LANDAUER_PRINCIPLE
```

## Task

Survey the following fields SYSTEMATICALLY and return every proven impossibility result that is NOT already in the database. Each field gets its own sweep. Return results in batches.

### Field Sweep Schedule

**Batch 1: Topology & Geometry**
- Fixed-point theorems (Brouwer, Kakutani, Lefschetz) and their impossibility corollaries
- Covering space obstructions
- Knot invariant limits
- Dimension-theoretic impossibilities (embedding theorems, Whitney)
- Topological obstructions to vector fields beyond hairy ball
- Deformation/rigidity theorems

**Batch 2: Complexity Theory**
- Oracle separation results (BGS, relativization barriers)
- Natural proofs barrier (Razborov-Rudich)
- Algebrization barrier
- Communication complexity lower bounds
- Circuit lower bounds
- PCP theorem as impossibility
- Unique games conjecture (if sufficiently proven)

**Batch 3: Game Theory & Mechanism Design**
- Nash equilibrium computation hardness (PPAD-completeness)
- Revenue maximization impossibilities (Myerson already present — find others)
- Mechanism design without money impossibilities
- Stable matching impossibilities
- Fair division impossibilities (envy-free + efficient + truthful)
- Auction theory impossibilities

**Batch 4: Quantum Information**
- No-broadcasting theorem
- No-deleting theorem
- Quantum speed limits (Margolus-Levitin)
- Holevo bound
- Tsirelson's bound
- Quantum error correction thresholds
- Monogamy of entanglement

**Batch 5: Analysis & Approximation Theory**
- Banach-Tarski (already related to Borsuk-Ulam — find distinct impossibility)
- Weierstrass approximation limits for non-continuous functions
- Kolmogorov superposition theorem and its limitations
- Impossibility of dimension-independent approximation rates
- Gibbs phenomenon (check if already present)
- Divergence of Fourier series for continuous functions

**Batch 6: Biology & Complex Systems (FORMAL PROOFS ONLY)**
- Price equation constraints
- Fisher's fundamental theorem limits
- Fitness landscape constraints (NK model)
- Metabolic rate tradeoffs with formal bounds
- Neural coding impossibilities (rate vs temporal codes)
- Evolutionary constraints on modularity

**Batch 7: Control Theory & Signal Processing**
- Bode gain-phase relation (distinct from sensitivity integral?)
- Fundamental limitations in estimation (Cramér-Rao bound)
- Kalman filter optimality conditions as impossibility
- Robust control impossibilities beyond Bode
- Channel coding converse theorems

**Batch 8: Economics & Social Science**
- Impossibility of rational expectations + efficiency (Grossman-Stiglitz)
- Diamond-Dybvig bank run impossibility
- Coase theorem limitations
- Phillips curve impossibility (long-run)
- Condorcet jury theorem limitations
- Welfare theorems' impossibility conditions

## Output Schema

For each new hub:

```json
{
  "hub_id": "UNIQUE_SNAKE_CASE",
  "hub_name": "Human-readable name",
  "domain": "Primary field",
  "impossibility_statement": "Precise statement of what cannot be simultaneously achieved",
  "formal_source": "The theorem/proof with attribution and year",
  "desired_properties": ["List of properties the system wants simultaneously"],
  "structural_pattern": "COMPOSE(X) → COMPLETE(Y) FAILS → BREAK_SYMMETRY(Z)",
  "why_closure_fails": "The specific mathematical reason COMPLETE fails",
  "known_resolution_count": 0,
  "connection_to_existing_hubs": ["IDs of existing hubs this relates to"],
  "key_references": ["Academic references"],
  "notes": "Any structural observations about what makes this hub interesting"
}
```

## Critical Instructions

1. **FORMAL PROOFS ONLY.** Every hub must have a real theorem behind it. Empirical tradeoffs don't count unless there's a proven bound. If something is conjectured, mark it explicitly.

2. **NO DUPLICATES.** Check every candidate against the 34 existing hubs. If it's a variant of an existing hub (e.g., Gibbard-Satterthwaite is already there — don't add a "manipulation impossibility" that's the same theorem reframed), skip it.

3. **STRUCTURAL PATTERN REQUIRED.** Every hub must fit the COMPOSE → COMPLETE FAILS → BREAK_SYMMETRY template, or you must explain why it doesn't fit and what alternative structural pattern it uses.

4. **CONNECTION TO EXISTING HUBS.** For every new hub, identify which existing hubs it connects to and why. Isolated hubs are low-value. Bridge hubs are high-value.

5. **RESOLUTION COUNT.** For each hub, estimate how many known resolution strategies exist in the literature. Hubs with 5+ known resolutions are immediately valuable. Hubs with 1-2 resolutions still matter but will need spoke densification later.

## Target

Return at least 10 new hubs per batch, 8 batches, total 60-80 new hubs. Quality over quantity — a well-characterized hub with clear structural pattern and connections is worth more than three thin ones.


# ═══════════════════════════════════════════════════════════════════════
# MACHINE 2: SPOKE DENSIFICATION — Layer 3 Fill Rate
# Target: 55.9% → 70%+ fill rate
# ═══════════════════════════════════════════════════════════════════════

## Context

You are filling the resolution matrix of a structural impossibility database. The matrix is 9 damage operators × 34 hubs. Current fill rate is 55.9%. Every empty cell is either a known resolution we haven't ingested, a genuine prediction target, or a structural impossibility. Your job is to fill cells from known literature.

### Current Hub × Operator Matrix (empty cells marked with ·)

For each hub below, I've listed which damage operators currently have spokes. Your job is to fill the EMPTY ones from domain literature.

```
Hub                        | DIS CON TRU EXP RAN HIE PAR QUA INV
---------------------------|---------------------------------------
FORCED_SYMMETRY_BREAK      |  ✓   ✓   ✓   ✓   ✓   ✓   ✓   ✓   ✓   (FULL)
CALENDAR_INCOMM            |  ✓   ·   ✓   ·   ✓   ✓   ✓   ·   ·
ARROW_SOCIAL               |  ✓   ✓   ✓   ·   ✓   ·   ·   ·   ·
GODEL_INCOMP               |  ✓   ·   ·   ✓   ·   ✓   ·   ✓   ·
HEISENBERG                 |  ✓   ✓   ✓   ·   ✓   ·   ✓   ·   ·
CAP_THEOREM                |  ·   ·   ✓   ·   ✓   ·   ·   ·   ·
MAP_PROJECTION             |  ✓   ✓   ·   ·   ·   ·   ✓   ·   ·
HALTING_PROBLEM            |  ·   ·   ✓   ·   ✓   ✓   ·   ·   ·
SHANNON_CAPACITY           |  ✓   ·   ✓   ✓   ✓   ✓   ✓   ·   ·
NYQUIST_LIMIT              |  ✓   ·   ✓   ✓   ✓   ·   ·   ·   ·
CARNOT_LIMIT               |  ✓   ✓   ·   ·   ·   ✓   ·   ·   ·
BODE_SENSITIVITY           |  ✓   ✓   ·   ·   ✓   ✓   ✓   ·   ·
NO_CLONING                 |  ✓   ·   ✓   ·   ✓   ✓   ✓   ·   ·
CRYSTALLOGRAPHIC           |  ✓   ✓   ·   ·   ✓   ✓   ·   ·   ·
FITTS_HICK                 |  ✓   ·   ·   ✓   ✓   ✓   ✓   ·   ·
IMPOSSIBLE_TRINITY         |  ✓   ·   ✓   ·   ·   ✓   ✓   ·   ·
QUINTIC_INSOLVABILITY      |  ·   ·   ✓   ✓   ·   ✓   ·   ·   ·
```

(Remaining 17 hubs also have empty cells — query the database for their current state.)

## Task

For each EMPTY CELL in the matrix, search the domain literature for whether a known resolution exists that matches that damage operator. If one exists, write the full resolution entry. If you can confirm NO resolution exists and the cell is structurally impossible, mark it as such with reasoning.

### Priority Order

1. **Consensus tensor predictions first.** The tensor predicts these cells should be filled:
   - CONCENTRATE × Quintic
   - DISTRIBUTE × Quintic
   - CONCENTRATE × Shannon
   Fill these FIRST with maximum effort — they're the strongest predictions.

2. **Hubs with most empty cells.** CAP_THEOREM has 7 empty cells. MAP_PROJECTION has 6. These offer the most improvement per hub.

3. **New operators (QUANTIZE, INVERT).** These columns are sparsest across all hubs. For each hub, ask: "is there a known resolution that works by discretizing (QUANTIZE) or by reversing direction (INVERT)?"

## Output Schema

For each filled cell:

```json
{
  "hub_id": "existing hub",
  "resolution_id": "UNIQUE_SNAKE_CASE",
  "resolution_name": "Human-readable name",
  "tradition_or_origin": "Origin",
  "period": "Time period",
  "property_sacrificed": "What is given up",
  "damage_operator": "One of the 9",
  "primitive_sequence": ["Ordered primitives"],
  "description": "Minimum 3 sentences. MECHANISM, not just description.",
  "cross_domain_analogs": {
    "existing_hub_links": ["resolution IDs from OTHER hubs with same damage operator"],
    "new_resolution_links": ["other new resolutions in this batch"]
  },
  "key_references": ["Academic references"],
  "confidence": "HIGH (known, documented) | MEDIUM (exists but informal) | LOW (plausible but unverified)"
}
```

For structurally impossible cells:

```json
{
  "hub_id": "...",
  "damage_operator": "...",
  "assessment": "STRUCTURALLY_IMPOSSIBLE",
  "reasoning": "Why this operator CANNOT apply to this impossibility (minimum 2 sentences)"
}
```

## Critical Instructions

1. **KNOWN RESOLUTIONS ONLY.** You're filling from literature, not inventing. If a resolution doesn't exist in any published work, don't fabricate one. Mark the cell as UNKNOWN.

2. **CROSS-DOMAIN LINKS ON EVERY ENTRY.** Every new spoke must link to at least one spoke in a different hub that shares its damage operator.

3. **DISTINGUISH UNKNOWN FROM IMPOSSIBLE.** An empty cell might be empty because nobody has tried (UNKNOWN) or because the operator structurally can't apply (IMPOSSIBLE). Both are valuable information. Don't default everything to UNKNOWN.

4. **TENSOR PREDICTIONS GET EXTRA EFFORT.** For the 3 consensus predictions, search deeply. If CONCENTRATE × Shannon means "localizing capacity to specific frequency bands" — is that what water-filling power allocation does? Is that what OFDM subcarrier allocation does? These might be known engineering practices that haven't been classified under the damage algebra.

## Target

Fill at least 30 cells. Identify at least 5 structurally impossible cells. Push fill rate from 55.9% toward 70%.


# ═══════════════════════════════════════════════════════════════════════
# MACHINE 3: PREDICTION VERIFICATION — Layer 5 Validation
# Target: Verify all 30 tensor predictions
# ═══════════════════════════════════════════════════════════════════════

## Context

A Tucker tensor decomposition on a 9×34 impossibility hub matrix has generated 30 predictions — empty cells the tensor says should be filled. 8 are stable from the original 7-operator basis. 22 are new from expanded hubs. 3 are consensus between SVD and Tucker methods. A previous round achieved a 47% verified hit rate (14/30 matched known mathematics), 90% known-or-plausible, and ZERO spurious predictions.

Your job is to verify each prediction: does the predicted resolution actually exist in known mathematics, science, or engineering?

## The 30 Predictions

### 3 Consensus Predictions (HIGHEST PRIORITY)
```
1. CONCENTRATE × QUINTIC_INSOLVABILITY
   Tensor says: A resolution that localizes the insolvability damage
   Question: Is there a known approach to the quintic that concentrates the algebraic obstruction?

2. DISTRIBUTE × QUINTIC_INSOLVABILITY  
   Tensor says: A resolution that distributes insolvability evenly
   Question: Is there a way to "spread" the quintic's unsolvability across all roots?

3. CONCENTRATE × SHANNON_CAPACITY
   Tensor says: Localizing the capacity constraint to specific bands
   Question: Water-filling? OFDM? Cognitive radio?
```

### 8 Stable Predictions (held from 7-op basis)
```
4.  HIERARCHIZE × MAP_PROJECTION — higher-dimensional projection methods
5.  HIERARCHIZE × CALENDAR — meta-calendar systems
6.  HIERARCHIZE × PYTHAGOREAN_COMMA — adaptive just intonation
7.  PARTITION × BORSUK_ULAM — domain splitting for topology
8.  PARTITION × CAP_THEOREM — sharding
9.  PARTITION × IMPOSSIBLE_TRINITY — currency zones
10. EXTEND × MAP_PROJECTION — adding dimensions to projection
11. TRUNCATE × MAP_PROJECTION — partial maps / nautical charts
```

### 22 New Predictions (from expanded hub set)
```
12. INVERT × MAP_PROJECTION — inverse cartography / GR connection
13. INVERT × QUINTIC — inverse Galois problem
14. INVERT × FOUNDATIONAL_IMPOSSIBILITY — paraconsistent logic
15. QUANTIZE × MAP_PROJECTION — polyhedral projections (Dymaxion)
16. QUANTIZE × IMPOSSIBLE_TRINITY — cryptocurrency / discrete capital
17. QUANTIZE × GOODHART — letter grades as anti-gaming
18. EXTEND × GOODHART — multi-objective optimization
19. INVERT × HALTING — running programs backward?
20. INVERT × HAIRY_BALL — reversing vector field construction
21. QUANTIZE × RUNGE — discrete node placement strategies
22. DISTRIBUTE × GIBBARD_SATTERTHWAITE — spreading manipulation vulnerability
23. CONCENTRATE × HAIRY_BALL — isolating singularity
24. RANDOMIZE × QUINTIC — probabilistic root finding
25. EXPAND × HEISENBERG — adding ancilla systems
26. INVERT × CARNOT — heat pumps as reversed engines
27. QUANTIZE × BODE — discrete frequency control
28. INVERT × ARROW — reversed preference aggregation
29. HIERARCHIZE × SEN — meta-level rights framework
30. PARTITION × HALTING — decidable sublanguage partitioning
```

## Task

For each prediction, search the literature and classify:

### Classification Categories

- **VERIFIED_EXACT**: A known mathematical object, theorem, or engineering practice exists that exactly fills this cell. Provide the name, reference, and structural description.

- **VERIFIED_APPROXIMATE**: Something exists in the neighborhood — the prediction points at a real area but the exact resolution is slightly different from what the tensor predicted. Explain the mismatch.

- **PLAUSIBLE_UNVERIFIED**: No known resolution found, but the structural logic is sound and the resolution *could* exist. Explain why it's plausible.

- **STRUCTURALLY_IMPOSSIBLE**: The damage operator genuinely cannot apply to this impossibility. Explain the structural reason.

- **SPURIOUS**: The prediction doesn't make mathematical sense — the combination is incoherent. Explain why.

## Output Schema

```json
{
  "prediction_number": 1,
  "cell": "OPERATOR × HUB",
  "classification": "VERIFIED_EXACT | VERIFIED_APPROXIMATE | PLAUSIBLE_UNVERIFIED | STRUCTURALLY_IMPOSSIBLE | SPURIOUS",
  "known_object": "Name of the known mathematics/engineering if verified (null otherwise)",
  "description": "What this resolution does and how it handles the impossibility (3+ sentences)",
  "primitive_sequence": ["Ordered primitives if verified"],
  "key_references": ["Academic references if verified"],
  "structural_reasoning": "Why this operator does or doesn't apply to this hub",
  "connection_to_existing": ["Which existing spokes this relates to"]
}
```

## Critical Instructions

1. **SEARCH DEEPLY BEFORE MARKING UNVERIFIED.** The 47% hit rate means roughly half these predictions correspond to known objects that might be described in domain-specific language you wouldn't immediately associate with the prediction. CONCENTRATE × Shannon might be "water-filling power allocation" in information theory. INVERT × Carnot might just be "heat pumps." Search the domain literature, not just the mathematical surface.

2. **ZERO TOLERANCE FOR FABRICATION.** If you can't find it, say PLAUSIBLE_UNVERIFIED. Do NOT invent a mathematical object to fill the cell. The zero-spurious rate from the previous round is a quality standard to maintain.

3. **STRUCTURAL IMPOSSIBILITY IS VALUABLE DATA.** If INVERT × Halting is structurally impossible because computation has no meaningful "reverse direction" in this context, that's an important result — it tells us the tensor is over-generalizing INVERT. Explain the structural reason clearly.

4. **CONSENSUS PREDICTIONS GET MAXIMUM EFFORT.** Predictions 1-3 are where both decomposition methods agree. These are the highest-confidence predictions. If they verify, it's strong validation. If they don't, something is wrong with the tensor. Search exhaustively.

5. **TRACK THE HIT RATE.** At the end, compute: verified_exact / total, (verified_exact + verified_approximate) / total, spurious / total. Compare to previous round (47% exact, 90% plausible-or-better, 0% spurious).

## Target

Classify all 30 predictions. Maintain the zero-spurious rate. Target 40%+ exact verification rate. Every VERIFIED_EXACT result should include enough detail for Machine 2 to immediately ingest it as a new spoke.


# ═══════════════════════════════════════════════════════════════════════
# MACHINE 4: FORGE PIPELINE — Reasoning Engine Core
# Target: Complete tourney + L22 CMA-ES experiment
# ═══════════════════════════════════════════════════════════════════════

## Context

This is the core reasoning engine work. Everything else in the Prometheus system exists to feed this pipeline. The Noesis discovery engine, the damage algebra, the ethnomathematics — all of it ultimately generates training signal for small model reasoning improvement.

### Current State
- Forge tool population: ~27 tools (survivors from 1,500+ distillation)
- Evaluation battery: 89 categories (trap_generator.py + extended + expanded)
- Category coverage: ~89/89 (recent estimate, needs verification)
- Known gap categories: temporal-sequential, causal-interventional, complex ToM, self-referential, spatial
- Steering vector experiments: L23 = 3 flips, L22 = 4 flips (Siblings channel found)
- Pending: L22 Finish-weighted CMA-ES, multi-vector L22+L23

## Task A: Tournament of 27

Run the full evaluation tournament.

### Steps
1. Load current Forge tool population
2. Run each tool against ALL trap categories (89 categories, full parametric battery)
3. For each tool, record:
   - Per-category pass/fail with margin
   - Total flip count
   - Behavioral fingerprint (via behavioral_fingerprints.py)
4. Cluster tools by behavioral fingerprint similarity
5. Identify:
   - Monoculture clusters (tools that are behaviorally identical)
   - Unique behavioral profiles (non-redundant tool count)
   - Gap categories (zero tools pass)
   - Top 5 tools by total flip count
   - Any new behavioral patterns not seen in previous tournaments

### Output
Save to `F:/prometheus/forge/tourney_27_results.json`:
```json
{
  "timestamp": "...",
  "total_tools": 27,
  "unique_profiles": 0,
  "category_coverage": "X/89",
  "gap_categories": ["list"],
  "monoculture_clusters": [{"cluster_id": 0, "tool_ids": [], "shared_fingerprint": "..."}],
  "top_5_tools": [{"tool_id": "...", "flip_count": 0, "unique_categories": []}],
  "per_tool_results": [{"tool_id": "...", "flips": 0, "categories_passed": [], "fingerprint": "..."}]
}
```

## Task B: L22 Finish-Weighted CMA-ES

Run CMA-ES at Layer 22 with a fitness function that weights Finish Before 3rd heavily.

### Rationale
- L22 found 4 flips including Siblings (not accessible at L23)
- But the Siblings vector PUSHED Finish Before 3rd deeper into its basin
- Question: is there a DIFFERENT vector at L22 that flips Finish Before 3rd?
- If YES → two orthogonal vectors at L22, combine them
- If NO → Finish Before 3rd is gated by a different layer entirely

### Fitness Function
```python
def fitness(steering_vector, model, layer=22):
    results = evaluate_all_traps(model, steering_vector, layer)
    score = 0
    # Heavy weight on Finish Before 3rd
    score += 5.0 * results['finish_before_3rd']['margin']
    # Standard weight on others
    for trap in ['overtake_race', 'overtake_2nd', 'overtake_last', 'siblings']:
        score += 1.0 * results[trap]['margin']
    return score
```

### Parameters
- Layer: 22
- Population size: match previous CMA-ES runs
- Generations: 150 (match L22/L23 runs)
- Log every generation's best fitness

### Output
Save to `F:/prometheus/seti/l22_finish_weighted_results.json`:
```json
{
  "layer": 22,
  "generations": 150,
  "fitness_function": "finish_weighted_5x",
  "best_fitness": 0.0,
  "flips": ["list of flipped traps"],
  "margins": {"trap_name": 0.0},
  "finish_before_3rd_flipped": true,
  "finish_before_3rd_margin": 0.0,
  "siblings_status": "flipped | degraded | unchanged",
  "interpretation": "..."
}
```

### Key Question to Answer
Did the Finish-weighted vector flip Finish Before 3rd? If yes, did it degrade Siblings? If the channels are antagonistic at L22 (flipping one pushes the other deeper), that's a confirmed structural property of the layer's basin geometry, not a search artifact.

## Task C: Journal Everything

Write detailed journal entries for both tasks to `F:/prometheus/journal/`. Include raw numbers, not just summaries. The tourney results inform which tools survive to the next round. The CMA-ES results determine whether the multi-vector experiment is L22-only or L22+L23.


# ═══════════════════════════════════════════════════════════════════════
# MACHINE 5: TENSOR REBUILD + EDGE COMPUTATION — Continuous Integration
# Target: Rebuild tensor on every data update, maintain prediction surface
# ═══════════════════════════════════════════════════════════════════════

## Context

You are the continuous integration engine for the Noesis database. Every time Machines 1-3 deposit new data (hubs, spokes, verified predictions), you rebuild the tensor decomposition and recompute the cross-domain edge graph. You run in a loop.

### Current State
- Tensor: 9×34, 55.9% fill rate
- Cross-domain edges: 2,423
- Decomposition method: Tucker (rank 3 per mode) + SVD for consensus
- Predictions: 30 current (8 stable, 22 new, 3 consensus)

## Main Loop

```
WHILE TRUE:
    1. Check database for new data (new hubs, new spokes, reclassifications)
    2. If no new data, sleep 5 minutes, continue
    3. If new data:
        a. Rebuild tensor
        b. Recompute predictions
        c. Compute new cross-domain edges
        d. Compare to previous predictions
        e. Log results
        f. Push to database
```

## Task A: Tensor Rebuild

### Steps
1. Query all composition_instances with hub_id, damage_operator, primitive_sequence
2. Construct 3D tensor: [9 damage operators] × [N hubs] × [11 primitives]
3. Fill tensor cells: for each (hub, operator) pair, compute weighted primitive vector
   - Weight by position: first primitive = 1.0, second = 0.5, third = 0.33, etc.
   - Sum across all spokes matching that (hub, operator) pair
   - Normalize to unit length
4. Run Tucker decomposition (rank 3 per mode)
5. Run SVD on the flattened 2D matrix (operators × hubs) for consensus check
6. Identify empty cells
7. For each empty cell, compute completion score from Tucker factors
8. Rank predictions by score
9. Flag consensus predictions (appear in both Tucker and SVD top-20)

### Output
Save to `F:/prometheus/noesis_tensor_latest.json`:
```json
{
  "timestamp": "...",
  "tensor_shape": [9, 0, 11],
  "fill_rate": 0.0,
  "total_predictions": 0,
  "consensus_predictions": 0,
  "stable_predictions": 0,
  "new_predictions": 0,
  "top_30_predictions": [
    {"rank": 1, "score": 0.0, "operator": "...", "hub": "...", "is_consensus": false, "is_stable": false}
  ]
}
```

## Task B: Prediction Stability Tracking

Compare each rebuild's predictions to the previous rebuild:

- **Stable**: prediction appears in both current and previous top-30
- **New**: prediction appears only in current top-30
- **Dropped**: prediction appeared in previous but not current
- **Score change**: for stable predictions, track score delta

Stable predictions across multiple rebuilds are the highest-confidence discoveries. Dropped predictions may have been filled by new data (good) or displaced by tensor restructuring (investigate).

Save stability log to `F:/prometheus/noesis_prediction_stability.jsonl` (append, one line per rebuild).

## Task C: Cross-Domain Edge Computation

After each tensor rebuild:

1. For all spokes sharing the same damage_operator across different hubs:
   - Compute cosine similarity of primitive vectors
   - If similarity > 0.7 AND hubs are in different domains → candidate edge
2. Check against existing edges — only add new ones
3. Insert new edges with provenance = 'tensor_rebuild_TIMESTAMP'
4. Report: new edges added, total edge count, most-connected hub pair

## Task D: Fill Rate & Hit Rate Monitoring

Track these metrics across rebuilds:

```json
{
  "rebuild_number": 0,
  "timestamp": "...",
  "hub_count": 0,
  "spoke_count": 0,
  "fill_rate": 0.0,
  "edge_count": 0,
  "prediction_count": 0,
  "consensus_count": 0,
  "verified_predictions_cumulative": 0,
  "hit_rate_cumulative": 0.0
}
```

**CRITICAL METRIC: hit_rate_cumulative.** This is verified predictions / total predictions generated across all rounds. If this drops below 30%, flag it prominently — it means the framework is degrading as it scales, and we need to investigate whether the primitives or operators need refinement.

Save to `F:/prometheus/noesis_metrics.jsonl` (append).

## Task E: Anomaly Detection

Flag any of these conditions:

1. **Fill rate regression**: new data somehow reduces fill rate (data quality issue)
2. **Edge explosion**: edge count grows faster than quadratic in spoke count (similarity threshold too loose)
3. **Prediction collapse**: fewer than 10 predictions in the top-30 above score 0.3 (tensor is losing discrimination)
4. **Hub isolation**: any hub has zero cross-domain edges after edge computation (topology gap)
5. **Operator monoculture**: any single damage operator accounts for >40% of all spokes (classification bias)

## Critical Instructions

1. **NEVER OVERWRITE PREVIOUS PREDICTIONS.** Append to the stability log. The history of predictions across rebuilds is itself valuable data — it shows which discoveries are robust to data growth.

2. **LOG EVERYTHING.** Every rebuild gets a timestamp, the data that triggered it, the resulting predictions, and the stability comparison. If something breaks at 3am, we need the full audit trail.

3. **EDGE COMPUTATION IS EXPENSIVE.** With 2,400+ edges already, pairwise comparison across all spokes is O(n²). If spoke count exceeds 500, switch to approximate nearest neighbor (FAISS or similar) rather than brute force.

4. **CONSENSUS IS GOLD.** Predictions that appear in both Tucker and SVD are the strongest signals. Always flag them separately. They get priority verification by Machine 3.

## Target

Run continuously. Rebuild within 10 minutes of new data. Maintain prediction surface. Watch the hit rate. The tensor is the instrument — keep it calibrated.
