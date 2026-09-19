# Power register -- every kernel instrument and the test in which it says NO

Written 2026-09-19 (overnight C98) after three instruments were found to lack power in one night:
C70 (reference agreement on an action-blind probe), C95 (the mutation ledger's anchor test caught every
mutant), C97 (seven of eight controls had never said NOT_MET). Rule: an instrument that has not been seen
to say NO is decoration; its green is a claim with no evidence. This register is maintained by hand and
checked against the suite by `tests/test_power_register.py` (every named test must exist).

| instrument | says NO as | demonstrated by |
|---|---|---|
| control.replay.v1 | NOT_MET | test_control_power::test_replay_says_not_met_for_a_world_that_lies_about_bit_replay |
| control.cheat.v1 | NOT_MET | test_playtest_findings::test_a_cheat_blind_world_makes_the_cheat_control_not_met_and_the_job_invalid |
| control.negative.v1 | NOT_MET / INDETERMINATE | test_control_power::test_negative_is_indeterminate_without_an_objective_and_not_met_when_the_abstainer_acts |
| control.positive.v1 | NOT_MET | test_control_power::test_positive_says_not_met_when_maximal_actions_cannot_move_the_world |
| control.sham.v1 | INDETERMINATE (no behaviour change) | test_control_power::test_sham_is_indeterminate_when_the_shuffle_changed_no_behaviour |
| control.scratch.v1 | NOT_MET (genome unchanged) / INDETERMINATE | test_control_power::test_scratch_says_not_met_when_the_fresh_player_has_the_primary_genome |
| control.permutation.v1 | INDETERMINATE (no behaviour change) | test_control_power::test_permutation_is_indeterminate_when_it_cannot_change_the_observation |
| control.ablation.v1 | NOT_MET / INDETERMINATE | test_control_power::test_ablation_says_not_met_when_the_ablated_arm_still_uses_a_workspace ; test_workspace (ablation INDETERMINATE without workspace) |
| admission: provenance | failed=[provenance] | test_admission_power::test_provenance_check_fails_a_row_without_author_or_license |
| admission: capabilities | failed=[capabilities] | test_admission_power::test_capabilities_check_fails_a_malformed_id |
| admission: conformance | failed=[conformance] | test_admission_power::test_conformance_check_fails_a_world_whose_trace_is_not_a_hash ; test_admission (bad observer) |
| admission: extensions | failed=[extensions] | test_admission_power::test_extensions_check_fails_a_declared_but_undemonstrable_extension |
| admission: replay | failed=[replay] | test_admission_power::test_replay_check_fails_a_world_that_declares_bit_and_drifts |
| admission: reference (agreement AND probe power) | failed=[reference] | test_admission::test_second_implementation_is_checked_against_the_reference_and_a_wrong_one_is_refused ; test_batch (wrong batch world) |
| admission: controls (cheat) | failed=[controls] | test_admission_power::test_controls_check_fails_a_world_whose_cheat_changes_nothing |
| admission: registry (absent machinery) | failed=[registry] | test_batch::test_absent_machinery_row_keeps_its_reason_across_repeated_admission |
| admission: performance | never (a receipt, not a check) | -- (recorded as such) |
| admission: observer determinism | failed=[determinism] | test_admission::test_nondeterministic_observer_is_refused |
| admission: substrate honesty | failed | test_admission::test_substrate_that_lies_about_representations_is_refused |
| admission: control arm validity | failed | test_admission::test_control_whose_arm_is_invalid_is_refused |
| series.verify | MISSING / MISSING_ARTIFACT / CORRUPT / CORRUPT_LAYOUT / BOUND_EXCEEDED | test_series::test_empty_disabled_missing_and_corrupt_are_distinguishable ; test_declared_bound_is_deterministic_and_reported_not_silent ; test_layout_mismatch_is_flagged_and_objective_reads_by_name_not_position |
| receipt.scan | TRUNCATED / RECEIPT_ID_MISMATCH / DUPLICATE / CHAIN_BREAK | test_integrity::test_truncated_last_line_is_reported_not_dropped ; test_edited_record_in_the_middle_is_named_by_line ; test_duplicate_receipt_ids_are_reported ; test_deleting_a_middle_receipt_breaks_the_chain_and_is_reported |
| executor: eligibility (max_runs) | TARGET_UNSUPPORTED | mutants M41 (caught) ; test_dof |
| executor: resume identity | ValueError | mutants M39 (caught) |
| executor: batch fallback | execution.reason | test_batch::test_batch_falls_back_and_says_why |
| objective shape summary | UNSUPPORTED / MIXED / none | test_objective_shapes::test_a_non_numeric_objective_value_is_reported_not_dropped ; test_scalar_and_none_shapes_are_named_in_the_summary |
| selector rank | SelectorNeedsScalar | test_objective_shapes::test_a_selector_without_a_rank_refuses_a_vector_objective_with_the_keys_named |
| mutation ledger | SURVIVED | possible only since C95 (anchor test deselected); 58/58 CAUGHT with real first failures |
| fuzz property batched==scalar | assertion + coverage guard | test_batch::test_the_random_property_actually_exercised_the_batch_path |
| cross-platform replay | assertion; SKIP when no second platform (a skip COUNT is the signal, C92b) | test_cross_platform |
| IR validate | defect list | test_kernel / test_fuzz (invalid IRs raise IRError at compile) |
| capability negotiation | BLOCKED_MISSING_CAPABILITY | test_kernel::test_capability_negotiation_is_a_result_not_an_exception |
| committed receipts as fixtures (38 files) | divergent runs | test_replay_committed::test_committed_receipts_replay_without_divergence ; power shown by hand: a one-constant world change (M73) fails 27 of 39 |
| checkpoint/resume | action/summary mismatch | test_integrity::test_checkpoint_carries_the_kernel_wrappers_state ; test_checkpoint_resume_property_over_random_compositions (guarded) |
| admission: mutable params in snapshot | failed=[extensions] | test_admission_power::test_extensions_check_fails_a_declared_but_undemonstrable_extension |

| forensic scan (random files) | one defect per edit / CHAIN_BREAK / DUPLICATE / TRUNCATED | test_integrity::test_forensic_scan_property_over_random_receipts_files (guarded) |
| series contract (random IRs) | status mismatch / MISSING_ARTIFACT | test_series::test_series_contract_over_random_compositions (guarded) |
| search invariants (random templates) | row mismatch | test_search::test_search_invariants_over_random_templates (guarded) |
| IR sweep / negotiation laws | assertion | test_fuzz::test_sweep_and_negotiation_laws |
| control vocabulary (random IRs) | assertion; NOT_MET/INDETERMINATE occur on random IRs | test_control_power::test_control_vocabulary_over_random_compositions (guarded) |
| admission order-independence | state/failed mismatch | test_admission_power::test_admission_is_order_independent_and_idempotent |
| accounting laws (random receipts) | assertion | test_workspace::test_accounting_laws_over_random_receipts (guarded) |
| mutation runner bytecode safety | stale-pyc false verdicts impossible since C122 | (runner: PYTHONDONTWRITEBYTECODE + purge) |

Known instruments WITHOUT a demonstrated NO (honest list):
- admission "performance": by design a receipt.
- observer.trace / observer.descriptor measure(): descriptive, no verdict.
- the census: a count of admission results; its power is the admission checks' power.
