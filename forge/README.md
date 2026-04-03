# Forge — Tiered Architecture

The forge is an evolutionary ratchet. Each tier's output becomes the next tier's primitives.

## Overview

| Tier | Location | Mines | Forges From | Battery | Best Accuracy |
|------|----------|-------|-------------|---------|---------------|
| **T1** | `agents/hephaestus/` | Concept triples (Sphinx ontology) | Raw LLM generation | 89-cat base + 19-cat computation-first (108 total) | 74% |
| **T2** | `forge/v2/` | Tool combinations (pairs of T1 tools) | Composing T1 tools | 12-cat battery from T1 failure modes | 100% on T2, 57% on T1 |
| **T3** | `forge/v3/` | Cross-tier substrate + computational lenses | Composing T1+T2 tools | 20-cat battery, 100 brutal traps | 100% on T3, 56% on T1 |

**Combined coverage:** T1+T2+T3 covers everything no single tier can.

## How Each Tier Works

Every tier has the same four components:

1. **Nous** — mines candidates (what to build next)
2. **Hephaestus** — forges tools from those candidates
3. **Battery** — validates tools against adversarial traps
4. **Nemesis** — co-evolves adversarial cases against forged tools

The difference is *what* each Nous mines and *what primitives* the forge has access to.

### Tier 1 (Original)

- **Nous mines:** Cross-field concept triples from the Sphinx 105-category ontology
- **Hephaestus forges:** Python reasoning tools from scratch via API (Qwen-397B / Augment fallback)
- **Battery:** 108 categories (89 base + 19 computation-first), 42% accuracy threshold
- **Primitives available:** None (raw generation)
- **Runs 24/7 via API.** Left untouched.

### Tier 2 (Tool Combinations)

- **Nous mines:** Pairs of T1 tools that might compose well
- **Hephaestus forges:** Ensemble tools that import and combine T1 tools
- **Battery:** 12 categories drawn from T1's persistent failure modes (Simpson's paradox, strategic deception, scheduling, etc.)
- **Primitives available:** All passing T1 tools

### Tier 3 (Cross-Tier Substrate)

- **Nous mines:** Cross-tier substrate pairs + computational science lenses
- **Hephaestus forges:** Tools that compose T1 and T2 tools through a computational lens
- **Battery:** 20 categories, 100 traps (cross-domain fusion, recursive belief, game theory, adversarial framing, etc.) with anti-NCD defenses
- **Primitives available:** All passing T1 + T2 tools
- **Uses Frame H (Primordial Soup):** 27 composable reasoning building blocks from `forge_primitives.py`

## Directory Structure

```
forge/
  README.md              ← this file
  v2/
    nous_t2/             ← T2 concept miner
    hephaestus_t2/       ← T2 forge + forged tools
    nemesis_t2/          ← T2 adversarial grid
    coeus_t2/            ← T2 coverage tracking
  v3/
    nous_t3/             ← T3 concept miner
    hephaestus_t3/       ← T3 forge + forged tools
    nemesis_t3/          ← T3 adversarial grid
    coeus_t3/            ← T3 coverage tracking

agents/hephaestus/       ← T1 (original, unchanged)
```

## Running Each Tier

### T1 (existing pipeline)
```bash
run_forge_pipeline.bat
# or with Augment fallback:
run_forge_pipeline.bat --use-aggie-api
```

### T2
```bash
cd forge/v2
python nous_t2/nous_t2.py --unlimited --delay 2.0
python hephaestus_t2/hephaestus_t2.py --poll-interval 300
python nemesis_t2/nemesis_t2.py --poll-interval 120
```

### T3
```bash
cd forge/v3
python nous_t3/nous_t3.py --unlimited --delay 2.0
python hephaestus_t3/hephaestus_t3.py --poll-interval 300
python nemesis_t3/nemesis_t3.py --poll-interval 120
```

### Break-Glass (Frame H, preferred)

When APIs are down, Claude Code agents forge directly using Frame H + `forge_primitives.py`:
- 27 composable building blocks (logic, probability, graph/causal, constraints, arithmetic, temporal, belief tracking, meta/calibration)
- LLM recombines primitives instead of coding from scratch
- Proven: 15 tools forged at 100% pass rate, up to 74% accuracy

## The Evolutionary Ratchet

```
T1 forges raw tools
  └─ T1 failures reveal hard categories
       └─ T2 mines tool combinations targeting those gaps
            └─ T2 failures reveal cross-domain gaps
                 └─ T3 mines substrate pairs + computational lenses
                      └─ T3 output is the next tier's primitives
                           └─ ...
```

Key properties:
- **Tiers run in parallel.** Lower tiers never stop — they are substrate generators.
- **LLM randomness is the mutation operator** at every tier.
- **Each tier has its own battery, ledger, forge directory, and Nemesis.**
- **No tier depends on another tier being "done."**

## Cross-Tier Performance Matrix

|  | T1 Battery | T2 Battery | T3 Battery |
|--|-----------|-----------|-----------|
| **T1 tools** | 74% | 0% | ~0% |
| **T2 tools** | 57% | 100% | 1% |
| **T3 tools** | 56% | 33% | 100% |
| **Combined** | covered | covered | covered |

Each tier dominates its own battery and contributes partial coverage to others. The ensemble is strictly stronger than any single tier.

## How to Add a New Tier

1. Create `forge/v{N}/` with subdirectories: `nous_t{N}/`, `hephaestus_t{N}/`, `nemesis_t{N}/`, `coeus_t{N}/`
2. Define what Nous mines at this tier (must be different from existing tiers)
3. Define the primitives available (all passing tools from tiers 1..N-1)
4. Build a battery from the failure modes of tiers 1..N-1
5. Copy and adapt the T2/T3 agent scripts, updating import paths and battery references
6. Add the tier to the cross-tier performance matrix
7. Update this README and the Pipeline Orchestrator role definition
