# Matched Filtering + Criticality + Type Theory

**Fields**: Signal Processing, Complex Systems, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T11:26:22.933253
**Report Generated**: 2026-03-31T17:31:45.970522

---

## Nous Analysis

**Algorithm**  
We build a *Typed Matched‑Filter Criticality Scorer* (TMFCS).  
1. **Parsing → Typed Feature Vectors** – Using only the stdlib (`re`, `ast`), we extract a set of atomic predicates from the prompt and each candidate answer:  
   - Predicates are tuples `(type, polarity, args)` where `type` ∈ {`Negation`, `Comparative`, `Conditional`, `Numeric`, `Causal`, `Order`}.  
   - `polarity` is +1 for affirmative, –1 for negated.  
   - `args` are either constants (numbers, entity strings) or variable placeholders.  
   Each distinct predicate gets an index in a dictionary; the presence/absence (weighted by polarity) forms a sparse binary vector **x** ∈ ℝⁿ.  
2. **Matched Filter** – We pre‑compute a *reference signal* **s** from a small set of expert‑provided gold answers (averaged vectors). The matched‑filter output for a candidate is the normalized cross‑correlation:  
   \[
   y = \frac{{\bf s}^\top {\bf x}}{\|{\bf s}\|\|{\bf x}\|}
   \]  
   Implemented with `numpy.dot` and `numpy.linalg.norm`. This yields a similarity score that is maximal when the candidate’s predicate pattern aligns with the gold pattern.  
3. **Criticality Modulation** – To reward answers that lie near the decision boundary (i.e., where small changes in predicate presence flip the score), we compute the susceptibility‑like term:  
   \[
   c = 1 - \exp\!\bigl(-\alpha \, \|{\bf x} - {\bf s}\|_2^2\bigr)
   \]  
   with α a small constant (e.g., 0.5). The final score is `score = y * c`. High scores require both strong alignment (matched filter) and proximity to the critical region where the system is most sensitive to logical differences.  
4. **Type Theory Guard** – Before scoring, we verify type consistency: each predicate’s `type` must match the expected type signature derived from the prompt (e.g., a `Conditional` must have antecedent and consequent of compatible sorts). Violations zero‑out the score. This uses a simple lookup table of allowed type combinations, enforceable with pure Python.

**Structural Features Parsed**  
Negations (`not`, `no`), comparatives (`greater than`, `less than`, `more`), conditionals (`if … then …`, `unless`), numeric values (integers, decimals, fractions), causal claims (`because`, `leads to`, `results in`), ordering relations (`before`, `after`, `precedes`, `follows`). Each maps to a predicate type with polarity.

**Novelty**  
Matched‑filter scoring of logical forms is uncommon; most similarity metrics use bag‑of‑words or embeddings. Adding a criticality term mirrors physics‑inspired sensitivity analysis rarely seen in NLP. Type‑theoretic guarding resembles dependent‑type program synthesizers but applied to lightweight predicate vectors. The triple combination is not documented in existing surveys, making it novel in this concrete form.

**Ratings**  
Reasoning: 8/10 — captures logical structure and sensitivity to subtle mismatches.  
Metacognition: 6/10 — limited self‑monitoring; relies on fixed α and reference set.  
Hypothesis generation: 5/10 — excels at scoring given hypotheses but does not propose new ones.  
Implementability: 9/10 — uses only regex, numpy, and stdlib; straightforward to code.

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

**Forge Timestamp**: 2026-03-31T17:30:55.946048

---

## Code

*No code was produced for this combination.*
