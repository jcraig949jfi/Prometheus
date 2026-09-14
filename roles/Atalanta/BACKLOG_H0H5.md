# Atalanta backlog (H0-H5 schema)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Schema:
roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md.

    <ID> | <item> | <lane> | <milestone> | <size> | <blocked_on> | <evidence of done>

SUPERSEDED 2026-09-11 by the ruling below; the original line is kept as
written: "Nothing below ATALANTA-01 is executable until ATALANTA-01 is
ruled, except ATALANTA-04, ATALANTA-05 and ATALANTA-11, which are
startable today. The first five rows are the ones this seat starts when
told to work." The rows themselves are left unedited; their disposition is
in the status block.

## Status after the 2026-09-11 ruling and ATALANTA-04

    ATALANTA-01  RULED by the operator 2026-09-11: RETIRE-AND-LIFT-ASSET.
    ATALANTA-04  DONE. DEAD_GATING_SPECIMEN.md + census + invariant +
                 reference/ (9 controls, 9 passed) + ledgers/.
    ATALANTA-03  TAKEN BY ARCHAEON: now base rule 9. Superseded here.
    ATALANTA-05  TAKEN BY ARCHAEON: comms fails closed off-M1 and names
                 EW_DB_HOST; documented in comms/README.md.
    ATALANTA-22  PARTLY ANSWERED: a second recording channel was found
                 (agora.intelligence_outputs, 354 + 305 rows). It is an
                 independent RECORD, not an independent MEASUREMENT --
                 one witness, two statements -- so the 354 keeps its
                 August M1 attribution and is not upgraded.
    ATALANTA-06/07/08/09/10/12/13/14/17  CLOSED BY THE RULING: all are
                 daemon repairs or revival steps. The daemon is retired.
    ATALANTA-19  ANSWERED by SALVAGE_ASSESSMENT_2026-09-11.md: no lane
                 remains and nothing uniquely useful is left inside the
                 agent. Clean retirement recommended.
    ATALANTA-02  STILL OPEN and still not this host's to do: the M1
                 filesystem residue. Lower value now that the telemetry
                 channel has been recovered.
    ATALANTA-15  ANSWERED: pheme_upstream_not_found 354 and
                 pheme_self_audit_null 305 -- identical to Atalanta's
                 counts, from agents launched in the same commit and
                 ticking within a second of each other. One failure
                 deployed twice, not two failures.
    ATALANTA-16  ANSWERED IN PART: no shared source for the phantom
                 apollo/runs path was found. What was established is that
                 two authors invented it independently in the same week,
                 which is evidence about the system permitting guesses,
                 not about a common source. Recorded as a NULL with its
                 search scope, per doctrine.
    ATALANTA-20  THE REMAINING ACT if the operator accepts retirement.
    ATALANTA-21  HANDED to the Necropolis Keeper in the Archaeon report,
                 with the telemetry census script as the starting point.

New, arising from this pass and NOT owned by this seat:
    the two machine probes (M1 and M2) fire every five minutes and fail
    every time, with no owner and no alarm route; cause unresolved with
    two hypotheses eliminated. Routed to Archaeon.

ATALANTA-01 | Rule the disposition left blank in the June dossier: retire-after-HITL, refactor-to-config-driven-upstream, adapt-to-eval-feedstock, or retire-and-lift-asset | TOOLS | program | XL | operator decision (NEW: what happens to a consumer seat whose producer is dormant by ruling) | the HITL line at pivot/COMPONENT_DOSSIERS_2026-06-24.md:179 filled in, or a D-nn row in archaeon/docs/expansion/DECISIONS.md
ATALANTA-02 | Locate and preserve the M1 runtime residue (354 artifacts, state.json, events.jsonl) before it is lost, or record in writing that it is already gone | TOOLS | program | S | a seat with M1 filesystem access (none on SPECTREX5) | a committed census file under roles/Atalanta/archive/ giving the artifact count and the state.json fields, or a committed note saying the residue is unrecoverable and on what evidence
ATALANTA-03 | Propose to Archaeon that upstream-liveness become a typed LAUNCH precondition in the base role, not a per-tick observation, with the park-and-stop gate the P47 autopsy specifies | ENGINE | program | M | Archaeon (proposal posted 2026-09-11) | a base-role or shared-guard change committed by Archaeon, or a recorded rejection with its reason
ATALANTA-04 | Write the DEAD-GATING specimen note: what 354 identical honest absence reports cost, and the three independent gates that all failed open (path, alarm route, launch precondition) | EVIDENCE | program | S | none | roles/Atalanta/DEAD_GATING_SPECIMEN.md, committed, with every number carrying its provenance grade
ATALANTA-05 | Report the SPECTREX5 comms resolver gap (local prometheus_fire has no comms schema; EW_DB_HOST=192.168.1.202 required) so no seat booting here reads a silent wrong database | TOOLS | program | S | none | a comms report to Archaeon and a line in comms/README.md or evidence_wiki/docs/OPERATIONS_V1.md naming the override
ATALANTA-06 | Add the assert_not_canonical guard to agents/atalanta/daemon.py and supersede scripts/atalanta_loop_launch.bat, so the loop cannot start from the canonical checkout | TOOLS | alpha | S | ATALANTA-01 (do not repair a tool that may be retired) | the guard in daemon.py plus a test that the entry point refuses when git-dir equals git-common-dir
ATALANTA-07 | Replace the three hardcoded APOLLO_RUN_ROOTS with a configured path and make absence a startup failure, not a tick artifact | TOOLS | alpha | S | ATALANTA-01 | daemon.py reading the path from config, plus a test that a missing upstream exits non-zero on the first tick
ATALANTA-08 | Write the reader that turns Apollo's real output (checkpoint pickles, novel_discovery.jsonl) into the {run_id, organisms, primitive_sequence} shape the miner expects | TOOLS | alpha | M | ATALANTA-01 and Apollo un-dormanted | a reader with a fixture test over one real apollo/run_v2d2b checkpoint, committed with the checkpoint's hash
ATALANTA-09 | Compute the attainable range and eligible count for primitive reuse and composite frequency over a real organism population BEFORE setting any threshold | EVIDENCE | alpha | M | ATALANTA-08 | a committed distribution table with N organisms, the observed range, and the threshold chosen after it, in that commit order
ATALANTA-10 | Lift aggregate_primitive_signals (daemon.py:270-299) into a standalone tested module so the salvage IP survives any retirement of the agent | TOOLS | program | S | ATALANTA-01 | the module plus a positive, a negative and a cheat fixture over synthetic organism sequences
ATALANTA-11 | Seed the calibration ledger with every unmeasured May-era claim this seat carries, and keep adding to it | EVIDENCE | program | S | none | roles/Atalanta/calibration/LEDGER.md with one row per claim and its status
ATALANTA-12 | Re-check the Type-E DR template's five mandated calibration patterns against current doctrine before any reuse of the prompt | LIT | alpha | S | ATALANTA-01 | a committed table: pattern, still-doctrine yes/no, the citation that settles it
ATALANTA-13 | Decide with Techne whether a primitive candidate handoff is a comms delegation or a file drop, and write the contract down | TOOLS | beta | S | ATALANTA-01, Techne | a contract file agreed in a comms exchange, committed under roles/Atalanta/ with Techne's ack id
ATALANTA-14 | Separate result artifacts from gate artifacts in any successor, so an artifact count can never rise while nothing happens | TOOLS | alpha | S | ATALANTA-01 | two distinct output directories plus a test that a gated tick writes to neither the result stream nor the lifetime counter
ATALANTA-15 | Answer whether Atalanta and Pheme failed twice or once: both launched 2026-05-23, both ran exactly 354 ticks, both 100 percent absence | EVIDENCE | program | S | ATALANTA-02 (needs the residue) | a committed comparison of the two state.json files and a stated reading with its eligible count
ATALANTA-16 | Trace why apollo/runs was named as a live path by two independent agents (Atalanta and Talos) in the same week | EVIDENCE | program | S | none, but low value before ATALANTA-01 | a committed note naming the shared source of the phantom path, or an explicit NULL if none is found
ATALANTA-17 | Register a freshness file (last_input_at, last_success_at) for the loop, readable without running it, if the loop survives ATALANTA-01 | TOOLS | alpha | S | ATALANTA-01 | the file, plus its MONITORS row pointing at it instead of at gitignored state
ATALANTA-18 | Declare and keep current this seat's conflicts of interest as a Necropolis subject and a PROF-Atalanta target | EVIDENCE | program | S | none | the declaration standing in STATUS.md and re-checked at each boot
ATALANTA-19 | Decide whether this seat has a lane at all once Apollo's own disposition is ruled, and say so plainly if the answer is no | TOOLS | program | XL | operator decision, downstream of Apollo APOLLO-04 | a committed recommendation from this seat that is able to say "not worth continuing"
ATALANTA-20 | If retired, write the retirement annotation so the residue, weak signals and gradients stay navigable rather than deleted | EVIDENCE | program | S | ATALANTA-01 resolving to retire | a retirement annotation beside the charter, with the salvage IP pointers resolved
ATALANTA-21 | Check whether any other agent in the 48-seat Necropolis roster shares the DEAD-GATING family, and count the class before calling it a pattern | EVIDENCE | program | M | the Necropolis Keeper owns this lane; offer, do not take | a comms offer to the Keeper and either a delegation accepted or a recorded decline
ATALANTA-22 | Verify the 354 figure against a second source, or mark it permanently single-sourced | EVIDENCE | program | S | ATALANTA-02 | either a second independent count committed, or a line in the calibration ledger marking the number single-sourced and un-re-verifiable
