# Cognitive Load Theory + Mechanism Design + Metamorphic Testing

**Fields**: Cognitive Science, Economics, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T22:49:12.282933
**Report Generated**: 2026-03-31T19:49:35.722768

---

## Nous Analysis

The algorithm treats each candidate answer as a set of logical propositions extracted by regex patterns for negations (“not”, “no”), comparatives (“greater than”, “less than”, “equals”), conditionals (“if … then …”), causal cues (“because”, “leads to”), numeric tokens, and ordering expressions (“first”, “before”, “after”). Each proposition becomes a node in a directed constraint graph G. Edges encode three relation types extracted from the prompt: (1) equivalence (e.g., “X = Y”), (2) inequality (e.g., “X > Y”), and (3) implication (e.g., “if X then Y”). The adjacency matrix C ∈ {0,1}^{n×n} records whether the answer asserts each relation (C[i,j]=1 if proposition i implies j).  

From the prompt we also derive a set of metamorphic relations M by applying predefined input transformations (doubling a numeric variable, swapping two ordered items, negating a condition). For each transformation we compute the expected change in C (e.g., doubling should double all numeric‑valued entries, swapping should permute rows/columns accordingly), yielding an expected matrix Ĉ.  

Cognitive Load Theory is used to penalize excessive chunking: propositions are grouped into chunks of size ≤4 (Miller’s limit). Let k = ⌈n/4⌉ be the number of chunks; the working‑memory penalty is p_wm = max(0,(k‑4)/k).  

Mechanism‑design inspiration provides a scoring rule that rewards truth‑telling: the consistency score s_cons = 1‑‖C‑Ĉ‖_F/‖Ĉ‖_F (Frobenius norm, normalized). Germane load is approximated by forward‑chaining inference (modus ponens) on G; let s_germ be the proportion of inferred propositions that satisfy Ĉ.  

Final score (numpy only):  

```
score = s_cons * (1 - p_wm) + 0.2 * s_germ
```

Higher scores indicate answers that respect the prompt’s logical and metamorphic constraints while staying within working‑memory limits and exhibiting useful inference.

**Structural features parsed:** negations, comparatives, conditionals, causal verbs, numeric values, ordering/sequencing expressions, and quantifiers (“all”, “some”).  

**Novelty:** While constraint propagation, metamorphic testing, and mechanism design appear separately in literature (e.g., SAT solvers, MR‑based testing, scoring rules), their conjunction—using MRs to generate expected constraint matrices, applying a truth‑eliciting scoring rule, and chunking‑based cognitive‑load penalties—has not been combined in a public reasoning‑evaluation tool.  

Reasoning: 7/10 — The method captures logical consistency and metamorphic expectations but relies on hand‑crafted regex patterns that may miss complex linguistic constructions.  
Metacognition: 6/10 — Working‑memory chunk penalty provides a crude metacognitive proxy; true self‑monitoring of inference depth is not modeled.  
Hypothesis generation: 5/10 — Forward chaining yields implied propositions, but the system does not actively generate alternative hypotheses beyond those entailed.  
Implementability: 8/10 — Uses only numpy and Python’s standard library (regex, matrix ops); no external models or APIs required.

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

**Forge Timestamp**: 2026-03-31T19:47:44.651867

---

## Code

*No code was produced for this combination.*
