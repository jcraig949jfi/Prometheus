# Sparse Coding + Compositionality + Sensitivity Analysis

**Fields**: Neuroscience, Linguistics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T19:54:52.538888
**Report Generated**: 2026-04-01T20:30:44.156106

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex to extract atomic propositions from the prompt and each candidate answer. Each proposition is a tuple `(type, polarity, args)` where `type` ∈ {negation, comparative, conditional, numeric, causal, ordering}. Store propositions in a list `P`.  
2. **Sparse coding** – Initialize a binary vector `s ∈ {0,1}^|P|` with L0‑norm ≤ k (e.g., k=5). Set `s[i]=1` for propositions that appear in the prompt; all others stay 0. This yields a sparse activation pattern.  
3. **Compositionality rules** – Define a deterministic composition table `C` that maps pairs of proposition types to a derived proposition (e.g., (comparative, ordering) → ordering, (conditional, negation) → inverted conditional). Represent `C` as a sparse adjacency matrix `A ∈ ℝ^{|P|×|P|}` where `A[j,i]=1` if proposition `j` can be composed from `i` using a rule in `C`.  
4. **Forward chaining (constraint propagation)** – Compute the closed‑form activation `h = (I + A + A² + … + A^m) s` (boolean OR after each power) using numpy’s dot and clip to `{0,1}`; `m` is the maximal composition depth (typically 2‑3). `h` indicates which propositions are entailed by the prompt under the compositional grammar.  
5. **Sensitivity analysis** – For each active input proposition `i` where `s[i]=1`, create a perturbed vector `s⁻ⁱ` with that bit flipped to 0. Propagate each `s⁻ⁱ` through the same forward chaining to obtain `h⁻ⁱ`. Compute the change Δᵢ = ‖h – h⁻ⁱ‖₁ (number of entailed propositions lost). The sensitivity score for a candidate answer is `S = Σᵢ Δᵢ / k`. Lower `S` means the answer’s entailment set is robust to removal of any single prompt proposition → higher answer quality.  
6. **Scoring** – Return `score = 1 / (1 + S)` (higher is better).  

**Structural features parsed**  
- Negations (`not`, `no`)  
- Comparatives (`greater than`, `less than`, `≥`, `≤`)  
- Conditionals (`if … then …`, `only if`)  
- Numeric values and units  
- Causal cues (`because`, `leads to`, `results in`)  
- Ordering/temporal relations (`before`, `after`, `precedes`)  
- Conjunctions (`and`) and disjunctions (`or`) handled via composition rules.

**Novelty**  
The triple blend of sparse binary coding, deterministic compositional rule application, and finite‑difference sensitivity analysis is not present in standard QA scoring tools. While neuro‑symbolic literature discusses similar ideas, a pure‑numpy implementation that explicitly computes robustness via propositional perturbations is novel.

**Rating**  
Reasoning: 7/10 — captures logical structure and robustness but ignores probabilistic uncertainty.  
Metacognition: 5/10 — provides a sensitivity signal but no explicit self‑monitoring of reasoning steps.  
Hypothesis generation: 4/10 — limited to propagating existing propositions; does not invent new ones.  
Implementability: 8/10 — relies only on regex, numpy boolean algebra, and fixed‑depth matrix powers; straightforward to code.

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
