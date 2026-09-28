# WP-4 Endogenous state robustness and lineage identity

**Question.** Under persistent registers (no aid), can a lineage founded by a zero-borrowing, self-poisoning donor
evolve reproductive machinery that copies from its own post-execution state? Or does establishment only SORT
founders that were already robust?

**Why it matters.** This is the North-Star question as applied to the W1 establishment barrier: whether the
barrier itself becomes an object of evolution.

**Existing evidence.**
- X-P2-ENDOSTATE: CLEAN_NULL for multi-genome early populations, which were already robust.
- 13 runs do go from poisoned early genomes to robust late ones, but their lineage identity is unresolved:
  Hamming distance cannot tell turnover from replacement, because descendants turn over 58-62/64 bytes
  (X-CONTENT).
- X-P2-LINEAGE replays those 13 runs with lineage tracking; see its SUMMARY.json when read.

**Method.**
1. Read X-P2-LINEAGE.
   - If late robust genomes are in the donor's lineage: localize the modification. Compare the earliest robust
     lineage member's genome with its poisoned ancestor, find the minimal byte change that confers robustness
     (knock-in / knock-out on the ancestor), and classify it with Ananke's T-M3-1 scheme:
     - BOOTSTRAP: a prefix that sets the registers the copy reads;
     - INSENSITIVE: the copy no longer reads those registers;
     - OTHER.
   - If they are not: it was replacement. Run the orthogonal probe below.
2. **Poisoned-founder evolution (LEASED).** Implant zero-borrowing donors (corpus NO_COPY set) under CARRY at
   higher founder counts or lower mutation, so lineages survive long enough to evolve. Measure robustness over
   time, with lineage tags.
3. **CONFIRM** any transition class on fresh seeds before promoting it.

**Resources.** Step 1: LIGHT / LEASED ~1 h. Step 2: LEASED ~3 h.

**Done when.** A declared verdict on whether an endogenous state-robustness transition exists in NPE, with the
mechanism class if it does.
