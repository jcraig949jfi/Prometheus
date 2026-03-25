# Coeus — Causal Intelligence Layer

*Titan of rational inquiry, the axis around which knowledge revolves.*

Sits between **Nous** (theory) and **Hephaestus** (forge), using causal
discovery to learn which concepts, fields, and score dimensions actually
drive forge success. Produces prescriptive directives that steer
Hephaestus's code generation toward proven patterns.

## Pipeline Position

```
Nous (generate + score) → Coeus (causal analysis + enrichment) → Hephaestus (forge)
                                       ↑
                           Hephaestus auto-triggers every 50 forges
```

Coeus also feeds back to Nous via **sampling weights** — concepts with positive
forge effects are oversampled, inhibitors are undersampled.

## What It Does

### 1. Builds a Causal Graph

From all Nous scores + Hephaestus outcomes (forged/scrapped):

- **Which concepts causally drive forge success** vs just correlate?
- **Which score dimensions predict working code?** (Answer: only implementability)
- **Which concept pairs synergize or conflict?**
- **Which fields help or hurt?**
- **Are any correlations confounded** by unobserved variables?
- **What happens if we remove a concept?** (counterfactual probabilities)

### 2. Generates Prescriptive Enrichments

For each triplet, produces a context block injected into Hephaestus's prompt.
Not descriptive statistics — **concrete code-generation directives**:

```
- **Active Inference**: Strong primary driver of forge success. Make this concept
  the core architectural pattern of the evaluate() method. Historical forge rate: 50%.
  This concept has a proven, unconfounded mechanical advantage.

- **Topology**: Historical inhibitor. Tools relying heavily on this tend to fail
  reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence()
  wrapper or structural parsing support only.

GLOBAL: The final tool must strictly beat the NCD compression baseline.
Use structural parsing as the primary scoring signal.
```

### 3. Feeds Sampling Weights to Nous

`graphs/concept_scores.json` contains per-concept forge effects. Nous reads this
on startup to bias triple sampling toward productive concepts.

## Methods (graceful degradation)

| Method | Package | What it does | When it runs |
|--------|---------|-------------|--------------|
| L1 regression | scikit-learn | Conditional associations | Always |
| NOTEARS/GES | causal-learn | Structure learning on score DAG | If installed |
| LiNGAM | lingam | Causal ordering via non-Gaussianity | If installed |
| FCI | causal-learn | Latent confounder detection | If installed |
| DAGMA | dagma | Non-linear synergies via MLP | If installed + 200 forges |
| Interventional | numpy | Counterfactual P(forge \| do(remove X)) | Always (20+ attempts) |

## Usage

```bash
# Full rebuild: causal graph + all enrichments
python agents/coeus/src/coeus.py

# Usually auto-triggered by Hephaestus every 50 forges
```

## Output

- **graphs/causal_graph.json** — Full causal model (influences, synergies, confounders, interventional)
- **graphs/concept_scores.json** — Per-concept scores (used by Hephaestus priority sort + Nous sampling weights)
- **enrichments/{combo_key}.json** — Per-triplet enrichment with prescriptive `enrichment_text`

## Current Findings

| Concept | Forge Effect | Forge Rate |
|---------|-------------|------------|
| Criticality | +1.155 | 50% |
| Sparse Autoencoders | +0.919 | 50% |
| Active Inference | +0.789 | 50% |
| Falsificationism | +0.655 | 40% |
| Topology | -0.462 | 0% |
| Epigenetics | -0.299 | 0% |

- **Implementability** is the only Nous score dimension predicting forge success (+0.221)
- **Cognitive Science** and **Theoretical Neuroscience** fields drive forges
- **Top synergy**: Ergodic Theory + Theory of Mind (+0.446)

## Dependencies

- `numpy`, `scikit-learn`, `scipy` (required)
- `causal-learn` (optional: NOTEARS, GES, FCI)
- `lingam` (optional: LiNGAM causal ordering)
- `dagma` (optional: non-linear DAG learning, needs 200+ forges)
