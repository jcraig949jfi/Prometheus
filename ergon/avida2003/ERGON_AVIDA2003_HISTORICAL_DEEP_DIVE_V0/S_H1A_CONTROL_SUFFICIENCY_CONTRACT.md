# S - H1A CONTROL-SUFFICIENCY CONTRACT

**FROZEN 2026-09-03, BEFORE any candidate control artifact has been opened.**
At the time of writing, no population file, no `detail-*.spop`, and no
contemporary genotype from the historical experiment exists on this machine.
The archive retrieval that might produce one is running and has not returned.

This document exists so that the archaeology cannot silently redesign H1A
around whatever happens to survive. If the recovered artifacts do not satisfy
this contract, the correct outcome is that H1A stays blocked -- not that the
contract is relaxed.

---

## 1. What H1A needs

For each of the three frozen checkpoints (`pd 101`, `pd 61`, `pd 11` -- depth,
not updates, frozen in G), a comparison between:

    g_succ(t)   the ancestor on the line of descent at that depth
    g_ctrl(t)   3 to 5 contemporary genotypes of class
                NON_EQU_DESCENDANT_CONTROL

## 2. Minimum information a control artifact must carry

A candidate artifact is SUFFICIENT only if, for each control organism, it
yields all five of:

    C1  genome sequence over the verified 26-letter alphabet
    C2  a contemporaneity coordinate (update, and phylogenetic depth if present)
    C3  fitness, or merit and gestation time from which fitness is computable
    C4  genome length (derivable from C1, so C1 satisfies this)
    C5  task/phenotype vector, or enough execution context to compute it with
        the historical evaluator

If C1 is absent the artifact is USELESS for H1A: without the sequence there is
no mutational neighbourhood to enumerate.
If C5 is absent but C1 is present, the artifact is CONDITIONALLY SUFFICIENT --
usable only once a validated historical evaluator exists (see the build
workstream), because the task count is a matching dimension.

## 3. Matching dimensions and tolerances

Frozen now, before any data is seen.

| Dimension | Rule | Tolerance |
|---|---|---|
| contemporaneity | **UPDATE**, not phylogenetic depth | control's birth update within +/- 5% of `g_succ(t)`'s birth update, or within the same update window if the artifact is a periodic dump |
| fitness | relative to `g_succ(t)` | within a factor of 2 (i.e. ratio in [0.5, 2.0]) |
| genome length | absolute | within +/- 3 instructions |
| task count | absolute | exactly equal, else within 1 if no exact match exists |
| EQU | control must NOT perform EQU | hard exclusion, no tolerance |
| descendancy | control must not be ancestral to any EQU-positive organism within the observation horizon | hard exclusion where descendancy is recorded; if descendancy is NOT recorded the control is admitted with class `NON_EQU_UNKNOWN_DESCENDANCY` and this is reported as a limitation, not hidden |

**Why contemporaneity is measured in UPDATES here while checkpoints are in
DEPTH.** Depth is a property of the *lineage* and is undefined for an
unrelated contemporary. The checkpoint is *selected* by depth; the controls are
*matched* by update, using the birth update recorded for that depth in the
lineage table (pd 11 -> update 734, pd 61 -> update TBD from the table, pd 111
-> update 27450). This is the only coherent joint definition and it is frozen.

## 4. Selection procedure

1. Filter all organisms in the artifact to those satisfying every hard
   exclusion in section 3.
2. Rank survivors by a deterministic distance:
   `d = |log2(fitness ratio)| + |len diff| / 3 + |task count diff|`
3. Take the 5 smallest.
4. Tie-break by lowest organism identifier in the artifact's own ordering --
   never by anything computed from the accessibility metric.

## 5. What happens at the boundaries

| Condition | Action |
|---|---|
| more than 5 qualifying controls | take the 5 nearest by the section-4 distance. Do NOT take all of them: the frozen estimator is the median of 3-5 and changing n changes the estimator. |
| exactly 3 to 5 | proceed |
| fewer than 3 at a checkpoint | that checkpoint is **DROPPED** and reported as dropped. It is not rescued by widening tolerances. |
| fewer than 3 at ALL THREE checkpoints | H1A remains blocked. Report `H1A_HISTORICAL_CONTROLS_UNRECOVERABLE`. |

## 6. Awkward cases, decided in advance

| Case | Decision |
|---|---|
| duplicate genotypes (same sequence, multiple organisms) | collapse to ONE control. Duplicates are the same point in genotype space and would fake independence. |
| organisms differing only by a neutral genotype change | treated as distinct controls ONLY if their sequences differ. Sequence identity is the criterion, not phenotype identity. |
| extinct lineages | ADMISSIBLE and in fact preferred -- an organism that left no descendants is the cleanest non-EQU control |
| EQU-positive organisms | EXCLUDED from controls. Separately retained as the N5 control set (post-EQU), which exists to test kill criterion K9. |
| organisms from a DIFFERENT population | **NOT POOLED.** Controls must come from the same population as `g_succ`. Pooling across populations would confound population-level differences with the precursor signal. |
| pooling across populations, ever | Only if multiple independent populations are recovered AND each yields its own complete control set, in which case each population is analysed separately and results are reported per population. Never pooled into one comparison. |
| the artifact is a periodic dump not containing the exact update | use the nearest dump at or before the checkpoint update, and report the offset |

## 7. What this contract forbids

- Widening a tolerance after seeing how many controls qualify.
- Substituting phylogenetic depth for update contemporaneity because depth is
  more convenient.
- Using organisms from a reconstruction run as controls. Those are
  RECONSTRUCTION CONTROLS and belong to a different experiment (H1B), never to
  H1A.
- Reporting a checkpoint with fewer than 3 controls.

---

*Frozen by Ergon, 2026-09-03, before any control artifact was opened.*
