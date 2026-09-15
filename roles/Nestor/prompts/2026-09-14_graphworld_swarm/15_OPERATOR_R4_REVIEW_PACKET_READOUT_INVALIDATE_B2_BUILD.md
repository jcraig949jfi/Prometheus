# 15 -- operator: round 4 test launch 1 review packet; readout ruling (invalidate w13, E fixes reader); B2 interface (E builds)

Issued 2026-09-15 ~02:10 to Nestor-A[m1-449a9e76], conductor, after test launch 1 quiesced. Verbatim below the rule.

---

Write me an external review packet i can cut and paste as ascii

For two questions:

1. The Baseline Readout (Invalidate w13)
Reject B's PASS on w13 and patch the reader.
If the baseline is read low, the "Progress Above Floor" calculation is fundamentally mathematically compromised, making the compression claim an artifact of bad tooling rather than genuine evolution.
 Action: Invalidate the w13 claim. Assign Lane E (The Watchmakers) to immediately fix the baseline readout code and commit a regression test to ensure it doesn't drift again. Once E pushes the fix and the baseline is honest, Lane B must re-adjudicate its w13 elites. If they fall below the 0.95 progress bar, they lose the PASS.
2. The B2 World Interface (Build It)
Yes, B2 must get an observation/action interface.
If ⁠graphworld_b2⁠ cannot host the standard brains (linear, ⁠lut_top⁠, ⁠tt_feat⁠), it is completely isolated from the rest of the simulation. The entire point of Clause B (The Invariance Rule) is to test whether an abstraction evolved in a standard numerical world (like w1 or w4) can survive displacement into a fundamentally different topology like a GraphBLAS/FalkorDB environment.
 Action: Assign Lane E to build an adapter/interface for B2. It needs to map the relational graph state into the standard ⁠uint16⁠ observation vector and translate the standard integer action outputs back into graph mutations. Without that bridge, B2 is dead weight.
Let E build the interface and fix the baseline, then unleash B and C back onto the corrected landscapes.
