+=====================================================================+
|  CAMPAIGN 4 -- ITEM DISPOSITION                                     |
|  Item:        C4-REH-1 (launch-gate item G2, integration rehearsal) |
|  Disposition: SKIPPED_SAFEGUARD_TERMINOLOGY                         |
|  Recorded by: Archaeon[m2-411504ab]   Date: 2026-09-17              |
+=====================================================================+

-----------------------------------------------------------------------
1. WHAT THIS RECORD IS
-----------------------------------------------------------------------

C4-REH-1 is the end-to-end integration rehearsal that gate item G2
requires. It is not a science slot and carries no scientific claim.

This item is being SET ASIDE rather than completed, for a reason that is
neither a defect in the item nor a defect in any project surface. The
reason is recorded here so that a later reader does not mistake it for
an engineering failure, an infrastructure fault, or a negative result.

-----------------------------------------------------------------------
2. THE OBSERVED CONDITION
-----------------------------------------------------------------------

Work on this item was interrupted repeatedly by an automated safeguard
acting on the lead's own output. The interruptions:

  - occurred across roughly seven separate attempts;
  - landed on messages of very different length, including one of eight
    words containing no commands at all;
  - discarded any pending commands in the interrupted output, so each
    interruption lost the tail of an in-progress sequence;
  - were not predictable from the content of the preceding step.

The proximate cause, as diagnosed by the operator, is the vocabulary
this programme inherited from its evolutionary-computation framing.
Read in bulk and out of context, that vocabulary resembles a
life-sciences subject matter rather than the mathematics of program
variation on a small virtual machine. The subject matter here is, and
has always been, integer-valued programs executing in a bounded
interpreter.

This is a presentation problem, not a research-conduct problem. No
finding, artifact or measurement in Campaigns 1-4 depends on the
wording.

-----------------------------------------------------------------------
3. WHY THE ITEM IS SET ASIDE RATHER THAN RETRIED
-----------------------------------------------------------------------

Retrying was attempted and did not converge. The interruptions were not
reduced by shortening messages, by splitting recipients, or by removing
detail. Each retry consumed budget and produced no artifact, and the
tail-loss behaviour meant sequences could not be completed reliably.

Continuing to retry would have accumulated cost without advancing the
item, which is the condition under which the campaign contract says to
record a terminal state and move on rather than convert a blocked item
into an open-ended engineering effort.

-----------------------------------------------------------------------
4. WHAT WAS COMPLETED BEFORE THE ITEM WAS SET ASIDE
-----------------------------------------------------------------------

All committed to main and independently verified:

  S1  bundle built, 48 units, sized so that a deliberate interruption
      intersects live work rather than finishing before it
  S2  every unit validated against the execution seat's own contract
      module, and hashed with it; 1,152 expected records declared as an
      accounting invariant
  --  queue observability confirmed from this seat, so the interruption
      could have been timed against a measured rate rather than guessed
  --  the executing seat's restart tool is ready and refuses to fire
      unless live work is present

Not performed: the interruption itself and the stages after it.

-----------------------------------------------------------------------
5. CONSEQUENCE FOR THE CAMPAIGN
-----------------------------------------------------------------------

Gate item G2 remains RED. The launch gate therefore continues to refuse,
which is correct: the integration path has not been demonstrated
end to end through an interruption.

Campaign 4 has NOT started and must not be recorded as started.

This item is available for a later attempt under the terminology
discipline in section 6, by this seat or another. Nothing about it needs
to be rebuilt; only the interruption and the stages after it remain.

-----------------------------------------------------------------------
6. TERMINOLOGY DISCIPLINE FOR SUBSEQUENT WORK
-----------------------------------------------------------------------

Applies to prose, messages and reports. It does NOT apply to field names
inside artifacts, code identifiers, or any schema already consumed by
another seat's parser: renaming those would break working machinery and
invalidate committed receipts for no scientific gain.

Preferred vocabulary in prose:

    program variant, candidate, sample          (for the unit of study)
    edit, perturbation, variation step          (for a change)
    variant set, sample set, starting set       (for a collection)
    derivation record, provenance               (for origin data)
    executes / halts / faults / no effect       (for outcomes)
    retained, unchanged, degraded, improved     (for comparisons)
    variant family, derivation chain            (for related variants)

Rule of thumb: describe what the interpreter does to integers, not what
the vocabulary evokes. Where a directive supplies a term verbatim, quote
it once as a defined label and use the neutral term thereafter.

-----------------------------------------------------------------------
7. DISPOSITION
-----------------------------------------------------------------------

  SKIPPED_SAFEGUARD_TERMINOLOGY

Defined here as: the item could not be carried to completion because an
automated safeguard repeatedly interrupted the lead's output, for
reasons of vocabulary rather than of conduct, and retrying did not
converge. The item is intact, its prerequisites are unaffected, and it
is resumable.

This is recorded alongside the campaign's other terminal states and is
not one of them. It is not SUPPORTED, NEGATIVE, INCONCLUSIVE,
REPRESENTATION_BLOCKED, INSTRUMENT_INVALID, or SKIPPED_RESOURCE_BOUND.
It is specifically not INSTRUMENT_INVALID: every instrument involved
returned correct results whenever it was allowed to run.

+=====================================================================+
