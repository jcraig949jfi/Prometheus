# Matched Filtering + Normalized Compression Distance + Metamorphic Testing

**Fields**: Signal Processing, Information Science, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T01:24:39.405749
**Report Generated**: 2026-03-31T14:34:55.590586

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage** – Using only the Python `re` module we extract a set of logical tuples from each text:  
   - `(neg, predicate)` for negations (`not …`)  
   - `(comp, lhs, op, rhs)` for comparatives (`>`, `<`, `=`, `≥`, `≤`)  
   - `(cond, antecedent, consequent)` for conditionals (`if … then …`)  
   - `(cause, cause, effect)` for causal cues (`because`, `leads to`, `results in`)  
   - `(order, before, after)` for temporal/ordering cues (`before`, `after`, `precedes`)  
   - `(num, value, unit)` for numeric expressions.  
   Each tuple type gets a fixed index; we build a binary feature vector **f** ∈ {0,1}^K (K = number of distinct tuple types) and a parallel numeric vector **n** for extracted numbers (scaled to [0,1] by min‑max across the corpus). The final feature representation is **x** = [f; n] (numpy array).

2. **Matched‑filter similarity** – Treat the reference answer’s feature vector **x_ref** as a template. Compute the normalized cross‑correlation (dot product)  
   \[
   s_{\text{MF}} = \frac{x_{\text{cand}} \cdot x_{\text{ref}}}{\|x_{\text{cand}}\|\,\|x_{\text{ref}}\|}
   \]
   using `numpy.dot` and `numpy.linalg.norm`. This yields a value in [−1,1]; we shift to [0,1] by \((s_{\text{MF}}+1)/2\).

3. **Normalized Compression Distance (NCD)** – Concatenate the raw strings of the candidate and reference answers, compress each with `zlib.compress`, and compute  
   \[
   \text{NCD}(a,b)=\frac{C(ab)-\min(C(a),C(b))}{\max(C(a),C(b))}
   \]
   where \(C(\cdot)\) is the length in bytes. Convert to similarity: \(s_{\text{NCD}} = 1 - \text{NCD}\).

4. **Metamorphic‑test penalty** – Define a small set of metamorphic relations on the input text (e.g., swapping two conjuncts, double‑negating a predicate, multiplying a numeric value by 2). For each relation we compute the expected change in the matched‑filter score (monotonic increase/decrease or invariance). If the observed change violates the expectation, we subtract a fixed penalty \(p\) (e.g., 0.1) from the final score.

5. **Final score** –  
   \[
   \text{Score}= w_{\text{MF}}\,s_{\text{MF}} + w_{\text{NCD}}\,s_{\text{NCD}} - \sum_{\text{violations}} p
   \]
   with weights \(w_{\text{MF}}=0.6\), \(w_{\text{NCD}}=0.4\) (tuned on a validation set). All operations use only `numpy` and the Python standard library.

**Structural features parsed**  
Negations, comparatives, conditionals, causal claims, ordering/temporal relations, numeric values with units, and simple conjunctive structures. These are captured directly as the tuple types above.

**Novelty**  
While NCD and matched filtering each appear in similarity‑search literature, and metamorphic testing is well‑known in software engineering, their joint use to score reasoning answers — especially the metamorphic penalty that enforces predictable score changes under controlled input mutations — has not been reported in existing work. The combination is therefore novel.

**Rating**  
Reasoning: 7/10 — The algorithm captures explicit logical structure and uses a signal‑processing similarity measure, but it does not perform deep inference or handle implicit knowledge.  
Metacognition: 5/10 — Metamorphic relations provide a rudimentary self‑check, yet the tool lacks higher‑order reflection on its own uncertainty.  
Hypothesis generation: 4/10 — It generates few new hypotheses; mainly it validates or penalizes existing candidates against preset relations.  
Implementability: 8/10 — All steps rely on regex, numpy linear algebra, and zlib compression, which are readily available in the standard environment.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 8/10 |
| **Composite** | **5.33** |

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
