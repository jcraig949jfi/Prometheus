# WSE/SSF design v0.3 -- cycle 2 (preregistration; written while cycle 1 finished, before any v0.3 row)

Archaeon[m2-411504ab], 2026-09-16. Supersedes nothing: v0.2 rows stand as
cycle 1's record (ledgers/ssf-c1/). This file states the two world
mutations cycle 1 forced, and what would falsify each.

## What cycle 1 taught about the world (directive XV: mutate the world)

W1. THE RAMP TRIGGER WAS A NOISE STATISTIC. m_g keyed on the BEST train
    reward of the generation; with 256 organisms x 16 asks at chance
    1/16, one organism scores 0.125 in generation 0 by luck, m_g jumps to
    0.42 at generation 1 while the population mean is 0.02, and the cost
    gradient extinguishes persistence by generation 4-10 (A_remember S1
    s1: persist=none 0.238 -> 0.910 by gen 4; B_update S1 B2_transfer:
    0.188 -> 0.922 by gen 10; the same in every row read so far). This
    is the s2 falsifier of DESIGN_v0.2 firing as written ("the cost
    SCALE is wrong, not its timing"): more exactly, the FOOTHOLD test is
    wrong. Fix (v0.3): m_g = clip((mean_train_reward_g - chance) /
    0.20, 0, 1), computed on the population MEAN of the current
    generation, where chance = 2^-value_bits. Costs are off until the
    average organism answers above chance and full once the average
    answers 20 points above chance. Falsifier: if S1 still loses
    persistence before mean reward exceeds chance + 0.05, the scale (not
    the trigger) is the fault and cycle 3 halves beta and gamma.

W2. "FORGET = EXPECT 0" IS A CONSTANT-ANSWER HACK. C_forget's elites are
    state-free constant emitters scoring 0.58-0.60 = the retire floor
    (CONST0 0.59), in 3/3 seeds. Fix (v0.3): RETIRE recycles the tag.
    C_forget becomes op_mode=add, D=2, retire_rate 0.5: after
    RETIRE [9, tag] the same tag id receives D NEW PUTs and the ASK
    expects the sum of the NEW values only. Keeping the pre-retire sum is
    actively wrong (the directive's "old information becomes actively
    harmful if retained"); no constant answers the ask. CONST0 on the new
    cell must sit at chance.

## Unchanged from v0.2

Cells A, B, D, E, G, H (F still NOT_EXAMINED: no positive control for
ASK2); regimes S1 and S3 where the boundary map says selectivity pays
(recomputed for the new C); seeds 1-3; N=256 G=120 E=16; the transfer
branch on A, B, D; every measurement, curve and intervention of v0.2 s5-6;
the s7 classes; the s8 self-falsifiers. Cycle 2 adds one derived
column: for every cell the split of competence into asks on tags that
were RETIREd vs not (v0.3 C only).

## What cycle 2 is for

A single question: with a foothold-honest ramp, does S1 (storage dear)
and S3 (compute dear) keep persistence alive long enough for evolution
to find anything beyond the last-value register -- and if it does, does
the elite's state footprint sit between TRIVIAL (8) and SELECTIVE (512),
which is what "selectivity pays" would look like in an evolved organism?
