# Hebbian Learning + Compositionality + Mechanism Design

**Fields**: Neuroscience, Linguistics, Economics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T18:24:05.357448
**Report Generated**: 2026-03-31T23:05:19.851760

---

## Nous Analysis

The algorithm builds a weighted, typed concept graph from each text using compositional extraction, updates edge weights with a Hebbian rule, and scores candidates via a mechanism‑design objective that rewards constraint satisfaction and penalizes violations.

**Data structures**  
- `vocab: dict[str, int]` maps lemmatized tokens to integer IDs.  
- `W: np.ndarray[float]` (|V|×|V|) stores synaptic strength for undirected co‑occurrence.  
- Separate adjacency lists `E_rel[rel_type]` hold directed triples `(s_id, o_id)` for each relation type extracted (causal, comparative, conditional, ordering, equality).  
- Activation vector `a: np.ndarray[float]` (|V|) marks concepts present in a prompt or answer (1 if present, else 0).

**Operations**  
1. **Parsing** – Apply a handful of regex patterns to capture:  
   - Negations (`not X`),  
   - Comparatives (`X is greater/less than Y`, `X > Y`),  
   - Conditionals (`if X then Y`, `X → Y`),  
   - Causal verbs (`X causes Y`, `X leads to Y`),  
   - Ordering (`X before Y`, `X after Y`),  
   - Equality (`X equals Y`),  
   - Numeric values with units.  
   Each match yields a lemma pair and a relation token; the pair IDs are added to `E_rel[rel_type]`.  
2. **Hebbian update** – For every sentence, compute outer product `np.outer(sent_a, sent_a)` and add to `W` with learning rate η (e.g., 0.01). This reinforces co‑occurring concepts.  
3. **Constraint propagation** – Compute transitive closure for causal and ordering edges using Floyd‑Warshall on boolean matrices derived from `E_rel`. Derive implied relations (e.g., if A→B and B→C then A→C).  
4. **Scoring a candidate** –  
   - **Consistency term** `C = # of candidate triples that are entailed by the prompt’s closure / total candidate triples`.  
   - **Hebbian similarity** `H = (a_prompt · a_candidate) / (‖a_prompt‖‖a_candidate‖)` (cosine, numpy dot).  
   - **Violation penalty** `V = Σ_{(s,o) in candidate¬} W[s,o]` where candidate¬ are triples contradicted by the prompt’s closure (e.g., asserting X > Y when prompt entails X ≤ Y).  
   - Final score `S = λ1*C + λ2*H - λ3*V` (λ’s set to 1.0, 0.5, 0.2). Higher S indicates better alignment.

**Structural features parsed** – negations, comparatives, conditionals, causal claims, ordering relations, equality statements, and explicit numeric values with units.

**Novelty** – Pure Hebbian weight updating combined with a mechanism‑design scoring rule is not found in current neuro‑symbolic or entailment tools; most existing systems use static similarity or learned neural models, whereas this approach derives incentives from constraint satisfaction and online synaptic‑like reinforcement, making the combination novel.

**Ratings**  
Reasoning: 7/10 — captures logical structure and propagates constraints but lacks deep quantifier or modal reasoning.  
Metacognition: 5/10 — the method provides a single score without internal confidence estimation or self‑monitoring.  
Hypothesis generation: 4/10 — it extracts and validates existing relations; generating novel hypotheses beyond the given text is limited.  
Implementability: 9/10 — relies only on regex, NumPy matrix ops, and standard containers; straightforward to code and test.

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

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T21:46:18.292902

---

## Code

*No code was produced for this combination.*
