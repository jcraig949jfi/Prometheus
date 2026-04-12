# Autopoiesis + Compositionality + Sensitivity Analysis

**Fields**: Complex Systems, Linguistics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T20:45:37.827237
**Report Generated**: 2026-03-27T05:13:40.019276

---

## Nous Analysis

**Algorithm – “Closure‑Sensitivity Scorer”**  
The tool parses a prompt into a set of logical **atoms** (propositions) using regex patterns for:  
- **Negations** (`not`, `no`, `never`) → polarity flag.  
- **Comparatives** (`greater than`, `less than`, `more`, `fewer`) → relational atom with a numeric threshold.  
- **Conditionals** (`if … then …`, `unless`, `provided that`) → antecedent‑consequent pair.  
- **Causal claims** (`because`, `leads to`, `results in`, `due to`) → cause‑effect edge.  
- **Numeric values** (integers/floats) → literal atom with a value field.  
- **Ordering relations** (`before`, `after`, `precedes`, `follows`) → temporal atom.

Each atom is stored as a Python `namedtuple` with fields: `id`, `type`, `polarity` (±1), `value` (float or None), `children` (list of child IDs). All atoms are placed in a NumPy‑backed structure:  
- `truth` – bool array of current truth values.  
- `dep_matrix` – sparse int matrix where `dep_matrix[i, j]=1` if atom *j* is a child of *i* (used for fast forward‑chaining).

**Compositional rules** are hard‑coded productions (e.g., if atom type=`conditional` and `truth[antecedent]==True` then set `truth[consequent]=True`; for comparatives, evaluate `value` against threshold; for causal, treat as deterministic implication). These rules are applied iteratively using NumPy vectorized operations until `truth` converges – the **autopoietic closure** (organizational closure reached when no new truths are generated).

**Sensitivity analysis**: For a candidate answer atom *a*, generate *K* perturbed worlds by randomly:  
1. Flipping polarity of a subset of negation atoms.  
2. Adding Gaussian noise (σ=0.05·|value|) to numeric literals.  
3. Toggling a small percentage of conditional antecedents.  
For each world, recompute the closure and record the truth value of *a*. The score is  
`S = 1 - std(truth_values_across_worlds)`, clipped to [0,1]. Low variance (robust truth) yields high score; high variance yields low score.

**Structural features parsed**: negations, comparatives, conditionals, causal claims, numeric literals, ordering/temporal relations.

**Novelty**: The triple blend is not found in existing NLP scorers. Autopoiesis supplies a self‑maintaining forward‑chaining closure; compositionality gives the rule‑based meaning construction; sensitivity analysis adds a robustness‑based grading dimension. Prior work treats these aspects in isolation (e.g., logical theorem provers, compositional semantics pipelines, or sensitivity‑only uncertainty metrics), but none combine them into a single, numpy‑only scoring loop.

---

Reasoning: 8/10 — The algorithm captures logical consequence and robustness, core to reasoning, though it lacks deep abstraction.  
Metacognition: 6/10 — No explicit self‑reflection on reasoning steps; only implicit via closure stability.  
Hypothesis generation: 5/10 — Generates perturbations but does not propose new hypotheses beyond answer truth.  
Implementability: 9/10 — Relies solely on regex, NumPy vectorization, and standard‑library containers; no external dependencies.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Autopoiesis**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 


Similar combinations that forged successfully:
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Chaos Theory + Active Inference + Compositionality (accuracy: 0%, calibration: 0%)
- Chaos Theory + Adaptive Control + Compositionality (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
