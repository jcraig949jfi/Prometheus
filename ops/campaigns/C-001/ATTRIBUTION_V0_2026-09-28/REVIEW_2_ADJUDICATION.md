# Review 2 -- Archaeon's adjudication (2026-09-28)

**Record:**
- claims: REVIEW_2_CLAIMS.md at 49abd0da4;
- review: review2/REVIEW_2.md;
- the reviewer's scripts: review2/*.py (transcript in C:/Prometheus-data/evidence/attribution_v0_2026-09-28/rev2/).

**Reviewer:** an isolated claude-opus-5-5 worker on ubu002, 11:30:29Z-11:45:15Z. It re-executed the frozen VM on the committed
tapes and did not re-run the replay.

**What it confirmed** (checks that could have killed the result and did not):
- material ids follow the taint data flow and are never reassigned by byte matching;
- aligned byte state equals material exactly (0.85/0.85 ... 0.33/0.33), so there are no back-mutations and no relabelling;
- the sample of cells 0..11 is effectively arbitrary (the lineage fills 124-128 of the 128 cells);
- EXECUTED_ONLY 0.889 with an independent seed;
- the X set is 1-minimal in 7/7 tapes and beats a size-matched random graft (0.057).

| claim | reviewer | Archaeon's ruling |
|---|---|---|
| R2-1 | STANDS WITH CORRECTION | **ACCEPTED.** The deep block's 0.0 is REPRODUCED at its own epoch (14,800). It is an unaligned comparison. What is refuted is the READING "complete turnover". At 14,800 the aligned figures are 0.32 of the tape and about 0.67 of the essential loci (one member). Across all 11 capable members at 14,300 the figure is 0.85, not 1.00. Essential-locus shares from 0x00 knockout are upper bounds, because 0x00 is NOP and knocking a locus to NOP cannot detect an essential NOP |
| R2-2 | STANDS WITH CORRECTION | **ACCEPTED.** The WHOLE founder-derived genome shifted (terminal NOP insertion plus tail loss), not the machinery "as a unit". The early offsets are standing variation (up to 11 distinct offsets among 12 members). Only -9 (fixed by 15,500) and then -11 (swept by 16,500) form a sequence. "Fixed-position state is also the wrong unit" is WITHDRAWN: once aligned, state tracks descent exactly, and the fault is the missing alignment (standard positional homology) |
| R2-3 | FAILS | **ACCEPTED; the claim is WITHDRAWN.** NEAR_COPIER -> EXACT_GATED is the founder's own first birth (input 142, epoch 13,955), which writes 00 00 + F[2:]. That is a fixed point of the founder's imperfect copying map, and no executed byte changed. So the founder was not the replicator; its first-generation product was. Gating also recurs after 14,500 (8/20 inputs at 17,300; 6/12 gated at 17,900). What survives: exact isolated self-copy stayed at >= 0.5 of sampled members (median 0.83) while aligned founder material in the essential loci fell from 0.85 to 0.33 |
| R2-4 | 1, 2, 4 with correction; 3 untestable; 5 with correction | **ACCEPTED.** H2 becomes "consistent with inheritance" (specific mutation ids were not stored). H3 is untestable with the committed data; genotypes move between inert, gated and ungated. H5: the origin PASSED THROUGH host execution, but necessity was never tested, and an exact self-copying child existed before the host began |
| R2-5 | STANDS WITH CORRECTION | **ACCEPTED.** The executed set is 66% of the tape on average (50-94%), not "~half". Exact is 0.83. "Input gating lost" FAILS for the lineage: it held only for TH-015's stride sample, counted births not copies, and the 18,400 tape has no exact self-copy. The BLOCK_128 explanation is WITHDRAWN: the founder already reproduced on 15 allowed inputs, and 128 was never necessary. Start-pc dependence is rise-then-fall, not monotone. MATERIAL_ONLY is near 0 by construction |

## Consequences for the attribution instrument
1. **Knockout value matters.** A knockout to one fixed byte cannot detect an essential locus whose value IS that byte. v0's A17
   knockout entries must record the replacement value, and machinery should be estimated with random-value replacement
   (Review 2's ko.py rule: essential if >= 8/16 random replacements abolish births). Added to ATTRIBUTION_V0.md limits.
2. **Alignment before any per-locus comparison.** Per-locus IBD records carry source loci (src_loci), so the material side was
   already alignment-aware. The failure was the analysis comparing state at fixed loci. A per-locus STATE comparison must state its
   alignment.
3. **"The founder is not the replicator."** This is a new distinction the schema should hold. The founder's imperfect copying map
   has a fixed point, and the fixed point, not the founder, is the self-copier. In v0 terms:
   - the founder -> child event is organism production with IBD on loci 2-31 and new constant material at loci 0-1;
   - the child's capability is exact_self_copy;
   - the founder's is not.
   D5T/D7 call the founder -> child event reproduction only if the donor is capable. The founder is capable of BIRTHS (the world's
   0.9-coverage rule) but not of exact self-copy. The record must say which capability the donor holds, because D5T/D7 read "copy
   capability" generically. Recorded as an open representational point, not fixed here.

## Process note
Both reviews found material defects in claims that my own tests and analysis passed. Review 2's decisive move was again EXECUTION:
it ran the founder's first-birth product through the VM and found the fixed point.
