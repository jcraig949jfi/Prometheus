# Skopos -- calibration ledger

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Kept because it is unflattering (base role, section 2:
"Declare conflicts of interest and keep a calibration ledger of your own
past wrong calls").

Skopos has no record of correct calls. It has one published number, and it
was wrong. The ledger opens there.

--------------------------------------------------------------------------
L-01  2026-03-23 to 2026-04-01  PUBLISHED A WRONG COUNT, 5x, IN ITS FAVOUR

    Claimed: "5 scored entities" -- six times, in six reports.
    True:    1 entity (5 entity-thread rows), of 448 eligible.
    Cause:   COUNT(*) over a table whose grain is (entity, thread),
             labelled "entities". skopos.py:510.
    Detected: 2026-09-11, by this seat, 163 days later.
             Not by the health check, not by the consumer, not by the
             follow-on design written on top of it.
    Direction: favourable to the seat. The error made the instrument
             look five times more productive than it was.
    Standing rule that follows: every count this seat writes carries
             its unit and its denominator.

L-02  2026-03-27 to 2026-04-01  SHIPPED A SELF-CONTRADICTING DOCUMENT FOUR TIMES

    The report asserted "5 scored entities" on line 4 and "0 entities"
    on all five thread lines below. Both numbers on one screen, four
    runs running, nobody -- including the agent generating it -- read
    the document it had just written.
    Standing rule that follows: an artifact this seat emits is read
             back by this seat before it is called output.

L-03  2026-03-27  CHANGED A SCORING KEY WITHOUT MIGRATING THE ROWS KEYED TO IT

    The research-thread list was replaced in code. Five existing rows
    orphaned silently. No error, no marker, no migration. The rows are
    still orphaned today.
    Standing rule: a key change is a migration or an explicit
             supersession marked in place. Never silent.

L-04  2026-03-23 to 2026-04-01  CALLED AN ELIGIBILITY ARTEFACT AN ALIGNMENT RESULT

    The reports are titled "Alignment Report" and say which threads are
    STARVING. What they actually measured was a 24-hour window
    intersected with a dedup rule that excluded everything already
    seen. The threads were not starving; the scorer was not looking.
    No eligible count appeared on any report.
    Standing rule: "nothing fired" and "nothing could have fired" are
             separate lines on every report this seat writes.

L-05  2026-04-03  ELABORATED THE DOCUMENTATION OF A DEAD INSTRUMENT

    Two days after the last run, agents/skopos/README.md gained 45
    lines describing the two-stage design and the Titan-prompt output
    -- an output that had never been produced once. The most detailed
    account of what Skopos did was written after it had stopped doing
    anything, and describes a branch that has never executed.
    Standing rule: documentation of a capability cites the artifact
             that capability produced, or says "never executed".

--------------------------------------------------------------------------
## Conflicts of interest, standing

1. Skopos authored the archaeology of Skopos
   (roles/Skopos/ARCHAEOLOGY_2026-09-11.md). Self-audit. Adverse
   findings only are credible; any favourable reading in it is
   unexamined. Independent pass: SKOPOS-08.
2. roles/Skopos/RESPONSIBILITIES.md section 3 proposes a future job for
   this seat. Section 5 recommends AGAINST revival, which is the
   correction for that interest, not a cancellation of it.
3. This seat has never adjudicated anything and should not be asked to
   until it has a calibrated record. Five entries above, all errors,
   is not a calibrated record; it is a floor.
