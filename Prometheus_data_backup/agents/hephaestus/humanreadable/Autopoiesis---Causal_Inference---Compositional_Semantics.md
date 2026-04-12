# Autopoiesis + Causal Inference + Compositional Semantics

**Fields**: Complex Systems, Information Science, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T19:26:52.827879
**Report Generated**: 2026-04-01T20:30:44.143107

---

## Nous Analysis

The algorithm builds a **truth‑maintenance causal graph** from each prompt and candidate answer.  
1. **Parsing (Compositional Semantics)** – Tokenize the text, then use a handful of regex patterns to extract atomic propositions and their logical constructors:  
   * Negations (`not`, `no`) → flip a Boolean flag.  
   * Comparatives (`greater than`, `less than`, `≥`, `≤`) → produce numeric constraint nodes.  
   * Conditionals (`if … then …`) → create an implication edge.  
   * Causal verbs (`because`, `leads to`, `causes`) → create a directed causal edge with weight 1.  
   * Conjunction/disjunction (`and`, `or`) → combine child nodes under a Boolean operator node.  
   The output is an abstract syntax tree (AST) for each sentence, which is flattened into a set of **proposition nodes** (ID, type, current truth value `{T,F,?}`) and a list of **directed edges** (cause → effect).  

2. **Autopoietic Closure (self‑producing organization)** – Each node carries an internal consistency rule derived from its AST: e.g., a node marked “X ∧ ¬X” is inherently contradictory. After any truth update, the system checks whether a node’s assigned value violates its internal rule; if so, the node is flagged inconsistent.  

3. **Causal Inference & Constraint Propagation** – Using a Pearl‑style do‑calculus approximation limited to deterministic edges:  
   * **Modus Ponens**: if cause is `T` and edge exists, set effect to `T`.  
   * **Contraposition**: if effect is `F` and edge exists, set cause to `F`.  
   * Numeric constraints are propagated via simple interval arithmetic (e.g., `x > 5` and `x < 3` → inconsistency).  
   Propagation repeats until a fixed point or a contradiction is detected.  

4. **Scoring Logic** – Start with score = 1.0. For each inconsistency found (node violating its autopoietic rule or conflicting constraints) subtract 0.2. For each derived implication that matches a claim explicitly present in the candidate answer, add 0.1. Clip the final score to `[0,1]`.  

**Structural features parsed**: negations, comparatives, conditionals, causal claims, numeric thresholds, ordering relations, conjunction/disjunction.  

**Novelty**: While causal DAGs, compositional semantics, and truth‑maintenance systems exist separately, binding them with an explicit autopoietic closure constraint—where each proposition must internally preserve its own logical organization—is not standard in existing QA scoring tools.  

Reasoning: 7/10 — The method captures logical consequence and consistency but remains limited to deterministic, rule‑based inference.  
Metacognition: 5/10 — No explicit self‑reflection on confidence or uncertainty beyond binary consistency checks.  
Hypothesis generation: 4/10 — The system derives implications but does not propose novel hypotheses beyond what is entailed.  
Implementability: 8/10 — Relies only on regex, basic graph propagation, and numpy for numeric intervals; feasible within the constraints.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 8/10 |
| **Composite** | **5.33** |

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
