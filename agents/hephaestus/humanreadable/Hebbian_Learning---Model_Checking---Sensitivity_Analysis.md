# Hebbian Learning + Model Checking + Sensitivity Analysis

**Fields**: Neuroscience, Formal Methods, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T19:23:50.567300
**Report Generated**: 2026-03-27T06:37:39.574712

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Proposition graph** – Use a handful of regex patterns to extract atomic propositions and their logical connectors:  
   - Negations (`not`, `no`, `-n’t`) → ¬p  
   - Comparatives (`>`, `<`, `≥`, `≤`, `more than`, `less than`) → p ⊓ q with a numeric constraint  
   - Conditionals (`if … then …`, `when …`, `unless`) → p → q  
   - Causal claims (`because`, `leads to`, `results in`) → p ⇒ q  
   - Ordering/temporal (`before`, `after`, `previously`) → p ≺ q  
   Each proposition gets an index; we store a binary feature vector **x**∈{0,1}^P (P = number of distinct propositions).  
   The logical structure is captured in two numpy matrices:  
   - **Adjacency A** (P×P) where A[i,j]=1 if a rule i→j exists.  
   - **Weight W** (P×P) initialized to zero; will be updated by a Hebbian rule.

2. **Model‑checking step** – For a candidate answer we build a temporary assignment vector **a**∈{0,1}^P by setting propositions that appear explicitly (or are entailed by numeric constraints) to 1.  
   We then perform a bounded depth‑first search over the state space of **a** (max depth = |P|) to verify all rules in **A**: a rule i→j is satisfied if ¬a[i] ∨ a[j] holds. The **satisfaction score** S = (# satisfied rules)/(# total rules).

3. **Hebbian learning update** – Whenever a premise i and consequent j co‑occur in the candidate (both a[i]=a[j]=1), we strengthen the connection:  
   `W[i,j] ← W[i,j] + η·a[i]·a[j]` with a small learning rate η (e.g., 0.01).  
   This creates a memory of which implications the candidate repeatedly affirms.

4. **Sensitivity analysis** – To measure robustness we add small Gaussian noise ε∼N(0,σ²) to **W** (σ=0.05) and recompute the satisfaction score S̃ for K=10 perturbations.  
   The variance V = Var(S̃) quantifies how fragile the answer’s logical support is.  
   Final algorithmic score:  
   `Score = S – λ·V` (λ=0.2 penalizes instability).

**Structural features parsed** – negations, comparatives, conditionals, causal/temporal implication, ordering relations, numeric constants, equality/inequality.

**Novelty** – Pure Hebbian weight adaptation is rare in symbolic reasoning scorers; most existing tools either use static graph‑based model checking or similarity metrics. Combining online Hebbian strengthening with exhaustive state‑space verification and a sensitivity‑based robustness term is not present in the surveyed literature, making the combination novel.

Reasoning: 7/10 — The algorithm captures logical coherence and rewards consistent implication patterns, but it still relies on shallow propositional extraction and may miss deeper semantic nuances.  
Metacognition: 5/10 — No explicit self‑monitoring or confidence calibration beyond variance; the method does not reflect on its own parsing failures.  
Hypothesis generation: 4/10 — The system scores given answers but does not produce new conjectures or alternative explanations.  
Implementability: 8/10 — All components (regex parsing, numpy matrix ops, bounded DFS) run with only numpy and the standard library, making it straightforward to code and test.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Hebbian Learning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Model Checking**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Hebbian Learning + Model Checking: negative interaction (-0.066). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Mechanism Design + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
