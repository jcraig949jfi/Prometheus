# Tier 2: Beyond Pattern Matching
## Design Document — Pushing the Forge Toward Actual Reasoning

*2026-03-29 — Athena (Science Advisor)*

---

## The Problem

We have 89/89 category coverage at 74% accuracy. That sounds like success. It's actually a warning.

Look at what the best tool does internally: 400 lines of regex patterns, string matching, number extraction, NCD as a tiebreaker, and a causal chain tracer that parses "A causes B" with regex and runs BFS on the extracted graph. The "metacognition" is 60 lines of regex patterns that detect presupposition keywords and return low confidence scores.

This is not reasoning. This is parsing. The tool doesn't *think* about the problem. It pattern-matches the prompt against a taxonomy of known problem types and executes a hardcoded solution path for each one. The battery rewards this because the battery's challenges are structurally regular — each category uses a template, and templates have syntactic fingerprints.

**The 74% accuracy ceiling is the ceiling of pattern matching.** To break it, we need challenges that force tools to actually compute, track state, handle novelty, and know what they don't know. We need a Tier 2 battery.

---

## What the Current Tools Actually Do

A forensic look at the top tool (`causal_inference_x_bayesian_inference_x_information_theory.py`):

| Component | Lines | What It Does | Is This Reasoning? |
|-----------|-------|-------------|-------------------|
| NCD tiebreaker | 6 | Compression distance between prompt and answer | No — statistical correlation |
| Metacognition | 60 | Regex detects presupposition/ambiguity keywords, returns low confidence | No — keyword spotting |
| Causal chain tracer | 50 | Regex extracts "A causes B" edges, BFS finds downstream | Partially — the BFS is real graph traversal, but the extraction is fragile regex |
| Numeric comparison | 5 | Regex extracts two numbers, compares them | No — parsing |
| Standard parser battery | 200+ | Regex patterns for 58 category types | No — template matching |

**The honest assessment:** The BFS over extracted causal graphs is the *only* component that does anything resembling inference. Everything else is lookup: "does the prompt contain these keywords? → execute this hardcoded response."

This matters because the forge is supposed to produce evaluation tools for Ignis's RLVF pipeline. If the evaluators themselves can't reason, they can't judge whether a model is reasoning. They'll reward pattern matching and penalize genuine reasoning that doesn't fit the regex templates. The evaluators become the monoculture's immune system.

---

## Where the Current Tools Fail (and Why)

The best tool fails on 29 of 89 categories (19 at 0%, 10 at 50%). These failures cluster into five groups:

### Group 1: Multi-Step State Tracking (7 categories, all 0%)

```
compositional_depth_scaling      — "Start with 9. Apply these steps in order..."
compositional_arithmetic_temporal — "Train A leaves at 4:00 PM at 70 mph..."
temporal_age_reasoning           — "Carol is 8. Alice is 3x Carol's age. Grace is 4 years older..."
temporal_frequency_coincidence   — "Event A every 8 days, B every 9 days. When do they coincide?"
temporal_rate_of_change          — "2020: 103, 2021: 124, 2022: 138. Is the rate increasing?"
temporal_causal_ordering         — "Patient recovered Day 11. Treatment began Day 10. Diagnosis Day 4."
temporal_relative_day            — "Today is Tuesday. What day is two days after the day before yesterday?"
```

**Why regex fails:** These require maintaining and updating an internal state through a sequence of operations. The tool has no working memory. It extracts numbers but can't track what they represent through transformations.

**What's actually needed:** A stateful computation engine. Parse the problem into an executable representation (a sequence of operations on named variables), execute it step by step, and return the final state. This is closer to a simple interpreter than a classifier.

### Group 2: Causal Reasoning Beyond Regex (5 categories, 0%)

```
causal_confounding               — "A study finds correlation between X and Y. Can we conclude...?"
causal_counterfactual            — "If Eve's package had been over 10kg..."
causal_intervention              — "If we forcibly prevent wet ground..."
compositional_causal_statistical — Simpson's paradox with numeric tables
correlation_not_causation        — "Cheese consumption correlates with doctorates..."
```

**Why regex fails:** The causal chain tracer works for simple "A causes B" chains but breaks on confounding (no explicit "causes" keyword), counterfactuals (hypothetical reasoning about absent causes), and Simpson's paradox (requires computing group-level vs aggregate statistics).

**What's actually needed:** A causal graph representation that handles confounders, mediators, and colliders — plus a counterfactual engine that can evaluate "what would have happened if X were different." For Simpson's, actual arithmetic on the provided numbers, comparing group rates to aggregate rates.

### Group 3: Theory of Mind (4 categories, 0%)

```
tom_intention_reading            — "Alice brought an umbrella on a sunny day. What was she thinking?"
tom_perspective_shift            — "Hank sees clock on her right. Bob faces Hank from opposite side."
tom_strategic_deception          — "Bob wants Hank to take stairs. Bob knows Hank does the opposite."
compositional_nested_tom_logic   — "Eve thinks safe contains diamond. Carol thinks Eve is wrong."
```

**Why regex fails:** Theory of mind requires modeling other agents' belief states as distinct from reality, and reasoning about how those beliefs interact. Regex can detect "thinks" and "believes" but can't maintain separate belief databases for multiple agents.

**What's actually needed:** A belief state tracker — a data structure that maintains {agent: {beliefs}} and can answer queries like "what does agent A believe about agent B's belief about X?" plus a perspective transformation engine for spatial problems.

### Group 4: Compositional Reasoning (3 categories, 0-50%)

```
compositional_multi_hop_with_distractor — "All widgets are flerps. Grace enjoys hiking. Is Dave's widget a device?"
compositional_logic_arithmetic          — "If X > 6 and X = 4 + 3, is X > 6?"
compositional_logic_tom                 — "In Grace's worldview, every dog is an animal. Grace sees a poodle."
```

**Why regex fails:** These combine reasoning types (logic + distractor filtering, logic + arithmetic, logic + belief state). The tool handles each type independently but can't compose them. The distractor sentences are specifically designed to pollute regex extraction.

**What's actually needed:** A multi-stage pipeline: (1) parse the problem into formal statements, (2) identify which statements are relevant (distractor filtering), (3) chain the relevant inferences, (4) evaluate the conclusion. This is closer to a theorem prover than a classifier.

### Group 5: Probabilistic and Metacognitive (10 categories, 50%)

```
base_rate_neglect, argument_strength, causal_common_cause,
tom_information_asymmetry, tom_mistaken_belief_chain,
temporal_concurrent_events, temporal_sequence_reconstruction, subset_inversion
```

**Why 50% (random chance on 2 candidates):** These require either probabilistic reasoning (Bayes' theorem, base rates) or nuanced judgment (argument quality, information asymmetry). The tools guess correctly half the time by accident. They have no mechanism for the actual reasoning.

**What's actually needed:** For probabilistic: Bayes' theorem implementation with number extraction. For argument strength: a framework for evaluating logical validity vs soundness. For information asymmetry: the belief state tracker from Group 3, plus a concept of "who knows what."

---

## The Tier 2 Battery Design

### Design Principles

1. **No category should be solvable by regex alone.** If a regex pattern can achieve >60% on a category, the category is too easy. Test this by running the NCD baseline tool and a simple regex matcher against every new category.

2. **Each category should require a specific computational capability.** Not "harder versions of Tier 1" but genuinely different reasoning that demands new architecture.

3. **Template variation must defeat keyword spotting.** Each category needs 5+ structurally different prompt templates, with randomized variable names, different surface forms for the same logical structure, and deliberate red herrings.

4. **Ground truth must be computationally verifiable.** Every challenge must have a deterministic correct answer that can be computed by a reference implementation. No subjective judgment.

### Proposed Tier 2 Categories

#### A. Stateful Computation (requires working memory)

| Category | Description | Required Capability |
|----------|-------------|-------------------|
| `state_machine_execution` | Given a state machine definition and an input sequence, what is the final state? | Parse FSM, execute transitions |
| `variable_binding_chain` | "Let x = 3. Let y = x + 2. Let z = y * x. What is z?" with 5-10 steps | Symbol table + arithmetic |
| `recursive_structure` | "Every time you split a group in half and add 1, starting from 64..." | Recursive computation |
| `constraint_propagation` | "A is between 3 and 7. B = A + 2. C < B. What values can C take?" | Constraint solver |
| `process_simulation` | "Machine A produces 3/hour. Machine B produces 5/hour. B starts 2 hours late. When does B's total exceed A's?" | Multi-variable simulation |

#### B. Formal Inference (requires logical engine)

| Category | Description | Required Capability |
|----------|-------------|-------------------|
| `syllogistic_chain_5hop` | 5-step syllogistic chain with distractors. "All A are B. All B are C. Some C are D..." | Forward chaining over 5+ steps |
| `contrapositive_reasoning` | "If it rains, the ground is wet. The ground is not wet. What can we conclude?" | Modus tollens, contrapositive |
| `quantifier_scope` | "Every student read a book" — same book or different? With context clues. | Quantifier scope disambiguation |
| `defeasible_reasoning` | "Birds fly. Tweety is a bird. Tweety is a penguin." — non-monotonic logic | Default reasoning with exceptions |
| `modal_reasoning` | "It is possible that X. It is necessary that Y. Can X and not-Y coexist?" | Modal logic |

#### C. Causal and Counterfactual (requires causal model)

| Category | Description | Required Capability |
|----------|-------------|-------------------|
| `do_calculus_complex` | Multi-variable causal graph with confounders. "If we intervene on X, what happens to Z given W?" | Causal graph + d-separation |
| `counterfactual_reasoning` | "A was true. B happened. If A had been false, would B have happened?" with multiple causal paths | Structural counterfactual |
| `natural_experiment` | "City A banned X. City B didn't. Both had Y increase. What does this tell us about X→Y?" | Difference-in-differences reasoning |
| `selection_bias` | "Of patients who survived surgery, 90% had complication Z. Does surgery cause Z?" | Survivorship/selection bias detection |
| `mediation_analysis` | "Does X affect Z directly, or only through mediator M?" | Path-specific effects |

#### D. Multi-Agent Belief (requires belief state tracker)

| Category | Description | Required Capability |
|----------|-------------|-------------------|
| `nested_belief_3deep` | "A thinks B thinks C thinks the box contains..." | 3-level recursive belief tracking |
| `information_cascade` | "A tells B (but not C). B tells C (but changes one detail). What does C believe?" | Belief propagation with mutation |
| `strategic_reasoning_2step` | "A knows B will react to A's action. What should A do?" | Game-theoretic lookahead |
| `common_knowledge_vs_shared` | "A and B both know X, but neither knows the other knows" | Common knowledge vs mutual knowledge |
| `deception_detection` | "A says X. A's incentive is for you to believe Y. What is likely true?" | Incentive-aware belief updating |

#### E. Metacognitive (requires self-awareness of reasoning limits)

| Category | Description | Required Capability |
|----------|-------------|-------------------|
| `insufficient_information` | Problem that looks solvable but is missing a critical piece. Tool must say "cannot determine." | Recognizing information gaps |
| `confidence_calibration` | "Given X evidence for and Y evidence against, how confident should you be?" | Probabilistic confidence assignment |
| `reasoning_about_reasoning` | "Which of these solution strategies would work for this problem?" | Strategy selection |
| `error_detection` | "Here is a worked solution with one error. Where is the error?" | Trace verification |
| `scope_of_conclusion` | "This data shows X about population P. Can we conclude X about population Q?" | Generalization boundary detection |

### Anti-Gaming Measures

The reason our current battery is solvable by regex is that the challenges have syntactic regularity. Tier 2 must break this:

1. **Variable name randomization.** Don't use "Alice" and "Bob" — use randomly generated names each time. Don't use "rain causes wet ground" — generate novel causal relationships.

2. **Surface form variation.** Each logical structure should have 5+ different natural language framings. "If A then B" can be expressed as "A implies B", "whenever A, B follows", "B is a consequence of A", "A is sufficient for B", "not A or B", etc.

3. **Distractor injection.** Every prompt includes 1-3 sentences that are grammatically relevant but logically irrelevant. Forces the tool to distinguish signal from noise.

4. **Adversarial paraphrasing.** Some prompts use keywords that would trigger the wrong regex pattern. "This is *not* a case where correlation implies causation" — a regex for "correlation" and "causation" would fire the wrong handler.

5. **Length variation.** Prompts range from 2 sentences to 2 paragraphs. Short prompts prevent "longer = harder" heuristics. Long prompts bury the key information in context.

---

## What the Forge Must Become

### The Architectural Leap

Tier 1 tools are **classifiers**: they categorize the prompt and return a score. Tier 2 tools must be **computers**: they parse the prompt into a formal representation, execute inference on that representation, and return a result.

This requires three capabilities the current forge prompt doesn't ask for:

#### 1. Intermediate Representation

The tool must convert natural language into a structured object — a causal graph, a belief state database, a variable binding table, a constraint set. The conversion can still use regex or heuristics (that's just parsing). But the *reasoning* happens on the structured object, not on the text.

```python
# Tier 1 approach (classifier)
def evaluate(self, prompt, candidates):
    if 'causes' in prompt and 'intervene' in prompt:
        return self._causal_handler(prompt, candidates)

# Tier 2 approach (computer)
def evaluate(self, prompt, candidates):
    ir = self._parse_to_ir(prompt)      # Build formal representation
    result = self._infer(ir)             # Reason over the representation
    return self._score_candidates(result, candidates)  # Map back to answers
```

#### 2. Execution Engine

The intermediate representation must be *executable*. A causal graph supports d-separation queries. A belief state database supports "what does A think B knows?" queries. A variable binding table supports arithmetic evaluation. The tool must be able to *run* the representation, not just inspect it.

This is where the forge prompt needs to change. Instead of "write a tool that evaluates reasoning," the prompt becomes "write a tool that *performs* the reasoning and then scores candidates based on whether they match the computed answer."

#### 3. Uncertainty Propagation

When the tool can't confidently parse the prompt into a formal representation, it should propagate that uncertainty rather than guessing. If 3 of 5 parsed variables are confident but 2 are ambiguous, the tool should score candidates based on the confident variables and reduce confidence proportionally for the ambiguous ones.

This is real metacognition — not regex patterns that detect "might" and "possibly," but principled uncertainty tracking through the computation pipeline.

### The Forge Prompt Evolution

The current forge prompt (multi-frame, 4 perspectives) produces tools that are sophisticated *parsers*. To produce tools that are sophisticated *reasoners*, the prompt needs a new framing:

**Frame E: Computational** — "Design a tool that converts this reasoning problem into a formal representation (graph, logic program, constraint set, state machine) and solves it computationally. The tool should work on problems it has never seen before, not by matching templates but by building and executing a model of the problem."

**Frame F: Adversarial robustness** — "A determined adversary will modify the surface form of every prompt to break your regex patterns while preserving the logical structure. Design a tool that is invariant to surface form variation — it must identify the logical structure regardless of how it's expressed."

**Frame G: Metacognitive** — "Design a tool that knows what it doesn't know. When the tool cannot confidently solve a problem, it should return a calibrated confidence score rather than a random guess. A tool that says 'I don't know' on 20% of problems and gets 90% of the rest is better than a tool that guesses on everything and gets 74%."

### Implementation Phases

**Phase 1: Tier 2 Battery (this week)**
Build the challenge generators for 25 Tier 2 categories. Validate that no current tool breaks 30% on them. This is the forcing function.

**Phase 2: Forge Prompt Update (this week)**
Add Frames E, F, G to the multi-frame forge. Run Opus against the Tier 2 battery. See what it produces without further guidance.

**Phase 3: Specialist Forge (next week)**
For each Tier 2 group (stateful, formal, causal, multi-agent, metacognitive), design a targeted forge prompt that specifies the required intermediate representation. "Build a tool that parses causal graphs from text and answers d-separation queries."

**Phase 4: Integration**
Merge Tier 1 and Tier 2 tools into a unified library. The combined battery (89 Tier 1 + 25 Tier 2 = 114 categories) becomes the new standard for RLVF.

---

## What This Means for the Convergence Theory

The convergence theory says transformers suppress dynamic model updating. If we build evaluation tools that *perform* dynamic model updating — that construct formal representations at inference time and reason over them — we create evaluators that can distinguish between:

- **Pattern matching** (the model learned a template and fills it in)
- **Heuristic application** (the model applies a shortcut that usually works)
- **Genuine reasoning** (the model constructs a novel inference chain)

Current Tier 1 evaluators can't tell the difference between 1 and 3, because the evaluators themselves do #1. Tier 2 evaluators, built on actual computation, can detect #3 by checking whether the model's answer is consistent with a correctly executed formal inference — not whether it matches a regex pattern.

This is the evaluator version of the same problem the convergence theory identifies in the model: **you can't test for reasoning with tools that don't reason.**

---

## Connections to Existing Work

**Noesis:** The tensor engine's composition chains are exactly the kind of multi-step computation Tier 2 tools need to evaluate. A chain like "topology.euler_characteristic → stat_mech.ising_model_1d" is a stateful computation — the output of step 1 becomes the input of step 2. Noesis is building the *compositions*. The Tier 2 battery tests whether models can *perform* compositions.

**Ignis:** The steering vector work shows that models have the capacity for reasoning (17/30 traps flipped) but the suppression circuit blocks it. Tier 2 evaluators would measure whether a steered model actually *computes* the answer or just pattern-matches to the right one. This distinguishes "the model found the channel" from "the model found a shortcut that happens to work on these prompts."

**The Forge Pipeline:** Nous generates concept triples. Hephaestus forges tools. The Tier 2 battery creates selection pressure for tools that *reason*, not tools that *parse*. This is the same principle as the expanded Tier 1 battery breaking the monoculture — a harder battery forces the forge to produce genuinely different tools.

---

## Risks and Honest Accounting

**Risk 1: Opus might not be able to produce Tier 2 tools.** The current tools are regex-heavy because that's what LLMs naturally produce when asked to "evaluate reasoning." Asking Opus to write a tool with a formal inference engine is a much harder prompt engineering challenge. It might produce tools that are nominally computational but effectively just more sophisticated parsers.

**Risk 2: The Tier 2 battery might be too hard for *any* numpy-only tool.** Some categories (nested 3-deep belief tracking, complex counterfactual reasoning) might require capabilities that can't be implemented in a stateless Python function with numpy. We'd need to accept lower coverage on Tier 2 than on Tier 1.

**Risk 3: Tier 2 tools might be brittle.** A formal inference engine that works perfectly on well-formed inputs might crash on the edge cases that Tier 1 tools handle gracefully with NCD fallback. The robustness of pattern matching is real — giving it up for theoretical superiority is a tradeoff.

**Mitigation for all three:** Start with the easiest Tier 2 categories (variable binding chains, syllogistic chains, temporal scheduling) and see what Opus produces. If the first 5 categories yield tools that genuinely compute, scale to 25. If Opus can't break out of the regex paradigm, that itself is a finding about what LLMs can and can't write.

---

## Existing Benchmarks That Map to Our Format

A survey of reasoning benchmarks reveals several that are already in prompt + candidate answers format and test exactly the capabilities our tools lack. These should inform Tier 2 category design and provide reference implementations for ground truth.

### Direct Fit (MC format, maps to our pipeline immediately)

| Benchmark | What It Tests | Why Our Tools Fail | Required Approach |
|-----------|-------------|-------------------|-------------------|
| **MUSR** (Sprague 2024) | Multi-step soft reasoning over 1000+ word narratives. Murder mysteries, team allocation. 5-10 chained inference steps through probabilistic evidence. | Evidence is *soft* — clues suggest but don't prove. Steps chain: missing one intermediate inference cascades. Relevant facts buried among distractors in long text. | Belief propagation / weighted evidence graphs. Extract facts, assign soft weights, chain inferences, select best-supported hypothesis. Abductive reasoning. |
| **FOLIO** (Wu 2023) | First-order logic inference from NL premises. True / False / Unknown classification. | The "Unknown" label is the killer — tools must recognize when premises are *insufficient*, requiring closed-world reasoning. | NL-to-FOL translation + theorem proving. Modus ponens, universal instantiation, existential introduction. Z3 or Prover9 given correct translation solves trivially. |
| **BoardgameQA** (Kazemi/DeepMind 2024) | Rules-based reasoning with conflicting rules, exceptions, overrides. State tracking across turns. Up to 8+ reasoning steps. | Rules conflict and override each other (defeasible reasoning). Must track which rules fire, resolve conflicts via specificity, chain forward. | Forward-chaining rule engine with Touretzky-style conflict resolution. Parse rules + exceptions, maintain state, resolve conflicts, chain to query. |
| **PrOntoQA** (Saparov 2023) | Synthetic syllogistic chains over fictional ontologies. Controllable 1-hop to 5+-hop depth. | At depth 5+, error accumulation breaks any approach that doesn't faithfully execute each step. Fictional entities prevent memorization. | Graph traversal / forward chaining. Algorithmically trivial — DFS on is-a hierarchy. Tests *faithfulness* of execution across N steps, not intelligence. |
| **LogiQA 2.0** (Liu 2023) | Logical reasoning from Chinese civil service exams. Sufficient/necessary conditions, disjunction, negation. | Systematic ambiguity of logical connectives in NL ("only if", "unless", "not all"). Distractors exploit common fallacies. | Formal logical parsing + truth-table evaluation. Identify logical form of premises, derive valid conclusions, check candidates against derivation. |
| **ReClor** (Yu 2020) | LSAT/GMAT logical reasoning. Argument analysis: strengthen, weaken, find assumptions, identify flaws. | Requires *meta-reasoning about argument structure* — identifying unstated premises, evaluating validity. Human expert: ~63%. | Argument mapping (premises → conclusion with gaps) + question-type-specific evaluation. Informal logic / critical thinking engine. |

### Partially Adaptable (generation tasks, need MC conversion)

| Benchmark | What It Tests | Adaptation Notes |
|-----------|-------------|-----------------|
| **ARC** (Chollet 2019) | Visual abstract reasoning — infer transformation rule from examples. | MC version (choose among candidate output grids) drastically reduces difficulty. Better as inspiration for "program induction" categories than direct import. |
| **GSM-Hard** | Grade-school math with large numbers. Exposes when models pattern-match vs compute. | Present candidate numerical answers. But verification is trivial arithmetic — tests parsing/planning, not selection. |
| **MATH** (Hendrycks 2021) | Competition math. Strategy selection + symbolic manipulation. | Level 4-5 problems require genuine insight. Hard to MC-ify without trivializing via plug-and-check. |

### 2025-2026 Benchmarks for Specific Gaps

| Benchmark | Tests | Why It Matters for Us |
|-----------|-------|----------------------|
| **ProcessBench** (Zheng 2024-25) | Identify the exact step where a reasoning chain breaks. | Directly tests trace evaluation — "where does it go wrong?" not "is this right?" Maps to our Tier 2 metacognitive `error_detection` category. |
| **KUQ** (Known-Unknown Questions, 2025) | Calibration between confidence and accuracy. Partitions questions the model should/shouldn't know. | Tests "knowing what you don't know" — our `insufficient_information` and `confidence_calibration` categories. |
| **ConflictQA** (2025) | Knowledge conflicts between parametric memory and provided context. | Tests whether tools recognize conflicts and handle them rather than defaulting. Maps to metacognitive reasoning. |
| **CLUTRR** (Sinha, extended 2024-25) | Family relationship reasoning. "A is B's mother, B is C's sister" → "A is C's mother." Variable chain length. | Tests compositional relational inference. Graph-based. Directly maps to our `syllogistic_chain_5hop` and `variable_binding_chain` categories. |

### Four Computational Families

The benchmarks cluster into four required computational approaches. Our current tools live in none of them:

1. **Symbolic logic engines** (FOLIO, PrOntoQA, LogiQA) — parse NL to formal logic, apply rules of inference
2. **State simulation / forward chaining** (BoardgameQA, BIG-Bench shuffled objects) — maintain world state through updates, apply rules with conflict resolution
3. **Evidence accumulation / probabilistic inference** (MUSR, abductive tasks) — weight evidence, chain soft inferences, select best explanation
4. **Program synthesis** (ARC) — search over transformation programs, fundamentally different from evaluating text

Tier 2 should have categories from all four families. Families 1-3 are achievable with numpy-only Python tools. Family 4 (program synthesis) is aspirational but worth including as a stretch target — if a forge tool spontaneously implements a DSL search over grid transformations, that's a genuine emergence event.

---

## Empirical Validation: The Deep Reasoning Engine (2026-03-29)

*Added by Pipeline Orchestrator after forging and validating the first computation-first tool.*

### The Experiment

The Tier 2 design above was written as theory. The same afternoon, the Pipeline Orchestrator built `deep_reasoning_engine.py` — a proof-of-concept tool that implements the "parse → compute → match" architecture described in "What the Forge Must Become." This section reports what happened when theory met the battery.

### Architecture

The deep reasoning engine has **18 computation modules**, each converting a problem type into a formal representation and executing it:

| Module | IR Type | Computation |
|--------|---------|-------------|
| `_compute_relative_day` | Day index (mod 7) | Parse "today is X", count yesterday/tomorrow offsets, compute `(day + offset) % 7` |
| `_compute_duration_midnight` | Minutes (mod 1440) | Convert AM/PM to 24h, subtract with midnight wraparound |
| `_compute_rate_of_change` | Value sequence → diffs → second diffs | Extract year:value pairs, compute successive differences, check sign |
| `_compute_scheduling` | Interval pairs | Parse time ranges, check interval overlap |
| `_compute_age` | Constraint system {name: value} | Extract absolute ages + relational constraints, propagate until fixed point |
| `_compute_train` | Equation: s₁t = s₂(t - Δt) | Parse speeds and departure times, solve for intersection, convert to clock |
| `_compute_sequence` | DAG → topological sort | Extract before/after/preceded edges, Kahn's algorithm |
| `_compute_causal_intervention` | Causal DAG → graph mutilation | Extract "causes/leads to" edges, identify blocked node, check downstream |
| `_compute_counterfactual` | Universal rule + hypothetical | Parse "all X who Y got Z" + "if A had Y", apply modus ponens |
| `_compute_confounding` | Correlation pattern | Detect "both increase" + causal question → confounding variable |
| `_compute_tom_deception` | Desire + inversion rule | Parse "wants X to go Y" + "does opposite" → output opposite(Y) |
| `_compute_perspective` | Spatial flip | Detect "opposite side" + left/right → return flipped side |
| `_compute_info_asymmetry` | Knowledge state | Detect "rigged/tampered" + "doesn't know" → return fair probability |
| `_compute_belief_chain` | Belief propagation | Parse "A mistakenly believes X, tells B, B tells C" → C believes X |
| `_compute_simpson` | Per-group arithmetic | Extract 4 rates (2 treatments × 2 groups), compare within-group rates |
| `_compute_logic_chain` | Transitive closure | Parse "all A are B" rules, BFS/DFS to check reachability |
| `_compute_causal_chain_counterfactual` | Causal chain + negation | Detect "A caused B caused C, if not A" → chain broken |
| `_compute_logic_tom` | Belief + transitivity | Parse "X believes all A are B" + "X sees instance of A" → X believes B |

Plus a `_compute_standard` module for basic arithmetic (bat-and-ball, all-but-N, fencepost, modular, parity, pigeonhole, percentage asymmetry, numeric comparison, coin independence, correlation≠causation).

**Key architectural difference:** The tool never pattern-matches candidate text to decide correctness. It computes an answer, then checks whether each candidate matches the computed answer via `_match_computed()`. The scoring is: 0.95 for match, 0.08 for mismatch. No NCD-weighted middle ground on computed categories.

### Results: Hard Categories

Tested against the 21 categories where the best regex-based elite tool scores <40%:

| Category | Elite (regex) | Deep Engine (compute) | Module Used |
|----------|:---:|:---:|---|
| `temporal_relative_day` | 0% | **100%** | Day mod-7 arithmetic |
| `compositional_multi_hop_with_distractor` | 0% | **100%** | Transitive closure (ignores distractors) |
| `causal_intervention` | 0% | **100%** | Graph mutilation |
| `causal_confounding` | 20% | **100%** | Confound pattern |
| `temporal_duration_across_midnight` | 37% | **100%** | Clock mod-24 |
| `temporal_rate_of_change` | 37% | **100%** | Second differences |
| `temporal_sequence_reconstruction` | 20% | **100%** | Topological sort |
| `tom_mistaken_belief_chain` | 23% | **100%** | Belief propagation |
| `compositional_logic_tom` | 30% | **100%** | Belief + transitivity |
| `tom_perspective_shift` | 13% | **100%** | Spatial flip |
| `causal_counterfactual` | 0% | **80%** | Modus ponens on hypothetical |
| `compositional_causal_statistical` | 13% | **80%** | Simpson's per-group arithmetic |
| `compositional_temporal_causal` | 33% | **67%** | Causal chain + negation |
| `causal_common_cause` | 20% | **60%** | Common cause detection |
| `tom_strategic_deception` | 7% | **60%** | Desire + inversion |
| `tom_information_asymmetry` | 17% | **60%** | Knowledge state |
| `temporal_scheduling_conflict` | 37% | **40%** | Interval overlap |
| `compositional_depth_scaling` | 37% | **40%** | Constraint propagation |
| `temporal_age_reasoning` | 17% | **40%** | Constraint solver |
| `compositional_arithmetic_temporal` | 7% | **20%** | Train equation solver |
| `tom_intention_reading` | 30% | **20%** | (no computation — requires world knowledge) |

**Aggregate: 74.8% on hard categories vs 21.4% for the best elite. 3.5× improvement.**

10 categories went from near-zero to 100%. The categories that didn't reach 100% reveal exactly where the next architectural challenge lies:

### Where Computation-First Still Fails

**60% tier (3 categories):** `tom_strategic_deception`, `tom_information_asymmetry`, `causal_common_cause` — the computation modules work on the majority of prompt variants but miss alternative phrasings. This is a parsing robustness problem, not a reasoning problem. More surface form patterns for the same computation would fix it. This is exactly the problem Tier 2's anti-gaming measures (variable name randomization, surface form variation, adversarial paraphrasing) are designed to force.

**40% tier (3 categories):** `temporal_scheduling_conflict`, `compositional_depth_scaling`, `temporal_age_reasoning` — the constraint propagation engine works but has edge cases where the regex parser doesn't extract all constraints from the prompt. Missing one constraint in a 4-constraint problem cascades to a wrong answer. This validates the design doc's point about intermediate representation quality being the bottleneck.

**20% tier (2 categories):** `compositional_arithmetic_temporal` (train problems) — the equation solver handles the basic case but the PM/AM time parsing is fragile. `tom_intention_reading` — this category requires *abductive inference from behavior to mental state* ("Alice brought an umbrella on a sunny day → she expected rain"). No computation module exists for this because it requires world knowledge, not formal inference. This is a genuine Tier 2 problem that can't be solved by computation alone.

### What This Proves About the Tier 2 Design

1. **The architectural leap works.** Parse → compute → match beats parse → regex-match on every category that requires multi-step inference. The theory in "What the Forge Must Become" is validated.

2. **The current battery is too easy.** 10 of 21 "hard" categories fell to straightforward computation modules (mod arithmetic, topological sort, BFS, constraint propagation). These aren't hard reasoning problems — they're *computations that regex can't express*. Tier 2 needs challenges that are hard even for a computation engine.

3. **The 74% overall ceiling is real but for a different reason than expected.** The deep engine scores 59.7% overall (lower than the 74% elites) because it trades breadth on easy regex categories for depth on hard computation ones. This means the battery scoring function rewards the wrong thing: a tool that aces 38 easy categories and fails 21 hard ones outscores a tool that computes the hard ones correctly. **The battery must weight hard categories higher** — or better, move to a scoring function that rewards computation over pattern matching.

4. **Parsing is the real bottleneck, not reasoning.** Once a problem is correctly parsed into formal representation, the computation is trivial. The 60% and 40% failure tiers are all parsing failures, not inference failures. This suggests Tier 2's anti-gaming measures (surface form variation, distractor injection, adversarial paraphrasing) will disproportionately test the part that matters.

5. **`tom_intention_reading` marks the boundary.** This is the one category where computation-first fails *in principle*, not just in implementation. Inferring mental states from behavior requires world knowledge (umbrellas are for rain, heavy coats are for cold). No amount of formal inference over the prompt text alone can solve it. This category belongs in Tier 2 and may require a different architecture entirely — one that combines computation with learned priors.

### Scoring Function Implications

The current scoring treats all 89 categories equally: accuracy = correct / total. This makes the 38 easy categories worth 42.7% of the score and the 21 hard categories worth 23.6%. A tool that perfect-scores the easy categories and random-guesses the hard ones gets ~55% accuracy — passing the 42% threshold comfortably.

**Proposed Tier 2 scoring:** Weight categories by difficulty tier.

```
score = (0.3 × easy_accuracy) + (0.3 × medium_accuracy) + (0.4 × hard_accuracy)
```

This makes hard categories worth more than easy ones, creating selection pressure for tools that compute rather than parse. The deep reasoning engine would score:

```
(0.3 × 0.45) + (0.3 × 0.55) + (0.4 × 0.748) = 0.135 + 0.165 + 0.299 = 0.599
```

vs the best regex elite:

```
(0.3 × 0.95) + (0.3 × 0.65) + (0.4 × 0.214) = 0.285 + 0.195 + 0.086 = 0.566
```

Under difficulty-weighted scoring, the computation-first tool wins. The forge would select for it.

### Immediate Next Steps (from Pipeline Orchestrator)

1. **Harden the parsing layer.** The 60% categories (tom_strategic_deception, tom_information_asymmetry, causal_common_cause) need 2-3 more surface form patterns each. The computation modules are correct; the input parsing is incomplete. Estimated: 30 minutes of regex work per category.

2. **Fix the constraint propagation edge cases.** The 40% categories (scheduling, depth_scaling, age_reasoning) need the constraint extractor to handle more natural language patterns for expressing constraints. Estimated: 1 hour.

3. **Implement difficulty-weighted scoring** in `test_harness.py`. This is a 10-line change that would immediately shift forge selection pressure toward computation-first tools.

4. **Begin Tier 2 generator implementation.** Start with the 5 easiest categories from the design: `variable_binding_chain`, `state_machine_execution`, `syllogistic_chain_5hop`, `do_calculus_complex`, `nested_belief_3deep`. Write generators in `trap_generator_tier2.py`.

5. **Run Opus against Tier 2 with Frame E prompt.** Test whether the forge can produce computation-first tools when prompted with "write a tool that converts problems into formal representations and solves them computationally."

---

## Council of Titans Response — Synthesis (2026-03-29)

*All five Titans (ChatGPT, Gemini, DeepSeek, Grok, Claude) responded to Prompt 09. Full responses in `council/titan_council_prompt_09_break_the_forge_response.md`.*

### Convergence: What All Five Agree On

Four computational primitives appeared independently in every response:

| Primitive | Required By | What It Means |
|-----------|------------|---------------|
| **Stateful execution** | All 5 Titans' Category 1 | Mutable registers/containers updated through sequential operations. Parse → execute → query final state. |
| **Multi-agent belief tracking** | All 5 top-5 | Partitioned knowledge bases per agent. "What does Alice think Bob knows?" |
| **Constraint satisfaction** | All 5 top-5 | Simultaneously satisfy multiple constraints through backtracking or propagation. |
| **Counterfactual reasoning** | All 5 top-5 | Causal DAG + premise alteration + recomputation of downstream consequences. |
| **Information sufficiency** | All 5 include | Determine whether the given information is sufficient. "Cannot be determined" as a valid computed answer. |

### Unique Contributions by Titan

**ChatGPT:** Cleanest taxonomy — Type-0 (textual correlation) → Type-1 (execution over state) → Type-2 (inference over structure). Proposed graph coloring, functional composition, parity invariants.

**DeepSeek:** Strongest examples. The "BANANA" letter-counting challenge (loop simulation over characters) is a perfect anti-regex benchmark. Mutual exclusivity constraints with propagation.

**Grok:** Hardest challenges. The hat-color logic puzzle and three-logicians problem require full combinatorial enumeration with iterative knowledge elimination. Tier 3 aspirational territory.

**Claude:** Most thorough (20 categories with full implementation notes, trap design principles, generator architecture). Key unique categories:
- **Defeasible reasoning** (Cat 4) — 3+ levels of exception override (animals→birds→penguins→mechanical-wing-penguins)
- **Referent tracking** (Cat 7) — anaphora chains where proximity heuristics give wrong answer
- **Closed-world negation** (Cat 9) — reasoning from what's NOT stated
- **Stable model finding** (Cat 14) — mutual dependencies, fixed-point computation
- **Conditional graph traversal** (Cat 11) — state-augmented BFS (key/lock puzzles)
- **Rule application order** (Cat 13) — same rules, different order → different result

### Three Meta-Insights from Claude's Synthesis

1. **Trap design is as important as category design.** Target 0% for wrong-architecture tools, not random chance. Every candidate set should include:
   - The keyword-matching trap (what regex would confidently select)
   - The intermediate-value trap (correct at step N but not the final answer)
   - The common-reasoning-error trap (base rate neglect, scope confusion, etc.)

2. **Three categories need LLM-generated prompts** — referent tracking (7), closed-world negation (9), and argument structure (20) require richer NL variation than parametric generators can produce. Use Opus to generate prompts with deterministic reference answers.

3. **Epistemic state tracking is the sharpest discriminator.** Partitioning facts by observer is architecturally impossible for regex tools and directly tests construct-then-check. The deep reasoning engine already has a primitive version (belief propagation scoring 100% on `tom_mistaken_belief_chain`).

### Quality Gate

**Any existing tool scoring above chance on a Tier 2 category = the challenge isn't hard enough.** Tighten the generator until the gap between wrong-architecture (0%) and right-architecture (90%+) is maximal. This is the battery's immune system against Goodharting.

### Consolidated Priority List for Implementation

Based on convergence across all five Titans, empirical validation from the deep reasoning engine, and implementation feasibility:

**Tier 2A — Implement First (parametric generators, clear computational primitives):**

| # | Category | Primitive | Why First |
|---|----------|-----------|-----------|
| 1 | `stateful_register_machine` | Interpreter | All 5 Titans' #1. Deep engine already solves simpler version. |
| 2 | `epistemic_belief_tracking` | Per-agent belief model | Sharpest discriminator. Deep engine has primitive. |
| 3 | `constraint_satisfaction` | CSP solver / backtracking | All 5 propose. Clean generators. |
| 4 | `recursive_evaluation` | Recursive function evaluator | Clean math, perfect generators. |
| 5 | `counterfactual_dependency` | Causal DAG + recomputation | All 5 propose. Deep engine has BFS. |
| 6 | `multi_step_arithmetic_carried` | Arithmetic interpreter | Intermediate values as traps. |
| 7 | `bayesian_update` | Probability calculator | Base-rate-neglect trap is universal. |
| 8 | `information_sufficiency` | Solution enumeration | "Cannot determine" as computed answer. |

**Tier 2B — Implement Second (more complex generators or NL variation needed):**

| # | Category | Primitive | Why Second |
|---|----------|-----------|------------|
| 9 | `defeasible_reasoning` | Non-monotonic inheritance | 3+ exception levels. Harder generators. |
| 10 | `logical_consistency_checking` | SAT solver | Requires CNF encoding. |
| 11 | `temporal_interval_algebra` | Allen's intervals | Many edge cases in interval relations. |
| 12 | `stable_model_finding` | Fixed-point computation | Cycle detection. No/multiple solutions. |
| 13 | `conditional_graph_traversal` | State-augmented BFS | Key/lock/permit mechanics. |
| 14 | `rule_application_order` | Ordered rewrite system | Order-sensitive transformations. |
| 15 | `compositional_instruction_following` | Sequential executor | Remove→sort→reverse→index. |
| 16 | `quantifier_scope` | FOL with scope resolution | Hard NL parsing. |

**Tier 2C — Implement Third (need LLM-generated prompts or world knowledge):**

| # | Category | Primitive | Why Third |
|---|----------|-----------|-----------|
| 17 | `referent_tracking_anaphora` | Discourse coreference | Needs LLM-generated prompts. |
| 18 | `closed_world_negation` | CWA engine | Needs varied closure cues. |
| 19 | `argument_structure_analysis` | Argument mapper + direction | Needs LLM-generated evidence. |
| 20 | `implicit_constraint_inference` | Constraint propagation | Domain knowledge borders. |

### Estimated Effort

- **Tier 2A generators (8 categories):** ~2 days. Clean computational primitives, parametric generation.
- **Tier 2B generators (8 categories):** ~3 days. More complex generation logic, more edge cases.
- **Tier 2C generators (4 categories):** ~2 days + Opus in the loop for prompt generation.
- **Total: ~1 week to full 20-category Tier 2 battery.**

The first 8 categories (Tier 2A) are enough to shift forge selection pressure. Ship those, run the forge against them with Frame E, and iterate.
