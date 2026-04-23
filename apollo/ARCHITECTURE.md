# Apollo v2_d — Gradient Recovery

## Diagnosis (gen 90, v2_c)

The engineering works. The evolution doesn't. Three interlocking failures:

1. **Flat fitness landscape**: 0% raw accuracy across entire population. No gradient for selection. Drift dominates because it's the only operator that produces "improvements" (marginally less bad NCD margins).

2. **Structural mutations die on arrival**: LLM mutations compile (100% rate) but lose in selection every time (0 in 485 elite entries). New structures have scrambled parameters — immediately worse than parameter-optimized incumbents.

3. **AOS reward corrupted**: Every operator gets reward=1.0 because Pareto improvement is trivially easy at 0% accuracy (any behavioral change = non-dominated on diversity axis). Bandit can't distinguish useful from useless.

## Three Fixes (must be applied together)

### Fix 1: Difficulty Curriculum
- Generate 20-30 easy tasks that exercise individual primitives
- Simple logic consistency, basic Bayesian updates, 2-3 variable constraints
- Mix into evolution set (don't replace hard tasks — add easy ones)
- As population accuracy climbs above 30-40%, rotate in harder tasks
- Goal: create a gradient from solvable to unsolvable

### Fix 2: Post-Mutation Parameter Annealing
- After every LLM structural mutation, run 5-10 rounds of parameter-only drift
- Evaluate on 10-20 easy tasks (cheap — ~1-2s total)
- Let the new structure tune its parameters before competing
- Tag as `annealed` in lineage

```python
def mutate_with_annealing(organism, llm_mutator, config, task_subset):
    child = structural_mutation(organism, llm_mutator)
    best = child
    for _ in range(10):
        variant = parameter_mutation(best, sigma=0.15)
        if evaluate_quick(variant, task_subset) > evaluate_quick(best, task_subset):
            best = variant
    best.lineage.mutations_applied.append('annealed')
    return best
```

### Fix 3: Accuracy-Only AOS Reward
- Before gen 300: reward = 1.0 if child.raw_accuracy > parent.raw_accuracy, else 0.0
- After gen 300: full Pareto improvement check
- Unblocks bandit from rewarding meaningless Pareto improvements

```python
def aos_reward(child, parent, generation, config):
    if generation < config.get('aos_accuracy_only_until', 300):
        return 1.0 if child.raw_accuracy > parent.raw_accuracy else 0.0
    else:
        return 1.0 if pareto_dominates(child, parent) else 0.0
```

### Fix 4: Selection Death Logging
- Log WHY LLM-mutated organisms lose in selection
- Did they die in racing, or survive racing but lose in NSGA-III?
- Evaluation failure vs selection failure require different fixes

## Implementation Order

1. Wait for gen 100 ablation data (diagnostic value)
2. Build difficulty curriculum (task_manager changes)
3. Add parameter annealing to mutation pipeline
4. Fix AOS reward signal
5. Add selection death logging
6. Restart from fresh population with curriculum

## Decision Point: After Gen 100

- If minimalist organism #2 (5 primitives) survives ablation → it's the first real atom, seed v2_d from it
- If nothing survives → restart with curriculum, the population has no honest computation
- Either way: ablation data tells us whether any primitive actually fires
