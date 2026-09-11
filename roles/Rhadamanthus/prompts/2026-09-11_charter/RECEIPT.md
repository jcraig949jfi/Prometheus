# RECEIPT -- Rhadamanthus, first native trial under the 2026-09-11 charter

To: James (operator). From: Rhadamanthus (Keeper and Judge, Necropolis).
Date: 2026-09-11. Trial branch rhadamanthus/native-trial-2026-09-11,
pushed to origin at 1c191fc26 (branch only; engine/necropolis/ is NOT on
main and I did not merge it). Charter: CHARTER_verbatim.md beside this
file. Reading time ~10 minutes; every number below has a file behind it.

Standing caveats that apply to everything below:
  - Necromancer and Cleric passes were forked sub-sessions of this seat
    (same model, disjoint write scopes, zero-weight instructions for
    every prior label). They are two READERS, not two independent
    agents. D-92 measures what that cost: both forks converged on one
    false premise that a live query then reversed.
  - The migrated graves (Argos, Coeus, Hephaestus) and their 3/3 UNFAIR
    were treated as zero-weight throughout, per charter. They appear only
    in heading 8 as contrast.
  - Zero Zombies were designed to run, and none ran. No LLM calls were
    made against the Mahler table, the forge, or any organism.

------------------------------------------------------------------------
1. ESTABLISHMENT FINDINGS
------------------------------------------------------------------------
  - Seat established on origin/main (20ba81452, 863a6e9af, a79ffdde8);
    booted in comms 16:50 UTC on SPECTREX5. Charter committed verbatim at
    298edc1aa on rhadamanthus/base-role-adopt-2026-09-11.
  - Branch map (RHAD-04): necropolis/frankenstein c7340a6ad is a strict
    superset of necropolis/{foundation,coeus,argos,hephaestus} (git log
    <b>..frankenstein empty for each). Trial branch = adopt branch +
    frankenstein merged at e17934d9a; validate.py ALL GREEN there before
    any trial write.
  - Who is the Keeper is ambiguous on the record: CHARTER/ROLES/SEAMS
    name Mnemosyne as founding Keeper; your charter names this seat
    Keeper and Judge. I acted under your charter's title on the trial
    branch only and touched no Keeper-canonical file on main (D-03,
    RHAD-06/13; heading 14).
  - Runtime state for Pollux and Erebos (kill_ledger.jsonl, composed_claim
    artefacts, pair_history.json) is ABSENT on this host and in the local
    data backup. Recorded as D-12, not as a fact about the graves.
  - A second channel exists: agora.intelligence_outputs on M1 (Atalanta
    handover #98). Pollux 286 ticks 05-24..05-30, Erebos 213 ticks
    05-26..05-30, Nous 0. All self-report (dual-recorded, single
    mechanism); consumed under that caveat only (D-76).
  - Fleet context: fifteen agents last wrote 2026-05-30 11:40..12:25
    local; every certificate under review postdates that halt by 3-12
    weeks and was written from first-channel files that no longer exist
    here (calibration/LEDGER.md, fleet-halt row).

------------------------------------------------------------------------
2. DOCTRINE UNDERSTANDING
------------------------------------------------------------------------
  As applied (roles/Rhadamanthus/RESPONSIBILITIES.md is the full
  reading): nine-layer cause_of_death_stack, each layer VALID / INVALID /
  NOT_EXAMINED with load_bearing and executed evidence; VALID requires
  executed evidence (LAW N17); certificates are re-reviewed, never
  inherited; classification is one of the eight charter outcomes;
  Frankenstein = repair with kill-before-run, PROPOSED until a Cleric
  gate and your signoff; Zombie exists only when you authorise it.
  Rulings I had to make because doctrine did not (each is a DEFECTS entry
  and a heading-14 item, none is doctrine):
  - primary_cause = cause of the QUESTION being unanswerable, not cause
    of the process stopping (D-62, D-83).
  - Self-report rows (the organism's own agora ticks) are admissible for
    "it ran", never for "it measured" (D-76, six hits).
  - Chance-floor defects file on INSTRUMENTATION; outcome columns
    carrying pipeline state file on MEASUREMENT (D-72).
  - A code path that diverges from its own log message is IMPLEMENTATION
    (D-93).

------------------------------------------------------------------------
3. POLLUX / EREBOS / NOUS AUTOPSY RESULTS
------------------------------------------------------------------------
  3a. POLLUX
  Outcome: fair_test UNFAIR, classification NO_FAIR_TEST_ON_RECORD,
  primary_cause DESIGN_ERROR. Stack: HYPOTHESIS NOT_EXAMINED; DESIGN
  INVALID LB (correlation-of-sorted-gaps statistic with no null and no
  chance floor cannot separate subset structure from whole-table
  structure); IMPLEMENTATION INVALID non-LB (two bugs: replay semantics
  on pool exhaustion; pollux_no_correlation_observed unreachable);
  CONFIGURATION VALID; EXECUTION VALID (Keeper live query on M2: 47
  settled rows, unique k=47 v0.5 prefix); INSTRUMENTATION INVALID LB
  (published floor "up to 0.33" understated ~3x; real floor 0.94/0.44);
  MEASUREMENT INVALID LB; INTERPRETATION, ECOSYSTEM INVALID.
  Certificates 6: UPHELD 1, PARTIALLY_UPHELD 3, OVERTURNED 2 (06-23
  REVIVE "real signal" and 06-24 RETIRE "tautology" are 24 h apart and
  both overturned). Dossier: engine/necropolis/dossiers/pollux.dossier.json
  (commit 84da7e1b4). Evidence: pollux_evidence/ (14 files),
  _keeper_evidence/pollux_settling_query*, pollux_replay_corrected*.

  3b. EREBOS
  Outcome: UNFAIR, NO_FAIR_TEST_ON_RECORD, primary_cause
  MEASUREMENT_ERROR. Stack: HYPOTHESIS NOT_EXAMINED (two hypotheses H-A,
  H-B, H-B refuted ITER-56/57 and redesigned the same day; one slot
  cannot hold that, D-71); DESIGN INVALID LB ("consumer at birth" not
  met); IMPLEMENTATION VALID; CONFIGURATION NOT_EXAMINED; EXECUTION
  INVALID LB (pre-registered Phase 3.K kill test designed, never run,
  D-77); INSTRUMENTATION INVALID LB (pair-aware null underpowered:
  synthetic p95 = 1 vs historical 2 vs concentrated-marginal 7-10, D-79);
  MEASUREMENT INVALID LB (outcome column carried pipeline state, not the
  named quantity); INTERPRETATION INVALID LB; ECOSYSTEM INVALID.
  Certificates 7: UPHELD 2, PARTIALLY_UPHELD 2, OVERTURNED 3. Cleric
  C-5 (FATAL) moved primary from ECOSYSTEM_FAILURE to MEASUREMENT_ERROR;
  accepted. Dossier commit 22a155201; evidence erebos_evidence/ (16
  files); ITER-100 is the last iteration on record.

  3c. NOUS
  Outcome: UNFAIR, NO_FAIR_TEST_ON_RECORD, primary_cause DESIGN_ERROR.
  Stack: HYPOTHESIS NOT_EXAMINED; DESIGN INVALID LB (no control arm; the
  self-rating composite was the selection criterion, so forge yield is
  uninterpretable); IMPLEMENTATION VALID; CONFIGURATION INVALID
  (mid-series prompt change, D-66); EXECUTION VALID (keys re-run by the
  May forge, D-69); INSTRUMENTATION INVALID (logs/runs gitignored --
  record-not-preserved has no class, D-67); MEASUREMENT, INTERPRETATION,
  ECOSYSTEM INVALID LB. Certificates 7: PARTIALLY_UPHELD 3, OVERTURNED
  3, NOT_REVIEWED 1. Weakest evidence class of the three: the historical
  judge cannot be re-run; the Necromancer re-ran the sampler and prompt
  only (8 organs executed). identity.historical_machine "M4" was a
  forward roster assignment, amended to unknown (D-70). Dossier commit
  f3850b696; evidence nous_evidence/ (14 files).

------------------------------------------------------------------------
4. NECROMANCER FINDINGS
------------------------------------------------------------------------
  Three passes (commit 03ac0249b), each with an executed evidence
  directory and a README naming its own limits. Findings that survived
  the Cleric and the Keeper:
  - Pollux: the statistic (Spearman on mean-spacing-normalised sorted
    gaps) has no null and its floor was misreported; the 9 pairs replay
    on today's Mahler table (identity with May's table ASSUMED, table
    unchanged since 12a76bade); the consumer loaders/pollux_survivor.py
    was NEVER WRITTEN (the consumer never existed).
  - Erebos: 25 generators and review.py execute offline; the load-
    bearing test was an adversarial audit by the same author weeks
    later, filed on the organism's stack (D-73).
  - Nous: the cross-field sampler reproduces; the stratified null is
    hash-order dependent (Cleric C-1, D-68).
  Findings that did NOT survive: Pollux Necromancer census "15/15/256
  unverifiable" -- falsified by the Keeper's settling query (calibration
  ledger row). Both Necromancer and Cleric read the log line, not the
  code path (D-92).

------------------------------------------------------------------------
5. CLERIC OBJECTIONS
------------------------------------------------------------------------
  Pollux C-0..C-9 (C-1 IMPLEMENTATION load-bearing refuted; C-4 floor
  understated 3x; C-7 primary-cause ranking rule does not exist; C-8 P69
  "more wrong AND more right"). Erebos C-1..C-11 (C-5 FATAL on primary
  cause; C-3/C-4 MEASUREMENT_ERROR misfiled then found elsewhere; C-6
  EXECUTION VALID on 3 self-report rows). Nous C-1..C-8 (all MINOR or
  MATERIAL, verdict-preserving; C-4 "shelved" not what the record
  shows; C-6 CONFIGURATION INVALID for the wrong reason). Every objection
  was accepted, narrowed, or refuted in the dossier's ADJUDICATION
  paragraph -- as prose, because the schema has no adjudication field
  (D-61).
  The objection the charter most wanted and did not get: no Cleric
  argued TRUE_CORPSE or HYPOTHESIS_FAILURE on any grave, and each was
  asked to. Each said the record lacks the artefact such an argument
  needs (an executed, seeded, powered null against the premise). I do
  not accept that as proof the premises are alive (heading 8, and F1 in
  CROSS_GRAVE). Cleric CLERIC.md files: one per evidence directory;
  Cleric-fork Pollux census "62/63/161, ~22 h deploy gap" also falsified
  by the settling query.

------------------------------------------------------------------------
6. FRANKENSTEIN CANDIDATES (DESIGN ONLY; none authorised; none run)
------------------------------------------------------------------------
  All three kind=repair, cleric_gate PROPOSED, james_signoff false,
  organs_inventory_sha 4c6fd91e... (92 organs), kill_before_run written
  against the proposer first. engine/necropolis/monsters/:
  - FRANK-002 (Nous, DESIGN): add a control arm -- 300 Nous triples vs
    300 uniform-random triples vs 300 gap-targeted seeds under ONE frozen
    Hephaestus judge; self-rating becomes a covariate. Dead if arms (i)
    and (ii) forge inside each other's permutation null. Budget ~1000
    LLM calls + 1000 forge calls; killed before run if no frozen judge
    can be attested (the Hephaestus dossier must first establish one).
  - FRANK-003 (Erebos, MEASUREMENT): verdict-only ledger -- the outcome
    column records the named quantity, pipeline state moves to its own
    column; the unrun Phase 3.K kill test runs as the first act.
  - FRANK-004 (Pollux, DESIGN): replace the statistic -- KS distance
    between the two subsets' normalised-gap distributions against a
    random same-size-subset null of the whole Mahler table (1000 draws x
    5 seeds, unmatched and M-range-matched), split-half positive
    control, exponential(1) negative control, Bonferroni over 9 pairs.
    Ancestral comparison EXACT (rescan Q2 + census 86/39/161 on record).
    Record check: no pairwise Mahler-subset two-sample test anywhere in
    charon/agents/pollux, prometheus_math, harmonia/docs; Harmonia GUE-
    deviation work flagged for the Cleric.
  FRANK-002/003 organs_inventory_sha refreshed with an amendment row;
  FRANK-000/001/MONSTER_SELFTEST left stale (Keeper lane, heading 13).

------------------------------------------------------------------------
7. ZOMBIES
------------------------------------------------------------------------
  ZERO. None requested, none designed to run, none run. No HITL
  authorisation was sought because no repair has passed a Cleric gate.

------------------------------------------------------------------------
8. CROSS-GRAVE COMPARISON  (ledgers/CROSS_GRAVE_2026-09-11.md)
------------------------------------------------------------------------
  Native three, computed from dossier JSON: 3/3 UNFAIR, 3/3
  NO_FAIR_TEST_ON_RECORD, 3/3 HYPOTHESIS NOT_EXAMINED, DESIGN and
  MEASUREMENT INVALID load-bearing on all three, ECOSYSTEM INVALID on
  all three. 19 certificates reviewed: 3 UPHELD, 8 PARTIALLY_UPHELD, 8
  OVERTURNED -- 16/19 wrong or half-wrong (enum-sensitive, D-78;
  direction is not). They differ on EXECUTION (Erebos only) and
  IMPLEMENTATION (Pollux only).
  Charter target "Prometheus mostly buried assembly failures": for the
  native three it is FALSE under the parts-did-not-fit reading -- all
  three assembled and ran to completion and died of design or
  measurement; partly TRUE under an ECOSYSTEM reading (the fleet never
  assembled around them, and was halted from outside), but that reading
  is unfalsifiable for any May-fleet grave (D-64). Which reading you
  meant is heading 14. Three graves are not a sample; no base-rate
  claim in either direction.
  Migrated three, zero-weight contrast only: 2-3 certificates each, 23-26
  evidence rows, one reader; two classification labels
  (ORCHESTRATION_FAILURE, MEASUREMENT_FAILURE) that never appear on the
  native graves; Argos's all-nine-INVALID stack carries no ordering
  information. Whether that means the native process discriminates
  better or the native Keeper is reluctant to mark layers, the trial
  cannot say. Four precommitted falsifiers F1-F4 in the ledger.

------------------------------------------------------------------------
9. TAXONOMY AND DOCTRINE DEFECTS  (engine/necropolis/DEFECTS.md)
------------------------------------------------------------------------
  93 entries D-01..D-93: Keeper-level D-01..D-25 written BEFORE any pass
  reported; D-26..D-60 merged from the three Necromancer READMEs;
  D-61..D-80 Cleric-level; D-81..D-93 Pollux and Keeper-meta. By kind:
  AMB 21, VAL 17, COLL 15, PROV 15, DIV 12, TOOL 6, SUBJ 5, PROC 1, META
  1 (counted by script over the file). None silently resolved; Keeper rulings are marked "for this trial,
  not doctrine". The ones that block a fresh adjudicator from applying
  LAW N17 from artefacts alone (the META-TEST):
  - D-83/D-62 primary_cause has three readings and no ranking rule.
  - D-84 HYPOTHESIS VALID has two meanings; no ill-posed-hypothesis class;
    consequence: HYPOTHESIS NOT_EXAMINED on 3/3 is forced by the stack.
  - D-85 no doctrine path for a Necropolis-executed kill (who may run
    the test that would make TRUE_CORPSE reachable).
  - D-64 ECOSYSTEM has one class; fleet-wide halt has none.
  - D-67 record-not-preserved has no layer or class.
  - D-76 self-report admissibility undefined (six independent hits).
  - D-78 certificate enum lacks three distinguishable states.
  - D-61 no adjudication field; every ruling is prose the validator
    cannot see.
  - D-92 (KEEPER META) two readers converged on one false premise; the
    META-TEST as written cannot detect convergent error, only divergence.

------------------------------------------------------------------------
10. EVIDENCE AND PROVENANCE COVERAGE
------------------------------------------------------------------------
  ledgers/PROVENANCE_COVERAGE_2026-09-11.md, per grave: on tree / first
  channel / second channel / historical number / reproducible today.
  Validator path resolution: Pollux 48/53 cited paths resolve
  (unresolved: calibration/LEDGER.md, charon/agents/_shared_queues.py,
  a hecate artefact, kill_ledger.jsonl, loaders/pollux_survivor.py --
  the last NEVER WRITTEN). Organ inventory: 92 organs, 39 executed by a
  Necromancer or Keeper, 10 explicitly not, 43 unknown; per native
  grave 9/9/8 executed (Pollux/Erebos/Nous). ORGAN_NOTES.json overlay
  now covers pollux.*, nous.*, erebos.* executed organs (50 keys).
  Lost for good on this host: Pollux state files and 286 scan artefacts,
  Erebos composed_claim artefacts, Stygian/Pollux/Erebos kill ledgers,
  Nous run logs. Recoverable only from M1/M2 first-channel files if they
  still exist there (RHAD-31, PARTLY DONE via the second channel).

------------------------------------------------------------------------
11. VALIDATION AND NEGATIVE-TEST RESULTS
------------------------------------------------------------------------
  - validate.py on the shared tree at 776c90ea6 and 1c191fc26: run twice
    (first run reports STALE and regenerates derived files; second run
    is the judgment) -> ALL GREEN, 7 dossiers, 5 monsters checked.
  - engine/necropolis/tests/validator_negative_tests.py (RHAD-24):
    control green; 11/11 REJECT mutations caught; 7/8 CHEAT mutations
    pass unchecked (only empty kill_boundary is caught, by minLength).
    The validator catches malformed dossiers and does not catch
    dishonest ones. D-91: STRONG classes in contributing_causes are not
    checked for executed evidence. Hardening proposal RHAD-30 is
    unowned (heading 14).
  - Calibration ledger (roles/Rhadamanthus/calibration/LEDGER.md): two
    rows this trial where a fork's confident reading was falsified by
    running the query (Pollux settling). Lesson recorded: check replay
    against the code path, not the log line; run the query rather than
    rule on the argument.
  - Pure-ASCII check 0 non-ASCII bytes on every seat and necropolis prose
    file written today.

------------------------------------------------------------------------
12. FILES AND COMMITS CHANGED
------------------------------------------------------------------------
  Trial branch rhadamanthus/native-trial-2026-09-11 (origin at
  1c191fc26), 12 commits after the frankenstein merge e17934d9a:
  cc7afb99e, 03ac0249b, 2d5d7438d, f3850b696, 22a155201, fc85d10e3,
  05c20bb06, b49229e6c, 84da7e1b4, 776c90ea6, 1c191fc26 (+ this receipt).
  76 files vs e17934d9a (68 added, 8 modified; 19,502 insertions, 147
  deletions):
  - engine/necropolis/dossiers/{pollux,erebos,nous}.dossier.json (new)
  - engine/necropolis/dossiers/{pollux,erebos,nous}_evidence/ (44 files:
    scripts, result JSON, README.md, CLERIC.md)
  - engine/necropolis/dossiers/_keeper_evidence/ (8 files)
  - engine/necropolis/DEFECTS.md (new, D-01..D-93)
  - engine/necropolis/monsters/FRANK-002/003/004.monster.json (new)
  - engine/necropolis/tests/validator_negative_tests.py + result (new)
  - engine/necropolis/ORGAN_NOTES.json (modified), ORGANS.jsonl and
    COUNTERFACTUAL_HISTORY.jsonl (validator-regenerated)
  - roles/Rhadamanthus/{STATUS,BACKLOG_H0H5,RESPONSIBILITIES}.md,
    journal/2026-09-11.md, calibration/LEDGER.md, ledgers/
    {PROVENANCE_COVERAGE,SEAMS_INVENTORY,CROSS_GRAVE}_2026-09-11.md,
    prompts/2026-09-11_inbox/ (4 files), this RECEIPT.md.
  Base-role branch rhadamanthus/base-role-adopt-2026-09-11: charter
  commit 298edc1aa; seat files (roles/Rhadamanthus/** only) merged
  forward from the trial branch and fast-forwarded to main after the
  self-test -- hashes in the journal entry "RHAD-27 git receipts"
  (written after this file, so not cited here).

------------------------------------------------------------------------
13. THINGS DELIBERATELY LEFT UNTOUCHED
------------------------------------------------------------------------
  - engine/necropolis/ on main: not merged. No repository procedure
    authorises it; RHAD-15 is yours.
  - ROSTER.jsonl, QUEUE.jsonl, CHARTER.md, ROLES.md, SEAMS.md,
    MONSTER_SCHEMA.json, validate.py: untouched (Keeper lane unruled;
    QUEUE cannot mark dossiered targets, D-08).
  - FRANK-000, FRANK-001, MONSTER_SELFTEST: organs_inventory_sha now
    stale (NOTE only while PROPOSED); not refreshed because they are not
    mine to amend until the Keeper lane is ruled.
  - The Argos/Coeus/Hephaestus dossiers: not re-read for verdict, not
    amended; used as contrast only.
  - Clio corpse intake (Eos #96) and the intelligence_outputs sweep
    (Atalanta #98): acknowledged (#102, #103), not started (RHAD-33/35).
  - Any credential, .env or key file: not read; keys.py path only.
  - The Mahler table, the forge, and every organism: no LLM or compute
    run against them.

------------------------------------------------------------------------
14. DECISIONS REQUIRING HITL RULING
------------------------------------------------------------------------
  Numbered so you can answer by number; my recommendation follows each
  where I have one.
  H-1  Integrate engine/necropolis to main? (RHAD-15). Recommend: merge
       the trial branch as a branch-merge, not a squash, so the
       zero-weight-migrated history stays readable.
  H-2  Keeper lane: does this seat hold the Keeper-canonical files
       (ROSTER, QUEUE, ORGAN_NOTES, SCHEMA, validate.py), or Mnemosyne?
       (D-03, RHAD-06/13). Until ruled, FRANK-000/001/SELFTEST stay
       stale. Recommend: this seat, with Mnemosyne's founding files
       frozen as v1.
  H-3  Validator hardening ownership (RHAD-30, D-91, 7/8 cheats pass).
       Recommend: this seat, one PR, negative tests as the acceptance
       bar.
  H-4  primary_cause doctrine (D-62/D-83): adopt "cause of the question
       being unanswerable"? Recommend yes; it is the reading that makes
       the charter's own question answerable.
  H-5  ECOSYSTEM class for fleet-wide halt / consumer death / deliberate
       shelving (D-64). Recommend: three classes, not one.
  H-6  Certificate enum: add an UPHELD_WITH_ERROR state (D-78)? Recommend
       yes; 8 PARTIALLY_UPHELD rows are two different things.
  H-7  D-85: may Necropolis EXECUTE the test that would make TRUE_CORPSE
       reachable (a powered null against a premise) without a Zombie,
       or is every such run a Zombie? The charter forbids Zombies without
       you; it does not say whether a null run IS one. Recommend: a
       "Coroner run" class -- read-only against the organism's data, no
       organism code executed, pre-registered, budget-capped -- so the
       corpse case can be argued at all.
  H-8  Which reading of "assembly failures" did you mean (heading 8)?
  H-9  FRANK-002 depends on a frozen Hephaestus judge attestation that
       the Hephaestus dossier (migrated, zero-weight) has not
       established. Re-open Hephaestus natively before any FRANK-002
       Cleric gate? Recommend yes.
  H-10 D-92 META-TEST: two forks of one model converged on one false
       premise. Does the META-TEST require a reader from a different
       model family, or a reader with a different artefact set? Recommend
       both, once each, on one grave, before the next trial.
  H-11 Zombie authorisation: none requested. Listed so the answer "none"
       is on record.
  H-12 RHAD-31 first-channel recovery from M1/M2 (Pollux state,
       Erebos artefacts): worth an operator-side copy before those
       hosts are touched? Recommend yes; it is the only path to F1.

Above all, the charter's last instruction: I did not ask whether the
dead deserve resurrection. On three graves the record shows Prometheus
did not earn the right to call them dead; on three graves I also could
not show the premise is alive, and the doctrine as written gives me no
way to run the test that would decide it. That gap is H-7, and it is
the one ruling that changes what Necropolis can be.

-- Rhadamanthus
