# Prime Number Theory + Analogical Reasoning + Metamorphic Testing

**Fields**: Mathematics, Cognitive Science, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T16:09:15.699899
**Report Generated**: 2026-03-27T03:26:11.429859

---

## Nous Analysis

**Algorithm**  
1. **Token‑to‑prime mapping** – Build a dictionary `prime_of[token]` that assigns each distinct lexical token (after lower‑casing and stripping punctuation) a unique small prime number using a pre‑computed list of the first 10 000 primes. This gives a collision‑free numeric signature for any token.  
2. **Relation extraction** – Apply a handful of regex patterns to the input prompt and each candidate answer to capture:  
   * Negations (`not`, `no`, `never`) → edge label `¬`  
   * Comparatives (`greater than`, `less than`, `≥`, `≤`) → edge label `cmp` with direction  
   * Conditionals (`if … then …`, `unless`) → edge label `→`  
   * Causal cues (`because`, `leads to`, `results in`) → edge label `⇒`  
   * Ordering (`first`, `second`, `before`, `after`) → edge label `ord`  
   * Numeric literals → node attribute `value` (float)  
   The output is a directed, labeled graph `G = (V, E)` where each node `v` stores the product of primes of its constituent tokens (`node_sig[v] = ∏ prime_of[t]`) and each edge `e` stores a relation type.  
3. **Metamorphic relation generation** – From the reference answer graph `G_ref` produce a set `M` of transformed graphs using deterministic mutations:  
   * Double every numeric node attribute (`value ← 2·value`)  
   * Swap the order of two nodes linked by an `ord` edge  
   * Invert a comparative edge (`≥` ↔ `≤`) while keeping the nodes  
   * Add or remove a negation node (`¬`) on a proposition  
   These are the metamorphic relations; they preserve the underlying logical structure but change surface form.  
4. **Scoring via prime‑based subgraph isomorphism** – For each candidate graph `G_cand` compute:  
   * **Exact match score** = number of edges `(u→v, r)` where `node_sig[u]·prime_of[r]·node_sig[v]` divides the same product in `G_ref` (using integer divisibility, a direct consequence of unique prime factorization).  
   * **Metamorphic satisfaction score** = proportion of `m ∈ M` for which `G_cand` satisfies all edges of `m` (again tested with divisibility).  
   * Final score = `0.6·exact + 0.4·metamorphic`, normalized to `[0,1]`.  
   All operations use NumPy arrays for the adjacency matrices and vectorized divisibility checks, requiring only the standard library and NumPy.

**Structural features parsed** – Negations, comparatives, conditionals, causal claims, ordering relations, and explicit numeric values. These are the primitives that the regex patterns target and that become edge labels or node attributes in the graph.

**Novelty** – Prior work treats analogical reasoning with graph embeddings or uses metamorphic testing in isolation. Combining a collision‑free prime coding of symbolic tokens (from number theory) with explicit metamorphic relation enforcement to test structural preservation is, to the best of current knowledge, not described in existing literature.

**Ratings**  
Reasoning: 8/10 — The algorithm captures logical structure and uses mathematically grounded similarity, but relies on hand‑crafted regexes that may miss complex phrasing.  
Metacognition: 6/10 — It can detect when a candidate violates a metamorphic relation (self‑checking), yet lacks explicit reasoning about its own confidence or error sources.  
Hypothesis generation: 7/10 — By generating systematic mutations of the reference, it proposes alternative valid forms, though it does not invent wholly new hypotheses beyond those mutations.  
Implementability: 9/10 — All steps are deterministic, use only NumPy and the Python standard library, and involve straightforward matrix operations and integer arithmetic.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Prime Number Theory**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Analogical Reasoning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Metamorphic Testing**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Analogical Reasoning + Dialectics + Mechanism Design (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Mechanism Design + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
