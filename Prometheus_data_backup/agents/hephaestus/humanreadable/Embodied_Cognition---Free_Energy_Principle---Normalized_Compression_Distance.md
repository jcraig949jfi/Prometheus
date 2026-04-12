# Embodied Cognition + Free Energy Principle + Normalized Compression Distance

**Fields**: Cognitive Science, Theoretical Neuroscience, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T06:51:10.589752
**Report Generated**: 2026-04-01T20:30:43.697121

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage** – Apply a fixed set of regex patterns to the prompt and each candidate answer to extract a list of *grounded propositions* P = {(s, r, o, pol)} where *s* and *o* are noun phrases (including detected numbers), *r* is a relation verb or preposition, and *pol*∈{+1,‑1} encodes negation (e.g., “not”, “no”). Patterns cover:  
   - Negations: `\b(not|no|never)\b`  
   - Comparatives: `\b(more|less|greater|fewer|higher|lower|>\s*\d+|<\s*\d+)\b`  
   - Conditionals: `\bif\s+.+?\bthen\b`  
   - Causal: `\b(because|due to|leads to|results in|causes)\b`  
   - Ordering: `\b(before|after|first|last|previous|next)\b`  
   - Numerics: `\d+(\.\d+)?`  
   Each match yields a triple; the polarity flag is flipped if a negation token appears within a window of three tokens left of the relation.  

2. **Constraint graph** – Build a directed multigraph G = (V, E) where V are unique noun‑phrase strings and each proposition adds an edge (s → o) labeled with r and pol. Store edges in adjacency dict: `adj[s][o] = list of (r, pol)`.  

3. **Compression‑based surprise** – Serialize G to a canonical string: sort V, then for each s in sorted order output `s:` followed with edges sorted by (o, r, pol). Join with `|`. Apply `zlib.compress` (standard library) to obtain byte length L(G).  

4. **Scoring** – For each candidate answer A, compute its graph Gₐ and its compressed length Lₐ. Compute the joint compression L₍ₚ,ₐ₎ by concatenating the two serializations with a separator and compressing again. Normalized Compression Distance:  
   `NCD = (L₍ₚ,ₐ₎ - min(Lₚ, Lₐ)) / max(Lₚ, Lₐ)`.  
   Lower NCD means the answer predicts the prompt better (smaller surprise). Convert to a score: `score = 1 - NCD` (clipped to [0,1]).  

**Parsed structural features** – negations, comparatives, conditionals, causal claims, ordering relations, explicit numeric values, quantifier cues (“all”, “some”, “none”), and modal likelihoods (“must”, “might”).  

**Novelty** – While NCD for text similarity and logical‑form extraction for QA exist separately, jointly using a compression‑based free‑energy proxy on a parsed constraint graph has not been described in the literature; the combination is therefore novel.  

**Ratings**  
Reasoning: 6/10 — captures relational structure but lacks deep inference (e.g., multi‑step chaining).  
Metacognition: 4/10 — no explicit self‑monitoring or uncertainty estimation beyond compression length.  
Hypothesis generation: 5/10 — can propose alternatives by perturbing edges, but generation is rudimentary.  
Implementability: 8/10 — relies only on regex, dicts, lists, and zlib; straightforward to code in <150 lines.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 6/10 |
| Metacognition | 4/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
| **Composite** | **5.0** |

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
