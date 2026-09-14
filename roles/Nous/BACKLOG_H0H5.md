# Nous -- backlog

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11 (created on the base-role adoption pass).

PROVISIONAL, AND BELOW THE SCHEMA FLOOR, DELIBERATELY. The schema
(roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md) requires
at least 20 items in priority order. This file has 10. The reason is
recorded rather than padded:

    This seat is BLOCKED on NOUS-XL-01 and its entire consumer chain is
    dead. Manufacturing 10 more items would mean inventing work for a
    pipeline with no live hop, which is the failure base rule 8 names as
    "scheduled activity is not progress". A backlog padded to a floor is
    a backlog that hides its own blocker. The floor is reported unmet
    instead.

Each item names the artifact that proves it done. NOUS-01 to NOUS-04 and
NOUS-06 to NOUS-07 need no decision from anybody. The first item is the
only urgent one on the list.

Format: ID | item | lane | milestone | size | blocked_on | evidence of done

NOUS-01 | Preserve the 4,187 uncommitted rows and agents/nous/nous.log, which exist only in the canonical checkout's working directory and which any seat's declared clean-up may delete: commit them under a `!agents/nous/runs/` re-include, archive them outside git, or record a deliberate decision to accept the loss | EVIDENCE | alpha | S | operator (17 MB into the repository exceeds the "bootstrap and registration" scope of this pass; the choice is one line and the risk is live until it is made) | either the commit adding the 10 run directories with the .gitignore re-include, or a committed note recording where they were archived, or a dated decision accepting the loss with the row count it costs
NOUS-02 | Correct agents/nous/README.md against the artifacts it cites, as dated annotations beside the original with supersession markers, never a silent rewrite | TOOLS | alpha | S | none | the committed README diff annotating the +0.221 / -0.4670 sign flip, the 1,500 / 5,918 corpus size and the 20-30% / 12.1% high-potential rate, each with its measured value and source
NOUS-03 | Diagnose the 153 `unclear` novelty rows and the ~100 rows missing an implementability rating, attributing each between model behaviour and scorer regex parse failure | EVIDENCE | alpha | S | none | a committed table splitting the rows by cause, with the scorer regex path quoted and 10 sampled raw response texts beside their parse outcome
NOUS-04 | Write the three controls the instrument never had and run them against the FROZEN committed corpus only (no API call): a shuffled-triple arm, a repeated-triple self-consistency arm, and a content-free-string arm scored by the committed scorer | EVIDENCE | alpha | M | none | roles/Nous/science/controls.py plus a committed result table giving the scorer's output on each degenerate arm beside the real-input distribution, with the eligible count for each
NOUS-05 | Join the Hephaestus forge ledger to the committed corpus and report how many forged tools trace to a specific Nous triple and what their composite scores were | EVIDENCE | alpha | M | Hephaestus (the ledger is that seat's lane; a read needs no permission but the join's interpretation should be reviewed by its owner, and section 2 says much of the ledger may itself be uncommitted) | a committed join table with the eligible count, plus the explicit count of forged tools having NO traceable Nous origin
NOUS-06 | Report the ignored-output measurement to the seats it concerns: Hephaestus (5,151 ignored files), Nemesis (12 tracked against 3,022 ignored), Icarus (644), and Archaeon as the owner of the base role and .gitignore | EVIDENCE | alpha | S | none | the comms message ids and the committed INBOX files under roles/Nous/prompts/, each stating that file counts were measured and results-versus-scratch was NOT determined
NOUS-07 | Post to the Necropolis Keeper the design input that `coeus-d1-frozen-judge-structure-test` would regress a concept dictionary and a sampler bias this seat authored, and that some forge-outcome rows it needs may be among the uncommitted 4,187 | EVIDENCE | alpha | S | none | the comms message id and the committed prompt file, with this seat proposing nothing about the experiment itself
NOUS-08 | Probe whether either model Nous actually used still answers for this account, as a ONE-CALL liveness read, not a relaunch | TOOLS | alpha | S | operator scope limit (this pass was bootstrap and registration only; NOUS-XL-01 supersedes it if the answer is PARK or RETIRE) | a committed record of the two model ids with their HTTP result and latency, or the explicit statement that the probe was not authorised
NOUS-09 | Add a dormancy freshness file for NousGeneratorLoop (last_input_at, last_success_at, no_op_reason) readable without running the loop, so the registry row stops depending on a log file that is itself uncommitted | TOOLS | alpha | S | none | the committed freshness artifact plus the MONITORS.md row pointing at it instead of at nous.log
NOUS-XL-01 | Decide: is Nous REVIVED with a re-premised charter, PARKED, or RETIRED with its machinery absorbed | program | program | XL | operator decision (NEW: no D-nn exists; propose one) | the decision recorded in archaeon/docs/expansion/DECISIONS.md and this seat's state changed to match. Seat recommendation: PARKED, committed corpus retained as a calibration fixture, with the argument against revival stated in RESPONSIBILITIES.md section 4
