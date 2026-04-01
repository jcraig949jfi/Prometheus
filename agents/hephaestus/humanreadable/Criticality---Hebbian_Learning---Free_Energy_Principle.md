# Criticality + Hebbian Learning + Free Energy Principle

**Fields**: Complex Systems, Neuroscience, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T01:44:39.143121
**Report Generated**: 2026-03-31T14:34:55.603586

---

## Nous Analysis

**Algorithm**  
1. **Parse → Proposition Graph** – Using regex we extract atomic propositions (e.g., “X > Y”, “if A then B”, “not C”). Each proposition becomes a node; directed edges encode logical relations (implication, equivalence, negation, ordering). The graph is stored as a NumPy adjacency matrix **W** (float64) where Wᵢⱼ = 1 for a direct link, 0 otherwise.  
2. **Hebbian Weight Update** – For every candidate answer we compute its proposition set **Sₐ**. For each pair (i,j)∈Sₐ we increase the synapse: Wᵢⱼ←Wᵢⱼ+η·xᵢ·xⱼ, where xᵢ=1 if proposition i appears in the answer, η is a small learning rate (0.01). This implements activity‑dependent strengthening.  
3. **Free‑Energy (Prediction Error)** – We maintain a prior expectation matrix **P** (initialized as the identity). The variational free energy for an answer is approximated by the reconstruction error: Fₐ = ‖Sₐ − sigmoid(W·Sₐ)‖₂², computed with NumPy. Lower Fₐ means the answer better predicts its own internal structure (prediction‑error minimization).  
4. **Criticality Tuning** – After each update we compute the leading eigenvalue λₘₐₓ of **W**. If λₘₐₓ > 1 (super‑critical) we globally scale W←W/λₘₐₓ; if λₘₐₓ < 0.9 (sub‑critical) we scale W←W·(1/λₘₐₓ). This drives the system toward the edge of chaos where susceptibility (∂F/∂W) is maximal, giving the most discriminative scoring.  
5. **Scoring** – Final score = −Fₐ (higher is better). The pipeline uses only NumPy for matrix ops and the stdlib for regex and control flow.

**Structural Features Parsed** – Negations (“not”, “never”), comparatives (“greater than”, “less than”), conditionals (“if…then”, “unless”), numeric values and units, causal verbs (“causes”, “leads to”), ordering relations (“before”, “after”, “precedes”), and equivalence (“is the same as”).

**Novelty** – The trio maps onto known frameworks: Hebbian learning ↔ Hopfield/Boltzmann machines, free energy ↔ predictive coding, criticality ↔ the “critical brain hypothesis”. Their explicit combination for scoring logical answer graphs via eigenvalue‑regulated Hebbian updates is not described in existing literature, making it novel.

**Ratings**  
Reasoning: 7/10 — captures logical structure and prediction error but relies on linear approximations.  
Metacognition: 5/10 — no explicit self‑monitoring of confidence beyond energy minimization.  
Hypothesis generation: 6/10 — generates implicit hypotheses via weight updates, yet limited to observed propositions.  
Implementability: 8/10 — uses only NumPy and stdlib; all steps are straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-28T08:48:27.393349

---

## Code

*No code was produced for this combination.*
