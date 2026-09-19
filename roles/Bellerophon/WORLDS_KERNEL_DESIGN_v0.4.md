# Prometheus Worlds Kernel -- design v0.4 (end-of-window snapshot, second half of the overnight loop)

Currency: 2026-09-19 (written after C102, before the final regression; the report's addendum carries the ending
commit and final counts). Supersedes v0.3 where they differ; v0.3 and v0.2 stay as the records of their halves.
Ledger of every cycle: roles/Bellerophon/OVERNIGHT_LEDGER_2026-09-19.md (append-only, failed approaches kept).

Authority: THINGS OBSERVED WORKING (a test or a committed receipt behind every line of section 1), and, this
half, THINGS OBSERVED NOT WORKING that a document had said would (section 2).

--------------------------------------------------------------------------
1. WHAT RUNS (observed since v0.3, cycles C91-C102)
--------------------------------------------------------------------------

  batched execution      budget.batch = k (EXECUTION POLICY, outside the scientific digest with wall_s and max_runs)
                         groups consecutive same-(arm, sweep point, digest) runs behind one ext.batch.v1 world;
                         every science field of a batched receipt equals the scalar path's run for run (18 hand
                         cases + 40 random IRs with a coverage guard); fallback with the reason on every receipt
                         (BATCH_NOT_REQUESTED / SCHEDULE_NOT_BATCHED / NO_BATCH_IMPLEMENTATION); one failing env is
                         one FAILED receipt; resume and wall budget work between batches; replay_file takes the
                         scalar path by default (an independent path is the point of a replay); search composes
                         (same archive rows on both paths)
  world.integer_batch.v1 numpy over n envs; a batch world IS a world (n_envs=1 face) so admission drives it through
                         the ordinary contract and reference agreement (a one-constant Wrong sibling is refused);
                         numpy is a native dep: absent -> the row stays UNAVAILABLE "import: ..." and the kernel
                         falls back (found by the WSL probe, which had gone SILENT: skip counts are a signal)
  objective shapes       Objective.evaluate value: number | {component: number|None} | None. objective.multi.v1
                         composes named objectives; SUMMARY splits report objective_shape (scalar / vector / none /
                         UNSUPPORTED / MIXED), per-component means and n; search rows carry the dict; selectors
                         take rank=<component> or refuse (SelectorNeedsScalar, keys named) BEFORE a generation is
                         written; objective.survival.v2 (ticks survived) beside v1 (a step function, pt_h finding)
  identity vs class      receipts: player_fingerprints[pid] = {hash (behavioural class on a 16-probe), silent,
                         spec_hash (manifest identity)}; archive rows carry player_hash; pt_h had 11 distinct
                         players behind one "fingerprint" (a point mutation the probe never visits)
  control power          every control can now say NO and has a test where it does: negative INDETERMINATE without
                         an objective; sham INDETERMINATE when the shuffle changed no behaviour; scratch NOT_MET
                         when a "fresh" player carries the primary's genome, INDETERMINATE when behaviour is
                         unchanged; permutation INDETERMINATE when it changed nothing; replay/positive/ablation
                         NOT_MET demonstrated. Control.arm may take registry= (call_arm)
  power register         roles/Bellerophon/science/POWER_REGISTER_2026-09-19.md: 32 instruments, the way each says
                         NO, the test that shows it; test_power_register refuses a stale citation
  structured observations ext.observation.structured.v1; contracts.flatten() (sorted keys, depth first, TypeError
                         otherwise); grid obs_mode="structured" (same trace); every reference player reads through
                         flatten(); observation_permute REFUSED at lowering for a structured world (also via the
                         permutation control) -- nothing flattened on a designer's behalf
  admission_params       a component with no valid default construction (objective.multi.v1) declares what
                         admission constructs it with; every admission factory() call uses them
  mutation ledger        honest since C95 (the anchor test is deselected inside mutant runs); 62 mutants, 62 CAUGHT
                         by BEHAVIOUR tests, real first failures recorded
  soak                   search above the kernel for 20 wall minutes in one process (science/SOAK_SEARCH_*.json):
                         per-generation wall, traced memory, file scan, marker order, elite movement

--------------------------------------------------------------------------
2. WHAT A DOCUMENT SAID WOULD WORK AND WAS OBSERVED NOT TO
--------------------------------------------------------------------------

  U1 "batched worlds = NPE-class throughput"   FALSIFIED for this world family. World-only: 6.0 us/env-tick
    scalar vs 8.6 us batched at n>=128 (0.70x, never faster; 0.18x at n=1). Executor end to end: 0.93-0.95x on
    500-tick runs; 1.3-1.8x on 5-tick runs is setup amortisation, not stepping. Profile of a scalar tick:
    world.step 36%, players.act 22%, observers 11%, JSON trace 8%, loop 23%. The vectorised transition (4 ops on
    6 registers) was never the cost; the PER-ENV CONTRACT (events as tuples, the trace as JSON text per tick,
    the pending queue) and the players are, and BIT-equality with the reference obliges the batch world to
    reproduce exactly that contract. Batching pays only when the contract itself is columnar (array trace,
    columnar events) and players/observers batch too -- which is a different world FAMILY, admitted by
    SEMANTIC/aggregate agreement, not BIT trace equality. The kernel PATH is proven; the throughput claim is not.
    Reopen when a world whose step dominates the tick exists (Box2D, c6 composed at scale).
  "37/37 mutants caught" (report of 04:52Z)   TRUE but the instrument could not have said otherwise for 18 of
    them since C87: the anchor-drift test failed for every applied mutant. No survivor was hidden (each had a
    real first failure in an earlier wave) but a regression of any of those tests would have been invisible.
  "5/5 controls MET" (EXP-002)   TRUE then and now, but until C97 four of the five could not have said NOT_MET
    on that experiment. After C97 the same 72/72 MET per control means: every sham/scratch arm changed behaviour.
  "batched execution reproduces scalar receipts" (my own C92 claim)   TRUE, and a 40-IR property test was green
    in 0.75 s with 28 of 202 runs batched: real but thin; guarded now.

--------------------------------------------------------------------------
3. DEFECTS THE ROWS (AND THE INSTRUMENTS) FOUND, C91-C102
--------------------------------------------------------------------------
  C92  the reference's stochastic kick evaluates its RIGHT side first (value = draw 2, index = draw 3); the
       numpy re-implementation had to state what integer_alt reproduced by copying the expression
  C92b importing numpy at install time broke the WHOLE registry on a host without it (WSL): 7 skips instead of 6
  C92c three test doubles with a stale run_one signature became 18 FAILED receipts and "DID NOT RAISE";
       C99 found the same in a playtest double (84 FAILED, valid=False)
  C94  a vector objective vanished from the split summary (objective_n=0) and would have crashed a generation
  C95  the mutation ledger could not say SURVIVED (see section 2)
  C96  survival.v1 is a step function (every elite life=0); 11 distinct players behind one probe fingerprint
  C97  seven of eight controls had never said NOT_MET; sham compared a count the shuffle preserves; scratch and
       permutation asserted a status the executor had already handled; a Proteus test blessed three equal traces
       as sham MET and scratch MET; _TransformControl looked up transforms in the process-global registry
  C100 statemachine.v3 read list(obs) -- the keys of a dict -- in two places (found by the fuzz, not by the test
       written for the feature)

--------------------------------------------------------------------------
4. ASSUMPTIONS STILL PRESENT (honest list, updated)
--------------------------------------------------------------------------
  execution is synchronous: one lock-step loop; turn-taking is expressible (width-0 spaces, C72); event-driven
    worlds would need a different loop contract (not designed)
  one world per experiment; heterogeneous machines yes, heterogeneous worlds only as a sweep axis
  communication is stigmergic or by mailbox door; no addressed message contract beyond mailbox
  ACTIONS are int lists (ActionSpace width x range) by CONTRACT: continuous actions travel as fixed-point ints
    (ext.continuous_actions.v1; the pendulum's act_scale) -- an encoding rule, exercised by fuzz and admission
  observations: REMOVED (structured, opaque to the kernel) -- permute is defined only for flat ones
  rewards singular: REMOVED (vector objectives with named components; rank or refuse)
  batched worlds: modelled and proven equal; NOT faster for a per-env-contract world (section 2)
  generations: the search layer commits per generation; a steady state is n=1 per generation (an expression,
    not a removal)
  kernel wrappers: REMOVED as an assumption (C111-C112: delay / permute / schedule on the batch face; EXP-001 batches)

--------------------------------------------------------------------------
5. STATUS OF THE NAMED ITEMS
--------------------------------------------------------------------------
  U1 batching          PATH DONE (ext.batch.v1, run_batch, policy, fallback, replay, search); THROUGHPUT CLAIM
                       FALSIFIED for the reference family; a columnar-contract family is the next design question
  U3 series            RESOLVED (unchanged since v0.3); batched receipts carry identical series hashes
  EXP-002              DONE; regenerated under powered controls: 432 runs, 5/5 MET 72/72, 0 INDETERMINATE
  admission            DONE for every slot; 40/40 admitted; every named check demonstrated failing
  Redis                UNAVAILABLE on M2 (unchanged)
  bridges              unchanged since v0.3 (SFE runtime executor; NPE UNAVAILABLE_INTERFACE by D-BELL-2)
  Box2D / compute      NOT started; now the named reopen condition for batching
