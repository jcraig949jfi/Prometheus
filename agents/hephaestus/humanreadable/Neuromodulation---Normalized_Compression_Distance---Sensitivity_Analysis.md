# Neuromodulation + Normalized Compression Distance + Sensitivity Analysis

**Fields**: Neuroscience, Information Science, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T19:54:13.586181
**Report Generated**: 2026-04-01T20:30:44.155108

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex‑based extraction to build a directed proposition graph `G = (V, E)`. Each node `v` holds a proposition string and a type tag from `{neg, comp, cond, num, caus, ord}`. Edges encode logical relations (e.g., `A → B` for conditionals, `A ≡ B` for comparatives).  
2. **Reference compression** – For the gold‑standard answer, compute its byte‑string `s_ref` (UTF‑8) and its compressed length `L_ref = len(zlib.compress(s_ref))`. Do the same for each candidate `s_i` → `L_i`.  
3. **Normalized Compression Distance (NCD)** – `NCD_i = (L_{ij} - min(L_i, L_j)) / max(L_i, L_j)` where `L_{ij}=len(zlib.compress(s_i + s_ref))`. Base similarity `S_i = 1 - NCD_i`.  
4. **Sensitivity analysis** – For each candidate, generate `k` perturbed versions by randomly applying one of: token swap, token deletion, or synonym substitution (using a tiny WordNet‑style list from the std lib). Compute `S_i^p` for each perturbation and define sensitivity `σ_i = std(S_i^p)` (numpy std). Low σ → robust answer.  
5. **Neuromodulatory gain** – Assign a gain `g_t` to each proposition type `t` (e.g., `g_caus=0.3`, `g_neg=0.1`, others 0). For a candidate, sum gains weighted by the proportion of its propositions of each type: `G_i = Σ_t g_t * (|V_t|/|V|)`. This mimics dopamine/serotonin‑like gain control that amplifies salient logical structures.  
6. **Final score** – `Score_i = S_i * (1 + G_i) / (1 + σ_i)`. Higher scores reward semantic similarity, logical richness, and robustness to perturbations.

**Structural features parsed** – negations (`not`, `no`), comparatives (`more than`, `less than`), conditionals (`if … then …`, `unless`), numeric values and units, causal claims (`because`, `leads to`, `results in`), ordering relations (`before`, `after`, `greater than`). All are captured as typed nodes/edges in `G`.

**Novelty** – While NCD‑based similarity and sensitivity‑to‑perturbation appear separately in compression‑based plagiarism detection and adversarial robustness work, coupling them with a neuromodulatory gain scheme that weights logical proposition types is not documented in the literature. It resembles attention‑gain models but operates purely on symbolic, compression‑derived metrics, making the combination novel for reasoning‑answer scoring.

**Ratings**  
Reasoning: 7/10 — captures logical structure and robustness, but relies on approximate compression and simple perturbations.  
Metacognition: 5/10 — provides a sensitivity estimate but lacks explicit self‑monitoring of uncertainty.  
Hypothesis generation: 4/10 — focuses on scoring given candidates; does not propose new answers.  
Implementability: 8/10 — uses only regex, numpy, zlib, and std‑lib; straightforward to code in <150 lines.

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
