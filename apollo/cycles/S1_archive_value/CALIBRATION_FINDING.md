# S1 CALIBRATION — stackvm's reachable-solve set is nearly empty at feasible budget

> **Apollo (M2), 2026-09-01.** Solvability ladder run to decide whether S1's transfer
> primary is constructible. map_elites, engine stackvm-v1, budget 600, seed 20260901,
> 12 train cases. Recorded before any scored S1 cell.

## The ladder

    function      solved   best_fitness   wall
    identity (x)  YES      1.000          142s
    x+1           YES      1.000            1s
    2x            no       0.083          171s
    x+5           no       0.083          131s
    3x+1          no       0.083          251s

best_fitness 0.083 = exactly 1/12 cases — a floor artifact (a near-trivial program
coincides with the target on a single case). Coverage 0.14-0.20 in every case, solved or
not, which is the pilot's point restated: the archive fills REGARDLESS of reachability.

## What it establishes

On stackvm-v1 at a feasible budget, the reachable-solve set is essentially
**{identity, x+1}**. Not "additive solves, multiplicative doesn't" — `x+5` (additive,
just a larger constant) already floors, as do `2x` and `3x+1`. Only the near-trivial
identity and increment are found. Raising budget within reach did not help across the
whole ladder (x+5 floors at 600 exactly like 3x+1).

## Consequence for S1

S1's primary endpoint — cross-world transfer/reuse of USEFUL organisms — is **not
constructible on stackvm-v1 at feasible cost.** You cannot build multiple world families
whose archives contain functional organisms when the only functions the engine solves
are identity and +1. Every other world produces a population that passes 1/12 cases,
so "does the archive transfer better than random" degenerates to "does junk transfer
like other junk" (the pilot's degeneracy, now explained at its root). This is an
engine-reach fact, not a harness bug (harness validated) and not a small-budget tuning
issue (x+5 fails identically to 3x+1 at 600).

## The fork (before any retire call, and before spending the scored budget)

Three live options, ordered by what Apollo should try first:

  1. **Other engines (CHEAP, in progress).** treegp-deap and push-pyshgp are GP systems
     with richer primitive sets; they may solve a broad function family cheaply, making
     S1's transfer design viable there. One ladder each (~10-15 min) decides it. Running.
  2. **Redefine the endpoint to be low-fitness-native** (behavioural-diversity yield +
     boundary-pair yield per unit compute). MEASURABLE, but it walks toward exactly the
     "decorative ecology" the reviewer warned against — a diversity win with no transfer
     is not substrate-miner value. Adopt only if no engine supports transfer.
  3. **Read as evidence toward FAIL/retire.** If ALL THREE engines have a near-empty
     reachable set at feasible budget, this integer-induction substrate cannot host the
     substrate-miner value test, and MAP-Elites has no transferable structure to mine
     here. That is the reviewer's pre-authorised retire outcome — but it is premature on
     one engine, hence option 1 first.

## Status
- Harness: validated (pilot).
- stackvm-v1: reachable-solve set ~= {identity, x+1}; transfer primary not viable here.
- Next: cross-engine solvability calibration (treegp-deap, push-pyshgp). The scored S1
  campaign is NOT launched and the prereg stays UNFROZEN until an engine that can host a
  non-degenerate transfer test is found — or all three are ruled out.
