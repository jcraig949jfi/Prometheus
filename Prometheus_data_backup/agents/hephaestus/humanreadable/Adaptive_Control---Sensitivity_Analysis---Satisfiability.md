# Adaptive Control + Sensitivity Analysis + Satisfiability

**Fields**: Control Theory, Statistics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T13:26:34.932410
**Report Generated**: 2026-03-31T14:34:56.054004

---

## Nous Analysis

**Algorithm**  
We build a lightweight MaxSAT scorer that treats each extracted proposition as a Boolean variable. The core data structures are:  

* `var_map: dict[str,int]` – maps each unique literal (e.g., “temperature > 30°C”) to an index.  
* `clauses: List[Tuple[List[int], float]]` – each clause is a list of signed variable indices (positive for the literal, negative for its negation) together with a current weight `w_i`.  
* `weights: np.ndarray` – shape `(n_clauses,)`, initialized to 1.0.  
* `sens: np.ndarray` – same shape, stores the sensitivity of the total score to each weight.  

**Parsing** (regex‑based, stdlib only) extracts:  
* atomic propositions with optional negation (`not`, `no`).  
* comparatives (`>`, `<`, `≥`, `≤`, `=`) turning them into propositions like “value > threshold”.  
* conditionals (`if … then …`) encoded as implication clauses `(¬A ∨ B)`.  
* causal cues (`because`, `leads to`, `results in`) also become implications.  
* ordering/temporal words (`before`, `after`) become precedence propositions.  

Each extracted proposition yields one or more clauses; numeric thresholds become ground‑truth facts (unit clauses) when the prompt supplies a value.

**Scoring loop** (adaptive control + sensitivity analysis):  

1. **Inference** – run a unit‑propagation + pure‑literal elimination loop (linear‑time) to derive a tentative assignment that satisfies as many unit clauses as possible. Remaining clauses are evaluated greedily: a clause contributes its weight if any literal is true under the current assignment.  
2. **Score** – `S = Σ w_i * satisfied_i / Σ w_i`.  
3. **Sensitivity** – perturb each weight by a small ε (e.g., 1e‑3) and recompute S; `sens[i] = (S_plus - S_minus)/(2ε)`.  
4. **Weight update (self‑tuning)** – increase weights of clauses with high positive sensitivity (they hurt the score when weakened) and decrease those with negative sensitivity: `w ← w * exp(η * sens)`, with a small learning rate η (e.g., 0.01). Renormalize to keep Σw = n_clauses.  
5. Iterate steps 1‑4 for a fixed number of epochs (e.g., 10) or until weight change < 1e‑4.  

The final `S` is the candidate‑answer score: higher means fewer violated weighted constraints, i.e., better logical and numeric consistency.

**Structural features parsed** – negations, comparatives, conditionals, causal language, numeric thresholds, ordering/temporal relations, equality statements.

**Novelty** – While weighted MaxSAT and adaptive clause weighting (e.g., WalkSAT’s noise adaptation) exist, coupling them with an online sensitivity‑driven weight update that treats the score as a control signal is not described in the literature. It merges adaptive control’s parameter tuning, sensitivity analysis’s gradient‑based insight, and SAT solving’s constraint propagation into a single scoring loop.

**Ratings**  

Reasoning: 7/10 — The method captures logical structure and numeric constraints, but relies on greedy unit propagation and may miss deeper proof‑theoretic reasoning.  
Metacognition: 5/10 — No explicit self‑monitoring of search depth or uncertainty; weight adaptation provides only rudimentary feedback.  
Hypothesis generation: 4/10 — The system evaluates given candidates; it does not propose new answer hypotheses beyond weighting adjustments.  
Implementability: 8/10 — All components use regex, numpy arrays, and simple loops; no external libraries or neural nets required.

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
