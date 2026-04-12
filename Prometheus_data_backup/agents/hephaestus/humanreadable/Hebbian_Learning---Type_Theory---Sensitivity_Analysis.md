# Hebbian Learning + Type Theory + Sensitivity Analysis

**Fields**: Neuroscience, Logic, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T20:47:44.538642
**Report Generated**: 2026-03-31T23:05:19.906270

---

## Nous Analysis

**Algorithm**  
We build a typed proposition graph and score answers with a Hebbian‑style compatibility measure that is then tempered by a sensitivity penalty.

1. **Parsing & typing** – Using only regex (from the stdlib) we extract the following patterns from a sentence:  
   *Negation*: `\b(not|no|never)\b` → flips polarity.  
   *Comparative*: `\b(greater|less|more|fewer|higher|lower)\b\s+\w+` → creates a `Quantity` node with a bound.  
   *Conditional*: `if\s+(.+?)\s+then\s+(.+)` → yields two nodes linked by an implication edge.  
   *Causal*: `\b(causes|leads to|results in|produces)\b` → causal edge.  
   *Ordering*: `\b(before|after|precedes|follows)\b` → temporal edge.  
   Each extracted fragment becomes a **proposition** `P = (id, predicate, args, type, polarity)`. `type` ∈ {`Entity`, `Quantity`, `Boolean`} is assigned by checking whether args match a known ontology (e.g., numbers → `Quantity`, true/false → `Boolean`). All propositions are stored in a list; we also keep a mapping `idx → proposition`.

2. **Graph construction** – For every pair of propositions that appear in the same sentence we add a directed edge weighted by a Hebbian term. Let `A` be the activation vector of length *N* (number of propositions) where `A[i]=1` if proposition *i* is present in the current parse, else 0. The weight matrix `W` (numpy `float64`, shape *N×N*) is updated as  
   `ΔW = η * (A[:,None] @ A[None,:])`  
   with a small learning rate `η=0.01`. Over a set of reference (gold) answers we accumulate `W ← W + ΔW`. Thus `W[i,j]` grows when propositions *i* and *j* co‑occur, capturing Hebbian “fire together, wire together”.

3. **Scoring a candidate** – Parse the candidate answer to obtain its activation vector `a`. The raw compatibility is the quadratic form  
   `s_raw = a.T @ W @ a`  
   (equivalent to summing weights of all co‑active proposition pairs).  

4. **Sensitivity penalty** – The gradient of the score w.r.t. activations is `g = 2 @ W @ a`. For each proposition we simulate a unit perturbation (flip polarity, shift a numeric bound by ±1, or toggle a conditional antecedent) producing `Δa_i`. The induced score change is approximated by `Δs_i ≈ g·Δa_i`. We compute the L1 norm of these changes: `S = Σ_i |Δs_i|`. The final score is  
   `score = s_raw - λ * S`  
   with `λ=0.1` to discourage answers whose score is fragile to small input changes.

**Structural features parsed** – negations, comparatives, conditionals, causal claims, ordering/temporal relations, numeric thresholds, and conjunction/disjunction markers (via explicit “and/or” regex).

**Novelty** – Pure Hebbian weight updating over a typed logical graph is not common in current NLP; most connectionist models use dense embeddings, and type‑theoretic parsers rarely incorporate Hebbian learning. Adding a sensitivity‑analysis robustness term to a Hebbian score is, to the best of my knowledge, novel.

**Ratings**  
Reasoning: 8/10 — captures logical co‑activation and robustness, but relies on hand‑crafted regex patterns.  
Metacognition: 6/10 — the sensitivity term offers a crude self‑check, yet no higher‑order reflection on uncertainty.  
Hypothesis generation: 5/10 — the system can propose alternative parses via perturbation, but does not generate new hypotheses beyond existing propositions.  
Implementability: 9/10 — uses only numpy and stdlib; all operations are explicit matrix updates and regex searches.

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

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
