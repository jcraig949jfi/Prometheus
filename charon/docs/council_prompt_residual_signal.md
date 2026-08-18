# Council Prompt: The Arithmetically Independent Residual
## For: Titan Council (Claude, ChatGPT, Gemini, DeepSeek, Grok)
## Context: Experimental results from Charon, Project Prometheus, 2 April 2026

---

## Ground Rules

You are hostile reviewers. Do not validate. Do not congratulate. For every claim, provide the strongest null hypothesis that explains the result, a specific falsification test, and the minimum threshold for evidence. If you think we're wrong, say exactly where and why.

---

## The Claim (One Sentence)

The spectral tail of L-function zeros (indices 5–19) encodes rank through a channel that is independent of central vanishing, conductor, and all standard BSD invariants. This is consistent with the ILS test function support theorem, which predicts that family discrimination requires higher zeros, but goes beyond ILS by showing the tail channel is also independent of the arithmetic invariants that determine the central value.

---

## The Evidence

### Dataset
13,150 elliptic curves (deduplicated by isogeny class), conductor ≤ 5,000, with 20+ stored zeros and BSD invariants from LMFDB. 6,036 rank-0, 6,690 rank-1.

### Result 1: The Ablation (reproduced)

| Feature Vector | ARI (within conductor strata) |
|---|---|
| All 20 zeros | 0.5195 |
| Drop first zero | 0.5231 |
| Drop first two | 0.5234 |
| **Zeros 5–19 only** | **0.5280** |
| First zero ONLY | 0.2968 |

Removing central zeros monotonically improves rank clustering.

### Result 2: The Permutation Test

Shuffled rank labels within conductor strata, 100 trials:
- **Real ARI (zeros 5–19): 0.5548**
- Shuffled ARI: mean = 0.0000, std = 0.0074, max = 0.0187
- **z-score = 74.8, p < 0.0001**

The clustering is genuinely rank-dependent. Not a structural artifact.

### Result 3: The Sha Stratification Kill Test

| Population | all_20 ARI | zeros_5_19 ARI | Delta |
|---|---|---|---|
| ALL ECs | 0.5195 | 0.5280 | +0.0085 |
| Sha=1 rank-0 + all rank-1 | 0.5254 | 0.5343 | **+0.0089** |
| Sha>1 rank-0 + all rank-1 | 0.3947 | 0.3953 | +0.0006 |

Controlling Sha does not reduce the ablation improvement. Sha is not the mechanism.

### Result 4: The BSD Variance Decomposition (The Wall)

| Zero Index | R²_conductor | R²_full (cond+BSD) | BSD Increment |
|---|---|---|---|
| **1** | 0.483 | 0.544 | **+0.061** |
| 2 | 0.786 | 0.787 | +0.001 |
| 3 | 0.887 | 0.888 | +0.001 |
| 4 | 0.923 | 0.923 | +0.000 |
| 5–20 (mean) | 0.968 | 0.968 | **+0.0001** |

BSD invariants explain 6.1% of zero-1 variance beyond conductor. They explain **nothing** in the tail. This is not a gradual falloff. It is a wall between zero 1 and zeros 2+. Two completely separate information channels in the same zero vector.

### Result 5: Faltings Height Dominates Zero 1

Partial correlations with first zero (controlling for log(conductor)):

| Invariant | r | p |
|---|---|---|
| Faltings height | **−0.168** | **2.3e−39** |
| Modular degree (log) | −0.107 | 7.5e−17 |
| Sha (log) | +0.062 | 1.6e−6 |

Faltings height, not Sha, is the dominant BSD predictor for the first zero. None of these invariants predict anything in zeros 5–20.

### Result 6: Root Number Conditioning (Q10 Pre-Kill)

The strongest null hypothesis: the spectral tail merely classifies SO(even) vs SO(odd) symmetry type. We killed it by conditioning on root number.

Within root number +1 (SO(even) only), rank 0 vs rank 2:
- **ARI on zeros 5–19: 0.4913** (84 strata, 6,817 rank-0, 458 rank-2)
- Permutation null: mean = −0.004, std = 0.036
- **z-score = 14.0, p < 0.0001**

The spectral tail discriminates within SO(even). This is not symmetry type classification.

Limitation: SO(odd) at conductor ≤ 5,000 contains only rank-1 curves. The within-SO(odd) test is not possible at this conductor range.

---

## What Has Been Stripped

The spectral tail signal at ARI = 0.55 survives after removing:
1. Central vanishing (ablation — first zero removed)
2. Conductor (Ridge regression within strata)
3. Sha order (stratification test)
4. Faltings height (variance decomposition)
5. Modular degree (variance decomposition)
6. Regulator (constant for rank 0; included in decomposition)

Every mechanism the literature and prior council review suggested has been tested and eliminated. Known invariants contribute essentially zero to the tail.

---

## The Mechanism We're Naming (Before You Do)

We are NOT claiming the spectral tail is an "independent channel" from the center. It isn't. The causal mechanism is zero repulsion.

Rank-2 curves have two zeros forced near the central point. Those central zeros repel higher zeros outward through the same electrostatic repulsion that governs GUE eigenvalue spacing. Zeros 5–19 for rank-2 curves are systematically shifted relative to rank-0 curves because the central zeros push them. We removed the central zeros from the feature vector, but we did not remove their physical effect on the tail. The tail is "independent" of the center in the feature-engineering sense, not in the causal sense.

**The honest framing:** The spectral tail is a higher-fidelity encoding of rank than central vanishing, because zero repulsion distributes rank information across the full spectrum. The first zero is a noisy, degenerate encoding (binary: vanishes or doesn't). Zeros 5–19 are a continuous, 15-dimensional encoding of the same underlying rank information, propagated through repulsion and spread across multiple dimensions instead of compressed into one. K-means on 15 continuous dimensions of propagated rank signal outperforms k-means on 1 binary dimension. The monotonic improvement gradient under ablation follows directly.

**The claim becomes:** The spectral tail is a higher-fidelity encoding of rank than central vanishing, mechanistically predicted by GUE repulsion but never previously demonstrated empirically as a computational clustering phenomenon. This is consistent with ILS but goes beyond it: ILS predicts the tail distinguishes symmetry types; our data shows the tail discriminates rank within a single symmetry type (rank 0 vs rank 2 within SO(even)), which repulsion predicts but ILS does not.

**The question for the Council:** Is this repulsion-propagation mechanism sufficient to explain ARI = 0.49 within SO(even)? Or does the magnitude of the within-symmetry-class discrimination require additional structure beyond repulsion? Can you quantify what ARI repulsion alone should produce, given the known spacing statistics?

---

## What We Want From the Council

### A. Attack the residual claim

1. **Is there a BSD invariant we missed?** We tested Sha, Faltings height, modular degree, and regulator. The Tamagawa product is not in our database. Could Tamagawa numbers, which encode local reduction at bad primes, explain 6% of tail variance the way Faltings height explains 6% of zero-1 variance? Is there a mechanism by which local data at bad primes influences zeros 5–19 specifically?

2. **Is conductor scaling masking BSD signal in the tail?** The tail R²_conductor = 0.968. Only 3.2% of tail variance is unexplained by conductor. If BSD invariants correlate with conductor (they do), our "BSD increment" may undercount BSD's contribution because the conductor model already captures it. How do we test for this collinearity? Should we orthogonalize BSD invariants against conductor before measuring tail contribution?

3. **Can Katz-Sarnak normalization create the wall?** Our zeros are normalized: γ_n / log(N). After normalization, the first zero retains arithmetic information (it's close to s=1/2 for rank-0, at s=1/2 for rank-1). But normalization pushes higher zeros toward universal spacing statistics. Could the wall be a normalization artifact? If we use raw (unnormalized) zeros, does BSD signal leak into the tail?

4. **The ILS interpretation has a specific prediction.** The support theorem says SO(even) and SO(odd) 1-level densities agree for test functions with Fourier support in [−1, 1]. What is the predicted crossover zero index for conductor ≤ 5,000? Does our wall (between zero 1 and zero 2) match or contradict that prediction?

### B. Attack the methodology

5. **Is z = 74.8 too good?** The permutation test gives z = 74.8. That's suspiciously large. Is there a bug in the test design? Could conductor stratification itself create structure that inflates ARI even after shuffling? Should we also shuffle conductor assignments?

6. **K-means on 16 dimensions with ~5 objects per stratum.** Many conductor strata have few objects. Is k-means reliable with k=2–5 on n=5–20 objects in 16 dimensions? What happens with a leave-one-out classifier instead?

7. **We used 13,150 objects but the original sprint used 133K.** The ablation was first observed on the full dataset (31K ECs + 102K MFs). These experiments use only ECs with 20+ zeros and Sha data (13K). Has the sample restriction biased the result? Should we re-run on the full 133K with the ablation only (no BSD decomposition)?

### C. Name the residual

8. **What mathematical structure could produce rank-dependent clustering in zeros 5–19 that is independent of all BSD invariants?** We are asking for theoretical candidates. Not speculation — mechanisms with published theoretical support. Options we can think of:
   - Selberg eigenvalue distribution beyond the Ramanujan bound
   - Galois representation image (Serre's uniformity conjecture territory)
   - Automorphic form weight or nebentypus character
   - Something in the Langlands program we haven't considered

9. **Is "arithmetically independent of the center" the right framing?** The BSD formula connects L'(1) to Sha, Tam, Reg, Ω, |E_tor|. If the tail is independent of ALL these, is it also independent of L'(1) itself? That would mean the tail encodes rank through a channel that doesn't pass through the central value at all — rank information that is globally distributed in the zero spectrum but invisible at the center. Is this mathematically possible? Does any existing conjecture predict or prohibit this?

10. **The strongest null — and its death.** The strongest null hypothesis was: ARI = 0.55 on zeros 5–19 is a trivial consequence of SO(even) vs SO(odd) symmetry type classification — the spectral tail merely rediscovers the known distributional difference between symmetry types.

    **We killed it.** Root number conditioning test: within root number +1 (SO(even) only), restricting to rank 0 vs rank 2:

    | Test | ARI | z-score | p-value |
    |------|-----|---------|---------|
    | SO(even) only, zeros 5–19 | **0.4913** | **14.0** | **< 0.0001** |
    | Permutation null (100 trials) | −0.004 ± 0.036 | — | — |

    84 conductor strata with mixed ranks (6,817 rank-0, 458 rank-2). The spectral tail separates rank 0 from rank 2 **within a single symmetry class**. This is not SO(even) vs SO(odd). The tail discriminates within SO(even), which the symmetry type null cannot explain.

    SO(odd) contains only rank-1 curves at conductor ≤ 5,000 (no rank 3), so the analogous test is not applicable. This is a limitation, not an evasion.

    **The question for the Council becomes:** What mechanism allows zeros 5–19 to discriminate between rank 0 and rank 2 within SO(even)? The ILS support theorem predicts that higher zeros distinguish SO(even) from SO(odd). It does NOT predict discrimination within SO(even). What does?

---

## The Honest State

**What we know:** Zeros 5–19 cluster by rank at ARI = 0.55 (z = 74.8 vs permutation null). No BSD invariant contributes to this clustering. Faltings height dominates zero 1 (r = −0.168) but is absent from the tail. The BSD/tail wall is sharp (increment drops from 0.061 to 0.0001 between zero 1 and zero 2). The signal survives within SO(even) at ARI = 0.49, z = 14.0 — it is not symmetry type classification. The candidate mechanism is GUE zero repulsion propagating central rank information into the tail.

**What we don't know:** Whether repulsion alone quantitatively explains the ARI magnitude, or whether additional structure is required. Whether the wall is a normalization artifact. Whether Tamagawa numbers break the decomposition. Whether the ILS crossover prediction matches our data. Whether the Faltings height–first zero correlation is novel.

**What we claim:** The spectral tail is a higher-fidelity encoding of rank than central vanishing. Zero repulsion distributes rank information across 15 continuous dimensions instead of compressing it into one binary indicator. This is mechanistically predicted by GUE repulsion, consistent with ILS, and goes beyond both by demonstrating within-symmetry-class discrimination. It has not been previously demonstrated empirically as a computational phenomenon.

**What we fear:** That GUE repulsion trivially produces ARI = 0.49 within SO(even) for any reasonable rank-2 population size, and a reviewer can show this with a five-line RMT simulation. If so, the finding reduces to "GUE repulsion works as expected." Tell us whether that simulation produces the observed ARI or falls short.
