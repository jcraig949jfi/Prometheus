# Adaptive Control + Compositionality + Normalized Compression Distance

**Fields**: Control Theory, Linguistics, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T02:10:29.634545
**Report Generated**: 2026-03-31T14:34:55.666585

---

## Nous Analysis

**Algorithm**  
1. **Parsing (Compositionality)** – Use a handful of regex patterns to extract atomic propositions and logical connectives from the prompt and each candidate answer, building a binary‑tree AST. Node types: `NOT`, `AND`, `OR`, `IMPLIES`, `COMPARE`, `NUMBER`, `CAUSE`. Each node stores its children list and a token string.  
2. **Feature vector** – For each AST compute a fixed‑length numpy vector: counts of each node type, depth, and a bag‑of‑tokens of leaf literals (numbers, variable names). This yields a compositional representation that is invariant to re‑ordering of commutative children.  
3. **Similarity via NCD** – Serialize each AST to a canonical bracket string (e.g., `(AND (NOT A) (COMPARE > X 5))`). Compress the string with `zlib` (available in the stdlib) and compute the normalized compression distance:  
   `NCD(x,y) = (C(xy) - min(C(x),C(y))) / max(C(x),C(y))`, where `C` is the compressed length. Lower NCD → higher structural similarity.  
4. **Adaptive Control weighting** – Maintain a scalar weight `w ∈ [0,1]` that blends structural similarity (`sim_struct = 1 - NCD`) and lexical similarity (`sim_lex = cosine` of the feature vectors). Initial `w = 0.5`. After scoring a batch of candidates, if the top‑ranked answer does not match a known correct answer (provided in a tiny validation set), update `w` by a simple rule:  
   - If `sim_struct` correctly separates the right answer while `sim_lex` does not, increase `w` by `η = 0.05`.  
   - Else decrease `w` by `η`.  
   Clip `w` to `[0,1]`. This online update mimics a self‑tuning regulator without gradient computation.  
5. **Score** – `score = w * sim_struct + (1‑w) * sim_lex`. Return candidates sorted by score.

**Structural features parsed** – Negations (`not`, `no`), conjunctions (`and`), disjunctions (`or`), conditionals (`if … then`), biconditionals, comparatives (`>`, `<`, `>=`, `<=`, `=`), ordering relations (`before`, `after`), causal cues (`because`, `leads to`, `results in`), numeric values with units, and quantified expressions (`all`, `some`).

**Novelty** – Pure‑numpy tools that combine NCD‑based structural similarity with an online‑tuned weight for lexical vs. structural cues are rare. Prior work uses either static NCD thresholds or tree‑edit distances; the adaptive weighting layer adds a control‑theoretic feedback loop not seen in existing open‑source reasoning scorers, making the combination modestly novel.

**Ratings**  
Reasoning: 7/10 — The algorithm captures logical structure and adapts to errors, but relies on shallow regex parsing and cannot handle deep quantifier scoping.  
Metacognition: 5/10 — Weight update provides basic self‑monitoring, yet no explicit uncertainty estimation or strategy revision beyond the scalar weight.  
Hypothesis generation: 4/10 — The method scores given candidates; it does not propose new answers or rewrite premises.  
Implementability: 8/10 — Only `re`, `zlib`, and `numpy` are needed; the AST construction and NCD computation are straightforward to code in <150 lines.

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
