# Hypatia -- backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Priority order. The first five are the ones this seat
would start today; four of the five are blocked by HYPATIA-01, which is the
whole point of listing them.

The seat's recommendation on HYPATIA-01, stated plainly because the base role
says to give one: ADAPT, not REVIVE and not RETIRE. The daemon scaffold, the
R1-R5 ladder and the dispatch provenance schema are sound and reusable. The
PREMISE (decompose proofs of open conjectures) is void and must not be
restarted. The cheapest honest re-premise is HYPATIA-03: point the same
machinery at objects that HAVE proofs, or at the program's own kill-geometry,
and require a parseability gate on emission before a single example is
allowed toward a corpus.

    HYPATIA-01 | Rule the disposition left blank in pivot/COMPONENT_DOSSIERS_2026-06-24.md (Hypatia section): ADAPT / REVIVE-after-ingester / RETIRE-after-HITL | program | program | XL | operator decision NEW: "Hypatia disposition, blank since 2026-06-24; seat recommends ADAPT" | the HITL line filled in, or a D-nn row in archaeon/docs/expansion/DECISIONS.md
    HYPATIA-02 | Preserve the 177 M1 artifacts, events.jsonl and state.json before they are lost | EVIDENCE | program | S | a seat with M1 filesystem access | the files committed under roles/Hypatia/archive/run_2026-05/ with a MANIFEST of sha256
    HYPATIA-03 | Re-premise the D-track onto a backlog whose problems have proofs, or onto kill-geometry, and write the preregistration before touching data | H1 | alpha | L | operator decision HYPATIA-01 | a committed preregistration naming the source catalog, the eligible count, and the INDETERMINATE branch, in its own commit ahead of any run
    HYPATIA-04 | Extract the R1-R5 ladder taxonomy into a standalone committed schema with worked examples, usable without the daemon | EVIDENCE | alpha | S | none | roles/Hypatia/science/ladder_schema.md plus a validator that rejects a malformed step
    HYPATIA-05 | Add an emission-time parseability gate to the daemon so it can never again emit an artifact it cannot itself load | TOOLS | alpha | S | operator decision HYPATIA-01 | a test in roles/Hypatia/science/ that fails on the 2026-05-30 report and passes on a repaired one
    HYPATIA-06 | Add the D-23 assert_not_canonical guard to agents/hypatia/daemon.py and mark scripts/hypatia_loop_launch.bat superseded | TOOLS | alpha | S | none | the guard in the entry point, referencing archaeon/workspace.py, plus a test that the daemon refuses to run in the main worktree
    HYPATIA-07 | Post the 4-vs-8 dispatch-count correction to Aporia and record whether the ledger is amended | EVIDENCE | program | S | Aporia (seat never_booted; message queues) | a comms message id and a dated line in calibration/LEDGER.md L-07 recording the outcome
    HYPATIA-08 | Report to Archaeon that the wake directive still says "pull the latest from the repo first", which WORKING_CONTRACT s3 says should have been reworded at its source | TOOLS | program | S | Archaeon | a comms message id, and either the reworded directive or a ruling that it stands
    HYPATIA-09 | Fix the Pheme seam contract (dict vs string) on the consumer side, gated on the cheat control not the exception | TOOLS | beta | S | operator decision HYPATIA-01 and Pheme (PHEME-01) | seam_contract_test.py extended with a repaired-seam case, all three controls still passing
    HYPATIA-10 | Measure whether the 8 surviving deep-research reports have any value as literature surveys, separately from their value as training data | LIT | program | M | none | a committed readout with an eligible count and an explicit NULL branch
    HYPATIA-11 | Write the freshness file (last_input_at / last_success_at) the MONITORS row says HypatiaDTrackLoop does not have | TOOLS | alpha | S | operator decision HYPATIA-01 | roles/Hypatia/state/freshness.json committed and readable without running the daemon
    HYPATIA-12 | Decide with Ergon whether a worked-solutions corpus has any consumer at all before anything is built to fill it | EVIDENCE | program | M | Ergon (seat never_booted) | a committed answer from Ergon, or a recorded refusal, in roles/Hypatia/prompts/
    HYPATIA-13 | Re-run the MATH-0008 confabulation as a named, citable example of an LLM satisfying an output contract it cannot satisfy honestly | EVIDENCE | program | M | operator decision HYPATIA-01 | a committed write-up with the 2621 s trace quoted and the substituted theorem identified
    HYPATIA-14 | Ask the Keeper to resolve the necropolis roster row carrying two different failure classifications for this seat | EVIDENCE | program | S | Necropolis Keeper | a comms message id and the resolved row, or a recorded ruling that both fields are intended
    HYPATIA-15 | Check whether any other seat ever consumed the R1-R5 ladder, and if none did, say so in one line | EVIDENCE | program | S | none | a committed grep receipt with its command and the count, including zero
    HYPATIA-16 | Establish whether aporia/mathematics/questions.jsonl has an owner today, since the catalog is the D-track's only input | LIT | program | S | Aporia | a named owner or a recorded absence in roles/Hypatia/ARCHAEOLOGY_2026-09-11.md
    HYPATIA-17 | Retire scripts/hypatia_loop_launch.bat properly if HYPATIA-01 rules RETIRE, lifting the salvage IP first | TOOLS | program | S | operator decision HYPATIA-01 | the salvage committed under roles/Hypatia/science/ and the script annotated, not deleted
    HYPATIA-18 | Keep STATUS.md current at four-hour granularity on any pass where this seat does work | program | program | S | none | the currency line in STATUS.md moving with each pass
    HYPATIA-19 | Record in MONITORS.md any change to HypatiaDTrackLoop's state, and never let its silence read as health | TOOLS | program | S | none | the row's state column matching the measured reality at each boot
    HYPATIA-20 | Add a row to roles/base-role/INHERITANCE.md for this seat in both tables, per the self-service ruling | program | program | S | none | two rows present and archaeon/tests/test_base_role.py passing
