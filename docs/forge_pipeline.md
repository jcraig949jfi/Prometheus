# The Forge Pipeline: Nous → Coeus → Hephaestus

*Automated discovery and construction of computable reasoning tools*

---

## What This Is

The forge pipeline is a three-agent system that **automatically discovers, implements, and validates pure-algorithmic reasoning tools**. These tools are Python classes that score and rank candidate answers to reasoning questions using only numpy and the standard library — no neural models, no training, no API calls.

The purpose: build a library of computable reasoning criteria that can replace human preference in training loops (RLVF — Reinforcement Learning from Verification Feedback). Instead of "what would a human rate highly," these tools answer "does this response satisfy falsifiability? Does it reduce uncertainty? Is it structurally consistent with the prompt?"

### Current Numbers

| Metric | Value |
|--------|-------|
| Concept dictionary | 89 concepts across 18 fields |
| Combinations evaluated | 1,561+ (Nous, 5+ runs, continuous) |
| Forge attempts | 175+ (continuous, Coeus-priority ordered) |
| Tools forged | 33+ (rising) |
| Tools scrapped | 115+ |
| Trap battery | 15 static + dynamic generator (8 categories, infinite variants) |
| Quality baseline | NCD (compression distance) — 20% accuracy, 7% calibration |
| Best tool | IBAI v2 — 67% accuracy, 53% calibration |
| Execution evaluator | 47% accuracy (solves computation traps structural tools miss) |
| Nous prompt | Implementation-focused (steers toward algorithms, not theory) |
| Coeus methods | L1 regression + NOTEARS + LiNGAM + FCI + DAGMA + interventional |
| Coeus enrichment | Prescriptive directives (not statistics) |
| Nous sampling | Coeus-weighted (oversamples forge drivers) |

---

## The Three Agents

### Nous — The Concept Miner

Nous samples cross-domain concept triples from a curated dictionary of 89 ideas spanning mathematics, physics, cognitive science, philosophy, neuroscience, biology, economics, and 11 other fields. Each triple combines ideas that don't normally meet — "Ergodic Theory × Falsificationism × Maximum Entropy" or "Tensor Decomposition × Criticality × Free Energy Principle."

**How it works:**

1. **Sample** a triple from the dictionary with cross-field bias (80% of triples span 2+ fields, forcing conceptual collisions)
2. **Query** a large model (Qwen 3.5-397B via NVIDIA NemoClaw) with a structured prompt: "How would combining these three concepts create a mechanism for a system to test its own reasoning?"
3. **Score** the response on four dimensions (1-10 each):
   - **Reasoning** — does the synthesis produce a coherent mechanism?
   - **Metacognition** — can it monitor its own performance?
   - **Hypothesis generation** — does it produce testable predictions?
   - **Implementability** — can an engineer turn this into working code?
4. **Rank** by composite score. Flag "high potential" entries (all three core ratings ≥ 7)

The prompt enforces a structured rating format at the end of each response to ensure reliable parsing. Max tokens: 2048 (up from 800 after early truncation issues caused score parsing failures).

Nous runs continuously, generating new combinations until stopped. Output is streamed to `responses.jsonl` with crash-safe append-per-entry.

**Output:** `responses.jsonl` with scored triples, `rankings.md` for human review.

### Coeus — The Causal Intelligence Layer

Coeus sits between Nous and Hephaestus. It learns which concepts, fields, and score dimensions causally predict forge success, then injects that knowledge back into the pipeline. Named for the Titan of rational inquiry.

**How it works:**

1. **Encode** the full history — every Nous entry paired with its Hephaestus outcome (forged or scrapped) — into a numeric matrix
2. **Analyze causally** using up to six methods (graceful degradation):
   - L1-regularized logistic/linear regression (always available)
   - NOTEARS/GES structure learning (if `causal-learn` installed)
   - LiNGAM causal ordering (if `lingam` installed)
   - FCI latent confounder detection (if `causal-learn` installed) — identifies when a concept's correlation with forge success is driven by an unobserved variable
   - DAGMA non-linear DAG learning (if `dagma` installed, requires 200+ forge attempts) — captures synergies that linear models miss
   - Interventional estimation — computes counterfactual probabilities: "if we remove concept X, forge probability drops by Y%"
3. **Output** per-concept influence scores, pair synergies, field effects, confounder flags, and interventional estimates
4. **Enrich** each incoming triple with a causal context paragraph using interventional language, injected into Hephaestus's code generation prompt

**What Coeus has learned so far:**

| Concept | Forge Effect | Forge Rate | Interventional |
|---------|-------------|------------|----------------|
| Criticality | +1.155 | 50% | — |
| Sparse Autoencoders | +0.919 | 50% | — |
| Active Inference | +0.789 | 50% | — |
| Falsificationism | +0.655 | 40% | — |
| Ergodic Theory | +0.520 | 21% | — |
| Free Energy Principle | +0.480 | 30% | — |
| Topology | -0.462 | 0% | — |
| Epigenetics | -0.299 | 0% | — |
| Symbiosis | -0.254 | 0% | — |

Key findings:
- **Implementability** is the only Nous score dimension that predicts forge success (weight +0.221). Reasoning, metacognition, and hypothesis scores are irrelevant to whether code gets forged.
- **Cognitive Science** and **Theoretical Neuroscience** fields drive forges. **Mathematics** alone is slightly negative — abstract math produces beautiful theory but unimplementable code.
- **Top synergy pair**: Ergodic Theory + Theory of Mind (+0.446)

Coeus is a **batch analysis tool**, not a continuous process. Hephaestus auto-triggers it every 50 forges (configurable via `--coeus-interval`).

**Prescriptive enrichment:** Coeus doesn't just report statistics — it translates causal matrices into concrete code-generation directives. The 397B model doesn't need to know the math behind the causal graph; it needs to know *how to treat each concept* to maximize trap battery survival. The enrichment system generates two outputs:

- **Directives** (for the 397B code gen prompt) — prescriptive instructions like "make this the core pattern" or "restrict to confidence() wrapper only"
- **Summaries** (for human-readable reports) — statistical descriptions with interventional estimates

**Enrichment example (prescriptive directives injected into Hephaestus prompt):**

```
- **Active Inference**: Strong primary driver of forge success. Make this concept
  the core architectural pattern of the evaluate() method. Historical forge rate: 50%.
  This concept has a proven, unconfounded mechanical advantage.

- **Topology**: Historical inhibitor. Tools relying heavily on this tend to fail
  reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence()
  wrapper or structural parsing support only.

- **Ergodic Theory**: Moderate positive synergy. Use this concept to support the
  primary logic, perhaps as a secondary validation step or scoring modifier.
  WARNING: Past correlation with success is confounded by an unobserved variable.
  Ensure the implementation is strictly deterministic and does not rely on implicit
  linguistic priors that may not generalize.

- Active Inference + Free Energy Principle: strong positive synergy (+0.350).
  These concepts reinforce each other — integrate them tightly rather than
  implementing as independent checks.

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural
parsing as the primary scoring signal. NCD is only a tiebreaker.
```

The directive thresholds are:
- Forge effect > 0.5 or interventional drop > 30% → "strong primary driver, make it the core pattern"
- Forge effect 0.1–0.5 → "moderate synergy, use as secondary validation"
- Forge effect < -0.1 → "historical inhibitor, restrict to confidence() or parsing support"
- FCI status "confounded" → deterministic implementation warning
- FCI status "direct_cause" → "proven unconfounded mechanical advantage"
- Pair synergy > 0.1 → "integrate tightly"
- Pair synergy < -0.05 → "keep in separate code paths"

### Hephaestus — The Forge

Hephaestus takes high-scoring Nous triples (enriched by Coeus) and attempts to forge them into working reasoning tools. It runs **continuously by default**, polling Nous for new results every 5 minutes and processing them in Coeus-priority order.

**The forge loop:**

```
Nous triple → Ledger dedup → Coeus priority sort → Code generation (397B model)
  → Code extraction (code-first, decline signals checked only if no code found)
  → Gate 1: Syntax (ast.parse)
  → Gate 2: Imports (numpy + stdlib only)
  → Gate 3: Interface (class ReasoningTool with evaluate + confidence)
  → Gate 4: Runtime (instantiate, call with test inputs, verify output format)
  → Gate 5: Trap battery (15 traps, must strictly beat NCD baseline)
  → forge/ or scrap/
  → Every 50 forges: auto-trigger Coeus rebuild + human-readable reports
```

**Gate details:**

**Code extraction** — The 397B model's response is scanned for Python code blocks. Code extraction runs FIRST. Decline signals ("not implementable", "no meaningful implementation") are only checked in prose *outside* code blocks, and only if no code was found. This prevents false positives from the Nous analysis text containing words like "unproductive" in context.

**Validation gates (1-4)** — Sequential checks that the code is syntactically valid, imports only allowed modules, defines the required `ReasoningTool` class with `evaluate()` and `confidence()` methods, and runs without crashing on a simple test case. Each gate can independently kill a candidate.

**Trap battery (gate 5)** — 15 reasoning traps in two tiers:

*Original 10:* Cognitive bias puzzles (bat-and-ball, gambler's fallacy, pound-of-gold), mathematical logic (0.999... = 1, pigeonhole principle), numeric comparison (9.11 vs 9.9).

*Compositional 5:* Transitivity (Alice > Bob > Carol), negation scope ("not the case that all birds can fly"), comparative reversal with stated premise, subject-object parsing ("the dog chased the cat"), modus tollens ("if rain then wet ground; ground is not wet").

A tool must **strictly beat the NCD baseline** on accuracy or calibration without losing on either metric. The NCD baseline scores 20% accuracy, 7% calibration.

**The code generation prompt includes:**
- The Nous theoretical analysis (what the combination means)
- Coeus enrichment (which concepts are causally strong, interventional estimates, confounder warnings)
- NCD quality floor (tells the model its scores must beat 20%/7%)
- Seed tool guidance (what patterns work vs don't: structural parsing > hash similarity, numeric eval catches comparison traps, NCD only as tiebreaker)

**The interface contract:**

```python
class ReasoningTool:
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Returns [{"candidate": str, "score": float, "reasoning": str}, ...]
        sorted descending by score."""

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns float in [0.0, 1.0]."""
```

Every forged tool is deterministic, fast, and interpretable. The `reasoning` field in evaluate output explains *why* the tool scored each candidate as it did.

**Continuous operation:**

Hephaestus runs continuously by default. After exhausting current candidates, it sleeps for 5 minutes then re-scans all Nous runs for new entries. The global ledger prevents reprocessing. Use `--runonce` for single-batch mode.

| Flag | Default | Effect |
|------|---------|--------|
| `--runonce` | off | Process current batch and exit |
| `--poll-interval` | 300s | Sleep between Nous re-scans |
| `--coeus-interval` | 50 | Auto-rebuild Coeus every N forges |
| `--reports-interval` | 50 | Auto-rebuild human-readable reports every N forges |
| `--all` | auto in continuous | Process all non-unproductive entries |
| `--top-n` | 20 in runonce | Take top N by Coeus priority |
| `--delay` | 3s | Rate limit between API calls |

---

## The Forged Tool Library

Surviving tools fall into distinct architectural families:

### NCD-based (compression distance)
Use `zlib.compress` to measure structural similarity between prompt and candidates. The NCD baseline is the quality floor — every other tool must beat it. NCD alone scores 20% accuracy — it can't distinguish short candidates like "Yes" vs "No."

### Structural Falsification Engines (best performers)
Parse the prompt for logical structure (negations, comparatives, conditionals, subject-object roles, quantifiers), then check whether each candidate contradicts or satisfies the extracted constraints. Includes numeric evaluation (`float("9.11") < float("9.9")`), transitive closure, and modus tollens detection. Elimination over selection — penalize contradictions rather than reward similarity. EFME v2: 60% accuracy, 53% calibration.

### Active Inference / Free Energy
Model candidates as hypotheses that minimize expected free energy. Balance exploitation (constraint satisfaction) with exploration (informativeness beyond the generic). Use local co-occurrence SVD for distributional semantics. Structural analysis dominates when signal is present; NCD is a fallback tiebreaker. IBAI v2: 67% accuracy, 53% calibration (current best).

### Feature-discovery bandits
UCB (Upper Confidence Bound) algorithms that learn which textual features are informative within a batch of candidates. Features include word n-grams, character trigrams, structural indicators (negation, comparative direction, conditional presence), and SVO roles. The bandit adapts its scoring across calls, making it resistant to gaming. Bandit v2: 40% accuracy, 47% calibration.

### Logical Consistency Checker
Symbolic reasoning via constraint propagation. Extracts structured facts from text (comparatives, negations, conditionals, quantifiers, verb-agent-patient), builds a constraint graph, checks transitivity/modus ponens/quantifier consistency. Scores based on constraints satisfied (+1) minus contradictions (-2, asymmetric). Hand-crafted reference implementation.

### Utility Wrappers (in `forge/utils/`)

**Criticality Regularizer** — Meta-criterion that measures whether a tool's scoring landscape has useful gradient. Flat landscapes (all candidates score the same) and degenerate landscapes (one candidate trivially dominates) are both penalized.

**Perturbation Calibrator** — Confidence wrapper that runs prompt perturbations (drop words, add "explain why," remove negation) and measures scoring stability. Candidates that score consistently across perturbations are more robust.

These are NOT standalone `ReasoningTool` classes — they wrap a base tool and enhance it.

---

## Techniques

### NCD (Normalized Compression Distance)
`NCD(x,y) = (C(xy) - min(C(x),C(y))) / max(C(x),C(y))` where C is `zlib.compress`. Approximates Kolmogorov complexity and provides a continuous fitness landscape. Every forged tool must beat NCD to survive. Includes information density penalty (compressed/raw ratio) and anti-echo penalty (reject candidates that bloat beyond 2x prompt length).

### Structural parsing
Regex-based extraction of logical structure from natural language prompts:
- Negations: "not," "never," "cannot" + scope
- Comparatives: "X is larger/taller/heavier than Y" → ordering relation
- Conditionals: "if P then Q" → implication
- Subject-object: "The dog chased the cat" → agent/patient roles
- Quantifiers: "all X are Y" → universal claims
- Numeric evaluation: parse and compare actual float values (`float("9.11") < float("9.9")`)
- "All but N" pattern: parse as N remaining

This is what separates v2 tools from v1. Hash-based tools measure string noise; structural parsers measure reasoning structure.

### Transitive closure
Given ordering relations (A > B, B > C), compute the full ordering (A > B > C > ...) and check candidate answers against it. Critical for multi-premise reasoning traps.

### Local distributional semantics
Build co-occurrence matrices from the prompt + candidates themselves, apply PPMI transform and truncated SVD, produce word vectors that carry meaning derived from usage patterns. Deterministic, numpy-only, zero external data.

### Causal discovery (Coeus)
Multiple methods applied to concept × outcome data:
- **L1 regression**: Always available. Identifies linear forge drivers.
- **NOTEARS/GES**: Structure learning on score dimensions.
- **LiNGAM**: Causal ordering among continuous variables.
- **FCI**: Detects latent confounders — flags concepts whose correlation with forge success might be spurious.
- **DAGMA**: Non-linear DAG learning via MLP. Captures synergies invisible to linear models. Requires 200+ forge attempts.
- **Interventional estimation**: Computes P(forge | do(remove concept)) — counterfactual drop probabilities.

### Cross-domain concept collision
The core intellectual engine. By forcing concepts from different fields into the same prompt (Ergodic Theory from dynamical systems + Falsificationism from philosophy + Maximum Entropy from information theory), the pipeline generates architectures that wouldn't emerge from any single discipline. The 89 concepts span 18 fields — mathematics, biology, philosophy, economics, neuroscience, physics, linguistics, and more.

---

## How to Run the Full Pipeline

### Quick start (continuous, fully automated)
```bash
# Terminal 1: Nous (generates combinations continuously)
python agents/nous/src/nous.py --unlimited

# Terminal 2: Hephaestus (forges continuously, auto-triggers Coeus + reports)
python agents/hephaestus/src/hephaestus.py

# Terminal 3: Nemesis (adversarial pressure, when available)
python agents/nemesis/src/nemesis.py
```

Nous mines concepts, Hephaestus forges tools, Nemesis tries to break them. Coeus learns from all three and steers the pipeline. Hephaestus auto-triggers Coeus + reports every 50 forges.

### Individual components
```bash
# Nous — single batch
python agents/nous/src/nous.py --n-combos 50

# Coeus — manual rebuild
python agents/coeus/src/coeus.py

# Hephaestus — single batch
python agents/hephaestus/src/hephaestus.py --runonce --top-n 20

# Reports — manual rebuild
python agents/hephaestus/src/build_reports.py --force

# Cleanup — one-time re-score + ledger rebuild
python agents/hephaestus/src/cleanup_once.py
```

### Evaluate forged tools
```bash
# From agents/hephaestus/src/
python -c "
from test_harness import load_tool_from_file, run_trap_battery
from pathlib import Path
for py in sorted(Path('../forge').glob('*.py')):
    try:
        tool = load_tool_from_file(py)
        r = run_trap_battery(tool)
        print(f'{py.stem:50s} acc={r[\"accuracy\"]:.0%} cal={r[\"calibration\"]:.0%} {\"PASS\" if r[\"passed\"] else \"FAIL\"}')
    except Exception as e:
        print(f'{py.stem:50s} ERROR: {e}')
"
```

---

## Data Flow

```
agents/nous/
  src/nous.py                    — continuous concept miner
  src/concepts.py                — 89-concept dictionary
  src/scorer.py                  — rating extraction (4 dimensions + novelty)
  runs/*/responses.jsonl         — scored triples (append-per-entry)

agents/coeus/
  src/coeus.py                   — batch causal analysis
  src/causal_graph.py            — regression + NOTEARS + LiNGAM + FCI + DAGMA
  src/enrichment.py              — per-triplet context with interventional language
  graphs/causal_graph.json       — full causal model
  graphs/concept_scores.json     — concept influence + pair synergy (used by Hephaestus priority sort)
  enrichments/*.json             — one enrichment per combo key

agents/hephaestus/
  src/hephaestus.py              — continuous forge engine
  src/code_extractor.py          — code-first extraction, decline signals secondary
  src/validator.py               — syntax, imports, interface, runtime checks
  src/test_harness.py            — 15-trap battery + NCD baseline comparison
  src/prompts.py                 — code gen prompt with Coeus + NCD floor + seed guidance
  src/build_reports.py           — human-readable markdown per combo
  src/cleanup_once.py            — one-time re-score + ledger rebuild
  forge/*.py                     — surviving tools
  forge/*.json                   — tool metadata (scores, margins, timestamps)
  forge/utils/                   — utility wrappers (perturbation calibrator, criticality regularizer)
  scrap/*.py + *.json            — failed forges with failure reasons
  humanreadable/*.md             — consolidated reports per combo
  ledger.jsonl                   — global dedup + outcomes + margin-over-NCD

agents/nemesis/                    — PLANNED (Phase 2)
  src/nemesis.py                 — adversarial co-evolution engine
  src/mutators.py                — prompt mutation operators (6 categories)
  src/generators.py              — parametric adversarial task generators
  src/evaluator.py               — run tools against adversarial tasks
  src/reporter.py                — failure analysis + blind spot detection
  adversarial/*.jsonl            — generated adversarial task sets
  reports/                       — failure analysis reports
```

---

## The Goodhart Question

> **"Are our evaluators measuring reasoning, or have they learned to pass tests?"**

This is the question **Nemesis** (planned) will answer. Without adversarial pressure,
tools can overfit to the trap battery distribution. Nemesis generates adversarial
mutations of existing traps, maintains a living adversarial set (100 validated tasks),
and feeds failure data back through Coeus. Tools must survive both the static battery
AND the adversarial set. See [forge_roadmap.md](forge_roadmap.md) and
[nemesis_design.md](nemesis_design.md) for the full design.

---

## Architectural Invariants

### Data Provenance Tagging (HARD GATE)

Every data point in the system carries a provenance tag:
- `training` — verified reasoning chains for model fine-tuning (Rhea)
- `evaluation` — trap battery results, tool scores (Hephaestus)
- `adversarial` — Nemesis-generated failure cases (test suites only)

A hard gate in the data pipeline **physically prevents cross-contamination**.
Adversarial data never enters a training path. This is not a convention — it's
enforced in code.

**Why this matters:** Rhea Batch 3 proved that mixing adversarial correction
chains into training data cost 25 points on metacognition. The lesson scales:
in a system this complex, someone will eventually try to use Nemesis failure
cases as training signal. The provenance gate makes that impossible without
explicitly removing the guard.

---

## Where This Goes

The forged tools are destined to become **fitness function terms in Rhea's RLVF loop**. The vision:

1. Rhea evolves a small model (CMA-ES over LoRA weights targeting identified ejection heads)
2. The evolved model generates reasoning chains
3. Forged tools score those chains (structural consistency, uncertainty reduction, falsifiability)
4. Nemesis generates adversarial tasks to pressure-test both the tools and the model
5. Scores become evolutionary fitness — chains that satisfy more tools are fitter
6. Next generation of LoRA weights is selected toward chains that survive computable reasoning criteria
7. Nemesis's failure data feeds back through Coeus to improve tool generation

Three co-evolving populations:
- **Generators** (Rhea's models) — evolve to produce reasoning that survives evaluation
- **Evaluators** (Hephaestus's tools) — evolve to catch failures the generators exploit
- **Adversaries** (Nemesis's tasks) — evolve to expose weaknesses in both

No human preference. No RLHF. Just mathematical verification (Lean 4 for formal proofs), algorithmic reasoning checks (forged tools), and adversarial pressure (Nemesis). The pipeline mines the concept space for new reasoning criteria, forges them into computable tools, pressure-tests them against adversarial mutations, and feeds the survivors into the evolutionary loop.

**The RLVF fitness function** for a reasoning trace T:

```
F(T) = Σ wᵢ · Sᵢ(T) - λ · σ(S)
```

Where:
- `Sᵢ(T)` = score from the i-th forged tool
- `wᵢ` = Coeus-derived weight (how robust/unconfounded that tool is)
- `λ · σ(S)` = **Nemesis variance penalty** — when tools disagree on a trace, penalize it

The variance penalty is the Goodhart defense: if a trace scores high on one tool but low on others, it's likely gaming a specific evaluator. The penalty prevents the model from optimizing for any single tool's blind spots.

**Convergence point:** Rhea's evolved models, trained on self-corpus, evaluated by Hephaestus's forged tools, pressured by Nemesis's adversarial tasks, guided by Coeus's causal intelligence. No human in the loop for evaluation.

**The Goodhart defense:** Two layers. Nemesis ensures tools measure reasoning, not trap familiarity. The variance penalty ensures models can't game individual tools. Together they create a system where the only way to score high is to actually reason.

This is the long game: an automated discovery engine for reasoning evaluation, producing an ever-growing library of verifiable criteria that push models toward genuine reasoning rather than pattern-matching. The definition of "good reasoning" itself evolves alongside the models being evaluated.
