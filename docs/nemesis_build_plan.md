# Nemesis Build Plan — Adversarial Co-Evolution Engine

*"Are our evaluators measuring reasoning, or have they learned to pass tests?"*

---

## Status: MVP + ALL STRETCH GOALS COMPLETE

| Goal | Status | Key Result |
|------|--------|------------|
| MAP-Elites grid (12 MRs) | **DONE** | 23/100 cells filled after 2 cycles |
| Shrinking to minimal cases | **DONE** | 20+ tasks shrunk per cycle |
| Ground truth validation | **DONE** | Execution evaluator cross-check rejects ~25% of candidates |
| Continuous operation | **DONE** | Reloads tools each cycle, 2min intervals |
| S1: Lineage tracking | **DONE** | Depth tracked, deep lineages prioritized in grid |
| S2: Per-tool difficulty model | **DONE** | Boundary MRs identified, persisted across cycles |
| S3: Gate 6 in Hephaestus | **DONE** | Tools must survive >= 50% of adversarial set |
| S4: Coeus dual graph | **DONE** | Goodhart warnings operational (Criticality flagged, Compressed Sensing undervalued) |
| SS1: MR composition evolution | Not started | Queued for future |
| SS2: RLVF fitness formula | **DONE** | F(T) = Σwᵢ·Sᵢ - λ·σ(S) with 122 tools |
| SS3: Athena plateau detection | Not started | Queued for future |

### First Results

- IBAI v2 drops from **67% static → 46% adversarial** — the Goodhart gap is real
- `info_theory_x_criticality_x_pragmatics` hits **85% adversarial survival** despite not being a static leader
- `paraphrase → chain_extend` is the most effective mutation chain (112 total tools broken)
- Coeus Goodhart warnings: **Criticality** (+1.249 forge, 38% adversarial) is Goodharting; **Compressed Sensing** (0% forge, 70% adversarial) is undervalued
- RLVF fitness function correctly scores right answers higher than wrong answers across 122 tools

---

## Core Principles (from Titan Council convergence)

1. **MAP-Elites for failure space** — not a bag of adversarial tasks, a quality-diversity
   grid that ensures coverage of the entire behavioral boundary.

2. **Metamorphic relations as formal framework** — not ad-hoc mutation categories,
   formal specifications of how inputs and outputs should co-vary.

3. **Minimal failing cases via shrinking** — when a task breaks a tool, automatically
   find the simplest mutation that still breaks it.

4. **Semantic equivalence as the Goodhart detector** — if a tool breaks on paraphrase,
   it's measuring syntax, not reasoning.

5. **Pure algorithmic** — no API calls, no neural models. NCD for novelty/coverage.

6. **Provenance tagging** — every data point tagged with source. Adversarial data
   never enters training. Hard gate in code (not convention).

---

## Architecture

### Pipeline Position

```
Nous → Coeus → Hephaestus (Gate 5 + Gate 6) ← Nemesis
                    ↑                              ↓
                    └── targeted_forge_requests ────┘
                    ↑                              ↓
              Coeus ←── adversarial_results.jsonl ──┘
                    ↓
              Nous sampling weights (Goodhart demotion)
```

### Three Generation Strategies

1. **Random** — apply random MR chains to seed traps (exploration)
2. **Targeted** — generate tasks for empty grid cells (coverage)
3. **Boundary** — target each tool's decision boundary using the difficulty model (pressure)

### Continuous Cycle

```
loop:
    1. Load current tool library (picks up newly forged tools)
    2. Generate tasks: random + targeted + boundary
    3. Validate ground truth (execution evaluator cross-check)
    4. Evaluate all tools against all validated tasks
    5. Update per-tool difficulty model
    6. Novelty check (NCD) + place in MAP-Elites grid
    7. Track adversarial lineage depth
    8. Shrink failures to minimal cases
    9. Write: failure report, adversarial results (Coeus), targeted forge requests
   10. Sleep → repeat
```

### MAP-Elites Grid (10×10)

```
          Linguistic Obfuscation →
     1  2  3  4  5  6  7  8  9  10
  1 [.][X][X][X][X][.][.][.][.][X]   X = filled
  2 [.][.][.][.][X][.][X][X][.][.]   B = blind spot
  3 [X][.][.][.][X][X][.][.][.][.]   . = empty
  4 [.][X][.][X][.][.][.][.][.][.]
  5-10: mostly empty (needs more chain_extend compositions)
```

Fitness per cell = tool disagreement + lineage depth bonus + blind spot bonus.

### 12 Metamorphic Relations

| MR | Transform | Expected | Δ Complexity | Δ Obfuscation |
|----|-----------|----------|-------------|---------------|
| comparison_flip | Swap A/B | flip | 0 | 0 |
| verb_inversion | "larger" → "smaller" | flip | 0 | +1 |
| negation_inject | Add "not" | flip | +1 | +1 |
| premise_shuffle | Reorder premises | same | 0 | +2 |
| distractor_add | Add irrelevant detail | same | 0 | +3 |
| passive_voice | Active → passive | same | 0 | +3 |
| paraphrase | Rewrite preserving meaning | same | 0 | +5 |
| chain_extend | Add chain elements | same | +2 | 0 |
| conditional_weaken | "if P then Q" → "maybe Q" | computed | +2 | +1 |
| affirm_consequent | Tempt invalid inference | computed | +3 | +1 |
| numeric_distractor | Add misleading number fact | same | +1 | +4 |
| scale_transform | Multiply numbers by K | same | 0 | +2 |

MRs compose: `paraphrase ∘ chain_extend ∘ distractor_add` targets (complexity=3, obfuscation=8).

### Feedback Loops

**Nemesis → Coeus:** `adversarial_results.jsonl` with per-tool results per task.
Coeus builds a second causal graph (adversarial robustness) and computes Goodhart
divergence between forge success and adversarial survival.

**Nemesis → Hephaestus:** `targeted_forge_requests.jsonl` maps blind spot MR
categories to concept triple suggestions. Blind spots become high-priority forge targets.

**Nemesis → Nous (via Coeus):** Goodhart indicators demote concepts in sampling
weights. Undervalued concepts (high adversarial, low forge) get boosted.

### RLVF Fitness Function

```
F(T) = Σ wᵢ · Sᵢ(T) - λ · σ(S)
```

- 122 tools, weights from adversarial robustness
- EFME v2 highest weight (0.739), logical consistency checker lowest (0.261)
- λ = 2.0 (variance penalty prevents gaming individual tools)
- Provenance gate: adversarial episodes raise ValueError if they touch training

---

## Directory Structure

```
agents/nemesis/
├── src/
│   ├── nemesis.py           — Main engine (continuous loop, 3 generation strategies)
│   ├── metamorphic.py       — 12 MR definitions + composition + targeted chains
│   ├── map_elites.py        — Grid + ToolDifficultyModel + novelty check
│   ├── shrink.py            — Iterative simplification to minimal failing case
│   ├── evaluator.py         — Run tools, compute disagreement, detect blind spots
│   ├── reporter.py          — Reports + targeted forge requests + adversarial JSONL
│   └── validators.py        — Ground truth validation (execution evaluator cross-check)
├── grid/grid.json           — Serialized grid + difficulty model
├── reports/                 — Timestamped failure analysis markdown
├── adversarial/
│   ├── adversarial_results.jsonl     — For Coeus (provenance: adversarial)
│   └── targeted_forge_requests.jsonl — For Hephaestus (blind spot → concept request)
├── configs/manifest.yaml
└── README.md
```

---

## Remaining Work

| Item | Priority | Description |
|------|----------|-------------|
| MR composition evolution (SS1) | Medium | Evolve MR chains via GA — crossover/mutation over sequences |
| Athena plateau detection (SS3) | Low | Signal when grid stabilizes (no new cells/replacements for N cycles) |
| Fill high-complexity grid rows | High | Rows 5-10 mostly empty — need deeper chain_extend compositions |
| Increase adversarial set to 50+ cells | High | More cycles will fill the grid naturally |
| Connect to Rhea CMA-ES loop | High | Wire rlvf_fitness.py as the fitness term in evolve_lora_gate_v.py |

---

## Usage

```bash
# Continuous (default — 2min cycles, reloads tools)
python agents/nemesis/src/nemesis.py

# Single cycle
python agents/nemesis/src/nemesis.py --runonce

# More generation volume
python agents/nemesis/src/nemesis.py --n-random 100 --n-targeted 50

# Custom interval
python agents/nemesis/src/nemesis.py --poll-interval 300
```
