# Statistical Mechanics + Dual Process Theory + Matched Filtering

**Fields**: Physics, Cognitive Science, Signal Processing
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T22:49:28.817693
**Report Generated**: 2026-04-02T04:20:11.563532

---

## Nous Analysis

**Algorithm**  
1. **Parsing & Feature Extraction** – For each prompt and each candidate answer, run a deterministic regex‑based parser that extracts a set of atomic propositions \(P=\{p_i\}\) where each \(p_i\) is a tuple \((\text{predicate},\text{arg}_1,\text{arg}_2,\dots)\). Predicates cover: negation (`not`), comparatives (`>`, `<`, `=`), conditionals (`if … then …`), causal verbs (`causes`, `leads to`), ordering (`before`, `after`), and numeric literals (integers, floats). The parser also builds a directed graph \(G\) of implied constraints (e.g., transitivity of `<`, modus ponens on conditionals).  
2. **Feature Vector** – Convert \(P\) into a sparse binary vector \(x\in\{0,1\}^d\) where each dimension corresponds to a distinct proposition type (e.g., “X > Y”, “Z causes W”, “value = 3.14”). Numerics are binned into fixed‑width intervals and added as separate dimensions.  
3. **Matched‑Filter Template** – From a small set of gold‑standard answers (or a hand‑crafted template) compute the prototype vector \(t\) by averaging their feature vectors. The matched‑filter score for a candidate is the normalized cross‑correlation  
\[
s_{\text{MF}} = \frac{x\cdot t}{\|x\|\,\|t\|}.
\]  
4. **Statistical‑Mechanics Energy** – Define an energy function that penalizes violated constraints:  
\[
E(x) = \sum_{c\in C} w_c \, \mathbb{I}[c \text{ unsatisfied by } x],
\]  
where \(C\) is the set of constraints extracted from the prompt (e.g., “if A then B”, “X > Y”) and \(w_c\) are hand‑tuned weights. The Boltzmann weight is  
\[
p(x) = \frac{\exp(-\beta E(x))}{Z},\qquad Z=\sum_{x'\in\mathcal{C}} \exp(-\beta E(x')),
\]  
with \(\beta\) controlling the sharpness (System 2 deliberation).  
5. **Dual‑Process Fusion** – System 1 provides a fast heuristic \(s_{\text{MF}}\). System 2 refines it by computing the posterior probability \(p(x)\). The final score is a convex combination  
\[
\text{Score}= \alpha\, s_{\text{MF}} + (1-\alpha)\, p(x),
\]  
with \(\alpha\in[0,1]\) (e.g., 0.3) favoring the slower, constraint‑aware term for harder items.  
All steps use only NumPy for vector ops and Python’s re/itertools for parsing.

**Parsed Structural Features** – Negations, comparatives, conditionals, causal verbs, temporal ordering, numeric values and their units, equality/inequality statements, and existential quantifiers (“some”, “all”).

**Novelty** – The combination mirrors energy‑based models (Markov Logic Networks) but replaces weighted logical formulas with a matched‑filter template and explicitly splits fast similarity scoring from slow constraint‑propagation scoring, a dual‑process twist not seen in standard SRL or neural‑symbolic hybrids.

**Ratings**  
Reasoning: 8/10 — captures logical structure and numeric consistency via constraint‑energy and matched filtering.  
Metacognition: 6/10 — dual‑process split offers a rudimentary self‑monitoring heuristic but lacks true self‑assessment.  
Hypothesis generation: 5/10 — the system evaluates given candidates; it does not propose new answers beyond the supplied set.  
Implementability: 9/10 — relies solely on regex, NumPy linear algebra, and basic graph propagation; no external libraries or training needed.

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
