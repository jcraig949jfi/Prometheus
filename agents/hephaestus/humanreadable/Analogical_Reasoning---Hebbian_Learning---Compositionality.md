# Analogical Reasoning + Hebbian Learning + Compositionality

**Fields**: Cognitive Science, Neuroscience, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T01:39:01.491926
**Report Generated**: 2026-04-02T04:20:11.712040

---

## Nous Analysis

**Algorithm – Hebbian‑Weighted Analogical Structure Matcher (HWASM)**  

1. **Parsing (Compositionality)**  
   - Tokenise the prompt and each candidate answer with `str.split()` and simple regex‑based POS hints (e.g., words ending in “‑ed” or “‑ing” → verb; prepositions from a fixed list).  
   - Extract **subject‑predicate‑object (SPO) triples** using a rule‑based chunker:  
     *NP* + *verb* + *NP* → (subj, pred, obj).  
     Special rules capture:  
     - Negations (`not`, `no`) → attach a `neg` flag to the predicate.  
     - Comparatives (`more than`, `less than`, `as … as`) → predicate `cmp` with direction.  
     - Conditionals (`if … then …`) → two triples linked by a `cond` edge.  
     - Causal markers (`because`, `leads to`, `results in`) → predicate `cause`.  
     - Ordering (`before`, `after`, `while`) → predicate `ord`.  
     - Numbers & units → tokenised as a separate entity type `NUM`.  
   - Store each triple as a directed edge in a **labeled multigraph**: `graph = {pred: {(subj, obj): weight}}`.  
   - Nodes are entity strings; edges keep a **Hebbian weight** (float) and a flag set (neg, cmp, etc.).

2. **Hebbian Learning (Weight Update)**  
   - Initialise all edge weights to 0.  
   - For each triple *t* in the prompt graph, increment its weight: `w[t] += η` (η = 0.1).  
   - For every pair of triples *t₁*, *t₂* that share **any argument** (subject or object), increase the weight of the **predicate‑predicate co‑occurrence**: `w_pred[p₁,p₂] += η`.  
   - These weights capture how often relational patterns fire together in the prompt, mimicking activity‑dependent strengthening.

3. **Analogical Reasoning (Structure Mapping)**  
   - To score a candidate, compute a **maximum‑weight bipartite match** between prompt edges and candidate edges:  
     *Left side* = prompt edges, *Right side* = candidate edges.  
     Edge‑match score = `w_prompt[e] * w_candidate[e'] * δ(type_match, flag_match)`, where `δ` is 1 if predicate type and all flags (neg, cmp, etc.) are identical, else 0.  
   - Solve the assignment with a simple greedy algorithm (sort matches by score descending, pick if both nodes unused) – sufficient for demo and uses only `numpy` for sorting.  
   - Final score = sum of selected match scores divided by total prompt weight (normalises to [0,1]).  
   - Higher scores indicate that the candidate preserves the prompt’s relational structure weighted by Hebbian co‑activation.

**Structural Features Parsed** – negations, comparatives, conditionals, causal claims, ordering relations, numeric quantities, quantifiers (via regex on “all”, “some”, “none”), and plural/singular agreement.

**Novelty** – Purely symbolic analogical mapping has been explored (e.g., structure‑mapping theory, predicate‑graph matching). Hebbian‑style weight updates over co‑occurring predicates are rare in deterministic NLP tools; most systems use static similarity metrics or neural embeddings. Combining the three yields a novel, fully rule‑based scorer that can be implemented with only `numpy` and the stdlib.

**Ratings**  
Reasoning: 7/10 — captures relational transfer and dynamic weighting, but limited by shallow parsing.  
Metacognition: 5/10 — no explicit self‑monitoring or confidence calibration beyond the raw score.  
Hypothesis generation: 6/10 — can propose analogical mappings, yet lacks generative recombination beyond observed triples.  
Implementability: 8/10 — relies on deterministic regex, graph operations, and a greedy matching algorithm; all feasible with numpy and stdlib.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
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
