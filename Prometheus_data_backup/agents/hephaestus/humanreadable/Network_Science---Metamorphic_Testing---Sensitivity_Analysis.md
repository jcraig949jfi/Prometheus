# Network Science + Metamorphic Testing + Sensitivity Analysis

**Fields**: Complex Systems, Software Engineering, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T01:40:10.071732
**Report Generated**: 2026-03-31T19:46:57.659432

---

## Nous Analysis

**Algorithm – Perturb‑Graph Scoring (PGS)**  

1. **Parsing & Graph Construction**  
   - Tokenise each prompt and candidate answer with a rule‑based regex pipeline that extracts:  
     * atomic propositions (noun‑verb‑noun triples),  
     * negations (`not`, `no`),  
     * comparatives (`greater than`, `less than`, `equal`),  
     * conditionals (`if … then …`),  
     * causal cues (`because`, `leads to`, `results in`),  
     * numeric literals and units.  
   - Each proposition becomes a node `v_i` with a feature vector **f** = [is_negated, is_comparative, is_conditional, is_causal, numeric_value (or 0)].  
   - Directed edges `e_ij` are added for explicit logical relations extracted from cue phrases:  
     * `if A then B` → edge `A → B` (type = implication),  
     * `A because B` → edge `B → A` (type = cause),  
     * `A is greater than B` → edge `A → B` (type = comparative‑gt),  
     * contradictory cues (`but`, `however`) → edge `A ⇄ B` (type = conflict).  
   - The graph **G** = (V, E) is stored as adjacency matrices **A_imp**, **A_cause**, **A_comp**, **A_conf** (numpy arrays of shape |V|×|V|).

2. **Metamorphic Relations as Graph Transformations**  
   - Define a set **M** of MRs that operate on **G**:  
     * **MR₁ (Input Scaling)**: multiply all numeric_value features by k (k = 2, 0.5).  
     * **MR₂ (Negation Flip)**: toggle `is_negated` on a randomly selected subset of nodes.  
     * **MR₃ (Order Invariance)**: permute nodes that share only comparative edges (no causal direction).  
   - For each MR m∈M, generate a transformed graph **G′_m** by applying the corresponding numpy‑based feature or adjacency update.

3. **Sensitivity‑Driven Scoring**  
   - Compute a base stability score **S₀** = 1 − (L₁‑norm of difference between node‑wise eigenvector centralities of **G** and its copy after a tiny random perturbation ε = 1e‑4).  
   - For each MR, compute **S_m** = 1 − (L₁‑norm of centrality difference between **G** and **G′_m**).  
   - Final candidate score = α·S₀ + (1−α)·(1/|M|)∑_m S_m, with α = 0.6 (empirically weights baseline robustness higher).  
   - All linear algebra uses numpy (`numpy.linalg.eig`, `numpy.linalg.norm`).

**Structural Features Parsed**  
Negations, comparatives, conditionals, causal claims, numeric values, and ordering relations (explicit “greater/less than” or implicit temporal order from “before/after”).

**Novelty**  
The triple fusion is not present in existing surveys: network‑science centrality is rarely coupled with metamorphic testing as a constraint‑generation mechanism, and sensitivity analysis is usually applied to models, not to discrete logical graphs. While each component appears separately in QA‑scoring work (e.g., Argumentation‑Graph centrality, MR‑based test oracles, robustness checks via input jitter), their specific integration into a single perturb‑graph scoring pipeline is undocumented, making the approach novel.

**Ratings**  
Reasoning: 8/10 — captures logical structure and stability under meaningful transformations.  
Metacognition: 6/10 — limited self‑reflection; the method evaluates consistency but does not explicitly reason about its own uncertainty.  
Implementability: 9/10 — relies solely on regex, numpy linear algebra, and basic data structures; no external libraries or APIs needed.  
Hypothesis generation: 5/10 — the framework can suggest which MR caused a large score drop, but generating novel hypotheses beyond perturbation analysis requires additional modules.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T19:23:58.205644

---

## Code

*No code was produced for this combination.*
