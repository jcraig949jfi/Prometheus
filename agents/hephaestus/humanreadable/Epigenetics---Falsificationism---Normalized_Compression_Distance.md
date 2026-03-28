# Epigenetics + Falsificationism + Normalized Compression Distance

**Fields**: Biology, Philosophy, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T11:54:27.539686
**Report Generated**: 2026-03-27T16:08:16.411671

---

## Nous Analysis

**Algorithm**  
1. **Feature extraction** – For each candidate answer *A* run a deterministic regex‑based parser that returns a ordered list *F* = [f₁,…,fₖ] of structural primitives: negation tokens, comparative operators (“>”, “<”, “as … as”), conditional antecedent/consequent pairs, causal cue verbs (“because”, “leads to”), numeric constants, and ordering relations (“first”, “then”). Each primitive is encoded as a binary feature (present/absent) and, when applicable, a numeric value (e.g., the integer after a comparative). The result is a feature vector *v(A)* ∈ {0,1}ᵏ × ℝᵐ.  

2. **Epigenetic encoding** – Treat *v(A)* as a “genome”. Attach an epigenetic mark vector *e(A)* ∈ {0,1}ᵏ where *eᵢ = 1* indicates that feature *fᵢ* is currently “active” (expressed). Initially *e(A) = v(A)* (all extracted features are active).  

3. **Falsification‑driven mutation** – For each active feature *fᵢ* generate a mutated copy *A⁽ⁱ⁾* by toggling its epigenetic mark (*eᵢ ← 1‑eᵢ*) while leaving all other marks unchanged. If the feature carries a numeric value, replace it with a counter‑example (e.g., increment/decrement by 1 or swap inequality direction). This yields a set *M(A)* of falsification attempts, each representing a minimal “heritable” change that could disprove a claim encoded by *fᵢ*.  

4. **Scoring with Normalized Compression Distance** – Compute the NCD between the original answer string *s(A)* and each mutated string *s(A⁽ⁱ⁾)* using a standard compressor (e.g., zlib):  

   NCD(x,y) = (C(xy) – min(C(x),C(y))) / max(C(x),C(y)),  

   where C(·) is the compressed byte length. The final score for *A* is  

   S(A) = 1 – (1/|M(A)|) Σ_{A⁽ⁱ⁾∈M(A)} NCD(s(A), s(A⁽ⁱ⁾)).  

   High S(A) indicates that most minimal falsifications produce large compression distance, i.e., the answer is robustly expressed; low S(A) means a small epigenetic change greatly alters compressibility, signalling a weak or easily falsifiable claim.

**Structural features parsed**  
- Negations (“not”, “no”, “never”)  
- Comparatives and superlatives (“greater than”, “least”, “as … as”)  
- Conditionals (“if … then”, “unless”)  
- Causal claims (“because”, “leads to”, “results in”)  
- Numeric constants and quantities  
- Ordering/temporal markers (“first”, “then”, “before”, “after”)  
- Quantifiers (“all”, “some”, “none”)  

**Novelty**  
Pure NCD‑based text similarity exists (e.g., Li et al., 2004), and argument‑mining pipelines extract logical primitives, but no published work couples epigenetic‑style heritable toggling of extracted features with a falsification loop to drive compression‑based scoring. The triple combination is therefore novel in this context.

**Ratings**  
Reasoning: 7/10 — captures logical robustness via falsifiable mutations but ignores deeper semantic nuance.  
Metacognition: 5/10 — the method can estimate its own uncertainty through variance of NCD scores, yet lacks explicit self‑reflection.  
Hypothesis generation: 6/10 — mutation step yields concrete counter‑examples, serving as hypotheses to test.  
Implementability: 8/10 — relies only on regex, basic bit vectors, and zlib, all available in numpy‑free stdlib.

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
