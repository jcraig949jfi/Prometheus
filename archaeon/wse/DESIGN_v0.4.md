# WSE/SSF design v0.4 -- cycle 3 (preregistration; written during cycle 2, before any v0.4 row)

Archaeon[m2-411504ab], 2026-09-16. Cycle 2 rows stand in ledgers/ssf-c2/.

## What cycle 2 taught (first six rows read at 21:05 UTC; the rest are read
## after this file is committed and cannot change it)

W3. THE MEAN-KEYED RAMP WORKS AS A TRIGGER; THE COMPUTE COEFFICIENT IS THE
    KILLER. B_update S1 B2_transfer s1: m_g = 0 for generations 0-4 while
    the transferred register solvers lifted the population mean to 0.128
    (their last-value reward ~1/(Kd+1) + chance); m_g rose to 0.33 at
    generation 5; the solvers burn their whole tick budget every tick
    (elite 13,600 ops/episode at gen 3 = 256 x 53 ticks), so alpha =
    0.02/kop x 13.6 kop x 0.33 = 0.09 against a reward edge of ~0.12;
    persist=none organisms (2-50 ops) took over by generation 20, the
    mean fell to 0.004, m_g returned to 0, and nothing was left to select.
    The v0.3 falsifier says: the mean DID exceed chance + 0.05 before the
    loss, so the trigger is right and the SCALE is wrong -- specifically
    alpha, which charges wasteful looping before evolution can learn to
    HALT. Storage (beta) was not the term that killed them.
W4. NAIVE POPULATIONS FIND NO FOOTHOLD EVEN AT ZERO COST. C_forget S0
    B1_naive (no cost at all, 120 generations, N=256): NO_ADAPTATION, as
    every naive row of cycle 1 and 2 so far. The stream world (Kd
    distractors, kind dispatch, tag discrimination) is a harder needle
    than v01's W0, which itself was found in 2/3 seeds. Search, not
    economics, is the binding constraint for de-novo lineages on this
    substrate (v01 Shape D again).

## Cycle 3: separate search from economics (two arms, three cells)

Cells A_remember, B_update, D_bind2 (the three with a transfer branch).
  ARM 1  SEARCH FLOOR. B1_naive at S0 (no cost) with N=512, G=200, E=16,
         seeds 1-3. Question: does a de-novo lineage EVER get a foothold
         (mean reward > chance + 0.05, or held-out >= 0.3) on the stream
         world at 4x the evaluations of cycle 1? If not in 9 rows, the
         de-novo route is declared search-limited at this budget and the
         program's next move is a substrate question (representation:
         opcode = word mod 25 on random words), not another world.
  ARM 2  ECONOMICS ON A LIVE LINEAGE. B2_transfer at S1' = (alpha 0.002,
         beta 0.05, gamma 0.02), mean-keyed ramp (non-monotone: recorded
         as a property -- a collapsed population gets its costs back off
         and may re-find a foothold), N=256, G=200, seeds 1-3. Questions:
         (a) do the transferred register solvers SURVIVE the ramp now that
         compute is cheap (persist share of the elite lineage stays
         non-none past generation 40)? (b) does the lineage LEARN TO
         HALT (ops/episode falls while reward holds) -- the cheapest
         selective-state adaptation available; (c) does anything exceed
         the last-value plateau 1/(Kd+1) on held-out episodes (tag
         discrimination), which would be the first evolved SELECTIVE
         behaviour in this program; (d) learning-curve slope over the
         last three curve points.
Predictions written to be lost: ARM 1 finds a foothold in >= 1 of 9 rows
(if it does, cycle 1-2's naive failures were budget); ARM 2 keeps
persistence in >= 2 of 3 rows per cell and shows a fall in ops/episode
of >= 50 % between generation 0 and 200 in at least one cell.

## Unchanged

World grammar, controls, nulls, boundary map (S1' is inside the
selectivity-pays region wherever S1 was: it is S1 with alpha lowered,
and alpha only hurts FULL_LOG and SELECTIVE, never TRIVIAL, so the
margin grows), interventions, curves, classes, records.

## Not done in cycle 3

Cells C, E, G, H (no foothold to test economics on; wait for ARM 1's
answer); F (no positive control); any change to organisms.
