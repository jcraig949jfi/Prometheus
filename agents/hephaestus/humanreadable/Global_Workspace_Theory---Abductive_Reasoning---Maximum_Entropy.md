# Global Workspace Theory + Abductive Reasoning + Maximum Entropy

**Fields**: Cognitive Science, Philosophy, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T12:54:40.580726
**Report Generated**: 2026-03-31T16:31:50.517896

---

## Nous Analysis

**Algorithm**  
We build a lightweight “workspace” that holds a set of *propositional atoms* extracted from the prompt and each candidate answer. Atoms are tuples `(predicate, args, polarity)` where polarity ∈ {+1,‑1} marks negation. Extraction uses a handful of regex patterns for:  
- atomic predicates (`is(X,Y)`, `has(X,Y)`),  
- comparatives (`greater_than`, `less_than`),  
- conditionals (`if … then …`),  
- causal verbs (`causes`, `leads_to`),  
- ordering (`before`, `after`).  

Each atom becomes a binary variable in a factor graph.  

**Abductive step** – For each candidate, we generate *explanatory hypotheses* by completing missing atoms that would make the candidate logically entail the prompt. This is a bounded search: we consider all single‑atom additions drawn from a lexical ontology (WordNet‑lite) that share at least one argument with existing atoms.  

**Maximum‑Entropy step** – The set of possible worlds (assignments to all atoms) is constrained by:  
1. Hard constraints: any assignment violating a extracted logical rule (e.g., transitivity of `greater_than`, modus ponens for conditionals) gets probability 0.  
2. Soft constraints: each hypothesized atom contributes a weight w equal to its *explanatory virtue* score (inverse frequency in the ontology + specificity).  

The MaxEnt distribution over worlds is the exponential family:  
`P(world) ∝ exp( Σ_i w_i·h_i(world) )` where `h_i` is 1 if hypothesis i holds in the world.  
We compute the partition function analytically because the factor graph is tree‑structured after grounding (max 20 atoms → ≤2^20 states, feasible with numpy).  

**Scoring** – The score of a candidate is the marginal probability that all its atoms are true under the MaxEnt distribution. Candidates with higher marginal probability receive higher scores.  

**Structural features parsed**  
- Negations (`not`, `no`) → polarity flip.  
- Comparatives (`more than`, `less than`, `≥`, `≤`).  
- Conditionals (`if … then …`, `only if`).  
- Causal claims (`causes`, `leads to`, `results in`).  
- Temporal/ordering (`before`, `after`, `while`).  
- Numeric values and units (for arithmetic constraints).  

**Novelty**  
The combination mirrors existing neuro‑cognitive models (Global Workspace + Abduction) and the MaxEnt principle, but the concrete pipeline — regex‑based logical grounding, bounded abductive hypothesis generation, and exact MaxEnt marginal scoring on a tiny factor graph — has not been packaged as a standalone evaluation tool. Prior work uses either symbolic theorem provers or neural similarity; this sits between them, offering a fully interpretable, numpy‑only scorer.  

**Ratings**  
Reasoning: 8/10 — captures deductive and abductive inference with principled uncertainty handling.  
Metacognition: 6/10 — the workspace monitors constraint violations but lacks explicit self‑reflection on hypothesis quality.  
Hypothesis generation: 7/10 — bounded search yields plausible explanations; completeness limited by ontology depth.  
Implementability: 9/10 — relies only on regex, numpy linear algebra, and basic data structures; runs in milliseconds for typical prompts.

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

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T16:30:36.837270

---

## Code

*No code was produced for this combination.*
