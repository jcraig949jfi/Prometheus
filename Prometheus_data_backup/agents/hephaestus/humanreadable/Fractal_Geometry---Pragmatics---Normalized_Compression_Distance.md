# Fractal Geometry + Pragmatics + Normalized Compression Distance

**Fields**: Mathematics, Linguistics, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T14:31:51.645957
**Report Generated**: 2026-03-31T14:34:56.096002

---

## Nous Analysis

**Algorithm**  
1. **Parsing & clause extraction** – Use a handful of regex patterns to split the input text into elementary clauses (e.g., “if … then …”, “X is greater than Y”, “not Z”, numeric expressions). Each clause becomes a node; edges are added when two clauses share a variable or appear consecutively, yielding a directed clause‑graph *G*. Store *G* as a NumPy adjacency matrix *A* (shape *n×n*).  
2. **Fractal self‑similarity** – Apply a box‑counting scheme on *A*: for scales *s = 1,2,4,8,…* (powers of two) compute the number of boxes *N(s)* needed to cover all non‑zero entries (a box is an *s×s* sub‑matrix; count it if any entry ≠0). Fit log *N(s)* vs log (1/s) with NumPy’s `polyfit` to obtain the estimated Hausdorff dimension *D*. The fractal similarity between candidate *c* and reference *r* is *S_f = exp(−|D_c−D_r|)*.  
3. **Normalized Compression Distance (NCD)** – Concatenate the raw UTF‑8 bytes of candidate and reference strings. Compute *C(x)=len(zlib.compress(x))*, *C(y)*, *C(xy)*, *C(yx)*. NCD = (C(xy)−min(C(x),C(y))) / max(C(x),C(y)). Similarity from compression is *S_n = 1−NCD*.  
4. **Pragmatic feature score** – From the clause list extract binary features: presence of negation, comparative, conditional, causal cue (“because”, “therefore”), numeric value, ordering relation (“more than”, “less than”). Count how many of Grice’s maxims are violated:  
   - *Quantity*: answer too short/long relative to reference (token count ratio outside [0.8,1.2]).  
   - *Quality*: presence of unverifiable claims (detected via lack of supporting numeric or causal clause).  
   - *Relevance*: Jaccard similarity of clause‑type sets <0.3.  
   - *Manner*: average clause length >2× reference (obscurity).  
   Each violated maxim subtracts 0.2 from a base pragmatic score *S_p∈[0,1]*.  
5. **Final scoring** – Combine: *Score = 0.4·S_n + 0.3·S_f + 0.3·S_p*. All operations use only NumPy (matrix ops, polyfit) and the Python standard library (regex, zlib).

**Structural features parsed**  
Negations (“not”, “no”), comparatives (“greater than”, “less than”), conditionals (“if … then …”), causal claims (“because”, “therefore”), numeric values (integers/decimals), ordering relations (“more than”, “fewer than”), and explicit speech‑act markers (“I assert”, “I suggest”). These are captured by the regex‑based clause extractor and fed into the pragmatic feature vector.

**Novelty**  
The trio has not been jointly used in public NLP scoring tools. NCD appears in similarity‑based baselines, fractal dimension has been applied to time‑series and images but rarely to syntactic graphs, and pragmatics is usually handled via neural models. Combining a graph‑based fractal estimate with compression‑based NCD and rule‑based pragmatic checks is therefore novel for pure‑algorithmic reasoning evaluation.

**Ratings**  
Reasoning: 7/10 — captures logical structure via clause graphs and compression similarity, but lacks deep inference chaining.  
Metacognition: 5/10 — provides self‑assessment (fractal dimension, maxim violations) yet offers limited reflection on its own uncertainty.  
Hypothesis generation: 4/10 — mainly scores given candidates; does not propose new answers beyond re‑ranking.  
Implementability: 9/10 — relies solely on regex, NumPy, and zlib; all components are straightforward to code and run offline.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 9/10 |
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
