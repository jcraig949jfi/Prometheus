# Tiered Forge Pipeline — Design Document

**Date:** 2026-04-02
**Author:** Pipeline Orchestrator + James
**Status:** Design phase — Tier 1 running, Tier 2 ready to build

---

## Core Principle

Each tier's output is the next tier's primitives. Tiers run in parallel. Lower tiers never stop — they're the substrate generators for everything above. As tiers get higher, wins become rarer but more valuable. The forge is an evolutionary food chain.

```
Tier 1 (exists)    →  High volume, cheap, 8% yield, 42% battery
    ↓ substrate
Tier 2 (build now) →  Lower volume, higher quality, 74%+ battery
    ↓ substrate
Tier 3 (future)    →  Rare wins, deep reasoning, deliberation
    ↓ substrate
...
Tier N             →  Open problems
```

---

## Tier 1 — Leave As-Is

**Pipeline:** Nous → Coeus → Hephaestus → Nemesis
**What it does:** Mines concept triples, forges tools from scratch using base primitives
**Battery:** 89 Tier 1 + 19 Tier 2 = 108 categories, pass at 42% acc / 46% cal
**Output:** ~8% yield, tools in forge/, scraps with accuracy data in ledger
**Role:** Photosynthesis layer. Generates genetic diversity. Never stops.

**What Tier 2 consumes from Tier 1:**
- Forged tools (357+ .py files with accuracy/calibration metadata)
- Behavioral profiles (19 known archetypes from fingerprinting)
- Near-miss scraps (35-41% accuracy — almost passed, interesting structure)
- Failure category map (which categories each tool covers/misses)
- The forge_primitives.py base library

---

## Tier 2 — The Build

### Directory Structure

```
agents/
  nous_t2/            # Tier 2 concept miner
    src/
      nous_t2.py      # Mines tool combinations, not concept triples
    runs/             # Tool-combination hypotheses
  coeus_t2/           # Tier 2 enrichment
    src/
      coeus_t2.py     # Enriches with T1 performance data
    enrichments/      # Performance-based enrichments
  hephaestus_t2/      # Tier 2 forge
    src/
      hephaestus_t2.py
      prompts_t2.py
      forge_primitives_t2.py  # T1 best tools distilled into primitives
      test_harness_t2.py      # T2 battery (harder than T1)
      trap_generator_t3.py    # Generates T2-level traps
    forge/            # T2 forged tools
    scrap/            # T2 scraps (feed T3)
    ledger.jsonl      # T2 ledger (independent from T1)
  nemesis_t2/         # Tier 2 adversarial
    src/
      nemesis_t2.py   # Structural perturbation, not just surface rewording
    grid/
```

### Nous_T2 — Tool Combination Miner

**Input:** Tier 1 forged tools + behavioral profiles + failure maps
**Output:** Hypotheses about tool combinations

Tier 1 Nous asks: "What concepts combine interestingly?"
Tier 2 Nous asks: "What tools combine interestingly?"

Its concept pool is NOT the 95 abstract concepts. It's:
- 357+ forged T1 tools (with their accuracy, calibration, category coverage)
- 19 behavioral archetypes
- The failure category map (which tools fail where)
- Near-miss scraps (38-41%) that almost passed

**Nous_T2 triple structure:** `substrate_1 + substrate_2 + computational_science`

The first two elements are Tier 1 substrate (forged tools, near-miss scraps, behavioral
archetypes). The third element is a computational science drawn from the same 95-concept
pool as Tier 1 — but now it's a LENS, not a building block.

**Example T2 triples:**
- `T1_nash_solver(73%) + T1_oscillation_tool(45%) + Information Theory`
  → "What if you applied information-theoretic compression to the disagreement between these two tools?"
- `T1_bayesian_tool(68%) + T1_near_miss_simpsons(41%) + Ergodic Theory`
  → "What if you treated the Bayesian updater as an ergodic process that converges to the Simpson's paradox solution?"
- `T1_swarm_tool(74%) + T1_sat_solver(45%) + Error Correcting Codes`
  → "What if the swarm's disagreement pattern is a signal that ECC can decode?"

The LLM randomness is the mutation operator. It doesn't just wire A into B — it asks
a generative question about how the computational science transforms the relationship
between the substrate elements. This finds combinations no lookup table would produce.

**Scoring:** Composite of complementarity (do the substrate tools cover different
categories?), near-miss potential (does one almost pass on categories the other misses?),
novelty (is this lens untried with these tools?), and LLM-scored plausibility of the
proposed mechanism.

### Coeus_T2 — Performance Enrichment

**Input:** T1 ledger, T1 battery results per tool, behavioral fingerprints
**Output:** Enrichment data for Nous_T2 hypotheses

Instead of mining literature (like T1 Coeus), T2 Coeus mines the data:
- Per-tool category coverage matrices
- Pairwise tool complementarity scores
- Failure mode clustering (which tools fail for the same reason?)
- Scrap analysis (what's the distribution of near-misses by category?)
- Temporal trends (is T1 getting better or plateauing?)

### Hephaestus_T2 — Composition Forge

**Input:** Nous_T2 hypotheses + Coeus_T2 enrichments
**Output:** Tools that compose/chain T1 tools

**Key difference from T1:** T1 Hephaestus generates tools from scratch. T2 Hephaestus composes existing tools.

**forge_primitives_t2.py contains:**
- All base primitives from forge_primitives.py (Tier 1)
- Best T1 tools distilled into callable functions
- NEW higher-order primitives:
  - `deliberate(solvers, prompt, candidates)` — try each solver, compare, backtrack
  - `perspective_shift(prompt, viewpoints)` — reframe from multiple POVs
  - `self_critique(answer, prompt, constraints)` — check if answer is consistent
  - `analogize(prompt, known_templates)` — map to nearest known problem type
  - `ensemble_vote(solvers, prompt, candidates)` — majority vote with confidence weighting
  - `error_correct(solvers, prompt, candidates)` — 2-of-3 redundancy check

**Prompts_T2 frames:**
- Frame H2-A: Deliberation (try-check-backtrack pipeline)
- Frame H2-B: Ensemble (error-correcting multi-tool composition)
- Frame H2-C: Perspective (multi-viewpoint analysis)
- Frame H2-D: Grafting (extract a specific parser from a scrap, graft onto a passing tool)

### Battery_T2 — The 48 Failures

**Seed:** The 48/186 traps that 74% tools currently fail.

**Categories (from Agent 3's failure analysis):**
- Simpson's paradox (aggregate vs subgroup reversal)
- Causal confounding (hidden common cause)
- Conjunction fallacy (specific vs general probability)
- Strategic deception in ToM (what does the liar want me to think?)
- Rate-of-change analysis (derivatives without calculus)
- Scheduling conflicts (parallel vs sequential task inference)
- Complex temporal ordering (multi-clause temporal chains)
- Framing effects (same data, different presentation, different answer)

**Growth:** Nemesis_T2 generates NEW traps in these categories, progressively harder.

### Nemesis_T2 — Structural Adversarial

T1 Nemesis does surface perturbation: same logic, different words.
T2 Nemesis does structural perturbation:
- Same logic, completely different domain (math problem → social reasoning)
- Compose two easy problems into one hard problem
- Embed a solved problem inside a misleading context
- Create problems where the obvious approach fails but a specific T2 primitive succeeds

---

## Tier 2 Pass Criteria

| Metric | Tier 1 threshold | Tier 2 threshold |
|--------|-----------------|-----------------|
| Accuracy | > 42% | > 74% |
| Calibration | > 46% | > 66% |
| T2 battery accuracy | N/A | > 50% on the 48 hard traps |
| Tool composition | N/A | Must chain 2+ T1 tools or T2 primitives |

---

## Data Flow Between Tiers

```
Tier 1 Hephaestus
    │
    ├── forge/*.py (passing tools) ──────→ Nous_T2 concept pool
    ├── scrap/*.py (near-misses) ────────→ Nous_T2 candidate grafts
    ├── ledger.jsonl (all attempts) ─────→ Coeus_T2 analysis
    ├── behavioral_fingerprints.json ────→ Coeus_T2 archetype map
    └── battery results per tool ────────→ Battery_T2 seed
                                              │
                                              ▼
                                    Tier 2 Hephaestus
                                         │
                                         ├── forge/*.py ──→ Tier 3 (future)
                                         └── ledger.jsonl ──→ Tier 3 (future)
```

---

## Build Order

### Phase 1: Scaffold (now)
- [ ] Create directory structure for agents/*_t2/
- [ ] Build forge_primitives_t2.py (T1 tools + higher-order primitives)
- [ ] Build trap_generator_t3.py (T2 battery from the 48 failures)
- [ ] Build test_harness_t2.py (T2 battery runner)

### Phase 2: Forge first (validate the concept)
- [ ] Manual break-glass forge of 5-10 T2 tools using Claude Code
- [ ] Validate against T2 battery
- [ ] Confirm T2 tools beat T1 tools on hard categories

### Phase 3: Automate
- [ ] Build nous_t2.py (tool combination miner)
- [ ] Build coeus_t2.py (performance enrichment)
- [ ] Build hephaestus_t2.py (composition forge)
- [ ] Build nemesis_t2.py (structural adversarial)
- [ ] Build run_forge_t2_pipeline.bat

### Phase 4: Close the loop
- [ ] Nous_T2 reads T1 output automatically
- [ ] T2 pipeline runs alongside T1
- [ ] Monitor T2 pass rate and battery difficulty co-evolution
- [ ] When T2 starts producing, design Tier 3

---

## Decision Authority

| Decision | Authority |
|----------|-----------|
| Tier 2 architecture | James (this doc) |
| Build scaffold | Autonomous |
| Break-glass forge T2 tools | Autonomous (report results) |
| Automate T2 pipeline | Ask James (new agents, machine load) |
| Start Tier 3 design | James (when T2 is producing) |
| Modify Tier 1 | Ask James (leave it alone by default) |

---

## Open Questions

1. **How do T1 tools become T2 primitives?** Auto-distill (extract the evaluate() function into a callable), or manually curate the best ones?
2. **How often does T2 re-scan T1?** Every N hours? On ledger change? Manual trigger?
3. **Should T2 scraps flow back to T1?** A T2 scrap might contain a novel parser that T1 could use.
4. **When is a tier "mature" enough to spawn the next?** Pass rate threshold? Number of forged tools? Coverage of its battery?

## Resolved Questions

- **What is Nous_T2's concept pool?** (Resolved 2026-04-02)
  Triples are `substrate_1 + substrate_2 + computational_science`. First two are T1 tools/scraps,
  third is a computational science from the 95-concept pool used as a LENS to guide combination.
  LLM randomness is the mutation operator — the generative question "how does this science
  transform the way these tools work together?" produces combinations no lookup would find.
