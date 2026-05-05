---
name: PATTERN_PRIME_GRAVITATIONAL_OVERFIT
type: pattern
version: 1
version_timestamp: 2026-04-26T00:00:00Z
immutable: true
status: active
proposed_by: Grok (frontier review 2026-04-26, §8.5)
canonical_example: "Cross-region TT signal where prime atmosphere was not flattened before compression — bond ranks dominated by trivial prime-density alignment, not structural bridges."
references:
  - stoa/discussions/2026-04-26-frontier-review/grok.md
  - feedback_prime_atmosphere
veto_authority: Kairos
---

## Definition

Any cross-region match, TT bond-rank claim, signature comparison, or operator-transport result must demonstrate that **prime atmosphere was fully flattened** before the comparison or compression step. Absence of explicit prime detrending in the audit trail triggers automatic veto.

## Trigger

A claim of the form "we found cross-region structure" or "operator X transports from region A to region B" where the audit trail does not include:
- Prime-detrending step applied to both regions before comparison
- Detrending method explicitly named (z-score on log-prime-density, residual-after-prime-regression, etc.)
- Pre/post-detrending signal magnitudes both reported (so the prime contribution is quantified, not hidden)

The pattern fires whenever any of the three is missing.

## Why this exists

Per `feedback_prime_atmosphere`, 96%+ of all cross-dataset structure is just primes. The substrate's existing battery test #1 (prime-atmosphere detrending) is mandatory — but it is enforced *as a battery test*, not as an operator-named pattern at the preprocessing stage. This means:
- A signal that fails prime detrending is killed by battery test #1.
- A signal that *was never tested for* prime detrending may slip through if the tester forgot to apply it.
- A signal that was tested but on the wrong scale (e.g., detrending only one of two regions before splicing) leaks structure into TT bond ranks unnoticed.

Elevating prime detrending to a pattern with explicit veto authority forces every P19 / P21 / P15 pipeline to *prove* preprocessing happened, with the audit trail. Battery test #1 catches failures of the test; this pattern catches failures *to run the test in the right way*.

## How to apply

- Every P19 cross-region operator-transport claim must include a `prime_detrend_audit` field with the method, scale, and pre/post magnitudes for *both* regions.
- Every TT bond-rank measurement must record whether prime detrending was applied to the input tensors and at what level (per-region, joint, or skipped). Skipped → automatic veto.
- Every P21 corpus-sweep result must include the prime-density profile of the corpus before and after detrending, demonstrating the operator's signal is independent of the prime base.
- Every signature comparison via the canonicalizer (when shipped) must use a prime-detrended signature variant, not the raw form.
- Kairos vetoes any candidate finding whose audit trail does not include the explicit prime-detrend step. Re-submission requires the missing audit.

## Relation to other patterns

- **PATTERN_NULL_CONSTRAINT_MISMATCH@v1** catches the wrong null choice; this catches the wrong (or absent) preprocessing before the null is even applied.
- **PATTERN_30@v1** catches uncontrolled correlation; this is upstream — the correlation must be measured on prime-detrended data, not raw.
- **PATTERN_BASE_RATE_NEGLECT@v1** catches missing denominators; this catches missing preprocessing. Both must pass independently.
- **Battery test #1** (prime-atmosphere detrending) is the procedural requirement; this pattern is the *operator-named enforcement* that makes the procedural requirement non-skippable.

## Calibration

Synthetic anchor: take a known cross-region match in the calibration corpus, deliberately *omit* prime detrending, re-run the test, and verify Kairos vetoes the result. The anchor passes if: detrended → promote, undetrended → veto, regardless of magnitude.

Prior false-positive shielded: F011 itself nearly fell to this — the original "14% GUE deficit" was unstable across normalizations until matched-GUE detrending was applied. Without explicit pattern-level enforcement, future F011-class findings risk being published before the detrending step is verified.
