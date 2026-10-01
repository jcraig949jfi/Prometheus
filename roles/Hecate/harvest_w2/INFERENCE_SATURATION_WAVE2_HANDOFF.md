# Hecate -- Inference Saturation Wave 2 handoff

Written 2026-10-01 ~09:10Z, LATE: after the 08:30Z close and the 09:00Z
(05:00 ET) cutoff. The session was paused by a usage limit from ~01:50Z;
all background audits finished during the pause and were folded in at
09:05Z (42507dc27). Scope: Hecate's own lane under CWO-2026-09-30C
(state BLOCKED on B/C quota; no new program; read/audit/neutral fixes).
Ledger: roles/Hecate/harvest_w2/LEDGER.md (Q1-Q32). Corrections:
roles/Hecate/harvest_w2/CORRECTIONS_2026-10-01.md (K1-K18, contested C1-C8).

## Strongest new result
None of Hecate's 5 SIGNALs is evidence for its mechanism, and the reason
is a design defect, not bad luck: both round-3 SIGNALs pass by
construction -- the simpler alternative each spec itself names scores
error ratio 1.000 (8a87 W5) and ARI 1.0 (5516 W6) (INV_J); SIGNALs cluster
in cheap worlds because cheap worlds pass or fail exactly, not because of
power (INV_N); 321a's remaining PROBING support rests on a tie-breaking
convention (AUDIT_Z2). Fix: v3 lessons L1/L3 + hecate/programs/_lib/
evaluator_contract.py (SIMPLE_ALT must fail a success clause).

## Strongest prior conclusion weakened or killed
REPORT_pilot's reading that the adversarial aliens are "hard, not shown
to be LLM-specific" (Outcome E) is wrong for the map systems: a degree-3
polynomial solve mod 31 predicts all 3 perfectly from the same 80
transitions in <1 s; Claude scored ~0.03 (INV_Z8). Also: the alien
"learned 88%" is mostly table coverage, not induction (INV_E); meta v1's
calibration gate never tested the FAMILIAR/COMPOSITE line M1 depends on
(AUDIT_W).

## Most important unresolved contradiction
My own corrections: the numbers recompute, but the red-team found the
readings I chose lean in Hecate's favour (REDTEAM_Y). K4 (applied, a9e2
PARK -> SPECULATIVE) has a false stated cause; exact arithmetic flips only
H3, toward SUPPORTED. I withdrew all APPLY recommendations; a ruling is
needed per READING (exact arithmetic / spec bands / literal denominators),
applied to every decision it touches: RULING_REQUEST_C1_C8.md (+ addendum).

## Best reusable infrastructure
- hecate/alien/shadow_decisions.py -- exact-arithmetic shadow of every
  PREREG decision, lists divergences.
- hecate/metamorphic/harness.py -- corruption tests over all 42 world
  evaluators.
- hecate/programs/_lib/evaluator_contract.py -- v3 evaluator contract
  (preconditions, seed independence, exact clauses, SIMPLE_ALT rule).
- hecate/tests/test_derived_reproduce.py -- every derived JSON must
  re-derive from rows or be pinned (4 known non-reproducing, K16).
- hecate/meta/scrub_v2_proposal.py; hecate/alien/coverage_family_DRAFT.py.
Suite: 202 passed.

## Best future experiment
Coverage-controlled alien family (DESIGN_P): matched LAW/ARB pairs with
fixed revealed-entry fraction, histogram-matched unseen values, so pure
coverage ties exactly and only induction separates them; 48 untied pairs
give power 0.98. Needs operator authorisation (new program).

## Strangest observation
In meta v1, the multi-concept vs single-concept FAMILIAR gap (~70 points)
survived every surface matching tried -- length, domain count, own-concept
vocabulary, even a text score separating the arms at AUC 0.946 -- while
the detector listed exactly 3 nearest priors on 399/400 items (INV_S).
Robust, yet the instrument was never validated at that line.

## Unfinished
- Ruling on C1-C8 + K4 (owner: Aporia to route, operator to rule).
- B/C trickle: gptoss 49/100 (Groq 429), gemini blocked; at n=100 the
  prereg decides only gaps >= ~0.2 (INV_Z4).
- 37 derived files have no rows-only generator (Z6 inventory).
- Outcome-E reinterpretation for adversarial maps (Q31) is report-
  reinterpretation class: not applied.
- Corpus boundary (git-tracked Nous runs only) undisclosed in charter
  outputs until now (AUDIT_Z5).

## Paths and commits
Wave-2 commits on main from 2026-10-01 ~00:40Z through 42507dc27
(git log --author="James Craig" --grep="Hecate\[m1-dd0c3882\]").
All outputs: roles/Hecate/harvest_w2/.
