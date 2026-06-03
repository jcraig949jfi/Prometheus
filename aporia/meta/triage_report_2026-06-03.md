# Aporia triage report — 2026-06-03

> Stand E instrument panel. Surfaces signals; does not decide. Human reads and adjudicates.

## Queue depth (live tickets)
- `aporia_inbox.jsonl`: 2 live
- `charon_inbox.jsonl`: 2 live
- `ergon_inbox.jsonl`: 14 live
- `harmonia_inbox.jsonl`: 1 live
- `techne_inbox.jsonl`: 65 live

## 1. OPEN tickets older than 14 days (58)
_Stand B: each should convert to ACTIVE_QUEUE / PARKED_SIGNAL / DOCTRINE_CANDIDATE / WONTFIX / SUPERSEDED / CHARTER._
- [27d] `charon_inbox.jsonl` techne-fire-3 — Create Substrate-Tester fire log file (cross-pillar coord from Techne T004) (`C-2026-05-06-T001`)
- [27d] `charon_inbox.jsonl` techne-fire-15 — Orchestrate cross-machine determinism audit (T013 follow-up) (`C-2026-05-07-T013-orchestration`)
- [27d] `techne_inbox.jsonl` aporia-seed — Performance/scale benchmark suite (`T-2026-05-07-T016`)
- [27d] `techne_inbox.jsonl` aporia-seed — Gauntlet threshold sensitivity sweep (`T-2026-05-07-T017`)
- [27d] `techne_inbox.jsonl` aporia-seed — Document KillVector v2 component bounds (`T-2026-05-07-T019`)
- [27d] `techne_inbox.jsonl` aporia-seed — kill_pattern key NFC unicode normalization audit (`T-2026-05-07-T022`)
- [27d] `techne_inbox.jsonl` aporia-seed — W4.7 LR-control reproducibility seed-pinning tooling (`T-2026-05-07-T031`)
- [27d] `techne_inbox.jsonl` aporia-seed — Trial 2 KillVector v2 revalidation harness (`T-2026-05-07-T032`)
- [27d] `techne_inbox.jsonl` aporia-seed — KillEmbedding training corpus accessor (read-only) (`T-2026-05-07-T033`)
- [27d] `techne_inbox.jsonl` aporia-seed — NearMissCorpus pre/post-view-separation audit harness (`T-2026-05-07-T034`)
- [27d] `techne_inbox.jsonl` aporia-seed — F-gate orthogonality MI audit (Charon G4 prep) (`T-2026-05-07-T035`)
- [27d] `techne_inbox.jsonl` aporia-seed — Convergence-bias self-check on substrate verdicts (`T-2026-05-07-T037`)
- [27d] `techne_inbox.jsonl` ergon-loop-fire-9 — Deg-12 +/-5 fixture triangulation follow-up — needed for v1.0 W4.x classified he (`E-2026-05-07-T008-deg12-triangulation-followup`)
- [27d] `techne_inbox.jsonl` substrate-tester:representation — Capability gap: cannot encode homotopy class in higher category (`T-2026-05-07-ST-fire1-002`)
- [27d] `techne_inbox.jsonl` substrate-tester:representation — Capability gap: combinatorial design (BlockDesign / IncidenceStructure) primitiv (`T-2026-05-07-ST-fire1-003`)
- [26d] `techne_inbox.jsonl` substrate-tester:representation — Capability gap: SymbolicLaurentPolynomial primitive missing (HOMFLY knot invaria (`T-2026-05-07-ST-fire21-001`)
- [26d] `techne_inbox.jsonl` substrate-tester:representation — Capability gap: ArityGradedOperationFamily primitive missing (A∞-algebra / dg-al (`T-2026-05-07-ST-fire21-002`)
- [26d] `techne_inbox.jsonl` substrate-tester:mutation-testing — Tier 2 audit gap: TriangulationPathRef frozen-mutation still survives (synthesiz (`T-2026-05-08-ST-fire33-001`)
- [26d] `techne_inbox.jsonl` substrate-tester:representation — Capability gap: finite-group representation (5th in 'Structured Equivalence Clas (`T-2026-05-08-ST-fire35-001`)
- [26d] `techne_inbox.jsonl` substrate-tester:representation — Capability gap: cannot encode M_3 matrix multiplication tensor (catalog entry #4 (`T-2026-05-08-ST-fire38-001`)
- [26d] `techne_inbox.jsonl` substrate-tester:representation — Capability gap: cannot encode optimal tensor network contraction order (catalog  (`T-2026-05-08-ST-fire39-001`)
- [26d] `techne_inbox.jsonl` substrate-tester:representation — Capability gap: tensor isomorphism (catalog entry #58) — GroupAction primitive m (`T-2026-05-08-ST-fire40-001`)
- [26d] `techne_inbox.jsonl` substrate-tester:representation — Border-rank variety membership (catalog #34) — Tier-B four-fire confirmation + S (`T-2026-05-08-ST-fire41-001`)
- [26d] `techne_inbox.jsonl` substrate-tester:representation — Z-eigenvalue distribution (catalog #66) — Tier B QUALIFIED + new Tier D distribu (`T-2026-05-08-ST-fire42-001`)
- [26d] `techne_inbox.jsonl` substrate-tester:representation — Three sigma_kernel test files fail under bare `pytest` invocation; pass under `p (`T-2026-05-08-ST-fire42-003`)
- [26d] `techne_inbox.jsonl` substrate-tester:representation — Tensor PCA threshold (catalog #73) — Tier D CONFIRMED + extended (3->5 primitive (`T-2026-05-08-ST-fire43-001`)
- [26d] `techne_inbox.jsonl` substrate-tester:representation — Kronecker positivity (catalog #95) — Tier E (representation-theoretic) emerges a (`T-2026-05-08-ST-fire44-001`)
- [26d] `techne_inbox.jsonl` substrate-tester:representation — CP identifiability (catalog #40) — 5-tier model HOLDS; refinements only; SATURAT (`T-2026-05-08-ST-fire45-001`)
- [25d] `techne_inbox.jsonl` aporia-seed — Classify 104 tensor open problems by substrate-primitive needs (`T-2026-05-08-T038`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — Lane 16 mutation-testing on method_spec.py surfaces 8/10 surviving mutations: fa (`T-2026-05-08-ST-fire49-001`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — RESOLVED: frozen-mutation puzzle from fire #49 — root cause diagnosed + manifest (`T-2026-05-08-ST-fire50-001`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — RESOLVED: factory-return-value gap from ST-fire49-001 — 11 tests added; all 4 mu (`T-2026-05-08-ST-fire51-001`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — §VI #43 best rank-r approximation — InfimalWitness as Tier B subtype #8 (refinem (`T-2026-05-08-ST-fire52-001`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — Lane 16 on exclusion_certificate.py: 1 genuine test gap (feeds_negative_space_ax (`T-2026-05-08-ST-fire52-002`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — prometheus_math/mutation_testing.py: docstring filter is coarse; AST-level analy (`T-2026-05-08-ST-fire52-003`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — RESOLVED: AST-level docstring filter shipped + fire #50 manifest expanded (12->2 (`T-2026-05-08-ST-fire53-001`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — RESOLVED: ST-fire52-002 — feeds_negative_space_axis return-value gap closed (7 t (`T-2026-05-08-ST-fire54-001`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — Lane 16 on triangulation_protocol.py: 5 surviving mutations (production-grade fr (`T-2026-05-08-ST-fire54-002`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — RESOLVED: ST-fire54-002 — 4 triangulation_protocol mutations now caught (32 test (`T-2026-05-08-ST-fire55-001`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — §II #16 Strassen asymptotic spectrum — 5-tier model holds; FOURTH saturation con (`T-2026-05-09-ST-fire56-001`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — Tier C MomentPolytope/SecantVarietyEquation test-suite stub shipped (17 tests, 6 (`T-2026-05-09-ST-fire58-001`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — Tier A++ TensorNetwork test-suite stub shipped (15 tests, 6 classes) (`T-2026-05-09-ST-fire59-001`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — Tier E stub shipped (24 tests). 5-STUB SET COMPLETE — 94 contract tests ready fo (`T-2026-05-09-ST-fire60-001`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — §XI #88 group-algebra mult — 5th saturation confirmation; CATALOG MATRIX SWEEP C (`T-2026-05-09-ST-fire61-001`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — Extend AST filter to cover string-literal numeric mutations + 2 ride-along retur (`T-2026-05-09-ST-fire61-002`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — RESOLVED: ST-fire61-002 — string-literal AST filter + Symbol/Capability return t (`T-2026-05-09-ST-fire62-001`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — Lane 16 on coordinate_chart.py: 6 genuine gaps + NEW inline-comment FP class (`T-2026-05-09-ST-fire63-001`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — RESOLVED: ST-fire63-001 — inline-comment filter + coordinate_chart return tests; (`T-2026-05-09-ST-fire64-001`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — Lane 16 on operator_portability.py: 7 GENUINE coverage gaps (0 FPs — post-trilog (`T-2026-05-09-ST-fire65-001`)
- [25d] `techne_inbox.jsonl` substrate-tester:representation — RESOLVED: ST-fire65-001 — operator_portability return tests; SCORE 0.300 → 1.000 (`T-2026-05-09-ST-fire66-001`)
- [23d] `ergon_inbox.jsonl` techne — Audit-prep doc for Dims 2/3/10 ready for Ergon consumption check (`T-2026-05-11-techne-to-ergon-dims-2-3-10-audit-prep`)
- [23d] `techne_inbox.jsonl` ergon — Training-anchor ingester entry harness shipped + ready for substrate-shaped pipe (`T-2026-05-11-ergon-to-techne-ingester-ready`)
- [23d] `techne_inbox.jsonl` ergon — Episode-emission consumption-capacity scaffold filed; awaiting Dims 2/3/10 audit (`T-2026-05-11-ergon-to-techne-consumption-scaffold-ready`)
- [21d] `ergon_inbox.jsonl` techne — training_anchor v1.1 schema shipped (optional bs_coverage field, backwards-compa (`T-2026-05-13-techne-to-aporia-and-ergon-training_anchor-v1.1-ready`)
- [21d] `ergon_inbox.jsonl` ergon — 2026-05-13 substrate-shaped pilot ingest: 14 parsed / 0 validated / 0 ingested ( (`T-2026-05-13-ergon-to-techne-pilot-ingest-results`)
- [21d] `ergon_inbox.jsonl` techne — Pilot training_anchor.jsonl staged at expected path — file exists, 0 valid recor (`T-2026-05-13-techne-to-ergon-pilot-staged-training_anchor-zero`)
- [21d] `ergon_inbox.jsonl` ergon — Track 1 closed: substrate-shaped-pipeline-to-Learner round-trip succeeded; behav (`T-2026-05-13-ergon-to-aporia-track1-fixture-created`)
- [20d] `ergon_inbox.jsonl` techne — training_anchor.jsonl now non-empty (2 valid entries with trust-tier discipline) (`T-2026-05-13-techne-to-ergon-training_anchor-jsonl-populated`)

## 2. Missing reasoning-tier / failure-axis (1)
_Stand C: required on tickets filed on/after 2026-06-01._
- `aporia_inbox.jsonl` aporia — Aporia verdict: SPAWN_SIBLING_SCOUR DENIED-as-no-op; menu growth is the real fix (`T-2026-06-03-aporia-polyhymnia-verdict`)

## 3. OPEN tickets with no inferable consumer/target (0)
- (none)

## 4. Pythia reports with no recorded actual_delta (55/55)
_Stand A1 audit incomplete while these stay null. Yield-per-token is unmeasurable until actual_delta is filled._
- critique: 21 unaudited
- literature_survey: 14 unaudited
- coordinate_collision: 8 unaudited
- false_anchor_hunt: 8 unaudited
- proof_decomposition: 4 unaudited

## 5. Repeated failure axes across live tickets (0)
- (no failure_axis fields populated yet — Stand C not yet producing data)

---
_Generated 2026-06-03T16:21:44.445007+00:00 by scripts/aporia_triage_report.py_