# Constraint Satisfaction + Normalized Compression Distance + Metamorphic Testing

**Fields**: Computer Science, Information Science, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T21:24:49.414204
**Report Generated**: 2026-03-31T20:00:10.414573

---

## Nous Analysis

**Algorithm**  
We build a lightweight reasoner that treats each candidate answer as a set of *atomic propositions* extracted from the text (e.g., “X > Y”, “¬P”, “if A then B”). Each proposition becomes a variable in a Constraint Satisfaction Problem (CSP) whose domain is {True, False}.  

1. **Parsing & Variable Creation** – Using regex patterns we capture:  
   * numeric comparisons (`\d+\s*[<>]=?\s*\d+`) → variables `cmp_ij`  
   * negations (`not\s+\w+`, `\bno\b`) → variables `neg_k` with constraint `neg_k ⇔ ¬base_k`  
   * conditionals (`if\s+.*then\s+.*`) → variables `cond_l` with constraint `cond_l ⇔ (antecedent → consequent)`  
   * ordering relations (`before`, `after`, `greater than`) → variables `ord_m` with transitivity constraints.  

   Each distinct proposition gets an integer ID; we store them in a list `props` and a dict `id→string`.

2. **Constraint Generation** – For every extracted proposition we add unit clauses reflecting its polarity (positive → variable = True, negative → variable = False). For conditionals we add two binary constraints: `(antecedent = True) ⇒ (consequent = True)` and its contrapositive. For ordering we add transitivity constraints: if `A < B` and `B < C` then `A < C`. All constraints are stored as tuples `(scope, function)` where `scope` is a tuple of variable IDs and `function` returns a bool given an assignment.

3. **Arc Consistency (AC‑3)** – We enforce AC‑3 using only Python lists and a deque; no external solver. If a domain becomes empty, the candidate is inconsistent and receives a low base score.

4. **Metamorphic Relations (MRs)** – We define a small MR set:  
   * **Input‑Doubling** – If a numeric variable appears, we create a mutated copy where all numbers are multiplied by 2 and re‑run AC‑3; the answer should retain the same truth value for ordering constraints.  
   * **Negation‑Flip** – Flip the polarity of every negation variable and check that the solution flips accordingly.  
   Violations add a penalty proportional to the number of failed MRs.

5. **Normalized Compression Distance (NCD) Tie‑breaker** – For candidates that survive CSP+MR with equal consistency, we compute NCD between the original prompt and each candidate using `zlib.compress` (standard library). NCD = (C(xy) – min(C(x),C(y))) / max(C(x),C(y)). Lower NCD → higher similarity to the prompt’s logical structure, yielding a final score:  
   `score = consistency_weight * (1 – inconsistency_ratio) – mr_penalty_weight * mr_violations – ncd_weight * NCD`.

**Parsed Structural Features**  
Negations, comparatives (`>`, `<`, `≥`, `≤`), conditionals (`if…then`), numeric values, ordering relations (`before/after`, `greater/less`), and logical connectives implicit in the CSP (AND via joint constraints, OR via alternative encodings).

**Novelty**  
The combination is not a direct replica of prior work. CSP solvers and NCD have been used separately for text similarity; metamorphic testing is mainly in software engineering. Integrating AC‑3‑based consistency checking with MR‑based robustness checks and an NCD tie‑breaker for logical similarity is novel in the context of lightweight, neural‑free answer scoring.

**Ratings**  
Reasoning: 8/10 — The algorithm captures deductive structure via CSP and MRs, providing genuine logical scoring beyond surface similarity.  
Metacognition: 6/10 — It can detect when its own constraints fail (inconsistency) but lacks explicit self‑reflection on uncertainty sources.  
Hypothesis generation: 5/10 — MRs generate limited mutants (doubling, negation flip); richer hypothesis space would need more sophisticated generators.  
Implementability: 9/10 — All components use only regex, Python lists/dicts, deque, and zlib; no external libraries or neural models are required.

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

**Forge Timestamp**: 2026-03-31T20:00:06.260710

---

## Code

*No code was produced for this combination.*
