# Campaign 2 -- MACHINE READINESS (Phase A exit gate)

Author: Archaeon m2-411504ab. Date: 2026-09-17 (Phase A 02:00-03:00 UTC).
Status: 8 of 9 groups IMPLEMENTED_AND_TESTED, 1 PARTIAL (F: one read route
the engine does not serve; the client package itself untouched). No group
NOT_IMPLEMENTED. Science may begin.

Evidence: archaeon/tests/test_campaign2_machine.py (15 tests) +
archaeon/tests/test_wse.py (25 tests, unchanged) = 40 passed;
archaeon/campaign2/PHASE-A/ (two live engine attempts: a01 create+keep, a02
resume+teardown; ATTEMPTS.json); archaeon/tests/data_evolve_snapshot_pre_c2.json
(the pre-refactor loop's numbers, reproduced by the refactored loop under
rng_label=<branch>).

-----------------------------------------------------------------------
GROUP  STATUS                   WHERE / HOW EXERCISED
-----------------------------------------------------------------------
A      IMPLEMENTED_AND_TESTED   archaeon/wse/reachability.py. Persistent table
       reachability table       archaeon/campaign2/REACHABILITY.jsonl, 309 rows
                                (219 baseline) imported from campaign-1 rows
                                (SFE-01 both attempts, 03, 07, 09, 10), the v01
                                survey (126) and SSF c1-c3. Keys cell / value_bits /
                                N / G / E / regime; per-run first_solved_gen,
                                reached, best_train_max, heldout, eval_resolution;
                                pooled n, k, freq, Wilson 95% band, class in
                                {COMMON, REACHABLE, RARE, UNESTABLISHED,
                                OBSERVED_UNREACHABLE_AT_BUDGET}; lookup() never
                                refuses; candidates(lo, hi) returns cells in a band.
                                Tests: test_reachability_classes_and_bands,
                                test_reachability_row_from_result_marks_kind.
                                Obligation (convention, not enforced): a harness's
                                PREREG.reachability_estimate is the lookup() result.
B      IMPLEMENTED_AND_TESTED   archaeon/wse/states.py. assay_states() computes
       typed states             INTERVENTION_NOT_APPLIED, RESIDUE_BELOW_FLOOR,
                                IMMATURE_ARTIFACT, STREAM_BELOW_THRESHOLD,
                                TARGET_UNREACHABLE, READOUT_CANNOT_EXPRESS,
                                POSITIVE_CONTROL_FAILED, UNDERPOWERED from rows,
                                counters, maturity blocks and a sealed threshold;
                                disposition_candidate() orders ENGINE_FAILURE >
                                INSTRUMENT_FAILURE > assay states > UNDERPOWERED >
                                {CAPABLE_NEGATIVE, WEAK_POSITIVE, SUPPORTED_POSITIVE,
                                INCONCLUSIVE}; n >= 10 alone never promotes (a
                                declared battery must have been run and survived).
                                Tests: test_typed_states_fire_from_measurements,
                                test_disposition_science_ladder.
C      IMPLEMENTED_AND_TESTED   archaeon/wse/evolve.py. RNG keyed on (campaign seed,
       common random numbers    world, regime, cell seed, rng_label="crn"); `branch`
                                is provenance only; rng_label is the opt-out.
                                gen0()/common_fill() build generation 0 from the
                                cell's own population with substitutions tagged by
                                origin; provenance recorded in trace[0] and the
                                result; an unprovenanced init_pop is flagged
                                GEN0_FILL_UNVERIFIED. Campaign-1 harnesses patched to
                                pass rng_label=<branch> (frozen rows reproducible;
                                snapshot test). Tests:
                                test_crn_default_and_opt_out_and_snapshot,
                                test_common_fill_provenance_and_origin_share.
D      IMPLEMENTED_AND_TESTED   archaeon/campaign2/runner.py Attempt: numbered
       resume / idempotence /   attempts (attempts/aNN), receipt written after every
       attempts                 step, deterministic step keys sha(experiment, step,
                                *parts), resume replays a prior attempt's steps whose
                                verifier still holds, attempt of record copied to the
                                experiment root + ATTEMPTS.json (no renaming). Engine
                                posts the client can key carry Idempotency-Key: the
                                smoke posted one observation twice under one key and
                                got the SAME obs id. Live: PHASE-A a02 replayed 8
                                steps (session, group, 2 worlds, publish, import,
                                experiment) and created nothing new. Test:
                                test_attempts_are_numbered_persisted_and_resumable.
                                Limit: experiments and worlds are not keyable
                                engine-side; their idempotence is local replay.
E      IMPLEMENTED_AND_TESTED   archaeon/wse/telemetry.py maturity(): source_cell,
       artifact maturity        source_elite_reward, source_competence,
                                share_above_chance, solved (first-class), budget,
                                generation, lineage; maturity_state() maps to
                                RESIDUE_BELOW_FLOOR / IMMATURE_ARTIFACT. Engine.publish
                                RAISES for any kind cmp2.pop.* without a maturity
                                block (test_engine_wrapper_refuses_population_material_
                                without_maturity); the smoke published one with it.
F      PARTIAL                  archaeon/wse/digest.py: canon/hexof/same/of_bytes/
       digest / client /        of_obj/canonical_bytes; every comparison in the
       descriptor               runner goes through same(); smoke: publish hash_ok,
                                import hash_ok, cross-session fetch hash_ok.
                                archaeon/wse/engine_descriptor.py reads the tracked
                                deploy pin (DEPLOYED_BUILD_M2.json) for base_url /
                                instance id / schema and resolves m2.crt; the
                                conformance default cert (m1.crt, L-002) fixed.
                                Read wrappers list_experiments / get_experiment /
                                list_observations live in runner.Engine and worked
                                (n=1 each); list_artifacts answers HTTP 405 (no such
                                GET route on this engine) -> wrapper kept, marked.
                                PARTIAL because (i) the wrappers live in Archaeon's
                                layer, not in sfclient (another seat's package; a
                                one-line move), and (ii) no artifact listing route.
                                Threat: none of the ten experiments needs to LIST
                                artifacts (ids are persisted in receipts).
                                Mitigation: receipts carry every id.
G      IMPLEMENTED_AND_TESTED   archaeon/wse/evolve.py Evolution: evaluate_generation()
       generation step API      / reproduce() / step() / run(); spec and regime may
                                change between steps (curricula, ramps, schedules,
                                pressures); run_cell() = Evolution.run() and
                                reproduces the pre-refactor snapshot bit for bit.
                                Test: test_step_api_matches_run_and_allows_spec_change.
H      IMPLEMENTED_AND_TESTED   first_solved_gen (result + reachability row); source
       telemetry                maturity (E); gen0 provenance (trace[0]); origin
                                shares per generation (imported-lineage share,
                                trace[g].origin_shares, elite_origins); intervention
                                applied counts (evaluate().interventions_applied,
                                Evolution.tabu_checked / tabu_hits); rung x generation
                                (telemetry.rung_matrix_row + shelf_report, which names
                                the generation a rung's competence FELL); genome
                                length / opcode-composition summaries (genome_summary,
                                population_summary; elite_summary in every result).
                                Tests: test_interventions_applied_is_counted,
                                test_maturity_and_summaries.
I      IMPLEMENTED_AND_TESTED   archaeon/campaign2/prereg.py (13 contract fields +
       automatic accounting     decl, validate/seal/render/unchanged) and
                                accounting.py (render_record: sections A-D generated,
                                C/E/F addenda for the agent; ledger_candidates +
                                append_ledger + recur; funnel_row for the campaign
                                table). Tested on synthetic receipts
                                (test_prereg_validate_seal_render,
                                test_record_and_ledger_generated_from_receipt); first
                                live use is C2-SFE-01.
-----------------------------------------------------------------------

Incomplete items, why, what they threaten, mitigation:
- F(i) wrappers not in sfclient: the package belongs to the engine tree; moving
  three one-line methods is a cross-seat change. Threatens nothing in campaign 2.
  Mitigation: runner.Engine is the only client surface the harnesses use.
- F(ii) no GET /artifacts route: engine-side. Threatens nothing (ids persisted).
- A obligation is by convention: the harness template calls reachability.lookup()
  and stores the result in PREREG.reachability_estimate; a harness that skips
  it would pass validate() with prose. Mitigation: the C2 harness base class
  (c2base.py) fills the field from lookup() itself.

Read-time findings recorded for the ledger (not fixed; campaign-1 rows frozen):
- SFE-05 transfer arms and SFE-07 seeded sets filled generation 0 from their own
  foundry seeds (555+seed, 909+seed), the L-030 family; their comparisons carry
  a fill confound. C2 successors use common_fill().
