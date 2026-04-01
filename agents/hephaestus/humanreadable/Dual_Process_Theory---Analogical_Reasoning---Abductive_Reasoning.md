# Dual Process Theory + Analogical Reasoning + Abductive Reasoning

**Fields**: Cognitive Science, Cognitive Science, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T22:19:45.154556
**Report Generated**: 2026-03-31T16:34:28.528451

---

## Nous Analysis

**Algorithm**  
1. **Fast pass (System 1)** – Use a handful of regex patterns to extract primitive propositions from the prompt *P* and each candidate answer *Aᵢ*. Each proposition becomes a labeled triple ⟨s, r, o⟩ where *s* and *o* are entity strings (or numeric literals) and *r* is a relation token drawn from a fixed set: ¬ (negation), <, >, = (comparatives), if‑then (conditional), because/causes (causal), before/after (ordering), member‑of, same‑as. Store the triples in a dictionary `props[P]` and `props[Aᵢ]`.  
2. **Graph construction** – Convert each triple set into a directed labeled multigraph *G* = (V, E) where V are unique entities and E = {(s, r, o)}.  
3. **Analogical mapping (System 2)** – Compute a structure‑matching score between *G(P)* and *G(Aᵢ)* using an approximate graph‑edit‑distance algorithm:  
   * Node match cost = 0 if strings equal (after lower‑casing & stemming), else 1.  
   * Edge match cost = 0 if relation labels identical, else 1.  
   * Insertion/deletion cost = 1.  
   The Hungarian algorithm yields a minimal‑cost bijection; similarity Sᵢ = 1 − (cost / max(|Vₚ|,|Vₐ|,|Eₚ|,|Eₐ|)).  
4. **Abductive entailment check** – Run constraint propagation on *G(Aᵢ)*: apply modus ponens for conditionals (if X → Y and X present ⇒ add Y), transitivity for < / > and before/after, and symmetry for equality. Derive the closure *C(Aᵢ)*.  
   *Abductive cost* ᵢ = number of prompt triples not in *C(Aᵢ)* that must be hypothesised (added as new edges) to make *P* entailed. Each hypothesised edge incurs a penalty λ (set to 0.5).  
5. **Final score** – `scoreᵢ = α·Sᵢ − β·costᵢ` with α = 0.6, β = 0.4. Higher scores indicate answers that preserve relational structure (analogy) while requiring few explanatory abductive assumptions.

**Structural features parsed** – negations (“not”, “no”), comparatives (“more than”, “<”, “>”), conditionals (“if … then”, “implies”), causal claims (“because”, “leads to”, “causes”), numeric literals, ordering relations (“first”, “second”, “before”, “after”), equality/identity, set‑membership (“is a”, “belongs to”).

**Novelty** – While Structure‑Mapping Engine (SME), abductive logic programming, and dual‑process models exist separately, fusing them into a single, deterministic scoring pipeline that uses regex‑based proposition extraction, graph‑edit‑distance analogy, and constraint‑based abductive cost is not present in current QA‑evaluation tools; thus the combination is novel.

**Ratings**  
Reasoning: 8/10 — captures deep relational and explanatory reasoning beyond surface similarity.  
Metacognition: 7/10 — the fast/slow split mirrors monitoring vs. control, though self‑adjustment is limited.  
Hypothesis generation: 7/10 — abductive step explicitly generates minimal hypotheses to explain gaps.  
Implementability: 9/10 — relies only on regex, numpy (for Hungarian/cost arrays), and stdlib; no external APIs or neural nets.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.33** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T16:33:29.390906

---

## Code

*No code was produced for this combination.*
