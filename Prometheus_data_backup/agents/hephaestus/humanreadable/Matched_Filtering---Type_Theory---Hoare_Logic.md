# Matched Filtering + Type Theory + Hoare Logic

**Fields**: Signal Processing, Logic, Formal Methods
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T23:10:07.671955
**Report Generated**: 2026-03-31T14:34:57.390072

---

## Nous Analysis

**Algorithm**  
We build a three‑layer scorer:

1. **Typed logical extraction** – Using a small grammar we parse the prompt and each candidate answer into a list of *typed tokens*:  
   `Token = (type, value, span)` where `type ∈ {Prop, Neg, Comparator, Conditional, Causal, Quantifier, Numeric, Conj, Disj}`.  
   The parser emits a sequence `T = [t₀, t₁, …, tₙ]`. Types enforce well‑formedness (e.g., a `Comparator` must be flanked by two `Numeric` or `Prop` tokens), which is a lightweight dependent‑type check.

2. **Hoare‑style step annotation** – Adjacent tokens are grouped into *primitive steps* `Sᵢ = (preᵢ, stmtᵢ, postᵢ)`.  
   - `preᵢ` and `postᵢ` are sets of propositions extracted from the token window (e.g., `{x>5}`).  
   - `stmtᵢ` is the central token type (e.g., a `Comparator` yields the relation `x > y`).  
   Invalid triples are discarded; the remaining list forms a *reasoning trace* `R = [S₀,…,Sₖ]`.

3. **Matched‑filter similarity** – We convert each trace into a fixed‑length feature vector `v ∈ ℝᵐ` where each dimension corresponds to a logical pattern (e.g., “Neg‑Prop”, “Conditional‑Prop‑Prop”, “Numeric‑Comparator‑Numeric”). The count of each pattern in the trace fills the vector.  
   For a reference answer we pre‑compute its vector `v_ref`. For a candidate we compute the normalized cross‑correlation (matched filter)  
   `score = max_{τ} (v_cand ⋆ v_ref)[τ] / (‖v_cand‖·‖v_ref‖)`,  
   which is equivalent to the dot product when vectors are zero‑mean and unit‑norm. The score lies in `[0,1]` and directly reflects how well the candidate’s logical structure matches the reference, maximizing signal‑to‑noise ratio of relevant patterns while suppressing irrelevant tokens.

**Parsed structural features**  
Negations (`not`, `no`), comparatives (`>`, `<`, `=`, `≥`, `≤`), conditionals (`if … then …`, `unless`), causal claims (`because`, `leads to`, `results in`), ordering relations (`before`, `after`, `precede`), numeric values and units, quantifiers (`all`, `some`, `none`), conjunction/disjunction (`and`, `or`), and modal operators (`must`, `might`).

**Novelty**  
Pure symbolic verifiers (e.g., theorem provers) ignore noisy natural‑language variation; pure similarity models (bag‑of‑words, embeddings) discard logical structure. The proposed hybrid—typed extraction → Hoare triples → matched‑filter correlation—has not been described in the literature as a unified scoring mechanism, making it novel.

**Ratings**  
Reasoning: 7/10 — captures deductive steps via Hoare triples but limited to shallow patterns.  
Metacognition: 6/10 — can flag missing pre/post conditions, yet lacks explicit self‑monitoring loops.  
Hypothesis generation: 5/10 — generates alternative traces only by shifting the correlation window, not by abductive inference.  
Implementability: 8/10 — relies solely on regex‑based parsing, numpy vector ops, and standard‑library containers; no external dependencies.

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

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
