# Analogical Reasoning + Self-Organized Criticality + Hebbian Learning

**Fields**: Cognitive Science, Complex Systems, Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T01:26:56.103276
**Report Generated**: 2026-03-27T06:37:42.134628

---

## Nous Analysis

**Algorithm**  
1. **Text → Relational Graph** – Using a handful of regex patterns we extract triples *(subject, predicate, object)* from the prompt and each candidate answer. Predicates are categorized into: negation, comparative, conditional, causal, ordering, and numeric‑value. Each unique entity gets an integer ID; we build a node‑feature matrix **F** ∈ ℝⁿˣᵏ (one‑hot predicate type + normalized numeric value if present) and an adjacency tensor **E** ∈ {0,1}ⁿˣⁿˣᵖ where *p* is the number of predicate types.  
2. **Hebbian Weight Matrix** – Initialize a symmetric weight matrix **W** = 0. For every parsed sentence we compute an activation vector **a** ∈ ℝⁿ (a_i = 1 if node i appears, else 0). Update **W** ← **W** + η · (**a** **a**ᵀ) (η = 0.05). This implements “neurons that fire together wire together” on the relational graph.  
3. **Self‑Organized Criticality (SOC) Avalanche** – Maintain a current activation **s** (initially **a**). Choose a threshold θ = 1.5. While any s_i > θ:  
   - topple node i: distribute its excess equally to all neighbors j where E[i,j,:] > 0, i.e., s_j ← s_j + (s_i‑θ)/deg_i;  
   - set s_i ← s_i‑θ.  
   The process repeats until all s_i ≤ θ, producing an avalanche pattern **s*** that highlights which relational structures have become critical.  
4. **Analogical Scoring** – For a candidate answer we repeat steps 1‑3 to obtain (**Fᶜ**, **Eᶜ**, **Wᶜ**, **s***ᶜ). Structural similarity is computed as the normalized trace of the Hebbian‑weighted overlap:  
   \[
   Sim_{struct}= \frac{\operatorname{tr}\!\big({F}^{T} W {F}^{c}\big)}{\|{F}\|_F \|{F}^{c}\|_F}
   \]  
   Activation overlap is the cosine similarity between the post‑avalanche vectors:  
   \[
   Sim_{act}= \frac{{s}^{*}\!\cdot\!{s}^{c*}}{\|{s}^{*}\|\|{s}^{c*}\|}
   \]  
   Final score = 0.6·Sim_struct + 0.4·Sim_act (weights tuned on a validation set). All operations use only NumPy and the Python standard library.

**Structural Features Parsed** – negations (“not”, “no”), comparatives (“greater than”, “less than”, “more than”), conditionals (“if … then …”), causal claims (“because”, “leads to”, “results in”), ordering relations (“first”, “before”, “after”, “preceded by”), numeric values (integers, decimals, percentages), and explicit entities (proper nouns, common nouns).  

**Novelty** – Purely symbolic spreading‑activation models (e.g., Collins & Quillian) and analogical mapping (SME) exist, but they lack a self‑organized criticality layer that dynamically re‑weights relations via avalanche dynamics. Combining Hebbian weight updates with SOC‑driven constraint propagation yields a distinct, parameter‑light mechanism not described in prior work.  

**Rating**  
Reasoning: 8/10 — captures relational structure and propagates critical constraints, yielding nuanced similarity beyond surface overlap.  
Metacognition: 6/10 — the method can monitor activation saturation (avalanche size) as a confidence signal, but lacks explicit self‑reflective loops.  
Hypothesis generation: 5/10 — generates implicit hypotheses via avalanche spread, yet does not propose new symbolic candidates autonomously.  
Implementability: 9/10 — relies solely on regex, NumPy linear algebra, and simple loops; no external libraries or training data required.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Analogical Reasoning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Self-Organized Criticality**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Hebbian Learning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Analogical Reasoning + Hebbian Learning: strong positive synergy (+0.262). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Dialectics + Mechanism Design (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Mechanism Design + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
