# Differentiable Programming + Analogical Reasoning + Sensitivity Analysis

**Fields**: Computer Science, Cognitive Science, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-29T03:07:17.615237
**Report Generated**: 2026-03-31T20:00:10.430575

---

## Nous Analysis

**Algorithm**  
The scorer builds a differentiable logical‑analogical graph from each text.  
1. **Parsing (regex + spacy‑lite)** extracts propositions \(p_i = (pred, args, polarity, modality, num)\).  
   - *pred*: predicate string (e.g., “greater”, “cause”).  
   - *args*: list of entity identifiers.  
   - *polarity*: +1 for affirmative, ‑1 for negation.  
   - *modality*: 0 = certain, 1 = possible (from “might”, “must”).  
   - *num*: optional numeric value (normalized).  
   Entities are stored in a dictionary; propositions become nodes in a directed multigraph \(G\).  
2. **Differentiable constraint layer** encodes logical rules as soft penalties. For each extracted rule (e.g., “if A then B” → \(A \rightarrow B\)) we add a term  
   \[
   \mathcal{L}_{\text{rule}} = \text{sigmoid}(A)\,(1-\text{sigmoid}(B))
   \]  
   where \(A,B\) are the truth‑values of the antecedent/consequent propositions obtained via a differentiable lookup (one‑hot → softmax over node embeddings). All rule losses sum to \(\mathcal{L}_{\text{logic}}\).  
3. **Analogical similarity** treats the reference answer graph \(G^{*}\) and candidate graph \(G^{c}\) as feature‑rich graphs. Node features concatenate predicate one‑hot, polarity, modality, and normalized numeric; edge features capture relation type (e.g., “subject‑of”, “object‑of”). A differentiable Sinkhorn‑based graph matching yields a soft permutation matrix \(P\); the analogy loss is  
   \[
   \mathcal{L}_{\text{analogy}} = \|F^{*} - P F^{c}\|_{F}^{2}
   \]  
   where \(F\) are stacked feature matrices.  
4. **Sensitivity analysis** perturbs each input token (flip negation, add/subtract ±1 to numeric, swap modality) and computes the gradient of the total loss \(\mathcal{L} = \mathcal{L}_{\text{logic}} + \lambda_{1}\mathcal{L}_{\text{analogy}}\) w.r.t. that perturbation using finite‑difference autodiff (numpy). The sensitivity penalty is the mean absolute gradient magnitude: \(\mathcal{L}_{\text{sens}} = \frac{1}{N}\sum |\partial \mathcal{L}/\partial \delta_{i}|\).  
5. **Final score** (higher = better):  
   \[
   s = \exp\!\big(-(\mathcal{L}_{\text{logic}} + \lambda_{1}\mathcal{L}_{\text{analogy}} + \lambda_{2}\mathcal{L}_{\text{sens}})\big)
   \]  
   All operations use only numpy (matrix ops, sigmoid, Sinkhorn) and the Python standard library (regex, collections).

**Structural features parsed**  
- Negations (not, no) → polarity = ‑1.  
- Comparatives (greater than, less than) → predicate “greater/less”, numeric args.  
- Conditionals (if … then …) → rule extraction.  
- Causal claims (because, leads to, causes) → predicate “cause”.  
- Ordering relations (before, after, precedes) → temporal edges.  
- Numeric values with units → normalized num field.  
- Quantifiers (all, some, none) → modality or extra predicate.  
- Modal adverbs (might, must, likely) → modality flag.

**Novelty**  
Prior work separates differentiable logic (e.g., Neural Theorem Provers) from analogical mapping (e.g., Structure‑Mapping Engine) or treats sensitivity as a post‑hoc robustness check. This scorer jointly optimizes logical consistency, analogical structure similarity, and input‑perturbation sensitivity in a single end‑end differentiable pipeline, which to our knowledge has not been combined for answer scoring.

**Ratings**  
Reasoning: 8/10 — captures logical, relational, and numeric reasoning via differentiable constraints and graph matching.  
Metacognition: 6/10 — sensitivity term reflects robustness awareness but lacks explicit self‑monitoring of reasoning steps.  
Hypothesis generation: 5/10 — the model can propose alternative parses via gradient‑based perturbations, yet does not explicitly generate new hypotheses.  
Implementability: 9/10 — relies solely on numpy regex, basic autodiff via finite differences, and Sinkhorn, all feasible in <200 lines.

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

**Forge Timestamp**: 2026-03-31T19:57:49.521712

---

## Code

*No code was produced for this combination.*
