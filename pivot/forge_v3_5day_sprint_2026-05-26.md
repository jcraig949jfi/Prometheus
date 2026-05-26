# Forge v3 — 5-Day Sprint Plan

**Filed:** 2026-05-26
**Goal:** Five improvements to deepen, broaden, and level-up the forge
**Method:** Slow-roll via loop, chipping away over 5 days

---

## Day 1: Compose Parser + Algorithm (The Decisive Test)

**What:** Wire a main-forge text parser to a diversity-forge inference engine.
Prove that diverse substrate composes into something better than either part alone.

**Design:**
```python
class ComposedTool:
    def __init__(self):
        self.parser = MainForgeParser()      # Extracts structure from text
        self.engine = ForwardChainEngine()    # Reasons over structured input
    
    def evaluate(self, prompt, candidates):
        # Stage 1: Parse text into structured propositions + constraints
        parsed = self.parser.extract(prompt)  # {propositions, rules, numerics, negations}
        
        # Stage 2: Feed structured input to inference engine
        for candidate in candidates:
            score = self.engine.score(parsed, candidate)
```

**Implementation:**
- Take the best parser from forge/ (highest R1 accuracy on the tier battery)
- Take the reasoner from diversity_forge/tools/reasoner_*.py
- Build a ComposedTool that chains them
- Run through the full 186-probe battery + 22 puzzle battery
- Compare: composed vs parser-alone vs reasoner-alone

**Success metric:** Composed tool beats both components on at least one tier.

**Files:**
- `agents/hephaestus/src/composer.py` — composition framework
- `agents/hephaestus/composed_tools/` — output directory

---

## Day 2: Multi-Turn Refinement (Inline Repair Loop)

**What:** Instead of scrapping failed tools, send the error back to the LLM
for immediate repair. Up to 3 refinement rounds per candidate.

**Design:**
```
Generate code
  → Gate 1-4 (syntax, imports, interface, runtime)
    → If fails: send {code + error} back to LLM with "fix only" prompt
    → Re-validate
    → Up to 3 rounds
  → Gate 5 (trap battery)
    → If close (acc >= 35%): send {code + failing traps} back to LLM
    → "These 5 traps fail. Fix the scoring logic for these cases."
    → Re-run battery
    → Up to 2 rounds
```

**Implementation:**
- New function `forge_one_with_refinement()` wrapping `forge_one()`
- Reuses the LLM_REPAIR_PROMPT for gate failures
- New REFINEMENT_PROMPT for near-miss trap battery failures
- Tracks refinement_rounds in ledger metadata

**Success metric:** Forge rate improves from ~2% to ~5%+ on the same candidates.

**Files:**
- Modify `agents/hephaestus/src/hephaestus.py` — add refinement loop
- New CLI flag: `--refine` (enable inline refinement, default off)

---

## Day 3: Parameterized Puzzle Generator

**What:** Replace the fixed 22-puzzle battery with a generator that produces
unlimited variants. Tools that memorize fixed problems fail on generated ones.

**Design:**
```python
class PuzzleGenerator:
    def constraint_satisfaction(self, n=3, seed=None):
        # Generate random NxN Latin square with clues
        
    def graph_problem(self, n_nodes=5, seed=None):
        # Random graph, random shortest-path query
        
    def state_machine(self, n_states=3, n_steps=5, seed=None):
        # Random transition table + input sequence
        
    def sequence_prediction(self, rule_type='geometric', seed=None):
        # Random sequence with known next element
        
    def planning(self, n_actions=4, seed=None):
        # Random precondition/effect actions, random goal
        
    def arithmetic_chain(self, n_steps=4, seed=None):
        # Random multi-step computation
```

**Implementation:**
- `agents/hephaestus/src/puzzle_generator.py` — parameterized generators
- Each generator produces {prompt, candidates, correct, category}
- Integrate into diversity_forge.py as `generate_battery(n=50, seed=...)`
- Run each generated tool against fresh puzzles (different seed) to detect memorization

**Success metric:** Tools that pass on fixed puzzles also pass on generated variants
(>80% retention = genuine algorithm, <50% = memorized).

**Files:**
- `agents/hephaestus/src/puzzle_generator.py` — new file
- Modify `diversity_forge.py` to use generated batteries

---

## Day 4: Seed from Winners (Exemplar-Driven Generation)

**What:** Use the best diversity-forge tools as seeds/exemplars for the next
generation. Show the LLM working code and ask it to improve or extend.

**Design:**
```
For each winning tool:
  1. "Here is a working tool that scores X%. Improve it to handle Y."
  2. "Here is a forward-chaining engine. Add natural language parsing."
  3. "Here is a backtracking searcher. Make it handle graph problems."
  4. "Combine this parser with this reasoner into one tool."
```

**Implementation:**
- `agents/hephaestus/src/seed_forge.py` — exemplar-driven generation
- Loads best tools from diversity_forge/tools/ and forge/
- Generates improvement prompts targeting specific weaknesses
- Evaluates against both puzzle and text batteries
- Tracks lineage: which seed → which child → what improved

**Success metric:** Seeded tools score higher than their parents on at least
one battery (text or puzzle).

**Files:**
- `agents/hephaestus/src/seed_forge.py` — new file
- `agents/hephaestus/seed_forge/` — output directory

---

## Day 5: Behavioral NCD (Honest Novelty Gate)

**What:** Replace source-code NCD with output-vector NCD. Two tools with
identical code structure but different answer patterns = different. Two tools
with different code but identical answers = same.

**Design:**
```python
def behavioral_ncd(tool_a, tool_b, battery):
    # Run both tools on same battery
    answers_a = [tool_a.evaluate(p, c)[0]["candidate"] for p, c in battery]
    answers_b = [tool_b.evaluate(p, c)[0]["candidate"] for p, c in battery]
    
    # NCD on answer vectors (not source code)
    vec_a = "|".join(answers_a).encode()
    vec_b = "|".join(answers_b).encode()
    return zlib_ncd(vec_a, vec_b)
```

**Implementation:**
- New function `compute_behavioral_novelty()` in hephaestus.py
- Runs new tool against battery, compares output vector to library
- Replaces or supplements `_compute_novelty()` in the forge pipeline
- Cache output vectors for existing library (compute once, reuse)

**Success metric:** Behavioral NCD gives different rankings than source NCD.
Specifically: tools from different models that look novel by source but
identical by behavior get correctly identified as duplicates.

**Files:**
- Modify `agents/hephaestus/src/hephaestus.py` — add behavioral novelty
- `agents/hephaestus/behavioral_vectors.json` — cached output vectors

---

## Execution Schedule

| Day | Task | Effort | Dependencies |
|-----|------|--------|-------------|
| 1 (May 26) | Compose Parser + Algorithm | Build + test | None |
| 2 (May 27) | Multi-Turn Refinement | Modify forge pipeline | None |
| 3 (May 28) | Puzzle Generator | New module | None |
| 4 (May 29) | Seed from Winners | New module | Day 1 results |
| 5 (May 30) | Behavioral NCD | Modify novelty scoring | Day 3 battery |

Each day: build → test → commit → report → loop.
Forges continue running in background throughout.
