# Hebbian Learning + Type Theory + Property-Based Testing

**Fields**: Neuroscience, Logic, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T19:47:35.591543
**Report Generated**: 2026-04-01T20:30:44.153107

---

## Nous Analysis

**Algorithm**  
1. **Parsing (type‑theoretic layer)** – Convert each answer into a list of typed propositions `P = [(pred, args, τ)]` where `τ ∈ {Bool, Int, Prop}`. Predicates are extracted via regex for negations (`not`), comparatives (`>`, `<`, `>=`, `<=`, `==`), conditionals (`if … then …`, `implies`), causal cues (`because`, `leads to`), ordering (`before`, `after`), and numeric literals. Each proposition is one‑hot encoded into a feature vector `f ∈ {0,1}^F` where `F` indexes the discovered predicate‑type pairs (e.g., `negation_Bool`, `comparative_Int`).  
2. **Hebbian weight matrix** – Initialise `W = zeros((F,F))`. For a reference answer `R` compute its feature mean `μ_R = average(f_R)`. Update weights with a Hebbian rule: `ΔW = η * outer(μ_R, μ_R)`; `W ← W + ΔW`. This strengthens co‑occurrence of features that appear together in correct reasoning.  
3. **Scoring** – For a candidate answer `C` compute `μ_C` similarly. Raw similarity `s = μ_C @ W @ μ_R` (numpy dot).  
4. **Property‑based testing layer** – Generate `N` mutants of `C` by randomly applying shrinking operators: flip a negation, swap args of a comparative, perturb a numeric constant by ±1, replace a conditional with its converse, or delete a causal cue. For each mutant `M` evaluate whether its parsed propositions satisfy the same constraint‑propagation rules (modus ponens, transitivity) derived from `R`. Count failing mutants `f`. Final score: `score = s / (1 + λ * f)` where `λ` controls penalty.  

**Structural features parsed** – negations, comparatives, conditionals, causal claims, ordering relations, numeric values/units, quantifiers (`all`, `some`), equality.  

**Novelty** – Combining Hebbian co‑occurrence learning with a type‑theoretic syntactic parser and property‑based mutant generation is not present in current reasoning‑scoring tools, which typically rely on neural embeddings or bag‑of‑words similarity.  

**Ratings**  
Reasoning: 8/10 — captures logical structure via typed propositions and constraint propagation, but limited to shallow syntactic patterns.  
Metacognition: 6/10 — the algorithm can self‑adjust weights via Hebbian updates, yet lacks higher‑order reflection on its own parsing failures.  
Hypothesis generation: 7/10 — property‑based mutagenesis creates systematic variations and shrinking to find minimal counter‑examples.  
Implementability: 9/10 — uses only numpy for matrix ops and std‑lib regex/random; no external dependencies.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
