# Sparse Autoencoders + Compositionality + Sensitivity Analysis

**Fields**: Computer Science, Linguistics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T16:12:04.550246
**Report Generated**: 2026-03-31T19:12:22.176301

---

## Nous Analysis

**Algorithm**  
1. **Dictionary learning (Sparse Autoencoder core)** – Build a matrix **D** ∈ ℝ^{F×V} where *V* is the vocabulary size and *F* ≪ *V* is the number of latent features. Using only NumPy, run iterative hard‑thresholding: initialize **D** with random columns, then for each training sentence *s* compute a sparse code **α** by solving  
   \[
   \min_{\alpha}\|x_s - D^\top\alpha\|_2^2 + \lambda\|\alpha\|_1
   \]  
   via a few iterations of soft‑thresholding on the gradient step (x_s is the bag‑of‑words vector of *s*). Keep the top *k* entries of **α** to enforce sparsity. Store the final **D**.  
2. **Compositionality layer** – Parse a sentence into a tree of atomic propositions *p_i* (extracted via regex for predicates, arguments, negations, comparatives, conditionals, causal markers, ordering words, and numbers). Each *p_i* is mapped to its sparse code **α_i** (lookup in **D** via OMP). Combine child nodes according to the logical operator at the parent:  
   - AND → **α_parent** = min(**α_left**, **α_right**) (elementwise)  
   - OR  → **α_parent** = max(**α_left**, **α_right**)  
   - NOT → **α_parent** = 1 – **α_child**  
   - IMPLIES (if‑then) → **α_parent** = max(1‑**α_antecedent**, **α_consequent**)  
   The root yields a compositional feature vector **α_root**.  
3. **Sensitivity analysis** – Generate *K* perturbed versions of the input sentence by (a) random token masking (10 % dropout), (b) synonym swap from a hand‑crafted list, (c) numeric perturbation (±5 %). For each perturbed version compute **α_root^{(j)}** and a base score *s_j* = –‖**α_root^{(j)}** – **α_gold**‖₂², where **α_gold** is the representation of a reference answer. The final score is  
   \[
   S = \frac{1}{K}\sum_{j=1}^{K}s_j - \gamma \,\operatorname{Var}\{s_j\}
   \]  
   with γ a small penalty for high variance (low robustness).  

**Parsed structural features** – Negations (“not”, “no”), comparatives (“greater than”, “less than”), conditionals (“if … then …”), causal markers (“because”, “leads to”), ordering relations (“before”, “after”), and explicit numeric values with units. Regex patterns extract these tokens and build the proposition tree.

**Novelty** – Sparse coding for interpretable features, logical composition of those features, and robustness‑via‑perturbation scoring have each appeared separately (e.g., dictionary learning in NLP, logic‑tensor networks, robustness checks). Their conjunction in a pure‑NumPy evaluation tool has not been documented in prior work, making the combination novel for lightweight reasoning assessment.

**Ratings**  
Reasoning: 7/10 — captures logical structure and robustness but limited to hand‑crafted operators.  
Metacognition: 5/10 — no explicit self‑monitoring or uncertainty estimation beyond variance.  
Hypothesis generation: 6/10 — can propose alternative parses via perturbations but lacks generative search.  
Implementability: 8/10 — relies only on NumPy and regex; all steps are straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T19:11:23.406923

---

## Code

*No code was produced for this combination.*
