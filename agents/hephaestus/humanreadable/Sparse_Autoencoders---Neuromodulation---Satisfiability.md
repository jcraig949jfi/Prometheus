# Sparse Autoencoders + Neuromodulation + Satisfiability

**Fields**: Computer Science, Neuroscience, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T15:11:21.492054
**Report Generated**: 2026-03-31T16:21:16.547113

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Feature Extraction** – Use a handful of regex patterns to pull atomic propositions from a prompt and each candidate answer:  
   - Literals: `P`, `¬P` (negation)  
   - Comparatives: `X > Y`, `X < Y` → encoded as `gt(X,Y)` / `lt(X,Y)`  
   - Conditionals: `if A then B` → implication `A → B`  
   - Causals: `A because B` → `B → A`  
   - Numeric values: `count = 3` → unary predicate `cnt3`  
   - Ordering: `before`, `after` → `ord_before(A,B)` etc.  
   Each distinct literal gets an index; a candidate answer becomes a binary vector **x** ∈ {0,1}^d indicating which literals are present.

2. **Sparse Autoencoder Dictionary** – Learn a dictionary **D** ∈ ℝ^{k×d} (k ≫ d) from a corpus of prompts using an iterative shrinkage‑thresholding algorithm (ISTA) with L1 penalty λ. **D** maps a dense code **z** ∈ ℝ^k to the literal space: **x̂** = Dᵀz. The code is forced sparse (‖z‖₀ ≤ s) by the soft‑threshold step.

3. **Neuromodulatory Gain** – Compute a context‑dependent gain vector **g** ∈ ℝ^k from global signal statistics of the prompt (e.g., proportion of negations, presence of modal verbs). Gain modulates the dictionary rows: **D̃** = diag(g) **D**. This implements a gain‑control mechanism akin to dopamine/serotonin adjusting neuronal responsivity.

4. **Weighted SAT Construction** – For each active literal i in **x**, compute a weight w_i = |z_i|·g_i (non‑zero only for sparse code entries). Build a weighted CNF where each clause corresponds to a logical rule extracted from the prompt (e.g., `gt(X,Y) ∧ lt(Y,Z) → gt(X,Z)`). Clause weight = sum of weights of its literals.

5. **Scoring via Weighted MaxSAT** – Run a unit‑propagation based MaxSAT solver (pure Python/numpy) that prefers assignments maximizing total satisfied clause weight. The solver returns:  
   - **S** = total weight of satisfied clauses  
   - **U** = size of a minimal unsatisfiable core (found via clause deletion)  
   Final score = S – α·U, with α a small penalty (e.g., 0.1) to discourage inconsistent answers.

**Structural Features Parsed** – negations, comparatives, conditionals, causal connectives, numeric constants, ordering/temporal terms, quantifiers (all/some), and conjunction/disjunction patterns.

**Novelty** – While sparse coding, neuromodulatory gain control, and weighted MaxSAT each appear separately, their tight coupling—where a learned sparse dictionary is dynamically gated by neuromodulatory signals to produce weighted clause scores—has not been described in existing SAT‑based or neuro‑inspired reasoning tools.

**Rating**  
Reasoning: 7/10 — captures logical structure and uncertainty via weighted SAT, but relies on hand‑crafted regex patterns that may miss complex language.  
Metacognition: 6/10 — gain vector provides rudimentary confidence monitoring; no explicit self‑reflection loop.  
Hypothesis generation: 5/10 — sparse code yields alternative literal sets, yet no mechanism for proposing novel hypotheses beyond re‑weighting existing literals.  
Implementability: 8/10 — all components (ISTA, regex parsing, unit‑propagation MaxSAT) run with numpy and the Python standard library; no external dependencies.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: unproductive
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
