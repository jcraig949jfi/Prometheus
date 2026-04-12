# Hebbian Learning + Free Energy Principle + Normalized Compression Distance

**Fields**: Neuroscience, Theoretical Neuroscience, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T01:55:16.132378
**Report Generated**: 2026-03-31T14:34:55.658585

---

## Nous Analysis

**Algorithm**  
1. **Parse the prompt** into a set of propositional nodes \(P = \{p_1 … p_K\}\) using regex patterns that capture:  
   - Atomic facts: “\(X\) is \(Y\)”, “\(X\) has property \(Y\)”.  
   - Negations: “not \(X\)”.  
   - Comparatives/ordering: “\(X\) > \(Y\)”, “\(X\) is taller than \(Y\)”.  
   - Conditionals: “if \(X\) then \(Y\)”.  
   - Causal claims: “\(X\) causes \(Y\)”.  
   - Numeric values: “\(X = 3\)”, “\(X\) ≈ \(Y\)”.  
   Each match yields a tuple \((subject, relation, object, polarity)\) stored in a list of dictionaries.

2. **Build a weighted adjacency matrix** \(W\in\mathbb{R}^{K\times K}\) (numpy array) where \(W_{ij}\) encodes the strength of the implication \(p_i \rightarrow p_j\). Initialize \(W_{ij}=0\). For every extracted conditional or causal claim, set \(W_{ij}=1\); for comparatives that imply ordering (e.g., \(X>Y\) and \(Y>Z\) ⇒ \(X>Z\)), add transitive edges later.

3. **Hebbian update**: after the initial pass, run a single Hebbian sweep over the proposition list: for each pair \((p_i,p_j)\) that co‑occur in the same prompt sentence (detected by overlapping token spans), increase \(W_{ij}\) and \(W_{ji}\) by \(\eta = 0.1\). This implements “fire together, wire together” using only numpy addition.

4. **Precision matrix** \(\Pi = \alpha I\) (scalar \(\alpha=1.0\)) represents the inverse variance of prediction error, per the Free Energy Principle.

5. **Evidence from candidate answer**: For a candidate answer string \(a\), compute its Normalized Compression Distance (NCD) to the textual form of each proposition \(p_i\) using zlib compression (standard library). Let \(d_i = NCD(a, text(p_i))\). Convert to similarity \(s_i = 1 - d_i\) (clipped to \([0,1]\)). Form evidence vector \(e = s\).

6. **Prediction and free energy**: Predicted belief vector \(b\) satisfies \(b = Wb + e\) (linear‑time solution via numpy.linalg.solve on \((I-W)\)). Prediction error \(\epsilon = e - b\). Variational free energy \(F = \frac{1}{2}\epsilon^\top \Pi \epsilon + \frac{1}{2}\log|\Pi|\) (the entropy term is constant for fixed \(\Pi\)). Score the candidate as \(-F\) (lower free energy → higher score).

**Structural features parsed**  
- Negations (“not”, “no”)  
- Comparatives and ordering relations (“greater than”, “less than”, “taller than”)  
- Conditionals (“if … then …”)  
- Causal claims (“causes”, “leads to”)  
- Numeric equality/approximation (“=”, “≈”, “about”)  
- Quantifiers (“all”, “some”, “none”) captured via simple keyword regex.

**Novelty**  
Pure Hebbian networks, predictive‑coding/FEP models, and compression‑based similarity have each been studied separately. No existing work combines a Hebbian‑updated implication graph, a free‑energy‑style belief update, and NCD‑derived evidence to score reasoning answers. Thus the combination is novel for this evaluation setting.

**Rating**  
Reasoning: 7/10 — The algorithm captures logical structure and propagates constraints, but relies on linear approximations that may miss deeper inference.  
Metacognition: 5/10 — No explicit self‑monitoring or confidence calibration beyond the free‑energy term.  
Hypothesis generation: 4/10 — Hypotheses are limited to propositional nodes; no generative search beyond similarity matching.  
Implementability: 9/10 — Uses only regex, numpy linear algebra, and zlib; straightforward to code in <150 lines.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 9/10 |
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
