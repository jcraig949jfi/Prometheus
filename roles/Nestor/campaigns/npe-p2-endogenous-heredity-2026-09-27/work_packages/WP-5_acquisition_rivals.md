# WP-5 Acquisition rivals: presence, density, byte distribution, random-walk baseline

**Question.** C-DENSE-COPY showed that a one-byte copy alias raises spontaneous donor acquisition from 1/64 to
39/64. Which property does the work? The candidates:
- the copy instruction's PRESENCE in random material;
- the soup DENSITY of block writes;
- the INFORMATION COST of the encoding (8 bits);
- the MUTATIONAL REACHABILITY of the encoding under each cell's mutation topology;
- the pair-tape soup being a worse SEARCH than a random walk.

**Existing evidence.**
- X-P2-ATTRIB: donors' competence runs entirely through the alias, 372/372.
- X-P2-SHAM (same 1-byte block-write density, no usable copier) and X-P2-PLANT (2-byte copy planted in every
  initial genome): see their SUMMARY.json files when read.

**Method.**
1. **Byte-distribution tuning (T-ACQ-3, LEASED).** Keep ED B0. Raise P(0xED) and P(0xB0) in the initial and
   mutation distributions until the per-program probability of the ED B0 pair matches the one-byte alias's
   per-program probability. Compare acquisition with W1 DENSE on paired seeds.
2. **Mutational reachability (T-ACQ-5, REPO/LIGHT).** Compute exactly the per-generation probability that one
   mutation creates ED B0, ED B8, E5 or E7 at an executable position, for Z8_64 (per byte, frame shifts) and
   Z8_SLOTTED (slot-aligned, OPERAND operator: opcode slots never mutate). Check against a census.
3. **Random-walk and uniform baselines (T-ACQ-4, LIGHT).** Count programs tested to the first COMPETENT donor
   under uniform bytes, the soup's empirical byte distribution, and mutation walks, on stock and dense VMs.
   Compare with the soup's programs-to-first-donor. Report hazards (T-ACQ-7).
4. **SELF alias vs copy alias (T-ACQ-6, LEASED).**

**Resources.** Steps 1 and 4: LEASED ~1.5 h each. Steps 2 and 3: LIGHT.

**Done when.** Each rival has a declared verdict, and the acquisition claim in FINDINGS is rewritten with the
mechanism that survives.
