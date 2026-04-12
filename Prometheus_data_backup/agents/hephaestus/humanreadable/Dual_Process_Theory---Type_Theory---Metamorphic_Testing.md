# Dual Process Theory + Type Theory + Metamorphic Testing

**Fields**: Cognitive Science, Logic, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T17:12:51.560392
**Report Generated**: 2026-03-31T14:34:56.979080

---

## Nous Analysis

**Algorithm**  
The tool builds a lightweight typed logical representation of both the prompt and each candidate answer, then applies a dual‑process scoring scheme that blends a fast heuristic (System 1) with a slow, constraint‑driven check (System 2) grounded in type theory and metamorphic relations (MRs).

1. **Parsing & Typing (Type Theory)**  
   - Use regex to extract atomic propositions:  
     - Numeric literals → type `Num` with value `float`.  
     - Comparatives (`>`, `<`, `=`) → type `Comp` with fields `left`, `op`, `right`.  
     - Conditionals (`if … then …`) → type `Cond` with `antecedent`, `consequent`.  
     - Negations (`not`, `no`) → flip a Boolean polarity flag on the attached proposition.  
     - Ordering chains (`A < B < C`) → split into binary `Comp` propositions.  
   - Each proposition is stored as a dict `{id, type, value, polarity, deps}` where `deps` lists IDs of propositions it logically depends on (e.g., the antecedent of a conditional). All propositions are placed in two NumPy structured arrays: one for the prompt, one for the candidate.

2. **Fast Heuristic (System 1)**  
   - Compute surface‑level overlap: token Jaccard between prompt and candidate, penalty for mismatched negation count, and a length‑normalization term.  
   - Fast score `S_fast = 1 – (α·neg_penalty + β·(1‑Jaccard))` (α,β tuned to 0.3,0.5).

3. **Slow Constraint Check (System 2)**  
   - **Type Consistency**: For each candidate proposition, verify that its `type` matches the expected type derived from the prompt (e.g., a numeric answer must be `Num`). Violations add to a type‑error count `E_type`.  
   - **Metamorphic Relations**: Define a small MR set derived from the prompt’s structure:  
     - *Doubling MR*: If the prompt contains a numeric input `x`, then replacing `x` with `2·x` in the candidate should double any `Num` output.  
     - *Order‑Invariance MR*: Swapping the order of independent premises (identified via empty `deps`) should leave the truth value unchanged.  
     - *Negation‑Flip MR*: Negating an antecedent in a conditional should flip the polarity of the consequent if the conditional is treated as material implication.  
   - For each MR, evaluate satisfaction using NumPy vectorized checks; count satisfied MRs `M_sat`.  
   - Slow score `S_slow = (M_sat / M_total) * (1 – γ·E_type)` with γ=0.2.

4. **Final Score**  
   `Score = 0.4·S_fast + 0.6·S_slow`.  
   The class exposes `score(prompt, candidate)` returning a float in `[0,1]`.

**Parsed Structural Features**  
Numeric values, comparatives, equality, ordering chains, conditionals (if‑then), negations, causal connectors (“because”, “leads to”), quantifiers (“all”, “some”), and conjunctions/disjunctions.

**Novelty**  
While metamorphic testing and type‑theoretic checking appear separately in software verification and some NLP sanity‑checks, coupling them with a dual‑process framework that explicitly distinguishes fast surface heuristics from slow logical constraint propagation is not present in existing work. No prior system uses MRs derived from prompt structure to guide a type‑aware, constraint‑based scoring function alongside a System 1 heuristic.

**Ratings**  
Reasoning: 7/10 — captures logical consistency and MR satisfaction but relies on shallow regex parsing, limiting deep semantic reasoning.  
Metacognition: 6/10 — provides two distinct scoring streams (fast/slow) yet lacks explicit self‑monitoring or confidence calibration.  
Hypothesis generation: 5/10 — focuses on evaluating given candidates; does not generate new hypotheses or alternative answers.  
Implementability: 8/10 — uses only regex, NumPy, and standard library; all components are straightforward to code and test.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
