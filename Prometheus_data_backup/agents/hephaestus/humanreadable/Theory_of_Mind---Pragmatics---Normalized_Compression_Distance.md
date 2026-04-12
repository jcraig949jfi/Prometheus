# Theory of Mind + Pragmatics + Normalized Compression Distance

**Fields**: Cognitive Science, Linguistics, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T13:19:16.714816
**Report Generated**: 2026-03-27T05:13:38.172082

---

## Nous Analysis

**Algorithm: Pragmatic‑Theory‑of‑Mind NCD Scorer (PTM‑NCD)**  

1. **Pre‑processing & Structural Parsing**  
   - Input: a *prompt* P (the question or scenario) and a list of *candidate answers* {A₁…Aₙ}.  
   - Use only the Python `re` module to extract a set of logical primitives from P and each Aᵢ:  
     *Negations* (`not`, `no`, `never`), *comparatives* (`more`, `less`, `>`, `<`), *conditionals* (`if … then`, `unless`), *causal cues* (`because`, `since`, `leads to`), *ordering relations* (`before`, `after`, `first`, `last`), and *numeric tokens* (integers, floats).  
   - Each primitive is stored as a tuple `(type, span, polarity)` in a list `struct(P)` and `struct(Aᵢ)`.  
   - Build a directed constraint graph G where nodes are primitives and edges represent inferred relations (e.g., transitivity of ordering, modus ponens from conditionals).  

2. **Theory‑of‑Mind Layer**  
   - Model two agents: Speaker (S) who produced P and Listener (L) who must choose an answer.  
   - For each candidate Aᵢ, compute a *belief matrix* Bᵢ ∈ ℝ^{k×k} (k = number of distinct entities in P) where Bᵢ[e₁,e₂] = 1 if S believes that relation R(e₁,e₂) holds according to struct(P), else 0.  
   - Update Bᵢ by propagating constraints through G (using NumPy matrix multiplication and thresholding) to infer implicit beliefs that S would attribute to L.  
   - The *mental‑fit* score MFᵢ = 1 – (‖Bᵢ – B̂‖₁ / (2·k²)), where B̂ is the belief matrix derived from struct(Aᵢ) (what the answer asserts). Higher MFᵢ means the answer aligns with S’s inferred beliefs about L’s knowledge.  

3. **Pragmatics Layer (Grice‑based penalties)**  
   - For each Aᵢ, check violations of the four maxims using simple regex‑based heuristics:  
     *Quantity*: penalize if answer adds >15 % extra primitives not entailed by P.  
     *Quality*: penalize if answer contains a negation of a primitive marked as asserted in P without a modal cue (`might`, `could`).  
     *Relation*: penalize if answer introduces a primitive type absent from P (e.g., introduces a causal cue when P only contains comparatives).  
     *Manner*: penalize if answer length > 2·|P| or contains ambiguous pronouns without antecedent.  
   - Sum the weighted violations to obtain a pragmatics penalty PPᵢ ∈ [0,1].  

4. **Normalized Compression Distance Core**  
   - Concatenate P and each Aᵢ with a separator `#`.  
   - Compute compressed lengths using Python’s `zlib` (available in stdlib) as an approximation of Kolmogorov complexity:  
     C(x) = len(zlib.compress(x.encode())).  
   - NCD(P,Aᵢ) = (C(P#Aᵢ) – min(C(P),C(Aᵢ))) / max(C(P),C(Aᵢ)).  
   - Lower NCD indicates higher algorithmic similarity.  

5. **Final Score**  
   - Combine the three components:  
     Scoreᵢ = α·(1 – NCD(P,Aᵢ)) + β·MFᵢ – γ·PPᵢ, with α+β+γ = 1 (e.g., α=0.4, β=0.4, γ=0.2).  
   - Rank candidates by Scoreᵢ; the highest is selected.  

**Structural Features Parsed**  
Negations, comparatives, conditionals, causal markers, temporal/ordering relations, numeric quantities, and entity mentions. These feed the constraint graph and the belief matrix.

**Novelty**  
The fusion of a compression‑based similarity metric with explicit Theory‑of‑Mind belief modeling and Grice‑maxim pragmatics is not present in existing NCD‑based text similarity tools (which are purely statistical) nor in standard logical‑reasoning solvers (which lack a pragmatic penalty layer). While each component has precedents, their joint use in a single scoring function is novel.

**Rating**  
Reasoning: 7/10 — The algorithm captures logical inference via constraint propagation and belief alignment, but relies on shallow heuristics for deeper reasoning.  
Metacognition: 6/10 — Theory‑of‑Mind component models speaker/listener beliefs, yet it is limited to binary belief matrices and lacks higher‑order recursion.  
Novelty/Hypothesis generation: 5/10 — Combines known ideas in a new way, but does not generate fresh hypotheses beyond re‑ranking existing candidates.  
Implementability: 8/10 — Uses only `re`, `zlib`, and NumPy; all operations are straightforward and runnable in a few dozen lines.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Theory of Mind**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Normalized Compression Distance**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Theory of Mind + Pragmatics + Mechanism Design (accuracy: 0%, calibration: 0%)
- Active Inference + Pragmatics + Property-Based Testing (accuracy: 0%, calibration: 0%)
- Category Theory + Embodied Cognition + Pragmatics (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
