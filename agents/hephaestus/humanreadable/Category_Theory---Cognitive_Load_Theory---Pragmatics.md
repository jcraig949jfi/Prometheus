# Category Theory + Cognitive Load Theory + Pragmatics

**Fields**: Mathematics, Cognitive Science, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T14:56:13.821712
**Report Generated**: 2026-03-31T17:10:38.111739

---

## Nous Analysis

**Algorithm – Pragmatic‑Functorial Load Scorer (PFLS)**  

1. **Data structures**  
   - `PromptGraph`: a directed labeled multigraph `G = (V, E)` where each node `v∈V` is a *term* (entity, predicate, or numeric literal) extracted via regex patterns; each edge `e = (src, rel, tgt)∈E` encodes a syntactic‑semantic relation (negation, comparative, conditional, causal, ordering).  
   - `AnswerGraph`: same structure built from each candidate answer.  
   - `FunctorMap`: a dictionary `F: V_Prompt → V_Answer` that maps prompt terms to answer terms preserving edge labels where possible (i.e., a graph homomorphism candidate).  
   - `LoadVector`: a 3‑element numpy array `[intrinsic, extraneous, germane]` representing cognitive‑load estimates for a given mapping.

2. **Operations**  
   - **Extraction** – Apply a fixed set of regexes to capture:  
     *Negations* (`not`, `no`, `-`), *comparatives* (`more than`, `less than`, `≥`, `≤`), *conditionals* (`if … then …`, `unless`), *causal* (`because`, `due to`, `leads to`), *ordering* (`before`, `after`, `first`, `last`). Each match creates a node and an appropriately labeled edge.  
   - **Functor construction** – For each answer, generate all possible injective mappings of prompt nodes to answer nodes that respect term type (entity vs. predicate vs. number). This is a constraint‑satisfaction problem solved by depth‑first search with pruning: a mapping is rejected if any prompt edge label cannot be found between the mapped answer nodes (preserving direction).  
   - **Load computation** – For a valid functor `F`:  
     *Intrinsic load* = number of distinct prompt relations that must be preserved (|E_Prompt|).  
     *Extraneous load* = count of answer edges not mapped from any prompt edge (|E_Answer| − |mapped|).  
     *Germane load* = number of mapped edges that also satisfy a pragmatic condition (see below).  
     Store as `LoadVector = np.array([intrinsic, extraneous, germane], dtype=float)`.  
   - **Pragmatic scoring** – Using Grice’s maxims, assign a bonus to each mapped edge:  
     *Quantity* – if the answer adds no superfluous entities beyond the prompt (penalize extra nodes).  
     *Quality* – if the edge polarity matches (negation preserved).  
     *Relation* – if the edge type is a conditional or causal and the answer respects the direction (modus ponens check).  
     *Manner* – if the answer uses the same syntactic form (e.g., both use “if … then …”).  
     Each satisfied maxim adds `+0.2` to the germane component; violations subtract `0.1` from germane.  
   - **Final score** – `score = - (intrinsic + extraneous) + germane`. Higher scores indicate lower extraneous load and higher germane (relevant) processing.

3. **Structural features parsed**  
   Negation tokens, comparative operators, conditional antecedents/consequents, causal connectives, temporal ordering markers, numeric literals with units, and quantifier phrases (“all”, “some”, “none”). These are turned into labeled edges so the functor can test preservation of logical structure.

4. **Novelty**  
   The combination of graph‑homomorphism (category‑theoretic functor) with a cognitive‑load vector and pragmatic maxim‑based germane weighting is not found in existing public reasoning‑evaluation tools. Related work uses either pure logical entailment checking or similarity metrics; none jointly model load constraints and pragmatic adequacy in a deterministic, numpy‑only algorithm.

**Ratings**  
Reasoning: 7/10 — captures logical structure via functor preservation but relies on exhaustive mapping search which may miss deeper abductive inferences.  
Metacognition: 6/10 — explicit load vector models working‑memory constraints, yet does not adaptively adjust thresholds based on learner expertise.  
Hypothesis generation: 5/10 — the system evaluates given answers; it does not generate new candidate hypotheses beyond mapping existing terms.  
Implementability: 8/10 — all components are implementable with regex, numpy arrays, and stdlib data structures; no external libraries needed.

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

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T17:08:50.503892

---

## Code

*No code was produced for this combination.*
