# Skopos -- backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Seat state BLOCKED on SKOPOS-XL-01. Items 06 and
below are NOT startable until that decision lands; they are listed with the
blocker named rather than hidden, per the schema's rule.

Format: ID | item | lane | milestone | size | blocked_on | evidence of done

SKOPOS-01 | Create the seat directory with RESPONSIBILITIES, ARCHAEOLOGY, CALIBRATION, STATUS, BACKLOG and a dated journal | EVIDENCE | program | S | none | roles/Skopos/ committed on main (DONE 2026-09-11)
SKOPOS-02 | Register the seat's two rows in roles/base-role/INHERITANCE.md (register + entry file) | EVIDENCE | program | S | none | the two rows present at origin/main (DONE 2026-09-11)
SKOPOS-03 | Register SkoposScoreCycle in roles/base-role/MONITORS.md with state DORMANT, dead input named, and lifetime productivity signal | EVIDENCE | program | S | none | the row present at origin/main (DONE 2026-09-11)
SKOPOS-04 | Record the boot in comms and sync the inbox before and after this pass | EVIDENCE | program | S | none | comms.agents row for Skopos with base_sha/branch/worktree_path; sync receipt (DONE 2026-09-11)
SKOPOS-05 | Post the defect reports found in other seats' files to their owners through comms | EVIDENCE | program | S | none | comms messages to PipelineOrchestrator (dead design premised on a 1-entity scorer) and Metis (consumes a self-contradicting report, metis.py:94-103)
SKOPOS-06 | Annotate agents/skopos/README.md in place with a dated supersession block naming the 1-entity lifetime and the never-executed GENERATE stage, without rewriting it | EVIDENCE | program | S | none | the annotation committed; original text unchanged below it
SKOPOS-07 | Add a dated annotation to each of the six alignment reports marking the header count as a 5x units error, corrected in place, originals intact | EVIDENCE | program | S | none | six annotated reports committed
SKOPOS-08 | Obtain an INDEPENDENT audit of roles/Skopos/ARCHAEOLOGY_2026-09-11.md from a seat that is not Skopos | EVIDENCE | program | S | a seat with an audit mandate accepting (Elenchus, Kairos or Aporia) | that seat's review committed under its own prompts directory, agreeing or dissenting item by item
SKOPOS-09 | Write the falsification test that would have caught D1 -- a fixture asserting a yield count equals a DISTINCT entity count, not a row count | TOOLS | program | S | SKOPOS-XL-01 | a test file that fails against skopos.py:510 as written and passes against the fix
SKOPOS-10 | Write the cheat control for the scorer: inject a fabricated maximally-relevant entity and assert the channel emits its own trigger value | TOOLS | program | S | SKOPOS-XL-01 | a fixture showing the 4+ branch executing for the first time in the seat's history
SKOPOS-11 | Write the negative control: assert a deliberately irrelevant entity scores 0 and produces no downstream artifact | TOOLS | program | S | SKOPOS-XL-01 | committed fixture and its recorded output
SKOPOS-12 | Write the positive control: a known-relevant entity with a pre-registered expected band, pre-registered in its own commit before the run | TOOLS | program | S | SKOPOS-XL-01 | preregistration commit preceding the result commit in git history
SKOPOS-13 | Separate the eligibility rule from the dedup rule and key the dedup on (entity, thread) to match the table grain | TOOLS | program | S | SKOPOS-XL-01 | the fix plus a test that a newly added thread scores an already-seen entity
SKOPOS-14 | Move the research-thread list out of code into versioned data, with rows keyed to the version | TOOLS | program | M | SKOPOS-XL-01 | thread list in a versioned file; a migration that either re-scores or marks orphaned rows superseded in place
SKOPOS-15 | Add the eligible count and the attainable score range to every report, with "nothing fired" and "nothing could have fired" as distinct lines | TOOLS | program | S | SKOPOS-XL-01 | a report showing both lines and a denominator on every count
SKOPOS-16 | Write last_input_at, last_success_at and an explicit no-op reason to a file readable WITHOUT running the scorer, and point the MONITORS row at it | TOOLS | program | S | SKOPOS-XL-01 | the freshness file committed and the registry row updated to name it
SKOPOS-17 | Add the D-23 workspace guard to the scorer's entry point so it refuses to run from the canonical checkout | TOOLS | program | S | SKOPOS-XL-01 | assert_not_canonical wired into skopos.py main(); a recorded refusal
SKOPOS-18 | Remove the automatic score-gated artifact path so no model score triggers an output without a deterministic predicate or a human | TOOLS | program | S | SKOPOS-XL-01 | the GENERATE trigger replaced by an explicit human-invoked command; the change committed with the base-role citation
SKOPOS-19 | Identify and name a LIVE selector in the current program that wants instrumenting, or record that none does | EVIDENCE | program | M | SKOPOS-XL-01 | a committed note naming the selector and its owner's acceptance, or a dated negative with the seats asked
SKOPOS-20 | Measure whether the March false number changed any Metis brief, or record the question as unanswerable and say why | EVIDENCE | program | S | SKOPOS-XL-01 | a committed measurement with its command, or a closed INDETERMINATE with its reason
SKOPOS-21 | Re-run the March scorer's judgement on the 448 eligible entities as an offline replay, to measure what the eligibility window cost, WITHOUT reviving the loop | EVIDENCE | program | M | SKOPOS-XL-01 and a model budget | a coverage table: entities scored, distribution of scores, count reaching 4, all with denominators
SKOPOS-22 | Check whether other seats' reports publish a yield without an eligible count, and report instances to their owners | EVIDENCE | program | M | SKOPOS-XL-01 (this is an audit lane and the seat holds no audit mandate) | a committed enumeration with the denominator present or absent per report, delivered to each owner
SKOPOS-23 | Retire agents/skopos/data/scores.db's orphaned rows by marking them superseded in place with their dead thread_ids, never by deletion | TOOLS | program | S | SKOPOS-XL-01 | a migration that adds a supersession column and leaves all five rows readable
SKOPOS-24 | Decide the seat's disposition | EVIDENCE | program | XL | operator decision SKOPOS-XL-01 (NEW: revive Skopos re-premised as instrumentation-of-selection, park it, or retire it with its machinery absorbed) | a ruling recorded in archaeon/docs/expansion/DECISIONS.md and reflected in roles/Skopos/STATUS.md

## Operator decisions this seat holds (the XL rows)

SKOPOS-XL-01 (SKOPOS-24) -- revive re-premised, park, or retire. Seat's
recommendation: PARK, argued against its own interest in
roles/Skopos/RESPONSIBILITIES.md section 5. Nothing here recommends RETIRE;
the base role is explicit that nothing is marked dead prematurely.
