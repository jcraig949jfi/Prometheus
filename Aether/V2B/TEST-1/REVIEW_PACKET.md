# V2-B TEST-1 review packet (advisory, asynchronous)

For: external and fresh-context adversarial reviewers. Self-contained summary: RESULT.md (same directory).
Reviewer independence must be stated by the reviewer: say whether you had repository or filesystem access.

## Claims to attack
1. "prov0 sees content forwarding where the XOR signature did not." Evidence: fwd P3_far 0.125 vs rcv 0.012 and v1 0
   on fresh seeds; 7 hand-worked fixtures; a zero-mismatch per-tick self-check against the physics.
2. "Content in the current laws transforms in place but does not travel."
3. "rcv_add composition is rare (2/256)."

## Questions
1. The self-check proves the shadow agrees with the committed BYTES. Could it still assign the wrong PARENT, with the
   same value but the wrong lineage? (Example: two neighbours proposing the same byte. The observer gives the winning
   slot, so the parent should be right. Can you construct a counterexample?)
2. Composition counts only TRACKED lineages. Should every INIT value become a lineage (dense origins), so that P5
   means "two independent ancestries" rather than "two of our 64"?
3. Is FAR = 3 a fair line, given v1 copies one hop by construction? Should the ruler be "beyond what the law's static
   wiring could reach in one write"?
4. Energy is not a lineage in prov0. Transfers move payload-derived amounts into energy, and energy then steers aim
   (rcv_str). Could content be travelling through energy, invisible to prov0?
5. Is reading the E-011 corroboration (rcv_adr 0.59 vs rcv_add 0.92) as the same partial picture justified, or are
   the two instruments measuring different things?
