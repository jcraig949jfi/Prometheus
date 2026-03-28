# Predictive Coding + Free Energy Principle + Metamorphic Testing

**Fields**: Cognitive Science, Theoretical Neuroscience, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T12:49:06.442486
**Report Generated**: 2026-03-27T16:08:16.441670

---

## Nous Analysis

**Algorithm: Hierarchical Prediction‑Error Scoring with Metamorphic Constraints (HPES‑MC)**  

1. **Parsing & Data Structures**  
   - Tokenise the prompt and each candidate answer with `str.split()` and simple POS‑like tags via regex (e.g., `\bnot\b` for negation, `\b(?:if|then)\b` for conditionals, `\b(?:more|less|greater|smaller)\b` for comparatives, `\d+(?:\.\d+)?` for numbers, `\b(?:because|since|due to)\b` for causal cues).  
   - Build a directed graph `G = (V, E)` where each node `v` encodes a propositional atom (e.g., “X > Y”, “¬P”, “value = 5”). Edges represent logical relations extracted from the prompt:  
     * **Comparative edges** (`X > Y`) stored with weight `w = 1`.  
     * **Conditional edges** (`if A then B`) stored as implication `A → B`.  
     * **Causal edges** (`A because B`) stored as `B → A`.  
   - Maintain a numpy array `ε` of prediction‑error values, one per node, initialised to 0.

2. **Predictive Coding Pass (Free Energy Minimisation)**  
   - For each node, compute a *top‑down prediction* as the logical consequence of its parent nodes using simple rule tables:  
     * If parent is `A → B` and parent’s truth = 1, predict child = 1.  
     * If parent is `¬A`, predict child = 1‑parent truth.  
     * For comparatives, propagate numeric bounds (e.g., from `X > Y` and known `Y = 3` predict `X ≥ 4`).  
   - Prediction error `ε_v = |observed_v – predicted_v|` where `observed_v` is 1 if the candidate answer contains the atom, else 0.  
   - Update node truths via gradient‑free descent: `truth_v ← truth_v – α * ε_v` clipped to `[0,1]` (α = 0.2). Iterate until total free energy `F = Σ ε_v²` change < 1e‑3 or max 10 iterations.

3. **Metamorphic Constraint Checking**  
   - Define metamorphic relations (MRs) derived from the prompt:  
     * **Duplication MR**: if answer contains `P`, then duplicated answer should contain `P` twice → score penalty if violated.  
     * **Ordering MR**: for a chain `X > Y > Z`, any answer must preserve transitive order; violations add `δ = 1` to `F`.  
   - After each coding pass, compute MR violations and add to free energy.

4. **Scoring**  
   - Final score for a candidate = `exp(-F)`. Lower free energy (better prediction + MR compliance) yields higher score, bounded in (0,1].  
   - All operations use only `numpy` for array math and `re`/`str` for parsing; no external models.

**Structural Features Parsed**  
Negations (`not`, `no`), conditionals (`if…then`), comparatives (`greater than`, `less than`), numeric values, causal markers (`because`, `due to`), and ordering chains (`X > Y > Z`). These are extracted as graph nodes/edges and used directly in prediction and MR steps.

**Novelty**  
The combination mirrors variational free‑energy minimization (Friston) with predictive coding hierarchies, but replaces neural variational densities with discrete logical nodes and uses metamorphic testing as hard constraints on output relations. While each component exists separately, their tight integration into a deterministic, regex‑based scoring engine has not been described in the literature to my knowledge.

**Rating**  
Reasoning: 8/10 — captures logical inference and numeric bounds via constraint propagation.  
Metacognition: 6/10 — free‑energy term offers a rudimentary self‑monitoring of prediction error, but lacks higher‑level reflection on strategy.  
Hypothesis generation: 5/10 — MRs generate alternative output expectations, yet the system does not propose new hypotheses beyond those encoded.  
Implementability: 9/10 — relies solely on regex, numpy arrays, and simple iterative updates; straightforward to code in <150 lines.

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
