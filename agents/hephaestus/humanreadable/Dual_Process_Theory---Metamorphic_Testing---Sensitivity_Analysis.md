# Dual Process Theory + Metamorphic Testing + Sensitivity Analysis

**Fields**: Cognitive Science, Software Engineering, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T18:24:49.339766
**Report Generated**: 2026-04-01T20:30:44.120110

---

## Nous Analysis

**Algorithm: Dual‑Process Metamorphic Sensitivity Scorer (DPMSS)**  

*Data structures*  
- **PromptParse**: a list of atomic propositions extracted from the prompt using regex‑based patterns (e.g., “X > Y”, “if A then B”, “not C”, numeric literals). Each proposition is stored as a tuple `(type, args)` where `type` ∈ {`comparison`, `conditional`, `negation`, `causal`, `ordering`} and `args` are the referenced entities or values.  
- **AnswerHypotheses**: for each candidate answer, a parallel list of propositions derived the same way.  
- **MetamorphicRelations (MR)**: a predefined set of binary relations over answer sets, e.g.,  
  1. **ScaleInvar**: multiplying all numeric values in the answer by a constant k leaves ordering propositions unchanged.  
  2. **NegFlip**: inserting a double negation leaves truth value unchanged.  
  3. **MonotoneInc**: if a premise “A → B” is present, then strengthening A (e.g., replacing “A ≥ 5” with “A ≥ 7”) cannot invalidate B.  
- **SensitivityMatrix**: a NumPy array `S` of shape `(n_answers, n_MR)` where `S[i,j]` measures the degree to which answer *i* violates MR *j* (0 = satisfied, 1 = fully violated).  

*Operations*  
1. **Parsing** – Apply a fixed set of regexes to prompt and each answer to fill `PromptParse` and each `AnswerHypotheses`.  
2. **Constraint Propagation** – Build a directed graph from conditional and causal propositions; run a depth‑first propagation to derive implied facts (modus ponens, transitivity). Store derived facts in a set `Derived`.  
3. **Metamorphic Evaluation** – For each MR, instantiate it on the answer’s proposition set (e.g., apply ScaleInvar by scaling all numeric args, then re‑run parsing and propagation). Compute violation as the proportion of derived facts that change truth value relative to the original answer. Populate `S`.  
4. **Dual‑Process Scoring** –  
   - **System 1 (fast)**: compute a baseline similarity score `sim_i` = Jaccard index between `PromptParse` and `AnswerHypotheses_i` (pure set overlap).  
   - **System 2 (slow)**: compute a robustness penalty `pen_i` = mean_j `S[i,j]` (average MR violation).  
   - Final score: `score_i = sim_i * (1 - pen_i)`. Scores lie in [0,1]; higher indicates answers that are both superficially aligned and robust under metamorphic perturbations.  

*Structural features parsed*  
- Comparatives (`>`, `<`, `≥`, `≤`, `=`), ordering chains, numeric literals and arithmetic expressions, negations (`not`, `no`, `-`), conditionals (`if…then…`, `unless`), causal verbs (`causes`, `leads to`, `results in`), and conjunctive/disjunctive connectives.  

*Novelty*  
The triple blend is not present in existing surveys: Dual Process Theory informs a two‑tier scoring (fast similarity + slow robustness), Metamorphic Testing supplies the perturbation‑based robustness metrics, and Sensitivity Analysis formalizes the quantification of output change under those perturbations. While each component appears separately in program analysis, software testing, and cognitive modeling, their joint use as a scoring engine for reasoning answers is undocumented.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and robustness, but relies on hand‑crafted MRs that may miss domain‑specific nuances.  
Metacognition: 7/10 — the dual‑process split mirrors self‑monitoring, yet the model does not explicitly reason about its own uncertainty beyond the penalty term.  
Hypothesis generation: 6/10 — generates implied facts via propagation, but does not propose alternative hypotheses beyond those entailed by the prompt.  
Implementability: 9/10 — uses only regex, NumPy arrays, and standard‑library data structures; no external dependencies.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: unproductive
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
