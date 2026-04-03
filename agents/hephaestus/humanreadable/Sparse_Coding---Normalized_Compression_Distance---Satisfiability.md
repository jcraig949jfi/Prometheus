# Sparse Coding + Normalized Compression Distance + Satisfiability

**Fields**: Neuroscience, Information Science, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T02:48:43.859687
**Report Generated**: 2026-04-02T04:20:11.840040

---

## Nous Analysis

**Algorithm**  
1. **Parsing & sparse encoding** – Each prompt and candidate answer is scanned with a small set of regex patterns that extract atomic propositions:  
   - `¬P` (negation) → literal `P` with sign = ‑1  
   - `P ∧ Q`, `P ∨ Q` → binary clauses  
   - `P → Q` → implication clause  
   - Comparatives (`>`, `<`, `=`) and numeric literals → arithmetic constraints  
   - Causal/linking verbs → directed edges  
   Each distinct proposition receives an index `i`. A candidate is represented by a sparse binary vector **x**∈{0,1}^d where `x_i=1` iff proposition `i` appears (sign handled by a parallel sign vector **s**). The vector is intentionally kept ≤ k non‑zeros (k≈5) by dropping low‑frequency propositions after a first‑pass count, enforcing sparsity.  

2. **Constraint construction** – From the prompt we build a conjunctive normal form (CNF) formula **F** consisting of:  
   - Unit clauses for asserted facts.  
   - Binary clauses for conditionals (`¬P ∨ Q`).  
   - Linear inequalities for numeric/comparative constraints.  
   The formula is stored as lists of clause literals (ints) and a separate list of arithmetic constraints (coeff vector, bound).  

3. **Scoring** – For each candidate answer **a**:  
   - **Sparse similarity**: compute the Normalized Compression Distance (NCD) between the bit‑string of **x_a** and the bit‑string of the prompt’s sparse vector **x_p** using Python’s `zlib.compress` (an approximation of Kolmogorov complexity). NCD ∈ [0,1]; lower means more similar.  
   - **Satisfiability penalty**: temporarily add the candidate’s literals (with signs) as unit clauses to **F** and run a pure‑Python DPLL SAT solver (with unit propagation and pure‑literal elimination). If the resulting formula is UNSAT, count the number of conflicts returned by the solver’s minimal unsatisfiable core extraction (each conflict adds 1 to the penalty).  
   - **Final score** = `α·NCD + β·(conflict_count / max_conflicts)`, with α,β∈[0,1] (e.g., α=0.6, β=0.4). Lower scores indicate better reasoning alignment.  

**Structural features parsed** – negations, conjunction/disjunction, conditionals, comparatives (`>`,`<`, `=`), numeric constants, causal verbs (“because”, “leads to”), and ordering relations (“before”, “after”).  

**Novelty** – Sparse coding of logical propositions has been explored in neuro‑symbolic work (e.g., Olshausen‑Field inspired binary embeddings), NCD is a known universal similarity metric, and SAT‑based conflict minimization is standard in automated reasoning. The novelty lies in tightly coupling a *hard‑coded* sparse bit‑vector representation with *exact* NCD compression and a *lightweight* DPLL solver to produce a single, gradient‑free score for answer ranking—a combination not reported in existing surveys of reasoning evaluation tools.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and numeric constraints via SAT, but sparse+NCD approximation may miss subtle semantics.  
Metacognition: 5/10 — the method does not monitor its own confidence or adapt thresholds; scoring is static.  
Hypothesis generation: 4/10 — generates hypotheses only as unit clauses; no exploratory abductive search beyond SAT solving.  
Implementability: 9/10 — relies solely on regex, bit‑arrays, zlib, and a pure‑Python DPLL solver; no external libraries or GPUs needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 9/10 |
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
