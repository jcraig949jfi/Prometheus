# Dynamical Systems + Free Energy Principle + Metamorphic Testing

**Fields**: Mathematics, Theoretical Neuroscience, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T16:22:09.127072
**Report Generated**: 2026-03-27T17:21:24.863551

---

## Nous Analysis

**Algorithm**  
The scorer builds a discrete‑time dynamical system whose state `x ∈ ℝⁿ` encodes the truth‑strength of propositions extracted from a prompt and a candidate answer.  
1. **Parsing** – Using only `re`, we extract:  
   * atomic propositions (e.g., “the temperature is high”),  
   * negations (`not`),  
   * comparatives (`>`, `<`, `=`),  
   * conditionals (`if … then …`),  
   * causal cues (`because`, `leads to`),  
   * ordering relations (`before`, `after`, `first`, `second`),  
   * numeric literals with units.  
   Each proposition gets an index; its initial value is 1 if asserted true, 0 if asserted false, 0.5 for unknown.  
2. **Implication matrix** – From conditionals and causal cues we fill a weight matrix `W ∈ ℝⁿˣⁿ` where `W[i,j]=w` means proposition *j* supports *i* with strength *w* (default 0.1). Negations flip the sign of the source column.  
3. **Free‑energy dynamics** – Let `y` be the vector of observed truth values from the prompt (fixed). Variational free energy is approximated by the squared prediction error  

   ```
   F(x) = ||W x – y||₂² .
   ```

   Gradient descent yields the update  

   ```
   x_{t+1} = x_t – α ∇F(x_t) = x_t – 2α Wᵀ (W x_t – y) .
   ```

   We iterate until `||x_{t+1}–x_t|| < 1e‑4` or a max of 100 steps, using only `numpy`.  
4. **Metamorphic relations (MRs)** – For each candidate we generate a set of synthetic variants by applying MRs derived from the extracted structure:  
   * **Numeric MR**: multiply every numeric literal by 2 → expect the corresponding proposition’s truth to shift proportionally (encoded by adjusting `y`).  
   * **Order MR**: swap the order of two conjuncts in a conditional → antecedent/consequent positions swapped in `W`.  
   * **Negation MR**: insert/delete a `not` → flip sign of the relevant column in `W`.  
   For each variant we run the same dynamics and record its final free energy `Fᵢ`.  
5. **Scoring** – The base score is negative free energy (lower error = better). We add a stability penalty based on the leading Lyapunov‑like exponent estimated from the Jacobian  

   ```
   J = I – 2α WᵀW ,
   λ_max = max real eig(J) .
   ```

   Final score  

   ```
   S = –F₀ + β·(1 – λ_max) ,
   ```

   with β = 0.2 to reward dynamical stability. Higher `S` indicates a more coherent answer.

**Structural features parsed** – negations, comparatives, conditionals, causal verbs, ordering/temporal relations, numeric literals with units, and conjunction/disjunction boundaries.

**Novelty** – While dynamical systems and the free‑energy principle appear in cognitive modeling, and metamorphic testing is well‑known in software verification, their conjunction to drive a gradient‑based error‑minimization scorer for textual reasoning has not been reported in the literature.

**Rating**  
Reasoning: 7/10 — captures logical consistency and numeric sensitivity via gradient descent on a principled energy function.  
Metacognition: 6/10 — stability term offers a rudimentary self‑check, but no explicit monitoring of search alternatives.  
Hypothesis generation: 5/10 — MRs generate variants, yet the system does not propose new hypotheses beyond those transforms.  
Implementability: 8/10 — relies solely on `numpy` for linear algebra and the standard library for regex; no external dependencies.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
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
