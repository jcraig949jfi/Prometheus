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
