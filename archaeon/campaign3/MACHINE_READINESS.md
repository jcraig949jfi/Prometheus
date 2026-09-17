# Campaign 3 -- MACHINE READINESS (Phase A exit)

Author: Archaeon m2-411504ab. Date: 2026-09-17 (Phase A 06:30-07:10 UTC).
Status: 5 of 6 groups IMPLEMENTED_AND_TESTED, 1 PARTIAL (E: the artifact
listing route belongs to the engine owner; requested, not blocking).
No group DEFERRED_WITH_MITIGATION. Science may begin.

Evidence: archaeon/tests/test_campaign3_machine.py (6 tests) +
test_campaign2_machine.py (16) + test_wse.py (25) = 47 passed; the
reachability table migrated in place (779 rows); the corridor table
populated from campaign-2 evidence (73 rows); comms #325 to Daedalus.

-----------------------------------------------------------------------
GROUP  STATUS                   WHERE / HOW EXERCISED
-----------------------------------------------------------------------
A      IMPLEMENTED_AND_TESTED   archaeon/wse/reachability.py: every row carries level in
       full-solve reachability  {FLOOR, SHELF, SUMMIT} (SHELF_MIN 0.45, SUMMIT_MIN 0.90),
                                first_foothold_gen (0.5, the campaign-1/2 criterion),
                                first_shelf_gen, summit_candidate_gen (training best
                                >= 0.9) and first_summit_gen (candidate CONFIRMED by a
                                held-out >= 0.9; D3-006 after the table showed a
                                training-only 0.9375 with held-out 0.53), summit_censored.
                                pooled()/lookup() report k_shelf, k_summit (confirmed),
                                k_summit_candidate, k_summit_any, class_summit, per-level
                                counts and a shelf histogram (0.1 bins of best training
                                reward). Table migrated (migrate_levels). Test:
                                test_levels_need_heldout_for_summit. Current reading:
                                W2_K2 4-bit N200 G60: 27 runs, 16 SHELF, 0 SUMMIT
                                (OBSERVED_UNREACHABLE_AT_BUDGET for the summit).
B      IMPLEMENTED_AND_TESTED   rows carry stopped_on_solve; lookup(G) pools every row
       right-censoring          that INFORMS budget G monotonically (rows run >= G
                                generations; stopped rows whose event precedes G); 34
                                campaign-2 stop-rule rows reclassified from treated to
                                baseline+censored (W0 4-bit G30: 11/21 solved, all
                                candidates pending a held-out). Test:
                                test_stopped_runs_inform_larger_budgets_monotonically.
C      IMPLEMENTED_AND_TESTED   archaeon/wse/corridor.py: rows (source cell, maturity,
       corridor table           competence, target cell, direct reuse, init reach at a
                                dose with level + transition generations, budget,
                                foundry, kind direct|init|ladder); edges() pools per
                                pair; table at archaeon/campaign3/CORRIDOR.jsonl.
                                Populated from campaign 2 by corridor_import.py: W0 ->
                                W2_K2 (15 init rows, 13 SHELF, 0 SUMMIT), W0 -> W3_K2
                                (direct 0.54, 8/10 SHELF), W2_K2 streams -> W0 1.00 /
                                W1_d1 0.83 / W1_d4 0.96 / W1_d16 0.92 / W3_K2 0.67
                                (direct), the delay ladder route -> W1_d4 (p=0.1:
                                3/6 SUMMIT-level). Test: test_corridor_rows_and_edges.
                                c3base.Experiment3.corridor_row() records at close.
D      IMPLEMENTED_AND_TESTED   telemetry.probe_plan(G, transitions, dense, sparse) and
       dense transition probes  transition_events(matrix, rung) -> appeared / collapsed
                                / recovered generations. Test:
                                test_probe_plan_and_transition_events.
E      PARTIAL                  sfclient.client.EngineClient gained list_experiments,
       client read path         get_experiment, list_observations (additive, documented;
                                runner.Engine delegates). GET /v2/worlds/{wid}/artifacts
                                does not exist (405): requested from Daedalus (comms
                                #325); ids stay in receipts. Not blocking.
F      IMPLEMENTED_AND_TESTED   evolve.Evolution(offspring_cap=share, import_tags):
       injection cap            reproduce() redraws a parent among residents once the
                                share of children with an import-origin PRIMARY parent
                                reaches the cap; Evolution.inject(manifests, tag)
                                enters imports into the current scored generation and
                                records origin shares before/after in the trace row;
                                common_fill(dose = len(substitutes)). Realized origin
                                shares were already in every trace row (origin_shares).
                                Caveat: origins propagate through mates as well, so the
                                realized share of children carrying an import origin can
                                exceed the primary-parent cap slightly (measured 6/20 at
                                cap 5/20 on a toy run); the cap is on descent, not on
                                mating. Test: test_per_ask_reward_inject_and_offspring_cap.
-----------------------------------------------------------------------

Also in Phase A: evaluate() returns per_ask_reward (credit per ask
position = which stream an organism solves on a K=2 cell) and the trace
carries elite_per_ask and pop_max_per_ask; the campaign-2 machine
(runner, prereg, accounting, c2base) is parametrized per campaign
(D3-001) and the preregistration contract gained the four campaign-3
fields inside the SEALED body (c3base.FIELDS_3); PREREG.md is written
beside PREREG.json.

Incomplete: E(ii) as above. Threat: none of the ten slots needs to list a
world's artifacts. Mitigation: receipts carry every id.
