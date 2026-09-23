# AETH-00B -- minimal production CPU implementation (receipt)

Baseline: frozen semantics `aeth00.v1` (commit `3ff4619de`); AETH-00A
oracle/test layer (commit `2d2468965`, 55 tests, 0 failures).

## Production files added

- `Aether/production/__init__.py` -- package marker (5 lines).
- `Aether/production/aeth00.py` -- the implementation (230 lines).

No existing file was modified except `Aether/test/` additions below.

## Exact public API

```
State(H, W, data)                     # H,W int; data byte-exact, len==H*W*4
State.cell(row, col) -> (opcode, arg0, arg1, payload)
step(state, seed, tick, trace=None) -> State   # new State; state untouched
arbitration_priority(seed, tick, target_row, target_col, target_field,
                      source_row, source_col) -> int
InvalidStateError(ValueError)          # bad input at the API boundary
TickOverflowError(OverflowError)       # step() from tick == 2**64-1
SEMANTICS_ID = "aeth00.v1"; WRITE_OPCODE = 0x01; NORTH/EAST/SOUTH/WEST = 0..3
```

`State` carries no seed/tick/history; both are supplied fresh to every
`step()` call (no hidden state, per instructions). No campaign runner,
simulation class, plugin system, organism abstraction, GPU layer, or
ISA dispatch framework exists.

## Independence statement

`production/aeth00.py` imports nothing from `reference.oracle`,
`reference.oracle_independent`, `reference.mutants`, or
`reference.golden_vectors`. Beyond not importing, its algorithm is a
different SHAPE from both reference oracles:

- `reference/oracle.py` and `reference/oracle_independent.py` are both
  **scatter** implementations: decode every WRITE cell's one proposal
  first, then group proposals by target for arbitration.
- `production/aeth00.py` is a **gather** implementation: for every
  (target cell, target field) it inspects only that target's up to 4
  physical von Neumann neighbors and asks whether each neighbor's own
  (opcode, arg0, arg1) actually addresses this (target, field) --
  directly realizing AETHER_SPEC.md's non-normative "Deferred
  implementation guidance" paragraph ("one owner per target cell ->
  inspects its up to 4 neighbor sources"), applied here to CPU.

A structural consequence, not a bolted-on check: because each physical
cell has exactly one `arg0` value, it can satisfy the "required
direction" test of at most one of the 4 neighbor slots for at most one
target overall (proof in `_NEIGHBOR_SLOTS`'s docstring). "One proposal
maximum per physical source" therefore holds by construction in
production; unlike the reference oracles/test harness, production
needs no `assert_no_duplicate_sources`-style runtime defect detector
(that detector's job, per AETHER_SPEC.md, is to catch a defective
*candidate* implementation -- production's own algorithm cannot
produce the shape of bug it detects).

Literal constants shared with the reference oracles (the two SplitMix64
multipliers, the seed XOR constant, opcode/direction/field encodings)
are frozen protocol constants transcribed independently from
`AETHER_SPEC.md` itself, not copied from oracle code.

## Files added under `Aether/test/`

- `conftest.py` -- test-infrastructure only: puts the `Aether/`
  directory on `sys.path` so `production` is importable; does not
  touch `reference`'s existing import mechanism.
- `test_production_conformance.py` -- State validation, seed/tick
  validation, tick-overflow rejection, all 14 `PRIORITY_VECTORS`, the
  signed/unsigned fixture, the 2-/3-way `WINNER_VECTORS` (checked via
  `arbitration_priority` + the one-line "greatest wins" reduction,
  since those two fixtures' sources are not physical neighbors of
  their target -- they test the raw math only, exactly as
  `reference/golden_vectors.py`'s own docstring describes them), the
  4-way `WINNER_VECTORS` fixture (checked at the full `step()`/grid
  level, since it IS four genuine physical neighbors), and trace tests.
- `test_production_differential.py` -- explicit hand fixtures plus the
  large-volume randomized differential property.

## Test results (red/green discipline followed)

1. `test_production_conformance.py` written first; first run failed on
   `ModuleNotFoundError: No module named 'production'` (red, confirmed).
2. `production/aeth00.py` implemented; conformance tests turned green.
3. Full existing AETH-00A suite re-run **unchanged**: still 55 passed.
4. `test_production_differential.py` added and run against both oracles.
5. Full mutant-kill suite (`test_mutants.py` + `test_golden_vectors.py`,
   23 tests) re-run unchanged: still all pass -- production code did
   not weaken or bypass any adversarial test.

**Final full-suite run:** `python -m pytest -q` from `Aether/test`:
**85 passed, 0 failures**, wall time ~796s (dominated by the 100,000-case
differential property below; pure Python, CPU only).

## Differential-case count and failures

- Explicit hand fixtures (`test_production_differential.py`): 9,
  covering H=W=1 self-targeting, H=W=2 pairwise aliasing, ordinary 3x3
  and 7x9 (mixed RESERVED_INERT/WRITE), dense 4-way collisions on one
  field across a whole 4x4 torus, RESERVED_INERT-heavy (2 WRITE cells
  in 36), same-value writes, independent 4-field contest on one
  target, and high-bit seed (`2**64-1`, `2**63`) / high-bit and
  max-valid tick (`2**64-2`, `2**63`). All 9: production, primary
  oracle, and independent oracle bytes identical. 0 failures.
- Randomized property (`test_property_production_agrees_with_both_
  oracles_on_random_worlds`, H,W in [1,5], WRITE/contest-biased):
  **100,000 generated cases**, each comparing production against BOTH
  `reference.oracle.Aeth00World.step()` and
  `reference.oracle_independent.step_bytes()` simultaneously. **0
  failures.**
- Trace-equivalence property (`test_production_conformance.py`):
  3,000 additional generated cases confirming trace-enabled and
  trace-disabled `step()` produce byte-identical next states.
- **Total new AETH-00B generated cases: 103,000** (exceeds the
  100,000 engineering stress target). Combined with AETH-00A's ~1,900:
  **~104,900 generated cases across the full suite, 0 failures.**

## Mutant status

All 9 required mutant bug shapes (`reference/mutants.py`) and all
golden-vector defect variants in `test_golden_vectors.py` remain
**killed**, unchanged from AETH-00A (23/23 tests pass). Production code
does not import or touch any mutant, so this rerun is a pure
regression check that adding production code left the AETH-00A
adversarial layer untouched.

## Golden-vector status

All 14 `PRIORITY_VECTORS`, the `SIGNED_VS_UNSIGNED_VECTOR`, and all 3
`WINNER_VECTORS` match production (2-/3-way via the priority
function + reduction; 4-way via full `step()`). 0 mismatches.

## Trace-enabled/disabled equivalence

Confirmed by one explicit contested fixture (2 competing neighbors, 1
RESERVED_INERT non-proposer, 1 same-value win) and by 3,000
Hypothesis-generated cases: `step(state, seed, tick, trace=[])` and
`step(state, seed, tick, trace=None)` always return `State`s with
identical `.data`. All three required event kinds
(`proposal_emitted`, `proposal_won`, `stored_bits_changed`) are
present and distinct in the traced run; a same-value winning proposal
is confirmed to report `stored_bits_changed=False`.

## Validation behavior for invalid inputs

- `H` or `W` outside `[1, 2**32-1]`, non-int, or `bool`: `InvalidStateError`.
- `data` length != `H*W*4`: `InvalidStateError`.
- `data` containing a value outside `[0,255]` or non-int elements: `InvalidStateError`.
- `seed` or `tick` outside `[0, 2**64-1]`, non-int, or `bool`: `InvalidStateError`.
- `tick == 2**64-1` at `step()`: `TickOverflowError` (rejected, never wrapped).
- `state` not a `State` instance at `step()`: `InvalidStateError`.

All validation happens at the API boundary before any transition
computation begins.

## Basic CPU benchmark (baseline only, not optimized)

Measured with a transient, uncommitted script (`_bench_tmp.py`, deleted
after use), pure Python 3.13, single-threaded, CPython, this machine:

| H | W | cells | ticks | elapsed | ticks/s | cell-steps/s |
|---|---|---|---|---|---|---|
| 4 | 4 | 16 | 2000 | 0.108s | 18,593 | 297,482 |
| 16 | 16 | 256 | 500 | 0.386s | 1,295 | 331,624 |
| 64 | 64 | 4,096 | 50 | 0.704s | 71.0 | 290,911 |
| 128 | 128 | 16,384 | 10 | 0.558s | 17.9 | 293,664 |

Throughput is roughly flat at ~290-330K cell-steps/second regardless
of world size (the O(16*H*W) gather loop is the dominant cost; no
optimization attempted, per instructions). This is the CPU baseline
for later GPU comparison, not a performance claim.

## Discrepancy discovered (found and fixed within AETH-00B, not a spec contradiction)

While implementing `State.__init__`'s validation, `bytes(data)` was
initially the sole normalization step. Python's `bytes(n)` for an
integer `n` silently builds an `n`-byte all-zero buffer instead of
raising -- so `State(1, 1, 4)` would have silently succeeded (`4 ==
H*W*4`) with a caller's plain integer mistaken for byte content. Fixed
by explicitly rejecting `isinstance(data, int)` before the `bytes()`
conversion, with a regression test
(`test_state_rejects_bare_int_data_instead_of_treating_it_as_a_length`).
This is an implementation-validation gap caught before freeze, not an
ambiguity in `aeth00.v1` itself -- no spec amendment proposed.

Separately, note (not a defect): the "signed vs. unsigned priority
comparison" mutant class demonstrated in `reference/mutants.py` cannot
occur by accident in this production module, because Python has no
native fixed-width integer type -- every value here is Python's
arbitrary-precision, always-non-negative-after-masking `int`; a signed
misinterpretation would require deliberately-written sign-extension
code, which this implementation does not have anywhere.

## What remains deliberately absent

GPU implementation, Runpod code, campaign/simulation/plugin/organism
abstractions, generalized "future Aether" framework, observatory
infrastructure, mutation/resource/heredity machinery, and any
performance optimization of the CPU path.

## Reproduction

```
cd Aether/test
python -m pytest -q                                   # full suite, ~13 min
python -m pytest test_production_conformance.py -v    # fast, ~18s
python -m pytest test_production_differential.py -v -k "not property"  # fast hand fixtures
```
