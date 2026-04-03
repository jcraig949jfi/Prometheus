# Immune Systems + Pragmatics + Free Energy Principle

**Fields**: Biology, Linguistics, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T04:51:13.087411
**Report Generated**: 2026-04-01T20:30:43.592126

---

## Nous Analysis

**Algorithm**  
1. **Parsing layer** – Using only `re` from the standard library, the prompt and each candidate answer are turned into a list of *propositional atoms*. Regex patterns capture:  
   - Predicate‑argument structures (`(\w+)\s+\(([^)]+)\)`)  
   - Negations (`not\|\!`)  
   - Comparatives (`>|<|>=|<=|==|!=`)  
   - Conditionals (`if\s+(.+?)\s+then\s+(.+)`)  
   - Causal connectors (`because|due to|leads to|results in`)  
   - Ordering/temporal words (`before|after|while`)  
   - Quantifiers (`all|some|none|every`)  
   - Numeric tokens (`\d+(\.\d+)?`).  
   Each atom is stored as a NumPy structured array with fields: `pred` (string ID), `args` (tuple of string IDs), `polarity` (+1 for affirmative, -1 for negated), `modality` (0=assertion,1=conditional,2=causal,3=comparative).  

2. **Representation as a factor graph** – Atoms are nodes; edges are added for logical relations extracted from the same regex pass (e.g., an `if‑then` creates an implication edge, a `because` creates a causal edge). The graph is encoded as two NumPy arrays: an incidence matrix `E` (nodes × edges) and a relation‑type vector `R`.  

3. **Free‑energy scoring** – For a candidate answer `A` we compute variational free energy `F = surprise + complexity`.  
   - **Surprise** = Σ ‑log P(atom | question) over atoms present in `A` but missing from the parsed question set `Q`. With a uniform prior over the vocabulary of atoms, this reduces to a constant `c` times the Hamming distance between binary node vectors `a` and `q`: `surprise = c * np.sum(np.abs(a - q))`.  
   - **Complexity** = KL‑divergence between the answer’s node‑activity distribution `a` (treated as a Bernoulli parameter vector) and a sparsity prior `p0=0.1`: `complexity = np.sum(a*np.log(a/p0) + (1-a)*np.log((1-a)/(1-p0)))`.  
   - **Pragmatic weighting** – Before computing `F`, each node’s contribution is scaled by a pragmatic weight derived from Grice’s maxims:  
     *Quantity*: inversely proportional to node degree (prefers concise answers).  
     *Quality*: higher weight for nodes with positive polarity (avoids contradictions).  
     *Relevance*: weight proportional to the sum of edge‑type scores linking the node to any question node (causal = 2, conditional = 1.5, comparative = 1, others = 0.5).  
     *Manner*: weight increased for nodes containing explicit numeric or comparative tokens.  
     These weights are stored in a vector `w` and applied as `a_weighted = a * w`.  

4. **Clonal selection loop** – Initialise a population of candidate answer vectors (the provided options). For each generation:  
   - Compute free energy `F_i` for every candidate using the weighted vectors.  
   - Select the top 20 % (lowest `F`).  
   - Produce offspring by *mutation*: randomly flip polarity of a node with probability 0.05, or swap a node with a synonym from a predefined lexical lookup (still stdlib).  
   - Replace the worst individuals with offspring.  
   - Iterate for a fixed number of generations (e.g., 10) or until improvement < 1e‑4.  
   The final score for each candidate is `S = -F_best` (higher = better). All operations rely on NumPy array arithmetic; no external libraries are needed.

**Structural features parsed**  
Negations, comparatives (`>`, `<`, `>=`, `<=`), conditionals (`if … then`), causal claims (`because`, `leads to`), ordering/temporal relations (`before`, `after`, `while`), quantifiers (`all`, `some`, `none`), and explicit numeric values. These are the primitives that generate the nodes and edges of the factor graph.

**Novelty**  
The triad is not found in existing literature: immune‑inspired clonal selection optimisation is usually applied to antibody design, not to answer ranking; variational free energy is used in perceptual neuroscience but rarely combined with pragmatic maxim weighting for text; and pragmatic‑aware scoring is typically done via rule‑based classifiers, not through an energy‑minimisation loop. While each component appears separately, their integration into a single scoring engine is novel.

**Ratings**  
Reasoning: 7/10 — The algorithm captures logical structure and optimises via clonal selection, but surprise term is simplistic (uniform prior).  
Metacognition: 6/10 — Pragmatic weights provide a rudimentary self‑monitor of relevance and quantity, yet no explicit confidence calibration.  
Hypothesis generation: 6/10 — Mutation explores answer space, but the search space is limited to the given candidates; no generative hypothesis creation.  
Implementability: 8/10 — All steps use only `re` and NumPy; the clonal selection loop is straightforward to code and runs in milliseconds for typical MCQ sizes.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
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

**Forge Timestamp**: 2026-04-01T07:57:30.511364

---

## Code

*No code was produced for this combination.*
