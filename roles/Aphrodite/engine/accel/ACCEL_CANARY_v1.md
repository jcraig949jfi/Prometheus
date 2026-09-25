# ACCEL_CANARY_v1 -- frozen equivalence canary for accelerated backends

Status: FROZEN at commit time. Written and committed BEFORE any backend code
exists on this branch. Any change to this file is a new canary version
(ACCEL_CANARY_v2, ...), never an edit in place.

Branch: `aphrodite/accel-azure-cpu-2026-09-23`, forked from clean science SHA
`cf601fa3e`. Engineering/conformance only. This branch may not modify the
science branch and no accelerated backend may contribute scientific results
until it passes this canary with ZERO unexplained semantic/charge mismatches
(operator ruling 2026-09-23).

## 1. Reference (the M4 serial run, committed)

| file | git blob | sha256 |
|---|---|---|
| `roles/Aphrodite/engine/TIER3C_RESULTS_2026-09-22.json` | `4760bbf0911a7692f117f0e1bf6de3c67b89c1d6` | `bdeb3ad831d25fca53b7297a6b8ecee450726e419f119177c3076c6ed9321bbd` |
| `roles/Aphrodite/engine/TIER3C_ARTIFACT_2026-09-22.json` | `71be7ecb3ecff12b41553aafdab9e1fea32316a0` | `afe040e960a0ee056160347c633553606a1bb848a611721699c928c1b7eb075e` |
| `roles/Aphrodite/engine/CONFORMANCE_GATE_2026-09-22.json` | `878b2f2f710daa3690750a125c95943c351369cb` | -- |

Reference content:

* **Transplant rows**: `detail[family][arm]` for all 3 families
  (`tc_new_sumgcdlast_minus_first`, `tc_new_summod_times_first`,
  `tc_rel_sum_minus_first`) x 10 arms (`EVOLVED`, `PRISTINE`, `SHAM_0`..`SHAM_7`)
  x 16 recipients (0..15) = **480 rows**. Reference totals: 227 qualified rows,
  sum(escrow_spent) = 106,839,976.
* **Conformance**: `conformance.check()` FULL sweep (limit_cases=0):
  900 programs, **21,600 comparisons, GREEN**, 0 mismatches.
* Serial wall-clock of the reference Tier-3C run on M4: 1196.7 s (whole
  pipeline including gate, qualification and meta stages).

## 2. Inputs the backend must use (no re-derivation)

* EVOLVED arm: `run_tier3c.Lib(TIER3C_ARTIFACT.evolved_entries)`; its
  `sha256()` must equal `evolved_sha256` = `2849244e1637...e079766`.
* PRISTINE arm: `run_tier3c.pristine()`; `sha256()` must equal
  `pristine_sha256` = `c2fc843e829a...0e1517c7b`.
* SHAM_k arms: `run_tier3c.Lib(run_tier3c.stage_shams()[k])`.
* Per-family dev size: `TIER3C_RESULTS.generator_qualification[fam].size`.
* Every cell is computed by calling `run_tier3c.run_recipient(fam, arm, lib, i, size)`
  UNCHANGED. No engine file may be modified.

## 3. Equivalence (the verdict rule)

A backend run is **EQUIVALENT** iff ALL of:

1. All 480 (family, arm, recipient) rows are present, no extras, no duplicates.
2. For every row, every field is identical to the reference (exact JSON value
   equality, including null vs value and type): `recipient`, `arm`, `family`,
   `escrow_spent`, `qualified`, `charges`, `coordinate`, `solution_body`,
   `artifact_bytes`, `false_positives`. Wall-clock is the ONLY field exempt
   (rows carry none; backend timing is recorded separately).
3. Library hashes for EVOLVED and PRISTINE match the reference hashes.
4. `conformance.check()` full sweep is GREEN with exactly 21,600 comparisons
   (and 900 programs, 0 mismatches).

Anything else is **NOT_EQUIVALENT**. A mismatch is a FAIL unless fully
explained by a documented root cause; an explained mismatch is still NOT
equivalence -- it only changes the diagnosis, never the verdict.

## 4. Output

`ACCEL_EQUIVALENCE_<backend>_<host>.json` containing: reference hashes, the
backend run's head SHA, worker count, host, wall-clock, per-row diffs (every
differing field with reference and backend values), missing/extra rows,
conformance result, mismatch count, and the verdict.
