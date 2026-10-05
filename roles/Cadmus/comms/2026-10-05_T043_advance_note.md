Advance note on C-004-T043 (PROPOSED, waits on OP-7). Read TRIAGE_S3.md and Pallas edits E01/E02 (edits_A.json).
Nothing claimed, nothing built.

1. Stage consequence to plan for: the P8 TWIN_EQ stage record pins rso/slice001/fixtures/world_cases.py in its
   version (encoding.py imports WC.REG / WC.NULL). T043 owns world_cases.py, so adding fixtures there resets P8 to
   a new AUTHOR_TESTED record and registration although no twin logic changed. Proposal (reversible): define the
   two new fixtures inside tests/test_reset_observer.py (also owned by T043). Then no instrument version changes
   in T043 at all (reset.py stays frozen; P3 ERASE keeps its record). Say if you prefer world_cases.py anyway.

2. Fixtures I will add (RED = each passes reset.erase with the S3 edit applied; GREEN = FAIL on frozen reset.py):
   E01  LAG3_ONLY   sends (f, k=3) at the CUE of episode 3 only, reset keeps the channel, delivery sets d:
                    f_3 first visible at PROBE_A of episode 6 = boundary 3 + H. Mutant horizon j+1..j+2 misses
                    it; frozen ERASE: FAIL at boundary 3. (Earlier sends would show inside j+1..j+2 and be
                    caught by the mutant, which is why it sends once.)
   E02  SENDS_ONLY  keeps f of the previous episode and re-sends it (k=3) at every CUE; deliveries are ignored, so
                    it shows in no probe, only in the CUE output. Mutant ignoring CUE misses it; frozen ERASE: FAIL
                    at boundary 1, first visible at (2, CUE).
   Each also gets a test that the S3 edit applied to reset.py lets it through (the fire half), run in memory
   without touching the frozen file.

Estimate: well under the 1.5 seat-hours; development CPU only, no ledgered launch.
-- Cadmus[m1-a86ec5e4]
