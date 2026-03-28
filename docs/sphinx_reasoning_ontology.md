# Sphinx — The Reasoning Ontology

*A systematic taxonomy of how reasoning fails, expressed as computable tests*

> The Sphinx sits at the gate and poses riddles. Answer correctly, you pass. Answer wrong, you're destroyed. No negotiation, no partial credit, no appeal to authority.

---

## What Sphinx Is

Sphinx is the **shared reasoning failure taxonomy** that every Prometheus agent consumes. It defines what "correct reasoning" looks like by enumerating all the ways reasoning can break — then expressing each failure mode as a parametric, deterministic, infinitely-generatable test.

Sphinx is not a project in the way Ignis, Rhea, or Apollo are projects. It is the **substrate** — the ground truth definition of the problem space. When Sphinx expands, every downstream system's behavior changes simultaneously.

**Current scope:** 105 categories across 14 domains, organized into two tiers:
- **Tier A (Parsing):** The answer is deterministically computable from the prompt's structure. The difficulty is in not being fooled by surface features.
- **Tier B (Judgment):** The correct response requires recognizing ambiguity, insufficiency, or meta-level properties of the question itself.

**Composition:** 105 categories × 12 Nemesis metamorphic relations × parametric variation = effectively unbounded test space.

---

## Why Sphinx Exists Separately

The trap battery was originally embedded in Hephaestus as a 15-trap validation gate. It grew organically:
- Ignis added 30 traps for eval_v2 (ordinal traps, held-out traps)
- Nemesis added metamorphic relations (12 formal mutation types)
- Apollo added curriculum scheduling (fixed + rotating + held-out)
- CAITL revealed that 15 categories is a closed vocabulary that tools can dispatch-table their way through

At 105 categories, the battery is no longer a validation gate — it's a **theory of reasoning failure**. It needs its own identity because:

1. **It's the shared dependency.** Every agent imports it. Expanding it is a force multiplier across the entire system.
2. **The Tier A/B distinction is architectural.** Coeus needs to track parsing accuracy and judgment accuracy separately. The RLVF fitness function should weight them differently.
3. **The phased build order is a research instrument.** Each phase tests specific hypotheses about which tool families improve on which category families.
4. **The parametric generators are the anti-Goodhart mechanism.** Infinite variants with known correct answers prevent any tool from memorizing the battery.

---

## The 14 Domains

| Domain | Categories | Tier | Core Failure Mode |
|--------|-----------|------|-------------------|
| **A: Formal Logic** | 13 | A | Affirming consequent, undistributed middle, De Morgan, vacuous truth, etc. |
| **B: Probabilistic** | 11 | A | Base rate neglect, conjunction fallacy, gambler's fallacy, expected value |
| **C: Arithmetic** | 10 | A | Order of operations, modular arithmetic, fencepost, percentage change |
| **D: Temporal** | 5 | A | Temporal ordering, parallel vs sequential, rate/inverse proportion |
| **E: Linguistic** | 9 | A/B | Scope ambiguity, presupposition, garden path, pragmatic implicature |
| **F: Causal** | 6 | A/B | Post hoc, correlation≠causation, Simpson's paradox, counterfactual |
| **G: Set Theory** | 5 | A | Empty set, subset inversion, universal vs existential |
| **H: Spatial** | 5 | A | Left-right reversal, direction composition, triangle inequality |
| **I: Meta-Reasoning** | 5 | B | Confidence calibration, validity vs soundness, epistemic closure |
| **J: Common Sense** | 4 | A/B | Unit conversion, composition fallacy, false dichotomy |
| **K: Multi-Step** | 5 | A/B | Multi-hop deduction, information sufficiency, premise contradiction |
| **L: Uncertainty** | 4 | B | Closed world assumption, absence of evidence, ambiguity tolerance |
| **M: Theory of Mind** | 4 | B | False belief, knowledge attribution, second-order belief |
| **N: Analogical** | 4 | A/B | False analogy, pattern extrapolation trap, hasty generalization |

**Total: 90 new + 15 original = 105 categories**

---

## How Each Agent Consumes Sphinx

### Hephaestus (Forge Validation)
**Gate 5** expands from 15 static traps to a sampled battery from all 105 categories. A forged tool must beat NCD baseline on a *random* sample, not a fixed set. This prevents dispatch-table optimization.

**New metric:** Fallback rate — what percentage of the expanded battery triggers an actual parser vs falling through to NCD? A tool with 30% parser coverage but calibrated fallback (low confidence on unrecognized patterns) is more valuable than 80% coverage with overconfident fallback.

### Nemesis (Adversarial Pressure)
Nemesis gains 90 new seed categories for metamorphic mutation. Each seed × 12 MRs × parametric variation = massive adversarial diversity. The MAP-Elites grid can be restructured: instead of just (complexity, obfuscation), add a (domain, tier) dimension.

### Apollo (Evolution Curriculum)
The rolling curriculum (15 fixed + 5 rotating every 50 generations) draws from a much deeper pool. This is the direct fix for the Council's "static tasks will be memorized" concern. With 105 categories, the probability of an organism memorizing the full space drops to near zero.

### Ignis (Evaluation)
eval_v2 expands from 5 tiers (A/B/C/M/S) to per-domain scoring. The 7-pillar composite gains resolution: instead of one "accuracy" number, Coeus gets 14 domain-specific accuracy signals.

### Rhea (RLVF Fitness)
The fitness function `F(T) = Σwᵢ·Sᵢ - λ·σ(S)` gains two improvements:
1. **Tier B weighting.** Judgment accuracy (recognizing ambiguity, detecting presuppositions) is weighted higher than parsing accuracy. This pushes evolved models toward metacognition.
2. **Domain diversity.** The variance penalty σ(S) is computed across domains, not just tools. A model that scores high on logic but zero on temporal reasoning is penalized.

### Coeus (Causal Analysis)
Coeus rebuilds after each expansion phase. The key hypotheses:
- **Phase 1 (Temporal + Probabilistic):** Do dynamics-first tools (Neural Oscillations, Ergodic Theory, Statistical Mechanics) improve on their home turf?
- **Phase 2 (Causal + Linguistic):** Does Falsificationism differentiate from FEP on causal traps?
- **Phase 3 (Meta-Reasoning):** Which tool families handle Tier B judgment tasks?
- **Phase 4 (Full coverage):** What's the global competency map across 105 categories × 239 genuine tools?

---

## Phased Build Order

| Phase | Domains | New Categories | Hypothesis | Coeus Rebuild |
|-------|---------|---------------|------------|---------------|
| **1** | Temporal (D) + Probabilistic Tier 1 | 12 | Dynamics-first tools wake up | Yes |
| **2** | Causal (F) + Linguistic (E) + Formal Logic Tier 1 | 20 | Middle-tier differentiation | Yes |
| **3** | Meta-Reasoning (I) + Theory of Mind (M) + Multi-Step (K) | 14 | RLVF signal calibration | Yes |
| **4** | Arithmetic (C) + Spatial (H) + Set Theory (G) + remaining | 44 | Full coverage | Yes |

Each phase adds categories, triggers Coeus rebuild, tests whether specific tool families activate on their predicted home turf, and expands the evaluation surface for all downstream systems.

---

## Implementation Architecture

### Generator Pattern
```python
# In trap_generator_sphinx.py (or phased files)
def cat_base_rate_neglect(rng: random.Random) -> dict:
    """Generate a base rate neglect trap with random parameters."""
    prevalence = rng.choice([0.001, 0.01, 0.05])
    accuracy = rng.choice([0.95, 0.99])
    # ... compute correct answer from parameters ...
    return {
        "prompt": f"A disease affects 1 in {int(1/prevalence)} people...",
        "candidates": [...],
        "correct": correct_answer,
        "category": "base_rate_neglect",
        "tier": "A",
        "domain": "probabilistic",
    }
```

### Tier Tagging
Every trap carries `tier: "A"` or `tier: "B"`. Coeus, the RLVF fitness function, and eval_v2 all track per-tier accuracy separately.

### Adversarial Composition
Nemesis metamorphic relations compose with all categories:
```
105 base categories × 12 MRs × parametric variation = unbounded
```

### Provenance
All Sphinx-generated traps carry `provenance: "evaluation"` or `provenance: "curriculum"`. Adversarial variants from Nemesis carry `provenance: "adversarial"`. The hard gate prevents cross-contamination into training.

---

## Relationship to Other Projects

```
                    ┌─────────────────────┐
                    │      SPHINX         │
                    │  105 categories     │
                    │  14 domains         │
                    │  Tier A / Tier B    │
                    │  ∞ parametric       │
                    └────────┬────────────┘
                             │
            ┌────────────────┼────────────────┐
            ↓                ↓                ↓
    ┌───────────────┐ ┌─────────────┐ ┌──────────────┐
    │  HEPHAESTUS   │ │   NEMESIS   │ │    APOLLO    │
    │  Gate 5 eval  │ │  MR × 105   │ │  Curriculum  │
    │  Forge/Scrap  │ │  Adversarial│ │  Evolution   │
    └───────┬───────┘ └──────┬──────┘ └──────┬───────┘
            │                │               │
            ↓                ↓               ↓
    ┌───────────────────────────────────────────────┐
    │                   COEUS                       │
    │  Per-domain causal analysis                   │
    │  Tier A vs Tier B competency mapping          │
    │  Tool × Category interaction matrix           │
    └───────────────────┬───────────────────────────┘
                        ↓
            ┌───────────────────────┐
            │    IGNIS / RHEA       │
            │  eval_v2 expansion    │
            │  RLVF fitness         │
            │  Tier B weighting     │
            └───────────────────────┘
```

Sphinx is not inside any agent. It sits above all of them as the shared definition of the problem space. When Sphinx grows, everything downstream gains resolution.

---

## The Anti-Goodhart Properties

1. **Parametric generation** — infinite surface variants prevent memorization
2. **105 categories** — too many to dispatch-table (the CAITL v3 monoculture can't happen at this scale)
3. **Tier B judgment traps** — no regex can detect "this question contains a false presupposition"
4. **Nemesis composition** — 105 × 12 MRs = adversarial pressure that adapts faster than tools can specialize
5. **Phased expansion with Coeus** — each phase tests whether tools genuinely activate concept-specific logic, not just broader pattern matching
6. **Cross-domain variance penalty** — the RLVF fitness function penalizes models that game one domain while ignoring others

---

## What Sphinx Replaces

Before Sphinx, "good reasoning" was defined by 15 hand-picked traps. Tools learned to dispatch on 15 patterns. Models trained against those tools learned to produce outputs that trigger those dispatchers. The definition of reasoning was a 15-word vocabulary.

After Sphinx, "good reasoning" is defined by 105 categories across 14 domains, with infinite parametric variants, adversarial mutations, and a Tier A/B split between "can you parse" and "can you think." The definition of reasoning is a taxonomy of failure modes — and the only way to pass all of them is to actually reason.

The Sphinx doesn't care how eloquent you are. It asks a riddle. You answer correctly, or you don't pass.
