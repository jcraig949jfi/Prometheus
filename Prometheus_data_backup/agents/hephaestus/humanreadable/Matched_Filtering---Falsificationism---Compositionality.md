# Matched Filtering + Falsificationism + Compositionality

**Fields**: Signal Processing, Philosophy, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T11:24:52.486136
**Report Generated**: 2026-03-31T14:34:55.991914

---

## Nous Analysis

**Algorithm**  
We build a lightweight “semantic‑signal” vector for each sentence using only regex‑based extraction and numpy operations.  

1. **Tokenisation & atom extraction** – Using a handful of regex patterns we pull out:  
   * atomic predicates (e.g., “X is Y”, “X > Y”, “if X then Y”)  
   * negation markers (`not`, `no`, `never`)  
   * comparative operators (`>`, `<`, `≥`, `≤`, `more than`, `less than`)  
   * causal/linking cues (`because`, `therefore`, `leads to`)  
   * numeric constants.  
   Each atom is assigned an integer ID; its polarity is +1 for affirmative, –1 for negated.  

2. **Compositional vector construction** – For each extracted triple (subject, relation, object) we create a one‑hot basis vector **eᵢ** (size = vocabulary of atoms). The sentence vector **s** is the weighted sum:  
   `s = Σ wₖ·eₖ` where weight `wₖ = polarityₖ * (1 + α·numeric_valueₖ)` (α is a small scaling factor). This implements Frege’s compositionality: meaning of the whole is the linear combination of its parts.  

3. **Matched‑filter scoring** – Given a prompt **p** we compute its reference vector **r** the same way. For each candidate answer **c** we compute its vector **cᵥ**. The matched‑filter score is the normalized cross‑correlation (dot product)  
   `score = (r·cᵥ) / (‖r‖·‖cᵥ‖)` – maximal when the candidate aligns with the prompt’s signal, i.e., optimal detection of known structure in noise.  

4. **Falsificationist penalty** – We generate the negation of the candidate (by flipping polarity of all extracted atoms) and compute its similarity to the prompt. If the negated version also scores high (above a τ threshold), the candidate is deemed non‑falsifiable (tautological or unfalsifiable) and we subtract a penalty λ·score_neg.  

Final score = matched‑filter score – λ·falsification penalty. All steps use only Python’s `re` module and `numpy` for vector arithmetic.

**Structural features parsed**  
- Negations (`not`, `no`, `never`) → polarity flip.  
- Comparatives (`>`, `<`, `more than`, `less than`) → ordered relation atoms with numeric weighting.  
- Conditionals (`if … then …`) → implication atoms; antecedent and consequent treated as separate clauses.  
- Causal claims (`because`, `therefore`, `leads to`) → directed edge atoms.  
- Numeric values → scalar modifiers on atom weight.  
- Ordering relations (e.g., “X before Y”) → temporal ordering atoms.  

**Novelty**  
The combination is not a direct replica of existing NLP pipelines. While matched filtering is classic in signal processing, applying it to compositional propositional vectors is uncommon. Adding a falsificationism‑based penalty mirrors Popperian demarcation but is rarely implemented in rule‑based scorers. Thus the hybrid is novel, though it shares spirit with semantic‑similarity models and logic‑based theorem provers that use vector‑style embeddings.

**Ratings**  
Reasoning: 7/10 — captures logical structure and signal alignment but lacks deep inference (e.g., multi‑step chaining).  
Metacognition: 5/10 — no explicit self‑monitoring or confidence calibration beyond the falsification penalty.  
Hypothesis generation: 4/10 — extracts and scores existing hypotheses; does not propose new ones.  
Implementability: 9/10 — relies only on regex, numpy, and basic linear algebra; easy to code and run offline.

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
