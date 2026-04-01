# Cognitive Load Theory + Free Energy Principle + Sensitivity Analysis

**Fields**: Cognitive Science, Theoretical Neuroscience, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T11:04:48.488000
**Report Generated**: 2026-03-31T17:10:38.154481

---

## Nous Analysis

**Algorithm**  
We build a deterministic scorer `ReasoningScorer` that works on a parsed logical‑form tree of the question and each candidate answer.  

1. **Parsing → data structure**  
   - Tokenise with regex (`\w+|[^\w\s]`) and build a directed acyclic graph (DAG) where each node is one of:  
     * `Prop` (predicate with args)  
     * `Not`, `And`, `Or`, `Imp` (connectives)  
     * `Quant` (∀, ∃) with bound variable  
     * `Num` (literal or variable) with comparator (`<,>,=,≤,≥`)  
     * `Cause` (edge labelled “causes”)  
   - Store node attributes: `type`, `children`, `payload` (e.g., predicate name, numeric value).  
   - The question DAG (`Q`) and answer DAG (`A`) are kept separate.

2. **Intrinsic load (IL)** – Cognitive Load Theory  
   - `IL = α·depth(Q) + β·branching_factor(Q)` where depth is longest root‑to‑leaf path, branching factor is average number of children.  
   - Higher IL → harder to process → subtract from score.

3. **Extraneous load (EL)**  
   - Count tokens in the answer that do **not** map to any node in `Q` (e.g., filler words, irrelevant adjectives).  
   - `EL = γ·|A \ Q|`.  
   - Penalise directly.

4. **Germane load (GL)**  
   - Count answer nodes that match a `Prop` in `Q` with identical payload (same predicate and args).  
   - `GL = δ·|A ∩ Q|`.  
   - Reward.

5. **Prediction error (PE)** – Free Energy Principle (variational free energy ≈ energy + KL; we drop KL for a point estimate)  
   - Assign a binary truth value to each `Prop` via simple model‑checking on the DAG (true if all literals satisfy the question’s constraints).  
   - Let `t_Q` be the truth of the question’s goal proposition, `t_A` the truth of the answer’s goal proposition.  
   - `PE = ε·(t_Q - t_A)²`.  
   - Minimising PE drives the answer toward the question’s expected truth.

6. **Sensitivity (S)** – Sensitivity Analysis  
   - Generate *k* perturbed versions of the answer DAG by:  
     * flipping a random `Not` node,  
     * adding/subtracting ε to a random `Num` payload,  
     * swapping the direction of a random `Cause` edge.  
   - Re‑compute the base score (IL‑EL‑GL‑PE) for each perturbed copy → vector `s`.  
   - `S = ζ·Var(s)`.  
   - High variance → fragile reasoning → penalise.

7. **Final score**  
   ```
   score = -IL - EL + GL - PE - S
   ```
   (All coefficients α,β,γ,δ,ε,ζ are set to 1.0 for simplicity; they can be tuned on a validation set.)

**Structural features parsed**  
- Negations (`Not`)  
- Comparatives (`<,>,=,≤,≥`) via `Num` nodes  
- Conditionals (`Imp`)  
- Numeric literals and variables (`Num`)  
- Causal claims (`Cause` edges)  
- Ordering relations (chained `<`/`>` through multiple `Num` nodes)  
- Quantifiers (`Quant`) and scoping  

**Novelty**  
Educational scoring systems have used Cognitive Load Theory alone; active‑inference/Free Energy formulations appear in computational neuroscience but rarely in answer‑selection; Sensitivity Analysis is standard for robustness testing of causal models. The concrete combination — using load‑based penalties, a variational‑free‑energy‑style prediction‑error term, and a finite‑difference sensitivity penalty on a parsed logical DAG — has not, to our knowledge, been presented together in a pure‑numpy, rule‑based scorer.

**Ratings**  
Reasoning: 8/10 — captures logical structure, uncertainty, and robustness, though it omits deeper semantic nuance.  
Metacognition: 6/10 — the scorer can report its own load components, giving a rudimentary self‑assessment of difficulty.  
Hypothesis generation: 5/10 — the method evaluates given hypotheses but does not generate new ones.  
Implementability: 9/10 — relies only on regex, basic graph operations, and NumPy for array math; no external libraries or training needed.

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

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T17:10:37.217427

---

## Code

*No code was produced for this combination.*
