# The Hephaestus Forge: History and Architectural Pivot Memo

**Filed:** 2026-05-30 (revised per frontier review)
**Authors:** James Craig, M3 Agent (Hephaestus operator)
**Status:** Pivot memo — justifies transition from automated tool generation to failure-mined mechanism engineering

---

## 1. Project Prometheus — Context

Project Prometheus is a multi-agent system for automated mathematical discovery built on a falsification-first methodology. Its central thesis is deliberately contrarian:

> LLM "hallucinations" — generative variance — are not a defect to suppress. They are the mutation engine of an evolutionary search. With ruthless mechanistic selection, useful structure can be extracted from the noise.

The system treats every generated artifact as a hypothesis under selection pressure. A 4-fold falsification battery, synthetic-null gate, KillVector geometry, and anti-anchor sentinels form a selection regime that lets useful mutations through and kills deleterious ones with high specificity. The interesting output is not what survives — it is *what gets killed and how*, because the kill geometry carries structured information that downstream training and discovery can navigate.

Empirical evidence supports this: gradient archaeology on ~314K logged kills shows `kill_pattern` carries **0.725 bits of mutual information** with operator class. The kill geometry is structured — not random noise but a navigable landscape.

Prometheus operates across four machines (M1-M4) with ~45 agents organized into specialized roles: Aporia (research coordination), Charon (falsification), Techne (substrate toolsmith), Ergon (the Learner), Harmonia (substrate architecture), and the forges — Hephaestus and Apollo — which are the subject of this document.

---

## 2. What Hephaestus Was Built To Do

Hephaestus is the automated forge for reasoning primitives. Named for the Greek god of the forge, fire, and craftsmanship, its original mandate was:

> Take theoretical concept combinations from Nous (e.g., "Quantum Mechanics × Neural Plasticity × Model Checking"), enrich them with causal intelligence from Coeus, and use a frontier LLM to hammer them into testable Python `ReasoningTool` classes — deterministic algorithms that can score and rank candidate answers to reasoning questions without any neural model at inference time.

Each generated tool passes through five validation gates: syntax (valid Python), imports (numpy + stdlib only, ensuring determinism and portability), interface (must define `evaluate()` and `confidence()`), runtime (instantiate and run without crashing), and a trap battery (must beat an NCD compression baseline on 15-186 reasoning probes).

The downstream consumer was always intended to be Apollo — the evolutionary computation engine that maintains a population of "organisms," each a routing graph over a library of reasoning primitives. Hephaestus produces the morphemes (atomic reasoning strategies). Apollo composes them into organisms (complex reasoning procedures). The falsification battery applies selection pressure at both levels.

---

## 3. The Forge's Journey: A Chronological History

### Phase 1: First Generation (March 2026)

Hephaestus activated on March 24, 2026 with a pool of 95 concepts spanning physics, biology, formal methods, neuroscience, and information theory. Every combination of three concepts was a candidate for forging. The model (qwen-397B via NVIDIA API) received a multi-section prompt including the Nous theoretical analysis, Coeus prescriptive directives, an NCD quality floor, and one of eight "frames" (Structural, Constructive, Dynamics, Judgment, Computational, Adversarial, Metacognitive, Primordial) selected by weighted rotation.

Over nine days (March 24 to April 2), Hephaestus produced **~1,960 tools across 9 forge versions**, with a ~40% forge rate against a 15-trap battery with NCD baseline at ~20% accuracy. Five named specialists emerged in forge_v8: causal, computation, temporal, theory-of-mind/liar, and generalist engines. Active model-quality work was underway (a MODEL_COMPARISON_REPORT testing 5 alternative models, a REPAIR_SCORECARD analyzing 630 scrap candidates).

On April 2, the forge stopped mid-API-call. The log ends at "Calling Augment API (auggie-sdk)..." with no error message. The cause was never definitively identified — likely API quota exhaustion or the attention pivot that followed.

### Phase 2: Dormancy and Autopsy (April-May 2026)

Hephaestus sat idle for 40 days. During this period, James pivoted to substrate-vocabulary and Learner work. On May 12, Aporia filed a chip-1 RESUME document identifying three revival paths and the key strategic question: *who is Hephaestus's current consumer?*

On May 13, Aletheia authored a consolidated autopsy of both forges (Hephaestus and Apollo). The autopsy's Reviewer Preamble articulated the Prometheus thesis with unusual clarity:

> Prometheus is not building a single AI. It is building the substrate from which intelligences emerge. The working hypothesis: provide an advanced symbolic language and a library of cognitive training seeds, apply selection pressure, and intelligences emerge from the primordial soup.

The autopsy's convergent finding: both forges were blocked on the same structural problem — **consumer drift**. Hephaestus kept producing the thing it was designed to produce; the downstream that wanted that output had moved on; the agent looked like it had "diminishing returns" but was actually producing into a vacuum.

### Phase 3: Revival and Instrumentation (May 15-17, 2026)

Hephaestus was revived on M3 (GANDALF) on May 15-16 as part of a multi-machine architecture: Apollo on M2, Nous + intelligence pipeline on M4, Hephaestus + Nemesis on M3, Redis on M1.

The revival added:
- **Agora telemetry** (Redis heartbeat + Postgres dual-write fallback)
- **Novelty gate** (source-code NCD > 0.85 admits tools that are structurally unique even if accuracy is below baseline)
- **Expanded import injection** (re, math, json, itertools, etc.)
- **Confidence wrapper** (auto-fixes None returns)
- **Scrap repair modes** (`--repair-scraps` for mechanical fixes, `--repair-with-llm` for API-based syntax repair)
- **Model field in ledger** (for A/B comparison across providers)

The first scrap repair pass recovered 10 high-novelty tools from the scrap pile. The first LLM repair pass recovered 7 more (5.5% repair rate).

### Phase 4: The Decorative Mechanism Discovery (May 17, 2026)

While evaluating a tool generated from "Quantum Mechanics × Neural Plasticity × Model Checking" (the EPMC tool), we discovered it appeared to demonstrate R6-level theory-of-mind reasoning — 50% accuracy on belief attribution, presupposition detection, and knowledge asymmetry probes.

Mechanism-knockout ablation — building a stripped control with only the regex/keyword components and comparing per-tier — revealed a richer and more instructive picture:

- **R6 (theory of mind): +2pp** — decorative. 96% of R6 performance came from regex keyword matching on known cognitive-bias patterns, not from the Hebbian/BFS mechanism.
- **R3 (abstraction): +28pp** — genuine. The Hebbian weight-updating during evaluation genuinely improved pattern recognition.
- **R5 (causal reasoning): +31pp** — genuine. State-space exploration aided counterfactual reasoning.
- **R2 (multi-step deduction): -22pp** — harmful. The BFS exploration actively interfered with chain tracking.

This finding was published as a white paper ("Correct for the Wrong Reason: Mechanism Knockout for LLM-Generated Reasoning Code") and established mechanism knockout as a standard validation step. The broader literature survey confirmed that no frontier model solves this problem: RLHF makes it worse (U-SOPHISTRY), chain-of-thought is demonstrably unfaithful, and scale plateaus for code generation.

### Phase 5: The Model and Prompt Sweeps (May 18-21, 2026)

To test whether different models or prompts would produce different reasoning mechanisms, we ran systematic sweeps:

**Model sweep (12 models × 100 candidates):** Five models produced usable output. The finding was definitive: **the prompt template dominates model identity**. All models converge on identical regex + NCD + meta-confidence architecture because the prompt specifies it. The one exception was Llama-4-Maverick, which partially escaped the template due to its 128-expert MoE architecture, producing Hamming error-correcting codes, reservoir networks, and Kalman filters.

**Prompt sweep (5 strategies × 20 candidates):** Algorithm-first, gap-fill, adversarial, exemplar, and concept-first (control). Modest tier-profile shifts but no accuracy breakthrough. The exemplar strategy ("here is a bad NCD tool, build something different") and gap-fill ("the library lacks R4 search tools") marginally outperformed concept-first.

The sweeps eliminated model choice as the primary lever and identified the prompt as the real constraint. Under Hephaestus's concept-combination prompt regime, LLMs overwhelmingly collapsed into pattern-matching code. The failure may belong to the artifact specification — "write a reasoning tool inspired by these concepts" — not necessarily to the models themselves. The falsified primitive is not "LLMs cannot generate algorithms." It is: free-form concept-combination prompting is a poor primitive for generating reliable reasoning mechanisms.

### Phase 6: The Diversity Forge and Composition Breakthrough (May 22-26, 2026)

Recognizing that the main forge's mechanism vocabulary was exhausted (~5 genuine patterns in ~1,960 costumes), we built a parallel **Diversity Forge** with:

- **Island prompts** (solver, searcher, reasoner, calculator, planner) — each targeting a different computational strategy
- **Mixed-format puzzle battery** (constraint satisfaction, state machines, graph traversal, sequences, planning) — problems that regex structurally cannot solve
- **MAP-Elites archive** (pyribs) tracking behavioral coverage
- **gpt-4o-mini via GitHub Models** as primary (separate endpoint, no NVIDIA contention)

The diversity forge's first 7 tools included a **genuine forward-chaining inference engine** (builds rule graphs, propagates beliefs via BFS) and a **backtracking searcher** with cycle detection — mechanisms the main forge never produced across 1,960 tools.

This led to the **composition result** (Day 1 of the 5-day sprint): wiring a text parser from the main forge to the diversity forge's inference engine produced a composed tool that solved problems neither component could solve alone. Modus tollens: 100% vs 0%. Transitivity: 100% vs 0%. The composition thesis received its first nontrivial positive evidence on a small class of structured puzzles — not yet validation, but a genuine signal.

### Phase 7: The v3 Sprint — Hand-Crafted Engines Climb the Ladder (May 26-30, 2026)

The 5-day sprint produced five deliverables, three of which reshaped the forge's direction:

**Day 1: Composition works.** Parser + engine composed = new capabilities. 48% on puzzles (vs 25% NCD baseline).

**Day 2: Refinement doesn't help.** Multi-turn LLM repair (send errors back for fixing) produced 0/10 improvements. The accuracy gap is mechanism limitation, not bug.

**Day 3: Puzzle generator.** 8 parameterized generators producing unlimited verified problems. The composed tool scored 45% on fresh never-seen puzzles — genuine generalization, not memorization.

**Day 4: Seed from winners.** Showing working code as exemplar + targeting specific weaknesses → children inherit parent capabilities AND add new ones. The DreamCoder pattern works for reasoning tool generation.

**Day 5: Behavioral NCD.** Source-code NCD inflates diversity claims. Behavioral NCD (output vectors, not code) catches tools that look different but behave identically.

The sprint's biggest insight: **LLM-generated tier specialists don't beat hand-crafted engines.** Every specialist scored at the auto-fix wrapper baseline. The composed tool's hand-crafted engines (OrderingEngine, ComputationEngine, StateEngine) outperformed because they implement real algorithms, not regex patterns.

### Phase 8: Mining Failures for Direction (May 30, 2026)

With 6,657 ledger entries, we mined the failure landscape for directional signals. Six signals emerged:

1. **Frame system kills the forge.** Frameless generation (18% rate) outperforms framed (0.3-1.5%) by 12-36×.
2. **860 near-misses are the gold mine.** Tools scoring 35-42% solve different problem subsets — composing the right ones compensates for individual miscalibration.
3. **Computational concepts forge; meta-concepts don't.** Chaos Theory (16%) vs Metamorphic Testing (1%). Concepts with obvious algorithms win.
4. **Best pairs suggest evaluation strategies.** Falsificationism + Predictive Coding (75%) outperforms all algorithm-suggesting pairs.
5. **NCD near-misses cluster at a Goodhart ceiling.** Tools implementing NCD can approach the NCD baseline from below but can't surpass it.
6. **The forge rate drop is the battery, not the forge.** March 8% (15 traps, NCD=20%) vs May 1.5% (186 traps, NCD=42%). Quality went up; pass rate went down because the bar got harder.

Mining the 860 near-misses for failure orthogonality — tools that solve problems the composed tool gets wrong — pointed directly to two missing computation families: **probabilistic fallacy detection** (R3) and **temporal computation** (R4).

Hand-crafting these engines produced the biggest ladder climb: R3 from 28% to 39% (+11pp), R4 from 29% to 61% (+32pp). The 9-engine composed tool now stands at 40% overall on the 186-probe battery.

---

## 4. The Reasoning Ladder: Not a Ladder but a Basis

The reasoning ladder (R0-R9), designed by Charon and operationalized by Harmonia B, provides the vocabulary for measuring what the forge produces. But the word "ladder" is misleading — the tiers behave as **orthogonal capability axes**, not ordered steps.

A tool can be R4-strong (solves constraint satisfaction via backtracking) and R2-weak (loses state in multi-step deductions). Climbing from R1 to R2 (adding rule propagation) is qualitatively different from climbing from R3 to R4 (adding search with backtracking). Each tier requires a different computational paradigm, not just more of the same.

Harmonia B operationalized this as a testable framework with procedurally generated probes (can't be memorized), four versions per tier (clean, isomorphic, adversarial, transfer), and a deterministic non-LLM verifier (z3+sympy, fails-closed). The 3-model comparison showed R2 constraint-tracking as the sharpest discriminator: Haiku 0% → Opus 75% → Sonnet 100%.

For the forge, the implication is prescriptive: **one engine family per tier-operation gives functionally-orthogonal novelty by construction.** This is not arbitrary variety — it is the minimum set of computationally distinct primitives needed to cover the reasoning space.

---

## 5. What the Forge Has Surfaced: The Honest Inventory

### The 9-Engine Composed Tool

Evidence status split into four levels:
- **Mechanism-present:** Code actually implements the claimed algorithm
- **Probe-effective:** Improves score on current probes
- **Generalizes:** Works on procedurally generated held-out variants
- **Composition-safe:** Improves composed organisms without damaging other tiers

| Engine | Tier | Mechanism | Mech | Probe | General | Comp-safe |
|--------|------|-----------|------|-------|---------|-----------|
| ForwardChainEngine | R2 | Fixpoint inference closure | Yes | +R2 | Untested | Yes |
| OrderingEngine | R2 | Transitive closure via BFS | Yes | 100% transitivity | Yes (generated) | Yes |
| ComputationEngine | R2 | Arithmetic, modular math | Yes | Solves bat-and-ball | Partial | Yes |
| NegationEngine | R2 | Modus tollens detection | Yes | Distinguishes valid/invalid | Untested | Partial (R5 harm) |
| ProbabilisticFallacyEngine | R3 | Quantifier/conjunction/base rate | Yes | +11pp R3 | Untested | Untested |
| SequenceEngine | R3 | Pattern detection (5 types) | Yes | 100% sequences | Yes (generated) | Yes |
| TemporalComputationEngine | R4 | Time math, LCM, scheduling | Yes | +32pp R4 | Untested | Untested |
| StateEngine | R3-R4 | State machine simulation | Yes | 100% state machines | Yes (generated) | Yes |
| CausalEngine | R1 | Keyword-matches "correlate" | **No** | **Harmful** (-6pp R5) | N/A | **Harmful** |

### The Honest Ladder Position

```
R1 (rule execution):       50%  ████████████████████  GENUINE
R2 (multi-step deduction):  33%  █████████████         GENUINE
R3 (abstraction/fallacy):   39%  ███████████████       GENUINE
R4 (temporal/search):       61%  ████████████████████████  GENUINE
R5 (causal reasoning):       0%  .                     ABSENT — no real causal engine
R6 (self-monitoring/ToM):   ~7%  ██                    MOSTLY ACCIDENTAL
```

---

## 6. The R5 and R6 Challenge: What the Failures Reveal

### R5: Mostly R1-R3 in Causal Clothing

Detailed examination of every R5 probe (16 problems across 8 categories) revealed that most "R5" problems are solvable with lower-tier techniques:

| Category | What it actually needs | Tier |
|----------|----------------------|------|
| correlation_not_causation | Keyword: "correlat" + causal question = No | R1 |
| post_hoc | Keyword: "and then" + "can we conclude cause" = No | R1 |
| causal_confounding | Pick candidate mentioning "confounding" / "common cause" | R1-R2 |
| causal_common_cause | Same as confounding | R1-R2 |
| necessary_vs_sufficient | Keyword: "necessary" + "guaranteed" = No | R1 |
| causal_counterfactual | Parse universal rule, apply hypothetically | R2 |
| causal_simpson_paradox | Extract fractions, compute weighted averages | R3-R4 |
| **causal_intervention** | **Build chain A→B→C, cut at intervention, check reachability** | **R5 genuine** |

Only 2 of 16 probes genuinely require R5 reasoning (causal intervention — building a DAG, cutting edges, checking downstream reachability). The other 14 are solvable with keywords, rule application, or arithmetic. This is important because it means a well-crafted engine hitting the specific patterns should score 75-87% on the R5 battery without implementing real do-calculus.

### R6: Two Completely Different Problems Conflated

R6 splits cleanly into an easy half and a hard half:

**Easy half (7 categories, ~14 probes):** Presupposition detection, sunk cost fallacy, survivorship bias, intention vs outcome, irrelevant premise, premise contradiction, argument strength. All solvable at R1-R2 with keyword patterns and syllogism logic. Our existing engines already partially handle these — they just aren't routed correctly.

**Hard half (14 categories, ~28 probes):** False belief tasks, knowledge attribution, second-order belief, theory of mind (perspective shift, strategic deception, intention reading, mistaken belief chains, information asymmetry, group knowledge), liar detection, self-referential consistency, confidence calibration, compositional logic within someone's worldview.

The hard half requires **state simulation of other agents' belief states** — a fundamentally different computational paradigm. A few subcategories are tractable (liar detection = constraint SAT, confidence calibration = verbal-to-numeric mapping), but genuine theory-of-mind problems need:

```python
class BeliefState:
    who_knows_what: dict[str, set[str]]   # agent → known facts
    who_believes_what: dict[str, set[str]] # agent → believed facts (may differ from reality)
    
    def update(self, event):
        # "A leaves room, B moves object"
        # → A still believes object in old location
        # → B knows object in new location
```

This is the genuine R6 frontier. No forge tool has ever produced anything like it, and LLMs don't generate it from concept-combination prompts. It requires hand-crafting with careful attention to the semantics of belief, knowledge, and perspective.

### The Path Forward: What to Hand-Craft

**For R5 — two separate artifacts, not one:**

**(a) CausalFallacyDetector (battery diagnostic, NOT R5 progress):**
Detects and subtracts lower-tier solvability from the R5 score. Handles correlation keywords (R1), counterfactual rule application (R2), Simpson's arithmetic (R3-R4). Its purpose is to expose how much of the "R5 battery" is really R1-R3 in causal clothing. Expected: 12-14/16 probes — but this measures battery quality, not R5 capability.

**(b) CausalInterventionEngine (genuine R5 candidate):**
Builds a directed causal graph from text. Implements do-operator semantics (cut incoming edges to intervened variable). Detects confounders (common cause of X and Y). Handles collider structure. Answers counterfactual queries by comparing baseline vs modified graph. This is the real R5 artifact — it should be evaluated only on the 2 genuine intervention probes (and on a separate procedurally generated causal battery).

**For R6 easy half (estimated result: 14/42 = 33%):**
Route existing engines (presupposition detection, syllogism logic) to the right R6 categories. Most of this capability already exists in the NegationEngine and ForwardChainEngine — it just fires on the wrong problems or doesn't fire at all.

**For R6 hard half (genuine ToM — uncertain timeline):**
Design a BeliefStateEngine that:
1. Tracks who is present/absent during events
2. Maintains per-agent belief sets that diverge from reality
3. Handles second-order beliefs ("A thinks B believes X")
4. Handles strategic reasoning ("A knows B always does the opposite")

This is the most architecturally challenging engine and should be designed carefully rather than rushed. The failures point to it but don't provide a simple code path — it requires a new representational framework.

---

## 7. The Thesis, Refined

The forge's journey from March to May 2026 traced an arc from ambitious automation to grounded mechanism engineering. The frontier review's verdict captures it precisely:

> Hephaestus has falsified "LLM-generated reasoning tools" as the primitive and validated "verified typed mechanisms" as the primitive. That is not a setback. That is the substrate becoming legible.

The refined architecture:

- **LLMs propose transductions** — NL-to-IR parsers, candidate schemas, edge-case generators, adapter code, mutation variants of specified algorithms
- **Verified kernels do reasoning** — hand-crafted algorithms (forward chaining, constraint propagation, state simulation, Dijkstra, Bayesian update) with mechanism-knockout validation
- **Composition climbs the ladder** — typed state→state transformers (blackboard ops) composed by Apollo into organisms that achieve higher-tier capabilities than any individual primitive

The forge's role going forward is not to maximize tool count. It is to **surface, verify, and adapt the minimum set of mechanistically distinct primitives** that unlock structured reasoning tier by tier. Each engine is a specific, testable claim: "this computation solves this class of problems." Mechanism knockout verifies the claim. The battery measures the coverage. Apollo composes the verified primitives into organisms. The kill ledger records what fails and why.

The 6,657 failures are not waste. They are the map that told us exactly where to look.

---

## 8. What Would Falsify the New Thesis?

The document falsifies the old primitive (LLM-generated reasoning tools at scale) but must pre-register falsifiers for the new one (verified typed mechanisms, failure-mined, composed). If these fire, the pivot is wrong:

**F1. Typed kernels do not compose.** Individual engines score well on their tier, but Apollo compositions fail to exceed the best single engine on held-out procedural probes. If composition adds no value over selection, the typed-transformer architecture is overhead.

**F2. Composition creates cross-tier harm.** Adding engines improves target tiers but damages other tiers enough that net capability does not improve. The TemporalComputationEngine's R4 gain (+32pp) was accompanied by an R5 regression (-6pp via CausalEngine interference). If this pattern persists — every new engine cannibalizes another tier — the ensemble architecture is wrong.

**F3. Behavioral NCD fails to predict complementarity.** Tools with high behavioral distance (different answer patterns) do not solve different held-out failures. If behavioral novelty does not predict compositional value, the diversity metric is decoration.

**F4. Hand-crafted kernels saturate quickly.** After R1-R4, every higher-tier engine becomes an expanding pile of special cases with diminishing returns per pattern. If R5 requires 50 special cases and R6 requires 200, the architecture doesn't scale — a different approach (learned representations, end-to-end training) is needed.

**F5. Failure mining is retrospective storytelling.** Mined near-miss clusters do not predict which next engine will improve held-out performance. This is the most important falsifier: if the "map" only works in hindsight, it is narrative, not navigation.

### The Pre-Registered Experiment

Freeze the current 6,657-entry ledger. Mine it to nominate three next engines (the CausalFallacyDetector, the CausalInterventionEngine, and one R6 candidate). Pre-register expected tier deltas for each. Build the engines. Evaluate on fresh procedurally generated probes (new seed, never used in the mining loop).

If the predicted deltas land within ±10pp: the failure geometry thesis strengthens.
If the predicted deltas miss by >20pp or the engines harm other tiers: the thesis weakens.
If a mined engine helps on training probes but not on held-out probes: it is overfitting the battery, not learning the capability.

---

## 9. Operational Doctrine (from Frontier Review)

The forge's new contract, per frontier review consensus:

> A Hephaestus artifact is no longer a ReasoningTool. It is a typed mechanism package.

Each artifact includes:
1. Input schema and output schema
2. Claimed operation family (not "tier" — one kernel per irreducible operation)
3. Minimal deterministic kernel
4. Mechanism knockout control (stripped version that removes the claimed mechanism)
5. Behavioral fingerprint vector (output pattern on standard battery)
6. Tier-local probe score
7. Cross-tier harm score (does it damage other tiers?)
8. Composition compatibility metadata (declared reads/writes for Apollo)
9. Failure signature (what it gets wrong and why)

The unit is not "one engine per tier." It is **one verified kernel per irreducible operation family:**

| Operation Family | Examples |
|-----------------|----------|
| Rule closure | Forward chaining, contradiction detection, transitive closure |
| Arithmetic binding | Bat-and-ball, modular math, rate computation |
| Sequence induction | Arithmetic/geometric/fibonacci/power detection |
| State simulation | State machines, register operations, stack tracking |
| Temporal algebra | Duration, scheduling, relative day, LCM |
| Probabilistic fallacy detection | Base rate, conjunction, quantifier inversion |
| Confounder detection | Common cause, correlation-not-causation |
| Intervention DAG | do-operator, edge cutting, path persistence |
| Counterfactual propagation | Modified-graph comparison |
| Belief-state tracking | Who knows what, after what events |
| Second-order belief | "A thinks B believes X" |
| Self-reference | Word counting, consistency checking |
| Calibration | Verbal probability → numeric mapping |

Each family is a separate engineering problem. Each requires its own verification, knockout control, and composition test. The forge produces them one at a time, verified before the next.

---

## 10. The Core Thesis, Tightened

> Reasoning primitives must be verified typed mechanisms, not generated tool-shaped code. LLMs are useful upstream of the mechanism boundary — as transduction proposers, parser generators, adapter scaffolds, and mutation operators — but not inside the selector and not trusted as the mechanism itself.

The 6,657 failures told us exactly which mechanisms are missing. The composition result showed that verified mechanisms, properly typed, produce capabilities that no individual tool achieves. The path forward is not more generation — it is the patient, failure-guided engineering of the irreducible operation families that cover the reasoning space.

That is the substrate becoming legible.
