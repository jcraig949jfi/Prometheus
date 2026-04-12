# Fractal Geometry + Information Theory + Property-Based Testing

**Fields**: Mathematics, Mathematics, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T20:27:07.173436
**Report Generated**: 2026-03-27T00:00:45.582535

---

## Nous Analysis

**Algorithm: Fractal‑Entropy Property‑Stability Scorer (FEPSS)**  

1. **Parsing & Graph Construction**  
   - Tokenize the candidate answer with `str.split()` (preserving punctuation as separate tokens).  
   - Build a directed labeled graph `G = (V, E)` where each token is a node `v_i ∈ V`.  
   - Add an edge `(v_i → v_j, r)` for every syntactic relation `r` extracted by a lightweight rule‑based parser (regex patterns for:  
     * negation (`not`, `no`, `never`),  
     * comparative (`more than`, `less than`, `>-`, `</`),  
     * conditional (`if … then …`, `unless`),  
     * numeric values (integers/floats),  
     * causal claim (`because`, `due to`, `leads to`),  
     * ordering (`first`, `then`, `finally`).  
   - Edge weight `w = 1` for all relations; multiple edges between same nodes are summed.

2. **Fractal Dimension Estimation**  
   - Compute the box‑counting dimension of `G`’s adjacency matrix `A` (treated as a binary image).  
   - For scales `ε = 2^k` (`k = 0…⌊log₂ N⌋`), cover the matrix with non‑overlapping squares of size `ε×ε` and count occupied boxes `N(ε)`.  
   - Fit `log N(ε) = -D·log ε + C` via least‑squares (numpy.linalg.lstsq) to obtain Hausdorff‑like dimension `D`.  
   - Lower `D` indicates more regular, self‑similar structure (e.g., strict logical chains); higher `D` signals noisy, irregular phrasing.

3. **Information‑Theoretic Scoring**  
   - Extract a feature vector `f` from `G`: counts of each relation type, presence/absence of numeric tokens, and depth of the longest directed path.  
   - Compute Shannon entropy `H = - Σ p_i log₂ p_i` where `p_i` are normalized frequencies of relation types.  
   - Higher `H` reflects richer, less predictable logical content.

4. **Property‑Based Testing Stability**  
   - Define a set of invariants derived from the question’s specification (e.g., “answer must contain exactly one numeric value”, “if X then Y must appear”, “no double negation”).  
   - Using Hypothesis‑style random generation (implemented with `random.choice` and a shrinking loop), generate `M` perturbations of the answer by:  
     * swapping adjacent tokens,  
     * inserting/deleting a stop‑word,  
     * flipping a negation,  
     * varying a numeric token within ±10 %.  
   - For each perturbed version, re‑parse, recompute `D` and `H`, and test invariants.  
   - Score stability `S = 1 - (F / M)` where `F` is the number of perturbations that violate any invariant or cause `D` to deviate > 0.2 from the original.

5. **Final Score**  
   - Combine normalized components:  
     `Score = α·(1 - D_norm) + β·H_norm + γ·S`  
     where `D_norm = (D - D_min)/(D_max - D_min)` (clipped to [0,1]), `H_norm = H / H_max` (max entropy for observed relation set), and `α+β+γ=1`.  
   - The class returns this scalar; higher scores indicate answers that are structurally regular, informationally rich, and robust to small perturbations.

**Structural Features Parsed**  
Negations, comparatives, conditionals, numeric values, causal claims, and ordering relations are explicitly captured as edge labels; the graph also encodes hierarchical depth (longest path) and token adjacency for fractal analysis.

**Novelty**  
While fractal dimension of text graphs and entropy‑based scoring appear separately in stylometry and complexity research, coupling them with a property‑based stability loop that uses shrinking perturbations to test logical invariants is not documented in existing NLP evaluation tools. Thus the combination is novel.

**Rating**  
Reasoning: 8/10 — The algorithm directly measures logical regularity (fractal dimension), informational richness (entropy), and robustness to specification‑driven perturbations, aligning with the pipeline’s emphasis on structural parsing and constraint propagation.  
Metacognition: 6/10 — The method can report which component (dimension, entropy, stability) lowered the score, enabling limited self‑diagnosis, but it does not adapt its parsing rules based on failure patterns.  
Hypothesis generation: 7/10 — By generating systematic perturbations and checking invariants, the tool behaves like a hypothesis‑driven tester, though the hypothesis space is limited to local token edits.  
Implementability: 9/10 — All steps use only `numpy` for linear algebra and the Python standard library for tokenization, random generation, and regex‑based relation extraction; no external APIs or neural models are required.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Fractal Geometry**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Information Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Property-Based Testing**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

Similar combinations that forged successfully:
- Active Inference + Pragmatics + Property-Based Testing (accuracy: 0%, calibration: 0%)
- Category Theory + Information Theory + Criticality (accuracy: 0%, calibration: 0%)
- Fractal Geometry + Cellular Automata + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-26T23:58:16.447811

---

## Code

*No code was produced for this combination.*
