---
name: PATTERN_CONDUCTOR_CONFOUND
type: pattern
version: 1
version_timestamp: 2026-04-26T00:00:00Z
immutable: true
status: active
proposed_by: DeepSeek (frontier review 2026-04-26, §8.5)
canonical_example: "Cross-region correlation between L-function regulators and Mahler measures that vanishes once stratified by conductor decile — the apparent signal was conductor-driven trivial scaling, not structural coupling."
references:
  - stoa/discussions/2026-04-26-frontier-review/deepseek.md
  - feedback_prime_atmosphere
veto_authority: Kairos
---

## Definition

Any cross-region correlation, signature match, or operator-transport claim must demonstrate **conductor-stratified null survival**: the signal must persist within each conductor (or analogous size-index) decile, not merely on the pooled corpus. Absence of conductor stratification triggers veto.

## Trigger

A claim of the form "regions A and B share structure" or "operator X transports from region A to region B" where the audit trail does not include:
- Conductor (or analogous index) stratification of both regions
- Per-decile effect size and matched-null comparison
- Demonstration that the signal does not collapse within deciles

The pattern fires whenever any of the three is missing.

## Why this exists

Many mathematical invariants scale with the conductor or index of the underlying object: regulator grows with conductor, Mahler measure grows with polynomial degree, analytic Sha order grows with conductor, hyperbolic volume grows with knot complexity. Two regions of the substrate that are independently sorted by their natural size index will produce *trivial* cross-region correlations purely because both invariants grow with size. These correlations:
- Survive `feedback_prime_atmosphere` detrending (primes are not the issue)
- Survive `PATTERN_30` controlled-correlation tests at the pooled level
- Survive matched-null tests when the matched null also pools across conductor

But they *vanish* when each region is stratified by its conductor decile and the within-decile correlation is computed. The vanishing is the diagnostic.

Without operator-named pattern enforcement at the stratification stage, the substrate's 5-of-5 battery will promote signals that are pure conductor echoes — the F011 pipeline's effect size of 0.46-0.51 is genuinely *within-stratum* (rank-invariant per F011 reports); a naive replication that pools across strata could easily report inflated effect sizes that are conductor-driven artifacts.

This is the conductor analog of `PATTERN_PRIME_GRAVITATIONAL_OVERFIT`: prime-detrending is mandatory pre-comparison; conductor-stratification is mandatory pre-correlation.

## How to apply

- Every P19 cross-region operator-transport claim must include a `conductor_stratification_audit` field with:
  - Stratification scheme (decile, log-bin, or domain-natural binning)
  - Per-stratum effect size and matched-null p-value
  - Demonstration that the within-stratum effect persists at ≥ 50% of the pooled effect
- Every P21 corpus-sweep result must include the conductor distribution of "interesting" stratum vs the corpus baseline; cherry-picking the high-conductor tail is automatic veto.
- Every TT bond-rank measurement on cross-region splices must apply conductor-decile flattening before TT decomposition (per `feedback_prime_atmosphere`-extension to non-prime gravitational wells).
- Every signature comparison via the canonicalizer must use conductor-residualized signatures, not raw conductor-conditioned signatures, for cross-region comparison.
- Kairos vetoes any candidate finding without conductor-stratified audit. Re-submission requires the missing audit.

## Relation to other patterns

- **PATTERN_PRIME_GRAVITATIONAL_OVERFIT@v1** catches missing prime detrending; this catches missing conductor stratification. Both are pre-comparison preprocessing patterns; both must pass independently.
- **PATTERN_30@v1** catches uncontrolled correlation; this is a specific class of "control variable that was not applied" — control by conductor decile.
- **PATTERN_BASE_RATE_NEGLECT@v1** catches missing denominator; this catches missing stratification. Different but complementary.
- **Battery test #1 (prime atmosphere) and PATTERN_PRIME_GRAVITATIONAL_OVERFIT** form one preprocessing pillar; this pattern is the second pillar — non-prime gravitational well enforcement at the conductor axis specifically.

## Calibration

Synthetic anchor: take a known cross-region match in the calibration corpus, deliberately stratify only on the pooled level (skipping conductor decile stratification), re-run the test, and verify Kairos vetoes the result. The anchor passes if: stratified → promote, unstratified → veto, regardless of magnitude.

Real-world calibration target: F011 itself. The F011 paper's effect of 0.46-0.51 was reported as rank-invariant (i.e., persists within strata). A re-analysis that pools across rank should produce an inflated effect size; the pattern should catch that re-analysis as conductor-confounded if conductor-stratification is the missing audit. If the pattern does not catch the synthetic conductor-pooled F011 reanalysis, the pattern's threshold is mis-tuned and must be revised.
