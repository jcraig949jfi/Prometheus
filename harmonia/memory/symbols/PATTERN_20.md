---
name: PATTERN_20
type: pattern
version: 1
version_timestamp: 2026-04-20T23:55:00Z
immutable: true
status: active
previous_version: null
precision:
  canonical_definition: "A pooled single-axis measurement can look clean (monotone, single-signed, high R2, low p) while masking stratum-level structure that contradicts it. The stratified or preprocessed view shows the real shape: different magnitudes per stratum, different signs per stratum, or the effect collapsing under proper preprocessing. The pooled number is the artifact; the stratified panel is the measurement."
  symptom_types: [preprocessing_drift, stratification_mixture, sample_unstable_raw_vs_stable_decon]
  symptom_count: 3
  anchor_count: 4
  verdict_vocabulary: [CLEAR, WARN, BLOCK]
  decision_rules:
    sign_discordant_or_pooled_contrary: BLOCK
    ratio_above_block_threshold: BLOCK
    ratio_above_warn_threshold: WARN
    no_stratified_data: WARN
    small_n_stratum: WARN_FLAG_INCONCLUSIVE
    clean_panel: CLEAR
  ratio_thresholds:
    warn: 1.2
    block: 2.0
  min_stratum_n: 100
  ratio_semantics: "abs(pooled_value) / mean(abs(stratum_values))"
  required_inputs: [pooled_value]
  optional_inputs: [pooled_n, stratified, min_stratum_n, ratio_warn_threshold]
  composition_rules:
    composes_with: [PATTERN_19, PATTERN_30]
    subsumes: null
    disjoint_from: [PATTERN_4]
proposed_by: Harmonia_M2_sessionA@c80f6116f
promoted_commit: pending
references:
  - F010@c043ba782
  - F011@cf5a58256
  - F013@ce0ba1692
  - F015@c043ba782
  - Pattern_4@c45fd79d5
  - Pattern_19@c45fd79d5
  - Pattern_21@c9335b7c2
  - PATTERN_30@v1
  - NULL_BSWCD@v2
redis_key: symbols:PATTERN_20:v1:def
implementation: harmonia/sweeps/pattern_20.py::sweep@c751dfc64
---

## Definition

**Stratification Reveals Pooled Artifact.** A pooled single-axis
measurement (ρ, slope, variance, bias) can look clean — monotone,
uniform, significant — while masking stratum-level structure that
contradicts the pooled reading. The stratified or preprocessed view
shows the real shape: different magnitudes per stratum, different signs
per stratum, or the effect largely collapsing under proper preprocessing.
The pooled number is the artifact; the stratified panel is the
measurement.

The symbol encodes the discipline as three decision rules and a
machine-checkable threshold pair, replacing a 100-line pattern-library
entry with a one-call diagnostic.

## Decision rules

| Input | Verdict | Rationale |
|---|---|---|
| sign-discordance between pooled and per-stratum OR pooled sign contrary to every non-zero stratum | `BLOCK` | pooled magnitude is a mixture across oppositely-signed strata; the pooled direction is an aggregation artifact. |
| `pooled_vs_mean_stratum_ratio > 2.0` | `BLOCK` | pooled magnitude diverges from per-stratum magnitudes by more than 2×; mixture-of-strata artifact. |
| `1.2 < ratio ≤ 2.0` | `WARN` | ratio above noise floor but below BLOCK; re-audit with tighter stratification or preprocessing. |
| no stratified companion provided | `WARN` | re-audit required with ≥1 stratification before promotion. |
| any stratum has `n < 100` | `WARN` (`FLAG_INCONCLUSIVE`) | stratum under-sampled; panel conclusions conditional on coverage. |
| `ratio ≤ 1.2` AND sign uniform AND all strata `n ≥ 100` | `CLEAR` | pooled consistent with per-stratum panel. |

Ratio semantics: `abs(pooled_value) / mean(abs(stratum_values))`. If
`mean_abs_stratum == 0` and `pooled ≠ 0`, ratio is infinite (BLOCK).

## Three symptom types

PATTERN_20 manifests through three concrete shapes. All are the same
underlying disease — pooled measurement is the null-coordinate projection
of a multi-stratum or multi-preprocessing landscape — but the surface
form differs.

1. **Preprocessing-dependent magnitude drift.** Same dataset, different
   preprocessing, different magnitudes. Anchor: F011 (pooled 40% deficit
   at n≈4K → first-gap-raw 59% at n=2M → first-gap-unfolded 38% at
   n=2M). Diagnostic: apply ≥1 preprocessing variant (unfolding, prime-
   detrend, density-normalization) and check magnitude stability.

2. **Stratification mixture contradicting pooled.** Pooled slope or ρ
   differs substantially from per-stratum values. Anchor: F015
   (pooled slope −0.60 vs per-k slopes in [−0.13, −0.49] — ~40% larger
   than any stratum). Diagnostic: split by ≥1 categorical axis with
   ≥3 levels and check pooled-vs-max-stratum ratio.

3. **Sample-unstable raw vs stable decontaminated.** Pooled raw statistic
   collapses at larger n while the decontaminated version stays put.
   Anchor: F010 (pooled ρ 0.404 at n=71 → 0.109 at n=75 at 2.5× per-
   degree sampling; decon ρ stable 0.269 → 0.270). Diagnostic: replicate
   pooled statistic at 2× sample size AND compare against a preprocessed
   (P052 or similar decon) variant.

Do NOT triage into subtypes before applying the pattern; the diagnostic
is unified. The three are lenses on one failure mode.

## Anchor cases

| F-ID | Symptom | Pooled | Stratified / Preprocessed | Outcome |
|---|---|---|---|---|
| F011 | preprocessing_drift | ~40% deficit at n≈4K | first-gap-unfolded 38% at n=2M | magnitude corrected; LAYER 1 calibration + LAYER 2 frontier |
| F013 | preprocessing_drift | pooled slope −0.00467 (R²=0.049) | unfolded slope −0.00121 (R²=0.001) | ~74% density-mediated; 26% structural residual |
| F015 | stratification_mixture | pooled slope −0.60 (R²=0.27) | per-k slopes [−0.13, −0.49] | sign uniform, magnitude non-monotone; pooled ~40% larger than any stratum |
| F010 | sample_unstable | pooled ρ 0.404 (n=71) → 0.109 (n=75) | decon ρ 0.270 stable | pooled was never the signal; decon is durable at z=2.38 |

All four anchors pre-date the symbol promotion and appear in
`pattern_library.md` Pattern 20 entry (promoted to FULL 2026-04-17). The
symbol codifies the diagnostic without changing the anchors.

## Connected patterns

- **`Pattern_4@c45fd79d5`** (Sampling Frame Trap) — disjoint. Pattern 4
  is about which rows were pulled; PATTERN_20 is about how the pulled
  rows were aggregated. Adjacent but distinct; a finding can be
  Pattern_4-clean and PATTERN_20-BLOCK, or the reverse. `sessionC draft
  2026-04-17` proposed subsumption; `sessionA` rejected — keep both,
  cross-reference.
- **`Pattern_19@c45fd79d5`** (Stale / Irreproducible Tensor Entry) —
  composes. F010 is the double-anchor: the 0.40 was stale (Pattern 19)
  AND pooled-artifact-at-every-n (PATTERN_20). When both fire, flag
  the entry as `pooled_artifact_plus_stale`, not "just stale" or "just
  artifact". Descriptions must reflect durable-plus-demoted state.
- **`Pattern_21@c9335b7c2`** (Null-Model Selection) — orthogonal.
  PATTERN_20 is about the pooled statistic being a projection; Pattern_21
  is about the null model being a projection. Both are the "treat the
  measurement instrument as a coordinate system" move applied to
  different pipeline steps. A PATTERN_20-CLEAR finding can still be
  Pattern_21-suspect.
- **`PATTERN_30@v1`** (Algebraic-Identity Coupling) — independent gate.
  Pattern 30 operates on variable pairs; PATTERN_20 on
  aggregation-vs-stratification. F015 carries both concerns (Pattern 30
  Level 1 for log(N) denominator; PATTERN_20 anchor for magnitude non-
  monotonicity). Run both in the sweep pipeline; composite verdict is
  `max(pattern_30, pattern_20)` under `BLOCK > WARN > CLEAR`.

## Derivation / show work

Three anchors (F011, F013, F015) surfaced independently during sessionA
+ sessionB + sessionC + sessionD parallel work on 2026-04-17. The shared
shape — pooled-vs-stratified disagreement with varying surface form —
was synthesized into a pattern-library entry by sessionC and promoted
to FULL after sessionA approved. F010 was added as the fourth anchor
tick 11:33 UTC 2026-04-17 on the bigsample re-run (`wsw_F010_bigsample`)
— the sample-unstable symptom was distinct enough from the F011/F013
preprocessing-drift symptom and the F015 stratification-mixture symptom
to warrant its own category, resolving the three-symptom taxonomy.

The symbol promotion 2026-04-20 replaces the prose entry's diagnostic
with typed decision rules. The pattern-library entry remains as the
prose anchor and derivation record; the symbol is the machine-resolvable
mechanism.

## Data / implementation

```python
from harmonia.sweeps.pattern_20 import sweep, Pattern20Check, StratifiedStat

# F015 anchor: sign-uniform but magnitude off by ~40% vs any stratum
result = sweep(Pattern20Check(
    pooled_value=-0.60,
    pooled_n=30000,
    stratified=[
        StratifiedStat("k=1", -0.13, n=8200),
        StratifiedStat("k=2", -0.45, n=6800),
        StratifiedStat("k=3", -0.49, n=5100),
        StratifiedStat("k=4", -0.36, n=4500),
        StratifiedStat("k=5", -0.48, n=3200),
        StratifiedStat("k=6", -0.46, n=2200),
    ],
))
# result.verdict == 'WARN', ratio ≈ 1.5, sign_agreement=True
```

The `pattern_20.py::sweep` implementation lives in
`harmonia/sweeps/pattern_20.py` and was shipped at commit `c751dfc64`
as part of gen_06 Pattern auto-sweeps v1.0. It passes the F010 / F011 /
F013 / F015 anchor regression set (see `harmonia/sweeps/test_sweeps.py`).

## Usage

**Tight (in a SIGNATURE provenance block):**
```
sweeps.pattern_20: WARN @ ratio=1.50 sign_agreement=True
  pooled=-0.60 (n=30000), mean|stratum|=0.40
  rationale: pooled magnitude is ~1.5× mean stratum; mixture-of-strata artifact
```

**Loose (in an inter-agent report):**
```
F015 is PATTERN_20@v1 anchor symptom #2 (stratification_mixture). Pooled
slope −0.60 exceeds per-k stratum magnitudes [−0.13, −0.49] by ~1.5×.
Sign uniform; magnitude pooled is artifact. Durable finding is per-k
sign-uniformity, not pooled magnitude.
```

**As a gate in an ingestion call:**
```python
from harmonia.sweeps import sweep_signature
outcome = sweep_signature(pooled_check=Pattern20Check(...))
# SweepBlocked raised if outcome.overall == 'BLOCK' and not overridden
register_specimen.register(..., sweep_outcome=outcome)
```

## Version history

- **v1** 2026-04-20T23:55:00Z — first canonicalization as a symbol.
  Promoted from the `pattern_library.md` Pattern 20 entry (FULL since
  2026-04-17). Four anchors at promotion (F010 sample_unstable;
  F011 preprocessing_drift; F013 preprocessing_drift; F015
  stratification_mixture). Implementation at `harmonia/sweeps/pattern_20.py`
  (commit c751dfc64). Graded decision rules match the prose entry
  verbatim — this symbol IS the pattern, now machine-resolvable in one
  call rather than re-read from prose across pattern_library + specimen
  descriptions.

  Second pattern-type symbol after PATTERN_30@v1. The promotion
  discipline follows PATTERN_30's template (frontmatter precision block,
  canonical_definition, verdict_vocabulary, decision_rules, anchor
  table, connected patterns, implementation pin, usage examples).
  Template is now stable across two anchors; subsequent migrations
  (PATTERN_21, PATTERN_19, PATTERN_13, PATTERN_18) inherit the shape.
