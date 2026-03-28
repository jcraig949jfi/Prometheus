# Fractal Geometry + Pragmatics + Multi-Armed Bandits

**Fields**: Mathematics, Linguistics, Game Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T15:23:39.253129
**Report Generated**: 2026-03-27T16:08:16.953259

---

## Nous Analysis

**Algorithm – Fractal‑Pragmatic Bandit Scorer (FPBS)**  

1. **Parse each prompt and candidate answer into a typed dependency tree** using only regex‑based patterns for the target structural features (see §2).  
   - Node fields: `type` ∈ {neg, comparative, conditional, numeric, causal, order}, `value` (token or number), `children` list.  
   - The tree is stored as an adjacency list `{node_id: (type, value, [child_ids])}`.

2. **Fractal self‑similarity score**  
   - For each tree, enumerate all distinct sub‑trees up to depth `d_max` (e.g., 4).  
   - Let `N(s)` be the number of distinct sub‑trees whose total node count equals scale `s`.  
   - Estimate the Hausdorff‑like dimension:  
     \[
     \hat D = \frac{\log N(s_2) - \log N(s_1)}{\log(1/s_2) - \log(1/s_1)}
     \]  
     using two scales (e.g., `s_1=2`, `s_2=4`).  
   - Compute similarity between prompt tree `T_p` and answer tree `T_a` as  
     \[
     S_{\text{frac}} = 1 - \frac{|\hat D_p - \hat D_a|}{\max(\hat D_p,\hat D_a)}.
     \]

3. **Pragmatic violation penalty/reward**  
   - Scan the answer tree for patterns that violate Grice’s maxims:  
     *Quantity*: missing expected numeric or causal node when present in prompt.  
     *Quality*: presence of a negation paired with an affirmative numeric claim (e.g., “not 5” vs “5”).  
     *Relation*: conditional node without a corresponding cause/effect in prompt.  
     *Manner*: comparative node lacking a clear `-er/than` structure.  
   - Each detected violation adds a weighted penalty `w_i` (empirically set to 0.1).  
   - Pragmatic score:  
     \[
     S_{\text{prag}} = 1 - \sum_i w_i \cdot \text{violation}_i .
     \]

4. **Multi‑Armed Bandit evaluation**  
   - Treat each candidate answer as an arm.  
   - Initial reward for arm `a`:  
     \[
     r_a = \alpha \, S_{\text{frac}}(a) + \beta \, S_{\text{prag}}(a)
     \]  
     with `α=0.6, β=0.4`.  
   - Maintain per‑arm statistics: total pulls `n_a`, cumulative reward `R_a`, mean `\mu_a = R_a/n_a`.  
   - After each evaluation step, update `n_a` and `R_a`.  
   - Compute Upper Confidence Bound (UCB) for ranking:  
     \[
     \text{UCB}_a = \mu_a + c \sqrt{\frac{\log N_{\text{total}}}{n_a}},
     \]  
     where `c=1.0` and `N_{\text{total}} = \sum_a n_a`.  
   - The final score returned for each answer is its current UCB value; higher UCB indicates a more promising answer given both structural fit and pragmatic soundness, while the bandit term encourages exploration of less‑tested candidates.

**Structural features parsed** – negations (`not`, `no`), comparatives (`more`, `less`, `-er`, `than`), conditionals (`if`, `unless`, `provided that`), numeric values (integers, decimals, units), causal claims (`because`, `leads to`, `results in`), ordering relations (`before`, `after`, `first`, `last`, `greater than`, `less than`).

**Novelty** – Prior work uses tree kernels or pragmatic feature vectors in isolation, or bandits for answer selection in dialogue systems. FPBS is the first to combine a fractal‑dimension based self‑similarity measure of parsed logical trees, explicit Grice‑maxim violation detection, and a UCB‑driven bandit loop to iteratively refine answer scores.

**Ratings**  
Reasoning: 7/10 — captures structural similarity and pragmatic soundness but relies on hand‑crafted regex patterns.  
Metacognition: 6/10 — the bandit term provides uncertainty awareness, yet no explicit self‑reflection on parsing errors.  
Hypothesis generation: 8/10 — the UCB mechanism actively proposes less‑explored answers as hypotheses for further evaluation.  
Implementability: 9/10 — all components (regex parsing, tree hashing, simple arithmetic, UCB) use only NumPy and the Python standard library.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

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
