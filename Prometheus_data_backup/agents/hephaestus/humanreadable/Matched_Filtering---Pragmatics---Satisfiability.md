# Matched Filtering + Pragmatics + Satisfiability

**Fields**: Signal Processing, Linguistics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T17:53:57.853532
**Report Generated**: 2026-03-31T19:54:52.091219

---

## Nous Analysis

**Algorithm – Pragmatic‑Matched‑Filter SAT Scorer (PMFSS)**  
1. **Parsing & representation** – Using only regex and the stdlib, each prompt and candidate answer is turned into a *predicate‑feature matrix* \(F\in\{0,1\}^{k\times m}\). Rows correspond to extracted structural primitives (negation, comparative, conditional, numeric constant, causal arrow, ordering pair); columns correspond to answer slots (subject, predicate, object, modifier). A value 1 indicates the primitive appears in that slot.  
2. **Context template (matched filter)** – From the prompt we build a *template vector* \(t\in\mathbb{R}^{k}\) where each entry is a weight derived from Gricean pragmatics:  
   - Quantity: weight ∝ inverse frequency of the primitive in the prompt (rare primitives get higher weight).  
   - Relevance: weight ∝ presence of the primitive in a causal or conditional chain detected via simple forward chaining (modus ponens) over extracted Horn‑style rules.  
   - Manner: weight ∝ clarity score (e.g., penalize ambiguous pronouns).  
   The template is normalized to unit \(L2\) norm.  
3. **Matching score** – For each candidate we compute the cross‑correlation (dot product) \(s = t^\top f\) where \(f\) is the flattened feature vector of the candidate. This is the matched‑filter output, maximising signal‑to‑noise ratio under the assumption that noise is i.i.d. Gaussian.  
4. **Satisfiability correction** – The primitive set is also encoded as a Boolean CNF formula \(\Phi\) (e.g., “if \(A > B\) then \(B < A\)”, negations as literals). Using a simple DPLL backtracking SAT solver (pure Python, no external libs), we test whether the candidate’s feature assignment satisfies \(\Phi\). If unsat, we extract a minimal unsatisfiable core (by literal removal) and compute a penalty \(p = \frac{|core|}{k}\). Final score: \(\displaystyle \text{Score}= s \cdot (1 - p)\).  
5. **Aggregation** – Scores for multiple candidates are ranked; the highest‑scoring answer is selected.

**Structural features parsed** – negations (“not”, “no”), comparatives (“greater than”, “less than”), conditionals (“if … then …”, “unless”), numeric values (integers, decimals, units), causal claims (“because”, “leads to”), ordering relations (“before”, “after”, “first”, “last”), and conjunction/disjunction cues.

**Novelty** – The approach fuses three well‑studied techniques: matched‑filter detection (signal processing), pragmatic weighting (linguistics), and SAT‑based consistency checking (automated reasoning). While each component appears individually in works like kernel‑based semantic similarity, logic‑enhanced embeddings, and pragmatic‑aware reranking, their exact combination—using a pragmatically derived template as a matched filter and correcting the output with SAT‑derived penalties—has not been published to our knowledge, making it novel in this specific formulation.

**Rating**  
Reasoning: 8/10 — The algorithm performs logical constraint propagation and numeric template matching, yielding strong deductive scoring.  
Metacognition: 6/10 — It can detect when a candidate violates its own constraints (unsat core) but does not explicitly reason about its own uncertainty beyond the penalty term.  
Hypothesis generation: 5/10 — Hypotheses are limited to extracting primitives; the method does not propose new relational structures beyond those present in the prompt.  
Implementability: 9/10 — All steps rely on regex, basic NumPy vector ops, and a pure‑Python DPLL solver; no external libraries or APIs are required.

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

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T19:54:08.323290

---

## Code

*No code was produced for this combination.*
