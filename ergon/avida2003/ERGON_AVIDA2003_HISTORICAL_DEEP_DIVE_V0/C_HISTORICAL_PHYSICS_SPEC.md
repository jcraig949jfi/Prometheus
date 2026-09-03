# C - HISTORICAL PHYSICS SPEC

What the world was, to the precision the evidence supports. Certainty classes
in E; this document states the physics and flags where it is version-skewed.

## Substrate

Self-replicating programs on a 2D grid, competing for CPU time. A genome is a
string over a **26-letter instruction alphabet** (VERIFIED_EXACT: the
supplementary table and `inst_set.default` agree instruction-for-instruction
and in order). Replication is by explicit `h-alloc` / `h-copy` / `h-divide`
head operations, so self-replication is encoded in the genome and can be
broken by mutation.

## The rewarded phenotype

Nine Boolean logic tasks, rewarded once each (`requisite:max_count=1`):

    NOT  NAND  AND  OR_N  OR  AND_N  NOR  XOR  EQU

To be credited with a task an organism must return the correct value for **all
32 bit-wise problems** in the series (supplementary II). Partial credit does
not exist. This is a sharp threshold and it matters for any accessibility
metric: the phenotype is a 9-bit vector with no intermediate states.

**ECHO is describable but not rewarded.** The supplementary lists it among the
one-input operations; it appears in neither the nine-function legend nor
`environment.cfg`. Any reconstruction that rewards ECHO is not this specimen.

## The reward function

`environment.cfg` gives each reaction `process:value=v:type=pow`. The nine
values are

    NOT 1   NAND 1   AND 2   OR_N 2   OR 3   AND_N 3   NOR 4   XOR 4   EQU 5

and they are **exactly** the minimum number of NAND operations required to
compute each function, as published in supplementary II and stated there to
have been proven by exhaustive search. Merit multiplier is therefore 2^v, so
EQU is worth 32x and the nine rewards span a 32-fold range.

This identity - reward exponent equals minimal NAND depth - is the single most
important piece of physics recovered in this pass, because it means the reward
landscape is a **computational-depth ladder**, not an arbitrary bonus schedule.

## Selection

Merit multiplies replication rate; organisms compete for CPU cycles. A genome
that performs a rewarded task replicates faster and displaces neighbours. The
paper's central point is that intermediates on the path to EQU were sometimes
individually deleterious, which is visible directly in the recovered lineage:
of 111 transitions on the line of descent, many carry relative fitness below
1.00.

## Version skew - stated, not hidden

Everything in the two config files above is `VERIFIED_EXACT` **for Avida 2.2
(2005-02-14)**. No 2003-era source or configuration has been recovered. The
supplementary independently confirms the instruction set, the nine tasks, the
32-bit credit rule and the minimum-NAND values, which is why those rows are
promoted to VERIFIED_EXACT for 2003. The functional form `type=pow` and the
`max_count=1` requisite are confirmed only for 2.2.

## What is NOT specified

Population size, world geometry, point/insertion/deletion/copy mutation rates,
replicate count, seeds, and the Avida version itself. See E. A faithful re-run
is therefore not currently possible and any re-run would be
`APPROXIMATE_RECONSTRUCTION`.
