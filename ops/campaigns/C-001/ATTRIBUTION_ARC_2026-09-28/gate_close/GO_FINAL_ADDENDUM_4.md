# GO_FINAL addendum 4 (2026-09-29): ruling on s4 v2.2 item V5 (loci with no usable dependence draws)
**Context:**
- Nestor #940: the s4 v2.1 review returned DOES NOT CONFORM from 2 of 2 fresh replicas (tsk-5b65fada2d69, tsk-6e51a53bfbf6);
  the blocking finding was B1 = Archaeon #933 (C4.4).
- s4 v2.2 was posted BEFORE running (17670fed... @ b0f215348).
- Its tallies stay unused until 2 further fresh replicas return CONFORMS.

**V5 question:** 22 self-class loci satisfy R1 condition 1 (ENTITY MOVE), but have NO usable dependence draws: every draw
suppressed the write, which counts toward Q8c-whether (R1.3). Are they "rule-identified" candidates in the flip-coverage
denominator?

**RULING: the literal text applies.**
- R1.3 reads "changes that locus's value in 0 of K draws", with suppressed draws counting elsewhere. With zero usable draws it is
  satisfied vacuously (0 changes).
- So these loci stay in the coverage denominator.
- The variant that excludes them is reported as a DIAGNOSTIC only. It does not gate.
- The vacuous case is a SPEC GAP: R1 did not anticipate a locus whose every intervention suppresses its own write. It is
  recorded for the independent final reviewer and for a future prereg version.
- It is NOT repaired after exposure.

This changes no threshold, key, sample or K. It chooses the text over a post-exposure alternative.
