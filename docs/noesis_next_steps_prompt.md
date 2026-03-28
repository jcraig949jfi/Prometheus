# Noesis — Next Steps for the Tensor Engine

## Context

You're working on Project Prometheus's tensor exploration engine called **Noesis**. You've already built:
- The concept tensor (95 concepts × 30D features) — strategic navigation
- The operation tensor (81 operations × typed features) — tactical chain construction, **37% execution vs 25% random**
- TT decomposition with reconstruction diagnostics (8.94% NRMSE at rank 10)
- Diversity cap to prevent Category Theory dominating all results
- Type compatibility matrix baked into pairwise scoring

The operation tensor is the validated granularity — concept-level failed, operation-level works. All future work should build on the operation tensor.

Read `docs/continuous_exploration_loop.md` for the full Noesis architecture and `docs/unified_theory_convergence.md` for why this work matters to the larger project.

## Priority 1: Wrap Library Functions as Organisms (Largest Impact)

The circularity problem: the tensor needs density (more organisms) to beat human intuition, but building organisms requires the cross-domain insight the tensor provides. The bridge is the **2,970 library functions** that Eos already discovered from numpy, scipy, networkx, sympy, etc.

### What exists
- `agents/eos/src/library_scanner.py` — discovered the 2,970 functions
- `organisms/mass_embedder.py` — already embedded 2,236 of them into 240D space
- `organisms/mass_embedder_checkpoint.json` — checkpoint at index 2500
- `organisms/embedded_library.zarr/` — the embeddings
- `organisms/library_embeddings.duckdb` — metadata

### What to build
A script (`organisms/library_wrapper.py`) that:

1. Reads the library manifest (the 2,970 functions already cataloged)
2. For each function, introspects the signature to determine:
   - Input types (map to semantic types: `scalar`, `array`, `probability_distribution`, `integer`, `matrix`, `adjacency_matrix`, `graph`, `dict`, etc.)
   - Output types (same semantic types)
   - Whether it's safely callable with standard test inputs
3. Wraps each viable function as a `MathematicalOrganism` operation with proper `input_type` / `output_type` metadata
4. Groups by source package (one organism per package or sub-package, e.g., `scipy_signal`, `numpy_linalg`, `networkx_centrality`)
5. Tests each wrapped operation against the standard probe battery (the same inputs from `experiment_tensor_vs_random.py`)
6. Saves successful wrappers as organism files

### Key constraints
- Start with **numpy** (~500 functions) — cleanest signatures, most likely to work
- Use semantic types from the existing organism base class, not Python types. `np.ndarray` should map to `array` or `matrix` depending on expected dimensionality.
- Skip functions that require complex structured inputs (class instances, file handles, etc.)
- Skip functions that are destructive or have side effects
- Each wrapped operation must be testable: call it with a standard input, check it doesn't crash, NaN, or produce enormous output
- Target: **200+ new operations** across 10-20 new organisms (currently 81 operations across 18)
- The operation tensor should be rebuildable after wrapping to include the new operations

### How to verify
```
cd f:\Prometheus
python organisms/library_wrapper.py --source numpy --test
python organisms/library_wrapper.py --source scipy --test
python organisms/tensor_navigator.py --diagnostics  # Rebuild with new organisms
```

After wrapping, re-run the tensor vs random experiment to see if the larger operation tensor produces better results.

---

## Priority 2: Build the Continuous Loop Daemon

The tensor navigator works. The operation tensor works. What doesn't exist is the process that runs forever.

### What to build
A script (`organisms/noesis_daemon.py`) that:

1. **Loads** the operation tensor and builds TT decomposition
2. **Scores** the full interaction space, extracts top-K frontier
3. **Executes** the top-K chains on test inputs (using `org.execute(op_name, input)`)
4. **Records** outcomes to DuckDB: chain, success/failure, score, output hash, timestamp
5. **Updates** the exploration map: mark executed chains, track which regions are explored
6. **Loops**: re-score with updated exploration mask, execute next batch, record, repeat
7. **Checkpoints** state to disk every N cycles: exploration map, velocity log, feature drift (if dream state is active)
8. **Resumes** from checkpoint on restart — detect existing state and continue

### Key design points
- **No LLM in the loop.** Pure tensor + execution. The LLM interpretation hook is a future addition.
- **Velocity tracking:** measure cracks per cycle (chains with score > threshold). Log to DuckDB.
- **Batch size:** configurable, default 100 chains per cycle
- **Cycle time target:** under 10 seconds per cycle at current scale (81 operations)
- **Graceful shutdown:** catch SIGINT, save checkpoint, exit cleanly
- **CLI flags:** `--cycles N` (run N cycles then stop), `--forever` (run until killed), `--resume` (continue from checkpoint), `--batch-size N`, `--threshold F`

### Storage
Use the existing DuckDB at `organisms/library_embeddings.duckdb` or create a new `organisms/noesis_state.duckdb`. Tables:
- `compositions`: chain_key, executed, score, output_hash, cycle, timestamp
- `velocity_log`: cycle, cracks, cumulative_cracks, chains_tested, timestamp
- `exploration_map`: concept_a, concept_b, status (explored/frontier/exhausted)

### How to verify
```
cd f:\Prometheus
python organisms/noesis_daemon.py --cycles 10 --batch-size 50  # Quick test
python organisms/noesis_daemon.py --cycles 100 --resume  # Continue
python organisms/noesis_daemon.py --forever  # Run until killed
```

---

## Priority 3: Quality Scoring Beyond Binary Success

Currently all successful chains score equally. A chain that produces a novel mathematical structure scores the same as one that produces `3.7`.

### What to build
Add a quality dimension to chain scoring in the operation tensor or the daemon:

1. **Embed the output** using the universal embedder (`organisms/universal_embedder.py`). Every chain output gets a 240D behavioral fingerprint.
2. **Novelty score**: embedding distance from all previously seen outputs. Chains that produce outputs far from everything else in the space get a bonus. Chains that produce outputs identical to existing ones get nothing.
3. **Structure score**: output dimensionality / input dimensionality. Chains that preserve or increase structure score higher than chains that collapse everything to a scalar.
4. **Combined quality**: `quality = 0.4 * execution_success + 0.3 * novelty + 0.2 * structure + 0.1 * speed`

### Where it plugs in
- In the daemon's record step: after executing a chain, embed the output and compute quality
- In the operation tensor's scoring: feed quality back as a feature update (this is the dream state's input signal)
- In the velocity metric: count only chains above a quality threshold as "cracks"

### How to verify
Run the daemon for 100 cycles, then check:
- Distribution of quality scores (should not be bimodal — if it is, the threshold needs adjustment)
- Top-10 chains by quality vs top-10 by raw execution rate — are they different? They should be.

---

## Priority 4: Framing on the Operation Tensor

The framing experiment ran on the concept tensor. Now run it on the operation tensor where the signal is real.

### What to build
Extend `experiment_framing.py` to work with the operation tensor:

1. Apply each of the 5 frame bias vectors to the operation feature matrix (not the concept matrix)
2. Compute the operation interaction tensor under each frame
3. Extract top-K chains per frame
4. Execute all chains
5. Compare: do different frames find chains that succeed on different input types?

### The key question
Does the devil's advocate frame (boosts falsifiability, suppresses stability) find chains that handle perturbation-sensitive inputs better? Does the Occam frame (boosts compression) find simpler chains that are more robust? If frames produce qualitatively different successful chains, framing has real signal at the operation level. If all frames produce the same successful chains, framing is only useful at the concept level for strategic navigation.

### How to verify
```
cd f:\Prometheus
python organisms/experiment_framing.py --operation-tensor --execute
```

Output should show per-frame execution rates AND per-frame success on different input types. Jaccard similarity between frames' successful chain sets should be low (frames find different things).

---

## Important Notes

- **Do NOT re-add Coeus/Nous data.** The tensor was decontaminated — feature matrix comes from `get_feature_matrix()` only. Exploration map is populated by real composition outcomes, not Nous hypotheses.
- **All organisms use `.execute(op_name, input)`** to run operations. Not `.get_operation()`.
- **The `CONCEPT_TO_ORGANISM` mapping** in experiment files maps 17 of 95 concepts to organisms. The other 78 have no organisms. Library wrapping (Priority 1) will grow this.
- **Semantic types matter.** The operation tensor's advantage over the concept tensor is type awareness. New wrapped functions MUST use semantic types (`probability_distribution`, `adjacency_matrix`, `scalar`, `array`, `integer`, `matrix`, `graph`), not Python types.
- **The continuous loop must be crash-safe.** Windows may reboot for updates. Checkpoint everything. Resume from last state.
- **Stay calibrated.** Everything is early stage. The 37% vs 25% result is promising but on 81 operations. Test every assumption at the new scale after wrapping.

---

## The Bigger Picture (for context, not for implementation)

Noesis is one piece of the Prometheus project. The tensor engine's output feeds into:
- **Nous** — tensor frontier replaces random concept sampling
- **Hephaestus** — tensor-guided forge targets instead of Coeus-weighted
- **Rhea** �� forge survivors become training data for model reasoning
- **Coeus** — composition outcomes become causal signal for concept scoring

The forge has 5 genuinely unique reasoning tool triples that survived 89-category testing. Those 5 tools should eventually become organisms in the tensor — reasoning algorithms composable at tensor speed. But that's future work. Right now the priority is growing the organism library (Priority 1) and proving the continuous loop works (Priority 2).

Read `docs/continuous_exploration_loop.md` for the full four-layer vision if you need architectural context. But build incrementally — Priority 1 first, then 2, then 3, then 4.
