# Pragmatics + Metamorphic Testing + Sensitivity Analysis

**Fields**: Linguistics, Software Engineering, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T15:22:21.506775
**Report Generated**: 2026-03-27T04:25:54.325466

---

## Nous Analysis

**Algorithm: Pragmatic‑Metamorphic Sensitivity Scorer (PMSS)**  

1. **Parsing & Data Structures**  
   - Tokenize the prompt and each candidate answer with a simple regex‑based splitter that preserves punctuation.  
   - Build a directed labeled graph **G = (V, E)** where each node *v* ∈ V is a *semantic atom*:  
        * numeric literal (int/float),  
        * entity phrase (noun chunk),  
        * predicate (verb + its arguments),  
        * modal/negation marker,  
        * comparative/superlative token,  
        * conditional connective (“if”, “then”, “unless”).  
   - Edges *e = (v_i, r, v_j)* encode syntactic‑semantic relations extracted via a small set of hand‑crafted patterns (e.g., “X is greater than Y” → edge with relation **gt**, “X causes Y” → **cause**, “not X” → **neg** attached to X).  
   - Store each graph as an adjacency list of dictionaries for O(1) edge lookup.

2. **Metamorphic Relations (MRs)**  
   - Define a taxonomy of MRs that operate on the graph:  
        * **Input‑Doubling MR**: multiply every numeric node value by 2; expect all **gt/lt** edges to preserve direction, and any **sum**‑type predicate to double.  
        * **Order‑Preserving MR**: permute entity nodes that appear only in symmetric predicates (e.g., “X and Y are friends”) and verify that the truth value of the answer does not change.  
        * **Negation‑Flip MR**: insert or remove a **neg** edge on a predicate node; the answer’s truth value should invert if the predicate is asserted, stay unchanged if it is merely presupposed.  
   - For each candidate answer, generate its graph **Gₐ**, apply each MR to produce a transformed graph **Gₐ′**, and compute a binary satisfaction score *sᵢ = 1* if the answer’s truth‑value prediction (derived from a simple rule‑based evaluator on the graph) respects the MR, else 0.

3. **Sensitivity Analysis Layer**  
   - Perturb numeric nodes by adding Gaussian noise 𝒩(0, σ²) with σ = 0.05·|value| (5 % relative).  
   - Re‑evaluate the answer under each perturbation; compute the variance *Var* of the binary satisfaction scores across *K = 20* samples.  
   - Define sensitivity penalty *p = 1 – exp(-Var)* (higher variance → larger penalty).

4. **Scoring Logic**  
   - Base score *B = (1/|MR|) Σ sᵢ* (average MR satisfaction).  
   - Final score *S = B · (1 – p)*.  
   - Scores lie in [0,1]; higher values indicate answers that are pragmatically coherent (respect implicatures via negation‑flip MRs), structurally stable under metamorphic transformations, and numerically robust.

**Structural Features Parsed**  
- Numerics and arithmetic relations (gt, lt, eq, sum, diff).  
- Entities and their symmetric vs. asymmetric predicates.  
- Negation scope (via **neg** edges).  
- Comparative/superlative constructions.  
- Conditionals and causal claims (→, cause, enable).  
- Quantifiers (“all”, “some”, “none”) treated as modal nodes.

**Novelty**  
The triple fusion is not explicitly documented: pragmatics supplies the negation‑flip MR; metamorphic testing provides the systematic relation‑based oracle‑free checks; sensitivity analysis adds a numeric robustness penalty. While each component appears separately in testing, NLP robustness, and pragmatic interpretation literature, their joint use in a graph‑based scoring engine for answer evaluation is, to the best of my knowledge, unexplored.

---

Reasoning: 7/10 — captures logical structure and pragmatic implicature via MRs, but relies on hand‑crafted patterns that may miss nuanced language.  
Metacognition: 6/10 — the scorer can reflect on its own sensitivity (variance penalty) yet lacks higher‑order self‑debugging loops.  
Hypothesis generation: 5/10 — generates alternative graphs through MRs, but does not propose new hypotheses beyond those encoded in the MR taxonomy.  
Implementability: 8/10 — uses only regex, numpy for noise, and stdlib data structures; straightforward to code and test.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Metamorphic Testing**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 


Similar combinations that forged successfully:
- Active Inference + Pragmatics + Property-Based Testing (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Category Theory + Embodied Cognition + Pragmatics (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
