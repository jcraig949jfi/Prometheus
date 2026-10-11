# NS-02 -- justified by NS-01 (proposal; not started; needs operator go)

## Question
Does adding an experimentally characterised failure (F15 candidate) to the archive measurably change what each arm
proposes -- and can exclusion reward causal novelty instead of imperfection?

## Changes motivated by NS-01 evidence
1. De-saturate the signature (NS-01 defect 2): add intervention axes measured on every candidate, independent of task
   success: (a) dose-response of readout excess to corrupting a fraction q in {.1, .3, .5} of state coordinates at
   t = 1; (b) dose-response to extra state noise; (c) symmetry probe: excess after a random permutation of state
   coordinates within the mechanism's declared groups (none -> skip); (d) capacity probe: two cues at t = 0 and t = 1,
   decode both. Requalify the engine (disguises + look-alikes) BEFORE use, with new look-alike pairs drawn from NS-01's
   collapsed perfect memories (e.g. A02 isometric rotation vs A05 S4-coset vs B07 Toom CA vs C05 winding number): pass
   only if >= 4/6 such pairs separate.
2. Exclude on causal organisation, not viability (defect 1): C's signal reports equivalence classes from the
   de-saturated signature only; a perfect memory is rejected only if its intervention profile matches a witness.
3. Archive v2 = NS-01 tier M + M-RELATIONAL (F15 candidate; witness W-REL) + the 7 NS-01 reproducibly distinct
   behaviours as additional witnesses. Freeze before generation.
4. F15 capacity scaling: DONE in NS-01 (KEEP_DISTINCT, slope 1.6). NS-02 extends it to a second relational family and
   a structured decoder; original plan was: decodability of W-REL vs decoder width {256..8192} x pairs M {1, 2, 4, 8, 16, 32, 64}
   x n_train {1k, 4k, 16k}. Decide: if required capacity grows at most linearly in M -> MERGE F15 into decoder-class
   dependence (KNOWN); if super-linearly -> keep as a distinct class (relational dilution).
5. The learning test (directive s12): rerun all four arms (8 each, fresh conversations) with archive v2; primary
   comparison per arm = fraction of proposals in the NEW class vs NS-01; plus whether B/C proposals move away from
   relational encodings once F15 is listed (anchoring vs avoidance). Two independent runs per arm (replication).
6. Different priors (defect 3): add an arm E with a different model (Haiku 4.5) under the Arm C protocol, and a D'
   grammar extended with relational / gauge primitives (to test whether D can reach F15 at all).

## Budget
~6 h CPU on ubu003, $0, ~1.2M generation tokens (2 runs x 5 arms x 8). Same supervisor, same separation rules.
Kill rule: if after NS-02 no arm yields a reproducibly distinct, intervention-separated new class and the archive
addition does not change any arm's proposal distribution by >= 2/8, report that archive-driven redirection is not
supported at this scale and stop the line.
