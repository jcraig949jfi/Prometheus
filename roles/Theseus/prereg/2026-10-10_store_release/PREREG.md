# THESEUS-48 preregistration -- why law-built solvers generalise: storing vs releasing the cue

Currency: 2026-10-09 (written during the compute pause; the run starts after 2026-10-10T00:00Z).
Code: theseus/synth/probe_store.py (new); task_system.py; pooled.py; hashes in
CODE_HASHES.txt.

Disclosure: two genomes were probed to validate the code. The probe's J_release must equal
task_J(V 8, k 8, ch0) exactly.
- a law-on solver: store 1.0, release 1.0, matching 45's 1.0
- a no-law solver: store 1.0 (memory row M0), release .21, matching 45's .21
No other probe output has been seen.

## Why

Law-built solvers generalise to V 8 far better than no-law solvers:
- 45: RD .166, seeds 1-3
- 47: 85% vs 27%, seed 4

Two candidate mechanisms failed preregistered tests: a single essential law (45) and
redundancy (47). The task needs two steps: STORE the cue through the distractors, then
RELEASE it into the sensor channel at the query. Which step breaks for no-law solvers at
V 8?

## Measurement (python -m theseus.synth.probe_store --tag store_release_2026-10-10 --workers 4)

Population: every selected-task solver (J >= .6 at V4 k8) of the law-on and no-law runs of
seeds 1-4 (the 45 and 47 populations; 559 solvers).

At V 8, k 8 (task seed 0, 400/400, the task_J draws), ridge decoders give:
- J_store: the cue decoded from the state before the query, using every non-sensor channel
  and all memory;
- J_release: the cue decoded from the sensor channel after the query. This is the task J.

Store-intact = J_store >= .6. Released = J_release >= .6.

## Primaries (CMH over the 4 seed strata, one-sided, alpha .025 each)

H-RELEASE: among store-intact solvers, law-on solvers release more often than no-law ones.
H-STORE: among all solvers, law-on solvers are store-intact more often than no-law ones.

Each is SUPPORTED iff p < .025 AND the RD_MH CI lower bound > 0; NOT SUPPORTED iff RD_MH <= 0;
else INDETERMINATE.

## Descriptive

Failure locus of solvers that fail at V 8 (J_release < .6), by arm:
- STORE-FAIL: J_store < .6
- RELEASE-FAIL: J_store >= .6

Also: the best single store source (X channel vs M row) by arm; J_store vs J_release
distributions.

## Predictions

| id | prediction | p |
|---|---|---|
| R1 | H-RELEASE SUPPORTED | 0.6 |
| R2 | H-STORE SUPPORTED | 0.4 |
| R3 | no-law failures are mostly RELEASE-FAIL (>= 60% of failing no-law solvers) | 0.55 |
| R4 | no-law solvers store in M (memory) as their best single source more often than law-on solvers | 0.5 |

## Compute

559 solvers x one V8 k8 episode set with per-source decoders: ~1 CPU-hour (MWO R2 cap 16).
