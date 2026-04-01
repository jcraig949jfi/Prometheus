# Dual Process Theory + Maximum Entropy + Sensitivity Analysis

**Fields**: Cognitive Science, Statistical Physics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T17:49:07.427668
**Report Generated**: 2026-03-31T17:55:19.907043

---

## Nous Analysis

**Algorithm – Constraint‑Driven Maximum‑Entropy Scoring with Sensitivity‑Based Robustness**

1. **Parsing & Feature Extraction (System 1‑style fast pass)**  
   - Input: prompt *P* and each candidate answer *Aᵢ*.  
   - Use a fixed set of regex patterns to extract atomic propositions and their logical modifiers:  
     *Negations* (`not`, `no`), *comparatives* (`greater than`, `less than`), *conditionals* (`if … then …`), *causal cues* (`because`, `leads to`), *ordering* (`before`, `after`), and *numeric literals*.  
   - Each extracted proposition becomes a binary feature *fⱼ* (1 if present, 0 otherwise).  
   - Build a feature matrix **F** ∈ {0,1}^{N×M} where *N* = number of answers (+1 for the prompt) and *M* = number of distinct proposition types.

2. **Constraint Specification (System 2‑style deliberate pass)**  
   - From the prompt’s feature vector **p** (row 0 of **F**) derive linear constraints on the expected feature counts under a distribution *q* over answers:  
     **E_q[fⱼ] = pⱼ** for every feature *j* that appears in the prompt (hard constraints).  
   - Optionally add soft constraints (e.g., total probability mass on answers containing a causal cue ≥ 0.6) expressed as inequalities **Aq ≤ b**.

3. **Maximum‑Entropy Distribution**  
   - Solve the convex optimization: maximize **H(q) = -∑ᵢ qᵢ log qᵢ** subject to **Eq[f] = p** and **Aq ≤ b**, **q ≥ 0**, **∑qᵢ = 1**.  
   - Using numpy, this reduces to finding the Lagrange multipliers **λ** that satisfy the moment conditions; the solution is an exponential family:  
     qᵢ ∝ exp(λ·Fᵢ).  
   - Compute **λ** via Newton‑Raphson on the dual (standard library only; numpy for linear algebra).  

4. **Scoring & Sensitivity Analysis**  
   - Base score for answer *Aᵢ*: **sᵢ = log qᵢ** (higher = more compatible with prompt constraints).  
   - Sensitivity: perturb each constraint *pⱼ* by a small ε (e.g., ±0.01) and recompute **λ**, yielding Δsᵢ/Δpⱼ ≈ (sᵢ^{pⱼ+ε} – sᵢ^{pⱼ‑ε})/(2ε).  
   - Final robustness‑adjusted score: **Ŝᵢ = sᵢ – α·‖∇ₚ sᵢ‖₂**, where α controls penalty for high sensitivity (chosen via cross‑validation on a held‑out set).  

**Structural Features Parsed**  
Negations, comparatives, conditionals, causal keywords, temporal/ordering relations, and explicit numeric values. Each maps to a distinct feature column, enabling the linear constraints that capture logical structure rather than surface similarity.

**Novelty**  
Maximum‑entropy scoring of textual answers is known in semantic parsing, but coupling it with dual‑process framing (fast feature extraction vs. slow convex solve) and explicit sensitivity‑based robustness penalties is not present in existing open‑source reasoning evaluators. The approach resembles constrained log‑linear models used in question answering, yet the sensitivity step for answer ranking is unique.

**Ratings**  
Reasoning: 8/10 — captures logical constraints via maxent, yielding principled, uncertainty‑aware scores.  
Metacognition: 6/10 — sensitivity provides a rough estimate of confidence, but no explicit self‑monitoring loop.  
Hypothesis generation: 5/10 — the method evaluates given hypotheses; it does not propose new ones.  
Implementability: 9/10 — relies only on numpy and regex; all steps are standard convex optimization with closed‑form updates.

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

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
