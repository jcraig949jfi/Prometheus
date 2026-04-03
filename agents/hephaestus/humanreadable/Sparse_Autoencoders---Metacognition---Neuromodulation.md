# Sparse Autoencoders + Metacognition + Neuromodulation

**Fields**: Computer Science, Cognitive Science, Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T23:50:04.083554
**Report Generated**: 2026-04-02T04:20:11.596533

---

## Nous Analysis

**Algorithm**  
1. **Parsing & proposition extraction** – Using a handful of regex patterns we pull out atomic propositions from the prompt and each candidate answer:  
   - Predicates (`is(X,Y)`, `has(X,Y)`)  
   - Comparatives (`X > Y`, `X = Y`)  
   - Conditionals (`if A then B`, `unless A`)  
   - Negations (`not A`, `no A`)  
   - Causal markers (`because A`, `leads to B`)  
   - Ordering/temporal (`before A`, `after A`)  
   - Numeric literals with units.  
   Each proposition is assigned a unique integer ID; the presence/absence of a proposition in a text yields a binary sparse vector **x** ∈ {0,1}^D (D ≈ number of distinct proposition types observed in a small training corpus of correct reasoning traces).

2. **Sparse Autoencoder dictionary** – Learn a dictionary **W** ∈ ℝ^{D×K} (K ≪ D) by minimizing  
   `‖X – WZ‖_F^2 + λ‖Z‖_1`  
   where X stacks the parsed vectors of correct traces, Z are the sparse codes, and λ enforces sparsity. Optimization is performed with iterative soft‑thresholding (ISTA) using only NumPy. The learned columns of **W** act as a logical feature basis (e.g., “comparative‑greater‑than”, “causal‑because‑predicate”).

3. **Encoding an answer** – For a candidate answer we compute its sparse code **z** = argmin_z ‖x – Wz‖_2^2 + λ‖z‖_1 (again ISTA). The reconstruction error **e** = ‖x – Wz‖_2^2 measures how well the answer fits the learned logical subspace.

4. **Constraint propagation (metacognitive monitoring)** – From the extracted propositions we build a directed graph G: nodes = propositions, edges = logical relations (implies, equals, greater‑than). We run a transitive‑closure‑style propagation (Floyd‑Warshall on the Boolean adjacency) to detect inconsistencies: a violation occurs when both A and ¬A become reachable, or when a numeric ordering contradicts a derived bound. Let **v** be the count of detected violations.

5. **Neuromodulatory gain** –  
   - Dopamine‑like signal **g_D** = σ(−e) · (1 − ‖z‖_0/K) (high when reconstruction is good and code is sparse).  
   - Serotonin‑like signal **g_S** = 1 − g_D (reflects uncertainty).  
   Final score:  
   `score = (1 − v / V_max) * (1 + α·g_D) − β·g_S`  
   where V_max is a normalizing max violation count, α and β are fixed gains (e.g., α=0.5, β=0.3). Higher scores indicate answers that are both logically consistent and well‑explained by the sparse logical dictionary, with metacognitive confidence modulating the influence via neuromodulatory gain.

**Structural features parsed**  
Negations, comparatives (`>`, `<`, `=`), conditionals (`if…then`, `unless`), causal claims (`because`, `leads to`), ordering/temporal (`before`, `after`), numeric literals with units, and explicit conjunctions/disjunctions.

**Novelty**  
Sparse dictionary learning for logical feature extraction, metacognitive confidence via reconstruction error/sparsity, and neuromodulatory gain modulation are each known in isolation (sparse coding for text, confidence calibration in metamemory, gain control in neuromodulation). Their tight integration into a single, numpy‑only scoring pipeline for reasoning answer evaluation has not been reported in public literature, making the combination novel in this context.

**Rating**  
Reasoning: 7/10 — captures logical structure and consistency but relies on hand‑crafted regex and linear approximations.  
Metacognition: 6/10 — confidence derived from reconstruction error/sparsity is principled yet simplistic for complex reasoning uncertainty.  
Hypothesis generation: 5/10 — the system scores given answers; it does not generate new hypotheses beyond the parsed proposition set.  
Implementability: 8/10 — all steps (regex, ISTA sparse coding, Boolean transitive closure) run with NumPy and the standard library, requiring no external APIs or neural code.

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
