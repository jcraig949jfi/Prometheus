# Cognitive Load Theory + Compositionality + Metamorphic Testing

**Fields**: Cognitive Science, Linguistics, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T19:49:17.965315
**Report Generated**: 2026-03-27T05:13:39.706279

---

## Nous Analysis

**Algorithm: Compositional Metamorphic Constraint Scorer (CMCS)**  

1. **Data structures**  
   - `PromptGraph`: a directed labeled multigraph where nodes are *atomic propositions* extracted from the prompt (e.g., “X > 5”, “¬rain”, “if A then B”). Edges encode syntactic‑semantic relations: *modifier* (adjective/adverb), *comparative*, *conditional*, *causal*, *order*.  
   - `AnswerGraph`: same structure built from each candidate answer.  
   - `ChunkCache`: dictionary mapping a tuple of node IDs to a *chunk vector* (numpy array of shape (d,)) that aggregates the semantic features of a sub‑graph (see step 2).  

2. **Operations**  
   - **Parsing (Compositionality)** – Use regex‑based patterns to detect tokens for negations (`not`, `no`), comparatives (`>`, `<`, `more than`, `less than`), conditionals (`if … then …`), causal cues (`because`, `leads to`), and numeric literals. Each detected token creates a node; surrounding syntactic dependencies (via a lightweight dependency‑parse using `nltk` or hand‑crafted rules) create labeled edges.  
   - **Chunking (Cognitive Load Theory)** – Recursively combine child node vectors into parent chunk vectors using a weighted sum: `chunk = W₁·vec(child₁) + W₂·vec(child₂) + …`, where weights are inversely proportional to the node’s depth (shallower = higher weight) to respect limited working memory. Leaf vectors are one‑hot encodings of the lexical category (e.g., `NUM`, `NEG`, `COND`).  
   - **Metamorphic Relations (Metamorphic Testing)** – Define a set of MRs that operate on the prompt graph:  
        *MR1 (Negation Flip)*: toggle a `NEG` edge and recompute the answer graph’s chunk vector.  
        *MR2 (Scale)*: multiply all numeric node values by a constant k > 0 and check if the answer’s comparative relations scale accordingly.  
        *MR3 (Transitive Closure)*: add implied edges via transitivity on `ORDER` or `CAUSAL` edges and verify that the answer graph remains consistent.  
   - **Scoring** – For each answer, compute a violation score: sum over all MRs of `‖chunk_prompt – chunk_answer‖₂` (numpy L2 norm) weighted by the intrinsic load of the involved sub‑graph (depth‑based). Lower total violation → higher score. Normalize to [0,1].  

3. **Structural features parsed**  
   - Negations, comparatives (`>`, `<`, `more than`), conditionals (`if … then …`), causal cues (`because`, `leads to`), numeric values, ordering relations (`before`, `after`, `first`, `last`), and conjunctive/disjunctive connectives.  

4. **Novelty**  
   - The approach unifies three well‑studied ideas: compositional semantic graphs (Montague/Frege), cognitive‑load‑driven chunking (Sweller), and metamorphic relation testing (Chen et al.). While each component appears separately in NLP (e.g., semantic parsers, cognitive‑load‑aware summarizers, MR‑based test oracles), their tight integration—using chunk vectors as the carrier for MR‑based constraint checking—has not been reported in public literature. Thus the combination is novel, though it builds on existing substrates.  

**Ratings**  
Reasoning: 8/10 — The algorithm directly evaluates logical consistency via MRs, capturing deeper reasoning than surface similarity.  
Metacognition: 6/10 — It models working‑memory limits through depth‑based chunk weighting, but lacks explicit self‑monitoring of load.  
Hypothesis generation: 5/10 — The method checks given answers; it does not propose new hypotheses beyond MR‑derived variations.  
Implementability: 9/10 — All steps rely on regex, simple graph operations, and NumPy linear algebra; no external APIs or neural models needed.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Cognitive Load Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Metamorphic Testing**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Cellular Automata + Cognitive Load Theory + Phenomenology (accuracy: 0%, calibration: 0%)
- Chaos Theory + Active Inference + Compositionality (accuracy: 0%, calibration: 0%)
- Chaos Theory + Adaptive Control + Compositionality (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
