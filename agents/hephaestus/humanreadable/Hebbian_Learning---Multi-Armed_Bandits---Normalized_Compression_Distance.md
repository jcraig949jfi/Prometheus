# Hebbian Learning + Multi-Armed Bandits + Normalized Compression Distance

**Fields**: Neuroscience, Game Theory, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T01:54:46.094112
**Report Generated**: 2026-03-31T14:34:55.658585

---

## Nous Analysis

**Algorithm**  
We maintain a set of candidate answers \(A=\{a_1,…,a_k\}\). For each candidate we store two arrays: a weight \(w_i\) (Hebbian trace) and a pull count \(n_i\) (bandit statistic). The total number of pulls \(T=\sum_i n_i\) is also tracked.  

1. **Similarity computation** – For the prompt \(p\) and each candidate \(a_i\) we compute the Normalized Compression Distance using a standard lossless compressor (e.g., zlib):  
   \[
   \text{NCD}(p,a_i)=\frac{C(p\Vert a_i)-\min\{C(p),C(a_i)\}}{\max\{C(p),C(a_i)\}},
   \]  
   where \(C(x)\) is the byte length of the compressed string and \(p\Vert a_i\) is the concatenation. Lower NCD indicates higher semantic similarity.  

2. **Arm selection (Multi‑Armed Bandit)** – At each scoring round we choose the candidate with the highest Upper Confidence Bound:  
   \[
   i^* = \arg\max_i \Bigl( w_i + \sqrt{\frac{2\ln T}{n_i}} \Bigr).
   \]  
   The exploration term encourages trying poorly sampled answers; the exploitation term favours candidates with high Hebbian weight.  

3. **Structural reward generation** – From the prompt we extract logical propositions using regex patterns for:  
   - Negations (“not”, “no”, “never”)  
   - Comparatives (“greater than”, “<”, “>”, “less than”)  
   - Conditionals (“if … then”, “unless”)  
   - Causal claims (“because”, “leads to”, “results in”)  
   - Ordering/temporal relations (“before”, “after”, “first”, “last”)  
   - Numeric values (integers, decimals).  
   These propositions are turned into nodes in a constraint graph; edges represent relations (e.g., \(X>Y\)). Constraint propagation (transitivity of > and <, modus ponens for conditionals) derives a set of implied truths.  

   For the selected candidate \(a_{i^*}\) we parse it with the same regexes, ground its propositions to the graph, and compute a reward \(r\in[0,1]\) as the fraction of its propositions that are satisfied by the propagated constraints (0 = violation, 1 = full consistency).  

4. **Hebbian weight update** – The weight of the chosen arm is updated with a Hebbian‑style rule that correlates similarity and reward:  
   \[
   \Delta w_{i^*} = \eta \cdot (1-\text{NCD}(p,a_{i^*})) \cdot r,
   \]  
   \[
   w_{i^*} \leftarrow w_{i^*} + \Delta w_{i^*},
   \]  
   where \(\eta\) is a small learning rate (e.g., 0.1). The pull count \(n_{i^*}\) is incremented, and \(T\) updated.  

The final score for any candidate after sufficient rounds is its weight \(w_i\); higher weights reflect answers that are both structurally consistent with the prompt and have repeatedly shown high compression‑based similarity when selected.

**Structural features parsed**  
Negations, comparatives, conditionals, causal claims, ordering/temporal relations, and numeric literals. These are extracted via regex, converted to propositional nodes, and used for constraint propagation to evaluate candidate consistency.

**Novelty**  
Pure NCD‑based similarity has been used for clustering and plagiarism detection; Multi‑Armed Bandits guide exploration in recommendation and reinforcement learning; Hebbian updates model synaptic plasticity in neural networks. Combining NCD similarity as the correlation signal for a Hebbian update, while using a bandit to allocate trials among candidate answers, is not found in existing literature for reasoning‑question scoring. Thus the approach is novel, though it builds on well‑studied components.

**Rating**  
Reasoning: 7/10 — The method captures logical consistency via constraint propagation and rewards similarity, but relies on shallow regex parsing and lacks deep semantic reasoning.  
Metacognition: 5/10 — No explicit self‑monitoring or uncertainty estimation beyond the bandit’s exploration term; limited reflective capability.  
Hypothesis generation: 6/10 — The bandit encourages trying diverse candidates, yet hypothesis generation is implicit and not guided by generative mechanisms.  
Implementability: 9/10 — Uses only numpy (for array ops) and the standard library (zlib, regex, math); all steps are straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
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
