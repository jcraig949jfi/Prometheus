# Global Workspace Theory + Falsificationism + Adaptive Control

**Fields**: Cognitive Science, Philosophy, Control Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T22:39:48.370589
**Report Generated**: 2026-03-31T16:31:50.614895

---

## Nous Analysis

**Algorithm**  
The tool builds a *Global Workspace* (GW) as a mutable NumPy array `W` of shape `(P,)` where each entry `w_i` is the current activation (confidence) of proposition `i`. Propositions are extracted from the prompt and each candidate answer by a deterministic parser that returns a list of atomic literals (e.g., `Rain`, `¬Wet`, `Temperature>20`) and binary relations (`If A then B`, `A causes B`, `X > Y`). These literals become indices in `W`.  

1. **Ignition & Competition** – For each candidate answer, its literals are temporarily injected into `W` (copy `W₀ → W_cand`). A forward‑chaining loop applies modus ponens on extracted conditionals: whenever `A` and `If A then B` are both active (`w_A>θ` and `w_rule>θ`), `w_B` is increased by `α·w_A·w_rule`. Negations suppress the opposite literal (`w_¬B ← w_¬B·β`). This spread continues until convergence (no change > ε).  

2. **Falsification Scoring** – After ignition, the algorithm attempts to derive a contradiction: if both a literal `L` and its negation `¬L` exceed the activation threshold θ, a falsification penalty `γ·(w_L + w_¬L)` is subtracted from the candidate’s base score. The final score is `S = Σ_i w_i – Σ_falsifications penalty`.  

3. **Adaptive Control** – After evaluating all candidates, the system updates a *reference weight vector* `W_ref` (the average activation of propositions that survived falsification across the batch) using a simple self‑tuning rule: `W_ref ← W_ref + η·(W_cand_best – W_ref)`, where `η` is a small learning rate. This updated reference biases the next round’s ignition, effectively tuning the GW to the statistical structure of the task.  

All operations use NumPy vectorized arithmetic; the parser relies only on `re` from the standard library.

**Structural Features Parsed**  
- Negations (`not`, `no`, `-`)  
- Comparatives (`>`, `<`, `≥`, `≤`, `equals`)  
- Conditionals (`if … then …`, `unless`)  
- Causal cues (`because`, `leads to`, `results in`)  
- Temporal/ordering (`before`, `after`, `while`)  
- Numeric constants and units  
- Quantifiers (`all`, `some`, `none`) mapped to universal/existential literals  

**Novelty**  
The fusion mirrors existing argumentation‑framework and belief‑revision systems, but the explicit global broadcast mechanism (GW ignition) combined with an online adaptive‑control update of propositional weights is not found in standard NLP reasoning tools, making the combination novel.

**Ratings**  
Reasoning: 8/10 — captures logical consequence and falsification concretely.  
Metacognition: 6/10 — adaptive weight update offers limited self‑monitoring.  
Hypothesis generation: 7/10 — generates and tests multiple candidate answer hypotheses via ignition.  
Implementability: 9/10 — relies solely on regex, NumPy, and std‑lib; straightforward to code.

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

**Forge Timestamp**: 2026-03-31T16:30:30.767834

---

## Code

*No code was produced for this combination.*
