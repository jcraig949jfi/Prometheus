# THESEUS-48 verdict: storing vs releasing the cue at V 8 (prereg roles/Theseus/prereg/2026-10-10_store_release/, d7cf381dd)

Commands:
- python -m theseus.synth.probe_store --tag store_release_2026-10-10 --workers 4 (559 solvers,
  seeds 1-4, law-on and no-law)
- scoring: PYTHONPATH=. python theseus/synth/store_release_score.py (SUMMARY.json)

Validity: for the 424 solvers shared with 45, J_release equals 45's J_V8k8 exactly
(max abs diff 0.0). The probe measures the same task.

## Primaries (CMH over 4 seeds, alpha .025 each)

H-RELEASE: among store-intact solvers (J_store >= .6 at V 8), the share that release
(J_release >= .6).

| seed | law-on | no-law |
|---|---|---|
| 1 | 77/91 | 35/47 |
| 2 | 59/74 | 36/57 |
| 3 | 58/70 | 39/55 |
| 4 | 60/69 | 17/47 |

CMH z 5.50, one-sided p 1.8e-8; RD_MH .216 [.132, .301]. SUPPORTED.

H-STORE: among all solvers, the share that are store-intact.

| seed | law-on | no-law |
|---|---|---|
| 1 | 91/91 | 47/52 |
| 2 | 74/78 | 57/66 |
| 3 | 70/75 | 55/62 |
| 4 | 69/71 | 47/64 |

CMH z 4.78, one-sided p 8.8e-7; RD_MH .116 [.065, .166]. SUPPORTED.

## Descriptive

| | law-on | no-law |
|---|---|---|
| store-intact | 304/315 (97%) | 206/244 (84%) |
| failing at V 8 | 61 | 115 |
| of which STORE-FAIL | 11 | 36 |
| of which RELEASE-FAIL | 50 | 79 (69%) |
| best single store source: X channel | 298 | 192 |
| best single store source: memory row M | 17 (5%) | 52 (21%) |

## Reading

The no-law deficit at a larger alphabet is mainly a RELEASE deficit.
- Most solvers in both arms still HOLD all 8 cue values somewhere before the query: 97% of
  law-on solvers and 84% of no-law solvers.
- What no-law solvers more often fail to do is put the stored value back into the sensor
  channel in a decodable form. Among store-intact solvers they release less often (RD .216).
  Storage also differs, but less (RD .116).
- No-law solvers lean on the memory field (remember/recall: human-derived ops) for storage
  four times as often.
- This fits the provenance of essential parts (36/38/40): about 60% of essential
  collision-generated laws WRITE the sensor channel. The generated k-ary laws are mostly
  release machinery, and law-built release keeps more of the cue's identity than the relay
  and recall paths available without laws.

This is a locus, not yet a mechanism: it says WHERE the no-law implementation loses
information, not why a k-ary law preserves it. A natural next test is a causal swap,
transplanting a solver's essential release law into a matched no-law solver that has the
store intact. Not run in this push.

## Predictions (all RIGHT)

| id | prediction | outcome |
|---|---|---|
| R1 | H-RELEASE SUPPORTED | RIGHT |
| R2 | H-STORE SUPPORTED, p .4 | occurred |
| R3 | no-law failures >= 60% RELEASE-FAIL | 69%, RIGHT |
| R4 | no-law solvers store in M more often | 21% vs 5%, RIGHT |
