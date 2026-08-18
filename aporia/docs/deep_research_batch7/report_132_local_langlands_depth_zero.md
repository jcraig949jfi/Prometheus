# Deep Research Report #132: Local Langlands Depth-Zero Census

**Topic:** Depth-zero supercuspidal representations for GL(2, Q_p), p ∈ {2,3,5,7,11,13,17,19}
**Target Agent:** Harmonia
**Date:** 2026-04-23

## 1. Problem Statement

Local Langlands for GL(n, Q_p) assigns each irreducible admissible smooth π a Weil-Deligne rep rec(π) of W_{Q_p}. Supercuspidals (not arising as subquotients of parabolic inductions) correspond to irreducible Weil-Deligne reps (with N = 0). **Depth-zero** supercuspidals (Moy-Prasad depth 0) form the tractable stratum: construction requires only cuspidal reps of finite reductive quotients of parahoric subgroups.

**Target:** enumerate, for GL(2, Q_p) with p ∈ {2,3,5,7,11,13,17,19}, complete equivalence classes of depth-zero supercuspidals; cross-match to Langlands parameter (tame inertial type + Frobenius eigenvalue class); tabulate invariants (central character, conductor, formal degree). Detect whether census exhibits DeBacker-Reeder counts exactly or reveals gaps.

## 2. Literature

- **Harris-Taylor (2001)** *Geometry and Cohomology of Some Simple Shimura Varieties*: proves local Langlands for GL(n, F) via étale cohomology.
- **DeBacker-Reeder (2009)** Ann. Math. 169, *Depth-zero supercuspidal L-packets and stability*: explicit construction from tame regular elliptic Langlands parameters; enumeration backbone.
- **Yu (2001)** JAMS 14: general tame construction; depth-zero is base case (d = 0).
- **Stevens (2008)** Invent. Math. 172: exhaustiveness for classical groups; Bushnell-Kutzko types parallel.
- **Bushnell-Henniart (2006)** *The Local Langlands Conjecture for GL(2)*: standard reference.

## 3. Data Sources

- **LMFDB `local_reps`:** sparse — coverage partial for p ≥ 11, inconsistent for p=2 (wildly ramified). Not primary source.
- **GAP character table library:** `CharacterTable("GL", 2, p)` returns ordinary character table; cuspidals identified as not induced from Borel. Key depth-zero source.
- **SageMath `WeilRepresentation`** + PARI `galoisinit` on quadratic extensions of Q_p for Langlands parameters.
- **Reeder's published tables** (DeBacker-Reeder 2009 preprints) for cross-validation.

## 4. Test Design

**Phase A — Finite-group census.** For each p, extract cuspidal characters of GL(2, F_p) via GAP. p=2 yields 1, p=3 yields 3; general (p² − p)/2 cuspidal characters, only (p − 1)/2 distinct supercuspidal L-packets at depth zero (up to twisting).

**Phase B — Lift to GL(2, Q_p).** For each cuspidal θ of GL(2, F_p), compactly induce to GL(2, Z_p) · Z(Q_p), then to GL(2, Q_p). Tag: central character χ_θ, Frobenius eigenvalue (uniformizer action choice), conductor exponent (expected 2 for depth zero non-split).

**Phase C — Langlands parameters.** For each supercuspidal, compute rec(π): 2-dim irreducible Weil rep induced from unramified character of W_K where K/Q_p is unramified quadratic (unramified case) or tame ramified quadratic (ramified case). Compare Bushnell-Henniart Ch. 34.

**Phase D — Ramanujan / formal-degree sanity.** For each π, formal degree should equal (vol(maximal compact) · dim(θ))^{-1}; verify up to p = 19.

## 5. Falsification

Census fails if any:
- Cuspidal character count at p deviates from (p² − p)/2 for p odd.
- Depth-zero supercuspidal L-packet count of GL(2, Q_p) differs from DeBacker-Reeder.
- Conductor exponent differs from 2 (unramified) or 3 (tame ramified).
- Langlands parameter match not bijective on any slice.

**p=2 edge expected to require separate handling** (wild ramification at depth-zero boundary); mismatch at p=2 alone is informative, not falsifying.

## 6. Budget

~1 day wall:
- GAP character tables GL(2, F_p) for p ≤ 19: instantaneous (largest GL(2, F_19) is 360 conjugacy classes, 378 irreducible — trivial).
- Phase C bottleneck: Weil-Deligne parameters via PARI for 8 primes × ~(p−1) cases — 3-4 hours.
- DeBacker-Reeder cross-validation: 1-2 hours manual.

## 7. Expected Outcome

Table of ~80 depth-zero supercuspidals (dominated by p = 17, 19) with full Langlands-parameter annotation — **ground-truth fixture** for Harmonia local-global compatibility tests. Census expected to reproduce DeBacker-Reeder exactly; research value is machine-readable Harmonia-ingestible table LMFDB lacks, plus surfacing any p=2 anomalies worth escalation.

**Word count: 748**
