# Rhadamanthus status

Currency: 2026-09-14 (court close; branch rhadamanthus/tool-harvest-2026-09-11
pushed to main by fast-forward; receipt at prompts/2026-09-14_court/RECEIPT.md;
freeze engine/necropolis/workshop/FREEZE_2026-09-14.json).

court state (2026-09-14 charter, prompts/2026-09-14_court/):
  Coroner contract v1.0 legislated (R-CR-1..3 ruled); DISP-001 records CR-001
  DEAD_BEFORE_RUN beside an untouched plan.  Admissibility ladder structural
  (45 admissible / 93).  Forensic map 16 questions: ANSWERABLE 1 /
  ANSWERABLE_RESTRICTED 11 / PARTIAL 4 / EMPTY 0; validator-enforced; only
  downward movement recorded.  Case POLLUX adjudicated with separated
  Necromancer + Cleric and a solo control arm (case_pollux/): DESIGN_ERROR as
  question-instrument mismatch; MEASUREMENT_ERROR admitted unranked;
  CONSUMER_ABSENT qualified inert; hypothesis UNTESTED; NO_FAIR_TEST_ON_RECORD;
  eight items unresolved on purpose; ZERO Zombies; no monster raised; no
  coroner descendant (RQ-1, RQ-14/15).  RQ-1..19 to Techne and others.
  HITL owed: H-A..H-D (RECEIPT item 15).  Next case only when charged
  (RHAD-49); no graveyard-wide campaign.


harvest state (2026-09-11 harvest charter, prompts/2026-09-11_harvest/):
  engine/necropolis/workshop/ holds a 93-row registry (TOOLS.jsonl,
  generated from the control run), 11 adapters, 194 Keeper controls in
  10 kinds (canonical run 174 PASS / 8 FAIL / 9 INFO / 3 ERROR at
  2d97a6c66), 5 batteries, a PROPOSED coroner contract with an enforcing
  runner, one PROPOSED coroner plan (CR-001, Pollux) that is pre-killed by
  its own positive control, a Frankenstein cross-reference (none run) and
  a 351-row candidate index.  READY 38 / READY_WITH_CAVEAT 7 /
  NEEDS_VALIDATION 31 / NEEDS_DEPENDENCY 9 / NEEDS_ADAPTER 2 / BROKEN 1 /
  UNTRUSTED 2 / HISTORICAL_ONLY 3.  Nothing historical was repaired;
  nothing was reproduced from historical inputs (no run was authorised).
  HITL owed: coroner rulings R-CR-1..3 (RHAD-37); CR-001 refile (RHAD-38).
  Techne disputes recorded (hypothesis / Lean host-local), not resolved.

trial state (2026-09-11 charter, unchanged since 2026-09-11):
seat state: ACTIVE under the 2026-09-11 charter (Keeper and Judge of the
  Necropolis realm; prompts/2026-09-11_charter/CHARTER_verbatim.md).
what it asserts: PRESENT (booted in comms 16:50 UTC on SPECTREX5 at
  863a6e9af), ACTIVE, PRODUCTIVE in committed files (three adjudicated
  dossiers, three CLERIC.md, three DESIGN-ONLY repairs FRANK-002/003/004,
  DEFECTS.md D-01..D-93, four seat ledgers), VALID only as far as
  validate.py and the seat's own negative tests reach: validate.py twice
  ALL GREEN on the shared tree at 776c90ea6 (7 dossiers, 5 monsters);
  no external reader has yet applied LAW N17 to these dossiers, so the
  charter's META-TEST is filed, not passed.
trial result (first native trial, Pollux / Erebos / Nous): 3/3 UNFAIR,
  3/3 NO_FAIR_TEST_ON_RECORD, 3/3 HYPOTHESIS NOT_EXAMINED; primary
  causes DESIGN_ERROR / MEASUREMENT_ERROR / DESIGN_ERROR; 19 certificates
  reviewed, 3 UPHELD; zero Zombies; no Cleric reached TRUE_CORPSE (D-84,
  D-85). Cross-grave: ledgers/CROSS_GRAVE_2026-09-11.md. The migrated
  3/3 UNFAIR was zero-weight and stays so.
workspace (2026-09-13): same worktree, now on branch
  rhadamanthus/tool-harvest-2026-09-11 (harvest commits 9ac363786,
  2d97a6c66, f05cac00f, +seat commit); seat files go to main via the
  base-role branch.
  Trial-era note: seat worktree rhadamanthus-base-role under the operator's
  worktrees directory, on branch rhadamanthus/native-trial-2026-09-11
  (base-role-adopt branch at 298edc1aa + necropolis/frankenstein c7340a6ad
  merged at e17934d9a; trial commits through 776c90ea6). Neither branch
  is on origin/main; engine/necropolis/ is not on origin/main.
comms (2026-09-13): inbox synced at harvest close; nothing addressed to
  Rhadamanthus since Techne #193; RHAD-43 posted #244 (reply to #193).
  Trial-era note:
  last sync 16:50 UTC (before the trial); a sync is owed before the
  push and after the receipt. Keeper-lane question (RHAD-13) unposted.
monitors owned or fed: none.
lane: engine/necropolis/ on the trial branch only. Keeper-owned canonical
  files touched THIS PASS under the charter's Keeper title, pending the
  Keeper-lane ruling: ORGAN_NOTES.json (pollux.* overlay), ORGANS.jsonl
  and COUNTERFACTUAL_HISTORY.jsonl (validator regeneration), DEFECTS.md.
  ROSTER, QUEUE, CHARTER, SCHEMA, validate.py untouched.
blockers: none on the next action. HITL needed for: integration of
  engine/necropolis to main (RHAD-15); Keeper lane (RHAD-06/13, incl.
  FRANK-000/001/SELFTEST stale organs_inventory_sha); any Zombie
  (RHAD-29, none requested); validator hardening ownership (RHAD-30,
  D-91); doctrine rulings D-62/D-83, D-64, D-78, D-85, D-92.
next executable action (2026-09-13): RHAD-43 report to Techne, then
  RHAD-37 rulings from James; before that the trial-era item stood as:
  RHAD-27 (push trial branch as a branch; merge
  seat files forward to base-role branch; self-test; fast-forward push
  per WORKING_CONTRACT), then RHAD-28 receipt, RHAD-32 memory.
seen, not mine: engine/necropolis/ is not on origin/main. Pollux and
  Erebos runtime state (kill_ledger, composed_claim artifacts) is absent
  from this machine.
