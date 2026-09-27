# Atlas status

Currency: 2026-09-25 (promotion absorbed; session saved for a reboot --
  resume record: roles/Atlas/RESUME_2026-09-25.md, which carries the 7
  open questions for the operator and the first actions on resume).

seat state: PARKED by the operator 2026-09-19 for the index LOOP (resume on
  the operator's word). The promotion work of 2026-09-24 was done on the
  operator's direct instruction, not by a loop tick. Routable in comms.
what it asserts: PRESENT (Atlas[m1-1c645957]), ACTIVE, PRODUCTIVE (schema
  atlas on M1 populated by 11 harvesters, the comb rules and the policy
  layer), VALID for the controls in atlas/tests; every classification,
  score and directive is Atlas's own and labelled ATLAS_DERIVED.
workspace: worktree atlas-base-role, branch atlas/promotion-2026-09-24,
  base 0e89f7104.
store: prometheus_fire (M1), schema atlas, migrations 001-010.

index (2026-09-24): 15 engines registered (4 with experiments: sfe,
  archaeon.frontier, npe, vivarium), 50 campaigns, 1,993 experiments (of
  which 46 are Atlas proposals, kind=proposal), 1,645 attempts, 3,280
  segments, 12,643 source pointers, 23,875 facts, 2,278 edges, 221 defects,
  5,662 classified commits, 192 open signals, 365 catalogued external
  ecosystems. Full numbers: reports/REPORT_2026-09-19.txt (index) and
  reports/ROADMAP_2026-09-24.txt (policy).

policy layer (new 2026-09-24):
  theory      10 propositions (1 STRONG, 4 MODERATE, 2 WEAK, 3 UNTESTED),
              7 evidence rows, 13 untested predictions outstanding.
  primitives  20 defined, 15 with a detection rule, 4,099 use rows.
              5 UNMEASURED: error_correction, partial_heredity,
              reproductive_closure, temporal_gating, write_authority.
              That is an instrumentation gap, NOT a coverage claim.
  soup        190 primitive pairs: 89 TESTED, 85 UNEXPLORED,
              16 SUGGESTED_BY_EVIDENCE.
  scores      46 proposals scored under atlas.policy/2 (policy/1 kept with
              its defect recorded: novelty was 0.000 for every proposal).
  portfolio   3 ISSUED updates, one per horizon (10 STRATEGY, 11 THEORY,
              12 MICRO); 5 superseded. MICRO currently reports HOLD plus a
              coverage-lag NOTE.
  blind spots 7 (5 COMMISSIONED as proposals, 2 OPEN: BS-memory-outside-world,
              BS-parent-child-detectors).

index coverage lag: 4.9 days. Newest MODELLED experiment activity
  2026-09-19 08:55; newest indexed commit 2026-09-24 07:09. Activity newer
  than that is unadapted or not visible from M1 -- it is never reported as
  absence, and every horizon must state this lag.

coverage: M1 only. M2-local evidence (frontier runs/, the M2 SFE ledger, M2
  logs) is recorded as EXPECTED:M2.
monitors owned or fed: AtlasIndexLoop -- PARKED (MONITORS.md; session loop,
  ~60 min, bound 6 non-productive ticks, accountable Atlas-M2; tick in
  loop/TICK.md). On resume the tick also advances the policy cadence:
  MICRO every ~10 newly indexed experiments, STRATEGY ~100, THEORY ~1000.
sibling seat: Atlas-M2 (m2-8f915f3d, M2), its own seat, one shared index
  (SIBLINGS.md).
blockers: none. Waiting: Cosmos's atlas_export_c0 harvest (comms #544).
ruled 2026-09-19: F:/SerendipityD is ignored for now (operator).
ruled 2026-09-25 (operator): one index pass then PARKED (both seats);
  REPORTS ONLY -- no portfolio directives posted to seats, anti-prior
  proposals go to the operator first; ATLAS-26 = keep inferring hosts,
  labelled, no interface requests; F:/SerendipityD still ignored.
pass 2026-09-25 (Atlas[m1-a5680f90]): lag now 2.7 days (modelled
  2026-09-22 15:07). Nestor C9, Ananke, Cosmos still unadapted.
  OPEN DEFECT: frontier/3 indexed 299,991 identical BLOCKED_BY_SUPPRESSION
  events as separate facts, so fact counts are distorted until frontier/4.
  See journal/2026-09-25.md.
repair 2026-09-26 (operator-authorized, bounded; Atlas stays PARKED):
  ATLAS-37 DONE -- cosmos/1 ingests the MANIFEST-verified C0 export (engine
  cosmos: 3 campaigns, 10 experiments, 10 attempts on M2, 8,856 facts,
  3,096 edges). frontier/4 HELD: Archaeon has not answered the operator's
  producer-semantics question, so the 299,991 suppression-echo facts still
  inflate CONCLUDED counts. See journal/2026-09-26.md.
reboot 2026-09-25: nothing in flight (Atlas runs no experiments; no
  collector, harvest or loop running). Tree clean, HEAD == origin/main at
  4e0fb48cb, all seven atlas/* branches merged. Index is ~1 day behind git
  and ~6 days behind in modelled activity -- adapter coverage, not quiet
  engines; re-harvest before reading anything as absence.
next executable action: ATLAS-37 (Cosmos export adapter), ATLAS-38 (model
  Nestor's S-series forensics as first-class evidence), ATLAS-39
  (instrumentation for the 5 unmeasured primitives).
