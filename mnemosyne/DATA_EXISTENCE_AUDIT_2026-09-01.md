# Data-Existence Audit — 2026-09-01 (Mnemosyne)

Population: all 534 rows of questions.jsonl joined to triage.jsonl (510 triaged; 24 untriaged).
Spine counts verified live (reltuples) at run time. Availability != attackability; the spec-author lane owns that judgment.

## Verdict histogram
- UNCLAIMED_CANDIDATE_DATA: 253
- NO_KNOWN_COUPLING: 222
- PURE_COMPUTE: 22
- CLAIMED_AND_PRESENT: 20
- CLAIMED_NEEDS_EXTENSION: 17

## Spine tables referenced, with live size
- algebra.groups: 544,831 rows
- algebra.lattices: 39,293 rows
- algebra.space_groups: 230 rows
- analysis.oeis: 394,454 rows
- charon_duckdb.dirichlet_zeros: 184,830 rows
- charon_duckdb.object_zeros: 120,649 rows
- physics.codata: 355 rows
- physics.materials: 10,000 rows
- physics.pdg_particles: 226 rows
- physics.superconductors: 16,414 rows
- public.artin_reps: 798,140 rows
- public.ec_curvedata: 3,824,372 rows
- public.g2c_curves: 66,158 rows
- public.lfunc_lfunctions: 24,351,376 rows
- public.mf_newforms: 1,141,510 rows
- public.nf_fields: 22,178,568 rows
- topology.knots: 12,965 rows
- topology.polytopes: 980 rows

## UNCLAIMED_CANDIDATE_DATA by subdomain (the dust-collecting class)
Bucket-C/'no data coupling' default rows whose subdomain has loaded data:
- number_theory: 75 problems <- public.ec_curvedata, public.nf_fields, public.lfunc_lfunctions, analysis.oeis, charon_duckdb.dirichlet_zeros
- additive_combinatorics: 41 problems <- analysis.oeis
- combinatorics: 33 problems <- analysis.oeis
- discrete_geometry: 32 problems <- algebra.lattices, topology.polytopes
- algebraic_geometry: 16 problems <- public.ec_curvedata, public.g2c_curves
- mathematical_physics: 16 problems <- physics.codata, physics.pdg_particles, physics.materials, physics.superconductors
- analytic_number_theory: 13 problems <- public.lfunc_lfunctions, charon_duckdb.dirichlet_zeros, charon_duckdb.object_zeros, analysis.oeis
- group_theory: 11 problems <- algebra.groups, algebra.space_groups
- additive_number_theory: 9 problems <- analysis.oeis
- quantum_information: 4 problems <- physics.pdg_particles
- diophantine_approximation: 1 problems <- analysis.oeis
- knot_theory: 1 problems <- topology.knots
- convex_geometry: 1 problems <- topology.polytopes, algebra.lattices

## CLAIMED_BUT_ABSENT (drift between triage claims and live spine)
- none: every recognized claimed source exists in the live spine

## CLAIMED_UNRECOGNIZED (data_source text my recognizer could not map)

## JOIN-INTEGRITY FINDINGS (file-level defects, not data-availability)
- questions.jsonl: 537 lines, 534 unique ids; duplicate ids: MATH-0491, MATH-0492, MATH-0493
- ID COLLISIONS (same id, DIFFERENT problem — one problem is shadowed everywhere downstream): MATH-0491, MATH-0492, MATH-0493
- triage.jsonl: 531 lines, 510 unique ids; duplicate ids: 21
- Authored-spec rows APPENDED over an earlier unspecced row (safe only for last-wins readers like backlog_gen.py:67; a first-wins reader sees bucket-C/unspecced): MATH-0057, MATH-0058, MATH-0060, MATH-0065, MATH-0066, MATH-0067, MATH-0129, MATH-0137, MATH-0154, MATH-0211, MATH-0212, MATH-0287, MATH-0293, MATH-0306, MATH-0316, MATH-0324, MATH-0348, MATH-0368
- Duplicated question ids also mean backlog_gen emits the CAT-<id> thread once per duplicate line (questions.jsonl is iterated, not deduped).

## Untriaged questions (in questions.jsonl, missing from triage.jsonl)
- MATH-0514 (Caccetta-Haggkvist conjecture) [graph_theory]
- MATH-0515 (Sidorenko's conjecture) [graph_theory]
- MATH-0516 (Broue's abelian defect group conjecture) [representation_theory]
- MATH-0517 (Atiyah conjecture on L2-Betti numbers) [topology]
- MATH-0518 (Greenberg's conjecture on Iwasawa invariants) [number_theory]
- MATH-0519 (Zimmer's conjecture on lattice actions) [dynamical_systems]
- MATH-0520 (Fakhruddin uniform boundedness for rational preimages) [dynamical_systems]
- MATH-0521 (Baker-DeMarco dynamical Andre-Oort) [dynamical_systems]
- MATH-0522 (Poonen rational 4-cycles conjecture) [dynamical_systems]
- MATH-0523 (Tropical maximal rank conjecture) [algebraic_geometry]
- MATH-0524 (Realizability of tropical curves) [algebraic_geometry]
- MATH-0525 (Loop space formality conjecture) [algebraic_geometry]
- MATH-0526 (Additivity of min output entropy for EB channels) [quantum_information]
- MATH-0527 (Quantum Unique Games conjecture) [computational_complexity]
- MATH-0528 (Exact Ryu-Takayanagi for random tensor networks) [mathematical_physics]
- MATH-0529 (Flajolet-Odlyzko conjecture on generating functions) [combinatorics]
- MATH-0530 (Stanley chromatic symmetric function distinguishes trees) [combinatorics]
- MATH-0531 (Cohen-Lenstra-Martinet heuristics for non-abelian extensions) [number_theory]
- MATH-0532 (Selmer group distribution heuristics (BKLPR)) [number_theory]
- MATH-0533 (Viterbo volume-capacity conjecture) [symplectic_geometry]
- MATH-0534 (Stochastic quantization of Yang-Mills 4D) [mathematical_physics]
- MATH-0535 (Chromatic splitting conjecture) [topology]
- MATH-0536 (Vorst K-regularity conjecture) [algebra]
- MATH-0537 (Durrett spatial fixation conjecture) [probability_theory]
