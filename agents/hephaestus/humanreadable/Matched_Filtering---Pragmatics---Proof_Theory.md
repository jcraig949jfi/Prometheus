# Matched Filtering + Pragmatics + Proof Theory

**Fields**: Signal Processing, Linguistics, Mathematics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T08:27:16.575160
**Report Generated**: 2026-04-01T20:30:43.790117

---

## Nous Analysis

**Algorithm**  
1. **Parse** each prompt and candidate answer into a directed labeled graph \(G=(V,E)\) where vertices are atomic propositions (predicates with arguments) and edges encode logical relations extracted by regex‑based patterns: negation (¬), conditional (→), biconditional (↔), comparative (> , <, =), causal (because →), ordering (before/after), and numeric constraints (≤,≥,=). Each vertex carries a feature vector \(f(v)=[type, polarity, numeric\_value, arity]\) encoded as a one‑hot for type (±1 for polarity) and a float for any extracted number.  
2. **Template construction** – from the reference answer (or a set of gold proofs) build a *matched‑filter template* \(T\) as the adjacency matrix \(A_T\) flattened into a vector \(t\in\mathbb{R}^{d}\) (where \(d=|V_T|^2\)).  
3. **Cross‑correlation scoring** – for each candidate, flatten its adjacency matrix \(A_C\) to vector \(c\) and compute the normalized cross‑correlation  
\[
s_{\text{MF}} = \frac{(c-\mu_c)\cdot(t-\mu_t)}{\|c-\mu_c\|\,\|t-\mu_t\|}
\]  
using only NumPy. This yields a similarity score maximized when the candidate’s relational structure aligns with the template (matched filtering).  
4. **Pragmatic penalty** – evaluate Grice‑style maxims on the candidate graph:  
   *Quantity*: penalize extra vertices not implied by the prompt (|V_C|‑|V_P|₊).  
   *Quality*: penalize vertices with contradictory polarity (both p and ¬p present).  
   *Relation*: penalize edges whose label does not appear in any shortest path between prompt‑derived premises and conclusion vertices.  
   Sum these penalties into \(s_{\text{Prag}}\in[0,1]\).  
5. **Proof‑theoretic validity** – run a lightweight cut‑elimination check: iteratively apply modus ponens and transitivity rules on the graph; if a contradiction (p∧¬p) is derivable, set \(s_{\text{Proof}}=0\); otherwise \(s_{\text{Proof}}=1\).  
6. **Final score** –  
\[
\text{Score}= w_1\,s_{\text{MF}} + w_2\,(1-s_{\text{Prag}}) + w_3\,s_{\text{Proof}}
\]  
with weights summing to 1 (e.g., 0.5,0.3,0.2). All operations use NumPy arrays and Python sets/dicts; no external libraries.

**Structural features parsed** – negations, conditionals/biconditionals, comparatives, causal clauses, ordering/temporal relations, numeric equality/inequality, and conjunctive/disjunctive conjunctions.

**Novelty** – The approach fuses three well‑studied ideas: matched‑filter detection from signal processing, pragmatic maxim analysis from linguistics, and cut‑elimination from proof theory. While each component appears separately in entailment systems (e.g., logistic regression over syntactic features, pragmatic heuristics in dialogue, theorem provers for logical validity), their exact combination — using cross‑correlation of graph‑based adjacency vectors as a filtered similarity metric, jointly constrained by pragmatic and proof‑theoretic checks — has not been reported in the literature, making it novel for a pure‑numpy, rule‑based evaluator.

**Ratings**  
Reasoning: 8/10 — captures logical structure and validity, but relies on hand‑crafted regex patterns that may miss complex constructions.  
Metacognition: 6/10 — includes pragmatic self‑checks (quantity, quality, relation) yet lacks explicit monitoring of uncertainty or alternative parse strategies.  
Hypothesis generation: 5/10 — generates a single scored candidate; no mechanism to propose multiple alternative proofs or interpretations.  
Implementability: 9/10 — uses only NumPy and stdlib; graph construction, cross‑correlation, and rule application are straightforward to code in <200 lines.

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
