# Free Energy Principle + Model Checking + Normalized Compression Distance

**Fields**: Theoretical Neuroscience, Formal Methods, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-29T00:33:51.416952
**Report Generated**: 2026-03-31T19:15:02.950536

---

## Nous Analysis

The algorithm builds a lightweight symbolic model of the prompt and scores each candidate answer by jointly evaluating (1) how well the answer satisfies extracted logical constraints (model checking), (2) how surprising the answer is given the prompt (variational free‑energy approximation), and (3) how compressible the answer‑prompt pair is (Normalized Compression Distance).  

**Data structures**  
- `Clause`: tuple `(pred, subj, obj, polarity, modality)` where `modality ∈ {assertion, conditional, causal, comparative, numeric}`.  
- `ConstraintGraph`: adjacency list where nodes are variable assignments (e.g., `X=5`) and edges represent allowed transitions derived from conditionals (`if A then B`) and causal links (`A → B`).  
- `Bitmask`: length‑`N` integer indicating which constraints are satisfied for a given world state.  

**Operations**  
1. **Parsing** – Regexes extract:  
   - Negations (`\bnot\b`, `\bno\b`) → flip polarity.  
   - Comparatives (`>`, `<`, `>=`, `<=`, `=`) → numeric constraints.  
   - Conditionals (`if .* then .*`) → implication edges.  
   - Causals (`because`, `leads to`, `causes`) → directed edges with weight 1.  
   - Quantifiers (`all`, `some`) → universal/existential guards.  
   - Temporal markers (`before`, `after`, `first`, `last`) → ordering constraints.  
2. **Model checking** – Construct a finite‑state automaton from the constraint graph. For each candidate, ground its propositions (replace variables with concrete values/noun phrases) and run a BFS/DFS to see if a path exists that satisfies all asserted clauses; the proportion of satisfied clauses yields `sat_score ∈ [0,1]`.  
3. **Free‑energy / surprise** – Approximate variational free energy as prediction error: `FE = NCD(prompt, answer)`.  
4. **NCD** – Compute using zlib (stdlib): `NCD(x,y) = (C(xy) - min(C(x),C(y))) / max(C(x),C(y))`, where `C` is compressed length.  
5. **Scoring** – `score = w1·sat_score - w2·FE`, with `w1,w2` tuned to keep the score in a usable range (e.g., `w1=1.0, w2=0.5`). Higher scores mean the answer is both logically consistent and less surprising.  

**Structural features parsed** – negations, comparatives, conditionals, causal claims, numeric values, ordering relations (before/after, first/last), and quantifiers.  

**Novelty** – While each component (compression‑based similarity, model checking, free‑energy principle) appears separately in the literature, their tight integration into a single, numpy‑only scoring pipeline for reasoning QA has not been reported; prior work uses them in isolation or with neural back‑ends, making this combination novel.  

Reasoning: 7/10 — captures logical structure and surprise but lacks deep temporal or probabilistic reasoning.  
Metacognition: 5/10 — provides a single scalar confidence; no explicit self‑monitoring or uncertainty decomposition.  
Hypothesis generation: 6/10 — can generate candidates that satisfy constraints via graph search, but creativity is limited to closed‑world completions.  
Implementability: 8/10 — relies only on regex, zlib, numpy for weighted sums, and standard data structures; straightforward to code.

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

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T19:14:55.854024

---

## Code

*No code was produced for this combination.*
