# Engineering Prompt: NCD Baseline + Logical Consistency Checker + Pipeline Improvements

*For: The Nous/Coeus/Hephaestus engineer*
*From: Athena (chief science officer)*
*Date: 2026-03-25*
*Context: Titan Council reviewed 7 forged tools. All 5 Titans independently identified the same two critical gaps.*

---

## SITUATION

We sent the 7 surviving forged tools to a 5-model review council (Claude, ChatGPT, Gemini, DeepSeek, Grok). The feedback was remarkably convergent:

1. **The hash-to-vector representation is the bottleneck** — all 7 tools apply sophisticated math to hash-derived noise. The frameworks are sound; the inputs are not.
2. **No tool checks logical consistency** — none verify entailment, contradiction, multi-step coherence, or compositional structure. We're building "reasoning evaluators that don't check reasoning" (direct quote from Claude).
3. **NCD (Normalized Compression Distance) via zlib** was independently proposed by 3 of 5 Titans as the best drop-in replacement for hash-based similarity. It's deterministic, numpy+stdlib only, captures structural similarity, and — critically — provides a continuous fitness landscape for the evolutionary engine to climb.

You already identified the two right integration points for NCD:
- **A) Baseline in the test harness** — replace random-chance (50%) with NCD. Pass threshold becomes "beat NCD."
- **B) Seed tool in `forge/`** — a working example of what "good" looks like.

This prompt covers those two tasks plus the bigger gap: forging a logical consistency checker.

---

## TASK 1: NCD Baseline + Seed Tool

### 1A. NCD Seed Tool for `forge/`

Write `forge/ncd_baseline.py` implementing the standard `ReasoningTool` interface:

```python
class ReasoningTool:
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Returns [{"candidate": str, "score": float, "reasoning": str}, ...] sorted desc by score."""

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns float in [0.0, 1.0]."""
```

Core mechanism:
```python
import zlib

def ncd(x: str, y: str) -> float:
    """Normalized Compression Distance. 0 = identical structure, 1 = unrelated."""
    xb, yb = x.encode('utf-8'), y.encode('utf-8')
    cx, cy = len(zlib.compress(xb)), len(zlib.compress(yb))
    cxy = len(zlib.compress(xb + yb))
    return (cxy - min(cx, cy)) / max(cx, cy)
```

- Score = `1 - ncd(prompt, candidate)` (lower distance = higher score)
- Confidence = `1 - ncd(prompt, answer)` clamped to [0, 1]
- Reasoning string should say something like `"NCD={ncd_value:.4f}, compression ratio={ratio:.4f}"`

Also write `forge/ncd_baseline.json` with the standard metadata format (concept_names can be `["Information Theory", "Kolmogorov Complexity", "Compression"]`).

### 1B. NCD Baseline in Test Harness

In `hephaestus/src/test_harness.py`:
- Add an NCD baseline scorer that runs the same 10 traps
- Change the pass threshold from "accuracy >= 60% AND calibration >= 50%" to "accuracy > ncd_accuracy AND calibration > ncd_calibration" (strictly greater than, not equal)
- Store the NCD baseline scores in the test results so we can see margin-over-baseline
- If a forged tool ties NCD on both metrics, it fails — it must beat NCD on at least one

**Important**: Run existing forged tools against the new baseline and report which survive. Some of the current tools in `forge/` may not beat NCD. That's the point — we're raising the bar.

### 1C. Write `forge/ncd_baseline.json`

```json
{
  "concept_names": ["Information Theory", "Kolmogorov Complexity", "Compression"],
  "concept_fields": ["Information Science", "Mathematics", "Information Science"],
  "nous_composite_score": null,
  "test_accuracy": null,
  "test_calibration": null,
  "forged_at": "2026-03-25T00:00:00",
  "notes": "Hand-crafted baseline. NCD via zlib. Not forge-generated."
}
```

(Fill in test_accuracy and test_calibration after running it through the trap battery.)

---

## TASK 2: Logical Consistency Checker — Forge It or Build It

This is the #1 gap identified by all 5 Titans unanimously. None of our 7 tools verify whether a candidate's answer logically follows from the prompt. They measure surface similarity, compression, stability, information content — but not reasoning.

### What It Should Do

Given a prompt and candidates, check:

1. **Entailment**: Does the candidate logically follow from premises in the prompt?
2. **Contradiction**: Does the candidate contradict claims in the prompt?
3. **Compositional consistency**: "dog bit man" ≠ "man bit dog" — word order matters
4. **Multi-step coherence**: If A > B and B > C, a correct answer should affirm A > C
5. **Calibration signal**: Hedging language ("probably", "might") should correlate with uncertainty

### Implementation Approach — Deterministic, numpy+stdlib only

This is NOT a neural approach. It's symbolic pattern matching + constraint propagation:

```
Text → Extract structured facts → Build constraint graph → Check consistency
```

**Fact extraction** (regex-based):
- Comparatives: "X is larger/greater/more than Y" → `(X, >, Y)`
- Negations: "not/never/no X" → `(NOT, X)`
- Conditionals: "if X then Y" → `(X, IMPLIES, Y)`
- Identity: "X is a Y" / "X is Y" → `(X, ISA, Y)`
- Quantifiers: "all X are Y" → `(FORALL, X, Y)`, "some X are Y" → `(EXISTS, X, Y)`

**Constraint propagation**:
- Transitivity: if `(A, >, B)` and `(B, >, C)` then `(A, >, C)` should hold
- Modus ponens: if `(P, IMPLIES, Q)` and `P` is asserted, then `Q` should be affirmed
- Contradiction detection: `(X, >, Y)` and `(Y, >, X)` in same text = contradiction

**Scoring**:
- `+1` per entailment satisfied
- `-2` per contradiction detected (asymmetric — contradictions are worse than missing entailments)
- Normalize by total constraints found
- Bonus for parsimony: shorter answers with same constraint satisfaction score higher (Occam)

### Two Paths — Pick One (or Both)

**Path A: Hand-build it** as a seed tool in `forge/`, like NCD. This is faster and guarantees quality, but it doesn't test the pipeline.

**Path B: Feed it to Nous → Hephaestus** as a concept triple. Suggested triple: `"Proof Theory" × "Constraint Satisfaction" × "Compositional Semantics"`. If the pipeline can't forge this, that's diagnostic — it tells us the code generation prompt needs work.

**Recommendation**: Do both. Hand-build a reference implementation in `forge/logical_consistency_checker.py`, then also add the triple to Nous and see if Hephaestus can forge something that beats it. If the forged version beats the hand-built one, the pipeline is working. If not, the hand-built one still raises the bar.

---

## TASK 3: Pipeline Improvements (from Titan Council feedback)

### 3A. Coeus: Add NCD forge effect

Once NCD is the baseline, Coeus should track a new metric: **margin over NCD** for each forged tool. This is more informative than raw accuracy/calibration because it measures *what the tool adds beyond compression-based similarity*.

In `coeus/src/causal_graph.py`, when encoding the dataset:
- Add `margin_accuracy` = tool accuracy - NCD accuracy
- Add `margin_calibration` = tool calibration - NCD calibration
- Use these as outcome variables alongside raw forge_success

This lets Coeus learn which concept combinations produce tools that add value *beyond what NCD gives for free*.

### 3B. Hephaestus: Seed tool injection in prompts

In `hephaestus/src/prompts.py`, add a section to the code generation prompt that shows the forging model what a good tool looks like. Include NCD as a concrete example:

```
--- Reference Implementation ---
The following NCD-based tool achieves {accuracy}% accuracy, {calibration}% calibration
on the trap battery. Your tool must beat these scores to survive.

{ncd_source_code}

Your implementation should capture reasoning patterns that pure compression misses.
```

This gives the 397B model a concrete quality floor and steers it away from reimplementing string similarity.

### 3C. Nous: Add missing concepts

The Titan Council identified concept gaps. Add these to `nous/src/concepts.py`:

```python
{"name": "Proof Theory", "field": "Mathematics", "short_description": "Study of formal proofs as mathematical objects; proof normalization, cut elimination, proof nets"},
{"name": "Constraint Satisfaction", "field": "Computer Science", "short_description": "Finding assignments that satisfy all constraints; arc consistency, backtracking, constraint propagation"},
{"name": "Compositional Semantics", "field": "Philosophy", "short_description": "Meaning of complex expressions determined by meanings of parts and rules of combination; Frege's principle"},
{"name": "Counterfactual Reasoning", "field": "Philosophy", "short_description": "Reasoning about what would have happened under different conditions; Lewis's possible worlds, Pearl's do-calculus"},
{"name": "Normalized Compression Distance", "field": "Information Science", "short_description": "Universal similarity metric via Kolmogorov complexity approximation; compression-based, model-free"},
```

These are the concepts the Titans said were missing. Adding them lets Nous generate triples that target the logical consistency gap directly.

### 3D. Test harness: Add compositional traps

The current 10-trap battery tests cognitive biases, math tricks, and logic puzzles. Add 3-5 traps that specifically test compositional/logical reasoning:

```python
# Trap 11: Transitivity
{"prompt": "If Alice is taller than Bob, and Bob is taller than Carol, who is tallest?",
 "candidates": ["Carol", "Alice", "Bob", "They are the same height"],
 "correct": "Alice"}

# Trap 12: Negation scope
{"prompt": "It is not the case that all birds can fly. Can penguins fly?",
 "candidates": ["Yes, all birds can fly", "No, some birds cannot fly", "The question cannot be answered from the given information", "Yes, penguins are birds"],
 "correct": "The question cannot be answered from the given information"}

# Trap 13: Comparative reversal
{"prompt": "9.11 is less than 9.9. Which number is larger?",
 "candidates": ["9.11", "9.9", "They are equal", "Cannot be determined"],
 "correct": "9.9"}

# Trap 14: Compositional word order
{"prompt": "The dog chased the cat. Who was being chased?",
 "candidates": ["The dog", "The cat", "Both", "Neither"],
 "correct": "The cat"}

# Trap 15: Modus tollens
{"prompt": "If it is raining, the ground is wet. The ground is not wet. Is it raining?",
 "candidates": ["Yes", "No", "Maybe", "Not enough information"],
 "correct": "No"}
```

These traps specifically target the gap the Titans identified. A tool that can't handle these is measuring string similarity, not reasoning.

---

## PRIORITY ORDER

1. **NCD baseline in test harness** (1B) — immediately raises the bar for all future forges
2. **NCD seed tool** (1A) — gives Hephaestus a concrete example
3. **New concepts in Nous** (3C) — unlocks logical consistency triples
4. **Compositional traps** (3D) — tests what we care about
5. **Logical consistency checker** (Task 2) — the big deliverable
6. **Coeus margin tracking** (3A) — learns from the new baseline
7. **Seed tool injection** (3B) — improves forge quality

---

## SUCCESS CRITERIA

After these changes:
- [ ] NCD baseline runs on all 10 existing traps, scores are recorded
- [ ] Existing forged tools are re-evaluated against NCD; survivors are documented
- [ ] A logical consistency checker exists in `forge/` (hand-built or forged or both)
- [ ] The logical consistency checker beats NCD on the new compositional traps
- [ ] Coeus tracks margin-over-NCD as a causal variable
- [ ] Nous concept list includes Proof Theory, Constraint Satisfaction, Compositional Semantics, Counterfactual Reasoning, NCD
- [ ] Test harness has 15 traps (10 original + 5 compositional)
- [ ] At least one forge run has been executed with the new pipeline and results documented

---

## CONTEXT FILES

Read these before starting:
- [agents/hephaestus/src/test_harness.py](agents/hephaestus/src/test_harness.py) — current trap battery
- [agents/hephaestus/src/hephaestus.py](agents/hephaestus/src/hephaestus.py) — forge loop
- [agents/hephaestus/src/prompts.py](agents/hephaestus/src/prompts.py) — code gen prompt
- [agents/hephaestus/src/validator.py](agents/hephaestus/src/validator.py) — validation gates
- [agents/coeus/src/causal_graph.py](agents/coeus/src/causal_graph.py) — causal analysis
- [agents/nous/src/concepts.py](agents/nous/src/concepts.py) — concept dictionary
- [docs/titan_council_prompt_07_forge_review_response.md](docs/titan_council_prompt_07_forge_review_response.md) — full Titan Council feedback
