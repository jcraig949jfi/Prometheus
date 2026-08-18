# Deep Research Report #82 — Rhythma: A Combinatorial-Native Phoneme for OEIS and Belyi Maps

**Prepared for:** Harmonia (Aporia Void Detector project)
**Date:** 2026-04-23
**Batch:** Deep Research Batch 5

## 1. Problem Statement

Harmonia's five existing phonemes (megethos, bathos, symmetria, arithmos, phasma) are EC/L-function-centric. The V3/V4 void-detection strategies flagged that oeis↔charon, groups↔oeis, bianchi↔groups, and belyi↔* pairs are structurally deaf to these phonemes because combinatorial objects lack canonical L-function observables. We propose **Rhythma** (ῥυθμός, "rhythm / measured flow") as a domain-native phoneme capturing the asymptotic pulse of a sequence or Belyi map.

**Formulation (3-component observable):**

Given a sequence a(n) (or the face/edge/vertex-count generating series of a Belyi dessin), define

  Rhythma(a) = (α, σ, β)

where a(n) ~ C · α^n · n^β as n → ∞, α is the exponential growth rate (reciprocal of the modulus of the closest-to-origin singularity ρ of the OGF, α = 1/|ρ|), σ is the Flajolet–Odlyzko singularity type at ρ drawn from the finite alphabet {algebraic(p/q), logarithmic(k), algebraic-logarithmic(p/q, k), essential, polar(k), meromorphic}, and β is the sub-exponential polynomial correction exponent (β = p/q − 1 for algebraic singularities, β = −1 for a simple pole, etc.).

This triple is complete in the sense that, by Flajolet–Odlyzko's transfer theorem (*Analytic Combinatorics*, Cambridge 2009, Theorem VI.1 / §VI.3), it determines the leading-order coefficient asymptotics up to the constant C.

## 2. Computability

Techne's existing `TOOL_SINGULARITY_CLASSIFIER` already classifies σ for ~394K OEIS sequences. The additional data Rhythma must persist per object:

- **α** (float64): exponential growth rate — derivable from the same singularity-detection pipeline (ratio test on a(n+1)/a(n) with Richardson extrapolation, or direct root-finding on denominator of an auto-guessed rational/algebraic OGF).
- **β** (rational, stored as (p, q)): extracted from the singular exponent when σ is algebraic or algebraic-logarithmic; stored as 0 for simple poles, undefined/None for essential singularities.
- **confidence** (float ∈ [0, 1]): required because ~30% of OEIS entries have too few terms for stable extrapolation; low-confidence Rhythma must be excluded from coupling tests.

Storage overhead: ~24 bytes per object × 394K ≈ 9.5 MB. Trivial.

## 3. Cross-Domain Coupling Structure

Two objects X, Y **Rhythma-couple** if:

1. |log α_X − log α_Y| < ε_α (default ε_α = 0.02, i.e. ~2% growth-rate match),
2. σ_X = σ_Y (exact singularity type match),
3. |β_X − β_Y| < ε_β (default ε_β = 1/12, finer than the coarsest algebraic exponent grid).

Coupling strength = exp(−|log α_X − log α_Y| / ε_α) when (2) and (3) hold, else 0. This is deliberately stricter than megethos (which only matches log-magnitude) because analytic combinatorics predicts that sequences sharing (α, σ, β) are governed by the *same* combinatorial schema (e.g. labelled trees all have σ = algebraic(1/2), β = −3/2, differing only in α — Otter's theorem; Flajolet–Sedgewick §VII.5).

## 4. Tensor Activation Predictions

Currently-silent pairs Rhythma should activate:

- **OEIS ↔ Belyi**: dessins d'enfants have OGFs enumerating by passport; Belyi covers of fixed genus have σ = algebraic(1/2), aligning with many OEIS tree/map families (cf. Lando–Zvonkin, *Graphs on Surfaces and Their Applications*, Springer 2004, §1.5). Expected high activation.
- **OEIS ↔ genus-2**: point counts #C(𝔽_p) as p varies have generating series in p whose singularity structure reflects the curve's Euler factor. Weaker but non-trivial coupling expected via β.
- **OEIS ↔ number_fields**: class-number generating series and zeta functions of orders have logarithmic-type singularities matching a small but distinctive OEIS subfamily (class-number A000XXX sequences). Mid-strength.
- **Belyi ↔ groups**: monodromy-group-indexed generating functions share α with OEIS group-enumeration sequences (A000001 family).

## 5. Literature

- **Flajolet, P. & Sedgewick, R.**, *Analytic Combinatorics*, Cambridge University Press, 2009 — the canonical reference; Parts B (Complex Asymptotics) and VI (Singularity Analysis) supply the classification and transfer theorems Rhythma relies on.
- **Flajolet, P. & Odlyzko, A.**, "Singularity analysis of generating functions", *SIAM J. Discrete Math.* 3 (1990), 216–240 — the original singularity-analysis paper.
- **Joyal, A.**, "Une théorie combinatoire des séries formelles", *Advances in Mathematics* 42 (1981), 1–82 — combinatorial species; provides a *structural* analogue of the phoneme idea.
- **Lando, S. K. & Zvonkin, A. K.**, *Graphs on Surfaces and Their Applications*, Springer 2004 — Belyi/dessin generating-function side.

No species-theoretic observable in the literature is deployed as a cross-domain coupling primitive; Rhythma would be novel in that operational role.

## 6. Falsification Criteria

Rhythma is validated iff, under the TT-scorer frozen on 2026-04-15:

- median coupling-rank on OEIS↔Belyi pairs ≥ 0.30, AND
- ≥ 2 of {OEIS↔genus-2, OEIS↔number_fields, Belyi↔groups} exceed rank 0.15, AND
- Rhythma-couplings are not redundant with megethos (Spearman ρ between the two coupling matrices < 0.6 on a 10K random-pair sample).

If any condition fails, Rhythma is retired; if only the redundancy test fails, β alone is kept as a megethos subcomponent.

## 7. Specific Computations for Harmonia

1. **Full OEIS Rhythma pass** (~30 min) — run `TOOL_SINGULARITY_CLASSIFIER` in (α, σ, β, confidence)-emit mode over all 394K entries; persist to `ergon/rhythma_oeis.parquet`.
2. **Belyi batch** — pull 1K dessins from LMFDB `belyi_galmaps`, compute passport OGFs, derive Rhythma. Expected runtime: 10 min.
3. **Coupling matrix** — OEIS × genus-2 pairwise Rhythma-couple under the V3 TT-scorer; flag top-1% pairs for manual inspection.
4. **Benchmark** — compare mean coupling rank against megethos, bathos, arithmos on matched-size samples; report redundancy ρ.

Deliverable target: coupling-rank table + redundancy diagnostic within 24 h of approval.

**Word count: 798**
