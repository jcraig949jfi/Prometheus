# Charon Journal — 2026-04-10 Round 5

## 15 challenges fired, 14 complete, 1 running

### The headline: genus-3 phase transition prediction CONFIRMED

R5-6 predicted ell_c < 2 for GSp_6. R5-10 computed Frobenius for 100 genus-3 curves via newly-installed SageMath. R5-15 tested the prediction: mod-2 congruence graph is EMPTY (0 genuine edges). The critical-prime scaling law works across three ranks (GL_2, GSp_4, GSp_6).

### Complete results

| # | Challenge | Finding |
|---|-----------|---------|
| R5-1 | Partial correspondence | DEAD across all domain pairs. No hidden fractional bridges. |
| R5-2 | Cross-level lifts | Branching factor = 1.000 universally. 4 depth-2 survivors are level-raising mod-15. |
| R5-3 | Constraint interference | CONSTRUCTIVE (1.37-15.84x). Squarefree conductor = only destructive channel. |
| R5-5 | CM field detector | 76% accuracy on 9-class problem. Detects families not individual discriminants. |
| R5-6 | Phase transitions | SHARP and SIMULTANEOUS. GSp_6 prediction: ell_c < 2. |
| R5-7 | Algebraic vs operadic | ORTHOGONAL. 0% homogeneity both directions. |
| R5-8 | Verbs by family | Equal = local tightness, And = constraint depth. QM = theta territory, RM = Eisenstein. |
| R5-9 | Spectral scaling law | EXISTS (1.83x) but weak. Orthogonal to mod-p (r=0.09). |
| R5-10 | Genus-3 Frobenius | 100 curves computed. 58 generic, 42 non-generic across 8 ST classes. |
| R5-11 | Prime entanglement | Independence broken at clustering level (z=272). NOT explained by Galois image. |
| R5-12 | Triangle collapse | Super-exponential. Triangles annihilate discretely. 8,075x excess at ell=2. |
| R5-13 | Asymptotic classifier | Linear regime = strongest enrichment (1.61x). EC recovers Hasse bound (α=0.49). |
| R5-14 | Dual representation | Two-layer: degree couples algebra+spectrum; mod-p is genuinely independent. |
| R5-15 | Genus-3 phase test | **PREDICTION CONFIRMED.** Mod-2 empty for genus-3. ell_c < 2 verified. |

### Key structural insights from Round 5

1. **Mathematical classification has 2 independent axes** (not 3): recurrence degree couples algebra and spectrum (ARI=0.878 at degree 2), while mod-p arithmetic is genuinely orthogonal (ARI~0.07). Within each degree stratum, algebra and spectrum are redundant.

2. **Cross-prime entanglement is real but tiny** (0.016 bits) and NOT explained by Galois image. The hidden variable is likely level structure (bad-prime cascade). Exact cluster membership remains independent; clustering TENDENCY is weakly coupled.

3. **Phase transitions in congruence structure are discrete** — triangles annihilate in one prime step, not gradual decay. The critical prime scales with group rank and the transition is CONFIRMED predictive across three ranks.

4. **Verb distributions track endomorphism algebra.** Equal measures local equational tightness. And measures cross-constraint depth. QM lives in theta territory; RM in Eisenstein. The operadic skeleton is a measurable shadow of the endomorphism algebra.

5. **The EC↔OEIS gap is total.** No partial correspondences (R5-1), no functorial bridges (R4-3), no fractional alignment at any prime. The separation is real and deep.

### SageMath installed
SageMath 10.7 working in WSL via conda. Genus-3 Frobenius computation feasible at 0.2s/curve for p≤97. Unblocks Richelot, Hida, higher-weight Hecke, L-values.

### Session running total: 55 challenges complete, 56 fired across 5+ rounds.

---

*Round 5: the instrument made a prediction and tested it on fresh data from a new domain. The prediction held. That's science.*
