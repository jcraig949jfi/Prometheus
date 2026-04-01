# Chaos Theory + Cellular Automata + Pragmatics

**Fields**: Physics, Computer Science, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T13:11:57.495694
**Report Generated**: 2026-03-31T14:34:57.618072

---

## Nous Analysis

The algorithm treats a sentence as a one‑dimensional cellular automaton (CA) whose cells correspond to token‑level feature bits. First, a regex‑based parser extracts a fixed set of structural predicates from the prompt and each candidate answer: negation tokens (¬), comparative markers (more/less), conditional antecedents/consequents (if…then), causal cues (because/leads to), numeric constants, and ordering relations (>, <, before, after). Each predicate maps to a binary feature; the resulting feature vector **f** ∈ {0,1}^L (L = number of distinct predicates) is the initial CA state.

The CA updates synchronously for T steps using elementary rule 110, implemented as a vectorized NumPy lookup:  
`next_state = rule110[left<<2 | center<<1 | right]` where the neighbourhood is obtained by rolling the state array. Rule 110 is Turing‑complete, allowing complex propagation of truth values across the feature grid.

To quantify sensitivity to initial conditions — the core of chaos theory — we compute an empirical Lyapunov exponent. Let **s₀^ref** be the state after T steps from the reference answer’s feature vector, and **s₀^cand** the analogous state from a candidate. Their Euclidean distance d₀ = ‖s₀^ref – s₀^cand‖ is measured at t=0. After each CA step t we compute d_t = ‖s_t^ref – s_t^cand‖. The exponent estimate is  
λ = (1/T) · log(d_T / d₀).  
A small λ indicates the candidate’s trajectory stays close to the reference’s, implying logical and pragmatic alignment. The final score is  
score = exp(−λ) · (1 + α·sim_lex) where sim_lex is a optional Jaccard overlap of content words (α ≤ 0.1) to prevent degenerate zero scores, and all operations use only NumPy and the standard library.

**Parsed structural features:** negations, comparatives, conditionals, causal markers, numeric values, ordering relations (>, <, before, after). These are extracted via regex and turned into the binary feature vector that seeds the CA.

**Novelty:** Combining CA rule‑based truth propagation with a Lyapunov‑exponent‑based distance metric for textual entailment is not present in existing work, which typically relies on static logical theorem provers or neural similarity measures; this hybrid introduces dynamical sensitivity to initial semantic perturbations.

Reasoning: 7/10 — captures logical inference via rule‑based propagation and sensitivity analysis.  
Metacognition: 5/10 — limited self‑monitoring; no explicit confidence calibration beyond λ.  
Hypothesis generation: 6/10 — can produce alternative trajectories but does not generate novel hypotheses autonomously.  
Implementability: 8/10 — relies solely on NumPy vectorization and regex, readily achievable in <200 lines.

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

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
