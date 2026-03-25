# Engineering Prompt: v2 Rebuilt Tools — Integration & Calibration

*For: Nous/Coeus/Hephaestus engineer*
*From: Athena (chief science officer)*
*Date: 2026-03-25*

---

## WHAT HAPPENED

We sent the 7 surviving forged tools to a 5-model Titan Council (Claude, ChatGPT, Gemini, DeepSeek, Grok). They independently converged on the same diagnosis:

1. The hash-to-vector representation is noise — sophisticated math on meaningless inputs
2. No tool checks logical consistency — "reasoning evaluators that don't check reasoning"
3. NCD (compression distance) is a good drop-in replacement for hash similarity
4. Structural parsing (negation, comparatives, conditionals, subject-object) is what's actually missing

Based on that, we rebuilt the three most promising tools, extracted two utility mechanisms, and retired the bottom two. Everything has been tested against the 15-trap battery (10 original + 5 new compositional traps).

---

## WHAT'S IN THE REPO

### Tier 1 — Rebuilt tools (in `agents/hephaestus/forge/`)

| File | What it is | Accuracy | Calibration | vs NCD |
|------|-----------|----------|-------------|--------|
| `ibai_v2.py` | Active Inference + NCD + structural constraints + local SVD | 53.3% (8/15) | 40.0% (6/15) | +33/+33 |
| `efme_v2.py` | Structural falsification + NCD tiebreaker | 46.7% (7/15) | 40.0% (6/15) | +27/+33 |
| `bandit_v2.py` | N-gram/structural UCB bandit + persistent state | 40.0% (6/15) | 40.0% (6/15) | +20/+33 |

All three beat NCD on both accuracy and calibration. The structural parsing is what makes the difference — these tools correctly handle transitivity, subject-object roles, negation scope, and modus tollens on the new compositional traps (11-15), where the v1 tools relied on hash-based coin flips.

### Tier 2 — Utility modules (in `agents/hephaestus/forge/`)

| File | Extracted from | What it does |
|------|---------------|-------------|
| `perturbation_calibrator.py` | EATM-S | Wraps any tool. Runs prompt perturbations, weights confidence by stability across perturbations. |
| `criticality_regularizer.py` | ME-CGA | Wraps any tool. Measures whether scoring landscape is flat/degenerate/critical. Adjusts scores toward discriminative regime. |

These are NOT standalone `ReasoningTool` classes. They're wrappers that take a base tool and enhance it. Usage:

```python
from perturbation_calibrator import PerturbationCalibrator
from criticality_regularizer import CriticalityRegularizer

base = SomeReasoningTool()
calibrated = PerturbationCalibrator(base)
regularized = CriticalityRegularizer(base)

# Use calibrated.calibrated_evaluate() / calibrated.calibrated_confidence()
# Use regularized.regularized_evaluate() / regularized.landscape_quality()
```

### Tier 3 — Retired (still in `forge/`, do NOT use in RLVF pipeline)

| File | Why retired |
|------|------------|
| `ergodic_theory_x_sparse_autoencoders_x_model_checking.py` | Trivially gameable by echoing prompt keywords. 40% accuracy. |
| `tensor_decomposition_x_criticality_x_free_energy_principle.py` | Impressive math on hash noise. No structural analysis. |

### Test runner

`agents/hephaestus/test_v2_tools.py` — runs everything against the trap battery with NCD baseline comparison. Just `python test_v2_tools.py`.

---

## WHAT YOU NEED TO DO

### 1. Fix the calibration gap (HIGH PRIORITY)

The v2 tools score 40% calibration vs v1's 60%. The root cause: NCD produces nearly identical confidence values for short candidates ("Yes" vs "No"). When `confidence("Is 9.11 larger than 9.9?", "Yes")` and `confidence(..., "No")` return almost the same number, calibration fails by coin flip.

**Fix**: The `confidence()` method should route through the same structural analysis as `evaluate()`. Right now EFME v2 and IBAI v2 do partial structural analysis in confidence, but they don't run the full constraint checker. The fix is straightforward:

```python
def confidence(self, prompt, answer):
    # Run the full structural scoring
    struct = self._constraint_score(prompt, answer)  # or _structural_score
    if struct > 0.3:
        return 0.8 + struct * 0.2   # high confidence for structurally consistent
    elif struct < -0.3:
        return 0.05                  # near-zero for structurally inconsistent
    else:
        # No structural signal — fall back to NCD
        ncd_val = self._ncd(prompt, answer)
        return (1.0 - ncd_val) ** 2
```

The key insight: when the structural parser has signal, it should dominate confidence. When it doesn't (no comparatives, no negation, no conditionals found), fall back to NCD.

### 2. Wire v2 tools into the Hephaestus pipeline

The v2 tools are hand-crafted, not forge-generated. They need to be integrated as:

**A) Seed tools** — Include them in the code gen prompt (`prompts.py`) so the 397B model sees what "good" looks like:

```
--- Reference Tools ---
The following hand-tuned tools achieve 40-53% accuracy on the trap battery.
Your tool must beat NCD baseline (20% accuracy, 7% calibration) to survive.

Key patterns that work:
- Structural parsing: extract negations, comparatives, conditionals from prompt
- NCD for relevance (tiebreaker, not primary signal)
- Constraint checking: does the candidate satisfy or violate prompt structure?

Key patterns that DON'T work:
- Hash-to-vector similarity (measures string noise, not reasoning)
- Bag-of-words overlap (gameable by echoing prompt)
- Pure NCD (can't distinguish short candidates like Yes/No)
```

**B) Baseline ensemble** — Consider using the best v2 tool (IBAI v2) as the new baseline instead of raw NCD. A forged tool should beat IBAI v2, not just NCD.

### 3. Add concepts to Nous (see companion prompt)

The companion prompt (`engineering_prompt_ncd_and_logical_checker.md`) has 5 new concepts to add to `nous/src/concepts.py`: Proof Theory, Constraint Satisfaction, Compositional Semantics, Counterfactual Reasoning, and Normalized Compression Distance.

### 4. Update Coeus with v2 performance data

Coeus should learn that:
- Structural parsing > hash similarity (causal finding from v2 results)
- Concepts involving logical structure (Falsificationism, Active Inference) have positive forge effect
- Concepts involving fake dynamics (Ergodic Theory as implemented) add no value

Manually seed these into the enrichment system so new forge runs benefit.

### 5. Traps that defeat EVERYTHING

These traps defeat all tools (v1 and v2) and define the next frontier:

| Trap | Why it's hard | What would fix it |
|------|--------------|-------------------|
| "Is 9.11 larger than 9.9?" | Requires numeric evaluation | `float(a) > float(b)` — trivial if you detect the comparison pattern |
| "Bat and ball = $1.10" | Requires solving `x + (x+1) = 1.10` | Equation extraction + solver |
| "Coin flip independence" | Domain knowledge (probability) | Pattern matching on independence keywords |
| "Sum of odd numbers" | Arithmetic rule knowledge | Could hardcode parity rules |
| "All but 8 die" | Language trick ("all but 8" = 8 remain) | Parse "all but N" as N |

The **numeric evaluation** trap is the most fixable. A tool that extracts numbers from the prompt using regex, parses comparison operators, and actually evaluates `float("9.11") < float("9.9")` would immediately pick up 2-3 traps. This could be a standalone tool or a feature added to EFME v2's structural parser.

### 6. Forge a logical consistency checker (from companion prompt)

The companion prompt (`engineering_prompt_ncd_and_logical_checker.md`) details the spec for a constraint-propagation-based logical consistency checker. This is the #1 gap identified by all 5 Titans. The v2 tools have a basic version of this (structural parsing), but a dedicated tool with full entailment/contradiction/transitivity checking would be much stronger.

---

## FILES TO READ

Before starting, read these in order:

1. `agents/hephaestus/forge/ibai_v2.py` — best v2 tool, shows the structural + NCD + SVD pattern
2. `agents/hephaestus/forge/efme_v2.py` — structural falsification approach
3. `agents/hephaestus/forge/bandit_v2.py` — feature-discovery with structural features
4. `agents/hephaestus/forge/perturbation_calibrator.py` — confidence wrapper
5. `agents/hephaestus/forge/criticality_regularizer.py` — landscape quality checker
6. `agents/hephaestus/src/test_harness.py` — trap battery + NCD baseline
7. `agents/hephaestus/test_v2_tools.py` — test runner (just run it to see current state)
8. `docs/titan_council_prompt_07_forge_review_response.md` — full Titan Council feedback
9. `docs/engineering_prompt_ncd_and_logical_checker.md` — companion prompt (NCD baseline + logical checker + pipeline improvements)

---

## SUCCESS CRITERIA

- [ ] v2 tools have calibration >= 50% (up from 40%)
- [ ] At least one v2 tool hits 60%+ accuracy (currently 53%)
- [ ] Numeric evaluation added to structural parser (fixes "9.11 > 9.9" class of traps)
- [ ] v2 tools wired into `prompts.py` as seed examples
- [ ] Coeus enrichments updated with v2 performance data
- [ ] Test runner passes cleanly with all tools evaluated
- [ ] Retired tools (EGSAE-MC, CPCTTN) excluded from RLVF pipeline config
