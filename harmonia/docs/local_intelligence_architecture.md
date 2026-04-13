# Local Intelligence Architecture
## Breaking the API token wall
### 2026-04-13 — Design for tomorrow's build

---

## The Problem

Generating millions of hypotheses at $0.01-0.10 per LLM call = $10K-$100K per overnight run. The API token cost literally gates sample size. The 99.9% failure rate means paying frontier prices for garbage.

## The Solution: Local SLM + Algorithmic Intelligence

The frontier LLM is used ONCE: to design the gene templates and seed the initial population. Then a local 7B model (free, infinite tokens) handles ALL mutation and recombination. The evolutionary algorithm IS the intelligence — the LLM is just the crossover operator.

---

## The Gene Format

This is the critical design question: what format lets a 7B model reliably parse and recombine hypotheses without hallucinating syntax errors?

### Answer: Structured JSON hypothesis templates

NOT free-form natural language. NOT code. A fixed-schema JSON object that the 7B model fills in by slot-filling, not by reasoning.

```json
{
  "id": "hyp_00042",
  "domain_a": "elliptic_curves",
  "domain_b": "maass_forms",
  "feature_a": "spacing_gamma2_gamma1",
  "feature_b": "coefficient_kurtosis",
  "coupling": "spearman",
  "conditioning": ["log_conductor"],
  "null_model": "permutation",
  "resolution": 2000,
  "prediction": "positive_correlation",
  "predicted_kill": "F31_prime_mediated",
  "novelty_tag": "spectral_to_information"
}
```

### Why this works for a 7B model:

1. **Fixed schema.** The model doesn't generate free-form text — it fills slots from controlled vocabularies. Each field has a finite set of valid values.

2. **Controlled vocabularies:**
   - `domain_a/b`: one of 42 known domains
   - `feature_a/b`: one of ~200 known extractable features (enumerated)
   - `coupling`: one of [spearman, mi, wasserstein, ks, ttcross, cosine]
   - `conditioning`: subset of [log_conductor, rank, torsion, cm, degree, level]
   - `null_model`: one of [permutation, shuffle_within, block_shuffle, synthetic_gue]
   - `resolution`: one of [100, 500, 2000, 10000]
   - `prediction`: one of [positive_correlation, negative_correlation, no_effect, threshold_effect]
   - `predicted_kill`: one of F1-F38 (which test is most likely to kill this)
   - `novelty_tag`: one of [magnitude, ordinal, spectral, topological, information, algebraic]

3. **Mutation = slot swapping.** The 7B model takes two parent hypotheses and produces a child by:
   - Swapping one domain (keep the rest)
   - Swapping the feature pair (keep the domains)
   - Changing the coupling method
   - Adding or removing a conditioning variable
   - Changing the resolution

4. **Validation is trivial.** Parse the JSON. Check every field against the controlled vocabulary. Reject malformed output instantly (no cost — just regenerate).

### The mutation prompt for the 7B model:

```
Given these two surviving hypotheses:
PARENT_A: {json}
PARENT_B: {json}

Generate a new hypothesis by combining elements from both parents.
You MUST use the exact field names and values from this vocabulary:
{controlled_vocabulary}

Output ONLY valid JSON matching this schema:
{schema}
```

This is trivial for a 7B model. It's slot-filling with constraints, not reasoning. Qwen-2.5-7B, Llama-3.1-8B, Mistral-7B — any of them handle this reliably at 4-bit quantization.

---

## The Full Architecture

### Machine 1 (SpectreX5, RTX — 16GB VRAM)
**Role:** Generator + Evolutionary Controller

- Local 7B model (vLLM or llama.cpp, 4-bit quantized)
- MAP-Elites archive
- Kill taxonomy database (SQLite)
- Constraint set (JSON)
- Hypothesis queue (Redis or filesystem)

**Loop (runs continuously):**
```
while True:
    parents = archive.select_parents(tournament_size=5)
    children = local_llm.mutate(parents, constraints)  # 7B, local, free
    for child in validate(children):
        queue.push(child)
    results = queue.get_completed()
    for result in results:
        archive.update(result)
        if result.killed:
            kill_taxonomy.add(result.failure_mode)
            constraints.update(result)
```

### Machine 2 (Skullport, or same machine CPU)
**Role:** Executor (Nemesis)

- Tensor train (tntorch, CPU)
- Battery v2 (F1-F38, numpy/scipy)
- Ungated coupling function
- Live Postgres connection (3.8M objects)

**Loop (runs continuously):**
```
while True:
    hypothesis = queue.pop()
    raw_coupling = ungated_sweep(hypothesis)
    if raw_coupling.gradient > threshold:
        battery_result = run_full_battery(hypothesis)
        queue.push_result(battery_result)
    else:
        queue.push_result(killed_at="ungated_sweep", gradient=raw_coupling.gradient)
```

### Frontier LLM (API, used sparingly)
**Role:** Seed designer + periodic review

- Called ONCE at startup to design the initial population (50 seed hypotheses)
- Called ONCE per day to review the MAP-Elites grid and suggest strategic pivots
- Called when a hypothesis SURVIVES F24+ (rare event, worth the cost)
- Total API cost: ~$1-5/day instead of $10K/day

---

## The Evolutionary Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Population (MAP-Elites archive) | 500 cells (50 domains × 10 measurement types) | Covers the full exploration space |
| Generation size | 20 hypotheses | Fits in one batch of 7B inference |
| Tournament size | 5 | Moderate selection pressure |
| Mutation rate | 1-2 slots per child | Conservative — most structure preserved |
| Crossover rate | 50% | Half children from two parents, half from single-parent mutation |
| Kill threshold | F1 permutation null z < 2 | Hard gate — nothing passes without beating randomness |
| Gradient threshold | Raw coupling > 0.01 | Low bar for exploration — high bar for prosecution |
| Generations per night | 1000+ | At ~1 second per hypothesis (7B inference + battery), 20K hypotheses per night |

---

## The Throughput Math

- 7B model inference: ~0.5 seconds per hypothesis (fill 10 JSON slots)
- JSON validation: ~0.001 seconds
- Ungated tensor sweep: ~2 seconds per hypothesis (subsample to 2000 objects)
- Full battery (if gradient passes): ~10 seconds per hypothesis
- 95% killed at ungated sweep, 4% killed at battery, 1% survive

**Per night (8 hours):**
- ~15,000 hypotheses generated
- ~750 reach the battery
- ~150 survive the battery
- ~15 reach F24+ (deep survivors)
- ~1-2 survive the full gauntlet (if anything does)

**Cost: $0 in API tokens. Just electricity.**

---

## What the Frontier LLM Does (Sparingly)

### At startup (one-time):
- Design the 50 seed hypotheses for the initial population
- Define the controlled vocabulary for each field
- Identify the most promising void cells in the MAP-Elites grid
- Cost: ~$2

### Daily review (once per day):
- Read the MAP-Elites grid state
- Read the top 10 survivors and top 10 kills from the last 24 hours
- Suggest 5 strategic mutations that the 7B model wouldn't think of
- Update the controlled vocabulary if new feature types are needed
- Cost: ~$1

### Survivor analysis (rare event):
- When a hypothesis survives F24+ (expected: 1-2 per night)
- Deep analysis: is this known math? What would the next kill test be?
- Design specific adversarial attacks on the survivor
- Cost: ~$0.50 per survivor

**Total daily API cost: $3-5. Total monthly: $100-150.**
Compare to: $10K-100K for API-driven generation at scale.

---

## The Morning Report

After each overnight run, the system produces:

1. **MAP-Elites heat map** — which (domain, measurement) cells have survivors
2. **Top 5 survivors** — full profiles including all F-test results
3. **New kill modes** — any failure patterns not in the original 21
4. **Void analysis** — cells with 1000+ attempts and zero survivors (confirmed empty)
5. **Constraint evolution** — how the negative space changed overnight
6. **Gradient landscape** — which regions show consistent positive gradients even without survivors

We read the report. Decide which survivors to investigate. Design new seed hypotheses for the next night's run. The machine does the grinding. We do the thinking.

---

## Build Order (April 14)

### Morning:
1. `forge/gene_schema.json` — the hypothesis template with controlled vocabularies
2. `forge/kill_taxonomy.db` — SQLite table seeded with 21 kills
3. `forge/constraints.json` — 10 negative dimensions formalized

### Afternoon:
4. `forge/mutator.py` — local 7B model interface for hypothesis mutation
5. `forge/executor.py` — hypothesis → computable test → battery → result
6. `forge/map_elites.py` — adapted from existing `cartography/shared/scripts/map_elites.py`

### Evening:
7. `forge/autonomous_explorer.py` — the orchestration loop
8. First test run: 100 generations, verify the loop works
9. Start overnight run: 1000 generations

### April 15 morning:
10. Read the morning report. Analyze survivors. Iterate.

---

*The machine takes the failures. We take the survivors.*
*Build cost: 1 day. Run cost: electricity.*
*The API wall is broken. The exploration scales to infinity.*
