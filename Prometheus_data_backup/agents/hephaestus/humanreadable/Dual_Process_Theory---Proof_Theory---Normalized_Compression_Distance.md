# Dual Process Theory + Proof Theory + Normalized Compression Distance

**Fields**: Cognitive Science, Mathematics, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T01:04:58.569727
**Report Generated**: 2026-03-27T04:25:51.198524

---

## Nous Analysis

**Algorithm**  
1. **Parsing (System 1 fast path)** – Use a handful of regex patterns to extract atomic propositions \(p_i\) from prompt and each candidate answer. Patterns capture:  
   - literals (e.g., “the cat is on the mat”)  
   - negations (`not`, `no`)  
   - comparatives (`>`, `<`, `≥`, `≤`, `equals`)  
   - conditionals (`if … then …`, `unless`)  
   - causal markers (`because`, `leads to`, `results in`)  
   - ordering (`before`, `after`, `first`, `last`)  
   - numeric tokens with units.  
   Each proposition is stored as a normalized string; the set of propositions for a text \(T\) is \(P_T\).  

2. **Graph construction (Proof‑Theoretic core)** – Build a directed implication graph \(G=(V,E)\) where \(V = P_{prompt}\cup P_{candidate}\). For every extracted conditional “if A then B” add edge \(A\rightarrow B\); for causal markers add the same direction; for comparatives derive ordering edges (e.g., “X > Y” → \(X\rightarrow Y\) with a weight 1). Negations are stored as a separate set \(N_T\).  

3. **Proof normalization (System 2 deliberate path)** – Compute the transitive closure of \(G\) using Floyd‑Warshall on a boolean adjacency matrix (implemented with NumPy). This yields the derived proposition set \(D_T\) (all propositions reachable via modus ponens). Apply cut‑elimination by removing any edge \(u\rightarrow v\) if there exists an alternative path \(u\rightsquigarrow v\) of length ≥ 2 (i.e., the edge is redundant). The remaining edge set defines a normalized proof net.  

4. **Similarity via Normalized Compression Distance** – Serialize the sorted lists \(D_{prompt}\) and \(D_{candidate}\) as plain text, concatenate them with a separator, and compress with `zlib` (available in the stdlib). Let \(C(x)\) be the compressed length. NCD is  
\[
\text{NCD} = \frac{C(xy)-\min(C(x),C(y))}{\max(C(x),C(y))}.
\]  
A low NCD indicates high structural similarity.  

5. **Dual‑Process scoring** –  
   - **System 1 score**: token‑level Jaccard similarity between raw proposition sets \(P_{prompt}\) and \(P_{candidate}\) (computed with NumPy).  
   - **System 2 score**: \(S_2 = \lambda_1\,(1-\text{NCD}) + \lambda_2\,\frac{|D_{prompt}\cap D_{candidate}|}{|D_{prompt}\cup D_{candidate}|}\) (consistency of derived proofs).  
   - Final score: \(S = \omega\,S_1 + (1-\omega)\,S_2\) with \(\omega=0.4\) (empirically favoring deliberate reasoning).  

**Structural features parsed** – literals, negations, comparatives, conditionals, causal claims, temporal ordering, numeric values/units.  

**Novelty** – While proof‑theoretic closure, compression‑based similarity, and dual‑process heuristics each appear separately, their integration—using a normalized proof net as the input to NCD and combining it with a fast token heuristic—has not been reported in existing literature.  

Reasoning: 7/10 — captures logical inference via proof closure but limited to surface‑level propositional extraction.  
Metacognition: 5/10 — provides two distinct scores but no explicit self‑monitoring of confidence beyond the weighted blend.  
Hypothesis generation: 4/10 — focuses on scoring given candidates; does not generate new answers.  
Implementability: 8/10 — relies only on regex, NumPy matrix ops, and stdlib compression; straightforward to code.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Dual Process Theory**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Proof Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Normalized Compression Distance**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Proof Theory + Constraint Satisfaction + Normalized Compression Distance (accuracy: 0%, calibration: 0%)
- Chaos Theory + Self-Organized Criticality + Normalized Compression Distance (accuracy: 0%, calibration: 0%)
- Ergodic Theory + Measure Theory + Dual Process Theory (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
