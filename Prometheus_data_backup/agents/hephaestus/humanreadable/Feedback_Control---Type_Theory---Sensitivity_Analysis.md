# Feedback Control + Type Theory + Sensitivity Analysis

**Fields**: Control Theory, Logic, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T02:08:18.192757
**Report Generated**: 2026-03-31T14:34:55.665585

---

## Nous Analysis

The algorithm builds a typed abstract syntax tree (AST) from the raw text using only regex‑based token extraction. Each token is classified into one of a fixed set of types: **Bool** (propositions), **Real** (numeric literals), **Order** (temporal or magnitude relations), and **Causal** (cause‑effect links). Nodes store: operator (¬, ∧, →, >, <, =, because, before, after), list of child node references, inferred type, and a concrete value when the node is a literal (e.g., 3.14).  

Parsing proceeds in three passes:  
1. **Extraction** – regex patterns capture negations (“not”, “no”), comparatives (“greater than”, “less than”, “≤”, “≥”), conditionals (“if … then …”), numeric constants, causal cue words (“because”, “leads to”), and ordering terms (“before”, “after”, “since”).  
2. **Typing** – a bottom‑up pass assigns types using a simple type‑inference table (e.g., child types Real + Real → Real for “>”, Bool + Bool → Bool for “∧”).  
3. **Sensitivity propagation** – Boolean semantics are relaxed to real‑valued signals via a sigmoid σ(x)=1/(1+e^{‑x}). Each node computes its output y = f(y₁,…,yₙ) and, using forward‑mode automatic differentiation, stores the partial derivatives ∂y/∂yᵢ. The root’s sensitivity vector S indicates how perturbations in atomic propositions affect the final truth value.  

Scoring uses a PID‑style feedback loop that iteratively reduces the error e = y_ref − y_cand between the reference answer’s root value y_ref (derived from a gold‑standard annotation) and the candidate’s root value y_cand. At iteration t:  
- pₜ = Kₚ·eₜ  
- iₜ = Kᵢ·∑_{k≤t} e_k  
- dₜ = K_d·(eₜ − e_{t‑1})  
The control signal uₜ = pₜ + iₜ + dₜ adjusts a weighting vector w that scales the leaf sensitivities before recomputing y_cand. After a fixed number of steps (or when |e| < ε), the final score is s = clip(1 − |u_T|, 0, 1).  

**Parsed structural features:** negations, comparatives, conditionals, numeric literals, causal claims, ordering relations.  

**Novelty:** While type‑theoretic parsing and sensitivity analysis appear separately in differentiable logic and uncertainty quantification, coupling them with a feedback‑control PID loop to directly optimize answer scoring is not documented in existing QA or evaluation literature.  

Reasoning: 7/10 — captures logical structure and propagates uncertainty, but real‑valued Boolean relaxation limits strict logical fidelity.  
Metacognition: 6/10 — the PID loop offers basic self‑correction, yet lacks higher‑order reflection on its own assumptions.  
Hypothesis generation: 5/10 — focuses on validating given candidates; generating alternative hypotheses would require additional search mechanisms.  
Implementability: 8/10 — relies only on regex, numpy for vector ops, and stdlib data structures; no external libraries needed.

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
