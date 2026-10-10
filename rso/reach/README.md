# rso/reach -- reachability cartography and the D1 archive-arm demonstration (C-013-T010, Argus)

Derivative of Nyx's archive-arm ladder (nyx/atlas/experiments/reach_archive/ @ 3318a2098, read only) on the FABLE-5.1
p1_slice reach world (docs/phase3/design/FABLE-5.1/prototype/p1_slice/, read only). Nothing here is Go-Explore: the
program is the state, so returning to an archived program is copying a genome.

| file | what |
|---|---|
| REACHABILITY_CARTOGRAPHY_V0.md | the reusable protocol (five questions, ten measurements, five mechanisms, worked example) |
| PREREGISTRATION.md | D1, frozen before any confirmatory lineage |
| FREEZE_D1.md, FROZEN_D1.json | the freeze record; the runner refuses to start if any frozen hash differs |
| NUMBA_DECISION.md, TIMING_py.json, TIMING_nb.json | the timed port decision |
| DESCRIPTOR_QUALIFICATION.json | descriptor near-miss qualification (descriptor.py) |
| CALIBRATION_B.json | outcome-blind X3G bucket counts (calibrate.py) |
| _proto.py | read-only prototype import shim; sha256 pins of the five prototype files |
| arms.py | the ladder reference (run_ladder, = Nyx's run_lineage/run_chain), reach adapters, kernels |
| arms_nb.py | numba port, exact differential against arms.py |
| certify.py | selection + sealed ruler + independent oracle recheck |
| stats.py | stratified exact test, Fisher, Holm, upper bounds, power |
| descriptor.py | R1/R2 qualification with planted must-fail controls |
| run_d1.py, analyze.py | confirmatory runner (C-013-T012 only) and preregistered analysis |
| tests/ | 75 tests: parity vs Nyx and vs reach.search_lineage, port differential, certification fire tests, stats anchors, analysis on synthetic ledgers, toy end-to-end run |

Environment: numba is required (harry1 had none; an isolated venv outside the repo was used: numba 0.65.1, numpy 2.4.6,
pytest 8.3.3, Python 3.12.10). Run tests: `<python> -m pytest rso/reach/tests -q`.
