# Theory of Mind + Matched Filtering + Normalized Compression Distance

**Fields**: Cognitive Science, Signal Processing, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T13:20:10.620211
**Report Generated**: 2026-03-27T16:08:16.463669

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage** – Using a small set of regex patterns we extract propositional triples ⟨s, p, o⟩ from the prompt and each candidate answer. Patterns capture:  
   * Negations (`not`, `never`) → polarity flag.  
   * Comparatives (`greater than`, `less than`, `more … than`) → ordered‑relation predicate.  
   * Conditionals (`if … then …`, `unless`) → implication predicate with antecedent/consequent slots.  
   * Causal claims (`because`, `leads to`, `results in`) → causal predicate.  
   * Numeric values and units → typed literals.  
   * Quantifiers (`all`, `some`, `none`) → scope modifier.  
   Each triple is stored as a dict `{subj, pred, obj, polarity, modality}` where modality ∈ {assertion, belief, desire, intention} inferred from cue verbs (`think`, `want`, `intend`).  

2. **Belief vector construction** – For each text we build a sparse vector **v** over a universal predicate‑argument space (hashed via Python’s built‑in `hash` to stay within std‑lib). The weight of a dimension is:  
   `w = polarity × confidence`, where confidence = 1.0 for assertions, 0.8 for beliefs/desires, 0.6 for intentions (reflecting Theory‑of‑Mind depth).  

3. **Matched‑filter score** – Treat the reference answer’s vector **v_ref** as the known signal and a candidate’s vector **v_cand** as the noisy observation. The optimal linear detector is the normalized cross‑correlation:  
   `MF = (v_ref · v_cand) / (‖v_ref‖‖v_cand‖)`.  
   This maximizes SNR under Gaussian noise assumptions.  

4. **Normalized Compression Distance (NCD)** – Concatenate the ordered list of triples (as strings) for reference and candidate, compress each with `zlib.compress`, and compute:  
   `NCD = (C(xy) - min(C(x),C(y))) / max(C(x),C(y))`, where `C(·)` is compressed length.  
   Similarity contribution is `S_NCD = 1 - NCD`.  

5. **Final score** – `Score = α·MF + β·S_NCD` with α+β=1 (e.g., α=0.6, β=0.4). Higher scores indicate answers that both match the logical structure of the reference (matched filter) and share compressible patterns (NCD), while the belief‑weighted vectors embed Theory‑of‑Mind depth.

**Structural features parsed** – negations, comparatives, conditionals, causal connectives, numeric literals with units, ordering relations, quantifiers, and modal verbs indicating belief/desire/intention.

**Novelty** – The triple‑layer combination (belief‑weighted vectors, matched‑filter detection, and NCD) is not found in existing surveys; related work uses either argument‑mining graphs or pure compression similarity, but none jointly optimizes a detection‑theoretic filter with ToM‑aware weighting and compression‑based similarity.

**Ratings**  
Reasoning: 7/10 — captures logical structure and belief depth, but relies on shallow regex parsing.  
Metacognition: 6/10 — models others’ mental states via modality weighting, yet lacks recursive belief modeling.  
Hypothesis generation: 5/10 — scoring favors similarity to reference; novel answer generation is indirect.  
Implementability: 8/10 — uses only regex, numpy (for dot/norm), zlib, and std‑lib; no external dependencies.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
