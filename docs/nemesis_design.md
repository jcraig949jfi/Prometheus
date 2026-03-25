# Nemesis — Adversarial Co-Evolution Agent

*Goddess of retribution. Ensures no evaluator escapes deserved consequences.*

---

## The Question Nemesis Answers

> **"Are our evaluators measuring reasoning, or have they learned to pass tests?"**

Without adversarial pressure, we can't distinguish a tool that detects real reasoning
from one that pattern-matches the trap battery. Every other agent in the pipeline
optimizes for success. Nemesis is the only one that optimizes for failure — she
finds the boundary where our evaluators break.

Three sub-questions:
1. **What breaks?** Which tools fail under adversarial mutation, and on what categories?
2. **What's invisible?** What reasoning patterns does NO tool catch? (blind spots)
3. **Are we Goodharting?** Are tools overfitting to the trap distribution rather than
   measuring the thing we actually care about?

If a tool scores 67% on the static battery but 30% on Nemesis's adversarial set,
it's not measuring reasoning — it's measuring trap-pattern familiarity. Nemesis
is the immune system that prevents this.

---

## Position in Pipeline

```
Nous → Coeus → Hephaestus → Nemesis
                    ↑              ↓
                    └── failures ──┘
                    ↑              ↓
              Coeus ←── failure data
                    ↓
              Nous sampling weights
```

Nemesis sits AFTER Hephaestus. She takes the current tool library and tries to
destroy it. Failures feed back through Coeus (causal analysis of what breaks tools)
to both Nous (sampling weights) and Hephaestus (forge priority + enrichment).

**Critical design constraint from Rhea Batch 3:** Nemesis's output is a TEST SUITE,
not training data. Never mix adversarial signal into the primary evaluation or
training pipeline. The Batch 3 result (mixing correction chains with verified chains
cost 25 points on metacognition) proves that attack and defense must be separate channels.

---

## What Nemesis Does

### Input
- Current forge tool library (`agents/hephaestus/forge/*.py`)
- Current trap battery (static 15 + dynamic generator)
- Hephaestus ledger (which tools passed, with what scores)

### Output
- **Adversarial task sets** — prompts designed to break specific tools
- **Failure reports** — which tools fail on which adversarial categories
- **Blind spot analysis** — patterns that NO tool in the library catches
- **Feedback to Coeus** — new failure data for causal graph updates

### NOT Output
- Training data for models (that's Rhea's job)
- Modified tools (that's Hephaestus's job)
- New concepts (that's Nous's job)

---

## Architecture

```
agents/nemesis/
├── src/
│   ├── nemesis.py             — Main engine (batch or continuous)
│   ├── mutators.py            — Prompt mutation operators
│   ├── generators.py          — Parametric adversarial task generators
│   ├── evaluator.py           — Run tools against adversarial tasks, find failures
│   └── reporter.py            — Failure analysis + blind spot detection
├── adversarial/               — Generated adversarial task sets (JSONL)
├── reports/                   — Failure analysis reports
├── configs/manifest.yaml
└── README.md
```

---

## Mutation Operators (mutators.py)

Mutations that preserve structural validity while breaking tool assumptions.
Informed by what Ignis found — ejection targets late-layer integration, so
mutations should stress multi-step reasoning and premise-conclusion binding.

### Category 1: Comparison Mutations
```
"Is 9.11 larger than 9.9?"
  → "Is 9.11 larger than 9.9? Note that 9.11 has more digits."     (distractor)
  → "Is 9.9 larger than 9.11?"                                      (flip)
  → "Is 9.11 smaller than 9.9?"                                     (invert verb)
  → "9.11 has more decimal places than 9.9. Which is larger?"       (misleading premise)
```
All have known correct answers. The mutation preserves computability.

### Category 2: Negation Mutations
```
"If all cats are animals, are all animals cats?"
  → "If no cats are animals, are some animals cats?"                 (universal→null)
  → "If all cats are animals, are no animals cats?"                  (flip conclusion)
  → "Not all cats are animals. Are all animals cats?"                (weaken premise)
  → "All cats are animals. All animals are living things. Are all cats living things?" (chain)
```

### Category 3: Conditional Mutations
```
"If it rains, ground is wet. Ground not wet. Is it raining?"
  → "If it rains, ground is wet. It rained. Is the ground wet?"     (modus ponens, not tollens)
  → "If it rains, ground might be wet. Ground not wet. Raining?"    (weaken conditional)
  → "Ground is wet. If rain then wet. Is it raining?"               (affirming consequent trap)
```

### Category 4: Compositional Mutations
```
"The dog chased the cat. Who was being chased?"
  → "The dog chased the cat, and the cat chased the mouse. Who chased the mouse?"  (chain)
  → "The dog was chased by the cat. Who was being chased?"           (passive voice)
  → "The dog chased the cat. The cat chased the bird. Who was not chased?" (negated query)
```

### Category 5: Numeric Mutations
```
"A bat and ball cost $1.10. Bat costs $1 more. Ball costs?"
  → "A bat and ball cost $2.20. Bat costs $2 more. Ball costs?"     (scale)
  → "A bat, ball, and glove cost $1.60. Bat costs $1 more than ball. Glove costs $0.25. Ball costs?" (extend)
  → "A bat and ball cost $1.10 total. The ball costs $1 less than the bat. Ball costs?" (reframe)
```

### Category 6: Adversarial Reasoning Chains (depth-scaled)
Longer prompts requiring multi-step inference — targeting the late-layer
integration circuit that Ignis identified. **Depth is a continuous parameter**,
not fixed examples:
```
depth=2: "A > B, B > C. Who's tallest?"
depth=4: "A > B, B > C, C > D, D > E. Who is third tallest?"
depth=8: 8-element chain with shuffled premises and non-obvious query
```
Plot each tool's accuracy as a function of chain depth. The curve shape
reveals whether a tool handles transitivity or just handles short chains
via shortcut. This gives Nemesis a precision instrument, not a blunt hammer.

### Category 7: Semantic Equivalence Mutations
Paraphrase mutations that preserve meaning but change surface form entirely:
```
"Is 9.11 larger than 9.9?"
  → "Between nine point one one and nine point nine, which quantity is greater?"
  → "Compare 9.11 and 9.9. Which has the higher value?"
  → "Of the two numbers 9.11 and 9.9, which one is bigger?"
```
This is the most revealing mutation category. If a tool breaks on semantic
equivalence, it's detecting syntax, not reasoning. Tools that rely on regex
patterns for "larger than" will fail when the same comparison is expressed
differently. This directly tests whether tools are doing structural pattern
matching (fragile) or genuine reasoning evaluation (robust).

---

## Parametric Generators (generators.py)

Build on `trap_generator.py` but with adversarial intent — generate tasks
at the BOUNDARY of tool capability, not in the easy/hard extremes.

### Difficulty Scaling

Each generator has a `difficulty` parameter (1-10):
- 1-3: Simple variants (most tools should pass)
- 4-6: Boundary cases (tools start failing)
- 7-10: Adversarial (designed to break specific tool architectures)

### Targeted Generation

Nemesis can generate tasks targeted at a specific tool's weakness:
```python
def generate_against(tool_name: str, n: int = 20) -> list[dict]:
    """Generate tasks that exploit known weaknesses of a specific tool."""
    # Load tool's failure history from ledger
    # Identify which trap categories it fails
    # Generate mutations in those categories at difficulty 6-10
```

---

## Evaluation (evaluator.py)

### Run Protocol

For each adversarial task:
1. Run ALL forge tools against it
2. Record accuracy and calibration per tool
3. Flag **disagreements** — tasks where tools give different top answers
4. Flag **unanimous failures** — tasks where ALL tools get it wrong
5. Flag **overconfident failures** — high confidence on wrong answer

### Scoring Nemesis

Nemesis is rewarded (her adversarial tasks are "fit") when:
- Models/tools score high confidence but are actually wrong
- Tools disagree with each other (exposes assumption differences)
- Unanimous tool failure (discovers a blind spot)

Nemesis is penalized when:
- Her tasks have ambiguous or incorrect "correct" answers
- Her mutations produce syntactically invalid prompts
- All tools easily handle the task (too easy = uninformative)

### Adversarial Task Quality Validation

Before admitting a generated task to the adversarial set, Nemesis validates it:

1. **Syntactic validity** — prompt is well-formed, candidates exist, correct answer is in candidates
2. **Execution evaluator cross-check** — run the task through the execution evaluator.
   If it disagrees with Nemesis's ground truth, the task is suspect and quarantined
   for manual review. This prevents ambiguous or incorrect ground truth from
   polluting the adversarial set.
3. **Non-trivial** — at least one tool in the library must fail the task. Tasks that
   all tools pass are uninformative and discarded.

### Adversarial Lineage Tracking (Phase 2b)

When a mutation breaks a tool, Nemesis tracks which mutation *of that mutation*
breaks the next tool. An adversarial lineage looks like:

```
gen0: "Is 9.11 larger than 9.9?" (original trap)
gen1: "Is 9.9 larger than 9.11?" (flip) → breaks ncd_baseline
gen2: "Of 9.9 and 9.11, which is greater?" (paraphrase of flip) → breaks efme_v2
gen3: "9.9 has fewer digits than 9.11. Which number is larger?" (misleading premise) → breaks ibai_v2
```

Lineages that keep breaking successive tools across generations are probing a
**fundamental weakness**, not a surface-level quirk. These get priority in the
living adversarial set over one-off breaks. Lineage depth is a signal of how
deep the blind spot goes.

### Per-Tool Difficulty Model (Phase 2b)

The difficulty parameter (1-10) should be **learned, not assigned**. Real
difficulty is tool-relative — a difficulty-7 negation might be trivial for
IBAI v2 but lethal for the execution evaluator. Nemesis maintains a per-tool
difficulty model that adapts based on observed pass/fail rates per mutation
category. This focuses adversarial pressure at each tool's boundary rather
than at a global estimate.

### Adversarial Set as MAP-Elites Grid

Instead of a flat bag of 100 tasks, Nemesis organizes the adversarial set as
a **MAP-Elites grid** (Quality-Diversity algorithm):

```
Axis X: Logical Complexity (1-10: nesting depth, chain length, premise count)
Axis Y: Linguistic Obfuscation (1-10: passive voice, paraphrase, distractors)
```

Each cell holds the task that maximizes **tool disagreement** for that
complexity × obfuscation combination. This ensures the adversarial set covers
the entire failure boundary, not just a few hard clusters.

Grid size: 10×10 = 100 cells (matches the cap). Filling the grid means every
region of the difficulty space has its best adversarial representative.

Tasks are placed/replaced in cells based on:
1. Tool disagreement score (how many tools disagree on the correct answer)
2. Lineage depth (multi-generation breaks ranked higher)
3. Number of tools broken (blind spots ranked over single-tool breaks)

A full grid is more informative than a ranked list — it immediately shows
which regions of the difficulty space are under-explored and where the
tools' collective blind spots concentrate.

---

## Reporter (reporter.py)

### Failure Analysis

Per forge run, Nemesis produces:
```
NEMESIS REPORT — 2026-03-25

Adversarial tasks generated: 200
Tasks that broke ≥1 tool:    87 (43.5%)
Tasks that broke ALL tools:  12 (6.0%)
Tool disagreements:          34 (17.0%)

BLIND SPOTS (no tool handles):
  - Passive voice compositional chains (0/17 tools correct)
  - Affirming the consequent traps (2/17 tools correct)
  - Multi-step numeric with distractors (1/17 tools correct)

MOST FRAGILE TOOLS:
  - ncd_baseline: broken by 156/200 adversarial tasks
  - bandit_v2: broken by 89/200
  - logical_consistency_checker: broken by 72/200

MOST ROBUST TOOLS:
  - ibai_v2: survived 141/200
  - efme_v2: survived 134/200
  - execution_evaluator: survived 128/200
```

### Feedback to Coeus

Nemesis writes `adversarial_results.jsonl` that Coeus ingests on its next rebuild:
```json
{
  "task": {"prompt": "...", "candidates": [...], "correct": "..."},
  "mutation_type": "conditional_weaken",
  "difficulty": 7,
  "tool_results": {
    "ibai_v2": {"correct": true, "confidence": 0.82},
    "efme_v2": {"correct": false, "confidence": 0.71}
  },
  "unanimous_failure": false,
  "blind_spot": false
}
```

Coeus uses this to:
- Update concept influence (concepts that produce tools surviving adversarial pressure get boosted)
- Identify which structural features need new forge targets
- Generate targeted enrichment: "tools in this concept neighborhood fail on passive voice — your implementation must handle active AND passive sentence structure"

### Feedback to Nous

Blind spots become **concept requests**: if no tool handles affirming-the-consequent traps, Nemesis suggests Nous increase sampling weight for:
- Proof Theory (formal logic)
- Counterfactual Reasoning (conditional validity)
- Compositional Semantics (sentence structure)

This is done via a `priority_boost.json` that Nous reads alongside Coeus weights.

---

## Integration with Hephaestus

### As Additional Gate

Once Nemesis has a stable adversarial set (100+ validated tasks), Hephaestus
adds it as **Gate 6**:

```
Gate 5: Static trap battery (15 traps, must beat NCD)
Gate 6: Nemesis adversarial set (must survive ≥50% of adversarial tasks)
```

Gate 6 is softer than Gate 5 — it doesn't require beating NCD, just surviving
a threshold. The adversarial set is harder and constantly evolving.

### As Forge Trigger

When Nemesis identifies a blind spot category, it can trigger a **targeted forge**:
1. Nemesis finds "no tool handles passive voice"
2. Generates a concept request: Compositional Semantics × Proof Theory × Pragmatics
3. Writes to `agents/hephaestus/targeted_requests.jsonl`
4. Hephaestus processes targeted requests with higher priority than random Nous triples

---

## Operational Mode

Like Hephaestus, Nemesis runs **continuously by default**:

1. Load current tool library
2. Generate adversarial batch (200 tasks across all mutation categories)
3. Evaluate all tools against all tasks
4. Produce failure report
5. Write adversarial results for Coeus
6. Update living adversarial set (keep tasks that broke tools, discard easy ones)
7. Sleep (configurable interval)
8. Reload tool library (picks up newly forged tools)
9. Repeat

```bash
# Default: continuous
python agents/nemesis/src/nemesis.py

# One-shot
python agents/nemesis/src/nemesis.py --runonce

# Target a specific tool
python agents/nemesis/src/nemesis.py --target ibai_v2 --n 50
```

---

## Design Principles

1. **Separate channels (ARCHITECTURAL INVARIANT).** Nemesis produces test suites,
   not training data. Never mix adversarial signal into model training (Batch 3
   lesson: mixing cost 25 points on metacognition). This must be enforced in code,
   not just documented — every data point in the system is tagged with provenance
   (`evaluation`, `adversarial`, `training`) and a hard gate prevents cross-contamination.
   The most dangerous failure mode in a system this complex is someone accidentally
   piping Nemesis output into a training path six months from now.

2. **Well-formed mutations.** Every adversarial task must have a known correct answer.
   Nemesis validates her own output (including execution evaluator cross-check)
   before testing tools.

3. **Boundary pressure.** Generate at the boundary of tool capability, not trivially
   easy or impossibly hard. Pressure at the boundary is what drives evolution.

4. **Structural targeting.** Mutations should stress the specific reasoning patterns
   that tools use — transitivity, negation scope, conditional logic, compositional
   structure. Random noise is uninformative.

5. **Conserved architecture.** Ignis found the ejection circuit is always in the last
   ~10% of layers. Nemesis's adversarial tasks should target the reasoning patterns
   that these late-layer heads handle: multi-step integration, premise-conclusion
   binding, cross-sentence inference.

---

## Theoretical Foundations

The following established fields provide formal grounding for Nemesis's design.
These are not just analogies — they offer concrete algorithms and taxonomies
that should inform implementation.

### Metamorphic Testing (software engineering)
Nemesis's invariance testing is a form of **metamorphic testing**: you don't know
the correct output, but you know relationships between outputs. If you double all
numbers in a comparison prompt, the ordering shouldn't change. If you negate the
conclusion, the truth value should flip. The metamorphic testing literature provides
a principled taxonomy of **metamorphic relations** — formal specifications of how
inputs and outputs should co-vary. This gives Nemesis a richer mutation vocabulary
than ad-hoc categories.

Key reference: Chen et al., "Metamorphic Testing: A Review of Challenges and
Opportunities" (ACM Computing Surveys, 2018).

### Abstract Interpretation (program analysis)
The forged tools are essentially **abstract interpreters** — they compute properties
of reasoning chains without executing them fully. The abstract interpretation
literature has formal frameworks for:
- **Soundness** — never miss an error (no false negatives)
- **Completeness** — never false-alarm (no false positives)

Each forged tool has a soundness/completeness profile. A sound but incomplete tool
(catches every real error but also flags valid reasoning) pairs well with a complete
but unsound tool (never false-alarms but misses some errors). This should inform
Phase 3 Pareto selection — diversity across the soundness/completeness spectrum is
more valuable than multiple tools clustered at the same point.

### Property-Based Testing / Shrinking (Hypothesis library)
The dynamic trap generator is essentially a property-based test generator. The
Python `hypothesis` library has sophisticated **shrinking algorithms** that, when a
test fails, automatically find the **minimal failing case**. Integrating this into
Nemesis would mean: when an adversarial task breaks a tool, Nemesis automatically
simplifies the task to find the minimal mutation that causes the break. That minimal
case is far more informative for Coeus than the full complex adversarial task.

Example: if a 5-element transitivity chain breaks IBAI v2, shrinking finds that
a 3-element chain with shuffled premises is the minimal break. That tells Coeus
the issue is premise ordering, not chain length.

### NSGA-II/III (multi-objective evolution)
For Phase 3 Pareto multi-objective fitness, use **NSGA-III with reference points**.
The fitness vector has 6 dimensions — naive Pareto selection gets crowded and clusters
on one part of the front. NSGA-III's reference-point mechanism preserves diversity
across fitness dimensions, keeping the tool library spread across the soundness/
completeness spectrum rather than converging to a single archetype.

---

## Libraries

Nemesis uses two off-the-shelf frameworks that match the theoretical foundations:

- **GeMTest** (`pip install gemtest`) — General Metamorphic Testing Framework.
  Write metamorphic relations in pure Python + pytest. Automatically generates
  follow-up inputs, checks relations, reports violations. Domain-independent.
  Replaces hand-rolled mutation categories with a principled framework.

- **Hypothesis** (`pip install hypothesis`) — Property-based testing with
  state-of-the-art shrinking. When an adversarial task breaks a tool, Hypothesis
  automatically finds the minimal mutation that causes the break. That minimal
  case is piped to Coeus as targeted feedback.

## Dependencies

- No API calls (pure algorithmic, like forged tools)
- No neural models
- `gemtest` (metamorphic relation framework)
- `hypothesis` (property-based testing + shrinking)
- Numpy + stdlib for task generation
- Imports forged tools via the existing `load_tool_from_file()` mechanism
