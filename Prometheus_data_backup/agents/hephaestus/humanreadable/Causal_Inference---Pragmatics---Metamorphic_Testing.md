# Causal Inference + Pragmatics + Metamorphic Testing

**Fields**: Information Science, Linguistics, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-29T00:01:18.861466
**Report Generated**: 2026-03-31T16:23:53.927778

---

## Nous Analysis

**Algorithm**  
The tool builds three typed adjacency matrices from a parsed prompt \(P\) and each candidate answer \(A\):  

1. **Causal matrix \(C\)** – \(C_{ij}=1\) if proposition \(i\) directly causes \(j\) (extracted via regex for “if … then …”, “because”, “leads to”).  
2. **Pragmatic matrix \(Pg\)** – \(Pg_{ij}=1\) if \(i\) pragmatically implicates \(j\) (detected from scalar alternatives, e.g., “some” → “not all”, or speech‑act cues like “please”, “I suggest”).  
3. **Metamorphic matrix \(M\)** – \(M_{ij}=1\) if output \(j\) is expected to relate to output \(i\) under a predefined transformation \(T\) (e.g., doubling a numeric input should double a numeric output; ordering unchanged).  

Parsing uses the standard library `re` to extract propositions, then assigns each a node ID. Numpy is used to compute transitive closures:  
- \(C^* = \text{repeated squaring until convergence}\) (Floyd‑Warshall style) to derive implied causal effects.  
- \(Pg^*\) similarly yields closure of implicatures.  
- For \(M\), we apply the transformation \(T\) to any numeric literals found in \(P\) and check whether the resulting numeric literals appear in \(A\) with the correct scaling; a binary match fills \(M\).  

Scoring a candidate \(A\):  
- **Causal consistency** = \(\frac{\|C^*_P \land C^*_A\|_1}{\|C^*_P\|_1}\) (fraction of prompt‑derived causal inferences also present in the answer).  
- **Pragmatic felicity** = \(\frac{\|Pg^*_P \land Pg^*_A\|_1}{\|Pg^*_P\|_1}\) (proportion of expected implicatures satisfied).  
- **Metamorphic invariance** = \(\frac{\sum_k \mathbf{1}[M_{kk}^A = T(M_{kk}^P)]}{\text{#numeric relations}}\) (whether each metamorphic relation holds under \(T\)).  

Final score = weighted sum (e.g., 0.4 causal + 0.3 pragmatic + 0.3 metamorphic), normalized to \([0,1]\).  

**Structural features parsed**  
Negations (“not”, “no”), comparatives (“more than”, “less than”), conditionals (“if … then …”, “unless”), numeric values and units, causal cues (“because”, “leads to”, “results in”), ordering/temporal relations (“before”, “after”, “greater than”), quantifiers (“some”, “all”, “none”), and speech‑act markers (“please”, “I suggest”, “I claim”).  

**Novelty**  
While causal graph‑based QA, pragmatics‑aware implicature checks, and metamorphic testing for NLP each appear separately, their joint use—especially propagating causal and pragmatic closures while validating metamorphic numeric invariants—has not been combined in a single scoring engine.  

**Ratings**  
Reasoning: 8/10 — captures causal, pragmatic, and metamorphic constraints with clear algebraic operations.  
Metacognition: 6/10 — limited to checking explicit constraints; no self‑reflection on uncertainty beyond binary satisfaction.  
Hypothesis generation: 7/10 — generates implied nodes via closure, offering candidate hypotheses for further testing.  
Implementability: 9/10 — relies only on regex, numpy matrix ops, and collections; straightforward to code and debug.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T16:22:46.183113

---

## Code

*No code was produced for this combination.*
