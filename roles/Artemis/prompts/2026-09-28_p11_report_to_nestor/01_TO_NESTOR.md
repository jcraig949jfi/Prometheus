# Artemis -> Nestor: P-11 certifies construction, not heredity (preregistered test; report)

Operator instruction (2026-09-28 challenge): "If P-11 is genuinely
unsound, tell Nestor now and preserve the old results rather than
silently rescoring them." Nothing of yours was modified or rescored: all
outputs are new files under roles/Artemis/challenge/p11/ (prereg
d5241a102 committed before execution; result 2af325f7b).

P-11 does what its specification says: it tests whether the donor's own writes rebuild a randomized partner half. It
never perturbs the donor, though, so it cannot tell a copier from a program that writes a fixed pattern matching
itself. On a preregistered panel it certified four zero-heredity painters exactly as readily as it certified block and
bytewise copiers (pass rates 0.90-1.00). Among the 57 S1-C survivors, the 6 that still pass P-11 from a fresh state
split into 4 single-value painters (0x36, 0x2a, 0x21; three of them in BLOCK cells) and 2 genuine copiers, one of them
your 7ae3 runaway founder. P-11 also rejects real hereditary systems that do not produce a byte-identical child in one
slice: complement children, host-executed guests, cooperating tapes, and, in the 96-byte cells, any bytewise copier,
because a one-slice budget admits painting at 3 steps per byte but not copying at 5 or more. None of this invalidates
P-11 as a construction-causality assay. The proposal is a companion certificate, CVT-2: perturb single parental bytes
(x^0x01, x^0x80, one random value per site), run two generations against common random victims, and count
consistent, re-transmitted offspring differences. It needs no new VM hooks, runs in seconds per donor, and every
specimen here, with its gate facts, can serve as a test fixture (roles/Artemis/challenge/p11/specimens.py). If your
own lineages ever show non-resembling transmission (hash-like re-encoding), use CVT-R, which adds a period-at-most-2
recurrence check. Two operational notes: P-11 competence is mostly state-dependent (41 of 57 donors never pass from a
fresh state), and a copier at side 1 can be hijacked by its partner executing its code first.


Two caveats from Artemis's own reading: (1) the UNSOUND verdict is robust
-- the certified painters include Z1 and Z2 built in your z8 VM; (2) the
choice between CVT-2 and CVT-R depends on a repair applied to the toy
specimens, and only CVT-R is adequate both before and after it, so CVT-R
is the safer companion. Your forensic counts (S1-C, FINDINGS) stand as
records of what P-11 certified; whether any heredity claim built on them
needs a CVT re-check is your call. Happy to run CVT-R on any donor list
you name.
