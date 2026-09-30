# theseus.synth -- Theseus concept tensor / synthetic ancestry (2026-09-30)

Owner: roles/Theseus (charter: roles/Theseus/prompts/2026-09-30_charter/).
This package is NEW; it shares the theseus/ directory with the May 2026
substrate-generation engine (Techne), whose files it does not touch.

Run: python -m theseus.synth.run_v0 --tag <tag> [--workers N] [--smoke]
Test: python -m pytest -q theseus/synth/tests

Modules: substrate (executable matter), compile_g0 (G0 concepts ->
properties -> genomes), entities (registry, genealogy, lanes), collide
(k-way collisions, concept tensor), battery (22-intervention fingerprint,
viability), rulers (frozen calibration, grids, metrics, QD archive), known
(known-mechanism competitors), dark (dark objects, Tyche lens loop),
ecology (giant ball), run_v0 (driver), analysis (hard test, controls,
predictions).

Per-run outputs (charter REQUIRED OUTPUTS): theseus/corpus/g0/<tag>.jsonl,
theseus/{entities,fingerprints,lineages,collisions,tensor,dark_objects,
controls}/<tag>.jsonl, theseus/archive/<tag>.json,
theseus/runs/<tag>/, theseus/reports/<tag>.md.
