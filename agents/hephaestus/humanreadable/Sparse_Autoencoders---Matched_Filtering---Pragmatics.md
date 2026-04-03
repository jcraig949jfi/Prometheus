# Sparse Autoencoders + Matched Filtering + Pragmatics

**Fields**: Computer Science, Signal Processing, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T05:54:36.316600
**Report Generated**: 2026-04-02T08:39:55.129856

---

## Nous Analysis

**Algorithm**  
1. **Feature extraction** – Parse each sentence with a lightweight regex‑based dependency extractor that yields a set of atomic predicates:  
   - *Entity* (noun phrase) → `E_i`  
   - *Relation* (verb + preposition) → `R_j(E_a, E_b)`  
   - *Modifier* (negation, comparative, quantifier) → flags attached to the predicate.  
   The output is a binary sparse vector **x** ∈ {0,1}^D where each dimension corresponds to a distinct predicate‑modifier tuple (e.g., `¬R_k(E1,E2)`, `R_l(E3,E4) > 5`). D is the size of a learned dictionary.

2. **Sparse Autoencoder dictionary** – Using only NumPy, run a few iterations of iterative soft‑thresholding algorithm (ISTA) on a corpus of training questions to learn an overcomplete dictionary **W** ∈ ℝ^{D×K} (K > D) that minimizes ‖x – Wz‖₂² + λ‖z‖₁. The latent code **z** is a sparse representation of the logical structure. Store **W** and the λ used.

3. **Matched‑filter scoring** – For a candidate answer **a**, compute its sparse code **z_a** via the same ISTA step (fixed **W**, λ). The matched filter output is the normalized cross‑correlation:  
   `s = (z_q · z_a) / (‖z_q‖₂ ‖z_a‖₂)`, where **z_q** is the code of the question. This maximizes the signal‑to‑noise ratio between question and answer logical patterns.

4. **Pragmatic weighting** – Apply a heuristic context vector **p** derived from Gricean maxims:  
   - *Quantity*: penalize answers with extra unsupported predicates (‖z_a‖₀ – ‖z_q‖₀).  
   - *Quality*: down‑weight predicates marked with negation or uncertainty flags.  
   - *Relation*: boost scores for causal or conditional predicates that appear in both question and answer.  
   Final score = s × exp(−α·‖z_a‖₀) × ∏_{k∈prag} w_k, where w_k are pre‑set weights (e.g., 0.8 for negation, 1.2 for causal match).

**Structural features parsed** – negations (`not`, `no`), comparatives (`more than`, `less than`), conditionals (`if … then`), numeric values and units, causal verbs (`cause`, `lead to`), ordering relations (`before`, `after`), and quantifiers (`all`, `some`, `none`).

**Novelty** – The pipeline combines three well‑studied ideas: sparse coding for dictionary learning (e.g., Olshausen & Field 1997; applied to text by Huang et al. 2013), matched‑filter detection (borrowed from radar/sonar signal processing), and pragmatics‑inspired weighting (similar to heuristic scoring in logic‑based QA like Heilman & Smith 2010). No prior work fuses all three in a single NumPy‑only scoring function, making the combination novel in this constrained setting.

**Ratings**  
Reasoning: 7/10 — captures logical structure via sparse codes and cross‑correlation, but limited by shallow regex parsing.  
Metacognition: 5/10 — includes simple uncertainty and quantity penalties; no explicit self‑monitoring or uncertainty estimation.  
Hypothesis generation: 4/10 — generates no new hypotheses; only scores given candidates.  
Implementability: 8/10 — relies solely on NumPy and std‑lib; ISTA and regex parsing are straightforward to code.

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
