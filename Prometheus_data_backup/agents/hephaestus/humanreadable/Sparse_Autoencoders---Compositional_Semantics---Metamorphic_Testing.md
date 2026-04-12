# Sparse Autoencoders + Compositional Semantics + Metamorphic Testing

**Fields**: Computer Science, Philosophy, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T17:56:42.257345
**Report Generated**: 2026-03-31T17:10:38.092741

---

## Nous Analysis

**Algorithm**  
1. **Parsing layer** – Using only the Python `re` module we extract a set of atomic propositions \(P=\{p_1,…,p_m\}\) from the prompt and each candidate answer. Patterns capture:  
   * Negations (`\bnot\b`, `n't`) → polarity flag.  
   * Comparatives (`more than|less than|greater than|less\ than`) → binary relation `comp(x,y,op)`.  
   * Conditionals (`if .* then .*`) → implication `cond(antecedent, consequent)`.  
   * Numeric values (`\d+(\.\d+)?`) → literal `num(value)`.  
   * Ordering (`before|after|precedes|follows`) → `order(x,y)`.  
   * Causal cues (`because|leads to|results in`) → `cause(x,y)`.  
   Each proposition is stored as a tuple `(type, args, polarity)` and one‑hot encoded into a binary vector \(x\in\{0,1\}^m\).

2. **Dictionary learning (Sparse Autoencoder)** – We learn an over‑complete basis \(D\in\mathbb{R}^{m\times k}\) (k > m) that reconstructs prompt vectors while encouraging sparsity. Starting from a random Gaussian matrix, we iterate:  
   * **Sparse coding** – For each vector \(x\) compute \(\alpha = \text{ISTA}(x,D,\lambda)\) (iterative soft‑thresholding algorithm) using only NumPy matrix multiplications and the shrinkage operator \(S_{\tau}(z)=\text{sign}(z)\max(|z|-\tau,0)\).  
   * **Dictionary update** – Solve \( \min_D \|X-DA\|_F^2\) with a closed‑form least‑squares step (NumPy `lstsq`).  
   After T iterations we keep the final \(D\).  

3. **Metamorphic‑relation scoring** – For each candidate we define a set of MRs derived from the prompt’s logical form:  
   * **Numeric scaling MR** – If a numeric literal \(v\) appears, the answer’s truth should change predictably when \(v\) is doubled (e.g., “more than 10” → false when \(v=20\)).  
   * **Order‑invariance MR** – Swapping two symmetric arguments in an ordering predicate should leave the answer’s truth unchanged.  
   * **Negation flip MR** – Adding a literal “not” should invert the binary truth value.  
   We evaluate each MR by re‑parsing the transformed prompt, recomputing its sparse code \(\alpha'\), and measuring agreement between original and transformed predictions (via a simple linear read‑out \(w^\top\alpha\) learned by ridge regression on the prompt’s gold label).  

   Final score for answer \(a\):  
   \[
   S(a)= -\|x_a-D\alpha_a\|_2^2 \;-\;\lambda\|\alpha_a\|_1 \;+\;\eta\sum_{r\in\text{MR}} \mathbb{I}[ \text{MR}_r \text{ satisfied} ]
   \]  
   where the first two terms are reconstruction and sparsity penalties (NumPy norms) and the last term rewards satisfaction of metamorphic relations.

**Structural features parsed** – negations, comparatives, conditionals, numeric literals, ordering relations, causal cues.

**Novelty** – Sparse autoencoders have been used for unsupervised feature learning in NLP, compositional semantics guides symbolic parsing, and metamorphic testing supplies oracle‑free validation. Their tight integration—learning a shared sparse dictionary from parsed logical forms and then scoring candidates by reconstruction error, sparsity, and MR compliance—has not been reported in existing work; prior approaches treat these components separately.

**Rating**  
Reasoning: 8/10 — captures logical structure and enforces consistency via MRs, improving over pure similarity baselines.  
Metacognition: 6/10 — the method can detect when its own reconstruction fails (high error) but lacks explicit self‑reflection on reasoning steps.  
Hypothesis generation: 5/10 — sparsity encourages diverse feature uses, yet hypothesis proposal is limited to linear read‑outs of the code.  
Implementability: 9/10 — relies only on NumPy and `re`; all operations (ISTA, dictionary update, MR checks) are straightforward to code.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T17:08:23.229538

---

## Code

*No code was produced for this combination.*
