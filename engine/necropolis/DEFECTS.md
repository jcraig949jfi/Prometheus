# Necropolis doctrine and taxonomy defects ledger

Append-only. Opened 2026-09-11 by Rhadamanthus during the first native trial
(Pollux, Erebos, Nous), which doubled as the portability test the charter
names: can a fresh adjudicator apply LAW N17 from repository artifacts alone,
without oral tradition from the founding Keeper?

Each entry: what was hit, where, which way the reader went, and why. Nothing
here is resolved by this file. Resolution needs a ruling (HITL or the Keeper
lane once its ownership is settled, D-03 below) and a schema/validator change
committed with a test.

Classes: AMB (ambiguity in doctrine), SUBJ (decision that required subjective
interpretation), COLL (taxonomy collision), PROV (missing provenance), DIV
(two competent readers would reasonably differ), VAL (validator does not
enforce what the doctrine says), TOOL (machinery defect).

## Keeper-level entries (from reading the doctrine and running the validator)

D-01 VAL  validate.py docstring says "every repo path cited is resolved (the
     Cleric's hallucination scan)"; the code emits a NOTE, never an error.
     Measured: tests/validator_negative_tests_result.json case
     hallucinated_evidence_path -> PASSES_UNCHECKED. A dossier whose evidence
     is a path that does not exist validates ALL GREEN. Went: left as-is,
     reported. Reader divergence: a Cleric who trusts the docstring will not
     re-check paths.

D-02 VAL  load_bearing:false is accepted with any single evidence path and no
     check that a measurement exists. Because fair_test FAIR excludes only
     load-bearing INVALID layers, a Necromancer can flip UNFAIR to FAIR by
     assertion. Measured: case non_load_bearing_by_assertion_makes_FAIR ->
     PASSES_UNCHECKED. This is the most consequential gap: FAIR is the
     precondition for every strong claim.

D-03 AMB  Who is the Keeper? CHARTER/ROLES/SEAMS name Mnemosyne as Keeper
     (ORGAN_NOTES.json "Keeper-owned"; sign-off carriage). The 2026-09-11
     operator charter names Rhadamanthus "Keeper and Judge". Nothing in the
     repository reconciles the two. Went: this seat acts as Keeper for the
     trial's own files and touches no Keeper-owned canonical file (ROSTER,
     QUEUE, ORGAN_NOTES) until ruled. Needs HITL.

D-04 VAL  A classification other than NEEDS_MORE_EVIDENCE can be asserted with
     every layer NOT_EXAMINED (case all_NOT_EXAMINED_but_classified_
     REPRESENTATION_FAILURE -> PASSES_UNCHECKED). The charter's "the stack
     supports the primary cause" has no analogue for the classification.

D-05 VAL  LAW N5 says surviving_claims "may be empty only for a defended
     TRUE_CORPSE"; the validator accepts an empty list with any
     classification (case empty_surviving_claims_without_TRUE_CORPSE).

D-06 VAL  death_certificates may all be NOT_REVIEWED and still satisfy LAW
     N17 by the validator (case every_certificate_NOT_REVIEWED). The law says
     every verdict is "reviewed"; the schema says NOT_REVIEWED "is honest for
     a transcription". Both are right; nothing says how many may remain
     unreviewed before disposition.

D-07 VAL  "VALID needs executed evidence" is unenforceable at the schema
     level: evidence is a path list, and a prose README satisfies it (case
     all_evidence_is_prose_README). The executed/read distinction exists only
     for organs (ORGAN_NOTES.executed_by_necromancer), not for stack layers.

D-08 TOOL QUEUE.jsonl status is pinned to READY by validate.py ("founding
     pass dispatches nothing"); progress is carried instead by an optional
     "investigated" object (date, dossier, classification) on three rows.
     So the row's status says READY while its investigated field says done,
     and nothing in SCHEMA or validate.py defines "investigated". A reader
     who filters on status (as this Keeper first did) reads the queue as
     six undispatched targets. Went: first misread it that way; corrected
     on reading the full rows. Recorded because the misreading is the
     portability defect.

D-09 COLL "dossier" means two things: ROSTER.dossier_exists refers to the
     June pivot thoughtwork dossiers (pivot/COMPONENT_DOSSIERS_2026-06-24.md);
     Necropolis dossiers are engine/necropolis/dossiers/*.json. Pollux,
     Erebos and Nous all read dossier_exists:true while having no Necropolis
     dossier before today.

D-10 SUBJ QUEUE.jsonl why_selected / calibration_role pre-label the expected
     outcome ("likely TRUE_CORPSE", "mechanism-good / emission-bad",
     "PRODUCER_BLOCKED vs CONSUMER_BLOCKED"). The queue is itself a death
     certificate in disguise and is not in prior_verdicts by any rule. Went:
     treated as zero-weight; each Necromancer was told so explicitly.

D-11 PROV ROSTER.source_locations is empty for Pollux and Erebos although
     their code is on the tree (charon/agents/pollux/, charon/agents/erebos/).
     A reader starting from the roster cannot find the corpse.

D-12 PROV Runtime state that the historical verdicts counted (Pollux
     kill_ledger 286 rows; Erebos 234 composed_claim artifacts) is gitignored
     and absent from this machine (M2, where Charon ran) and from the local
     data backup. The August autopsies read something; where is unrecorded.

D-13 TOOL validate.py writes ORGANS.jsonl and COUNTERFACTUAL_HISTORY.jsonl in
     place when stale, and reports the regeneration as an error on that run.
     A validator with side effects cannot be run by parallel passes on one
     tree, and the first run after any dossier change is always RED. Went:
     each pass validated on a private copy; the Keeper ran the shared tree
     once at the end.

D-14 AMB  LAW N17's admissible-layer table puts IDENTITY_PROVENANCE_ERROR on
     INTERPRETATION only. A wrong artifact attributed at EXECUTION time (the
     run that was measured was not the run that was designed) has no layer
     that may carry it except INTERPRETATION, which reads as "the historical
     conclusion did not follow". Two readers will file it differently.

D-15 AMB  CAPABILITY_CEILING is admissible on DESIGN/IMPLEMENTATION/
     CONFIGURATION/EXECUTION but the classification CAPABILITY_BOUND requires
     it as primary_cause. Nothing says whether a ceiling that is also a
     DESIGN_ERROR (the design assumed a capability) is filed as one or both.

D-16 DIV  fair_test scope is optional. For organisms with eras (all three
     trial graves ran under changing upstream instruments), FAIR/UNFAIR
     without a scope is ambiguous, and the validator accepts the omission
     (case fair_test_without_scope).

D-17 COLL The AUTOPSY_TAXONOMY clusters that failure_classes SHOULD cite are
     mechanistic (DEAD-GATING, LOW-BITS-EMISSION, ...); the LAW N17 cause
     classes are epistemic (DESIGN_ERROR, MEASUREMENT_ERROR, ...); the 13
     classifications are archaeological (REPRESENTATION_FAILURE,
     CONSUMER_BLOCKED, ...). Three vocabularies describe one death and no
     mapping between them is written. Example: "LOW-BITS-EMISSION" can be a
     DESIGN_ERROR (no novelty gate), a MEASUREMENT_ERROR (rows counted as
     facts) or an INTERPRETATION_ERROR (volume read as coverage), and the
     classification could be REPRESENTATION_FAILURE or MEASUREMENT_FAILURE.

D-18 DIV  The charter's outcome list (eight statements) and the schema's
     thirteen classifications are different partitions. "Recoverable residue
     exists" and "a Frankenstein counterfactual is warranted" are not
     classifications; a grave can be NO_FAIR_TEST_ON_RECORD and also both.
     Went: adjudication records the charter outcome in the journal and the
     classification in the dossier; the mapping is the adjudicator's.

D-19 AMB  Which certificate is the "historical verdict"? For each trial grave
     there are at least three of different dates and authors (June disposition
     plan, June pivot dossier, August autopsy row) and they disagree (Pollux:
     REVIVE "real signal" in June, RETIRE / LOW-BITS in June-24 and August).
     N17 says review each; nothing says whether a later certificate that
     contradicts an earlier one is itself evidence about the earlier one.

D-20 PROV Nous has no AGENT_AUTOPSIES row (autopsy_exists:false) yet a
     historical_status of "shelved" and a machine "M4". The shelving has no
     author, date, or reason on the tree that the roster points to.

(Entries D-21 onward are appended from the three Necromancer READMEs and the
Cleric attacks, prefixed with the grave.)

## Keeper-level entries from the second-channel census (comms #98 instrument)

D-21 PROV ROSTER.jsonl gives Pollux and Erebos historical_status "active"
     and machine M2. agora.intelligence_outputs (M1 canonical store) shows
     their last rows on 2026-05-30 (dossiers/_keeper_evidence/
     intelligence_outputs_census_result.json). "active" is 104 days stale
     and nothing on the roster says when a status was last measured.

D-22 COLL The August AGENT_AUTOPSIES rows for Pollux (P69) and Erebos (P57)
     are dated 2026-08-21 and read as if describing a then-current
     organism; the runs they count are May 2026 (05-24..05-30 and
     05-26..05-30). A reader who takes the autopsy date as the run date
     mis-stacks EXECUTION under the August ecosystem. The roster carries no
     run window at all.

D-23 AMB  Fifteen May-fleet agents wrote their last row within 45 minutes
     on 2026-05-30 (fleet_halt_census_result.json). LAW N17's ECOSYSTEM
     layer exists, but nothing in the doctrine says how a shared halt is
     recorded once rather than in fifteen dossiers, or whether an organism
     that was running at the halt can be UPHELD as dead at EXECUTION at
     all. Went: recorded here and in each trial dossier's ECOSYSTEM layer
     as the same fact; the doctrine question stays open.

D-24 VAL  agora.agent_heartbeats says "online" for every one of those
     agents today. The instrument the fleet used for liveness is a write-
     only artifact (the LIVENESS-AS-ARTIFACT cluster in AUTOPSY_TAXONOMY
     names this for Hypatia). Any dossier that cites a heartbeat as
     evidence of EXECUTION is citing the organism's own claim. The schema
     has no field for "evidence is self-report".

D-25 DIV  Dual-recorded, single-mechanism (Atalanta #98). The Pollux 286
     matches across kill_ledger (August reading) and intelligence_outputs
     (today). One reader will write "verified"; the doctrine has no
     provenance grade between single-sourced and independently verified.

## Necromancer-level entries (merged by the Keeper from the three READMEs;
## grave-prefixed; wording condensed, substance unchanged; the READMEs are
## the primary record: dossiers/<grave>_evidence/README.md section 7)

D-26 POLLUX COLL A tautological statistic (a normalisation leg that returns
     a constant) is admissible as IMPLEMENTATION_ERROR (the line),
     INSTRUMENT_ERROR (the leg cannot observe) and DESIGN_ERROR (the
     contrast is defined around a constant). No ranking rule; the
     primary_cause and therefore NO_FAIR_TEST_ON_RECORD vs
     MEASUREMENT_FAILURE turn on the ranking. (Same shape as D-17.)

D-27 POLLUX AMB  EXECUTION VALID with all runtime state lost: the only
     execution evidence is a second channel written by the same process.
     The doctrine does not say whether single-mechanism dual recording
     satisfies "executed evidence". (Erebos D7/D15 and Nous 7 hit the same
     wall; see D-25.)

D-28 POLLUX SUBJ QUEUE/ROSTER pre-labels read as certificates; the
     charter's zero-weight instruction is not in the files. (Same as D-10;
     recorded again because a second reader hit it independently.)

D-29 POLLUX PROV P69's census is unverifiable: printed in-pass, ledger
     absent, Hecate figure cited to a path that does not exist. A
     certificate whose inputs are gone can be neither UPHELD nor
     OVERTURNED on its numbers; PARTIALLY_UPHELD is being used for "form
     reproduced, numbers unverifiable", a third state the enum lacks.

D-30 POLLUX TOOL validate.py's cited-path scan runs relative to its own
     directory; on a scratch copy every repo path is "unresolved" and the
     note is uninformative. (Erebos D16 and Nous 8 report the same; on the
     shared tree 43/49 Erebos and 37/37 Nous paths resolve.)

D-31 POLLUX VAL  SCHEMA requires premise_exclusion as an array; _TEMPLATE
     and the Coeus dossier omit it, so a fresh writer has no example of its
     shape (first validate run failed on type str).

D-32 POLLUX PROV Contradictory certificates coexist on the tree with no
     cross-reference: 06-23 REVIVE "real signal" and 06-24 RETIRE
     "tautology" 24 hours apart; 06-24 "ZERO Learner references" beside a
     Learner corpus that yielded 286 Pollux rows. Nothing links a later
     reading to the one it overturns. (Instance of D-19.)

D-33 POLLUX DIV  HYPOTHESIS VALID means "well-posed" to this reader;
     another would write NOT_EXAMINED because no fair instrument touched
     it. "VALID needs executed evidence" is undefined for the hypothesis
     layer when the test was never run. (Erebos D1 is the same
     divergence; the two Necromancers went opposite ways.)

D-34 EREBOS DIV  Executed-by-whom: Phase 3.K was executed by the original
     author in June; the Necromancer executed the instrument (calibration),
     not the measurement. MEASUREMENT rests on the calibration run;
     HYPOTHESIS/DESIGN partly on quoted verdicts.

D-35 EREBOS AMB  "External consumer" boundary: Stygian is a sibling under
     the same operator (Charon). Counted as external; a reader who defines
     external as "outside the swarm" gets only Harmonia B (code import).

D-36 EREBOS COLL Two hypotheses under one agent_id (H-A composer, H-B
     Layer-2 value). Certificates attack H-B; seam evidence defends H-A.
     fair_test scoped to H-B; scoped to H-A a reader could argue FAIR and
     not-refuted, for which the schema has no classification except
     CONSUMER_BLOCKED. (Instance of D-16.)

D-37 EREBOS AMB  Three kill conditions on record (Sprint-1 rule, ITER-100,
     the 06-15 pause); none is Erebos's own firing. The pause was recorded
     as the death; nothing in the doctrine says which of several unfired
     kill conditions is "the" death.

D-38 EREBOS SUBJ CONSUMPTION.jsonl counts design-doc consumption by Aporia
     as consumption; not counted as consumption of Erebos output here.
     The seam has no "consumed what" field.

D-39 EREBOS COLL ROSTER dossier_exists refers to the pivot dossier, not a
     Necropolis dossier. (Same as D-09; Nous 6 also.)

D-40 EREBOS DIV  A reader who refuses self-reported rows must mark
     EXECUTION NOT_EXAMINED. (See D-27.)

D-41 EREBOS AMB  "Underdetermined" vs HYPOTHESIS_FAILURE: an
     underdetermined test was not allowed to carry a hypothesis kill; the
     validator would accept either.

D-42 EREBOS SUBJ Calibration scope: one planted signal class
     (partner-conditioned kill pattern). MEASUREMENT says "no resolution
     for this class at N=699", not "no power ever".

D-43 EREBOS AMB  load_bearing semantics when the author self-downgraded
     (catalog-tier reclassification 05-27): treated as honest, not a layer
     failure; another reader files it as a HYPOTHESIS observation.

D-44 EREBOS COLL The queue's SELF-CONTAINED-GENERATION label was overturned
     (the seam was built but under-consumed) and no replacement class
     exists in any of the three vocabularies. (Instance of D-17.)

D-45 EREBOS DIV  NO_FAIR_TEST_ON_RECORD chosen; CONSUMER_BLOCKED fits the
     same stack; recorded in uncertainty. The classification is not a
     function of the stack.

D-46 EREBOS PROV 213 intelligence_outputs ticks vs 234 composed_claim
     artefacts: different objects, windows and hosts; recorded, not
     reconciled.

D-47 EREBOS SUBJ Six scripts against a brief asking for 2-4; declared
     rather than merged so each result answers one question.

D-48 EREBOS PROV Keeper census is dual-recorded single-mechanism; every
     EXECUTION number carries the caveat in prose only (no field).

D-49 EREBOS TOOL ORGANS.jsonl grew 39 -> 72 on the scratch copy; the
     Necromancer may not write the shared derived files, so validate.py's
     in-place regeneration has to be run by the Keeper. (Same as D-13.)

D-50 NOUS PROV No AGENT_AUTOPSIES row: the "prior verdict" slot is empty
     and the reviewer chooses which documents are certificates (four plus
     README plus QUEUE were chosen). (Same as D-20.)

D-51 NOUS DIV  Layer of the prompt change (da42cc7e0): DESIGN here; a
     second reader files it under CONFIGURATION (a string constant) or
     EXECUTION (it happened mid-series). Verdict-changing.

D-52 NOUS AMB  load_bearing read as "changed the historical answer", but
     which historical answer (resume doc, disposition plan, amended
     PENDING-REVIEW, thoughtwork) is undefined for a grave with an amended
     record.

D-53 NOUS COLL NO_FAIR_TEST_ON_RECORD, MEASUREMENT_FAILURE and
     SUPERSEDED_BUT_ORGANS_SALVAGEABLE all validate for the same stack; the
     choice lives in rationale prose. (Same shape as D-45.)

D-54 NOUS AMB  Whether supersession by a descendant is ECOSYSTEM_FAILURE or
     not a failure at all is not stated; filed as ECOSYSTEM INVALID,
     load-bearing for the LIMBO status.

D-55 NOUS AMB  Absence of Nous rows in a channel Nous never wrote to
     (agora.intelligence_outputs; Nous ran on M4 pre-template): the
     doctrine does not say whether such absence is EXECUTION or
     INSTRUMENTATION evidence; recorded under both.

D-56 NOUS TOOL The path resolver extracts "data/priority_triples.json"
     from a parenthetical as a separate path (false unresolved note).

D-57 NOUS VAL  A certificate correct in substance but carrying a defect in
     its own source (the "18-field" docstring) can only be
     PARTIALLY_UPHELD, since UPHELD forbids listing errors. (Pairs with
     D-29: the enum lacks both "form right, numbers unverifiable" and
     "substance right, source defective".)

D-58 NOUS AMB  Frankenstein fields: SCHEMA requires changed_design as an
     array; the charter A/Y/M/C->C'/R/kill template is prose. Encoded as
     four items; another reader splits differently.

D-59 KEEPER DIV  Two Necromancers reading the same doctrine went opposite
     ways on the same question (D-33 vs D-34: HYPOTHESIS VALID for Pollux
     as "well-posed", HYPOTHESIS evidence-by-quotation for Erebos with a
     stated NOT_EXAMINED alternative; Nous wrote NOT_EXAMINED). Three
     readers, three answers, one rule. This is the portability test's
     clearest measured failure so far.

D-60 KEEPER COLL Across the three READMEs the same defect recurs under
     different wording five times (D-27/D-40/D-48/D-55 self-report; D-30/
     D-56 path scan; D-28 pre-labels; D-39/D-50 dossier and certificate
     slots). The ledger has no dedup key; the Keeper cross-referenced by
     hand. A defects ledger that grows by repetition will read as more
     broken than the doctrine is.

## Cleric-level entries (merged by the Keeper from the Nous and Erebos CLERIC.md
## section 6 lists; grave-prefixed; the CLERIC.md files are the primary record;
## cross-references to earlier entries are the Keeper's)

D-61 KEEPER VAL  SCHEMA provenance.role enum is Necromancer|Cleric|Keeper; there
     is no adjudicator/Judge value, no Cleric-objection field and no
     adjudication field anywhere in the dossier. Every adjudication in this
     trial lives as an "ADJUDICATION (...)" paragraph inside
     disposition.rationale and the investigator string, i.e. as prose the
     validator cannot see. (Found when validate.py rejected role
     'Necromancer + Cleric + Judge'.)

D-62 KEEPER AMB  primary_cause has three readings (Erebos DD-2): cause of the
     organism stopping / cause of the certificates being wrong / cause of the
     question being unanswerable. The Erebos stack yields ECOSYSTEM_FAILURE /
     INTERPRETATION_ERROR / MEASUREMENT_ERROR respectively. Keeper RULING for
     this trial (not doctrine): the third reading, because the charter asks
     whether Prometheus earned the right to call the grave dead, not why the
     process stopped. Nous D-1 ("upstream wins" is convention, not rule) is the
     same gap from the other side. Needs a HITL doctrine ruling; recorded, not
     resolved. (Same family as D-17, D-26.)

D-63 KEEPER PROV Two different ITERs are labelled "Phase 3.K" on the Erebos
     record: ITER-66 scale stress (36f46b97f, 05-30) and ITER-83/84 pair-aware
     null (d7120eb5a, 06-03). A certificate citing "Phase 3.K" is resolved only
     by matching its numbers. Instance of a general defect: phase labels were
     reused within one organism's own history.

D-64 NOUS COLL The ECOSYSTEM layer admits one class (ECOSYSTEM_FAILURE =
     nothing consumed what it emitted). Consumer-instrument failure, operator
     re-allocation, deliberate shelving, and fleet-wide halts (Erebos DD-1)
     have no class, so the layer is forced to misuse the one it has or omit
     the event. Every May-fleet grave will hit the halt case. (Nous D-2, Erebos
     DD-1; relates to D-54.)

D-65 NOUS DIV  load_bearing has two readings inside one dossier: "carried the
     historical result" (DESIGN, MEASUREMENT) vs "carried the recorded status"
     (ECOSYSTEM). validate.py treats them identically and only within
     DESIGN..MEASUREMENT for UNFAIR. (Nous D-3; relates to D-43, D-52.)

D-66 NOUS AMB  A mid-series prompt change is DESIGN to one reader and
     CONFIGURATION_ERROR ("parameter regime") to another; no rule decides.
     (Nous D-4; same as D-51, recorded again because the Cleric hit it
     independently of the Necromancer.)

D-67 NOUS COLL Record-not-preserved (gitignored logs/runs) has no layer or
     class: INSTRUMENT_ERROR requires an apparatus that could not observe;
     here it observed and the record was discarded. (Nous D-5, Nous C-5; the
     Erebos INSTRUMENTATION layer carries the same fact under INSTRUMENT_ERROR
     for lack of anywhere else.)

D-68 NOUS VAL  "Executed evidence" (LAW N17) does not require determinism; a
     hash-order-dependent null passed the Necromancer's own bar (Nous C-1).
     No rule requires a seed or a replication count on an executed evidence
     row.

D-69 NOUS AMB  Whether a later consumer's re-run of the organism's keys (the
     May forge windows re-running March Nous keys) is part of the organism's
     fair_test scope is undefined. (Nous D-7.)

D-70 NOUS PROV identity.historical_machine takes a ROSTER label with no
     UNKNOWN value and no evidence requirement, and the label then leaks into
     findings as fact ("M4" was a 2026-05-13 forward assignment). (Nous D-9;
     amended in nous.dossier.json to "unknown ...".)

D-71 EREBOS COLL One HYPOTHESIS slot and one DESIGN slot for two hypotheses
     (H-A, H-B) and two versions of H-B (v1 refuted ITER-56/57, v2 redesigned
     the same day). The stack cannot express "refuted then repaired before
     the pre-committed test" without a false VALID or a lossy NOT_EXAMINED;
     the Keeper chose NOT_EXAMINED with the history in the finding. (Erebos
     DD-3; extends D-36.)

D-72 EREBOS COLL An underpowered statistic fits MEASUREMENT_ERROR ("recorded
     quantity is not the quantity named"), INSTRUMENT_ERROR ("apparatus could
     not observe") and DESIGN "chance floor"; Necromancer and Cleric filed the
     same evidence on different layers. Keeper ruling for this grave: chance
     floor -> INSTRUMENTATION; outcome column carrying pipeline state ->
     MEASUREMENT (SCHEMA's own words). (Erebos DD-4; same family as D-26.)

D-73 EREBOS AMB  Whose DESIGN: the layer describes the organism's design, but
     the load-bearing test (Phase 3.K) was an adversarial audit designed by
     the same author weeks later; a defect in the audit's statistic is filed
     on the organism's stack with no field naming which artefact is meant.
     (Erebos DD-5.)

D-74 EREBOS PROV LAW N6 "consumer at birth" is cited by SCHEMA and by
     dossiers but its text is not carried in the dossier; a reader cannot
     check the rule from the dossier alone. The Keeper quoted it inline in the
     Erebos DESIGN evidence as a workaround. (Erebos DD-6, second half; the
     8-vs-13 first half is D-18.)

D-75 EREBOS VAL  Nothing in SCHEMA/validate.py requires a sampled census to be
     labelled as a sample: "every summary ends enqueued=True" was built on a
     `limit 3` read and passed as a universal claim. (Erebos DD-7; the
     Keeper's own instrument.)

D-76 EREBOS AMB  Self-report admissibility: LAW N17 "executed evidence" does
     not say whether evidence executed BY THE ORGANISM (its own agora rows,
     tick summaries) counts. The census caveat "DUAL-RECORDED IS NOT
     INDEPENDENTLY VERIFIED" exists but no rule consumes it. (Erebos DD-8;
     same as D-27/D-40/D-48/D-55 -- the fifth independent hit.)

D-77 EREBOS DIV  A pre-registered kill test that never ran is EXECUTION_ERROR
     ("not executed faithfully"), DESIGN (designed but unreachable) or nothing
     (stopped from outside). Keeper ruling for this grave: EXECUTION_ERROR by
     SCHEMA EXECUTION's "no partial runs", with the finding that the stop was
     the author's own (timeline). (Erebos DD-9.)

D-78 EREBOS VAL  Certificate review granularity: a certificate factually right
     in its count but wrong in one inference can only be PARTIALLY_UPHELD,
     the same value used for "half wrong". The Cleric's requested
     "UPHELD-with-one-error" does not exist. (Erebos DD-10; pairs with D-29
     and D-57 -- the enum now lacks three distinguishable states.)

D-79 EREBOS VAL  Calibration worlds are not fingerprinted against the real
     ledger's structure: Necromancer synthetic null p95 = 1, historical 2,
     Cleric concentrated-marginal 7-10. "Instrument at floor" claims need a
     rule requiring the synthetic floor to bracket the historical one before
     the conclusion is admitted. (Erebos DD-11.)

D-80 EREBOS TOOL The Necromancer's external_refs counts drifted between the
     pass and the Cleric re-run (A 3->4, A2 14->19, B 198->207) because the
     tree moved and OWN_PREFIXES is incomplete; the committed result file is
     a snapshot without a tree SHA in its own body. (Erebos C-9.)

## Frankenstein-stage entries (Keeper writing as Doctor Frankenstein, 2026-09-11)

D-81 KEEPER PROC ORGANS.jsonl carried executed_by_necromancer = null for every
     nous.*, erebos.* and pollux.* organ at the point the first monsters were
     filed, although the dossier prose and evidence scripts record
     executions (Nous: 5918/5918 scorer replay, salvage build row-for-row,
     1212-row forge join; Erebos: 146 / 608+1 / 59 test passes, harness run
     on synthetic ledgers, consumer audit re-run). The mechanism exists
     (ORGAN_NOTES.json Keeper overlay, consumed by build_organs.py) but
     nothing in the Necromancer or Keeper procedure says WHEN to populate
     it, and the three Necromancer forks recorded execution only as
     parentheses inside residue strings. Fixed for nous.*/erebos.* by the
     Keeper on 2026-09-11 (30/88 organs now true); pollux.* still null
     pending the Pollux adjudication. Procedure gap, not schema gap.
     (Pairs with D-68.)

D-82 KEEPER PROV The historical Erebos kill_ledger.jsonl and
     kill_ledger_enriched.jsonl are gitignored (charon/agents/.gitignore
     */state/) and absent from the canonical tree and the worktree; every
     Phase 3 number on the record was computed over bytes no reader can
     recover. MONSTER_SCHEMA ancestral_comparison allows "the closest
     recoverable proxy" but nothing in SCHEMA.json requires a dossier to
     say, per load-bearing evidence row, whether the input bytes still
     exist. FRANK-003 says so in prose. (Instance of D-67 at the monster
     layer; erebos.representation_hints.1 is the organism-level statement.)

## Pollux Cleric entries (merged by the Keeper from dossiers/pollux_evidence/
## CLERIC.md section 6, D-1..D-9; plus two Keeper entries from the settling
## query and the corrected replay; rulings recorded, nothing resolved)

D-83 POLLUX AMB  primary_cause ranking is undefined: SCHEMA says "proximate
     cause", the Necromancer applied "deepest load-bearing INVALID" (not in
     any doctrine text), and the charter's MEASUREMENT_ERROR example ("a
     metric that carries its own answer") describes corr_raw = 1 literally.
     A reader applying "proximate" lands on MEASUREMENT_FAILURE; the Keeper
     landed on DESIGN_ERROR by the charter's definition of
     NO_FAIR_TEST_ON_RECORD ("could not have answered its own question").
     Keeper RULING for this trial: primary = cause of the question being
     unanswerable (D-62 carried over); the "deepest INVALID" rule is
     withdrawn as non-doctrine. The alternative reading is recorded in
     pollux.dossier.json uncertainty[4]. (Pollux D-1; same family as D-62.)

D-84 POLLUX COLL HYPOTHESIS VALID has two meanings: "well-posed and
     answerable" (the Necromancer's) and "not refuted" (the natural one).
     There is no class for an ILL-POSED hypothesis -- one with no defined
     test on the record -- so the only honest verdict is NOT_EXAMINED, which
     also means "nobody looked". Pollux is filed NOT_EXAMINED with the
     N1/N2 result in the finding. (Pollux D-2.)

D-85 POLLUX COLL A Necropolis-executed null that kills an organism's only
     operationalization (N1/N2: PROMOTED recurs under independence up to
     0.94) has no place in the stack: HYPOTHESIS_FAILURE requires a FAIR
     historical test (validate.py line 210), the historical test is UNFAIR,
     and a kill executed after death is not a death certificate. The result
     lives as prose in the HYPOTHESIS finding and in kill_boundary. The
     doctrine forbids optimizing for resurrection rate but gives the
     opposite result -- a fair post-mortem kill -- nowhere to go.
     (Pollux D-3; HITL doctrine question.)

D-86 POLLUX VAL  EXECUTION VALID is a conjunction ("ran as written, no
     partial runs, faithful") with no grade for self-reported evidence. For
     Pollux every EXECUTION row descends from the daemon's own agora writes.
     Keeper ruling: admitted because two independent readers and a code
     replay agree on every count, with the caveat carried in the finding.
     No field says "VALID on self-report". (Pollux D-4; D-76 sixth hit.)

D-87 POLLUX DIV  load_bearing on post-outcome layers (INTERPRETATION,
     ECOSYSTEM) has no defined referent: nothing after the outcome can carry
     the outcome. The Necromancer set both false; validate.py accepts any
     value. (Pollux D-5; same fact as D-65 from the other side.)

D-88 POLLUX PROV DISCHARGED ON THIS GRAVE, GAP REMAINS. Two readers of a lost
     ledger agreeing (06-24 dossier, P69: 86/39/161) is one observation
     copied twice unless a third channel exists. Here the Keeper found one
     (agora.intelligence_outputs GROUP BY output_summary) and it matched
     both readers exactly, so the Cleric's C-3 lost by execution. No rule
     says a dossier must look for a second channel before grading a
     certificate's count, and nothing marks a count as "single-source".
     (Pollux D-6.)

D-89 POLLUX PROV DISCHARGED ON THIS GRAVE, GAP REMAINS. Commit time is not
     deploy time: the Cleric inferred a ~22 h gap between commit 43b094552
     and the v0.6 behaviour from the readers' counts; the tick sequence
     shows an 11-minute restart gap ending 2 minutes before the commit, so
     v0.6 was running from the working tree before it was committed.
     identity/observed_history has no deploy-time field and no rule asks
     for one; a grave with no second channel could not have settled this.
     (Pollux D-7.)

D-90 POLLUX VAL  Null sidedness is not a required field: the Necromancer's
     T3 reported two-sided p on a one-sided verdict (deg14 "fails" at
     0.093; signed p 0.023). validate.py checks evidence presence, not that
     a p-value's alternative matches the verdict it is cited against.
     (Pollux D-8; Cleric C-5.)

D-91 POLLUX VAL  validate.py line 210 requires fair_test FAIR for a STRONG
     class only when it is PRIMARY; a STRONG class in contributing_causes
     under UNFAIR passes. Nothing on this trial exercised the hole, but the
     negative test does not exist in tests/. (Pollux D-9; belongs to
     RHAD-30 validator hardening.)

D-92 KEEPER META Reader CONVERGENCE, not divergence, as a META-TEST failure:
     the Necromancer fork (pollux_rescan.py Q4, "P69's census is
     unreproducible; replay yields 15/15/256") and the Cleric fork
     (cleric_census_fit.py S2, "if the code produced the ledger, 62/63/161")
     reached opposite-sounding but jointly false claims from ONE shared,
     untested assumption: that a settled pair leaves the rotation
     unconditionally. daemon.py _promote_settled_replace removes it only
     while CANDIDATE_POOL still has a replacement. Two adversarial passes
     agreed on the false premise because both read the daemon's LOG LINE
     ("active rotation shrunk") instead of its code path. The META-TEST
     asks whether fresh adjudicators diverge; it has no check for whether
     they share an unexamined premise. Recorded against the Keeper's lane in
     roles/Rhadamanthus/calibration/LEDGER.md. Detected only because the
     Keeper ran the Cleric's proposed settling query rather than ruling on
     the argument. (Keeper; pollux_replay_corrected_result.json.)

D-93 KEEPER AMB  A code path that diverges from its own log message
     (pool-exhaustion: log says "rotation shrunk", code leaves the pair in
     rotation) has no owning layer: IMPLEMENTATION (the code is wrong
     relative to its comment) or INSTRUMENTATION (the log is the instrument
     the operator and every later reader consulted, and it lied).
     Keeper ruling for this grave: IMPLEMENTATION, non-load-bearing, with
     the question kept open in provenance.unresolved_questions. (Keeper.)
