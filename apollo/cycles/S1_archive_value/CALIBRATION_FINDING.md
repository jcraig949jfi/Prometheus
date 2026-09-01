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

## Cross-engine calibration (ADDED 2026-09-01, all engines, budget 600, seed 20260901)

    function      stackvm-v1   treegp-deap   push-pyshgp
    identity (x)  SOLVED 1.0   0.000         SOLVED 1.0
    x+1           SOLVED 1.0   0.000         0.083
    x+5           0.083        0.000         0.083
    2x            0.083        0.000         0.083
    3x+1          0.083        0.000         0.083

- **treegp-deap: uniformly 0.000, cannot solve the identity the other two solve.**
  This is a SUSPECTED INSTRUMENT DEFECT (adapter/representation/fitness-scale mismatch
  in the treegp-deap task binding), run identically to the working engines, so the
  difference is treegp-side. Filed for the Foundry operator; NOT used as difficulty
  evidence. Cause not yet verified (would need to inspect a treegp organism's output
  type on an identity task).
- **The two WORKING engines converge:** union reachable-solve set at feasible budget =
  {identity, x+1}. Nothing with a genuine constant (x+5) or a multiplier (2x, 3x+1)
  solves on stackvm OR pyshgp.

## Conclusion (option 1 exhausted)

S1's cross-world transfer-of-useful-organisms primary is **not constructible on any
available engine at feasible budget**, because the substrate hosts no non-trivial
functional organisms to transfer. This is engine-independent (holds on both working
engines), not a harness bug, and not small-budget tuning (x+5 floors as hard as 3x+1).

**What this does NOT establish:** that much larger budgets (10-100x, expensive and
uncertain — x+5 floored badly at 600) wouldn't move the frontier; that a DIFFERENT world
type (the Foundry may gain richer worlds/oracles in the ~2026-09-02 release) wouldn't
host it; that partial-credit/behavioural transfer shows nothing.

## Recommendation to HITL

The S1 value test is currently **blocked at the SUBSTRATE, not at Apollo's machinery**
(the machinery is built and validated). The decision is which of:
  (a) WAIT for the imminent Foundry release, re-run this cheap ladder on its new worlds
      before any endpoint pivot or retire call. CHEAP, and the substrate is about to
      change anyway. Apollo's lean.
  (b) LARGE-BUDGET probe of whether the solve frontier moves (expensive, uncertain).
  (c) ACCEPT as the S1 result: on the current substrate MAP-Elites has no transferable
      structure to mine because the substrate hosts none at feasible cost — a hold/
      scale-down, keeping the validated adapter/replay/fossil infrastructure. This is
      the reviewer's pre-authorised "good instrument, no research program" outcome, and
      it would be premature only because the substrate is about to change (hence (a)).

Prereg stays UNFROZEN and unscored. No scored cell has been run.


## CORRECTION 2026-09-01 (Source Viability Gate, broader op ladder)
The 'reachable-solve set = {identity, x+1}' above was measured on AFFINE functions only and is too narrow. The gate's ladder tested distinct operations, and the substrate reaches PARTIAL functional fitness on a rectifier-like capability that affine-only calibration missed: **abs and threshold both 0.583 (7/12 cases, verified pop_mass 2), modular 0.417** (stackvm-v1, budget 300). These are partial-fitness, not solves (still no exact solve beyond identity/x+1). The Source Viability Gate still returns **FAIL** on G1 (only 2 distinct nontrivial ops reach the 0.5 threshold, need >=3; and abs+threshold likely reflect ONE rectifier capability, agreeing on the same non-negative cases), and on G2 (abs mass 2 < 3). Disposition unchanged (mining suspended). A bug was caught in the gate's mass extraction (fitness is top-level in ARTIFACT_EXECUTED, not nested) -- fixed and verified. Gate artifact: apollo/cycles/S1_archive_value/gate/gate_stackvm-v1_50b5c2327c64.json.
