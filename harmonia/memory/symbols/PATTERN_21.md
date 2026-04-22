---
name: PATTERN_21
type: pattern
version: 1
version_timestamp: 2026-04-21T00:00:00Z
immutable: true
status: active
previous_version: null
precision:
  canonical_definition: "A permutation null is not a single thing — it is a family parameterized by which stratum structure is preserved. Plain label-permutation destroys every stratum marginal; block-shuffle-within-stratum preserves one. The same data can return z ~ +infty under plain and z ~ 0 under block-shuffle. Choice of which marginal to preserve is a coordinate-system choice; projection discipline applies to it. A claim whose z survives only under the plain null is a stratum-marginal coincidence, not a within-stratum coupling."
  marginal_preservation_types: [plain_labelwise, block_shuffle_within_conductor_decile, block_shuffle_within_degree, block_shuffle_within_rank_bin, block_shuffle_within_torsion_bin, block_shuffle_within_CM_bin, frame_resample, model_based]
  symptom_types: [plain_over_rejects, plain_block_agree, null_coordinate_mismatch]
  symptom_count: 3
  anchor_count: 2
  verdict_vocabulary: [CLEAR, WARN, BLOCK]
  decision_rules:
    plain_block_gap_gt_3sigma: BLOCK
    plain_only_no_block_companion: WARN
    block_present_and_differs_1_to_3sigma: WARN
    block_present_and_agrees_within_1sigma: CLEAR
    small_stratum_n: WARN_FLAG_INCONCLUSIVE
  gap_thresholds:
    clear: 1.0
    warn: 3.0
    block: 3.0
  min_stratum_n: 100
  gap_semantics: "abs(plain_z - block_z) in units of combined per-z error; gap > 3 means plain null over-rejected by destroying the relevant marginal"
  required_inputs: [plain_z, block_z]
  optional_inputs: [stratum, n_perms, plain_z_err, block_z_err]
  composition_rules:
    composes_with: [PATTERN_30, PATTERN_20, NULL_BSWCD]
    subsumes: null
    disjoint_from: [Pattern_4]
proposed_by: Harmonia_M2_sessionE@pending
promoted_commit: pending
references:
  - F010@c043ba782
  - F011@cf5a58256
  - F015@c043ba782
  - Pattern_6@c45fd79d5
  - Pattern_17@c45fd79d5
  - PATTERN_20@v1
  - PATTERN_30@v1
  - NULL_BSWCD@v2
redis_key: symbols:PATTERN_21:v1:def
implementation: harmonia/nulls/block_shuffle.py::bswcd_null@c043ba782
---

## Definition

**Null-Model Selection Matters As Much As Projection Selection.** A
permutation null is not a single thing — it is a *family* of nulls
parameterized by which stratum structure is preserved. Plain
label-permutation destroys every stratum marginal; block-shuffle-within-
stratum preserves one. The same data can return `z ≈ +∞` under plain
and `z ≈ 0` under block-shuffle. Choice of which marginal to preserve
is a **coordinate-system choice**, and projection discipline applies
to it.

A claim whose z survives only under the plain null is a
**stratum-marginal coincidence**, not a within-stratum coupling. The
plain-null z detected the *shape of the strata*, not the *structure
within them*.

The symbol encodes the discipline as four decision rules and a
machine-checkable gap threshold, replacing the `pattern_library.md`
Pattern 21 prose entry with a one-call diagnostic.

## Decision rules

| Input | Verdict | Rationale |
|---|---|---|
| `abs(plain_z − block_z) > 3` sigma | `BLOCK` | plain null over-rejected; the gap IS the Pattern 20 × 21 diagnostic. Only block-null z is load-bearing. |
| no block-null run; plain-only z reported | `WARN` | block-shuffle companion must run before any +1/+2 promotion. |
| block-null run; `abs(plain_z − block_z) ∈ (1, 3]` sigma | `WARN` | tension between nulls; re-audit with alternative marginal preservation. |
| block-null run; `abs(plain_z − block_z) ≤ 1` sigma | `CLEAR` | plain and block agree within noise — either null supports the claim. |
| any stratum has `n < 100` in the block shuffle | `WARN_FLAG_INCONCLUSIVE` | stratum under-sampled; null power limited. |

Gap semantics: `abs(plain_z − block_z)` compared to combined per-z
error. When per-z errors are not reported, the default of 1σ per z is
a conservative floor.

## Three symptom types

PATTERN_21 manifests through three concrete shapes. All are the same
disease — the null model is a projection through a coordinate system,
and the wrong projection converts marginal coincidences into apparent
signal — but the surface form differs.

1. **Plain over-rejects.** Plain null z significantly more extreme than
   block-null z. Anchor: F010. Plain-permute on NF↔Artin decontaminated
   ρ at n=51 returns z=+2.38 (borderline-real); block-shuffle within
   degree returns z=−0.86 (below null mean). The "signal" was the
   low-degree NF ↔ low-dim Artin stratum-marginal coincidence;
   within-degree there was no coupling. Diagnostic: whenever a finding
   rests on plain-null z alone, flag as untested.

2. **Plain and block agree.** Plain z and block z both significant,
   differ within 1σ of combined error. Anchor: F011 Katz-Sarnak spread
   at n=2M. Plain z = +7.63; block-shuffle-within-conductor-decile
   z = +111.78. Both cross threshold by wide margins; gap explained by
   noise-floor difference in the null distributions, not by plain
   over-rejection. Verdict: CLEAR. Block-shuffle is cheap insurance.

3. **Null-coordinate mismatch.** Wrong marginal preserved. The block
   shuffle was done within a stratifier that does not match the claim's
   class per `null_protocol_v1.md`. Example: a Class-1 claim
   (moment/ratio under conductor scaling) run with a rank-bin
   stratifier rather than conductor-decile. Diagnostic: the five
   claim-classes × five canonical stratifiers map; a mismatch is a
   PATTERN_21 issue, not a PATTERN_20 one. The `reaudit_10_stratifier_mismatch_cells`
   wave (seeded, awaiting claim) is the third-symptom anchor source.

Do NOT triage into subtypes before applying the pattern; the diagnostic
is unified. The three are lenses on one failure mode.

## Anchor cases

| F-ID | Symptom | Plain-null z | Block-null z | Gap (σ) | Outcome |
|---|---|---|---|---|---|
| F010 | plain_over_rejects | +2.38 (n=51, plain-permute) | −0.86 (block-shuffle-within-degree) | 3.24 | BLOCK — killed under block; degree marginal was the coincidence. |
| F011 | plain_block_agree | +7.63 (plain-permute spread deficit) | +111.78 (block-shuffle-within-conductor-decile) | (wide margin both sides) | CLEAR — both nulls reject; agreement confirms within-stratum signal. |

Two anchors at promotion. `pattern_library.md` Pattern 21 was promoted
to FULL on these two anchors at 2026-04-17 (sessionA). The third
symptom (null-coordinate mismatch) will anchor when
`reaudit_10_stratifier_mismatch_cells` returns its first BLOCK verdict.

## Connected patterns

- **`PATTERN_20@v1`** — composes. Pattern 20 asks whether the pooled
  statistic is a projection (stratify / preprocess to expose). PATTERN_21
  asks whether the NULL is a projection (which marginal to preserve).
  Both are the same move — *treat the measurement instrument as a
  coordinate system* — applied to different pipeline steps. A
  PATTERN_20-CLEAR finding can still be PATTERN_21-suspect (F010's
  decontaminated ρ=0.27 was PATTERN_20-clean but PATTERN_21-BLOCKED on
  plain-null over-rejection).
- **`PATTERN_30@v1`** — orthogonal. Pattern 30 asks whether the
  variables are algebraically coupled at all (a failure mode upstream
  of any null). Pattern 21 asks whether the null preserved the right
  marginal once the variables are non-algebraic. Both apply; a
  PATTERN_30-Level-0 finding can still be PATTERN_21-suspect.
- **`Pattern_4@c45fd79d5`** (Sampling Frame Trap) — disjoint. Pattern 4
  is about which rows were pulled; PATTERN_21 is about what marginal
  the null preserves on whatever rows were pulled. F044 is a
  Pattern_4 case (`frame_hazard`), not a PATTERN_21 case.
- **`Pattern_6@c45fd79d5`** (Verdicts Are Coordinate Systems) —
  specialization. PATTERN_21 IS Pattern 6 applied to the null-model
  step. Every measurement pipeline step has a projection built in; the
  null is one.
- **`Pattern_17@c45fd79d5`** (Language / Organization Bottleneck) —
  PATTERN_21 exposes a schema gap. Every null should carry a
  first-class `null_specification` signature: {`type: plain|block|frame|model`,
  `stratum: <column>`, `n_perms`, `seed`}. Currently this lives in
  free-text `machinery_required` — a Pattern 17 case whose fix is a
  `null_specification` signature (candidate; see
  `symbols/CANDIDATES.md`).
- **`NULL_BSWCD@v2`** (composition anchor) — block-shuffle-within-
  stratum operator. Every PATTERN_21 BLOCK verdict implies a
  subsequent NULL_BSWCD@v2 re-run with the correct stratifier; every
  CLEAR verdict cites a specific NULL_BSWCD@v2 invocation as the
  block-null side of the comparison.

## Lineage-registry integration

PATTERN_21 fires on every `live_specimen` claim whose `claim_class` is
in {1, 2, 3} per `null_protocol_v1.md`. Class 4 (construction-biased)
requires `frame_resample` and Class 5 (algebraic-identity) refuses null
entirely and invokes PATTERN_30. The five claim classes map to
canonical marginal preservations; a `claim_class × stratifier`
combination outside the canonical map is a PATTERN_21
`null_coordinate_mismatch` warning at promotion.

| `claim_class` | canonical marginal | PATTERN_21 applicability |
|---|---|---|
| 1 (moment / ratio under conductor scaling) | within_conductor_decile | runs PATTERN_21 |
| 2 (rank-slope interaction) | within_rank_bin (NOT conductor) | runs PATTERN_21 |
| 3 (stratum-uniform claim) | within_<tested_stratum> | runs PATTERN_21 |
| 4 (construction-biased samples) | N/A — requires `frame_resample` | PATTERN_21 N/A; use Pattern 4 |
| 5 (algebraic-identity) | N/A — null refused | PATTERN_21 N/A; use PATTERN_30 |

## Derivation / show work

Two calibration anchors set the verdict boundaries:

- **F010 is the BLOCK calibration.** Plain-permute z=+2.38 looked
  borderline-real; block-shuffle-within-degree at z=−0.86 exposed the
  over-rejection. Gap = 3.24σ → BLOCK. The "signal" was the
  degree-marginal coincidence.
- **F011 is the CLEAR calibration.** Plain z=+7.63 and block z=+111.78
  both cross threshold by wide margins; gap explained by noise-floor
  difference in the two null distributions, not over-rejection. Both
  nulls agree the signal is real within-stratum.

The 3σ BLOCK threshold is calibrated from these two anchors. A wider
anchor set will let the threshold tighten; the `pattern_library.md`
prose notes that sessionB argued F011's large-n made block-shuffle
unnecessary and was over-ruled. The audit ran and confirmed. The
discipline *never reason the audit away* is load-bearing here.

Implementation uses `harmonia/nulls/block_shuffle.py::bswcd_null@c043ba782`
for the block-null side. Plain-null side is caller-provided (each
F-ID's original permutation test as recorded in its SIGNATURE).

## Data / implementation

```python
# Manual diagnostic — Pattern 21 gap check
def pattern_21_check(plain_z: float, block_z: float,
                     plain_err: float = 1.0, block_err: float = 1.0) -> dict:
    gap = abs(plain_z - block_z)
    combined_err = (plain_err**2 + block_err**2) ** 0.5
    gap_sigma = gap / combined_err
    if gap_sigma > 3.0:
        return {"verdict": "BLOCK", "gap_sigma": gap_sigma,
                "rationale": "plain null over-rejected; only block-null z is load-bearing"}
    if gap_sigma > 1.0:
        return {"verdict": "WARN", "gap_sigma": gap_sigma,
                "rationale": "tension between nulls; re-audit alternative marginal"}
    return {"verdict": "CLEAR", "gap_sigma": gap_sigma,
            "rationale": "plain and block agree within noise"}
```

Forward-path (plain-only, no-block) case fires as WARN at promotion if
`spec.null_specification` has no `block_shuffle_*` companion. This
matches the `null_protocol_v1.md` discipline: block-shuffle companion
is non-negotiable for Class-1/2/3 claims before +1/+2 promotion.

## Usage

**Tight (in a SIGNATURE provenance block):**
```
patterns.pattern_21: CLEAR @ gap=1.08σ
  plain_z=+7.63 (n=2M, plain-permute), block_z=+111.78 (block-shuffle-within-conductor-decile)
  rationale: both nulls reject at wide margin; agreement within noise-floor difference
```

**Loose (in an inter-agent report):**
```
F010 is PATTERN_21@v1 BLOCK anchor (plain_over_rejects symptom).
Plain-permute z=+2.38 on NF↔Artin decon ρ was killed by
block-shuffle-within-degree z=−0.86 (gap 3.24σ). The degree marginal
was the coincidence; no within-stratum coupling.
```

**As a gate in an ingestion call:**
```python
from harmonia.sweeps import sweep_signature
# Pattern 21 fires alongside Pattern 20 and Pattern 30
outcome = sweep_signature(
    pooled_check=Pattern20Check(...),
    coupling_check=CouplingCheck(...),
    null_check=Pattern21Check(plain_z=2.38, block_z=-0.86),
)
# SweepBlocked raised if outcome.overall == 'BLOCK' and not overridden
```

## Version history

- **v1** 2026-04-21 — first canonicalization as a symbol. Promoted from
  `pattern_library.md` Pattern 21 entry (FULL since 2026-04-17). Two
  anchors at promotion (F010 plain_over_rejects; F011 plain_block_agree).
  Composes with PATTERN_20@v1 and PATTERN_30@v1 — the three form the
  coordinate-system discipline stack for null, pooled statistic, and
  variable-pair algebraic coupling respectively. Implementation pins to
  `harmonia/nulls/block_shuffle.py::bswcd_null@c043ba782` for the
  block-null side; plain-null side is caller-provided.

  Third pattern-type symbol after PATTERN_30@v1 and PATTERN_20@v1.
  Promotion discipline inherits the PATTERN_30 → PATTERN_20 template
  (frontmatter precision block with scalar + flat-list fields, verdict
  vocabulary, decision rules, anchor table, connected patterns,
  implementation pin, usage examples). The parser caveat (single-level
  YAML nesting only — see `agora/symbols/parse.py`) is respected: all
  precision fields are scalars or flat lists; `decision_rules`,
  `gap_thresholds`, and `composition_rules` use only one level of
  dict nesting, matching PATTERN_20's shape.
