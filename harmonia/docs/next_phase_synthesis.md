# Next Phase Synthesis
## From exploration to targeted reasoning
### 2026-04-13

---

## What's Exhausted

- Open-ended correlation search across domains (21 kills, 0 novel bridges)
- Feature-level cross-domain matching (F33-F38 kill everything)
- Invariant-level structure detection (all known math or artifact)
- More-of-the-same experiments (diminishing returns)

## What's NOT Exhausted

### 1. The instrument itself as a product

The battery (40 tests), the kill taxonomy (21 modes), the cross-domain protocol (7 layers), and the calibration anchor (7 theorems at 100.000%) are a reusable scientific instrument. It can be POINTED AT specific questions rather than wandering.

**Open conjectures the instrument could attack:**
- BSD rank predictions at specific conductors (we have 3.8M curves)
- Goldfeld's conjecture on average rank (we have the statistics)
- Specific Langlands functoriality predictions (we have EC + MF + Maass data)
- Montgomery's pair correlation for restricted test functions (we have zeros)
- Specific Sato-Tate refinements for CM families (we have the split)

### 2. The structure probe (Harmonia's suggestion)

A simple model (MLP, 50 lines) that takes raw zero vectors and predicts algebraic invariants. The model itself isn't the finding — WHAT IT LEARNS is the finding. Gradient attribution shows which zeros matter. Truncation experiments show how much spectral data is needed. This is synthetic reasoning at the simplest level: let the model discover the functional.

### 3. The meta-analysis as science (James's instinct)

Three directions that DON'T drill deeper into the same well:

**A. Process, not product.** The 35GB formula trees, mathlib proofs, SciPy call graphs encode HOW humans do math. COMPOSE exists in source code. Does the structure of mathematical PRACTICE predict mathematical TRUTH? This is a question about the sociology/epistemology of mathematics that our instrument can answer.

**B. Failures as data.** 21 kills with 19 distinct failure modes. A generative model of false positives: given two random datasets with certain properties, predict WHICH artifact type will appear. This is a contribution to the methodology of data-driven science, not to mathematics specifically.

**C. Biological stress test.** 43 organism metabolic networks, completely untouched. Does the battery WORK on non-mathematical structured data? Does BREAK_SYMMETRY appear in enzyme→pathway mappings? This tests whether the instrument is specific to math or general to structured knowledge.

### 4. The synthetic reasoning layer

Not RL for hypothesis generation. Not a black-box predictor. Something that can:

- Look at the kill taxonomy and REASON about which regions of hypothesis space are still viable
- Look at weak signals in the void and REASON about whether they're worth pursuing
- Look at the negative space and REASON about what properties the primitive must have

This is closer to a theorem prover than a neural net. It takes the CONSTRAINTS (10 negative dimensions, 21 kill signatures, 7 calibration anchors) and derives what's CONSISTENT with all of them simultaneously.

The simplest version: a constraint solver. Feed it the 10 negative dimensions as constraints on a hypothesis space. Ask: what mathematical properties could exist that satisfy all constraints? The answer isn't a discovery — it's a MAP of where to look.

The more ambitious version: a chain-of-thought reasoner that reads the kill reports, the council feedback, and the surviving signal, and generates SPECIFIC testable hypotheses that are designed to be hard to kill. Each hypothesis comes with its predicted failure mode and the test that would kill it.

---

## The Three Options (James's call)

### Option A: Point the instrument at a specific open conjecture
Lowest risk, highest near-term payoff. Pick one conjecture (BSD, Goldfeld, Montgomery refinement), design the exact experiment, run it. The instrument is calibrated for exactly this.

### Option B: Build the structure probe + meta-analysis
Medium risk. The MLP on zeros (50 lines), the failure-mode generative model, and the biological stress test. These produce methodology contributions even if they don't produce mathematical discoveries.

### Option C: Build the synthetic reasoning layer
Highest risk, highest long-term payoff. A constraint-driven hypothesis generator that reasons about the negative space. This is the "level of synthetic reasoning" James is asking about. Not RL — constraint satisfaction + chain-of-thought over the project's own results.

### Option D: All three in parallel
M1 takes Option A (conjecture targeting), M2 takes Option B (probes + meta), and the reasoning layer (Option C) is designed as the next major infrastructure build.

---

## My Recommendation

Option D. The instrument is ready for conjecture targeting (M1). The meta-analysis and biological stress test are immediately actionable (M2). And the synthetic reasoning layer is what makes the project SCALABLE — instead of humans reading kill reports and deciding what to try next, the system reasons about its own results.

But the reasoning layer doesn't need TensorFlow or NVIDIA. It needs the kill taxonomy as structured input, the constraint set as formal logic, and a language model (which we already have) as the reasoning engine. The infrastructure is: structured memory of kills + constraint solver + hypothesis template generator.

We already have the kills. We already have the constraints. We just need to formalize them into something a reasoning engine can work with.
