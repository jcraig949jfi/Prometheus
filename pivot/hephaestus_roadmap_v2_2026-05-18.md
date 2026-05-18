# Hephaestus Forge — v2 Roadmap

**Filed:** 2026-05-18
**Author:** M3 Agent + James Craig
**Status:** Active roadmap
**Predecessor:** `roles/PipelineOrchestrator/DESIGN_tiered_forge.md` (2026-04-02)

---

## 0. What We Learned (the v1 ledger)

Three months of forge operation (March-May 2026) produced:

**Assets:**
- ~20 genuinely distinct reasoning mechanisms (from ~1,960 generated files)
- 5 named specialists with real algorithms (causal BFS, SAT solver, day arithmetic, register tracker, compass state machine)
- 15 category-specific parsers that solve known trap types
- A meta-confidence detector that recognizes cognitive bias traps
- 5,449 ledger entries mapping which concept combinations work and which don't
- 186-probe tier-stratified battery (R1-R6) with behavioral profiling infrastructure
- Mechanism-knockout protocol that catches decorative mechanisms before false attribution
- A white paper documenting the decorative mechanism problem (no one else has published this with worked examples)

**Findings:**
- qwen-397B has a limited mechanistic vocabulary (~5 patterns regardless of concept prompt)
- Concept-combination prompting produces volume, not diversity — names are labels, not implementations
- 92% of generated tools perform worse than NCD compression baseline on the expanded battery
- The novelty gate works: it catches the rare genuine outliers (~2-3% of output)
- Near-miss scraps contain no hidden novel mechanisms (confirmed via LLM deep inspection)
- The R6 "theory of mind" finding was a decorative mechanism: regex did the work, BFS was cosmetic for that tier
- BUT the same tool's BFS genuinely contributed +28pp to R3 abstraction — mechanisms can be real on one tier and decorative on another
- Failure data (kill patterns, scrap reasons) is structured, not random — 0.725 bits MI with operator class in the broader kill ledger

**The map this draws:**
- Concept-combination + single model = exhausted after ~5,000 attempts
- Genuine mechanistic diversity requires different models, different prompt strategies, or different generation paradigms entirely
- The measurement infrastructure (tier battery, phenotype vectors, mechanism knockout) is more valuable than the tools themselves — it's reusable across any generation approach
- Apollo composition of the ~20 real tools is the next decisive test

---

## 1. Library Consolidation (Week 1)

### 1.1 Collapse to canonical set

Reduce ~1,960 files to the genuine distinct mechanisms:

```
canonical/
  parsers/
    numeric_comparison.py      — float parsing, magnitude comparison
    quantifier_logic.py        — "all A are B" ≠ "all B are A"
    conditional_logic.py       — modus tollens, modus ponens, contrapositive
    negation_scope.py          — double negation, scope tracking
    subject_verb_object.py     — syntactic role extraction
    temporal_ordering.py       — before/after, causal sequence
    arithmetic_traps.py        — bat-and-ball, all-but-N, fencepost
    probability_independence.py — gambler's fallacy, fair coin
    parity_rules.py            — odd+odd=even, pigeonhole
    equality_edge_cases.py     — 0.999...=1, pound-of-gold
  specialists/
    causal_specialist.py       — DAG construction + BFS reachability + intervention
    computation_specialist.py  — register tracking, arithmetic chains
    temporal_specialist.py     — day-of-week algebra, age reasoning
    tom_liar_specialist.py     — brute-force SAT over truth assignments
    compass_direction.py       — state machine for N/E/S/W composition
  meta/
    meta_confidence.py         — presupposition/bias trap detector
    ncd_baseline.py            — compression distance (the floor)
  novel/
    epmc_hebbian_bfs.py        — Hebbian plasticity + BFS (genuine R3/R5 contribution)
    spas_evolutionary.py       — evolutionary architecture search per query
    [any future genuine novelties]
```

Each canonical tool gets a **mechanism attribution card** (from the white paper schema):
- Allowed claims (which tiers, with ablation evidence)
- Forbidden claims (which tiers are decorative)
- Routing constraints (which compositions to avoid)

### 1.2 Archive the versions

Move forge_v2 through forge_v9 to `archive/`. They're historical data, not active substrate. The ledger and phenotype analysis preserve their information.

---

## 2. Round 2 Generation (Weeks 2-4)

### 2.1 What to change

The v1 approach (concept-combination prompting with a single model) exhausted its mechanistic vocabulary. Round 2 changes three things:

**Different models.** Run the same prompt strategy through 3-4 different code-gen models. Each model has different training data and different biases — different mechanistic vocabularies.

Candidates:
- Claude (via Augment API) — strongest at structured code, may produce cleaner mechanisms
- DeepSeek-Coder — strong at algorithmic code, different training mix
- Gemini — different architecture, different generation patterns
- Continue qwen-397B as control (we understand its patterns now)

**Different prompt strategies.** Instead of only "generate a ReasoningTool inspired by these concepts," add:

- **Algorithm-first prompts:** "Implement a reasoning tool using [specific algorithm: minimax, A* search, belief propagation, constraint propagation, Bayesian network inference]. Apply it to score candidate answers."
- **Mechanism-targeted prompts:** "The current library is missing tools that do [backtracking search / probabilistic inference / analogical transfer / semantic entailment]. Generate a tool that implements this specific capability."
- **Gap-filling prompts:** Use the coverage map to identify underrepresented R-tiers and morpheme types, then prompt specifically for those gaps.
- **Repair-and-extend prompts:** Take an existing specialist tool and prompt "extend this tool's approach to handle [new problem type]."

**Different evaluation.** Every generated tool gets:
- Tier profile (per-tier accuracy on 186 probes)
- Mechanism knockout (strip novel component, measure delta)
- Rarity score (does it solve problems others don't?)
- Model attribution (which model generated it)

### 2.2 Target: mechanism families we don't have

From the survey of what's missing:

| Missing Capability | Target Tier | Prompt Strategy |
|---|---|---|
| Probabilistic inference (actual Bayes, not keyword) | R3 | Algorithm-first: belief propagation |
| Multi-step state tracking (5+ steps) | R2 | Algorithm-first: register machine |
| Constraint satisfaction with backtracking | R4 | Algorithm-first: arc consistency + backjumping |
| Semantic similarity (beyond token overlap) | R3 | Mechanism-targeted: embedding-free semantic features |
| Analogical transfer (structural mapping) | R3-R7 | Algorithm-first: structure mapping engine |
| Formal verification / proof checking | R6 | Algorithm-first: simple proof validator |
| Spatial reasoning | R4 | Gap-filling: grid/position puzzles |
| Natural language inference | R3 | Mechanism-targeted: entailment via structural decomposition |

### 2.3 Success metric

Round 2 succeeds if it produces **10+ new mechanism families** that pass mechanism knockout (>15pp delta on at least one tier). Volume is irrelevant. We want distinct algorithms, not more regex+NCD variants.

---

## 3. Apollo Integration (Weeks 3-6)

### 3.1 Feed canonical tools as genes

Apollo's gene library expands from the fixed 25 Frame H primitives to:
- 25 existing Frame H primitives
- ~20 canonical forge tools (each with mechanism attribution card)
- Any Round 2 tools that pass mechanism knockout

### 3.2 The decisive experiment

Per `apollo_value_proposition_2026-05-17.md`:

Run Apollo for 5,000 generations with two conditions:
- **Condition A (diverse):** Gene library includes failure-orthogonal tools from the forge
- **Condition B (homogeneous):** Gene library uses only the top-10-accuracy tools

Measure:
- Coalition value: do evolved organisms beat the best individual tools by >10%?
- Failure orthogonality: do organisms fail on different problems than any single tool?
- Routing diversity: do multiple distinct topologies survive in the elite?

### 3.3 Falsification conditions

Apollo's compositional premise is **falsified** if after 10,000 generations:
- No coalition value (organisms ≤5% better than "N best tools")
- No failure orthogonality (organisms fail same problems as dominant tool)
- Routing collapse (>80% converge to single topology)

This is a real test with a real null hypothesis. The result, positive or negative, is valuable.

---

## 4. Measurement and Publication (Ongoing)

### 4.1 Extend the tier battery

Current: 186 probes across 89 categories mapped to R1-R6.
Target: 300+ probes with:
- Generated probes (anti-contamination)
- External benchmark anchors (ARC-AGI, BIG-Bench Hard)
- R3 probes for genuine rule discovery (not just pattern recognition)
- R4 probes requiring actual backtracking
- R5 probes with explicit interventional vs observational distinction

### 4.2 Mechanism knockout as standard infrastructure

Automate the knockout protocol:
- For every tool with a claimed novel mechanism, auto-generate a stripped control
- Run both through the tier battery
- Store mechanism deltas in the sidecar
- Flag decorative mechanisms automatically

### 4.3 Frontier scanning

The reasoning-evaluation space is active. Stay current with:
- ARC-AGI Prize progress (abstraction/rule discovery)
- FunSearch / AlphaEvolve (program synthesis + evaluation)
- Process Reward Models (step-level verification)
- DreamCoder (library learning / emergent taxonomy)
- Lexicase selection (specialist preservation in evolutionary systems)
- Any new "faithful CoT" or "mechanism verification" work on arXiv

### 4.4 The decorative mechanism paper

The white paper (`whitepaper_decorative_mechanisms_2026-05-17.md`) is publication-ready. Consider:
- Posting to arXiv as a short paper / technical report
- Sharing with the AI safety community (the decorative mechanism pattern has direct safety implications)
- Using it as a reference for the Prometheus methodology

---

## 5. Long-Term: The Closed Loop

The end state is a self-improving search ecology:

```
Nous (concept generation)
  → biased by forge coverage gaps and Apollo gene usage
Hephaestus (mechanism generation)
  → multiple models, algorithm-first prompts, mechanism knockout
  → produces mechanism-attributed, tier-profiled canonical tools
Apollo (evolutionary composition)
  → composes tools into organisms
  → ablation-gated gene promotion
  → failure-orthogonal diversity pressure
Kill Ledger (structured failure data)
  → 314K entries, 0.725 bits MI with operator class
  → training signal for Ergon
Ergon (navigation learner)
  → predicts which tools/organisms solve which problems
  → biases future Nous concept selection
  → the loop closes
```

The loop doesn't need to close all at once. Each segment that produces measurable downstream value justifies the next segment.

---

## 6. Timeline

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | Library consolidation | Canonical ~20 tools with attribution cards |
| 2-3 | Round 2 generation (multi-model, algorithm-first) | 10+ new mechanism families |
| 3-4 | Apollo gene library expansion | Canonical tools ingested as genes |
| 4-6 | Apollo decisive experiment | Coalition value measured |
| Ongoing | Tier battery expansion + frontier scanning | 300+ probes, arXiv current |
| 6-8 | Results analysis + publication | What worked, what didn't, what's next |

---

## 7. The Stance

Three months ago: zero primitive reasoning components, no measurement infrastructure, no understanding of what models produce when asked to generate reasoning code.

Now: a characterized library, a diagnostic toolkit that catches false capability attribution, tier-stratified evaluation, a map of what current code-gen models can and cannot produce mechanistically, and a clear-eyed assessment of where the genuine assets are.

The 5 genuine mechanism families are the first data points on a map nobody had drawn before. The finding that 92% of tools are the same pattern in different costumes is itself a contribution — it tells the field what to expect from concept-combination prompting and what to do differently.

Every failed forge, every decorative mechanism caught, every near-miss rejected by the deep inspector is a data point that makes the map more accurate. The only guaranteed failure is doing nothing. The forge's job is to explore the space of computable reasoning strategies. Some of that space is empty. Knowing that it's empty is the finding.

The next round uses what we learned to explore differently: different models, different prompts, algorithm-first instead of concept-first, targeted gap-filling instead of combinatorial spray. The measurement infrastructure is ready. The decisive test (Apollo composition) is specified with falsification conditions.

The forge continues.
