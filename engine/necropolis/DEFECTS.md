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
