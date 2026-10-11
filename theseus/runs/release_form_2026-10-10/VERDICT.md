# THESEUS-50 verdict: is the FORM of a generated law the release machinery? (prereg roles/Theseus/prereg/2026-10-10_release_form/, 2c3293992)

Commands:
- python -m theseus.synth.release_form --tag release_form_2026-10-10 --workers 4
- scoring: PYTHONPATH=. python theseus/synth/release_form_score.py (SUMMARY.json)

## Part A: H-FORM (store-intact solvers; F >= 1 vs F = 0)

F >= 1 means the solver has at least one multi-source react rule writing the sensor channel.
Release counts, F >= 1 vs F = 0:

| stratum | F >= 1 | F = 0 |
|---|---|---|
| law-on seed 1 | 74/87 | 3/4 |
| law-on seed 2 | 58/72 | 1/2 |
| law-on seed 3 | 54/63 | 4/7 |
| law-on seed 4 | 54/61 | 6/8 |
| no-law seed 1 | 17/23 | 18/24 |
| no-law seed 2 | 7/14 | 29/43 |
| no-law seed 3 | 6/7 | 33/48 |
| no-law seed 4 | - | 17/47 |

No-law seed 4 has no F >= 1 solver, so it is excluded from the CMH.
CMH one-sided p .170; RD_MH .059 [-.068, .186]. INDETERMINATE.

F >= 1 share among all solvers: law-on 293/315 (93%), no-law 47/244 (19%).

## Part B: H-MULTI (79 recipients, identical donor draws to 49)

| variant | mean release J | rescued |
|---|---|---|
| baseline | .325 | - |
| SWAP (donor law) | .445 | 31 |
| CTRL (multi-source, coefficients scrambled) | .425 | 26 |
| SINGLE (donor law cut to one non-sensor source) | .500 | 37 |

CTRL - SINGLE: mean -.074, median -.007; Wilcoxon one-sided p 1.0.
VERDICT: NOT SUPPORTED. The single-source cut rescues MORE than the multi-source forms.

## Reading (correcting 49's reading)

49 read the rescue as the law's FORM (multi-source). That is wrong. What rescues release is a
direct coupling from a storage channel back into the sensor channel. The simplest one-source
react does it best: +.175 mean J, rescuing 37/79 = 47% of store-intact, release-failing
solvers.

Law-bearing ecologies supply sensor-writing react rules almost universally (93% of law-on
solvers have one, vs 19% of no-law solvers). The no-law ecology's op repertoire rarely
produces one: its react rules come only from G0 compiles and mutation.

So the release advantage of law-bearing ecologies (48, RD .216) is best read as SUPPLY. The
collision-generated law guarantees every child a k-ary coupling into the sensor channel, and
the release step needs exactly that coupling. It is not a special form or a special set of
learned coefficients.

This is consistent with:
- 45: an essential law's identity does not predict generalisation;
- 47: redundancy does not explain it;
- 49: coefficients barely matter.

Within-arm F does not predict release (H-FORM INDETERMINATE). In law-on, nearly every solver
has F >= 1, so there is no contrast. In no-law, F >= 1 solvers are few and are not better.
The supply reading rests on Part B's causal rescue and the 93% vs 19% contrast, not on Part A.

Claim ceiling (charter): the mechanism found is mundane. The generated k-ary law contributes
a read-back coupling that human-derived rules rarely provide in this substrate. "The
ecology's own laws carry a more general memory implementation" now reduces to "the
ecology's own laws supply the release coupling".

## Predictions

| id | prediction | outcome |
|---|---|---|
| F1 | H-FORM SUPPORTED | WRONG (INDETERMINATE) |
| F2 | H-MULTI SUPPORTED | WRONG (NOT SUPPORTED; single-source is better) |
| F3 | SINGLE raises J by < .05 | WRONG (+.175) |
| F4 | law-on solvers have F >= 1 more often | RIGHT (93% vs 19%) |

F1-F3 go in the ledger as one row. 49's verdict is annotated.
