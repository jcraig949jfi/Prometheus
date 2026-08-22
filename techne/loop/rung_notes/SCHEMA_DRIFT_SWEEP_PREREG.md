# Pre-registration: is the #78 schema drift a CLASS or an incident?

Written cycle 043 **before measuring any drop rate outside the three ledgers already known**.
Committed before the sweep runs.

## The question

Cycle 042 found a field-level producer/consumer schema mismatch: `load_prepass` filters on a flat
`rep` field that the campaign writer never emits, dropping 100% of 998 rows silently. Seam
triangulation (`SEAM_TRIANGULATION.md`) localized it to the writer, and the underlying condition
was that **no field-level schema is written down anywhere for these ledgers.**

If the absent contract is the real cause, the drift should not be confined to one producer.

## What I already knew when writing this (disclosed)

- `load_prepass` × 3 ledgers, measured in cycle 042: `p1_prepass.jsonl` 998→0 (**100%**),
  `nearmiss_mix-M30_prepass.jsonl` 400→200 (50%, both readers agree), `probe_prepass.jsonl`
  252→126 (50%, flat `rep`). Those three are the KNOWN set and are the control, not the test.
- The `assemble.py` shared-loader family and its live call sites, enumerated repo-wide:
  `load_prepass` 11, `load_forge_scraps` 3, `load_signature_classes` 3,
  `load_theseus_rejected` 0, `load_wall_oracles` 0.
- Which candidate ledger files exist on disk. I have NOT measured any acceptance rate outside the
  three above.

## Population and sample size, declared

**n = every (loader, ledger) pair enumerable repo-wide from the `assemble.py` shared-loader
family where the ledger file exists on disk**, including *latent* pairs whose loader has no live
caller today. Latent pairs are included deliberately: cycle 041 established that prevalence and
live exposure are two populations, and excluding never-called code would rewrite the prevalence
question to flatter the result.

Enumerated before measurement:

    load_prepass          x  p1_prepass.jsonl                 (KNOWN - control, affected)
    load_prepass          x  nearmiss_mix-M30_prepass.jsonl   (KNOWN - control, clean)
    load_prepass          x  probe_prepass.jsonl              (KNOWN - control, clean)
    load_forge_scraps     x  agents/hephaestus/ledger.jsonl   (UNMEASURED)
    load_signature_classes x theseus/.../signature_index.sqlite (UNMEASURED, sqlite not jsonl)
    load_theseus_rejected x  <no live caller; batch path resolved at call time> (LATENT)
    load_wall_oracles     x  <no live caller; corpus path resolved at call time> (LATENT)

**Test set = the UNMEASURED and LATENT pairs only.** The three known pairs are reported as the
control and are excluded from the hit rate, because scoring an instrument on the case that
motivated it is the flattery cycle 038 was built to stop.

## The observable

For each test pair, executed read-only:

    ROWS   records present in the source
    KEPT   records the loader returns
    DROP   1 - KEPT/ROWS

**Signature of the class:** `DROP = 100%` on a non-empty source, *because a field the loader keys
or filters on is absent from the records* — not because a legitimate filter excluded them. The
distinction is checked by inspecting whether the filtered field is present at all, exactly as in
cycle 042 where `key[0]` held the data the flat `rep` filter was looking for.

## Predictions, committed

1. **Primary.** At least one test pair shows DROP ≥ 90% on a non-empty source with the filtered
   field absent. Confidence: **low-to-moderate.** The three known ledgers are 2 clean / 1 broken,
   and one broken producer is compatible with an incident.
2. **Secondary.** Any hit will be a producer written by a DIFFERENT role from the consumer, since
   cross-role seams have no shared review.
3. **Effect direction.** Partial drops (0 < DROP < 100%) will correspond to legitimate filters
   whose field IS present — i.e. drop rate alone will not separate the class; field presence is
   the discriminator.

## Decision rule, fixed in advance

- **CLASS CONFIRMED** — ≥ 1 test pair matches the signature. #78 is the first instance found, not
  the only one, and the absent-schema diagnosis is supported.
- **NULL — INCIDENT, NOT CLASS** — 0 of the test pairs match, and every non-100% drop is explained
  by a filter on a field that is present. Then #78 is a one-off, the "absent contract" story is
  **weakened**, and I report that the class hypothesis failed its first out-of-sample test. **This
  is a real and publishable outcome and it is the one I currently expect to be a coin flip.**
- **INCONCLUSIVE** — test pairs cannot be executed read-only without side effects, or their paths
  are not resolvable without running a producer. Report as unmeasured; do NOT count as null.

## Constraint

No new general-purpose instrument. The sweep calls existing loaders on existing files and counts.
Read-only; nothing outside `techne/` and `prometheus_math/` is modified.

## What would make me wrong

If a test pair shows 100% drop but the filtered field IS present and the exclusion is correct,
that is a legitimate filter and must NOT be counted as a hit. Prediction 3 exists so that this
failure mode is decided by field presence, declared here, rather than by drop rate after the fact.
