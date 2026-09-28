# WP-7 Tape-rotation world: withdrawing the self-location scaffold (Thread T-LOC-1)

**Question.** NPE copiers almost never locate themselves. All 280 of 280 SELF-free competent copiers in the transplant study
copy between absolute tape addresses, and fail when moved by 16 bytes or more. If the world no longer supplies fixed placement,
two things are unknown: do copiers still arise and establish, and do true locators (explicit self-location plus relative
destination; 2 known genomes, seed 16000026) appear and win?

**Why it matters.** This is the self-location half of ARC3's central question: can a lineage internalize a function the
environment supplies? Register initialization already turns out to be commonly internalized (182/332 copiers are
"state-free"); self-location, so far, is not.

**Design (LENS then LEASED-M1).**
1. **World axis "placement rotation".** Before each pair interaction, draw r uniformly from the tape size, rotate the
   tape contents by r, run both organisms from their rotated start offsets, then rotate back.
   - Code that addresses relative to itself or its PC is unaffected.
   - Absolute-address code is broken.
   - Implement as a runner subclass that wraps `_pair_interact` (never edit frozen world.py), passing the rotated tape
     through the same z8 calls.
2. **Fail/pass self-test.** A known tape-anchored copier (any corpus SELF-free copier) must lose competence under rotation.
   The true-locator genome from seed 16000026 (see delegates/selflocation/trace_locator.txt) must keep it.
3. **Arms.** Random populations on the dense VM, in the CARRIED and ZERO worlds, each with and without rotation. Measure
   acquisition, establishment, and the architecture class of first donors (transplant classifier in
   delegates/selflocation/selfloc.py).
4. **Competition.** Implant one true locator plus one tape-anchored copier together, with and without rotation.

**Rulers.** Fair entry-state competence (x_a3_fair/run_fair.py ENTRY battery); competence must be assayed under the
same rotation policy as the world.

**Done when.** The graph has nodes answering:
- whether rotation abolishes acquisition;
- whether true locators arise spontaneously when placement varies;
- whether, in competition, locators beat anchored copiers under rotation.
