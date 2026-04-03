# Hebbian Learning + Maximum Entropy + Normalized Compression Distance

**Fields**: Neuroscience, Statistical Physics, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T19:46:36.236701
**Report Generated**: 2026-04-01T20:30:44.152106

---

## Nous Analysis

**Algorithm**  
1. **Feature extraction** – For each prompt *P* and candidate answer *A* we run a deterministic regex pass that extracts binary structural atoms:  
   - Predicate‑argument tuples (e.g., `X causes Y`) with polarity (negated/affirmed).  
   - Comparative relations (`X > Y`, `X is more than Y`).  
   - Conditional antecedent/consequent (`if X then Y`).  
   - Causal links (`because X, Y`).  
   - Numeric constants and their units.  
   - Ordering/temporal markers (`before`, `after`, `first`, `second`).  
   Each atom is hashed to a fixed‑length index (e.g., modulo 1024) yielding a sparse binary vector **f**∈{0,1}^D for the prompt and **g**∈{0,1}^D for the candidate.  

2. **Hebbian weighting** – Initialise a weight matrix **W**∈ℝ^{D×D} with zeros. For every (prompt, candidate) pair we update  
   ```
   W ← W + α * (f ⊗ g)          # outer product, α∈(0,1] learning rate
   ```  
   After processing all candidates, the Hebbian‑derived prompt‑specific vector is  
   ```
   h = W @ f          # matrix‑vector product (numpy)
   ```  
   The Hebbian similarity score for a candidate is `s_heb = h · g`.  

3. **Maximum‑Entropy (log‑linear) scoring** – Treat **h** as the natural‑parameter vector θ of an exponential family over candidates. The unnormalized log‑probability is simply the linear form  
   ```
   s_me = θ · g = s_heb
   ```  
   (Because the partition function is constant across candidates for ranking, we keep the linear term.)  

4. **Normalized Compression Distance (NCD)** – Compute  
   ```
   C(x) = len(zlib.compress(x.encode()))
   NCD(P,A) = (C(P+A) - min(C(P),C(A))) / max(C(P),C(A))
   ```  
   Lower NCD indicates higher algorithmic similarity.  

5. **Final score** – Combine the two terms with a trade‑off λ:  
   ```
   Score(A) = s_me - λ * NCD(P,A)
   ```  
   Candidates are ranked by descending Score. All operations use only numpy (for vectors/matrix) and the stdlib (zlib, re).

**Structural features parsed** – negations, comparatives, conditionals, causal claims, numeric values with units, ordering/temporal relations, quantifiers, and modal operators. Each yields a distinct atom in the feature vector.

**Novelty** – While Hebbian co‑occurrence, MaxEnt log‑linear models, and compression‑based similarity have each been used separately, their explicit integration—Hebbian‑derived weights feeding a MaxEnt scorer that is corrected by NCD—does not appear in existing literature. The closest analogues are holographic reduced representations or vector‑space models augmented with compression distances, but the joint learning‑update step is new.

**Ratings**  
Reasoning: 7/10 — captures logical structure and uncertainty via principled weighting, but lacks deeper inference chaining.  
Metacognition: 5/10 — the method evaluates its own confidence indirectly through the MaxEnt partition term, yet no explicit self‑monitoring loop.  
Hypothesis generation: 4/10 — scoring favors candidates similar to the prompt; generating novel hypotheses beyond recombination is weak.  
Implementability: 9/10 — relies only on regex, numpy, and zlib; all components are straightforward to code and run offline.

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
