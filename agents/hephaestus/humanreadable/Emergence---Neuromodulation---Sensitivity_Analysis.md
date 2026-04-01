# Emergence + Neuromodulation + Sensitivity Analysis

**Fields**: Complex Systems, Neuroscience, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T19:58:28.181209
**Report Generated**: 2026-03-31T20:00:10.442573

---

## Nous Analysis

**Algorithm: Emergent Constraint‑Gain Scoring (ECGS)**  

1. **Parsing & Data Structures**  
   - Extract propositional atoms from the candidate answer using regex patterns for:  
     * negations (`not`, `no`),  
     * comparatives (`greater than`, `less than`, `≥`, `≤`),  
     * conditionals (`if … then …`, `unless`),  
     * causal verbs (`causes`, `leads to`, `results in`),  
     * numeric constants and units,  
     * ordering relations (`before`, `after`, `first`, `last`).  
   - Each atom becomes a node *i* with fields:  
     - `val[i]` ∈ {0,1} (truth assignment from the prompt’s gold facts),  
     - `conf[i]` ∈ [0,1] (initial confidence, set to 1 if directly supported, 0.5 if inferred).  
   - For every extracted relation *r* (e.g., “A causes B”, “X > Y”) create a directed edge *i → j* with a base weight *w₀[r]* = 1.0. Store edges in an adjacency matrix **W** (numpy float64) and a parallel list of relation types for later masking.

2. **Emergence Layer (Macro‑coherence)**  
   - Form the constraint satisfaction matrix **C** = **W** ⊙ **M**, where **M** masks edges that are logically satisfied given current `val` (e.g., a causal edge is satisfied if `val[i]==1` and `val[j]==1`).  
   - Compute the leading eigenvalue λ₁ of **C** (via `numpy.linalg.eigvals`). λ₁ captures a global, non‑reducible coherence score – the emergent property of the answer’s internal constraint network.

3. **Neuromodulation (Gain Control)**  
   - For each node compute uncertainty *u[i]* = 1 − conf[i].  
   - Derive a dopaminergic‑style gain factor *g[i]* = 1 + α·u[i] (α = 0.3).  
   - Modulate edge weights: **W̃** = **W** * (g[source]·g[target])ᵀ (outer product, numpy broadcasting).  
   - Re‑compute **C̃** = **W̃** ⊙ **M** and its leading eigenvalue λ̃₁. This step implements state‑dependent gain control, amplifying constraints that involve uncertain propositions.

4. **Sensitivity Analysis (Robustness Check)**  
   - Perturb each edge weight by ±ε (ε = 0.05) one‑at‑a‑time, recompute λ̃₁, and record the absolute change Δλₖ.  
   - Compute sensitivity *S* = meanₖ(Δλₖ).  
   - Final score = λ̃₁ / (1 + β·S) (β = 0.2), penalizing answers whose emergent coherence is fragile to small input perturbations.

**Structural Features Parsed** – negations, comparatives, conditionals, causal claims, numeric values/units, and ordering/temporal relations. These are the atoms and edges that feed the constraint matrix.

**Novelty** – While probabilistic soft logic and Markov logic networks capture weighted constraints, ECGS adds a biologically‑inspired neuromodulatory gain layer and an explicit finite‑difference sensitivity step to derive an emergent eigenvalue‑based score. This specific combination of emergence (spectral coherence), neuromodulation (uncertainty‑driven gain), and sensitivity analysis (perturbation‑based robustness) is not present in existing public reasoning‑scoring tools.

**Ratings**  
Reasoning: 8/10 — captures logical structure and global coherence via eigenvalue, but relies on linear approximations.  
Metacognition: 7/10 — uncertainty‑based gain provides a crude self‑assessment; no explicit reflection on reasoning steps.  
Hypothesis generation: 6/10 — can propose alternative weight perturbations, yet lacks generative proposal of new facts.  
Implementability: 9/10 — uses only numpy and stdlib; all operations are matrix algebra and regex parsing.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
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
