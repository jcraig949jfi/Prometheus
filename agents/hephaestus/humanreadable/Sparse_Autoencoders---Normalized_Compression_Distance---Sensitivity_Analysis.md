# Sparse Autoencoders + Normalized Compression Distance + Sensitivity Analysis

**Fields**: Computer Science, Information Science, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T16:12:55.578401
**Report Generated**: 2026-03-31T14:34:56.906077

---

## Nous Analysis

**Algorithm**  
1. **Parsing & proposition extraction** – Use regex patterns to capture atomic propositions from a prompt and each candidate answer:  
   - Predicate‑argument tuples (e.g., `Verb(Subj, Obj)`)  
   - Negations (`not P`)  
   - Comparatives (`X > Y`, `X < Y`)  
   - Conditionals (`if P then Q`)  
   - Causal cues (`because P, Q`)  
   - Numeric literals and ordering chains (`X < Y < Z`).  
   Each unique proposition gets an index; a candidate is represented as a binary term‑frequency vector **x** ∈ {0,1}^|V| (V = vocabulary of propositions).  

2. **Sparse dictionary learning (Sparse Autoencoder core)** – Initialize dictionary **D** ∈ ℝ^{|V|×k} with random columns, enforce ‖d_i‖₂=1. Iterate T times:  
   - **Sparse coding**: for each **x**, run Orthogonal Matching Pursuit (OMP) to obtain code **a** with at most s non‑zeros (s ≪ k) minimizing ‖x – Da‖₂.  
   - **Dictionary update**: **D** ← **D** + η (X – DA)Aᵀ, then renormalize columns.  
   After T iterations, **D** captures disentangled features; each answer is stored as its sparse code **a** (int8 indices + float32 values).  

3. **Normalized Compression Distance (NCD)** – Convert a sparse code **a** to a deterministic byte string: pack indices as 4‑byte little‑endian ints, values as 4‑byte floats, concatenate for all non‑zeros. Apply `zlib.compress` to obtain length C(·). For two answers a,b:  
   NCD(a,b) = (C(ab) – min(C(a),C(b))) / max(C(a),C(b)).  

4. **Sensitivity analysis** – Generate m perturbed codes by randomly flipping f bits in the packed byte string (f = 1% of length). Compute NCD between original and each perturbed code; sensitivity σ = std(NCD_perturb).  

5. **Score** – For a candidate answer c against a reference answer r:  
   score(c) = – NCD(r,c) × (1 – σ_c).  
   Higher (less negative) scores indicate better semantic alignment and robustness.  

**Structural features parsed** – negations, comparatives (>/<, ≤/≥), conditionals (if‑then), causal markers (because, leads to), numeric literals, ordering chains, conjunctions, and quantifiers (all, some).  

**Novelty** – While sparse autoencoders, NCD, and sensitivity analysis appear separately in representation learning, similarity metrics, and robustness testing, their joint use to produce a sparse, compressibility‑based, perturbation‑aware scoring function for reasoning answers has not been reported in the literature. Existing tools rely on bag‑of‑words, TF‑IDF cosine, or neural embeddings; this combination introduces explicit logical proposition encoding, learned disentangled features, compression‑based distance, and a quantified robustness term, making it novel.  

**Ratings**  
Reasoning: 7/10 — captures logical structure via proposition parsing and sparse coding, but OMP is approximate and may miss deep inference.  
Metacognition: 6/10 — sensitivity analysis provides a robustness proxy, yet it does not model higher‑order self‑reflection about answer correctness.  
Hypothesis generation: 5/10 — the method scores given candidates; it does not generate new hypotheses or alternative explanations.  
Implementability: 8/10 — uses only numpy for matrix ops and stdlib (zlib, re, random) for parsing, compression, and perturbation; feasible to code in <200 lines.

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
