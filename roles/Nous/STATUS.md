# Nous -- status

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11T13:30Z (base-role adoption pass). Updated at least
every four hours of activity. Plain language, no dramatic words.

## State

    seat state       BLOCKED on NOUS-XL-01 (revive / park / retire)
    present          YES  -- booted in comms 2026-09-11
    active           YES  -- this adoption pass ran; nothing else since April
    productive       NO   -- no domain output today; the artifacts are
                            roles/Nous/ and two committed scripts
    valid            n/a  -- this seat has adjudicated nothing

## What is true right now, in one paragraph

Nous generated scored cross-domain concept triples between 2026-03-24 and
2026-04-02 and has produced nothing since. The loop did not stop, it
starved: the last line of its log is an API call that never returned, and
nobody noticed for 162 days. Two things were established on this pass.
First, 41.4% of everything the seat ever produced -- 4,187 rows, ten run
directories, the whole final six days, plus the log that records the
death -- was never committed, because .gitignore:140 swallowed it; it
exists on one machine's disk and nowhere else. Second, the seat measured
its own shipped instrument and falsified its ranking channel: the
composite it handed downstream is nearly constant and cannot separate the
scorer's own reject class (p = 0.31). Its consumer chain is dead at every
hop (Coeus MEASUREMENT_FAILURE 2026-09-10; the forge stopped 2026-05-28).
No prompt, message or task has ever been addressed to this seat. It is
registered, it is not running, and it recommends PARKED over REVIVED
unless a live consumer is named first.

## Numbers a reader may want without opening the archaeology

Committed corpus (the figures another seat can reproduce):

    corpus                       5,918 rows, 12 run directories
    high_potential                 719 (12.1%)
    novelty == novel             5,462 (92.3%)    novelty == existing:  4
    reasoning rating sd          0.532 (mode 7 holds 57.7% of rows)
    reject-class separation      6.4696 vs 6.4067, z = +1.28, p = 0.308
    controls of any kind             0
    last COMMITTED output        2026-03-27

On this machine's disk only, in no tree:

    uncommitted rows             4,187 in 10 run directories (17 MB)
    uncommitted date range       2026-03-28 .. 2026-04-02
    also uncommitted             agents/nous/nous.log (the death record)
    last output overall          2026-04-02T12:43:29Z
    dormant for                  162 days
    prompts ever received            0

Reproduce: `python roles/Nous/science/corpus_audit.py` (add `--check` to
fail on drift from the values frozen at 363120e08), and
`python roles/Nous/science/test_guard.py` for the workspace guard's
positive and negative controls. Both pass at 363120e08.

## Standing loops

    NousGeneratorLoop            DORMANT since 2026-04-02; not relaunched
                                 registered in roles/base-role/MONITORS.md
                                 input  PRESENT-UNVERIFIED (NVIDIA NIM;
                                        the two models Nous used were not
                                        probed today)
                                 output consumer DEAD since 2026-05-28

## Blockers

    NOUS-XL-01   operator decision: revive with a re-premised charter,
                 park, or retire with the machinery absorbed. Nothing in
                 the repository answers it. Recommendation: PARKED, with
                 the committed corpus retained as a calibration fixture
                 rather than as a hypothesis source.

## Next executable action

NOUS-01: preserve the 4,187 uncommitted rows and nous.log. They are one
`git clean` from gone and the working contract explicitly permits any
seat to delete untracked scratch in the canonical checkout. This pass did
NOT commit them -- 17 MB is beyond the operator's "bootstrap and
registration" scope -- so the decision needed is one line: commit them
under a `!agents/nous/runs/` re-include, archive them outside git, or
accept the loss deliberately. Accepting the loss is a legitimate answer;
losing them by not answering is not.
