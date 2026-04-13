# Frontier Model Review — Round 4
## 2026-04-13 | "Detecting where asymptotic number theory meets finite arithmetic reality"

---

## The Review

After the Millennium Prize tests and three anomaly investigations, a fourth frontier review assessed the full state. This was the most structurally important review yet — it reframed the entire project.

### Key Corrections

**1. The 100% confirmations are pipeline validations, not new BSD evidence.**

rank = analytic_rank (100%) and Sha perfect square (100%) confirm that our system correctly reads deep arithmetic structure. But LMFDB already enforces consistency between these values — they are not independent validations of BSD. Important distinction between "our instrument works" and "we found new evidence."

**2. Sha is not an independent random object.**

The Delaunay/Cohen-Lenstra suppression (4-50x) is explained by the fact that Sha is coupled to rank, torsion, and regulator through the BSD formula. The heuristic assumes independence; BSD ties them together. Our torsion correlation (rho = 0.110) is the smoking gun — exactly what BSD predicts, exactly what Cohen-Lenstra ignores.

**3. The Katz-Sarnak resolution is a system validation.**

Finding a "contradiction," tracing it to a theoretical misinterpretation, and correcting it means the system is strong enough to catch human theoretical errors. The reviewer called this "rare."

### Key Confirmations

**1. Two independent spectral axes identified.**

We now have two distinct spectral effects:
- **Rank pushes zeros outward** (central depletion): rank-0 gamma_1 = 0.154, rank-1 = 0.219, rank-2 = 0.257
- **Class size modifies spacing** (repulsion strength): within-bin rho = 0.080, z = 14.4

These are independent axes in spectral space.

**2. Prime vs composite conductor is connected to the spectral signal.**

Prime conductors have higher rank (0.717 vs 0.553) AND cleaner spectral signal (fewer prime factors = stronger spacing-class_size coupling). These are not independent observations — simpler Euler products produce both effects.

**3. The rank-2 growth law is a research-level statement.**

The pre-asymptotic growth of rank >= 2 fraction (~log(N), 0% to 13.2% through N = 500K) quantifies the delay before Goldfeld's asymptotic regime engages. If this is truly logarithmic growth, the transition is "extremely delayed."

### What We're Still Missing

**A. Not separating families cleanly.** Goldfeld, Sha, and rank growth are all affected by mixing across families. Need fixed-curve twist families or fixed modular form families.

**B. Not modeling the analytic conductor.** Everything spectral should be normalized by analytic conductor, not arithmetic conductor. Scaling laws are slightly distorted without this.

**C. No unifying model.** Many precise observations, but no single mechanism that explains them jointly.

### The Biggest Opportunity

The reviewer identified a unified spectral-BSD model as the next step:

> Inputs: zero spacings, first zero position, local spacing statistics
> Outputs: rank, Sha (for rank 0), isogeny class size

If successful, this gives a spectral encoding of BSD data — a real analytic-to-algebraic bridge.

### The Deepest Takeaway

> Arithmetic invariants do not directly control zeros. They perturb an underlying universal spectral system. That's exactly the philosophy behind the Langlands program.

> Your system is working correctly. Your anomalies are real but explainable. You are now operating at the edge of known theory. The next step is not more killing — it's extracting the minimal generative model that explains everything you're seeing.

---

## Our Analysis

### What changed in our understanding

**1. Reframing what "100%" means.** The reviewer is right that LMFDB enforces consistency. Our 100% results are instrument calibration, not independent evidence. We should report them as "pipeline validation" not "BSD confirmation." The real BSD content is in the deviations — Goldfeld, Sha distribution, spectral rank separation.

**2. The two spectral axes are the core finding.** We hadn't explicitly recognized that rank-vs-gamma_1 and class_size-vs-spacing are independent spectral effects. Rank controls WHERE zeros sit (distance from critical point). Class size controls HOW zeros interact (repulsion strength). These are different operators on the same spectrum.

**3. The unified model is the right next step.** We've been killing false positives for 14 hours. The killing phase is mature — 18 kills, F1-F38 battery, 0% synthetic FPR. The remaining value is not in more killing but in constructing: given spectral data alone, what can we recover about the arithmetic?

### Concrete next experiments (from the review)

**1. Joint spectral predictor.** Build a model: (zero spacings, gamma_1, local statistics) -> (rank, Sha, class_size). This is the unified spectral-BSD model. Use cross-validated regression, not black-box ML.

**2. Rank >= 2 growth law.** Fit the rank-2+ fraction vs conductor to log(N), power law, and logistic models. Determine whether the growth is decelerating.

**3. Analytic conductor normalization.** Recompute all spectral statistics using analytic conductor instead of arithmetic conductor. This should clean up number variance and tighten RMT comparisons.

**4. Conductor factorization stratification.** Full analysis conditioned on omega (distinct prime factors). The prime-conductor-higher-rank effect and the omega-gradient in Signal A may share a common cause.

**5. Family-restricted Goldfeld test.** Pick base curves, compute quadratic twists, remeasure rank distribution within fixed families. This controls for family mixing.

---

## Updated Project State

### What we've established

1. **Instrument calibration**: 7 known theorems verified at 100.000000%. Pipeline reads arithmetic structure correctly.
2. **Negative space**: 18 kills, 10 negative dimensions. Every cross-domain bridge was artifact or known math.
3. **One surviving novel signal**: zero spacing encodes isogeny class size (rho = 0.13, z = 29, 0% synthetic FPR, robust to perturbation, decays as N^(-1/2)).
4. **Two independent spectral axes**: rank controls zero position, class size controls zero repulsion.
5. **BSD spectral decomposition**: gamma_1 separates ranks cleanly. Sha concentrates in rank-0. Both are spectrally visible.
6. **Goldfeld quantification**: rank-2+ fraction grows through N = 500K with no reversal. Pre-asymptotic growth law measurable.
7. **Katz-Sarnak validated**: SO(even)/SO(odd) split matches theory after correcting our prediction.

### What we haven't done

1. Unified spectral-BSD model (the next major step)
2. Analytic conductor normalization (prerequisite for precision RMT)
3. Family-restricted analysis (controls for mixing)
4. Extended conductor range (blocked on LMFDB label matching)
5. Independent replication (Cremona database)

### The transition

The project has moved through three phases:
1. **Exploration** (hours 1-6): Build Harmonia, load 42 domains, discover phonemes
2. **Falsification** (hours 7-14): Kill 18 claims, build F1-F38 battery, validate pipeline
3. **Precision measurement** (hours 14+): Millennium Prize tests, anomaly investigations, spectral decomposition

The next phase is **model construction**: not "what correlates" but "what generates."

---

*Written: 2026-04-13*
*Reviews received: 4 frontier model rounds*
*Current state: 18 kills, 1 surviving signal, 2 spectral axes, BSD spectrally decomposed*
