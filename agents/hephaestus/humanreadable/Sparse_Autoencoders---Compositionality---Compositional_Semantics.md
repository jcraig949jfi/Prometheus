# Sparse Autoencoders + Compositionality + Compositional Semantics

**Fields**: Computer Science, Linguistics, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T18:25:33.702484
**Report Generated**: 2026-03-27T06:37:47.128955

---

## Nous Analysis

**Algorithm**  
1. **Parsing layer (regex‑based)** – Extract a typed dependency tree from the prompt and each candidate answer. Nodes are lexical items (nouns, verbs, adjectives, numbers) annotated with semantic tags: `neg`, `comp`, `cond`, `caus`, `ord`, `num`. Edges encode syntactic relations (subject‑verb, verb‑object, modifier‑head, comparative‑than, if‑then, cause‑effect). The output is a list of **predicate‑argument structures** (PAS) where each predicate is a symbol (e.g., `greater_than`, `cause`, `not`) and each argument is either a constant (entity or number) or another PAS.  
2. **Sparse dictionary learning** – Build a matrix **D** ∈ ℝ^{V×K} where V is the vocabulary size (unique tokens) and K ≫ V is an overcomplete basis. Each column d_k is a latent feature (e.g., “negation”, “comparative”, “numeric magnitude”). Using only numpy, run an iterative **K‑SVD** style update: for each PAS, form a bag‑of‑tokens vector x, solve min‖x‑Dz‖₂² + λ‖z‖₁ via coordinate descent to obtain a sparse code z (typically <5 non‑zeros). Store the code for every predicate and argument.  
3. **Compositional scoring** – For a PAS, combine child codes with a fixed tensor‑product operation:  
   `z_parent = Σ_i (z_child_i ⊗ w_rel_i)` where ⊗ is the outer product flattened to a vector, and w_rel_i is a learned relation‑specific weight matrix (also learned via sparse coding on relation labels). The result is a sparse vector representing the whole meaning.  
   Compute the reconstruction error **E = ‖x_question·D – z_question‖₂²** and similarly for each candidate. The score is `S = –E` (lower error → higher similarity). Optionally enforce logical constraints (transitivity of `greater_than`, modus ponens for conditionals) by projecting offending codes onto the constraint subspace before scoring.  

**Structural features parsed** – negations (`not`, `no`), comparatives (`more than`, `less than`, `-er`), conditionals (`if … then …`), numeric values and units, causal claims (`because`, `leads to`), ordering relations (`before`, `after`, `greater than`, `less than`), conjunctions/disjunctions, and quantifiers (`all`, `some`).  

**Novelty** – The approach merges three well‑studied ideas: (1) sparse autoencoders/dictionary learning for disentangled feature discovery, (2) Fregean compositionality via explicit predicate‑argument structures, and (3) tensor‑product based compositional semantics. While each component appears in neurosymbolic or tensor‑product literature, the end‑to‑end pipeline that uses only numpy, regex parsing, sparse coding, and fixed tensor‑product composition to score answers is not present in existing work, making the combination novel for a pure‑algorithmic evaluation tool.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and numeric relations via sparse codes and constraint projection, yielding strong discriminative power.  
Metacognition: 6/10 — the method can flag high reconstruction error as uncertainty, but lacks explicit self‑reflective mechanisms.  
Hypothesis generation: 5/10 — generates alternative parses via sparse code alternatives, yet does not actively propose new hypotheses beyond scoring.  
Implementability: 9/10 — relies solely on regex, numpy linear algebra, and simple coordinate‑descent loops; no external libraries or GPUs required.

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

- **Sparse Autoencoders**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 37% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Compositional Semantics**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Compositionality + Sparse Autoencoders: strong positive synergy (+0.433). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Compositional Semantics + Sparse Autoencoders: strong positive synergy (+0.397). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Gauge Theory + Sparse Autoencoders + Compositional Semantics (accuracy: 0%, calibration: 0%)
- Thermodynamics + Sparse Autoencoders + Compositionality (accuracy: 0%, calibration: 0%)
- Category Theory + Sparse Autoencoders + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
