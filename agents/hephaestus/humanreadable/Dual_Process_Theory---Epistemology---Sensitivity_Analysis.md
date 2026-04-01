# Dual Process Theory + Epistemology + Sensitivity Analysis

**Fields**: Cognitive Science, Philosophy, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T00:43:23.855368
**Report Generated**: 2026-03-31T14:34:55.541389

---

## Nous Analysis

**Algorithm: Dual‑Process Epistemic Sensitivity Scorer (DPESS)**  

1. **Data structures**  
   - `Prop`: a named tuple `(id, text, polarity, type, value)` where `polarity ∈ {+1,‑1}` captures negation, `type` ∈ `{comparative, conditional, causal, ordering, numeric}` and `value` holds extracted numbers or entities.  
   - `Graph`: adjacency list `Dict[int, List[Tuple[int, float, str]]]` where each edge `(src, wgt, rule)` represents a logical rule (e.g., modus ponens) extracted from conditionals; `wgt` is the initial epistemic weight.  
   - `Belief`: `np.ndarray` of shape `(n_props,)` holding current confidence scores in `[0,1]`.  

2. **Parsing (System 1 – fast heuristic)**  
   - Apply a handful of regex patterns to the prompt and each candidate answer to extract propositions and their `type`.  
   - Negations flip `polarity`. Comparatives (`>`, `<`, `≥`, `≤`) become ordering props with a numeric `value`. Conditionals (`if … then …`) create directed edges; causal verbs (`because`, `leads to`) become causal edges. Numeric literals are stored as numeric props.  
   - Initialise `Belief[i] = base` where `base = 0.9` if the proposition originates from a reliable source (epistemology: reliabilism – e.g., cited data), otherwise `base = 0.5`.  

3. **Constraint propagation (System 2 – slow deliberate)**  
   - Perform iterative belief update: for each edge `(i → j, wgt, rule)`, compute `new = Belief[i] * wgt` if rule is modus ponens; for ordering, enforce transitivity via Floyd‑Warshall‑style min‑max propagation.  
   - After each iteration, project beliefs back to `[0,1]` (clip). Stop when `np.max(np.abs(Belief_new - Belief_old)) < 1e‑3` or after 20 iterations.  

4. **Sensitivity analysis (epistemic robustness)**  
   - For each input proposition `k`, add a small perturbation `ε = 0.01` to its base belief, re‑run the propagation, and record the change in the final belief of the answer proposition `a`: `Δ_k = |Belief_a^perturbed - Belief_a|`.  
   - Compute overall sensitivity `S = mean(Δ_k)`. Low `S` indicates the answer’s truth is robust to input noise.  

5. **Scoring logic**  
   - Coherence `C = Belief_a` (final belief after propagation).  
   - Justification `J = mean(base belief of premises used in the proof path)` (epistemology: foundationalism – weight of basic beliefs).  
   - Final score: `Score = 0.4*C + 0.3*(1‑S) + 0.3*J`. Higher scores reward answers that are strongly believed, minimally sensitive to perturbations, and grounded in well‑justified premises.  

**Structural features parsed** – negations, comparatives (`>`, `<`), conditionals (`if…then`), causal claims (`because`, `leads to`), ordering relations (`before/after`, `more than`), and numeric values.  

**Novelty** – While probabilistic soft logic and Markov Logic Networks combine weighted rules with belief propagation, the explicit integration of System 1/System 2 dual‑process timing, epistemic justification layers (foundationalism/coherentism/reliabilism), and a sensitivity‑analysis robustness term is not present in existing public reasoning‑evaluation tools.  

**Ratings**  
Reasoning: 8/10 — The algorithm captures logical structure, propagates constraints, and quantifies robustness, offering a nuanced score beyond surface similarity.  
Metacognition: 6/10 — It distinguishes fast heuristic parsing from slow deliberative update, but does not model the learner’s awareness of its own processing modes.  
Hypothesis generation: 5/10 — The system evaluates given answers; it does not generate new hypotheses or explore alternative explanations beyond the supplied candidates.  
Implementability: 9/10 — Uses only regex, NumPy arrays, and basic graph operations; no external libraries or APIs are required.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
