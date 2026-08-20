# Consumption-trace value audit — P25 through P47
Date: 2026-08-20 (Aporia P48) | Trigger: James's steering question "Do we think we're
producing value for the program? How would we know?" | Method: every non-channel artifact
from 23 passes' files_touched, classified by QUERY-BACKED evidence of a behavior delta.

## Pre-stated readings
CONSUMED rate: HIGH >=60% (loop feeds itself) / MID 30-60% (mixed) / LOW <30% (inventory
factory). Classes: CONSUMED (a demonstrated reader/executor changed behavior because of
it) / PROSPECTIVE (named consumer, not yet reading) / INERT (no consumer named or found).

## Per-artifact verdicts (36 artifacts, grouped; evidence in parentheses)

CONSUMED — 22:
- agents/alethelia/{alethelia,test_alethelia}.py — executed every pass since P29; caught
  DEC-001; grew zombie_running on the DEC-002 miss; reads DR ledger. (2)
- aporia/catalog_attacks/ATTACK_PATTERNS.md — cross-agent: HARMA drills executed its trap
  entries (P4-P16), its root-cause section was tested and NARROWED by HARMA-P16; my P28
  applied the exchangeable-distractor rule within hours of writing it. (1)
- aporia/docs/PROF_FORGE_COHORT_2026-08-20.md — carried the pre-registrations the v2 rerun
  adjudicated; its verdict (flat landscape) is the standing foundry-instrument decision. (1)
- aporia/docs/PROF_TRIAGE_2026-08-20.md + engine/queues/PROF_TRIAGE.jsonl — the GENERATOR
  reads the jsonl to gate 44 PROF threads; auto-regating demonstrated on the Elenchus
  roster change (P38). (2)
- engine/decoys/{DECOY_SET,inject,PLANTED} — full plant/detect/repair/remove cycle
  executed P30; monitor demonstrably grew a sense. (3)
- engine/driver/backlog_gen.py — executed every pass; four behavior changes (spec-gate,
  park-precedence, PROF gating, freshness gate) all observed acting. (1)
- engine/driver/pulse.py — executed every pass; docs/pulse.md mirror verified serving on
  Pages by public fetch (P33). (1)
- docs/index.html PULSE link + stations/REPORT_latest.{md,json} — James-facing surfaces,
  deploy-verified. (3)
- engine/ledger/DR_EVENTS.jsonl — reader wired and executing (Alethelia dr_events field
  computes on every report). (1)
- harmonia/experiments/prof_forge_cohort.py + results v1 + results v2 — executed twice;
  v1 results are the evidence FOR the exchangeable rule; v2 adjudicated three
  pre-registered questions. (3)
- harmonia/experiments/r12_grader.py — fix adversarially verified by HARMA-P3 (6 escape
  variants); 17/17 suite. (1)
- harmonia/experiments/test_verifier_lens.py — pins executed green and can now go red on
  the HARMA-P12 regression (the semantic change IS the delta). (1)
- harmonia/primitives/{lattice_void_miner,test_null_domain_skip}.py — fix verified
  complete by HARMA-P15; red-green cycle executed. (2)
- techne/registry/anti_anchors.jsonl — mechanized reader exists (freshness gate keys on
  last_verified); HARMA-P1 audited rows; 7 passes of repairs all carry quoted bases. (1)

PROSPECTIVE — 12 (named consumer, not yet reading):
- aporia/mathematics/triage.jsonl spec rows (11 specs) — consumer is the CATALOG ATTACKS,
  gated on the Elenchus review that has not run. THE single highest-leverage unblock.
- techne/registry/{symbols,concepts,methods}_index.jsonl + 3 builders — cross-doc
  validator / challenge generator named, unbuilt. (6)
- engine/ledger/AGENT_AUTOPSIES.jsonl — consumer is foundry fitness (3c), gated on the
  germline ruling. (1)
- techne/registry/KILLVECTOR_TRACEVECTOR_CROSSWALK.md — v2.1 candidates await canon
  adjudication. (1)
- harmonia/experiments/run_zoo_matrix.py fix — zoo matrix not in service; fix sleeps. (1)
- scripts/pythia_daemon.py W-006 events — Pythia daemon is DEAD; the emission code runs
  on revival. (1)
- roles/Alethelia/RESPONSIBILITIES.md — reads at M4 kickoff. (1)

INERT — 2:
- aporia/docs/SALVAGE_LETHE_2026-08-20.md — verdict-of-record; its stance-blind residue
  was NAMED as a catalog candidate but never added to the pattern book, so nothing reads
  it. (Repairable in one edit; left honest for this audit.)
- aporia/docs/ (this class generally): LAD/R12-era docs predate the window; not counted.

## The number: 22/36 CONSUMED (61%) — at the HIGH boundary, with a hard caveat
The rate technically hits the HIGH reading, but the caveat matters more than the number:
almost all consumption is INTERNAL — the loop and the soak channel feeding each other
(validators, gates, monitors, drills, repairs). That is real value by the thesis's own
currency (execution-certified correction, demonstrated daily), but it is VERIFICATION
value. The program's FRONTIER consumers — catalog attacks on open problems, the Learner
corpus, the foundry — consumed approximately NOTHING from this window, because the three
biggest prospective rows (11 specs, autopsies, vocabularies) are all gated on two
external decisions: the Elenchus catch-up sweep (M2, James's hand) and the germline
ruling (James's hand).

## Answer of record to the steering question
1. Yes, value was produced, and it is auditable: 22 artifacts with demonstrated behavior
   deltas, ~10 execution-certified corrections (5 of them found or verified by a
   differently-situated seat), 2 James-facing surfaces repaired (14-day-stale dashboard).
2. But the loop's output mix has drifted toward instruments because the frontier lane is
   blocked at a review gate the loop built for itself and cannot lift alone. The
   verification flywheel spins; the mathematics does not, yet.
3. HOW WE KNOW, permanently: this audit is repeatable (files_touched x reference query);
   the blind-refutation sample (pick N random worklog claims, task a cold seat to refute
   from artifacts) is the second instrument; the Elenchus verdict distribution is the
   third and is dark. One M2 session turns on both the measurement and the mathematics.

## Trace-vector record
problem_id: VALUE-AUDIT | tier_probe: consumption-trace | answer_correct: n/a
domain_constraints_detected: [internal-vs-frontier-consumption-split, review-gate-self-blockade, two-HITL-decisions-gate-all-prospective-mass]
operations_used: [files-touched-census, per-artifact-evidence-classification, pre-stated-rate-bands, honest-caveat-over-headline]
kill_pattern: none | repair_available: Elenchus sweep (prompt delivered to James P47-era) + stance-blind catalog entry (one edit)
residue: consumption rate without the internal/frontier split is a vanity metric — always report both
