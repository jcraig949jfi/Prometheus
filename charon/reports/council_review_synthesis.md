# Council Review Synthesis
## Date: 2026-04-02
## Verdict: Architecture validated. Most scientific claims need surgery.

---

## The Five Things They Agree On

1. **ARI = 0.55 is largely baked in.** Rank IS the order of vanishing at s=1/2. The first zeros literally encode rank by definition (BSD). The number 0.55 is what you'd expect from a noisy rank indicator, not a discovery. **Kill test needed:** recompute everything excluding the first zero. If structure collapses, we rediscovered BSD in disguise.

2. **Orthogonality (rho=0.04) is inflated by graph sparsity.** 62K components means most pairs are disconnected → correlation is near-zero by construction. The meaningful test is conditional rho on connected pairs only. Also: isogenous curves share L-functions, so their zero distance is 0 by definition — that's perfect correlation on those specific edges, masked by the ocean of disconnected pairs.

3. **Murmuration reproduction is a sanity check, not a finding.** It's a proven theorem now (Zubrilina 2023, Sawin-Sutherland 2025). Frame as "pipeline validation," not "independent confirmation."

4. **The character confound is MORE interesting than we thought, not less.** Claude's point: non-trivial character shifts toward Unitary symmetry, which should make zeros LESS EC-like (EC = Orthogonal), not MORE. The 3.3x enrichment goes the WRONG direction from naive Katz-Sarnak. This is unresolved, not killed. Either (a) 20 zeros can't distinguish symmetry types at this scale, or (b) there's a genuine finite-conductor effect.

5. **The architecture is the defensible contribution.** Everyone agrees: type-agnostic pipeline with pre-registered kill conditions is the real output. The scientific claims need tightening but the engineering is sound.

## The Three Things We Got Wrong

1. **The paramodular test was testing the wrong thing** (Claude). Genus-2 L-functions are degree 4; our dim-2 MFs have degree 2 L-functions. Comparing raw zero vectors between different-degree L-functions is geometrically meaningless. The null was incorrectly formulated. The kill stands, but for the wrong reason.

2. **Modularity recovery may be circular** (Claude). LMFDB computes EC zeros and MF zeros from the same L-function. We're checking whether the same L-function has the same zeros, which is guaranteed by definition. 100% recovery is not evidence that the coordinate system works — it's tautological.

3. **"Dirichlet coefficients have no continuous geometry" is too strong** (Gemini). PCA on Dirichlet coefficients DOES cluster by vanishing order (Costa 2016, arXiv:2502.10360 Feb 2025). Our k-NN on raw sequences failed, but that's our distance function being naive, not the coefficients being information-free. We killed a straw man.

## The One Experiment Everyone Says To Run

**Remove the first zero and recompute everything.**

If ARI survives: the zero geometry encodes something beyond rank-counting. Real finding.
If ARI collapses: we've built a noisy rank detector. Useful tool, not geometric discovery.

This is a single query on existing data. Highest information-per-token experiment available.

## Revised Expansion Priority (Council Consensus)

| Source | Priority 1 | Priority 2 | Priority 3 |
|--------|-----------|-----------|-----------|
| ChatGPT | Artin reps | Number fields | Dirichlet chars |
| Claude | Number fields | Artin reps | Dirichlet chars |
| Perplexity | Dirichlet chars | Artin reps | Number fields |
| Gemini | Number fields | — | — |

Split decision. Dirichlet characters for calibration (esp. character confound), number fields for generality, Artin reps for Langlands content.

## Papers We Must Read Before Claiming Anything

1. **arXiv:2502.10360** — "Machine learning the vanishing order of rational L-functions" (Feb 2025). PCA on Dirichlet coefficients clusters by vanishing order. Directly adjacent to our work. We cannot claim novelty without engaging with this.
2. **Sawin-Sutherland (arXiv:2504.12295)** — Explicit formula for EC murmuration density (April 2025). Our "reproduction" is downstream of this theorem.
3. **Oliver (2024, ICMS)** — Unsupervised learning on LMFDB data using PCA on L-function data. Adjacent to our k-NN approach.
4. **Zubrilina (2023)** — Murmuration density formula for modular forms. Proven theorem, not conjecture.

## Immediate Actions

1. **Run the first-zero ablation** — drop zero[0], recompute ARI. Binary outcome.
2. **Run conditional rho** — restrict orthogonality test to connected pairs only.
3. **Read arXiv:2502.10360** — before writing or claiming anything about Dirichlet geometry.
4. **Fix the murmuration framing** — "consistent with proven phenomenon," cite Sawin-Sutherland.
5. **Investigate the character direction** — the 3.3x enrichment goes AGAINST Katz-Sarnak prediction. Don't dismiss this.
