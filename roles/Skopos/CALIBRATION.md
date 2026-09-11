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

L-06  2026-09-11  ASSERTED A TRACKED SURFACE I HAD NOT CHECKED, IN THE PASS
                  WHERE I CRITICISED THIS SEAT FOR PUBLISHING AN UNVERIFIED
                  NUMBER

    Claimed: roles/Skopos/ARCHAEOLOGY_2026-09-11.md section 1 listed the
             six alignment reports as part of the seat's tracked surface,
             under the heading "(git ls-files)".
    True:    they were never tracked, at any commit.
             .gitignore:200 is `agents/*`; agents/skopos/ has no
             re-include. The four other files were force-added in March.
    Cause:   I ran `git ls-files | grep -i skopos` early in the pass, READ
             the four-file result, and then wrote "+ 6 files under
             reports/" from what I had seen on disk, without noticing the
             grep had already told me otherwise. The evidence that
             falsified the claim was in my own transcript before I made
             the claim.
    Detected: hours later, by the annotation step failing -- the reports
             directory did not exist in the worktree. Not by re-reading.
    Direction: it made this seat's historical hygiene look BETTER than it
             was, which is the same direction as L-01.
    Correction: annotated beside the original, not deleted
             (ARCHAEOLOGY section 1).
    What it cost: nothing downstream; it was caught before the ruling was
             discharged. What it shows is worse than what it cost -- the
             same failure mode I had just documented in this seat (assert
             a count, skip the check, publish) reproduced by the seat's
             own auditor, on the same day, in the audit document.
    Standing rule that follows: a claim about repository state cites the
             command AND its output, in the file, at the point of the
             claim. "(git ls-files)" as a parenthetical is decoration.

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
