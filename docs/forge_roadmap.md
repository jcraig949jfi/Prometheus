# Forge Pipeline Roadmap

*From static structural checks to dynamic adversarial evolutionary evaluation*

---

## Current State (v1 — operational)

```
Nous (concept mining) → Coeus (causal intelligence) → Hephaestus (forge + validate)
```

- 89 concepts, 1561+ combinations evaluated
- 15-trap static battery, NCD baseline
- Structural parsing + NCD + constraint propagation
- Best tool: IBAI v2 at 67% accuracy, 53% calibration
- Coeus: L1 regression + NOTEARS + LiNGAM + FCI + interventional estimates
- Continuous operation, auto-rebuild every 50 forges

**What works:** computable invariants, automated epistemology search, causal feedback into evaluator generation, continuous fitness landscape (NCD + cliffs).

**What breaks:** surface structure only, static traps (overfitting risk), no adversarial pressure, no execution grounding, no reasoning trace evaluation, implementability bias shaping epistemology.

---

## Phase 1 — Immediate (COMPLETE)

### 1A. Dynamic Trap Generation (replace static battery) -- DONE
**Priority: CRITICAL — prevents evaluator overfitting**

Turn the 15 static traps into parametric generators that produce infinite variants:

```python
def generate_numeric_comparison():
    a = round(random.uniform(1, 100), random.randint(1, 3))
    b = round(random.uniform(1, 100), random.randint(1, 3))
    correct = "Yes" if a > b else "No"
    return {"prompt": f"Is {a} larger than {b}?", "candidates": ["Yes", "No"], "correct": correct}
```

Categories:
- Numeric comparison (infinite variants of 9.11 vs 9.9)
- Logical inversion (parameterized quantifier/negation puzzles)
- Transitivity chains (variable length: A > B > C > ... > N)
- Compositional word order (agent/patient/verb permutations)
- Arithmetic word problems (parameterized bat-and-ball)

Keep the original 15 as a **held-out validation set**. Forge-time evaluation uses generated variants. This breaks overfitting immediately.

**Where:** `hephaestus/src/trap_generator.py`, called by `test_harness.py`

### 1B. Reasoning Trace Evaluation (not just answers) -- DESIGNED, NOT YET WIRED
**Priority: HIGH — unlocks step-level scoring**

Current tools evaluate final answers. Extend the `ReasoningTool` interface:

```python
class ReasoningTool:
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Existing: rank candidate answers."""

    def confidence(self, prompt: str, answer: str) -> float:
        """Existing: confidence in answer."""

    def evaluate_trace(self, prompt: str, trace: list[str], answer: str) -> dict:
        """NEW: score a reasoning chain step-by-step.
        Returns {"score": float, "step_scores": [float, ...],
                 "flags": ["step_3_contradicts_step_1", ...]}"""
```

Optional method — tools that don't implement it fall back to answer-only evaluation. This is backward-compatible. New forges can target trace evaluation.

**Where:** `hephaestus/src/test_harness.py` (extended interface), `hephaestus/src/prompts.py` (updated contract)

### 1C. Execution Evaluator (cheap v1) -- DONE
**Priority: HIGH — grounds reasoning in behavior**

A hand-crafted tool that catches cases where reasoning sounds right but is numerically wrong:

```python
class ExecutionEvaluator(ReasoningTool):
    def evaluate(self, prompt, candidates):
        # Extract numeric expressions from prompt
        # Evaluate them with Python
        # Compare candidate answers to computed results
```

Covers: arithmetic, numeric comparison, "all but N" patterns, probability calculations. Does NOT require Z3 or Lean — just `eval()` on extracted expressions with sandboxing.

**Where:** `hephaestus/forge/execution_evaluator.py` (hand-crafted seed tool)

---

## Phase 2 — Nemesis: Adversarial Co-Evolution (weeks 2-4)

### The Question Nemesis Answers

> **"Are our evaluators measuring reasoning, or have they learned to pass tests?"**

Without adversarial pressure, we can't distinguish a tool that detects real reasoning from one that pattern-matches the trap battery. If IBAI v2 scores 67% on static traps but 30% on adversarial mutations, it's not measuring reasoning — it's measuring trap familiarity. Nemesis is the immune system that prevents Goodharting.

### The Missing Agent

**Nemesis** — goddess of retribution. Pure algorithmic (no API calls). Generates adversarial tasks designed to break current tools, maintains a living adversarial set (capped at 100), and feeds failure data back through Coeus.

```
Nous → Coeus → Hephaestus → Nemesis
                    ↑              ↓
                    └── failures ──┘
                    ↑              ↓
              Coeus ←── failure data
```

Nemesis sits AFTER Hephaestus. She takes the current tool library and tries to destroy it. See [nemesis_design.md](nemesis_design.md) for full specification.

### 2A. Nemesis Core Engine

```
agents/nemesis/
├── src/
│   ├── nemesis.py           — Main adversarial engine
│   ├── trap_mutator.py      — Mutate existing traps to find blind spots
│   ├── structure_breaker.py — Generate long-range dependencies, nested conditionals
│   ├── causal_traps.py      — Counterfactual / intervention-based traps
│   └── execution_traps.py   — Reasoning that sounds right but fails when run
├── adversarial/             — Generated adversarial task sets
├── configs/manifest.yaml
└── README.md
```

**Nemesis's fitness signal:** She is rewarded when:
- Models score high but are actually wrong (tool failure)
- Tools disagree with each other on the same prompt
- Execution contradicts the reasoning trace

This is GAN-like but the objective is **epistemic failure discovery**, not realism.

### 2B. Mutation Operators

```python
# Flip comparisons
"9.11 is larger than 9.9" → "9.9 is larger than 9.11"

# Insert negations
"All cats are animals" → "Not all cats are animals"

# Extend reasoning chains
"A > B, B > C" → "A > B, B > C, C > D, D > E"

# Add irrelevant distractors
"A bat and ball cost $1.10" → "A bat, ball, and unused glove cost $1.10"

# Swap agent/patient
"The dog chased the cat" → "The cat chased the dog"

# Counterfactual injection
"If it rains, ground is wet" → "If it rains, ground is wet. It rained. Is the ground dry?"
```

### 2C. Feedback Loop

When Nemesis breaks a tool:
1. The failure case is logged with the tool's failure mode
2. The failure mode is fed to Nous as a **targeted concept triple** request: "build a tool that catches this specific failure"
3. Hephaestus forges a tool targeting that weakness
4. Nemesis tries to break the new tool
5. Repeat

This is **failure-driven evaluator synthesis** — the forge becomes reactive to discovered weaknesses rather than just exploring the concept space.

### 2D. Integration with Hephaestus

Add to `test_harness.py`:
- In addition to the static/generated trap battery, run the **Nemesis adversarial set** (latest generated adversarial tasks)
- Tools must survive both to be forged
- Nemesis adversarial set updates periodically (unlike static traps)

---

## Phase 2b — Nemesis Evolution (after initial Nemesis operational, weeks 3-4)

### Adversarial Lineage Tracking
Track mutation-of-mutation chains. Lineages that break successive tools across
generations probe fundamental weaknesses, not surface quirks. Priority in the
living adversarial set scales with lineage depth.

### Per-Tool Learned Difficulty
Replace static difficulty (1-10) with adaptive per-tool difficulty model based
on observed pass/fail rates per mutation category. Focuses pressure at each
tool's decision boundary.

### Semantic Equivalence as Primary Diagnostic
Once Category 7 (paraphrase mutations) is operational, use it as the primary
Goodhart detector: if a tool's adversarial accuracy on paraphrases is significantly
lower than on structural mutations, it's detecting syntax not reasoning.

---

## Phase 3 — Coeus v3 & Multi-Objective Fitness (weeks 4-6)

### Dual Causal Graphs
Once Nemesis has been producing adversarial results, Coeus maintains TWO graphs:
1. **Forge success graph** — which concepts predict passing the static battery
2. **Adversarial robustness graph** — which concepts predict surviving Nemesis

The **divergence** between these two graphs is the key diagnostic. Concepts that
predict forge success but NOT adversarial robustness produce tools that pass tests
but don't detect reasoning. Concepts that predict BOTH produce genuine evaluators.

### Bidirectional Interventional Estimates
Currently: P(forge | do(remove X)). Add: P(forge | do(add X to failing triple)).
The asymmetry reveals whether a concept is a necessary ingredient or merely
correlated with other necessary ingredients. If removing Criticality drops forge
rate but adding it doesn't rescue failing triples, Criticality is a marker, not
the active ingredient.

### Temporal Causal Analysis (PCMCI)
Add time dimension to the causal graph. Nous prompt has evolved, enrichments have
been added, sampling weights have changed. A forge from run 1 and run 5 happened
under different conditions. PCMCI (tigramite) lets Coeus distinguish "this concept
produces good tools" from "this concept produced good tools before we improved the
prompt." Requires `tigramite` package.

### DAGMA Divergence Monitoring
At 200+ forges, DAGMA activates. Monitor explicitly for cases where non-linear
effects contradict linear model. If Ergodic Theory + Theory of Mind is the top
linear synergy but DAGMA finds it's actually Ergodic Theory + Active Inference
with Theory of Mind as confounder, that changes the sampling strategy.

### 3A. Multi-Objective Fitness (originally Phase 3)

### 3A. Fitness Vector (not scalar)

Replace single pass/fail with a multi-dimensional fitness object:

```json
{
  "structural": 0.67,
  "execution": 0.80,
  "causal": 0.45,
  "invariance": 0.72,
  "calibration": 0.53,
  "adversarial_survival": 0.60
}
```

Use Pareto front selection: a tool survives if no other tool dominates it on ALL dimensions. This prevents collapsing to a single proxy metric (Goodhart).

**Where:** `hephaestus/src/test_harness.py` (multi-channel evaluation), `hephaestus/src/fitness.py` (new: Pareto aggregation)

### 3B. Causal Perturbation Evaluator

A tool that explicitly tests counterfactual validity:

```python
class CausalEvaluator(ReasoningTool):
    def evaluate(self, prompt, candidates):
        # 1. Extract causal claims from prompt ("if P then Q")
        # 2. Generate counterfactual: "what if not-P?"
        # 3. Check if candidate answer changes appropriately
        # 4. Score based on causal consistency
```

This is the "do-calculus for reasoning chains" — testing whether the model's answer is causally valid, not just internally consistent.

### 3C. Invariance Testing Suite

Expand the perturbation calibrator into a full invariance test battery:

| Transform | What it tests | Example |
|-----------|--------------|---------|
| Paraphrase | Meaning preservation | "Is 9.11 > 9.9?" → "Is nine point eleven greater than nine point nine?" |
| Order | Premise independence | Swap sentence order in multi-premise prompts |
| Distractor | Irrelevant detail robustness | Add unrelated facts to prompt |
| Negation flip | Logical sensitivity | "Is X true?" → "Is X false?" (answer should flip) |
| Scale | Numeric generalization | "9.11 vs 9.9" → "91.1 vs 99" |

Score = consistency across transforms. Truth is invariant under symmetry transformations.

---

## Phase 4 — Closing the RLVF Loop (weeks 6-8)

### 4A. ReasoningEpisode Schema

Standardize everything around a single atomic object:

```json
{
  "episode_id": "uuid",
  "prompt": "...",
  "task_type": "trap | adversarial | synthetic",
  "model": {"model_id": "...", "lora_id": "..."},
  "output": {
    "answer": "...",
    "reasoning_trace": ["step1", "step2"],
    "confidence": 0.8
  },
  "evaluations": [
    {"tool": "IBAI_v2", "structural": 0.7, "flags": []},
    {"tool": "ExecutionEval", "execution": 1.0},
    {"tool": "CausalEval", "causal": 0.4, "flags": ["counterfactual_fail"]}
  ],
  "fitness": {
    "structural": 0.7,
    "execution": 1.0,
    "causal": 0.4,
    "invariance": 0.6,
    "composite": 0.65,
    "pareto_rank": 3
  }
}
```

This flows through the entire system: Rhea generates episodes, forged tools evaluate them, fitness drives evolution.

### 4B. Selection Loop (Rhea Integration)

For each prompt:
1. Generate K=5-10 candidates from evolved model
2. Evaluate all with full tool library (structural + execution + causal + invariance)
3. Compute fitness vector
4. Select top 1-2 by Pareto rank
5. Store as elite dataset
6. Use elite traces as few-shot examples for next generation

This approximates evolution via sampling + selection + replay — no CMA-ES needed for v1.

### 4C. Failure-Driven Forge Trigger

When the evaluation loop detects:
- High variance between tools (disagreement)
- High fitness but wrong answer (tool failure)
- New failure mode from Nemesis

→ Feed to Nous as targeted concept triple request
→ Hephaestus forges a tool for that specific failure
→ New tool enters the library
→ Loop continues

**This is the convergence point:** Rhea's evolved models, evaluated by Hephaestus's forged tools, pressured by Nemesis's adversarial tasks, guided by Coeus's causal intelligence. No human in the loop.

---

## Research Foundations

These established fields provide formal grounding for the roadmap. Not analogies —
concrete algorithms and frameworks that should inform implementation.

| Field | Relevant to | Key insight | Library |
|-------|------------|-------------|---------|
| **Metamorphic testing** | Nemesis mutations | Formal taxonomy of input-output relationships. "If you double all numbers, ordering shouldn't change." Principled mutation vocabulary. | `gemtest` |
| **Abstract interpretation** | Pareto tool selection | Forged tools are abstract interpreters. Soundness (no false negatives) vs completeness (no false positives). Diverse spectrum > clustered tools. | Theory only |
| **Property-based testing** | Nemesis shrinking | Auto-find minimal failing case. Minimal cases far more informative for Coeus. | `hypothesis` |
| **NSGA-III** | Multi-objective fitness | 6-dim fitness needs diversity preservation. Reference points prevent Pareto crowding. | `pymoo` |
| **DoWhy + DoWhy-GCM** | Coeus refutation | Automatic refutation tests on every causal edge. Concepts that survive refutation get boosted; fragile ones get warnings. | `dowhy` |
| **gCastle** | Coeus algorithm diversity | 20+ discovery algorithms in one API. Surfaces what DAGMA misses on small data. | `gcastle` |
| **Hoare Logic** | Trace evaluation | Pre/post conditions on reasoning steps. {P}step{Q} catches internal contradictions final-answer tools miss. | Theory + regex |
| **Sensitivity Analysis** | Coeus robustness | Is this causal effect robust under model misspecification? Complements FCI confounder detection. | `dowhy` |

---

## Architectural Invariant: Data Provenance

Every data point carries a provenance tag enforced in code (not convention):
- `training` — verified reasoning chains (Rhea)
- `evaluation` — trap battery results (Hephaestus)
- `adversarial` — Nemesis failure cases (test suites only)

Hard gate prevents cross-contamination. Adversarial data never enters training.
Batch 3 cost: 25 points metacognition from mixing adversarial into training.

---

## Priority Order

| # | Phase | Task | Impact | Effort | Status |
|---|-------|------|--------|--------|--------|
| 1 | 1 | Dynamic trap generation | Prevents overfitting | Low | **DONE** |
| 2 | 1 | Execution evaluator | Grounds in behavior | Low | **DONE** |
| 3 | 1 | Reasoning trace interface | Step-level scoring | Medium | Designed |
| 4 | **2** | **Nemesis agent (12 MRs, MAP-Elites grid)** | **Adversarial pressure** | **Medium** | **DONE** |
| 5 | 2 | Semantic equivalence mutations (paraphrase MR) | Goodhart detector | Low | **DONE** (in #4) |
| 6 | 2 | Compositional depth scaling (chain_extend MR) | Precision instrument | Low | **DONE** (in #4) |
| 7 | 2 | Adversarial task validation (exec evaluator) | Prevents bad ground truth | Low | **DONE** (in #4) |
| 8 | 2b | Adversarial lineage tracking | Finds deep weaknesses | Medium | **DONE** |
| 9 | 2b | Per-tool learned difficulty | Focuses pressure | Medium | **DONE** |
| 10 | 3 | Dual causal graphs (forge vs adversarial) | Key diagnostic | Medium | **DONE** — Goodhart warnings operational |
| 11 | 3 | Bidirectional interventional estimates | Active ingredient detection | Medium | 300+ forges |
| 12 | 3 | Temporal causal analysis (PCMCI) | Prompt evolution effects | Medium | tigramite + data |
| 13 | 3 | DAGMA divergence monitoring | Non-linear contradiction detection | Low | ~200 forges (imminent) |
| 14 | 3 | RLVF fitness function F(T) = Σwᵢ·Sᵢ - λ·σ(S) | Weighted multi-tool scoring | Medium | **DONE** — 122 tools, variance penalty |
| 15 | 3 | Causal perturbation evaluator | Counterfactual validity | Medium | After #3 |
| 16 | 3 | Invariance testing suite | Robustness | Medium | After #5 proven |
| 17 | 4 | ReasoningEpisode schema + provenance gate | Standardizes data flow | Medium | **DONE** — hard gate in code |
| 18 | 4 | Failure-driven forge trigger | Closes the loop | Low | **DONE** — blind spots → targeted requests |
| 19 | 4 | Rhea integration | Full RLVF loop | High | **NEXT** — fitness function ready |
| 20 | 2 | Metamorphic relations framework (12 MRs + composition) | Principled mutation taxonomy | Low | **DONE** (built into #4) |
| 21 | 2 | Shrinking for minimal failing cases | Better Coeus feedback | Low | **DONE** (built into #4) |
| 22 | 3 | DoWhy refutation tests on causal edges | Refutation p-values on every edge | Medium | After 200+ forges |
| 23 | 3 | gCastle algorithm diversity | Discovery algorithms DAGMA misses | Low | After DoWhy |
| 24 | 3 | Soundness/completeness profiling | Abstract interpretation for tools | Medium | After Nemesis data |
| 25 | 3 | Hoare-style trace pre/post conditions | Internal contradiction detection | Medium | After #3 wired |
| 26 | 4 | Provenance gate extend with DoWhy robustness tag | Prevent fragile verifiers entering Rhea | Low | After #22 |
| 27 | 3 | Heterogeneous Treatment Effects (econml CausalForest) | When/with-what concepts work, not just IF | Medium | 300+ forges |
| 28 | 3 | Bayesian Structural Time Series (CausalPy) | Measure causal impact of pipeline changes | Medium | After multiple prompt versions |
| 29 | 2 | Mechanism-type diversity bias in Nous sampling | Ensure triples have constraint+structure+dynamics+measure | Low | **DONE** (metadata added) |
| 30 | 3 | Coeus mechanism-type causal model | "Successful tools need constraint+measure" patterns | Medium | After mechanism data accumulates |
| 31 | 2 | NCD-based novelty/coverage for Nemesis adversarial set | Prevent adversarial clustering without neural deps | Low | **DONE** (built into #4) |
| 32 | 4 | Athena: abductive reasoning over pipeline stagnation | Prevents local optima, drives high-level exploration | High | After full loop operational |
| 33 | 2 | MAP-Elites grid for Nemesis adversarial set | QD coverage of failure boundary (complexity × obfuscation) | Medium | **DONE** (core of #4) |
| 34 | 3 | SHAP Interaction Values (XGBoost) for all-pairs concept synergy | 89×89 interaction matrix, finds "dark synergies" | Low | After 200+ forges |
| 35 | 4 | Nemesis variance penalty in RLVF fitness: F(T) = Σwᵢ·Sᵢ - λ·σ(S) | Tool disagreement as first-class fitness signal | Medium | After Rhea integration |
| 36 | 3 | MutPy fuzzing of forged tool code | Catch tools passing traps via trivial logic bugs | Low | After Nemesis operational |

**Completed (not originally planned):**
- Nous prompt rewrite (implementation-focused, steers toward algorithms)
- Coeus-weighted Nous sampling (oversamples forge drivers)
- Prescriptive enrichment directives (Coeus tells 397B HOW to use each concept)
- FCI confounder detection
- Interventional estimates P(forge | do(remove X))
- Nous concept dictionary expanded to 95 (added Metamorphic Testing, Property-Based Testing, Abstract Interpretation, Hoare Logic, Sensitivity Analysis, Satisfiability)
- Mechanism metadata added to all 95 concepts (constraint: 15, structure: 28, dynamics: 38, measure: 14)

**PHASES 1-4 SUBSTANTIALLY COMPLETE.** 22 items done. The RLVF loop is built.

**What's operational:**
- Nous → Coeus → Hephaestus → Nemesis (full pipeline, all continuous)
- RLVF fitness function: F(T) = Σwᵢ·Sᵢ - λ·σ(S) with 122 tools
- Dual causal graph: Goodhart warnings identify concepts that pass tests but don't detect reasoning
- Provenance gate: hard code enforcement, adversarial data cannot enter training
- Failure-driven forge: Nemesis blind spots → targeted concept requests
- Adversarial-aware sampling: Nous demotes Goodhart concepts, boosts undervalued ones

**What's next (remaining roadmap items):**
- **#19 Rhea integration** — connect fitness function to CMA-ES evolutionary loop
- #11 Bidirectional interventional estimates (300+ forges)
- #12 Temporal causal analysis / PCMCI
- #15 Causal perturbation evaluator
- #27 econml CausalForest for heterogeneous treatment effects
- #32 Athena as abductive reasoner over pipeline stagnation

---

## The Big Picture

The system evolves from:

```
Static concept mining → static evaluation → pass/fail
```

To:

```
Adversarial task generation ↔ evaluator co-evolution ↔ model evolution
```

Three populations co-evolving:
- **Generators** (Rhea's models) — evolve to produce reasoning that survives evaluation
- **Evaluators** (Hephaestus's tools) — evolve to catch failures the generators exploit
- **Adversaries** (Nemesis's tasks) — evolve to expose weaknesses in both

This is **reasoning as survival under a growing set of computable constraints** — an evolutionary ecology where the definition of "good reasoning" itself evolves alongside the models being evaluated.

---

## Agent Namespace (updated)

| Agent | Role | Status |
|-------|------|--------|
| Nous | Concept mining | Operational (continuous) |
| Coeus | Causal intelligence | Operational (batch, auto-triggered) |
| Hephaestus | Forge + validate | Operational (continuous) |
| Nemesis | Adversarial co-evolution | **Planned (Phase 2)** |
| Athena | Chief science officer | Reserved |
| Rhea | Model evolution (CMA-ES/LoRA) | Operational (Ignis) |
| Eos/Dawn | Orchestration | Operational |
| Metis | System orchestrator | Operational |
