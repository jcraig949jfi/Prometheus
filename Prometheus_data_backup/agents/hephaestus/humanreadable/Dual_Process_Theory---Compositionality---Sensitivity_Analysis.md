# Dual Process Theory + Compositionality + Sensitivity Analysis

**Fields**: Cognitive Science, Linguistics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T10:12:08.587371
**Report Generated**: 2026-03-31T14:34:55.944915

---

## Nous Analysis

**Algorithm: Dual‑Process Compositional Sensitivity Scorer (DPCSS)**  

1. **Parsing & Representation**  
   - Tokenise the prompt and each candidate answer with a simple regex‑based splitter that preserves punctuation.  
   - Build a **typed dependency graph** `G = (V, E)` where each node `v ∈ V` is a lexical item annotated with a *semantic type* (entity, quantity, predicate, negation, comparative, conditional). Edges encode syntactic relations extracted via shallow parsers (e.g., `nsubj`, `dobj`, `advmod`, `aux`).  
   - Store node attributes in a NumPy structured array: `dtype=[('id','i4'),('type','U12'),('value','f8'),('polarity','i1')]` where `value` holds numeric quantities (or NaN for non‑numeric) and `polarity` captures negation (`-1`) or affirmation (`+1`).  

2. **Compositional Meaning Construction (System 1)**  
   - Perform a bottom‑up pass: for each production rule (e.g., `NP → Det N`, `VP → Verb NP`, `Adj → Comparative Adj`) compute a **feature vector** `f(v) = combine(f(children))` using fixed NumPy operations:  
     * concatenation for categorical features,  
     * element‑wise sum for polarity,  
     * weighted sum for numeric values (weights from a hand‑crafted lookup table).  
   - The root vector `f_root` yields a *fast intuition score* `s_intuition = dot(w_intuition, f_root)` where `w_intuition` is a preset weight vector (e.g., higher weight on polarity and numeric magnitude).  

3. **Constraint Propagation & Sensitivity (System 2)**  
   - Encode logical constraints as linear inequalities over node values:  
     * Transitivity: if `A > B` and `B > C` then `A > C` → enforce `value_A - value_C ≥ ε`.  
     * Modus ponens: if `P → Q` and `P` true then enforce `value_Q ≥ value_P`.  
     * Negation flips polarity.  
   - Assemble a sparse matrix `A` and vector `b` representing all constraints; solve the feasibility problem `A x ≤ b` using NumPy’s `linalg.lstsq` to obtain the minimal perturbation `δ` needed to satisfy constraints.  
   - Compute a **sensitivity penalty** `p_sens = ‖δ‖₂`.  

4. **Final Scoring**  
   - `score = s_intuition - λ * p_sens` (λ tuned on a validation set).  
   - Candidates are ranked by descending score; ties broken by lower perturbation magnitude (more robust).  

**Structural Features Parsed**  
- Negations (`not`, `n’t`), comparatives (`more than`, `less than`, `-er`), conditionals (`if … then`), causal markers (`because`, `leads to`), numeric values (integers, decimals, fractions), ordering relations (`greater than`, `at most`), and quantifiers (`all`, `some`).  

**Novelty**  
The triple blend is not directly documented: Dual Process Theory supplies the two‑stage scoring intuition vs. robustness; Compositionality provides the recursive feature‑building mechanism; Sensitivity Analysis supplies a concrete perturbation‑based penalty. Prior work treats these aspects separately (e.g., logic‑based solvers, compositional distributional models, or robustness checks), but no published tool unifies them in a single numpy‑only pipeline that extracts shallow syntactic graphs, propagates hard constraints, and blends intuitive and sensitivity scores.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and numeric reasoning but relies on shallow parsers; deeper semantic nuance may be missed.  
Metacognition: 6/10 — the two‑stage design mirrors System 1/System 2, yet the model lacks explicit self‑monitoring of its own uncertainty.  
Hypothesis generation: 5/10 — generates feasibility perturbations but does not propose alternative explanatory hypotheses beyond constraint satisfaction.  
Implementability: 9/10 — uses only regex, NumPy, and standard‑library data structures; no external dependencies or training required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
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
