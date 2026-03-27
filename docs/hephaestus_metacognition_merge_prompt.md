# Hephaestus: Metacognition Merge — Council Responses → v5 Tools

You are Hephaestus, the Forgemaster. Athena's Titan Council reviewed 10 reasoning tools and 4 of 5 members returned metacognition enhancements. Your job: extract the best ideas from each Council member, merge them into improved tools, test against Sphinx, and produce the v5 metacognition-enhanced library.

## Inputs

### Council Responses
File: `docs/titan_council_metacognition_responses.md`

Four members responded (line numbers):
- **Gemini** (line 1): Built a universal `_meta_confidence_cap()` engine. Identified 3 underlying architectures across the 10 tools. Applied the engine to the prime tool of each architecture. Most architectural.
- **ChatGPT** (line 727): Diagnosed the core issue: `confidence = f(correctness)` instead of `confidence = f(question_properties)`. Listed systematic Tier B gaps. Provided modular upgrade patterns.
- **Grok** (line 1360): Improved Tools 6, 7, 10 with working `_meta_confidence()` helper + enhanced `_secondary()`. Full working code.
- **DeepSeek** (line 1481): Full working code for Tool 1 with complete `_cat_score` preserved plus metacognitive additions. Most complete.

Claude did not respond — skip.

### The 10 Source Tools (v4)
Directory: `agents/hephaestus/forge_v4/`

```
1. chaos_theory_x_metacognition_x_pragmatics.py           (315 lines, Arch A)
2. falsificationism_x_network_science_x_compositionality.py (315 lines, Arch A)
3. analogical_reasoning_x_neural_oscillations_x_free_energy_principle.py (315 lines, Arch A)
4. analogical_reasoning_x_dialectics_x_mechanism_design.py  (126 lines, Arch B)
5. analogical_reasoning_x_mechanism_design_x_model_checking.py (126 lines, Arch B)
6. category_theory_x_ergodic_theory_x_metacognition.py      (126 lines, Arch B)
7. statistical_mechanics_x_compressed_sensing_x_falsificationism.py (200 lines, Arch C)
8. reservoir_computing_x_active_inference_x_abductive_reasoning.py (200 lines, Arch C)
9. analogical_reasoning_x_pragmatism_x_type_theory.py       (315 lines, Arch A)
10. category_theory_x_network_science_x_mechanism_design.py  (315 lines, Arch A)
```

### Scoring Data
File: `agents/hephaestus/forge_v4/all_scores.json`
Structure: `{"metadata": {...}, "tools": {"name": {"unseen_tier_a": float, "unseen_tier_b": float, ...}}}`

### Sphinx Battery
The test harness is at `agents/hephaestus/src/test_harness.py`. The expanded battery generators are in `agents/hephaestus/src/trap_generator.py` and `trap_generator_extended.py`.

## Your Task

### Step 1: Extract `_meta_confidence` implementations

Read all 4 Council responses. Extract every `_meta_confidence`, `_meta_confidence_cap`, or equivalent function. You should find:

- **Gemini's** `_meta_confidence_cap()` — presupposition, scope ambiguity, false dichotomy, subjectivity, self-reference detection
- **ChatGPT's** modular pattern — answerability classification, presupposition generalization, ambiguity aggregation
- **Grok's** `_meta_confidence()` — presupposition/loaded questions, scope/pronoun ambiguity, unanswerability
- **DeepSeek's** implementation — embedded in the full tool code

### Step 2: Build the merged `_meta_confidence` function

Combine the best regex patterns from all 4 into one function. The merge rules:

1. **Union of all detection patterns.** If Gemini catches presuppositions with pattern X and Grok catches them with pattern Y, include both.
2. **Most conservative confidence cap.** If Gemini returns 0.25 for presuppositions and Grok returns 0.22, use 0.22 (lower = more cautious = better for Tier B).
3. **ChatGPT's structure.** Use ChatGPT's diagnostic framework as the skeleton: classify the question FIRST (answerable/ambiguous/unanswerable/presupposition), THEN score.
4. **No memorization.** No exact trap wordings. All patterns must be structural (detect "Have you stopped X?" not "Have you stopped making errors?").

### Step 3: Apply to all 10 tools

For each of the 10 source tools:
1. Read the v4 file from `forge_v4/`
2. Add the merged `_meta_confidence()` function
3. Modify `confidence()` to call `_meta_confidence()` and cap the return value
4. Modify `evaluate()` to include metacognition signals in the reasoning string
5. DO NOT modify `_cat_score()` or any Tier A parsing logic — preserve verbatim

### Step 4: Test each improved tool

Run each improved tool against the Sphinx battery (both seen and unseen). Record:
- Tier A accuracy (must not decrease from v4)
- Tier B accuracy (should increase)
- Confidence calibration on Tier B traps (should show low confidence on ambiguous/unanswerable)
- Overall accuracy

### Step 5: Produce output

Save improved tools to `agents/hephaestus/forge_v5/` with the same filenames.

Create `agents/hephaestus/forge_v5/metacognition_merge_report.md` with:
- Which Council member's patterns were used for each detection category
- Per-tool before/after scores (v4 → v5)
- Any Tier A regressions (these are failures — fix before shipping)
- The merged `_meta_confidence()` function as a standalone reference

### Step 6: Apply the merged metacognition to the FULL v4 library

After validating on the 10 test tools, apply the same `_meta_confidence()` to ALL tools in `forge_v4/` that share the same architectures (Gemini identified 3 architectures — A, B, C). This should be mechanical: insert the function, modify `confidence()`, preserve everything else.

Save the full enhanced library to `forge_v5/`.

Run the full Sphinx battery (seen + unseen, Tier A + Tier B) on the complete v5 library and save results to `forge_v5/all_scores.json`.

## Constraints

- numpy + stdlib only (no torch, no transformers, no API calls)
- All tools must be self-contained (no shared modules — we learned this lesson with _caitl_v3)
- Deterministic (same input → same output)
- Preserve the ReasoningTool interface: `evaluate(prompt, candidates)` and `confidence(prompt, answer)`
- Tier A accuracy must NOT decrease. If it does, the merge broke something — debug and fix.
- Every tool must pass the existing test harness gates before admission to forge_v5/

## What Success Looks Like

- 10 test tools: Tier B unseen accuracy increases by 5%+ with zero Tier A regression
- Full library: median Tier B unseen improves from current baseline
- The `_meta_confidence()` function catches presuppositions, scope ambiguity, false dichotomies, unanswerability, and validity-vs-truth traps WITHOUT memorizing specific trap wordings
- `confidence()` returns < 0.3 on questions that are ambiguous, unanswerable, or contain false presuppositions
- Every tool is self-contained — no shared imports

## Context

This is the bridge between the forge library and the RLVF fitness function. Tier B accuracy (metacognition / judgment) is weighted 2x higher than Tier A (parsing) in Rhea's fitness function. Tools that know when they don't know are more valuable than tools that are confidently wrong. The Council unanimously agreed: `confidence = f(question_properties)` not `confidence = f(answer_score)`. Make it so.
