# Theseus v0 preregistration -- AMENDMENT 1 (run v0_1)

Currency: 2026-09-30. Committed AFTER run v0_2026-09-30 (result b63ae617f,
H1 FAIL) and BEFORE run v0_1_2026-09-30. Code hashes:
CODE_SHA256_AMENDMENT_1.txt.

## Why

The v0 run exposed four defects (calibration ledger rows of 2026-09-30):
1. evolved lenses (generation-0 synthetic roots) were eligible parents in
   the DEEP and VERY_DEEP lanes, so arm D contained generation-1 children
   and overlapped arm E;
2. coalition pools iterated a Python set, so the ecology depended on
   PYTHONHASHSEED and was not reproducible from the master seed;
3. lensDependencies was inherited through ancestry, not measured;
4. VISUAL_EXPORT was silently empty, and arm rows (P, B, C genomes and
   viability) were not exported, so H1 could not be recomputed from
   committed rows alone.

## What changes (correctness and export only)

1. entities.eligible: kind "lens" is never a DEEP or VERY_DEEP parent; a
   lens enters only through the DEEP_LENS lens slot.
2. ecology: every pool that feeds an RNG draw is sorted; the run is
   launched with PYTHONHASHSEED=0.
3. lensDependencies = lenses the genome executes (lensmap rules present);
   inherited lens ancestry moves to metadata.lens_ancestry. "Requires
   evolved lens L" is still only stated from a measured held-out drop.
4. VISUAL_EXPORT takes ecology candidates and asserts non-empty; all arm
   rows are exported to theseus/controls/arms_<tag>.jsonl.

## What does not change

Substrate, compiler, collision engine, battery, viability gates, rulers
and calibration procedure, known library, dark gate, lens admission, all
budgets, the H1 decision rule, validity gates, and P1-P9 scoring code.

## Status of v0_1 and one new prediction

v0_1 is a corrected REPLICATION of v0 under a different effective random
stream (set order changed), not a second chance for H1: v0's FAIL stands
as recorded. If v0_1 disagrees with v0, both are reported and the
disagreement is the finding (seed variance of H1; backlog THESEUS-20).

P10 (made now, having seen v0): H1 is FAIL again in v0_1.       p = 0.8
