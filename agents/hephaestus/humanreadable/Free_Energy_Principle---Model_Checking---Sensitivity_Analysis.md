# Free Energy Principle + Model Checking + Sensitivity Analysis

**Fields**: Theoretical Neuroscience, Formal Methods, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T04:32:36.107236
**Report Generated**: 2026-03-31T14:34:46.385192

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Finite‑State Structure**  
   - Tokenise the prompt and each candidate answer with `re.findall`.  
   - Extract atomic propositions:  
     *Negations* (`not`, `no`), *comparatives* (`>`, `<`, `>=`, `<=`, `more than`, `less than`), *conditionals* (`if … then …`, `unless`), *causal claims* (`because`, `leads to`, `results in`), *ordering relations* (`before`, `after`, `first`, `last`), *numeric values* (integers/floats).  
   - Build a directed graph `G = (V, E)` where each vertex `v∈V` is an atom labeled with its polarity (True/False) and each edge `e∈E` encodes a logical relation extracted from the pattern (e.g., an edge `A → B` for “if A then B”, an edge `A –| B` for “A unless B”, a weighted edge for comparatives).  
   - The graph is interpreted as a finite‑state transition system: a state is a truth‑assignment to all vertices; transitions flip the truth value of a single vertex according to its incoming edges (deterministic update rule).  

2. **Specification Extraction (Prompt as LTL)**  
   - Convert the prompt’s extracted relations into a set of Linear Temporal Logic formulas `Φ` (e.g., `G (A → F B)` for “whenever A holds, B will eventually hold”, `G (¬(C ∧ D))` for mutual exclusion).  
   - Use a simple BFS‑based model checker: enumerate reachable states from the initial state (all atoms false) up to a depth bound `d = |V|`. For each state, evaluate every formula in `Φ` using standard LTL semantics (next, until, globally). Record a Boolean satisfaction vector `s(state)`.  

3. **Free‑Energy‑Like Prediction Error**  
   - For a candidate answer, compute its characteristic state `s_ans` by evaluating the same atomic propositions on the answer’s text (True if the proposition appears with affirmative polarity, False if negated or absent).  
   - Define prediction error as the mean‑squared deviation between the answer’s truth vector and the set of satisfying states:  
     `E = (1/|S|) Σ_{s∈S} ‖s_ans – s‖²`, where `S = {state | ∀ϕ∈Φ, ϕ holds in state}`.  
   - This is analogous to variational free energy: minimizing `E` selects answers whose truth‑assignment is closest to any model of the prompt constraints.  

4. **Sensitivity Analysis**  
   - For each atomic proposition `v_i`, create a perturbed answer by toggling its truth value (add/remove negation, flip comparative direction). Re‑compute `E_i`.  
   - Sensitivity score: `S = sqrt( (1/n) Σ_i (E_i – E)² )`. Lower `S` indicates the answer’s score is robust to small perturbations.  
   - Final candidate score: `Score = –E – λ·S` (λ = 0.5 balances fit and robustness). Lower `Score` → better answer.  

All steps use only `numpy` for vector operations and the Python standard library for regex, BFS, and arithmetic.

**Structural features parsed**  
Negations, comparatives, conditionals, causal markers, ordering/temporal cues, and explicit numeric literals. These are mapped to atoms and edge types in the transition system.

**Novelty**  
The combination mirrors existing frameworks—probabilistic soft logic (truth‑weighted Markov nets), bounded model checking (BFS state exploration), and local sensitivity analysis in probabilistic programming—but integrates them into a single, deterministic scoring pipeline that operates on shallow syntactic parses. No published work couples Free Energy‑style prediction error with exhaustive LTL model checking and finite‑difference sensitivity in this exact way, making the approach novel in its algorithmic composition.

**Rating**  
Reasoning: 8/10 — captures logical consistency and robustness via explicit constraint propagation and error minimization.  
Metacognition: 6/10 — the method can report its own uncertainty (sensitivity) but does not reason about its reasoning process.  
Hypothesis generation: 5/10 — focuses on evaluation; generating new hypotheses would require additional generative components.  
Implementability: 9/10 — relies solely on regex, BFS, and numpy linear algebra; no external libraries or APIs needed.

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

- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Model Checking**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Free Energy Principle + Model Checking: strong positive synergy (+0.259). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Sensitivity Analysis: strong positive synergy (+0.375). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-28T03:27:15.482589

---

## Code

*No code was produced for this combination.*
