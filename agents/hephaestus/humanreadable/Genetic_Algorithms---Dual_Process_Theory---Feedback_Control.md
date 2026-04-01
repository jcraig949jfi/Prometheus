# Genetic Algorithms + Dual Process Theory + Feedback Control

**Fields**: Computer Science, Cognitive Science, Control Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T17:36:40.517476
**Report Generated**: 2026-03-31T18:13:45.702628

---

## Nous Analysis

**Algorithm**  
Each candidate answer is encoded as an individual `I = (T, f, fit)` where `T` is a parse‑tree (nested list) of propositional clauses extracted by regex, `f ∈ ℝ^d` is a feature‑vector of structural pattern counts, and `fit` is a scalar fitness. A population `P` of size `N` is stored as a Python list of such tuples; feature vectors are kept in a NumPy array for fast dot‑product.

1. **Fast heuristic (System 1)** – Compute `h = w·f` where `w` is a fixed weight vector learned offline (e.g., via linear regression on a small validation set). `h` rewards presence of useful patterns (comparatives, causal cues) and penalizes obvious flaws (double negation, unsupported numeric claims).

2. **Deliberate constraint check (System 2)** – From `T` derive a set of Horn clauses. Run forward chaining (unit resolution) to infer all literals entailed by the prompt + candidate. Count violations `v` where a clause contradicts an entailed literal or where a required literal cannot be derived. Constraint score `c = -λ·v` (λ > 0).

3. **Fitness** – `fit = h + c`. Higher `fit` means better alignment with both shallow cues and deep logical consistency.

4. **Genetic operators**  
   *Selection*: tournament of size 3, pick the individual with highest `fit`.  
   *Crossover*: choose a random subtree in each parent’s `T` and swap them, producing two offspring; feature vectors are recomputed from the new trees.  
   *Mutation*: with probability `p_m` pick a leaf node and either (a) flip a negation, (b) change a comparator (`<`↔`>`, `=`↔`≠`), or (c) perturb a numeric constant by adding Gaussian noise `𝒩(0,σ²)`. After mutation, rebuild `f` and recompute `fit`.

5. **Feedback control (PID on mutation rate)** – Let `e_g = f_target − mean(fit_P)` be the error between a desired fitness (e.g., the fitness of a known correct answer) and the population mean after generation `g`. Update the mutation probability:  
   `p_m ← p_m + K_p·e_g + K_i·Σ_{i≤g} e_i + K_d·(e_g−e_{g−1})`, clamped to `[0.01,0.5]`. Integral and derivative terms are maintained as scalars. This drives the search toward higher fitness while preventing premature convergence.

**Parsed structural features**  
- Negations (`not`, `no`, `never`)  
- Comparatives and equality (`>`, `<`, `≥`, `≤`, `=`, `≠`)  
- Numeric constants and units  
- Causal connectives (`because`, `leads to`, `causes`)  
- Conditionals (`if … then …`, `unless`)  
- Temporal/ordering relations (`before`, `after`, `while`)  
- Quantifiers (`all`, `some`, `none`)  
- Logical conjunction/disjunction (`and`, `or`)

**Novelty**  
Evolutionary search of logical forms and dual‑process scoring have appeared separately (e.g., genetic programming for program synthesis, ACT‑R‑style hybrid models). Coupling a PID‑regulated mutation rate with a explicit fast‑heuristic + slow‑constraint fitness function, all implemented with only NumPy and the stdlib, is not documented in existing reasoning‑evaluation tools, making the combination novel.

**Ratings**  
Reasoning: 8/10 — The algorithm directly optimizes for both shallow cue matching and deep logical consistency, addressing the core of reasoning evaluation.  
Metacognition: 6/10 — It monitors population fitness and adapts mutation via feedback, but lacks explicit self‑reflection on strategy selection.  
Hypothesis generation: 7/10 — Crossover and mutation generate new logical structures, serving as hypotheses; however, the search is blind to semantic plausibility beyond constraints.  
Implementability: 9/10 — All components (regex parsing, NumPy dot‑product, forward chaining, tournament selection, PID update) run with only NumPy and the Python standard library.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T18:12:31.858093

---

## Code

*No code was produced for this combination.*
