# Dual Process Theory + Self-Organized Criticality + Compositional Semantics

**Fields**: Cognitive Science, Complex Systems, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T22:23:26.937087
**Report Generated**: 2026-03-31T14:34:57.352075

---

## Nous Analysis

1. **Algorithm**  
   - **Data structures**  
     * `tokens`: list of word strings from the prompt and each candidate answer.  
     * `props`: list of proposition objects extracted via regex; each prop has fields `id`, `text`, `type` (negation, comparative, conditional, causal, order, numeric), and `args` (sub‑prop IDs or literals).  
     * `graph`: adjacency list `graph[src] = [(dst, w), …]` where `w∈[0,1]` encodes logical strength (e.g., 1.0 for material implication, 0.5 for conjunction).  
     * `node`: dict `node[id] = {'S1':float, 'S2':float, 'theta':float}` where `S1` is the fast intuition score, `S2` the slow deliberation score, and `theta` a firing threshold.  
   - **Operations**  
     1. **Extraction** – Apply a fixed set of regex patterns to capture:  
        * Negations (`\bnot\b`, `\bno\b`)  
        * Comparatives (`\bmore\b|\bless\b|\bgreater\b|\blesser\b`, numeric patterns)  
        * Conditionals (`if.*then\b`, `\bunless\b`)  
        * Causal cues (`\bbecause\b`, `\bleads to\b`, `\bresults in\b`)  
        * Ordering (`\bbefore\b`, `\bafter\b`, `\bfirst\b`, `\blast\b`)  
        * Numeric values (`\d+(\.\d+)?`).  
        Each match creates a proposition; logical connective words create edges with appropriate weights.  
     2. **Initialization** – For each prop, compute `S1 = cosine(tfidf(prop.text), tfidf(expected_answer_text))` using only numpy (no external models). Set `S2 = 0`. Set `theta = 0.2` (empirically chosen).  
     3. **SOC propagation** – Repeat until no node fires:  
        * For each node `i`, compute `Δ = Σ_{j→i} w_{ji} * (S2_j - S1_j)`.  
        * If `|Δ| > theta_i`, fire: `S2_i += Δ`; propagate `Δ` to all outgoing neighbors (add to their pending Δ).  
        * This is the avalanche rule; the system self‑organizes to a critical state where further firings cease.  
     4. **Scoring** – Let `M` be the set of props that match the candidate answer’s semantic head (exact token match or synonym via a static word‑list). Final score = `Σ_{i∈M} S2_i / Σ_i max(S2_i,0)`. Scores are normalized to [0,1].  

2. **Parsed structural features** – Negations, comparatives, conditionals, causal claims, ordering relations, explicit numeric values, and conjunction/disjunction markers.  

3. **Novelty** – Dual‑process modeling and SOC have been studied separately in cognition and physics; compositional semantic graphs are standard in NLP. Coupling System 1/System 2 activation with an SOC avalanche on a logically extracted graph has not, to our knowledge, been used for answer scoring, making the combination novel in this context.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and heuristic‑deliberate interaction but relies on shallow regex parsing.  
Metacognition: 5/10 — the algorithm monitors its own activation (theta) yet lacks explicit self‑reflection on confidence.  
Hypothesis generation: 4/10 — generates updates via avalanche but does not propose alternative interpretations beyond propagation.  
Implementability: 8/10 — uses only numpy and the standard library; all steps are deterministic and straightforward to code.

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
