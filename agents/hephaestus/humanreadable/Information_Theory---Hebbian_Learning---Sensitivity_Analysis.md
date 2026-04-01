# Information Theory + Hebbian Learning + Sensitivity Analysis

**Fields**: Mathematics, Neuroscience, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T16:36:30.092739
**Report Generated**: 2026-03-31T18:05:52.494537

---

## Nous Analysis

**Algorithm: Information‑Hebbian Sensitivity Scorer (IHSS)**  

1. **Parsing & feature extraction** – Using only the Python `re` module we extract a fixed set of logical predicates from each sentence:  
   * atomic propositions (noun phrases),  
   * negations (`not`, `no`),  
   * comparatives (`>`, `<`, `more than`, `less than`),  
   * conditionals (`if … then …`, `unless`),  
   * causal markers (`because`, `due to`, `leads to`),  
   * ordering relations (`before`, `after`, `first`, `last`).  
   Each predicate gets a unique integer ID; a sentence is represented as a binary vector **x** ∈ {0,1}^P where P is the predicate vocabulary size.

2. **Hebbian co‑occurrence matrix** – Over the whole prompt (premise + all candidate answers) we update a symmetric weight matrix **W** ∈ ℝ^{P×P} with a simple Hebbian rule: for every pair of predicates (i,j) that co‑occur in the same sentence,  
   `W[i,j] ← W[i,j] + η` (η = 0.01). No decay is applied; after processing the prompt **W** encodes how often concepts fire together.

3. **Information‑theoretic similarity** – Treat the premise vector **x₀** and a candidate vector **xₖ** as samples from a joint binary distribution estimated by counting co‑occurrences across the prompt:  
   * p(i) = (∑_s x_s[i]) / S,  
   * p(i,j) = (∑_s x_s[i]·x_s[j]) / S, where S is the number of sentences.  
   Mutual information I(x₀;xₖ) = ∑_{i,j} p(i,j) log [p(i,j)/(p(i)p(j))] is computed with `numpy.log` and `numpy.sum`. This quantifies how much knowing the premise reduces uncertainty about the candidate.

4. **Sensitivity analysis** – For each candidate we generate a set of perturbed versions **xₖ′** by applying elementary syntactic flips (negation toggle, comparative reversal, causal direction swap). For each perturbation we recompute MI, obtaining a set {Iₖ′}. Sensitivity Sₖ = std(Iₖ′) (standard deviation). Low Sₖ means the score is robust to small linguistic changes.

5. **Final score** –  
   `scoreₖ = I(x₀;xₖ) * (1 + α·pathₖ) / (1 + β·Sₖ)`  
   where `pathₖ = max_{i,j} W[i,j]` over premise‑active i and answer‑active j (the strongest Hebbian link), and α,β are small constants (e.g., 0.1) to keep the terms in a comparable range. The score is higher when the candidate shares information with the premise, is strongly linked via Hebbian co‑occurrence, and varies little under perturbations.

**Structural features parsed** – negations, comparatives, conditionals, causal markers, ordering/temporal relations, and atomic noun‑phrase predicates. These are the exact symbols the regex extracts and feeds into the binary vectors.

**Novelty** – The combination is not a direct replica of existing work. Pure information‑theoretic scoring appears in lexical similarity metrics (e.g., mutual information–based word similarity), and Hebbian weighting is used in associative memory models, but jointly updating a co‑occurrence matrix from a single prompt and then using it to gate an MI‑based similarity while explicitly measuring sensitivity to syntactic perturbations is novel in the context of answer‑scoring engines. It aligns with recent neuro‑symbolic hybrids that bind statistical association (Hebbian) with information‑theoretic relevance, yet it remains fully implementable with numpy and the stdlib.

**Ratings**  
Reasoning: 8/10 — The algorithm captures logical overlap, reinforces it with learned co‑occurrence, and penalizes brittleness, giving a nuanced reasoning score.  
Metacognition: 6/10 — It provides a single scalar confidence but offers no explicit self‑monitoring of why a candidate failed beyond variance; limited reflective depth.  
Hypothesis generation: 5/10 — The method scores existing candidates; it does not propose new answers, though the Hebbian path could be used to generate hypotheses in an extension.  
Implementability: 9/10 — All steps use regex, numpy arrays, and basic arithmetic; no external libraries or APIs are required, making it straightforward to code and run.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Information Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Hebbian Learning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Hebbian Learning + Information Theory: strong positive synergy (+0.444). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Information Theory + Emergence + Hebbian Learning (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T18:03:40.467594

---

## Code

*No code was produced for this combination.*
