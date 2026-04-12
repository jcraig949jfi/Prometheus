# Active Inference + Cognitive Load Theory + Normalized Compression Distance

**Fields**: Cognitive Science, Cognitive Science, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T19:35:29.021319
**Report Generated**: 2026-03-27T04:25:55.897089

---

## Nous Analysis

**Algorithm**  
1. **Parse** the prompt `P` and each candidate answer `Aᵢ` with a fixed set of regexes to extract atomic propositions:  
   - *Entity* (`\b[A-Z][a-z]+\b`)  
   - *Predicate* (`\b(is|are|was|were|has|have|does|did)\b`)  
   - *Negation* (`\bnot\b|\bn’t\b`)  
   - *Comparative* (`\bmore|less|greater|smaller|>|<\b`)  
   - *Conditional* (`\bif\b.*\bthen\b|\bunless\b`)  
   - *Causal* (`\bbecause\b|\bdue to\b|\b leads to\b`)  
   - *Numeric* (`\b\d+(\.\d+)?\b`)  
   - *Ordering* (`\bbefore\b|\bafter\b|\bfirst\b|\blast\b`)  

   Each proposition becomes a node in a directed labeled graph `G(P)`; edges encode relations (e.g., `A ->[greater] B`).  

2. **Constraint propagation**:  
   - Apply transitivity on `greater/less` and `before/after` edges (Floyd‑Warshall on the adjacency matrix using numpy).  
   - Apply modus ponens on conditional edges: if `if X then Y` and `X` is asserted, add `Y`.  
   - Detect contradictions (both `P` and `¬P` present) → assign infinite surprise.  

3. **Compute surprise** using Normalized Compression Distance (NCD) as a Kolmogorov‑complexity proxy:  
   - `C(x) = len(zlib.compress(x.encode()))`  
   - `NCD(P,A) = (C(P+A) - min(C(P),C(A))) / max(C(P),C(A))`  
   - Surprise `S = NCD(P,A)`. Lower `S` means the answer compresses well with the prompt (high expected accuracy).  

4. **Cognitive‑load penalties** (intrinsic, extraneous, germane):  
   - *Intrinsic load* `Lᵢ = |unique propositions in G(P)|` (working‑memory demand).  
   - *Extraneous load* `Lₑ = count of tokens in A that do not map to any proposition in G(P)` (irrelevant info).  
   - *Germane load* `L_g = number of newly inferred propositions after propagation that are present in A` (relevant schema construction).  
   - Load score `L = Lᵢ + λₑ·Lₑ - λg·L_g` (λ’s set to 0.5 to penalize extraneous and reward germane).  

5. **Expected free energy approximation**:  
   - `F = S + α·L` (α = 0.2 weights load against surprise).  
   - Final answer score `= -F` (lower free energy → higher score).  
   - Choose the candidate with maximal score.  

**Structural features parsed** – negations, comparatives, conditionals, numeric values, causal claims, ordering relations (before/after, first/last).  

**Novelty** – NCD‑based similarity is well‑known; cognitive‑load quantification appears in tutoring systems; active‑inference approximations have been used in predictive‑coding models. Jointly using compression‑derived surprise, load‑aware penalties, and logical constraint propagation in a single scoring function has not, to my knowledge, been combined in a pure‑numpy, rule‑based tool, making the combination novel for reasoning‑answer evaluation.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and uncertainty but relies on heuristic weighting.  
Metacognition: 6/10 — load terms approximate self‑monitoring yet lack explicit belief updates.  
Hypothesis generation: 5/10 — generates inferred propositions via propagation but does not explore alternative hypotheses.  
Implementability: 9/10 — only regex, numpy, and zlib; straightforward to code and run offline.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Active Inference**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Cognitive Load Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Normalized Compression Distance**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Active Inference + Epistemology + Network Science (accuracy: 0%, calibration: 0%)
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Active Inference + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
