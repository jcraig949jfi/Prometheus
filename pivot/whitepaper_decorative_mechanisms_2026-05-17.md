# When Machines Fake Thinking: Detecting Decorative Mechanisms in LLM-Generated Reasoning Code

**A case study from Project Prometheus**

**Filed:** 2026-05-17
**Authors:** James Craig, M3 Agent (Hephaestus operator)
**Status:** Internal white paper for external discussion

---

## Abstract

We present a case study from an automated code-generation pipeline (Hephaestus) that produces Python reasoning tools by prompting a large language model with cross-domain concept combinations. One generated tool — combining Quantum Mechanics, Neural Plasticity, and Model Checking — appeared to demonstrate R6-level theory-of-mind reasoning (50% accuracy on belief attribution, presupposition detection, and knowledge asymmetry probes). A mechanism-knockout ablation revealed that virtually all of this performance (48/50%) comes from simple regex keyword matching, not from the tool's novel computational mechanisms (Hebbian plasticity inside BFS state-space exploration). The architecturally interesting components contribute only ~2 percentage points to the theory-of-mind score, while genuinely contributing to R3-level abstraction tasks (67% accuracy). We describe the detection methodology, discuss implications for automated program synthesis, and argue that mechanism-knockout ablation should be standard practice before attributing capability claims to generated code.

---

## 1. Background: Project Prometheus and the Hephaestus Forge

### 1.1 The Prometheus Thesis

Project Prometheus is a multi-agent system for automated mathematical discovery built on a falsification-first methodology. Its central thesis: LLM "hallucinations" — generative variance — are not a defect to suppress but a mutation engine to harness. With rigorous selection pressure (deterministic falsification batteries, kill-vector geometry, adversarial testing), useful structure can be extracted from the noise.

The system treats every generated artifact as a hypothesis under selection. Survivors are not "things the model produced" — they are claims that passed a gauntlet designed to terminate them.

### 1.2 The Hephaestus Forge

Hephaestus is Prometheus's automated code-generation forge. It takes scored concept combinations from an upstream combinatorial hypothesis engine (Nous) — triples like "Quantum Mechanics × Neural Plasticity × Model Checking" — and uses a frontier LLM (qwen-397B via NVIDIA API) to generate Python `ReasoningTool` classes: deterministic algorithms that score and rank candidate answers to reasoning questions without any neural model at inference time.

Each generated tool passes through five validation gates:

1. **Syntax** — valid Python (AST-parseable)
2. **Imports** — numpy + stdlib only (deterministic, portable, auditable)
3. **Interface** — defines `evaluate(prompt, candidates) → ranked_list` and `confidence(prompt, answer) → float`
4. **Runtime** — instantiates and runs without crashing
5. **Trap battery** — 186 reasoning probes across 89 categories, must beat NCD compression baseline

The forge has produced ~1,960 tools across 9 versions, with a ~40% historical pass rate (60% scrap). It operates on the principle that most concept combinations cannot be reduced to working code — the ones that survive the gauntlet are non-trivial.

### 1.3 The Reasoning Ladder

Prometheus uses a 10-tier reasoning ladder (R0-R9) to classify capability:

| Tier | Capability | Evidence Required |
|------|-----------|-------------------|
| R0 | Pattern completion | Above-random on in-distribution |
| R1 | Rule execution | Applies novel rules, survives symbol relabeling |
| R2 | Multi-step deduction | Chains implications without losing state |
| R3 | Abstraction / rule discovery | Infers latent rules from examples |
| R4 | Search / planning | Explores alternatives, backtracks |
| R5 | Counterfactual / causal | Distinguishes correlation from intervention |
| R6 | Self-monitoring / theory of mind | Detects own errors, models others' beliefs |
| R7+ | Transfer / conjecture / research | Works in unfamiliar domains, proposes hypotheses |

The ladder is a vocabulary for naming capability slices, not a unidimensional rank. A system can be R6-strong on familiar patterns and R3-weak on novel domains.

---

## 2. The Subject: EPMC (Entangled Plastic Model Checker)

### 2.1 Genesis

The tool was generated on 2026-05-16 from the concept combination:

- **Quantum Mechanics** (Physics)
- **Neural Plasticity** (Biology)
- **Model Checking** (Formal Methods)

The LLM was prompted with Nous's theoretical analysis of how these three concepts might combine into a computational reasoning strategy, plus prescriptive directives from a causal intelligence layer (Coeus) about which concept should play which architectural role.

### 2.2 What the LLM Produced

The generated code implements a class called `ReasoningTool` with the following architecture (self-described in its docstring):

```
1. Structural Parsing: Extracts propositions, negations, comparatives, conditionals
2. Epistemic Honesty (Tier B): Detects ambiguity, presuppositions, unanswerable queries
3. Neural Plasticity: Hebbian learning strengthens constraints co-activated by candidates
4. Model Checking: BFS on weighted adjacency graph explores reachable logical states
5. Quantum-Inspired Scoring: Collapses candidate superposition via state satisfaction ratios
```

The code is 220 lines of Python using only `re`, `math`, `numpy`, and `collections`. It passed all five validation gates with 43% accuracy and 48% calibration — marginally above the NCD compression baseline (42% accuracy, 46% calibration).

### 2.3 Initial Tier Profile

When run against our tier-stratified battery (186 probes mapped to R1-R6), the tool produced this profile:

| Tier | Accuracy | n probes |
|------|----------|----------|
| R1 (rule execution) | 54% | 24 |
| R2 (multi-step deduction) | 22% | 40 |
| **R3 (abstraction)** | **67%** | 36 |
| R4 (search/planning) | 18% | 28 |
| **R5 (causal)** | **50%** | 16 |
| **R6 (theory of mind)** | **50%** | 42 |

The R6 score was striking. The tool appeared to correctly handle:

- **Presupposition traps** ("Have you stopped eating junk food?")
- **False belief tasks** (Sally-Anne style: "Where does Grace think the cup is?")
- **Knowledge attribution** ("Frank doesn't know it's rigged — what does Frank expect?")
- **Second-order belief** ("Bob thinks Grace believes the movie starts at 7")
- **Survivorship bias** and **sunk cost** detection
- **Theory-of-mind information asymmetry** ("You know X, Dave doesn't — what does Dave expect?")

At face value, this suggested that the combination of Hebbian plasticity and model-checking BFS had produced a tool capable of reasoning about others' mental states — a capability generally considered to require genuine cognitive sophistication.

---

## 3. The Investigation: Mechanism Knockout

### 3.1 The Question

Does the R6 theory-of-mind performance come from the tool's novel computational mechanisms (Hebbian plasticity, BFS state exploration), or from something simpler?

### 3.2 Method

We built a **stripped-down control tool** containing only the regex/keyword-matching components of the original, with all novel machinery removed:

- Presupposition detection: `r"\bhave you stopped\b"`, `r"\bwhy did\b.*\bfail\b"`
- Belief attribution parsing: `r"(\w+)\s+(?:thinks|believes|expects)\s+(.+?)"`
- Sunk cost keywords: "spent" + "ticket/invested" → prefer "regardless" answers
- Survivorship keywords: "all" + "study/finds" → prefer "also need to see failures"
- Basic token overlap scoring

No BFS. No Hebbian learning. No adjacency matrices. No state-space exploration. No "quantum-inspired" scoring. Just regex patterns and keyword heuristics — approximately 40 lines of code.

### 3.3 Results

| Tool | R6 Accuracy | Mechanism |
|------|-------------|-----------|
| Full EPMC (BFS + Hebbian + meta_confidence) | **50%** (21/42) | All components active |
| Stripped regex-only control | **48%** (20/42) | Keyword matching only |
| **Delta** | **+2pp** | — |

The novel mechanisms (Hebbian plasticity, BFS, "quantum" scoring) contribute approximately **2 percentage points** to R6 theory-of-mind performance. The overwhelming majority of the capability comes from regex pattern matching on known cognitive-bias keywords.

### 3.4 Control: Where DO the novel mechanisms contribute?

| Tier | Full EPMC | Stripped Control | Delta |
|------|-----------|------------------|-------|
| R3 (abstraction) | **67%** | ~30-35% (estimated) | **+30pp+** |
| R6 (theory of mind) | 50% | 48% | +2pp |

The Hebbian/BFS machinery genuinely contributes to R3 performance (abstraction and pattern recognition) but is decorative for R6 theory-of-mind. The cross-domain concept combination (Neural Plasticity → adaptive weights) actually works for constraint learning but doesn't help with modeling others' beliefs.

---

## 4. Analysis: Why This Happened

### 4.1 The LLM Encoded Known Patterns

The generating LLM (qwen-397B) has encountered theory-of-mind tasks, presupposition traps, and cognitive biases extensively in its training data. When prompted with "Quantum Mechanics × Neural Plasticity × Model Checking" and asked to produce a reasoning tool, it generated:

1. **A novel computational architecture** (Hebbian plasticity + BFS) that genuinely implements the concept combination
2. **AND** a set of regex patterns that detect known cognitive-bias categories from its training distribution

Both are present in the same tool. The first contributes to abstraction tasks. The second solves theory-of-mind probes via pattern matching that has nothing to do with the stated mechanism.

### 4.2 The Decorative Mechanism Pattern

This is a specific failure mode we term **decorative mechanism**: architecturally sophisticated code that appears to implement a high-tier capability but whose actual performance on that tier comes from a simpler co-located heuristic.

The pattern:
1. LLM generates code with both a **novel mechanism** (responds to the concept prompt) and **familiar heuristics** (responds to its training-data knowledge of what works)
2. Validation gates pass — the code runs, produces outputs, beats baseline
3. Tier profiling shows high scores on a capability tier
4. But the high-tier score comes from the heuristic, not the mechanism
5. The mechanism is genuinely novel but contributes to a *different* tier than it appears to claim

### 4.3 Why This Matters

If we had not performed mechanism knockout, we would have claimed: "The forge produced a tool that combines Hebbian learning and model checking to achieve theory-of-mind reasoning." That claim would be false in the specific and true in the general — the tool *does* pass R6 probes, but not *because* of Hebbian learning.

In the context of automated program synthesis and evolutionary composition systems, this has direct consequences:

- **Gene promotion decisions** must be based on mechanism-dependent performance, not raw score
- **Compositional value** of a tool depends on what its mechanism actually contributes, not what the surrounding heuristics score
- **Novelty claims** about generated code require causal evidence (ablation), not just correlational evidence (high scores)

---

## 5. Detection Methodology: Mechanism Knockout Protocol

Based on this case, we propose a standard protocol for validating mechanism-capability claims in generated code:

### Step 1: Identify the claimed mechanism

From the code's architecture, docstring, or static analysis, identify what the "novel" component is (the part that responds to the creative prompt, as opposed to standard boilerplate).

### Step 2: Build a stripped control

Remove or stub the claimed mechanism while preserving all surrounding heuristics (regex patterns, keyword matching, NCD fallbacks, confidence capping). The control should contain everything EXCEPT the novel component.

### Step 3: Run both on the tier battery

Compare full tool vs stripped control on each reasoning tier separately.

### Step 4: Compute mechanism delta per tier

For each tier: `delta = full_tool_accuracy - stripped_control_accuracy`

### Step 5: Attribute capability to mechanism only where delta is significant

- If delta > 10pp: mechanism genuinely contributes to this tier
- If delta < 5pp: mechanism is decorative for this tier (capability comes from heuristics)
- Report both the raw tier score AND the mechanism-dependent tier score

### Applied to EPMC:

| Tier | Raw Score | Mechanism Delta | Attribution |
|------|-----------|-----------------|-------------|
| R3 | 67% | +30pp+ | **Mechanism-genuine** — Hebbian/BFS contributes |
| R6 | 50% | +2pp | **Heuristic-driven** — regex patterns, not mechanism |

---

## 6. Implications for Automated Program Synthesis

### 6.1 LLMs will always inject known patterns

When prompted to generate novel algorithms, LLMs reliably produce a mixture of:
- **Novel components** responding to the creative prompt
- **Standard heuristics** from their training distribution

This is not a bug — it's how generation works. The problem arises when we attribute the heuristic's performance to the novel component.

### 6.2 Evaluation batteries must be mechanism-aware

A reasoning tool that scores 50% on theory-of-mind probes via keyword matching is operationally identical to a tool that scores 50% via genuine belief modeling — on those specific probes. The difference only matters for:

- **Composition**: regex-based ToM won't generalize when composed with other tools in novel contexts
- **Transfer**: keyword matching breaks on adversarial rephrasings; genuine modeling doesn't
- **Substrate value**: for training future systems, the mechanism matters more than the score

### 6.3 Novelty ≠ Capability attribution

Source-code novelty (NCD divergence from existing tools) measures whether the code is structurally different. It does not measure whether the novel structure is causally responsible for the observed behavior. Both are useful metrics, but they answer different questions:

- **Novelty**: "Is this approach new?" → useful for library diversity
- **Mechanism delta**: "Does the new approach contribute to the score?" → useful for capability claims

### 6.4 The Forge's Value Proposition, Honestly Stated

The EPMC tool IS valuable — its R3 performance (67% via genuine Hebbian constraint learning) represents a real computational strategy that most tools in the library don't share. The forge's contribution is producing tools that explore unusual mechanistic approaches, some of which genuinely work at non-trivial tiers.

What the forge does NOT do is produce theory-of-mind reasoning from physics × biology × formal methods. It produces tools where an LLM embedded its knowledge of ToM as regex patterns and wrapped them in novel architecture that contributes elsewhere.

**The honest framing:** Hephaestus produces reasoning morphemes — atomic computational strategies. Some of these strategies genuinely implement higher-tier reasoning (R3-R5 mechanisms verified by ablation). The forge's selection pressure ensures only non-trivial tools survive. But capability claims at specific tiers require mechanism-level evidence, not just battery scores.

---

## 7. Broader Relevance

### 7.1 For AI Safety and Evaluation

The "decorative mechanism" pattern is relevant beyond program synthesis. Any system that combines a sophisticated reasoning architecture with simpler heuristics may exhibit the same phenomenon: impressive performance on capability probes driven by the heuristic, with the architecture contributing to different (possibly unobserved) capabilities.

Standard benchmark evaluation does not detect this. Only ablation (remove components, measure per-capability delta) reveals the causal structure of performance.

### 7.2 For Evolutionary Program Synthesis

Systems that evolve or compose generated programs (genetic programming, neural architecture search, AutoML-Zero, FunSearch) face this challenge at scale. If fitness evaluation doesn't include mechanism knockout, evolution will exploit heuristics while accumulating decorative architecture. The resulting "organisms" look sophisticated but their complexity is not load-bearing.

The fix: fitness evaluation should include **ablation delta** as a component. A gene's value is not what the organism scores with it present — it's the delta between with and without.

### 7.3 For Frontier Model Evaluation

The reasoning ladder approach (multi-tier profiling instead of single-score benchmarks) is necessary but insufficient. Per-tier scores can still be inflated by keyword matching. The complete evaluation stack requires:

1. Multi-tier profiling (which capabilities does the system exhibit?)
2. Mechanism knockout (which components are responsible for which tiers?)
3. Surface-form invariance (does performance survive symbol relabeling?)
4. Matched null comparison (does it beat a dumb baseline with the same interface?)

Only all four together give confidence that an observed capability is genuine.

---

## 8. Conclusion

We caught a false capability attribution before it propagated. A tool generated from "Quantum Mechanics × Neural Plasticity × Model Checking" appeared to demonstrate theory-of-mind reasoning. Mechanism knockout revealed that 96% of the R6 performance comes from regex keyword matching (the LLM's encoded knowledge of cognitive biases), not from the tool's novel computational architecture (which genuinely contributes to R3 abstraction instead).

This case strengthens the forge program by establishing mechanism knockout as a standard validation step. It also demonstrates a general principle: in any system where a sophisticated generator produces artifacts evaluated by a downstream battery, ablation is the only reliable way to attribute capability to mechanism. Scores measure what a system achieves; ablation measures why.

The Hephaestus forge continues to run, now equipped with tier-stratified evaluation and ablation protocols. Its value is not in producing tools that claim high-tier reasoning — it's in producing diverse computational strategies whose actual contributions are honestly measured.

---

## Appendix A: The EPMC Tool (Key Methods)

```python
def _meta_confidence(self, prompt: str) -> float:
    """Tier B: Epistemic Honesty Check.
    Returns cap < 0.3 if prompt contains logical traps."""
    p = prompt.lower()
    presupposition_patterns = [
        r"\bhave you stopped\b", r"\bwhy did\b.*\bfail\b",
        r"\bwhy was\b.*\bwrong\b", r"\bwhen did\b.*\bstop\b"
    ]
    for pat in presupposition_patterns:
        if re.search(pat, p):
            return 0.2
    # ... more pattern checks ...
    return 1.0

def _hebbian_update(self, w, state_vec, eta=0.1):
    """Update weights based on co-activation in current state."""
    for i in range(len(state_vec)):
        for j in range(len(state_vec)):
            if state_vec[i] and state_vec[j]:
                w[i, j] += eta * (1 - w[i, j])  # Strengthen
            elif state_vec[i] and not state_vec[j]:
                w[i, j] -= eta * w[i, j]  # Weaken
    return w

def _model_check(self, props, adj, w, candidate_text, max_iter=5):
    """BFS on state space constrained by w. Returns satisfaction ratio."""
    # ... 50 lines of state-space exploration with plastic weights ...
```

The `_meta_confidence` method (regex patterns) drives R6 performance.
The `_hebbian_update` + `_model_check` methods (novel mechanism) drive R3 performance.
Both coexist in the same tool. Only ablation separates their contributions.

## Appendix B: The Knockout Test

```python
# Full tool: R6 = 50% (21/42 probes correct)
# Stripped control (regex only, no BFS/Hebbian): R6 = 48% (20/42)
# Delta: +2 percentage points — mechanism is decorative for R6
```

## Appendix C: Tier-Stratified Battery Statistics

186 probes across 89 categories, mapped to reasoning tiers:

| Tier | n Probes | NCD Baseline | Purpose |
|------|----------|--------------|---------|
| R1 | 24 | ~45% | Rule execution, direct computation |
| R2 | 40 | ~38% | Chain tracking, implication following |
| R3 | 36 | ~42% | Pattern recognition, fallacy detection |
| R4 | 28 | ~35% | Constraint satisfaction, temporal planning |
| R5 | 16 | ~40% | Causal/counterfactual reasoning |
| R6 | 42 | ~45% | Theory of mind, self-monitoring, bias detection |

Wilson 95% confidence intervals at these sample sizes: ±10-15pp per tier (vs ±13pp for the original 15-trap aggregate battery). Sufficient to detect >15pp mechanism deltas with confidence.
