+==============================================================================+
|                                                                              |
|   APOLLO S1 -- ARCHIVE VALUE TEST -- REVIEW PACKAGE                           |
|   The one authorised substrate-miner falsification campaign: built, and       |
|   returned a decisive negative at the substrate before spending scored        |
|   compute.                                                                   |
|                                                                              |
|   Prepared by : Apollo (M2), 2026-09-01                                       |
|   For         : James (HITL) + external frontier reviewers                   |
|   Status      : results report + request for critique                        |
|   Self-contained: every number was measured on this machine against the      |
|                   live Foundry host; no repo access needed to review.        |
|                                                                              |
+==============================================================================+


0. THE MANDATE
--------------
After Apollo's Gen-2 reassignment to "Serendipity substrate miner" and a verified
end-to-end plumbing slice, the HITL review of 2026-09-01 granted Apollo EXACTLY ONE
serious falsification campaign -- explicitly designed to be able to KILL the
substrate-miner role, not to confirm it -- and set the bar:

  "Apollo earns continued substrate-miner compute only if MAP-Elites produces at least
   a 2x enrichment over random in independently-verified transferable/reusable
   structures ... Search is more expensive and architecturally more complex than random
   generation; a 5% advantage isn't enough to justify Apollo."

The campaign is S1, the Archive Value Test. Its proposition (weaker and more plausible
than the falsified Gen-1 claim that evolution autonomously widens capability):

  Quality-diversity search (MAP-Elites) produces a more useful population of
  transferable, behaviourally distinct structures than matched random search, under
  equal evaluation budget.

The archive is on trial. Coverage is NOT assumed to be a good. A filled archive whose
members neither transfer nor improve downstream is "decorative ecology," and S1 was
built to be able to say so.


1. WHAT WAS BUILT (and committed before any measurement)
--------------------------------------------------------
- Fossil schema change (reviewer Q1): organism_source is now STRUCTURAL and enforced at
  write time -- a create_random specimen can never be read as a search discovery.
- S1 apparatus (apollo/serendipity/s1_*.py + apollo/cycles/S1_archive_value/):
  * world families with independently-constructed semantics (affine, piecewise,
    modular, quadratic-reserve) + a DEAD-RANDOM control world (structureless target);
  * ledger-based population extraction -- the MAP-Elites archive is reconstructed from
    the host's 87k-event ledger as ARCHIVE_INSERT minus ARCHIVE_EVICT; the random
    population as ARTIFACT_EXECUTED in the run's seq bracket (winners AND losers kept);
  * cross-family zero-shot transfer scoring via /v0/evaluate (task-relative fitness);
  * a FROZEN analysis script with the preregistered primary, controls, and >=2x
    threshold, committed before any scored number existed.
- Preregistration with two mandatory controls: (6a) dead-world -- MAP-Elites must NOT
  turn an unreachable target into "interesting diversity"; (6b) size+diversity-matched
  random subsample -- if the MAP-Elites edge vanishes under matching, it was bookkeeping.


2. THE PRIMARY ENDPOINT, AND WHY IT MATTERS
-------------------------------------------
transfer_rate(P, W_t) = P(a distinct member of population P is USEFUL on a held-out
cross-family world W_t), where "useful" means fitness >= tau_t and tau_t is the
75th-percentile fitness of the RANDOM population on W_t (a bar MAP-Elites cannot game,
set from random). Primary comparison:

  ENRICHMENT = rate(map_elites archive) / rate(random)   [pooled over cross-family pairs]

This directly tests whether the archive is MINED SUBSTRATE (reusable structure) rather
than diverse junk. It is size-invariant, so a ~15-member archive and a ~300-evaluation
random population compete on equal footing.


3. THE PILOT KILLED THE PRIMARY'S OPERATIONALIZATION (as intended, cheaply)
--------------------------------------------------------------------------
A throwaway pilot (seed 999, reserve worlds, separate directory -- cannot touch scored
cells) validated the whole pipeline computes, then exposed a fatal degeneracy:

  tau_t came out at the FLOOR (0.083, and 0.000 for one target). With tau ~ 0, EVERY
  member counts as "useful," so rate(map_elites)=0.81, rate(random)=0.73,
  ENRICHMENT=1.11 -- no signal.

Root cause, not a bug: at feasible budget NEITHER driver produces a functional organism
even on its own world (best fitness 0.083-0.167 = passing 1-2 of 12 cases). There is
nothing worth transferring, so the transfer test degenerates to "does junk transfer like
other junk?" -- answer: equally, at the floor.

The control already earned its keep: on the DEAD-RANDOM world MAP-Elites still filled a
13-cell archive (coverage 0.19). Under a coverage-based endpoint the new Apollo would
have called that value. It is not, and the transfer endpoint (however degenerate here)
flattened it -- which is exactly what control 6a is for.


4. THE SOLVABILITY LADDER EXPLAINED IT AT THE ROOT (single engine)
------------------------------------------------------------------
MAP-Elites, stackvm-v1, budget 600, 12 train cases:

  function       solved   best_fitness
  identity (x)   YES      1.000
  x+1            YES      1.000
  x+5            no       0.083
  2x             no       0.083
  3x+1           no       0.083

The reachable-solve set is essentially {identity, x+1}. Not "additive vs multiplicative"
-- x+5 (a larger additive constant) already floors. Only the near-trivial identity and
increment are found. Budget is not the lever: x+5 floors as hard as 3x+1 at 600.


5. CROSS-ENGINE CALIBRATION (all three engines, budget 600)
-----------------------------------------------------------
  function      stackvm-v1   treegp-deap   push-pyshgp
  identity      SOLVED 1.0   0.000         SOLVED 1.0
  x+1           SOLVED 1.0   0.000         0.083
  x+5           0.083        0.000         0.083
  2x            0.083        0.000         0.083
  3x+1          0.083        0.000         0.083

- The two WORKING engines converge: union reachable-solve set = {identity, x+1}. Nothing
  with a real constant or a multiplier solves on stackvm OR pyshgp.
- treegp-deap returns a uniform 0.000 -- it cannot solve the identity the other two
  solve. This is a SUSPECTED INSTRUMENT DEFECT (adapter/representation/fitness-scale
  mismatch in the treegp-deap task binding), run identically to the working engines so
  the difference is treegp-side. Filed for the Foundry operator; NOT used as evidence.
  Cause not yet verified (would need to inspect a treegp organism's output type).


6. RESULT
---------
S1's cross-world transfer-of-useful-organisms primary is NOT CONSTRUCTIBLE on any
available engine at feasible budget, because the substrate hosts no non-trivial
functional organisms to transfer. This is:
  - engine-independent (holds on both working engines),
  - not a harness bug (the harness is validated end to end),
  - not small-budget tuning (x+5 floors as hard as 3x+1 at budget 600).

The substrate-miner value test is BLOCKED AT THE SUBSTRATE, not at Apollo's machinery.
No scored cell was run. The prereg stays UNFROZEN, with its 2x threshold and both
controls intact, for whenever an engine/world can host a non-degenerate test.


7. WHAT THIS DOES AND DOES NOT ESTABLISH
----------------------------------------
ESTABLISHES:
  - The S1 apparatus works: ledger-based archive reconstruction, cross-family transfer,
    frozen analysis, controls -- all validated on live data.
  - On the CURRENT Foundry, integer-induction worlds, feasible budget (~600 evals,
    ~1-4 min/burst), the reachable-solve set on the working engines is near-trivial.
  - The campaign paid for itself in cheap failures (a pilot + two calibration ladders)
    rather than a multi-hour scored run on a degenerate metric.

DOES NOT ESTABLISH:
  - That much larger budgets (10-100x; expensive, uncertain -- x+5 floored badly at 600)
    would not move the frontier.
  - That a DIFFERENT world type would not host it. The Foundry is evolving; a release is
    expected ~2026-09-02 and may add richer worlds/oracles.
  - That partial-credit or behavioural transfer (rather than solve-transfer) shows
    nothing. Not yet tested.
  - Any verdict on the Gen-1 null. S1 tests a different, weaker proposition.


8. THE DECISION (HITL), WITH APOLLO'S RECOMMENDATION
----------------------------------------------------
  (a) WAIT for the imminent Foundry release; re-run this cheap ladder on its new worlds
      before any endpoint pivot or retire call. ~20 minutes. The substrate is about to
      change anyway. APOLLO'S LEAN.
  (b) LARGE-BUDGET frontier probe -- expensive, uncertain.
  (c) ACCEPT as the S1 result now: on the current substrate MAP-Elites has no
      transferable structure to mine because the substrate hosts none at feasible cost.
      This is the reviewer's pre-authorised "good instrument, no research program"
      outcome. Premature ONLY because the substrate is about to change (hence (a)).


9. QUESTIONS FOR THE REVIEWER
-----------------------------
  Q1. Is "blocked at the substrate, not at Apollo" a fair reading, or is a reachable-set
      of {identity, x+1} across two engines already enough to call the substrate-miner
      value proposition dead ON THIS FOUNDRY regardless of the coming release?
  Q2. If the new release still yields a thin reachable set, what is the LAST admissible
      move before retire -- a behavioural/partial-credit transfer endpoint (risking the
      "decorative ecology" trap), or stop?
  Q3. The pilot degeneracy was caught by a relative bar (tau from random). Is there a
      cheaper pre-flight that would have flagged "source search produces nothing
      functional" before building the full transfer harness at all?
  Q4. Retire-check, standing: if S1 cannot be made non-degenerate on the new release
      either, the recommendation is to keep the adapter/replay/fossil infrastructure and
      stop scheduled evolutionary mining. Is that the right disposition, and what
      evidence from the new release would flip it either way?


10. ARTIFACTS (for a reviewer with repo access)
-----------------------------------------------
  apollo/cycles/S1_archive_value/PREREGISTRATION.md     endpoints, controls, 2x threshold
  apollo/cycles/S1_archive_value/PILOT_FINDING.md       the degeneracy, explained
  apollo/cycles/S1_archive_value/CALIBRATION_FINDING.md the ladder + cross-engine table
  apollo/cycles/S1_archive_value/s1_analyze.py          the frozen analysis
  apollo/serendipity/s1_worlds.py, s1_campaign.py       world families + runner
  apollo/serendipity/{foundry_creds,world_adapter,eval_adapter,fossil}.py  adapters
  roles/Apollo/STATUS.txt                               machine-readable current state
  Commits (origin/main): S1 harness+pilot+calibration, cross-engine calibration.

+==============================================================================+
|  END -- reply with answers to section 9 and a disposition on section 8.      |
|  As standing policy: "this apparatus is not worth continuing" remains a       |
|  first-class answer. A validated harness is not a reason to keep searching.   |
+==============================================================================+
