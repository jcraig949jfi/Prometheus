# Cognitive Load Theory + Normalized Compression Distance + Sensitivity Analysis

**Fields**: Cognitive Science, Information Science, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T17:35:04.208929
**Report Generated**: 2026-03-31T14:34:57.004081

---

## Nous Analysis

**Algorithm**  
1. **Parsing & proposition extraction** – Using only `re` we scan the prompt and each candidate answer for six structural patterns:  
   - Negations: `\b(not|no|never)\b`  
   - Comparatives: `\b(more|less|greater|smaller|higher|lower)\b.*\bthan\b`  
   - Conditionals: `if.*then\b|\bunless\b|\bprovided that\b`  
   - Numeric values: `\d+(\.\d+)?`  
   - Causal claims: `\b(causes?|leads? to|results? in|because\s+of)\b`  
   - Ordering relations: `\b(before|after|precedes?|follows?)\b`  

   Each match yields a proposition token (e.g., `NEG(p)`, `COMP(a,b)`, `COND(p→q)`, `NUM(v)`, `CAUSE(p→q)`, `ORDER(a<b)`). Propositions are stored as strings in a list `props`.  

2. **Intrinsic load (IL)** – Approximate working‑memory chunks as the size of the minimal proposition set after removing duplicates: `IL = len(set(props))`.  

3. **Extraneous load (XL)** – Count redundant sub‑patterns: for every 2‑gram of propositions we compute a hash (`hash(tuple(pair))`) and tally frequencies; `XL = sum(freq-1 for freq in hash_counts.values() if freq>1)`.  

4. **Germane load via NCD** – Concatenate the reference answer string `R` and candidate string `C`. Compute compressed lengths with `zlib.compress` (standard library): `Cx = len(zlib.compress(R.encode))`, `Cy = len(zlib.compress(C.encode))`, `Cxy = len(zlib.compress((R+'\n'+C).encode))`.  
   Normalized Compression Distance: `NCD = (Cxy - min(Cx,Cy)) / max(Cx,Cy)`. Germane load is taken as `GL = 1 - NCD` (higher when candidate is similar to reference).  

5. **Sensitivity analysis (SA)** – Generate `k=5` perturbed versions of the candidate by randomly inserting, deleting, or substituting a single character (using `random.choice` on the ASCII set). For each perturbed version `C_i` compute `NCD_i`. Sensitivity is the average absolute deviation: `SA = mean(|NCD_i - NCD|)`. Lower SA indicates robustness.  

6. **Score** – Combine the three components with fixed weights (e.g., w₁=0.4, w₂=0.3, w₃=0.2, w₄=0.1):  
   `score = w₁*(1 - IL/IL_max) + w₂*(1 - XL/XL_max) + w₃*GL - w₄*SA`, where `IL_max` and `XL_max` are the maxima observed across all candidates for normalization. The score lies roughly in `[0,1]`; higher means better reasoning quality.

**Structural features parsed** – negations, comparatives, conditionals, numeric literals, causal claims, ordering relations (including transitive chains via later constraint propagation if desired).

**Novelty** – While NCD, cognitive‑load‑inspired weighting, and sensitivity checks each appear separately in plagiarism detection, cognitive‑tutoring systems, and robustness testing, their joint use to produce a single, interpretable reasoning score from purely algorithmic text features has not been reported in the literature. The combination is therefore novel.

**Rating**  
Reasoning: 7/10 — captures logical structure and robustness but relies on superficial proxies for deep semantic understanding.  
Metacognition: 6/10 — provides explicit load estimates that could guide self‑regulation, yet offers no feedback on why a load is high.  
Hypothesis generation: 5/10 — the method evaluates given answers; it does not generate new hypotheses or alternative explanations.  
Implementability: 9/10 — uses only `re`, `zlib`, `numpy` (for averaging) and the Python standard library; no external models or APIs required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.0** |

**Novelty**: unproductive
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
