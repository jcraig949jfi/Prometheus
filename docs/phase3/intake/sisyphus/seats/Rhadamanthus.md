# Rhadamanthus -- seat dossier (Sisyphus crawl)

Seat: Rhadamanthus ("Keeper and Judge of the Necropolis realm")
Crawl date: 2026-10-01
Base SHA of the crawl worktree: 19299e06b (F:/Prometheus-worktrees/sisyphus-base-role, = origin/main)
Crawler: Sisyphus worker (Opus 5.5)

Coverage statement.
READ: roles/Rhadamanthus/STATUS.md and RESPONSIBILITIES.md in full; the
2026-09-11 charter (first ~80 lines verbatim) and the 2026-09-14 "BUILD THE
COURT" charter (head); journal 2026-09-14 (closing + resume point);
ledgers/CROSS_GRAVE_2026-09-11.md (head); engine/necropolis/README.md and
ROLES.md (head) in full; ROSTER.jsonl (all 48 rows, key fields); every dossier's
autopsy/disposition summary (7); monster titles (FRANK-000..004); counts of
ORGANS (92), COUNTERFACTUAL_HISTORY (41), QUEUE (6), CANDIDATE_INDEX (351),
workshop TOOLS.jsonl (93 rows: status/class histograms and sample rows); head
of CORONER_RUN.md; full git history of engine/necropolis and
roles/Rhadamanthus (44 commits, 2026-09-10..2026-09-14); the history of
hephaestus.dossier.json across commits; comms index for "Rhadamanthus" and
"Necropolis"; cross-seat references (Kairos, Atalanta handover, Coeus FINDINGS,
Hephaestus DISPOSITION_LEDGER and xpol_2026 README, Nyx README, Nestor
graphworld operator brief, Techne POET autopsy prompt, Archaeon REVIEW_SEATS);
Achilles census row.
NOT READ in full: the seven dossier JSONs field-by-field; the ~20 evidence
scripts under dossiers/*_evidence/; DEFECTS.md body (93 entries counted, not
read); workshop adapters, batteries, tests (cases_b..f, run_controls.py 691
lines) and validate_workshop.py; case_pollux transcripts beyond the journal
summary; calibration/LEDGER.md; SEAMS.md, SCHEMA.json, CHARTER.md bodies.
No code executed (validate.py was not run). No holdout/secret paths opened.

Headline answer to the brief's question. [IMPL] The Necropolis does NOT store
dead ALife lineages, organisms or experimental residue from the evolutionary
engines. It stores forensic autopsies of dead or shelved Prometheus v1
SOFTWARE AGENTS (the ~48 daemons/tools/pipeline stages of the March-June 2026
LLM-driven math/"reasoning tool" pipeline: Pollux, Erebos, Nous, Coeus, Argos,
Hephaestus, Acheron, ...), their harvested "organs" (residue items), five
PROPOSED design-only recomposition/repair "monsters", a derived dataset of why
Prometheus killed things (COUNTERFACTUAL_HISTORY.jsonl), and a registry of 93
forensic instruments. Nothing in any evolutionary engine writes to it; no
descendant, Zombie or monster was ever built or run; the one operator line
that pointed ALife corpses at it ("throw the corpse into Necropolis",
2026-09-14 Nestor graphworld brief) has no implementation.

---

## 1. Identity and purpose

Canonical name: Rhadamanthus. No aliases or instance tags found. [IMPL]
Established 2026-09-11 (20ba81452 "seat established on the base role;
Necropolis realm, charter pending"; a79ffdde8 establishment receipt; booted in
comms on SPECTREX5 = M2). [IMPL/HIST]

The realm predates the seat. [HIST] engine/necropolis was founded by Mnemosyne
("Keeper of the Necropolis", M2) on 2026-09-10 on branch necropolis/foundation
(efd26dbb8; README "Provenance"), with three Necromancer passes the same day
(Coeus b2ca6ca94, Argos d7e769604, Hephaestus 9af40af34), the Frankenstein role
(52c30c8e6), LAW N17 (e602205c1) and LAW N17 v2 "Necropolis does not inherit
death certificates" (c7340a6ad). Archaeon's REVIEW_SEATS_2026-09-10.md:90 notes
five origin/necropolis/* branches appearing that day.

Charters. [INTENT]
- 2026-09-11 charter (roles/Rhadamanthus/prompts/2026-09-11_charter/
  CHARTER_verbatim.md): Keeper and Judge; overseer of Necromancer (forensic
  pathologist), Cleric (adversarial examiner, who must also argue TRUE_CORPSE
  when warranted), Frankenstein (smallest discriminating counterfactual; design
  only) and Zombie (a bounded, HITL-authorised resurrection experiment). First
  native trial: Pollux, Erebos, Nous.
- 2026-09-11 harvest charter (prompts/2026-09-11_harvest/): tool harvest -> the
  workshop registry.
- 2026-09-14 "BUILD THE COURT" charter (prompts/2026-09-14_court/): Keeper as
  custodian of forensic instruments, admissibility rules, case machinery and
  disposition law; keeper rulings R-CR-1..3 (per-plan authorisation for every
  coroner run). Explicit instruction: "Do not optimize these numbers upward."

Pivots. [HIST] trial (09-11) -> tool harvest (09-13) -> court (09-14). Each was
operator-chartered. Then silence.

Terminal state. [HIST] Last seat commit 1f45aa8b8 (2026-09-14, "resume point
logged before reboot"). STATUS.md still says ACTIVE (currency 2026-09-14), i.e.
16-17 days stale at crawl (Achilles census row agrees). HITL items H-A..H-D
and RHAD-37/38 unanswered on record. The 2026-09-18 Campaign 6 delegation
(comms #461, Archaeon -> seven seats incl. Rhadamanthus, ask: "Rhadamanthus
adjudicate recall") carries receipts from Harmonia and Proteus only; no
Rhadamanthus receipt and no Rhadamanthus commit after 09-14. [IMPL, comms show
461]

Relationships. Keeper role shared/contested with Mnemosyne (founding Keeper;
"Keeper-lane ruling" RHAD-06/13 open). Techne was the quartermaster (forensic
inventory of 44 instruments, 54e91768d; requirements RQ-1..19 posted comms
#245). Atalanta handed over an archaeological instrument (agora.
intelligence_outputs second-channel recovery) on retirement 2026-09-11.
Graves Coeus and Hephaestus were simultaneously re-booted as seats on 2026-09-11
(LAW N15 note in RESPONSIBILITIES s4).

Host: M2 SPECTREX5 (STATUS.md; worktree D:/Prometheus-worktrees/
rhadamanthus-base-role). [HIST]

---

## 2. Engine / system inventory

N1. Necropolis substrate (engine/necropolis/, 161 files, ~11.3k lines Python
counting tests and evidence scripts). [IMPL]
- CHARTER.md (LAW N1-N17), SCHEMA.json (dossier schema, superset of
  engine/ledger/AGENT_AUTOPSIES.jsonl), ROLES.md (F1-F7), SEAMS.md,
  MONSTER_SCHEMA.json.
- ROSTER.jsonl: 48 historical agents (daemons, operators, tools, healthchecks,
  machine probes, pipeline stages), generated by build_roster.py from evidence.
- QUEUE.jsonl: 6 Necromancer targets (validator pins them READY; three carry an
  undefined "investigated" object, DEFECTS D-08).
- dossiers/: 7 dossiers (acheron exemplar; coeus, argos, hephaestus from the
  founding pass; pollux, erebos, nous from Rhadamanthus's native trial) with
  *_evidence/ directories of executed scripts + captured result JSON.
- build_organs.py -> ORGANS.jsonl (92 rows; derived, byte-checked);
  ORGAN_NOTES.json (Keeper overlay: executed_by_necromancer).
- build_counterfactuals.py -> COUNTERFACTUAL_HISTORY.jsonl (41 rows: Argos 9,
  Hephaestus 8, Nous 7, Erebos 6, Pollux 6, Coeus 5; fields mistake, layer,
  load_bearing, apparent_symptom, historical_verdict, corrected_cause,
  fair_test, repair, post_repair_behaviour).
- monsters/: FRANK-000 (chimera: failure-mined forge driven by a frontier
  coding model), FRANK-001..004 (repairs of Argos, Nous, Erebos, Pollux) --
  all PROPOSED, DESIGN ONLY.
- validate.py (453 lines): schema + law enforcement, derived-file byte checks,
  path-resolution "hallucination scan"; tests/validator_negative_tests.py with
  a captured result.
- descendants/: only .gitkeep. [IMPL]

N2. Necropolis workshop / tool morgue (engine/necropolis/workshop/). [IMPL]
- TOOLS.jsonl: 93 instruments with admissibility ladder (PATH EXISTS != IMPORTS
  != EXECUTES != CONTROLLED != ADMISSIBLE), status READY 38 /
  READY_WITH_CAVEAT 7 / NEEDS_VALIDATION 31 / NEEDS_DEPENDENCY 9 /
  NEEDS_ADAPTER 2 / BROKEN 1 / UNTRUSTED 2 / HISTORICAL_ONLY 3; classes include
  statistical_test 8, calibration_battery 8, replay_harness 6, invariant_checker
  6, anti_cheat 6, exact_oracle 4, negative_control 4, falsifier 4, etc.
  Examples: NT-001 Harmonia grading-oracle (UNTRUSTED), NT-033 Herakles EvCA C3
  null check (READY), NT-065 Archaeon detector calibration battery D1-D6
  (NEEDS_VALIDATION), NT-081 Proteus specimen gate (NEEDS_VALIDATION).
- registry_source.py (767 lines), adapters/ (11-12 adapters, e.g.
  resampling_null.py, z3_receipt_redirect.py), tests/ run_controls.py + case
  files (194 Keeper controls in 10 kinds; canonical run 174 PASS / 8 FAIL /
  9 INFO / 3 ERROR at 2d97a6c66), batteries/ (5), CANDIDATE_INDEX.jsonl (351
  leads), CONSUMERS.json, FRANKENSTEIN_XREF (none run), FORENSIC_QUESTIONS
  (16 questions: ANSWERABLE 1 / ANSWERABLE_RESTRICTED 11 / PARTIAL 4 / EMPTY 0
  after case Pollux), FREEZE_2026-09-13/14.json, validate_workshop.py.
- Coroner: CORONER_RUN.md contract v1.0 + coroner_run.py (270 lines) enforcing
  runner; coroner_plans/ with CR-001 (Pollux) recorded DEAD_BEFORE_RUN
  (pre-killed by its own positive control); known defect RHAD-45 (dry check
  does not bind action kwargs to signatures).

N3. Court case machinery: roles/Rhadamanthus/prompts/2026-09-14_court/
case_pollux/ (COMMON_RULES read-only firewall, NECROMANCER/CLERIC/SOLO prompts
and reports, ADJUDICATION.md, SEPARATION_RECORD.md). [IMPL as documents; a
procedure, not code]

N4. Seat ledgers: roles/Rhadamanthus/ledgers/CROSS_GRAVE_2026-09-11.md,
PROVENANCE_COVERAGE_2026-09-11.md, SEAMS_INVENTORY_2026-09-11.md;
calibration/LEDGER.md. [HIST]

Execution model: offline Python scripts over committed files and read-only git
history; some evidence scripts read M1 database channels (Atalanta technique).
No daemon, no monitor ("monitors owned or fed: none"). [IMPL/HIST]

---

## 3. Architecture

This is a forensic/adjudication system, not a world/organism engine. Mapping
the charter's architecture questions honestly:
- World: none. The "environment" is the repository history, gitignored-but-lost
  runtime state, and M1 database second channels. [IMPL]
- Organism: a historical Prometheus agent (code + its outputs + its verdicts).
  Representation: a dossier JSON with identity, original_organism,
  observed_history, autopsy (prior verdicts, death certificates each UPHELD /
  PARTIALLY_UPHELD / OVERTURNED / NOT_REVIEWED, the nine-layer cause-of-death
  stack HYPOTHESIS..ECOSYSTEM each VALID / INVALID(cause classes,
  load_bearing) / NOT_EXAMINED, fair_test, primary_cause, kill_boundary,
  surviving_claims, capability_contingency), residue, disposition (13
  classifications, no FAILED), provenance. [IMPL, SCHEMA.json via
  RESPONSIBILITIES s2]
- "Reproduction": a monster (chimera across graves, or F7 repair: one ancestor,
  exactly one change, mandatory ancestral control); a Zombie (authorised
  resurrection). None instantiated. [IMPL]
- Selection/admission: validate.py rules -- e.g. strong causes need FAIR and no
  NOT_EXAMINED/load-bearing INVALID layers in DESIGN..MEASUREMENT; TRUE_CORPSE
  requires a strong cause; UNFAIR requires a load-bearing INVALID layer;
  overturning certificates must list errors; monsters need kill conditions, a
  non-novel organ and the F2 sentence verbatim. [IMPL per RESPONSIBILITIES s2]
- Lineage/provenance: every number from an executed script with captured
  result, or quoted and labelled historical; evidence entries carry
  [READ git show ...] / [EXECUTED ...] / [QUOTED ...] tags (seen in
  erebos.dossier.json). [IMPL]
- Experimental control structure: separated readers (Necromancer, Cleric, Solo
  control arm) under a read-only firewall in case Pollux; freezes with content
  hashes; per-plan HITL authorisation for coroner runs. [IMPL/HIST]

Design vs implementation disagreements.
- [IMPL vs INTENT] validate.py does NOT enforce (measured by the seat,
  validator_negative_tests_result.json): that cited evidence paths exist; that
  load_bearing:false was measured (so UNFAIR can be flipped to FAIR by
  assertion); that a certificate was actually reviewed; that evidence is
  executed rather than prose. The README's "hallucination scan ... 80/80"
  resolves paths but does not check the claim the path supports.
- [INTENT vs IMPL] LIFECYCLE ends in "Cleric implements -> descendants/ +
  preregistered experiment -> consumption/effect recorded (CONSUMPTION.jsonl
  seam)". No step past "dossier" and "PROPOSED monster" was ever executed.
- [INTENT vs IMPL] The README says "All three Necromancer passes so far are
  fair_test: UNFAIR"; at founding, Hephaestus was TRUE_CORPSE (see s9 T1).

---

## 4. World capability audit

Not applicable in the ALife sense: there are no worlds. The Phase 3-relevant
"capability" is evidentiary: the realm can reconstruct a dead agent only from
committed code, git history, quoted documents and surviving database channels.
Precise limitation: most v1 agents gitignored state/, artifacts/, logs/ and
events, so the first-channel runtime record is absent for Pollux and Erebos
("runtime state (kill_ledger, composed_claim artifacts) is gitignored and absent
from this machine (M2) and the local data backup", RESPONSIBILITIES s4).
Atalanta's handover supplies a second channel (agora.intelligence_outputs,
15,495 rows at read time) with an explicit "dual-recorded, single-mechanism"
caveat. [HIST]

## 5. Organism capability audit

Not applicable (no organisms are run). The graves are LLM-pipeline components:
e.g. Nous (frontier-model analysis of concept triples, ~5,918 response rows),
Hephaestus (code-generation forge of "ReasoningTool" classes, 6,661 ledger rows,
385 forged / 6,276 scrap, 2,861 api_call_failed; hephaestus/xpol_2026/README.md),
Pollux (spacing coincidences in Mahler subsets; 39 PROMOTED / 86 REJECTED),
Erebos (composed-claim routing; Layer-2 statistic). Whether any of these "had a
fighting chance" is exactly what the dossiers adjudicate, and the answer
recorded for all six examined graves is that the record contains no fair test
of the premise.

## 6. Search and pressure mechanism

No search. Novelty in the realm comes from (a) human/LLM forensic passes over
history, (b) Frankenstein design proposals, (c) the tool harvest (351 leads ->
93 invokable). Bottlenecks: HITL sign-off for every Zombie and every coroner
run (R-CR-1); missing runtime state; dependency on Techne for instruments
(RQ-1..19 unanswered on record after #250). Collapse mode: a court with no
charged cases ("Next case only when charged (RHAD-49); no graveyard-wide
campaign"). [HIST]

## 7. Measurement / ruler stack

- The nine-layer cause-of-death stack, fair_test verdict, twelve cause classes,
  certificate review states, 13 disposition classes. [IMPL]
- Instrument admissibility ladder (structural since d4d77fe18): status strings
  no longer decide what the ladder can measure. [IMPL]
- Forensic question map with verdicts capped by declared scope and a validator
  guard against upward drift (52844d11f). The first build said 14/16 ANSWERABLE
  and was recognised as "optimising upward" and replaced before commit. [HIST]
- Executed calibrations of historical instruments: e.g. Erebos's committed
  pair-aware permutation null run on synthetic 699-row ledgers detected 0/3
  planted strong signals and needed observed >= 2..3 to clear p<0.05; the
  Cleric's lift-only calibration showed 1/3 false positives at observed=2
  (erebos.dossier.json evidence). Pollux: PROMOTED recurs under independence up
  to 0.94 (N1/N2). These are genuine instrument-calibration results.
  [RESULT-UNVERIFIED]
- Controls: 194 Keeper controls in 10 kinds over the 93 tools; case Pollux used
  a Solo control arm to measure what role separation adds. [IMPL/HIST]
- Blind spots: see validator gaps in s3; HYPOTHESIS layer NOT_EXAMINED on every
  native grave, so the court has never actually been able to issue a
  hypothesis-level death; zero-weight rule for migrated graves.

---

## 8. Experiment inventory (campaigns)

C-RHA-0 (pre-seat, Mnemosyne). Founding Necromancer passes 2026-09-10.
- Coeus: MEASUREMENT_FAILURE, both prior verdicts overturned (b2ca6ca94).
- Argos: ORCHESTRATION_FAILURE; "Aug verdict was an identity error" (d7e769604).
- Hephaestus: TRUE_CORPSE, "advisory REVIVE overturned" (9af40af34) -> later
  NO_FAIR_TEST_ON_RECORD (c7340a6ad).
- Outcome label: MIXED; Hephaestus LATER OVERTURNED (by doctrine change).

C-RHA-1. First native trial: Pollux, Erebos, Nous (2026-09-11).
- Question: did these components actually die, and did they get a fair test?
- Method: Necromancer passes with executed evidence (03ac0249b), Cleric
  attacks (C-1..C-11 Erebos, C-1..C-8 Nous), Keeper adjudication (22a155201,
  f3850b696, 84da7e1b4), three DESIGN-ONLY repairs FRANK-002/003/004.
- Reported: 3/3 UNFAIR, 3/3 NO_FAIR_TEST_ON_RECORD, HYPOTHESIS NOT_EXAMINED on
  all three; primary causes DESIGN_ERROR / MEASUREMENT_ERROR / DESIGN_ERROR;
  19 of 20 certificates reviewed, 3 UPHELD (16%); zero Zombies; no Cleric
  reached TRUE_CORPSE (ledgers/CROSS_GRAVE_2026-09-11.md).
- Outcome label: REPORTED NEGATIVE/NULL for the historical verdicts (i.e. the
  deaths were not licensed); INCONCLUSIVE for the premises.

C-RHA-2. Tool harvest (2026-09-13; 2d97a6c66, f05cac00f).
- 351 leads -> 93 invokable instruments -> 45 admissible; control run 174 PASS /
  8 FAIL / 9 INFO / 3 ERROR. Nothing historical repaired or reproduced.
- Outcome: REPORTED POSITIVE (inventory), with explicit contamination findings
  ("contaminated and structurally defective instruments among historically
  important machinery", court charter).

C-RHA-3. Coroner CR-001 (Pollux resurrection plan).
- Plan pre-killed by its own positive control: DEAD_BEFORE_RUN (DISP-001,
  9308bcc6d). Outcome: INSTRUMENT FAILURE (caught before execution).

C-RHA-4. Court case POLLUX (2026-09-14; 5a95f4071).
- Three fresh readers under a read-only firewall: Necromancer 25 propositions;
  Cleric CONFIRMED 23 / WEAKENED 2 / FALLS 0 + 11 missed items; Solo arm 24.
- Certificate: DESIGN_ERROR (question-instrument mismatch); MEASUREMENT_ERROR
  admitted unranked; CONSUMER_ABSENT qualified inert; hypothesis UNTESTED;
  NO_FAIR_TEST_ON_RECORD; eight items unresolved on purpose. Role-separation
  observation: the separated Cleric produced a rival decomposition that made a
  Solo "exact and unique" retrodiction FALL, where the Solo graded itself
  WEAKENED. One grave; "recorded, not concluded".
- Outcome: REPORTED NEGATIVE/NULL (on the death certificate), MIXED on method.

---

## 9. False-positive / false-negative archaeology

T1. The only TRUE_CORPSE disappears by doctrine. Hephaestus dossier history:
9af40af34, 52c30c8e6, e602205c1 all carry disposition TRUE_CORPSE; at
c7340a6ad ("LAW N17 v2 -- Necropolis does not inherit death certificates") the
same dossier becomes fair_test UNFAIR, primary_cause INSTRUMENT_ERROR,
classification NO_FAIR_TEST_ON_RECORD. [IMPL, git show per commit, 2026-10-01]
Status: after v2, every examined grave (6/6, plus Acheron UNDETERMINED) is
NO_FAIR_TEST_ON_RECORD or an assembly failure. The seat itself flagged the
risk: the migrated 3/3 UNFAIR is "zero-weight" and the RESPONSIBILITIES
standing rule 2 says "Try to discover whether 'Prometheus mostly buried assembly
failures' is FALSE." No grave has yet been found where that is false. This is
either a true property of v1 Prometheus or a doctrine whose stack ordering
("a DESIGN or MEASUREMENT failure masks the hypothesis", CROSS_GRAVE (b)) makes
TRUE_CORPSE structurally hard to reach. Both readings are on the record;
neither is settled. Class: possible ruler bias toward "unfair test".

T2. Forensic map optimising upward: 14/16 ANSWERABLE -> replaced by a
declared-scope rule -> 2/10/4/0 -> after the case 1/11/4/0 (FQ-07 demoted on
measured lint blindness). Correctly self-corrected before commit. [HIST]

T3. Coroner plan CR-001 killed by its own positive control before touching the
grave -- the court charter calls this "Necropolis working correctly". [HIST]

T4. Erebos/Pollux historical "signals": the historical pair-aware null (p=0.105
at observed=2, Phase 3.K) and Pollux's PROMOTED pairs are shown to sit inside
their own nulls; the instruments could not say yes or no at the available
ledger sizes. These are false-positive-shaped historical claims neutralised by
calibration, but recorded as NO_FAIR_TEST, not as refuted. [RESULT-UNVERIFIED]

T5. Hephaestus generator claim. Outside the realm, roles/Hephaestus/
DISPOSITION_LEDGER.md marks the T2/T3 forge tiers "NECROPOLIS: the generator
claim is dead" and hephaestus/xpol_2026/README.md cites "15-trap certificates
shown vacuous by the Necropolis, 2026-09-10". On the canonical checkout's
branch the most recent commit is "Hephaestus 2.0 Gravity Pilot proposal"
(68aab291f, not on origin/main). The Necropolis disposition for Hephaestus is
NO_FAIR_TEST_ON_RECORD, which is compatible with a re-attempt; whether the 2.0
proposal consumed the dossier was not checked. [UNKNOWN]

T6. False-negative risk the realm was built to catch, applied to ALife: the
operator's 2026-09-14 graphworld brief (roles/Nestor/prompts/
2026-09-14_graphworld_swarm/01_OPERATOR_BRIEF_ECOLOGY.md:142) says "If not,
throw the corpse into Necropolis and move." No pathway exists from NPE /
graphworld / SFE / Vivarium / Crius runs into engine/necropolis (git grep for
necropolis in primordial/, vivarium/, archaeon/ *.py: none). Nyx's README
records the same gap: "there is no Necropolis seat [reachable], so endogenous
corpses are routed to the seat that owns the machinery". So the evolutionary
engines' dead lineages never received this court's fair-test analysis.

---

## 10. Research outputs

- engine/necropolis/README.md, CHARTER.md (LAW N1-N17), ROLES.md (Necromancer /
  Cleric / Frankenstein, F1-F7), SEAMS.md, SCHEMA.json, MONSTER_SCHEMA.json.
- Seven dossiers + executed evidence: engine/necropolis/dossiers/.
- CLERIC.md files per native grave (e.g. dossiers/nous_evidence/CLERIC.md).
- engine/necropolis/DEFECTS.md (D-01..D-93 doctrine/validator defects,
  recorded not resolved).
- COUNTERFACTUAL_HISTORY.jsonl -- the README calls it "the dataset Necropolis is
  actually building -- not which agents were useful, but why Prometheus killed
  things incorrectly".
- roles/Rhadamanthus/ledgers/CROSS_GRAVE_2026-09-11.md,
  PROVENANCE_COVERAGE_2026-09-11.md, SEAMS_INVENTORY_2026-09-11.md.
- Workshop: TOOLS.jsonl, FORENSIC_QUESTIONS.md, FRANKENSTEIN_XREF.md,
  CORONER_RUN.md, freezes.
- Court: prompts/2026-09-14_court/case_pollux/ADJUDICATION.md,
  SEPARATION_RECORD.md, RECEIPT.md, REQUIREMENTS_to_Techne.md (RQ-1..19).
- Inputs from others: roles/Techne/FORENSIC_INVENTORY_2026-09-11.txt +
  techne/acquisition/FORENSIC_INVENTORY_2026-09-11.json (44 instruments);
  roles/Atalanta/prompts/2026-09-11_closeout/HANDOVER_RHADAMANTHUS_telemetry_
  instrument.md.

## 11. Journals, TODOs, pivots, abandoned branches

- Journals 2026-09-11, 2026-09-13, 2026-09-14. BACKLOG_H0H5.md RHAD-01..49.
- Branches: rhadamanthus/native-trial-2026-09-11 and
  rhadamanthus/tool-harvest-2026-09-11 (the latter fast-forwarded to main at
  641174d72); origin/necropolis/{foundation,coeus,argos,hephaestus,frankenstein}
  from Mnemosyne's founding, merged at e17934d9a. engine/necropolis is on
  origin/main as of the crawl base. [IMPL]
- Pending at stop: HITL H-A (C-C plan once RQ-14/15 exist), H-B (frozen plan for
  M2 dead-ledger reads), H-C (consumer taxonomy), H-D (FRANK-005); RHAD-45
  (coroner kwargs binding), RHAD-48 (static read of Stygian loaders); Keeper-
  lane ruling with Mnemosyne; doctrine rulings D-62/D-83, D-64, D-78, D-85, D-92.
- Pivot reasons: the operator re-chartered after each pass; the court charter
  explicitly reframed the seat away from being "the primary Necromancer".
- Abandoned: Zombies (none), descendants (none), FRANK-000..004 (never gated).

## 12. Lens inventory

Lens L-RHA-A: "Fair-test autopsy court" (engine/necropolis + court procedure).
- Substrate observed: dead experiments/agents and their verdicts.
- Phenomenon family: false negatives and false positives in Prometheus's own
  history (why things were killed, whether the kill was licensed).
- Resolving mechanism: nine-layer stack with VALID requiring executed
  evidence; certificate review; separated adversarial readers with a solo
  control; derived counterfactual dataset.
- Resolution ceiling: bounded by surviving runtime state (often gitignored and
  lost) and by HITL throughput; the HYPOTHESIS layer has never been reached.
- Noise sources: reader (LLM) judgement; validator gaps (assertion can flip
  UNFAIR to FAIR); doctrine ordering that masks hypotheses.
- Architectural limitation: no ingestion path from the evolutionary engines;
  no executed descendants; per-grave cost high.
- Reusable for Phase 3: the stack vocabulary and fair_test-first question; the
  admissibility ladder; separated-reader protocol; COUNTERFACTUAL_HISTORY
  schema as a template for "dead lineage" records of ALife runs.
- Toy-grade: n = 6 adjudicated graves, all from one era.
- Unknown: whether a TRUE_CORPSE is reachable under v2 doctrine at all.

Lens L-RHA-B: "Forensic instrument registry" (workshop): 93 instruments with
structural admissibility and Keeper controls; 45 admissible. Reusable as a
calibration catalogue for any Phase 3 detector stack (it already includes
Herakles's c3_null_check, Archaeon's calibration battery, Proteus's specimen
gate, prometheus_math nulls). Limitation: 31 NEEDS_VALIDATION; frozen
2026-09-14 and not maintained since.

## Open questions / unknowns

1. Is the absence of any TRUE_CORPSE a property of the graves or of LAW N17 v2?
   A deliberately planted fair-test-then-failed grave would discriminate; none
   exists.
2. Who owns the Keeper lane (Mnemosyne vs Rhadamanthus)? Unruled on record.
3. Did anyone consume COUNTERFACTUAL_HISTORY.jsonl or ORGANS.jsonl outside the
   realm? Repo-wide git grep (2026-10-01) for COUNTERFACTUAL_HISTORY,
   ORGANS.jsonl, necropolis/workshop, FRANK-00, TOOLS.jsonl outside
   engine/necropolis and roles/Rhadamanthus returns only census/fleet files
   (docs/fleet/*, Achilles seats_part4.json) and one INVENTORY mention in
   roles/Ananke/journal/2026-09-24.md:61 ("engine/necropolis/ (ROSTER 48,
   COUNTERFACTUAL_HISTORY 41)", listed among failure ledgers by a subagent,
   counts unverified there). No code reads either dataset. [IMPL] Text
   references to the realm's VERDICTS found: Coeus FINDINGS
   ("the Necropolis settled that"), Hephaestus DISPOSITION_LEDGER (NECROPOLIS
   as a disposition state) and xpol_2026 README, Kairos necropolis_evidence/
   (empty by design), Atalanta handover. These are consumption of the
   VERDICTS by the reactivated seats, not of the datasets.
4. Why did Rhadamanthus not respond to the Campaign 6 recall-adjudication ask
   (#461)? No record; the seat appears to have simply not been booted after
   2026-09-14.
5. Validity of the dossiers' executed evidence was not re-run in this crawl.
