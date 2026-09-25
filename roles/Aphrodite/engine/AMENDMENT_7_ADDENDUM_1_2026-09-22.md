# AMENDMENT 7, ADDENDUM 1 -- the scratch control as I declared it makes the
# experiment vacuous

Dated 2026-09-22. Written BEFORE any arm was run and BEFORE any transplant
performance was measured. The organ is already extracted and hashed
(5488abb9f6354f02..., commit 72af932dd), so this addendum cannot have been
shaped by any transplant result.

--------------------------------------------------------------------------
THE DEFECT
--------------------------------------------------------------------------

AMENDMENT 7 section D declares:

    "1 SCRATCH  fresh recipient, no transplanted organ, searching from the
     ORIGINAL grammar (composition + the full fold space)"

That control already contains the fold space. For the selected third family
the fold search space is 2 INIT x 30 E x 1 F = 60 candidates, and the ORGAN
arm's hole space is the SAME 60 candidates. A scratch recipient carrying the
fold grammar is not a no-organ control; it is an organ-bearing arm under
another name, and ORGAN vs SCRATCH would measure nothing but noise.

This is INVARIANT 1 turned on my own experiment: the organ is decorative
relative to a substrate that already contains the fold mechanism. Had I run
it as declared, the null would have been an artifact of my control
definition, not a fact about organ reuse.

--------------------------------------------------------------------------
THE CORRECTION: RUN BOTH CONTROLS, REPORT BOTH
--------------------------------------------------------------------------

I am not swapping one control for a friendlier one. Both are run and both
are reported, because they answer different questions:

  SCRATCH-A  exactly as declared in AMENDMENT 7 section D: composition
             (size <= 4 over the declared primitives) PLUS the full fold
             space, including the trailing choice.
             ORGAN vs SCRATCH-A asks: does FREEZING THE SKELETON and
             restricting search to the holes help, given a substrate that
             already has the fold mechanism? The honest prior is NO, and a
             null here is expected and uninformative about reuse.

  SCRATCH-B  the pre-slice-2C grammar: composition (size <= 4) plus the
             scalar while-helper search, and NO fold space. This is the
             substrate as it existed before the organ was discovered.
             ORGAN vs SCRATCH-B asks the question the ruling actually
             poses: does an evolved structural artifact improve a fresh
             recipient's capacity to acquire a new capability, relative to
             a recipient that does not have that structure at all?

SHAM is unchanged and is run against both readings: it carries the
equal-size decorative `h // h` fossil that failed slice-2C load-bearing, and
searches SCRATCH-B's grammar. If SHAM matches ORGAN, the effect is carrying
scaffolding, not the organ.

The interpretation thresholds from AMENDMENT 7 section F are unchanged and
are applied to ORGAN vs SCRATCH-B: ORGAN's median M1 must be at most half of
SCRATCH-B's median M1, and ORGAN's M2 must be at least as high. The
ORGAN-vs-SCRATCH-A comparison is reported as a separate line and is NOT used
to claim STRUCTURAL_SEARCH_LEVERAGE.

--------------------------------------------------------------------------
WHAT A REVIEWER SHOULD CHECK
--------------------------------------------------------------------------

That this addendum is committed before the arms ran (it is: the run script
does not yet exist at this commit), and that SCRATCH-A is reported with the
same prominence as SCRATCH-B even though it is expected to be null. If only
the flattering comparison appears in the final packet, the correction was
drift after all.
