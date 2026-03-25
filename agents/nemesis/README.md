# Nemesis — Adversarial Co-Evolution Engine

*Goddess of retribution. Ensures no evaluator escapes deserved consequences.*

> **"Are our evaluators measuring reasoning, or have they learned to pass tests?"**

Nemesis generates adversarial tasks using formal metamorphic relations, organizes
them in a MAP-Elites quality-diversity grid, finds minimal failing cases, and
produces failure reports + Coeus feedback. Pure algorithmic — no API calls, no
neural models.

## First Result

IBAI v2 (our "best" tool at 67% static accuracy) drops to **46% adversarial survival**.
Meanwhile `information_theory_x_criticality_x_pragmatics` hits 85% adversarial survival
despite not being a static battery leader. **Static performance and adversarial robustness
measure different things.** That's the Goodhart gap.

## How It Works

1. **Generate** adversarial tasks by composing metamorphic relations on seed traps
2. **Validate** ground truth (execution evaluator cross-check, structural validity)
3. **Evaluate** all forge tools against all tasks (compute disagreement, find blind spots)
4. **Place** in MAP-Elites grid (10x10: logical complexity × linguistic obfuscation)
5. **Shrink** failures to minimal cases (iterative simplification)
6. **Report** failure analysis + write adversarial results for Coeus
7. **Sleep**, reload tools (picks up newly forged), repeat

## MAP-Elites Grid

Each cell holds the adversarial task that maximizes tool disagreement for that
(complexity, obfuscation) region. 100 cells = 100 diverse adversarial tasks
covering the entire behavioral boundary.

```
          Linguistic Obfuscation →
     1  2  3  4  5  6  7  8  9  10
  1 [.][X][X][X][X][.][.][.][.][X]
  2 [.][.][.][.][X][.][X][X][.][.]
  3 [X][.][.][.][X][X][.][.][.][.]
  4 [.][X][.][X][.][.][.][.][.][.]
  5-10: empty (needs more chain_extend compositions)
```

## Metamorphic Relations (12 core MRs)

| MR | What it does | Expected |
|----|-------------|----------|
| comparison_flip | Swap A and B in "Is A > B?" | flip |
| verb_inversion | "larger" → "smaller" | flip |
| negation_inject | Add "not" to change answer | flip |
| premise_shuffle | Reorder premises | same |
| distractor_add | Add irrelevant detail | same |
| passive_voice | Active → passive construction | same |
| paraphrase | Rewrite preserving meaning | same |
| chain_extend | Add elements to transitivity chain | same |
| conditional_weaken | "if P then Q" → "if P then maybe Q" | computed |
| affirm_consequent | Tempt with invalid inference | computed |
| numeric_distractor | Add misleading numeric fact | same |
| scale_transform | Multiply all numbers by K | same |

MRs compose: `paraphrase ∘ chain_extend ∘ distractor_add` produces a task
deep in the hard corner of the grid.

## Usage

```bash
# Continuous (default — reloads tools each cycle, 2min intervals)
python agents/nemesis/src/nemesis.py

# Single cycle
python agents/nemesis/src/nemesis.py --runonce

# More tasks per cycle
python agents/nemesis/src/nemesis.py --n-random 100 --n-targeted 50
```

## Output

- **grid/grid.json** — serialized MAP-Elites grid state
- **reports/nemesis_report_*.md** — failure analysis with tool rankings, blind spots, MR effectiveness
- **adversarial/adversarial_results.jsonl** — machine-readable results for Coeus (provenance-tagged)

## Architectural Invariant

All output is tagged `provenance: "adversarial"`. This data NEVER enters model
training paths. Rhea Batch 3 proved that mixing adversarial signal into training
cost 25 points on metacognition. The provenance tag is a hard gate, not a convention.

## Dependencies

- numpy (for NCD novelty check)
- No API calls, no neural models, no external services
