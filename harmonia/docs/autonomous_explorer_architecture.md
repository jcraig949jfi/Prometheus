# The Autonomous Explorer: Architecture for Tomorrow
## From manual exploration to evolutionary ghost hunting
### 2026-04-13 → Build starts 2026-04-14

---

## Why This, Why Now

The exploration phase is exhausted. 21 kills, 0 novel bridges, 1 weak survivor. Human-driven hypothesis generation has hit the wall — the failure rate is 99.9% and the emotional whiplash of manual generation burns you out. The instrument (40-test battery, 3.8M calibration, adversarial ecosystem) is the sharpest tool we've built. But we're still swinging it by hand.

The pivot: shift the burden of failure from humans to machines. Build an adversarial evolutionary ecosystem where the machine experiences millions of rejections while we sleep. We step back in only to analyze the battle-tested survivors.

This is the Charon research cycle with a massive performance upgrade: structured constraint memory, ungated exploration, quality-diversity evolution, and the full precision-fixed battery as the fitness function.

---

## Architecture: Three Layers

### Layer 1: The Nemesis (Falsification Environment)

The 10 negative dimensions and 21 kill signatures, locked in as absolute environmental constraints. Anything that touches these dies instantly. The Nemesis doesn't search — it destroys.

**Components:**
- `battery_v2.py` (F1-F38) — the 40-test gauntlet
- `cross_domain_protocol.py` — 7-layer cross-domain filter
- `kill_taxonomy.db` — structured SQLite table of all kills:
  ```
  (kill_id, hypothesis_type, failure_mode, F_test_that_killed,
   domain_pair, what_it_taught, constraint_added, timestamp)
  ```
- `negative_dimensions.json` — the 10 formal constraints:
  ```
  NOT ordinal, NOT magnitude, NOT distributional, NOT preprocessing,
  NOT engineering, NOT tautology, NOT prime-mediated, NOT partial-artifact,
  NOT trivial-baseline, NOT small-prime-localized
  ```
- Ungated tensor coupling (raw MI/rank correlation, no gates) for exploration
- Gated tensor coupling (full battery) for prosecution

**The Nemesis rule:** A hypothesis survives if and only if:
1. The ungated coupling shows a positive gradient with resolution
2. The signal appears from ≥ 2 independent measurement angles
3. The full 40-test battery cannot kill it
4. It is NOT consistent with any of the 21 known kill signatures

### Layer 2: The Sovereign Generator (Hypothesis Factory)

A frontier LLM (Claude/GPT-4/DeepSeek) that proposes computable hypotheses. Not RL — prompt engineering with structured memory. The key innovation: the prompt INCLUDES the full constraint set, so the LLM reasons about what's POSSIBLE given everything we've eliminated.

**The prompt template:**
```
You are a mathematical hypothesis generator for Project Prometheus.

CONSTRAINTS (the hypothesis MUST satisfy ALL of these):
{10 negative dimensions}
{21 kill signatures — do NOT propose anything matching these patterns}
{7 calibration anchors — the hypothesis must be consistent with known math}

AVAILABLE DATA:
{42 domains, key datasets, object counts}

SURVIVING SIGNALS:
{spectral tail z=-25.7, alpha=0.464}
{any new survivors from this round}

TASK: Propose 10 computable hypotheses that:
1. Are testable with existing data
2. Do NOT match any known kill pattern
3. Specify: the claim, the test, the predicted failure mode,
   and what we learn if it survives OR dies
4. Vary across different mathematical domains and approaches
5. Include at least 2 that probe the void regions (low-signal areas)

Rate each hypothesis: novelty (1-5), kill probability (1-5),
information value if killed (1-5).
```

**Mutation operators (the "genes"):**
- Domain pair swaps (test the same structure in different domains)
- Feature set variation (same domain, different measurement angles)
- Resolution scaling (same test at 10x more data)
- Conditioning variation (add/remove confounds)
- Representation change (raw data vs log vs rank vs spectral)
- Null model variation (different shuffling strategies)
- Threshold variation (vary the detection sensitivity)

### Layer 3: The Forge (Evolutionary Search)

MAP-Elites or NSGA-II wrapping the Generator + Nemesis. The population is hypotheses. The fitness is survival depth (how many F-tests passed before death). The diversity axes are: domain, measurement type, and mathematical primitive.

**The MAP-Elites grid:**
- X-axis: Domain pair (110 possible pairs from 42 domains, binned into 10 categories)
- Y-axis: Measurement type (categorical: correlation, distribution, topology, spectral, information-theoretic)
- Cell: Best-surviving hypothesis for this (domain, measurement) niche

**Each generation:**
1. Generator proposes N hypotheses (N = 10-50, LLM calls)
2. Each hypothesis is translated to a computable test (template matching)
3. Ungated tensor sweep runs the test (raw coupling, gradient tracking)
4. Survivors (positive gradient + multi-angle) enter the battery
5. Results logged: kill/survive, failure mode, F-tests passed, signal strength
6. Kill taxonomy updated with new failure modes (if novel)
7. MAP-Elites grid updated: if this hypothesis beat the current occupant of its cell, replace
8. Generator receives updated constraints for next round

**Mutation:** When spawning new hypotheses, the Generator can:
- Cross two survivors from different cells ("what if we test domain A's approach on domain B's data?")
- Vary a killed hypothesis's weakest point ("the convergence rate died at a_2/a_3 — what if we skip small primes?")
- Explore a void cell ("no hypothesis has ever survived in the (knot, information-theoretic) niche — try something")

---

## The Mathematical Genes

What the system is allowed to mutate:

### Feature genes
- Which features to extract from each domain (a_p, zeros, spacing, entropy, compression, graph topology)
- How to normalize (raw, log, rank, z-score, ST-weighted)
- Which primes to include/exclude (all, odd only, skip first k)

### Coupling genes
- How to measure dependence (MI, Spearman, Wasserstein, KS, TT-Cross bond)
- Resolution (sample size per test: 100, 500, 2000, 10000)
- Conditioning variables (conductor, rank, torsion, CM flag)

### Structural genes
- Graph construction (congruence mod ell, nearest-neighbor, threshold similarity)
- Dimensionality (1D scalar, 2D projection, full feature vector)
- Temporal structure (sequential order preserved vs shuffled)

### Meta genes
- Which F-tests to fear most (track which tests kill most hypotheses in each niche)
- Which domains are most/least explored (void detection)
- Which failure modes are most common (avoid well-known traps)

---

## The Unattended Run

### Startup:
```bash
python forge/autonomous_explorer.py \
    --n_generations 1000 \
    --hypotheses_per_gen 20 \
    --battery full \
    --log forge/results/run_001.jsonl \
    --constraint_db forge/kill_taxonomy.db
```

### What it does while we sleep:
- Generation 1: 20 hypotheses, most die at F1 (permutation null). 2-3 reach F24. 0-1 survive.
- Generation 10: Constraints tightened by 50+ kills. Generator avoids known traps. Some hypotheses reach F30+.
- Generation 100: The generator has 500+ constraints. Only highly adapted hypotheses are produced. The survivors (if any) have passed 30+ tests each.
- Generation 1000: The MAP-Elites grid shows which (domain, measurement) niches have ANY survivors. The void map is complete. The constraint set is the tightest it can be.

### What we see in the morning:
- A heat map of the (domain, measurement) grid showing survival depth per cell
- The top 5 survivors across all niches, with full kill-test profiles
- The updated kill taxonomy (which new failure modes were discovered)
- The constraint set (which negative dimensions were reinforced or refined)
- The void analysis (which niches remain unexplored despite 20,000 attempts)

---

## Tech Stack

| Component | Technology | Already exists? |
|-----------|-----------|----------------|
| Nemesis (battery) | battery_v2.py + cross_domain_protocol.py | YES |
| Kill taxonomy | SQLite (kill_taxonomy.db) | NO — build tomorrow |
| Constraint set | JSON (negative_dimensions.json) | PARTIAL — formalize |
| Generator | Claude/GPT-4 API via council_client.py | YES (needs new prompt) |
| Hypothesis → test translation | Template matching + code generation | PARTIAL |
| Ungated tensor | tntorch + raw coupling function | YES (needs separation from battery) |
| MAP-Elites | Custom Python (exists in cartography/shared/scripts/map_elites.py) | YES |
| Orchestrator | Python loop (generate → test → update → repeat) | NO — build tomorrow |
| Logging | JSONL + structured results | YES (battery_logger.py) |

**What's new to build:**
1. `forge/kill_taxonomy.db` — structured kill memory
2. `forge/autonomous_explorer.py` — the orchestration loop
3. `forge/hypothesis_templates.py` — translating LLM output to computable tests
4. `forge/map_elites_integration.py` — the quality-diversity wrapper
5. Update `council_client.py` prompt with constraint injection

**Estimated build time:** 1 day for the core loop. 1 day for MAP-Elites integration. 1 day for testing and first unattended run.

---

## What We're Really Building

Not a search engine. Not a neural net. An **adversarial evolutionary ecosystem** where:

- The environment (Nemesis) is the sharpest falsification instrument in empirical mathematics
- The organisms (hypotheses) are generated by frontier LLMs reasoning about constraints
- The selection pressure (MAP-Elites) ensures diversity across domains and measurement types
- The memory (kill taxonomy) ensures the system never repeats a mistake
- The human (us) sets the initial conditions and analyzes the survivors

The system fails millions of times. We only see the ones that survive everything. The burden of failure shifts from human to machine. The psychological cost drops to zero. The exploration continues 24/7.

And if nothing survives 1000 generations — that's itself a finding: the negative space is complete, and the remaining structure in mathematics is already captured by known theorems. Which is exactly the level of confidence we need before claiming anything.

---

## First Run Parameters

**Domains:** Start with the 20 mathematical domains (EC, MF, NF, G2, Maass, knots, lattices, etc.)
**Measurement types:** correlation, distribution, topology, spectral, information-theoretic
**Hypotheses per generation:** 20
**Generations:** 100 (first run), then 1000 (overnight)
**Constraint seed:** 21 kills + 10 negative dimensions + 7 calibration anchors
**Target:** Fill 50+ cells in the MAP-Elites grid, identify any cell with survival depth > F24

---

*Designed: 2026-04-13*
*Build: 2026-04-14*
*First unattended run: 2026-04-14 evening*
*First survivors (if any): 2026-04-15 morning*
*The machine takes the failures. We take the survivors.*
