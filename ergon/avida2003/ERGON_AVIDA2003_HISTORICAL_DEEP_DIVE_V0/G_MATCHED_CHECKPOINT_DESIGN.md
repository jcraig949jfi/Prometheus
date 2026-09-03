# G - MATCHED CHECKPOINT DESIGN

## The timescale problem, and the choice frozen here

The directive proposes checkpoints at `T_EQU - 100`, `-50`, `-10` and permits
adjustment "if the actual Avida timescale makes them inappropriate", provided
the change is justified and **frozen before examining any accessibility
metric**. This section is that freeze. No accessibility metric has been
computed at the time of writing.

The recovered lineage makes the ambiguity concrete. EQU appears at
**phylogenetic depth 111**, born at **update 27450**. Those are two different
clocks and they are wildly non-linear with respect to each other: the first 17
depth steps span updates 0-1118, while single later steps span thousands of
updates.

Measured in **updates**, `T_EQU - 100` = update 27350, which on this lineage is
well inside the final depth step - all three proposed checkpoints would collapse
onto one or two genotypes. That is inappropriate.

Measured in **phylogenetic depth**, the checkpoints are well separated and each
names a distinct genotype.

**FROZEN DECISION: checkpoints are defined in phylogenetic depth.**

    checkpoint A   pd 101   ( T_EQU - 10 )
    checkpoint B   pd  61   ( T_EQU - 50 )
    checkpoint C   pd  11   ( T_EQU - 100 )

Justification: depth is the unit in which the historical record is published,
it is the unit in which mutations accumulate, and it is the only one of the two
clocks that yields three separated genotypes. Updates remain recorded for every
checkpoint so the wall-clock separation is never lost.

## Focal genotypes

`g_succ(t)` is read directly from `lineage_of_descent.jsonl` at pd 101, 61, 11.
All three are VERIFIED_EXACT strings.

## Controls

`g_dead(t)` - class `NON_EQU_DESCENDANT_CONTROL`, 3-5 per checkpoint, matched
on as many as possible of: same update window, fitness, genome length, task
count, no EQU, not ancestral to EQU within the observation horizon,
genealogically close.

**These do not exist in any recovered artifact.** See F. Until they are
recovered, G is a design and not a runnable protocol.

The class name is deliberate: they are *not* "dead ends" until descendant
history establishes that status, and with a single case-study population that
status may never be establishable.

## The matched-control estimator, frozen now

Per checkpoint, the contrast is

    delta_X(t) = X( g_succ(t) )  -  median over controls of X( g_dead(t) )

**Median, not mean**, frozen before any metric is computed, because control
sets of size 3-5 are small enough that a single lethal-heavy outlier would
dominate a mean. This is recorded here specifically so it cannot become an
analysis degree of freedom later.
