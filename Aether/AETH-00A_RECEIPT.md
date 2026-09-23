# AETH-00A -- tests and independent oracle (receipt)

Built against the FROZEN AETH-00 contract, semantics_id `aeth00.v1`
(commit `3ff4619de`). Test/support code only; **no production AETH-00
transition implementation exists after this milestone.**

## Files added

- `Aether/test/reference/__init__.py` -- package marker/scope note.
- `Aether/test/reference/oracle.py` -- PRIMARY independent CPU oracle
  (`Aeth00World`, `splitmix64_mix`, `pack_coords`, `arbitration_priority`,
  `decode_proposals`, `group_contests`, `assert_no_duplicate_sources`,
  `arbitrate`, `commit`).
- `Aether/test/reference/oracle_independent.py` -- SECOND, structurally
  independent oracle (`step_bytes`, flat-byte representation) for test 22.
- `Aether/test/reference/mutants.py` -- 9 deliberately broken candidate
  implementations, one per required bug shape.
- `Aether/test/reference/golden_vectors.py` -- frozen arbitration vectors
  (test 23).
- `Aether/test/test_spec_inventory.py` -- tests 1-11, 13-19, 21, 26, 27.
- `Aether/test/test_golden_vectors.py` -- test 23 + defect-detection checks.
- `Aether/test/test_mutants.py` -- test 24 (kills all 9 mutants).
- `Aether/test/test_properties.py` -- test 12 (Hypothesis).
- `Aether/test/test_differential_oracle.py` -- test 22.
- `Aether/test/test_statistical_diagnostics.py` -- tests 20 and 25.
- `Aether/AETH-00A_RECEIPT.md` -- this file.

No existing file was modified. `pytest` and `hypothesis` were
`pip install`ed into the ambient Python (3.13.5) with the user's
explicit permission; no project dependency file existed to declare them
in, and none was added (AETH-00A adds no production dependency).

## 27-test-ID -> executable-test mapping

| Plan # | Executable test(s) |
|---|---|
| 1 | `test_spec_inventory.py::test_01_all_nop_world_invariant_across_ticks` |
| 2 | `test_spec_inventory.py::test_02_single_write_changes_only_intended_neighbor_field` |
| 3 | `test_spec_inventory.py::test_03_toroidal_wrap_from_every_edge_and_corner` |
| 4 | `test_spec_inventory.py::test_04_all_four_target_fields_reachable` |
| 5 | `test_spec_inventory.py::test_05_snapshot_semantics_differ_from_sequential_evaluation` |
| 6 | `test_spec_inventory.py::test_06_newly_written_opcode_has_no_effect_this_tick` |
| 7 | `test_spec_inventory.py::test_07_collision_outcome_deterministic` |
| 8 | `test_spec_inventory.py::test_08_collision_outcome_independent_of_enumeration_order` |
| 9 | `test_spec_inventory.py::test_09_replay_is_bit_identical_tick_for_tick_not_only_hash` |
| 10 | `test_spec_inventory.py::test_10_only_winning_fields_change_and_untargeted_fields_preserved` |
| 11 | `test_spec_inventory.py::test_11_dimensions_and_dtypes_invariant_across_ticks` |
| 12 | `test_properties.py` (all 5 property tests) |
| 13 | `test_spec_inventory.py::test_13_dense_collisions_exactly_one_winner_across_many_seeds` |
| 14 | `test_spec_inventory.py::test_14_degenerate_self_targeting_h1_...`, `..._h2_...`, `..._genuine_collision_at_minimal_dimensions_...` |
| 15 | `test_spec_inventory.py::test_15_reserved_inert_bytes_preserved_untouched_never_traps` |
| 16 | `test_spec_inventory.py::test_16_same_value_write_wins_but_changes_zero_bits` |
| 17 | `test_spec_inventory.py::test_17_inert_cell_can_still_be_written_to` |
| 18 | `test_spec_inventory.py::test_18_independent_per_field_arbitration_no_cross_field_interaction` |
| 19 | `test_spec_inventory.py::test_19_replay_identity_uses_all_six_required_components` |
| 20 | `test_statistical_diagnostics.py` (design + `run_diagnostic`) |
| 21 | `test_spec_inventory.py::test_21_exhaustive_tiny_torus_single_write_fixtures` |
| 22 | `test_differential_oracle.py` (all 3 tests) |
| 23 | `test_golden_vectors.py::test_all_priority_vectors_match_oracle`, `test_winner_vectors_match_oracle`, `test_signed_vs_unsigned_fixture_matches_oracle` |
| 24 | `test_mutants.py` (all 9 mutant tests) + the `_variant_*` tests in `test_golden_vectors.py` |
| 25 | `test_statistical_diagnostics.py` (preregistration docstring + `run_diagnostic`) |
| 26 | `test_spec_inventory.py::test_26_tick_overflow_is_rejected_not_wrapped` |
| 27 | `test_spec_inventory.py::test_27_harness_detects_duplicate_physical_source_proposal` + `test_mutants.py::test_mutant_duplicate_source_aliasing_is_detected_by_harness` |

## Oracle architecture

`oracle.py`'s `Aeth00World` holds `H, W, seed, tick` and a nested
`grid[row][col] = (opcode, arg0, arg1, payload)` tuple structure.
`step()` composes five standalone, independently-testable stages
(`decode_proposals -> group_contests -> assert_no_duplicate_sources ->
arbitrate -> commit`), each named after and cited to its
AETHER_SPEC.md section, returning a NEW `Aeth00World` (S[t] is never
mutated). `oracle_independent.py`'s `step_bytes` re-implements the same
law from scratch on a flat `bytes` buffer with manual index arithmetic,
a single function, and independently-ordered key-construction code, so
that agreement between the two (`test_differential_oracle.py`) is
evidence, not a tautology.

## Golden vectors (test 23)

18 frozen fixture records in `golden_vectors.py`: 14 raw
`arbitration_priority` vectors (seed=0/tick=0 swept over all 4 target
fields; seed=`2**64-1` and seed=`2**63`; tick=`2**64-2` and
tick=`2**63`; target-near-max, source-near-max, and both-near-max
coordinate triples; two coordinates-containing-0 cases; one fully-mixed
case), 3 winner-determination fixtures (2-way, 3-way, 4-way contests,
checking both the winning SOURCE and its VALUE), and 1 signed-vs-
unsigned ordering fixture. Two vectors (`PRIORITY_VECTORS[0]` and
`[3]`) were hand-verified: the full 5-step SplitMix64 chain
(`h0..h3, priority`) was computed digit-by-digit with an independent
one-off script using different variable names than `oracle.py`, then
matched against `oracle.arbitration_priority`'s live output. This
manual pass caught a real transcription risk worth recording: it is
easy to miscount the chain as 4 mix applications instead of the
spec's 5 (`h0=M(...)`, then `h1,h2,h3,priority` are each one more `M(...)`
-- 5 total); my first manual attempt did exactly that and disagreed
with the code until corrected. The remaining 15 vectors were produced
by the same formula, then sanity-checked for structural properties
(e.g. `PRIORITY_VECTORS[0..3]` are pairwise distinct, matching the
tie-freedom proof).

## Mutant catalog (test 24) and which tests kill each

| Mutant | Bug | Killed by |
|---|---|---|
| `mutant_min_priority_arbitrate` | min instead of max | `test_mutants.py::test_mutant_min_priority_picks_wrong_winner`, `test_golden_vectors.py::test_variant_min_instead_of_max_picks_wrong_winner` |
| `mutant_in_place_sequential_step` | in-place update, no snapshot | `test_mutants.py::test_mutant_in_place_update_violates_snapshot_semantics` |
| `mutant_duplicate_source_proposals` | source duplicated via aliasing | `test_mutants.py::test_mutant_duplicate_source_aliasing_is_detected_by_harness` |
| `mutant_signed_priority_arbitrate` | signed priority comparison | `test_mutants.py::test_mutant_signed_priority_picks_wrong_winner`, `test_golden_vectors.py::test_variant_signed_comparison_picks_wrong_winner` |
| `MutantStaleNextState` | stale next-state initialization | `test_mutants.py::test_mutant_stale_next_state_reverts_untouched_field` |
| `mutant_wrong_direction_step` | wrong direction encoding | `test_mutants.py::test_mutant_wrong_direction_encoding_targets_wrong_cell` |
| `mutant_global_arbitration_step` | global instead of per-field arbitration | `test_mutants.py::test_mutant_global_arbitration_drops_a_genuinely_independent_field` |
| `mutant_priority_payload_swap_step` | correct winner, wrong payload committed | `test_mutants.py::test_mutant_priority_payload_swap_writes_wrong_value` |
| `mutant_priority_missing_wrap` / `_mix_no_wrap` | uint64 wrap omitted | `test_mutants.py::test_mutant_missing_uint64_wrap_diverges_from_frozen_vector`, `test_golden_vectors.py::test_variant_missing_uint64_wrap_diverges_on_baseline_vector` |

`test_golden_vectors.py` additionally kills 5 priority-level variants
not listed above (not full mutants, just broken `arbitration_priority`
call shapes): missing seed, missing tick, missing target coordinate,
missing target field, missing source coordinate, and 32-bit coordinate
truncation -- each shown to diverge from a specific frozen vector
chosen so that component is non-zero/non-degenerate.

## Property-based tests (test 12) and results

5 Hypothesis properties in `test_properties.py`, each `max_examples=300`
(one at 200), generators biased toward WRITE-heavy, contested worlds,
`H,W` in `[1,5]` (stated bound). All passed: only winner-targeted
fields differ; no byte synthesis (single-tick and 4-tick chained);
enumeration-order independence; full replay-identical-input ->
identical-output. `test_differential_oracle.py` adds a 6th property
(300 examples) cross-checking the two independent oracles agree.
Total: **~1,900 Hypothesis-generated cases**, 0 failures, plus 4
hand-built differential fixtures.

## Statistical diagnostic (tests 20, 25): design and result

Preregistered in `test_statistical_diagnostics.py`'s module docstring
BEFORE `run_diagnostic()` is defined: 11 strata (all direction-combos of
arity 2, 3, 4 from {N,E,S,W}), N=300 independent contests/stratum
(fresh random seed+tick per contest), exact two-sided binomial test per
(stratum, slot) cell against the null p=1/arity, Bonferroni-corrected
family-wise alpha=0.01 across 28 cells (per-cell alpha ~= 0.000357).
**Measured result** (`python test_statistical_diagnostics.py`, this
exact frozen N): 0 of 28 cells flagged. This is a diagnostic statement
about this one sample, not a neutrality proof (stated explicitly in the
file): failing to reject H0 is not evidence of fairness, only that this
sample did not detect deviation at this power. No Runpod credit spent.

## Discrepancies/ambiguities discovered in aeth00.v1 (none blocking)

1. AETHER_SPEC.md's "Invalid-input handling" paragraph explicitly
   covers dimensions and buffer length but does not explicitly state
   whether a `seed` or `tick` value supplied outside `[0, 2**64-1]` at
   construction time must raise. In a genuinely uint64-typed host
   language this can't occur; it's an artifact of Python's untyped
   integers. `Aeth00World.__init__` defensively raises `ValueError` for
   both, which is stricter than the frozen text requires but does not
   contradict it. No spec amendment is proposed; flagging only so a
   future production implementation makes the same choice deliberately.
2. Not a spec defect: the 5-step SplitMix64 chain (`h0..h3, priority`)
   is easy to miscount as 4 steps by hand (see golden-vector section
   above). The frozen text itself is unambiguous; this is a
   transcription pitfall for implementers, worth naming explicitly.

No contradiction was found. AETH-00A did not need to touch
`AETHER_SPEC.md`, `AETHER_TEST_PLAN.md`, or any other frozen document.

## Reproduction

```
cd Aether/test
python -m pytest -v
python test_statistical_diagnostics.py
```

## What remains intentionally absent

The production AETH-00 transition implementation (CPU or GPU), any
Runpod code, mutation/resource/heredity/observatory machinery, and any
generalized "future Aether" abstraction. Nothing in `Aether/test/`
imports or adapts code from BEE, NPE, SFE, or any other Prometheus
engine.
