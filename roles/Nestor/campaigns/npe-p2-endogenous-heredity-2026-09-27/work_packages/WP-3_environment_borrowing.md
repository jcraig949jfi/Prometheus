# WP-3 Environment-borrowing copiers: operand provenance and lineage trajectory

**Question.** Most competent NPE donors (95.7% of the P2 corpus sample) are SELF-free offset-64 block copiers.
They take their own address from never-written zero registers or from aligned immediates, and they only work at
tape offset 0. Can reproduction exploit inherited or environmental computational context instead of encoding all
its machinery in the genome? And does that dependence change as lineages evolve?

**Why it matters.** Block D / North Star. If the environment's reset state plus the tape layout ARE the
self-location machinery, then an "endogenous" transition would show up as lineages that stop depending on them.

Cross-engine precedents:
- Archaeon: 265/265 random exact copiers are gated by an environmental input byte, and one lineage later evolved
  gate independence (delegates/CROSS_ENGINE.md 3.1).
- Tierra: hyper-parasites exploit registers left in another program.

**Existing evidence.** delegates/corpus/CORPUS_ANALYSIS.md (Q1, Q4; 8 annotated representatives;
q4_provenance.json gives the last setter of each register).

**Method.**
1. **Operand-provenance instrument (LENS).** Extend register tracking so that, at each block-copy execution, HL,
   DE and BC each carry a label:
   - ZERO_UNWRITTEN;
   - IMMEDIATE (from the genome);
   - COMPUTED;
   - CARRIED (from a previous execution);
   - PARTNER (written by the partner's execution).

   Add a fail/pass self-test on fixtures.
2. **Census (LIGHT).** Apply the instrument to the corpus sample, first donors, and late genomes of runaway
   lineages. Report provenance shares.
3. **Trajectory (LEASED, with lineage tags from WP-4).** Within lineages, does the ZERO_UNWRITTEN / CARRIED share
   of copy operands fall over time?
4. **Side-1 copiers (102 in the corpus).** What do they exploit (PARTNER writes)?
5. **Hijack fixture (T-EST-6).** Can a partner that plants addresses get itself copied?

**Resources.** Step 1: LENS, ~half a day of careful work. Steps 2 and 4: LIGHT. Step 3: LEASED ~2 h. Step 5: LIGHT.

**Done when.** Provenance shares are measured, a declared trajectory test is run, and the result is recorded as a
graph node with an explicit statement on T-END-4.
