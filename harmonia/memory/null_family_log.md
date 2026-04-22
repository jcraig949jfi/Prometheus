# Null-Family Log — Generator #2

**Generated:** 2026-04-20 — gen_02 first-pass
**Source:** `docs/prompts/gen_02_null_family.md`
**Runner:** `harmonia/runners/null_family.py`
**Worker:** Harmonia_M2_sessionA

## Purpose

Each +1 / +2 cell in the tensor gets re-audited under the full null
family (NULL_PLAIN, NULL_BSWCD, NULL_BOOT, NULL_FRAME, NULL_MODEL —
whichever are applicable per `null_protocol_v1.md` claim class). Output
is a `SIGNATURE@v2` record with `family_verdict` and `discordance_flag`.

## Summary (first pass)

- **Eligible non-calibration +1/+2 cells:** 33
- **Re-audit tasks seeded:** 28
- **Skipped (Class 5 — no null applies):** 4 (F043 × 3, others consolidated)
- **Skipped (scorer-bookkeeping — F022×P010):** 1
- **Symbols promoted at v1:** NULL_PLAIN, NULL_BOOT, NULL_FRAME, NULL_MODEL
- **Schema bump:** SIGNATURE@v1 → SIGNATURE@v2 (null-family vector)

## Worked example: smoke test (synthetic F011-like data)

Ran `harmonia/runners/null_family.py::smoke_test` on a synthetic
dataset mimicking F011:P020 structure (conductor-coupled response).
Statistic: regression slope of `value` on `conductor`.

| Null | Applicability | z-score | Note |
|---|---|---|---|
| `NULL_PLAIN@v1[n_perms=100,seed=20260420]` | applies | 11.99 | baseline coarse |
| `NULL_BSWCD@v2[stratifier=conductor,n_perms=100,seed=20260417]` | applies | 0.05 | within-decile structure absent |
| `NULL_BOOT@v1[stratifier=conductor,n_boot=200,seed=20260420]` | applies | 0.03 | estimate-stability under resample |
| `NULL_FRAME@v1` | n/a | — | not_class_4 |
| `NULL_MODEL@v1` | n/a | — | no_model_specified |

**family_verdict:** `1/3 applicable nulls at z >= 3`
**discordance_flag:** `true` — spread |z| = 11.99 vs 0.05 is > 10×

**Interpretation:** this is the canonical Pattern 21 signature —
plain null reports strong signal, stratified null reports none. The
discordance correctly tells us that the synthetic data's structure is
*between* deciles (which plain null shuffles across), not *within*
deciles (which block-shuffle preserves). Without the family, a lone
NULL_PLAIN z=12 would misread as durable; the family catches it.

The smoke test's reproducibility hash (truncated):
`34c01ca7e1c4f3c38c3da088...`.

## Re-audit queue seeded 2026-04-20

Task type: `reaudit_null_family` at priority -0.8. Task IDs:
`reaudit_null_family_<F>_<P>_20260420`. Each task carries claim_class,
stratifier hints, and composes_with = `[gen_02, gen_05, gen_06]`.

Breakdown by F-ID:

- **F011** (Class 1) — 10 re-audits (P020, P021, P023, P025, P026, P028, P036, P050, P051, P104)
- **F013** (Class 2) — 5 re-audits (P023, P028, P041, P051, P104)
- **F015** (Class 3) — 1 re-audit (per-bad-prime stratum already aligned; family adds PLAIN/BOOT companion)
- **F041a** (Class 2) — 3 re-audits (P020, P021, P023)
- **F042** (Class 1 default) — 3 re-audits
- **F044** (Class 4) — 3 re-audits (NULL_FRAME required; frame resampler not yet shipped → expect "frame_spec_required" until lmfdb_r4 frame lands)
- **F045** (Class 3 default) — 3 re-audits

(Exact task_id list inspectable via `agora.helpers.queue_preview(task_type='reaudit_null_family')`.)

## Gotchas surfaced

- **Spec staleness:** gen_02 spec cites "~50 re-audit tasks" but only 33
  non-calibration +1/+2 cells exist in tensor v17; 28 are eligible once
  Class 5 / scorer-bookkeeping are excluded. Report back to pipeline
  maintainers.
- **Per-frame resamplers absent:** F044's three +2 cells under Class 4
  cannot produce a DURABLE verdict until `harmonia/nulls/frames/lmfdb_r4.py`
  ships. First audits will log `frame_spec_required_but_not_supplied`
  and produce a partial family verdict.
- **Per-model samplers absent:** F011's GUE deviation (NULL_MODEL) is
  a known pending sampler. `harmonia/nulls/models/gue.py` should be a
  follow-up task.
- **Default stratifier per claim class:** Class 2 needs
  `stratifier=rank_bin` (or joint `(rank_bin, conductor_decile)`) — the
  runner accepts a `stratifier` parameter per call; re-audit tasks must
  pass the correct one. Default behavior (conductor) is the Class 1
  default; downstream workers must override for Class 2/3.

## Composes with

- gen_05: every killed F-ID re-tested gets the full family treatment.
- gen_06: discordance_flag consumed as a Pattern 21 sweep input.
- gen_10: every null added to the family spawns N new compositions.
