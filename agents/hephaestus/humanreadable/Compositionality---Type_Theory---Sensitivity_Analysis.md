# Compositionality + Type Theory + Sensitivity Analysis

**Fields**: Linguistics, Logic, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T20:09:45.361506
**Report Generated**: 2026-04-01T20:30:44.158107

---

## Nous Analysis

**Algorithm**  
1. **Parsing (Compositionality)** – Use a handful of regex patterns to extract atomic propositions from the prompt and each candidate answer:  
   - Entities (`[A-Z][a-z]+`), numeric literals (`\d+(\.\d+)?`), comparatives (`>`, `<`, `>=`, `<=`), negations (`not`, `no`), conditionals (`if … then …`), and causal markers (`because`, `due to`).  
   - Build a typed abstract syntax tree (AST) where each node stores:  
     - `type`: one of `{Entity, Quantity, Predicate, Proposition}`  
     - `value`: the extracted token or sub‑tree  
     - `children`: list of child nodes (for logical connectives).  
   The AST implements Frege’s principle: the meaning of a node is a function of its children’s meanings and the connective’s rule (e.g., `AND` → logical conjunction, `>` → numeric comparison).

2. **Type Assignment (Type Theory)** – Walk the AST bottom‑up, assigning simple dependent types:  
   - `Entity : Type`  
   - `Quantity : ℝ` (real numbers)  
   - `Predicate : Entity → Prop`  
   - `Prop : Type` (truth‑valued).  
   If a node’s children cannot be unified according to the expected function type (e.g., applying a `Predicate` to a `Quantity`), the node is marked **type‑error**. Type‑checking propagates constraints upward; any type‑error invalidates the whole candidate.

3. **Sensitivity Scoring (Sensitivity Analysis)** – For each leaf node that is a mutable atomic proposition (negation flip, numeric ±ε, comparator reversal), create a perturbed copy of the AST, re‑evaluate its truth value using the same type‑checked semantics, and record whether the overall proposition’s truth value flips.  
   - Let `k` be the number of leaves tested and `f` the number of flips. Define **robustness** `r = 1 – f/k`.  
   - Final score for a candidate = `type_correct * r`, where `type_correct` is 1 if no type‑error occurred, else 0.  
   - Candidates are ranked by this score; higher values indicate answers that are both well‑typed and robust to small perturbations.

**Structural Features Parsed**  
Negations, comparatives, conditionals, numeric values, causal markers, ordering relations (`>`, `<`, `=`), and conjunction/disjunction connectives.

**Novelty**  
While semantic parsing with regex, type checking in proof assistants, and local sensitivity analysis each exist separately, integrating them into a single scoring pipeline that enforces type‑soundness *and* quantifies robustness to input perturbations is not commonly seen in lightweight, pure‑Python evaluation tools.

**Ratings**  
Reasoning: 7/10 — captures logical structure and type safety but lacks deep semantic nuance.  
Metacognition: 5/10 — the method does not explicitly model self‑reflection or uncertainty beyond sensitivity.  
Hypothesis generation: 6/10 — can suggest alternative parses via perturbations, yet no guided search for new hypotheses.  
Implementability: 8/10 — relies only on regex, AST traversal, numpy for numeric eps, and stdlib; straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
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
