# THESEUS-27b preregistration -- structure selection, with a cap that binds and selection at parent choice

Currency: 2026-10-08. Committed before any run of this configuration.

## Why

THESEUS-27 was VOID (acbb40334): the protected pca-elite set outgrew the cap (active 390)
and selection acted only through elite membership, while R5 is weakly heritable through
collisions (Spearman parent->child .14-.18, slope .22-.30). Two fixes, nothing else:
  --elite-protect-k 150   only the top 150 elites by quality are protected (cap 300)
  --seed-select 1.5       coalition seed weight x exp(1.5 * z(quality)); partners keep
                          the v0 near/far/under/random modes (distant pressure unchanged)
Default-preservation verified: with all new flags at defaults, a smoke run reproduces the
THESEUS-25 reference entities 125/125.

## Design

Common: PYTHONHASHSEED=0, master seed as v0_1, law ON, 30 generations, --ecology-only
--pop-cap 300 --elite-grids pca --dark-protect-gens 3 --elite-protect-k 150 --seed-select 1.5
  SELB-REP: --quality rep   (tag v0_1_selbrep_2026-10-08)
  SELB-R5:  --quality r5    (tag v0_1_selbr5_2026-10-08)
PRIMARY: H1 by the unchanged rule (h1_rescore --d-ref <tag> --a-v1-rows
theseus/runs/h1_large_A_2026-10-08/A_V1_ROWS.jsonl), arms A/B/C/R from v0_1.
MANIPULATION CHECK: median R5 of viable DEEP+VERY_DEEP children, SELB-R5 minus SELB-REP,
bootstrap CI (r5_trend).
BINDING: max active <= 345 (cap 300 + one generation's births) in both runs.

## Decision rule (unchanged from 27)

- cap does not bind in either run -> VOID.
- manipulation check CI not above 0 -> selection did not take; H1 reported descriptively.
- STRUCTURE-SELECTION-HELPS: H1 PASS for SELB-R5 and not for SELB-REP.
- NO-HELP: H1 not PASS for SELB-R5.  BOTH-PASS: reported as such.

## Predictions

T1 the cap binds in both runs.                            p = 0.85
T2 manipulation check passes (CI above 0).                p = 0.45
T3 H1 is not PASS for SELB-R5.                            p = 0.8
T4 H1 is not PASS for SELB-REP.                           p = 0.85

Compute: 2 ecology-only runs (~22 min each) + 2 H1 rescorings; ~3.5 CPU-hours.
