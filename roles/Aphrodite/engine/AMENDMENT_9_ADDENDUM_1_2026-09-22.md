# AMENDMENT 9, ADDENDUM 1 -- one meta-tribunal family is unusable, excluded
# by its own positive control, BEFORE any arm was run

Dated 2026-09-22. Written after the Tier-3 artifact was frozen and hashed
(61d6a1370587bfd4..., meta-development complete) and BEFORE any transplant arm
executed. No arm result existed when this was written.

--------------------------------------------------------------------------
THE DEFECT
--------------------------------------------------------------------------

The frozen meta-tribunal catalog contains four families. Running each
family's OWN WITNESS -- the known-correct program -- through the hostile
tribunal gives:

    mt_sum_minus_last          extrap 1.00  stress 1.00  ce 1.00  meta PASS
    mt_gcd_plus_first          extrap 1.00  stress 1.00  ce 1.00  meta PASS
    mt_summod_times_first      extrap 1.00  stress 1.00  ce 1.00  meta PASS
    mt_prodshift_minus_first   extrap 0.22  stress 0.00  ce 0.53  meta PASS

mt_prodshift_minus_first's body is `acc * (v + first)` with init 1. At
tribunal lengths (20-60, and 200) the running product exceeds the declared
value ceiling of 10^40, so the correct program itself returns no value and is
scored wrong. THE FAMILY IS UNSOLVABLE AT TRIBUNAL LENGTHS BY ANY PROGRAM.

--------------------------------------------------------------------------
DISPOSITION
--------------------------------------------------------------------------

mt_prodshift_minus_first is EXCLUDED from the Tier-3A analysis. The exclusion
is made on the POSITIVE/SENSITIVITY control -- a family whose own witness
cannot pass cannot discriminate between arms -- and NOT on any arm's
performance, which did not exist when this was written.

WHAT THE EXCLUSION COSTS, stated plainly rather than buried: the meta-tribunal
catalog was deliberately mixed, with two families whose body kind the donor
had seen and two whose body kind it had not, so that over-specialisation of
the evolved library would be exposed. mt_prodshift was one of the two
UNSEEN-body families. Its removal leaves:

    mt_sum_minus_last        body kind SEEN by the donor
    mt_gcd_plus_first        body kind SEEN by the donor
    mt_summod_times_first    body kind UNSEEN by the donor

So the over-specialisation probe now rests on ONE family instead of two. That
weakens the design, and the report must not claim the over-specialisation
test is as strong as it was designed to be. C6 of the criterion (useful
effect across more than one independently selected family) is still evaluable,
since three families remain.

--------------------------------------------------------------------------
WHAT WAS NOT DONE
--------------------------------------------------------------------------

The value ceiling was NOT raised to rescue the family. Raising it would
change the declared grammar semantics -- immutable under AMENDMENT 9 section
1 -- after seeing that a family failed. The family is excluded instead, and
the design is reported as weakened rather than repaired.

No replacement family was substituted. Choosing a new family at this point,
with the evolved library already frozen and its contents known, would be
selection with knowledge of the artifact -- precisely what section 3a forbids.
