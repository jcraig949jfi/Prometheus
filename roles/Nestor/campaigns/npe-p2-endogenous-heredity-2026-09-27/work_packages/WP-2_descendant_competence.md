# WP-2 Descendant-competence failure: S2 -> S3 and S4 -> S5

**Question.** In X-P2-BRIDGE the stage chain loses the most between S2 and S3, and between S4 and S5:
- S2 -> S3: a certified causal copy is made, but no competent descendant ever appears.
- S4 -> S5: a descendant makes its own certified copy, but the lineage never runs away.

Where exactly does each fail?

**Why it matters.** Block E. "Copying succeeds but the child inherits unusable state" is a different failure from
"the child is competent but never reaches the right execution context". The two need different fixes and point
to different endogenous transitions.

**Existing evidence.**
- x_p2_bridge/results/*.json: per run S1-S4 epochs, founder copy ages, births_L / causal_L.
- The P-11 break rate is ~5-16% per edge (X-CERT-BREAK).
- In the world, a child's slot keeps the overwritten organism's registers.
- The founder's side matters: corpus Q4 finds 1,052 copiers that work on side 0 only.

**Method.**
1. **Child autopsy (LEASED, ~100 runs, x_p2_bridge runner).** Hook each certified birth from the founder and
   record:
   - the child genome's fresh-start competence (cached);
   - its copy rate from the state it will actually start with (the victim's carried registers; run_nc.copies);
   - its side at its next execution;
   - its survival to its next execution.

   Classify each failed S3 as:
   - STRUCTURAL: the child genome is not competent;
   - STATE: competent fresh, but not from its inherited registers;
   - CONTEXT: competent from its state, but dies or is paired on the wrong side before copying.
2. **S4 -> S5 (branching).** Estimate children per copier per epoch and child copy capacity (XE-EST-1, T-EST-4).
   Test whether a branching model with the measured rates predicts the S5 shares.
3. **Who-inherits-state arms (T-EST-5).** At a replication event the child gets:
   (a) its slot's old registers (current);
   (b) zeros;
   (c) the donor's post-run registers.

   The parent keeps its own registers in all three.

**Rulers.** As above; declare the classification thresholds before running.

**Controls.**
- Fixtures with a known child outcome.
- A replay check against recorded depth.
- Self-tests for the inheritance arms.

**Resources.** Step 1: LEASED ~1.5 h. Step 2: LIGHT. Step 3: LEASED ~2 h.

**Done when.** Each failed S3/S5 run is assigned a mechanism class, and the dominant class is stated with its share.
