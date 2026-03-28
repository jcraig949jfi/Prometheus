# Noesis — Type Compatibility Fix for Tensor Navigator

## Context

You're working on the Prometheus project's tensor exploration engine called **Noesis**. The tensor navigator (`organisms/tensor_navigator.py`) scores concept triples by mathematical feature similarity, but an experiment (`organisms/experiment_tensor_vs_random.py`) showed that **random chain sampling outperforms tensor-guided sampling** (12% execution rate vs 4%). The reason: the tensor scores *conceptual affinity* but has zero awareness of *operational type compatibility*. It recommends "Topology × Immune Systems" but `betti_numbers` outputs a scalar while `self_nonself_discrimination` expects a different input type. The chains crash before producing results.

## Key Files

- `organisms/base.py` — `MathematicalOrganism` base class. Has `compatible_chains(other)` method that finds type-compatible operation pairs between two organisms. Each operation has `input_type` and `output_type` metadata.
- `organisms/__init__.py` — `ALL_ORGANISMS` list, 18 implemented organisms as classes.
- `organisms/concept_tensor.py` — 95 concepts encoded as 30D feature vectors. Hand-seeded. Scoring functions: `compute_pairwise_interactions()`, `compute_triple_tensor_fast()`. Scores are: novelty (0.4 weight), complementarity (0.35), resonance (0.25).
- `organisms/tensor_navigator.py` — TT decomposition, top-K extraction, frontier detection, diversity cap. Recently decontaminated (Coeus/Nous data removed). Has reconstruction error diagnostics.
- `organisms/experiment_tensor_vs_random.py` — The experiment that proved tensor guidance currently loses to random. Fix this.

## The Three Levels of Fix

### Level 1: Pre-filter by type compatibility (do first)

In `experiment_tensor_vs_random.py`, the `sample_tensor_guided_chains()` function currently picks organism pairs based on tensor pairwise scores, then randomly selects operations. Instead:

1. For each organism pair the tensor recommends, call `org_a.compatible_chains(org_b)` to get the list of type-compatible operation pairs
2. Only create chains from compatible pairs
3. If a high-scoring organism pair has zero compatible operations, skip it
4. This should immediately raise tensor-guided execution rates above random

Also update `sample_random_chains()` to optionally use type filtering too, so you can compare: random-unfiltered vs random-filtered vs tensor-filtered. The interesting comparison is random-filtered vs tensor-filtered — does the tensor add signal *beyond* type compatibility?

### Level 2: Type compatibility as tensor signal

In `concept_tensor.py`, add type compatibility awareness to the scoring:

1. Load all 18 implemented organisms (from `ALL_ORGANISMS`)
2. For each organism pair that maps to a concept pair, count the number of type-compatible operation chains
3. Create a `type_compatibility_matrix` (95×95) where entry [i,j] = number of compatible chains between concept i's organism and concept j's organism (0 for the 77 concepts without organisms)
4. Use this as a multiplier or additional term in `compute_pairwise_interactions()`. A concept pair with zero compatible operations should score lower, regardless of feature similarity.
5. This means the tensor itself learns "interesting AND connectable"

### Level 3: Operation-level tensor

This is the deeper redesign. Currently the tensor operates at concept granularity (95 concepts). But compositions happen at operation granularity (81 operations across 18 organisms). Consider:

1. Build a second tensor at operation level: 81 operations × 30 features
2. Features for operations: input_type encoding, output_type encoding, computational properties (from the existing concept features of their parent organism), behavioral features (from the universal embedder's 240D fingerprints if available)
3. The operation tensor's scoring function can directly check type compatibility: operations that type-match get a bonus, operations that don't get zeroed
4. Top-K from the operation tensor gives you directly executable chains, no filtering needed
5. The concept tensor remains for high-level navigation ("which domains should we explore?"), the operation tensor handles low-level chain construction ("which specific operations should we connect?")

This is a bigger piece of work. The concept tensor stays as-is for strategic navigation. The operation tensor is a new tactical layer underneath it. Only build this if Level 1+2 results show the tensor signal is real (tensor-filtered meaningfully outperforms random-filtered).

## How to Verify

After each level, re-run the experiment:
```
cd f:\Prometheus
python organisms/experiment_tensor_vs_random.py
```

Success criteria:
- **Level 1**: Tensor-guided execution rate > random execution rate
- **Level 2**: Tensor-guided mean score > random mean score by >10%
- **Level 3**: Tensor-guided chains produce higher novelty scores (output hashes are more diverse) than random-filtered chains

## Important Notes

- The tensor navigator was recently decontaminated — Coeus/Nous enrichment data was removed. Do NOT re-add it. The feature matrix should come from `get_feature_matrix()` only, not `enrich_with_coeus()`.
- The `experiment_tensor_vs_random.py` already has the full test harness, scoring, and comparison logic. You just need to fix the chain sampling.
- All organisms use `.execute(op_name, input)` to run operations, not `.get_operation()`.
- The `CONCEPT_TO_ORGANISM` mapping in the experiment file maps 17 of 95 concepts to organisms. The other 78 concepts have no organisms yet.
- Keep the experiment deterministic: `random.seed(42)` and `np.random.seed(42)` are already set.
- Read `docs/continuous_exploration_loop.md` for the full Noesis vision if you need architectural context.
