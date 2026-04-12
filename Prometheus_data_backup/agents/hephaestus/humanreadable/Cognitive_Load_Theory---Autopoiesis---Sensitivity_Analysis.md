# Cognitive Load Theory + Autopoiesis + Sensitivity Analysis

**Fields**: Cognitive Science, Complex Systems, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T13:07:19.126865
**Report Generated**: 2026-03-27T16:08:16.459669

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage** – Using only `re` we extract atomic propositions from the prompt and each candidate answer. A proposition is a tuple `(sid, rel, oid, polarity, numeric?)` where `rel` is a predicate (e.g., “causes”, “greater‑than”, “equals”), `sid`/`oid` are subject/object identifiers, `polarity ∈ {+1,‑1}` marks negation, and `numeric?` holds a floating‑point value if the proposition contains a number. All propositions are stored in a NumPy structured array `props` with fields `id`, `subj`, `pred`, `obj`, `pol`, `val`.  

2. **Autopoietic knowledge graph** – We build a directed graph `G = (V,E)` where each vertex `v∈V` corresponds to a proposition ID. Edges represent valid inference rules extracted via regex patterns:  
   - *Modus ponens*: if `(A → B)` and `A` are present, add edge `A → B`.  
   - *Transitivity*: if `(A > B)` and `(B > C)` add edge `A > C`.  
   - *Causal chaining*: if `(A causes B)` and `(B causes C)` add edge `A causes C`.  
   The graph is closed under these rules (organizational closure).  

3. **Cognitive‑load chunking** – We simulate a working‑memory buffer of capacity `K` (default 4). Starting from the set of propositions explicitly stated in the prompt, we perform a breadth‑first forward‑chaining on `G` but only keep the first `K` newly inferred propositions at each depth; excess inferences are marked *extraneous*. The number of retained propositions gives the *intrinsic load*; the count of discarded inferences is the *extraneous load*; the number of retained propositions that also appear in the candidate answer is the *germane load*. Loads are computed as simple integer counts and stored in a NumPy array `load = [intrinsic, extraneous, germane]`.  

4. **Sensitivity analysis** – For each candidate answer we generate `M` perturbed copies (`M=20`) by:  
   - flipping the polarity of a random negation,  
   - adding Gaussian noise `N(0,σ²)` to each numeric value (`σ=0.05·|value|`).  
   For each perturbed copy we recompute the germane load (step 3). The sensitivity score is the variance of these germane loads across perturbations, `sens = np.var(germane_perturbations)`.  

5. **Final score** –  
   ```
   score = (germane_load * correctness) \
           - 0.5 * extraneous_load \
           - 0.3 * sens
   ```  
   where `correctness` is the fraction of candidate propositions that match a reference answer (exact tuple match). All operations use only NumPy arithmetic and Python sets/lists; no external models are invoked.

**Structural features parsed**  
- Negations (`not`, `no`, `-`) via polarity flag.  
- Comparatives (`greater than`, `less than`, `≥`, `≤`) as ordered relations.  
- Conditionals (`if … then …`) as implication edges.  
- Numeric values and units captured in the `val` field.  
- Causal verbs (`causes`, `leads to`, `results in`) as causal edges.  
- Ordering relations (`before`, `after`, `precedes`) as transitive edges.

**Novelty**  
While cognitive‑load metrics, autopoietic closure, and sensitivity analysis each appear separately in educational‑data mining, formal verification, and robustness testing, their conjunction—using a self‑producing inference graph whose active chunk size is bounded by working‑memory limits and whose answer quality is penalized by output variance under minimal perturbations—has not been reported in the literature. Hence the combination is novel.

**Rating**  
Reasoning: 7/10 — The algorithm captures logical structure and robustness but relies on shallow regex parsing, limiting deep semantic understanding.  
Metacognition: 6/10 — Load estimation mirrors self‑regulation awareness, yet no explicit monitoring of strategy shifts is modeled.  
Hypothesis generation: 5/10 — Forward chaining yields new propositions, but the process is deterministic and undirected, offering limited exploratory generativity.  
Implementability: 9/10 — All steps use only `re`, `numpy`, and Python built‑ins; the working‑memory bound and perturbation loops are straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
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
