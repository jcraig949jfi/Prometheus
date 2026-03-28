# Self-Organized Criticality + Hebbian Learning + Sensitivity Analysis

**Fields**: Complex Systems, Neuroscience, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T04:25:24.635978
**Report Generated**: 2026-03-27T04:25:59.227385

---

## Nous Analysis

**Algorithm**  
1. **Parsing & Node Creation** – Use regex to extract propositional triples (subject, predicate, object) and annotate each with structural features: negation (`not`), comparative (`more/less`), conditional (`if…then`), causal (`because/leads to`), numeric value, ordering (`>`/`<`). Each unique triple becomes a node *i* in a directed graph.  
2. **Weight Initialization (Hebbian)** – Build a co‑occurrence matrix *C* where *C*_{ij} increments when nodes *i* and *j* appear in the same sentence or within a sliding window of *k* tokens. Initialize the weight matrix *W* = α·*C* (α = 0.1) using NumPy; this implements “fire together, wire together.”  
3. **Self‑Organized Criticality Dynamics** – Assign each node an activation *a*_i ∈ [0,1]. Set a uniform threshold θ = 0.5. Iterate:  
   - Find the set *F* = { i | *a*_i > θ }.  
   - For each *f* ∈ *F*, fire: *a*_f ← *a*_f − θ (reset) and distribute its excess equally to outgoing neighbors: for each *j* with *W*_{fj}>0, *a*_j ← *a*_j + (*W*_{fj} / ∑_l *W*_{fl})·θ.  
   - Continue until *F* is empty. This is analogous to a sandpile avalanche; the system settles into a critical state where activation follows a power‑law distribution over cascade sizes.  
4. **Sensitivity Analysis** – For each weight *W*_{pq}, compute a finite‑difference sensitivity of the activation of a candidate‑answer node *a*_ans:  
   Δ*W* = ε·|*W*_{pq}| (ε = 1e‑3). Perturb *W*_{pq} → *W*_{pq}+Δ*W*, re‑run the SOC dynamics, record *a*_ans′. Sensitivity *S*_{pq}=|*a*_ans′−*a*_ans|/Δ*W*.  
   Aggregate *S* over all incoming weights to *a*_ans (or over weights linked to supporting premises) to obtain a robustness score; higher aggregate sensitivity indicates that the answer’s activation strongly depends on the input structure, i.e., the reasoning is well‑grounded.  
5. **Scoring** – Normalize the aggregate sensitivity to [0,1] and use it as the final score for each candidate answer.  

**Structural Features Parsed**  
Negations, comparatives, conditionals, causal claims, numeric values, ordering relations (>, <, =), and conjunctions/disjunctions inferred from connective tokens.  

**Novelty**  
While spreading‑activation networks, Hebbian learning, and sandpile SOC models exist separately, combining them to (i) learn propositional weights via Hebbian co‑occurrence, (ii) drive the network to a critical state through threshold avalanches, and (iii) quantify answer robustness with localized sensitivity analysis is not described in the literature to our knowledge, making the combination novel.  

**Rating**  
Reasoning: 8/10 — captures logical structure and propagates influence via avalanches, yielding nuanced scores.  
Metacognition: 6/10 — the method can monitor activation stability but lacks explicit self‑reflection on its own reasoning process.  
Hypothesis generation: 7/10 — sensitivity weights highlight which premises most affect answers, guiding hypothesis refinement.  
Implementability: 9/10 — relies only on NumPy for matrix ops and Python’s re/std‑lib for parsing; no external APIs or neural components.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Self-Organized Criticality**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Hebbian Learning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Apoptosis + Falsificationism + Self-Organized Criticality (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
