# Harmonia E Session Journal - 2026-04-26

## Restore

- Read `private_strategy/HarmoniaPrompts/Harmonia Starter Prompt 04-26-2026_latest.md`.
- Read `harmonia/memory/restore_protocol.md` v4.3.
- Attempted required Agora restore calls: `substrate_health()`, `queue_preview(limit=15)`, `tail_sync(10)`, and `resolve('SHADOWS_ON_WALL@v1')`.
- Redis at `192.168.1.176:6379` timed out both in the default sandbox and after escalation, so live Agora queue inspection and sync posting were blocked from this harness.
- Re-attempted the end-of-session `tail_sync(20)`, `queue_preview(15)`, and `HARMONIA_E_STATUS` post with a raw Redis client and 1-second socket timeout after REQ-026 completion; all three returned `TimeoutError: Timeout connecting to server`.

## Forging: REQ-026 / TOOL_SAT_SOLVER

Delivered:

- `techne/lib/sat_solver.py`
- `techne/tests/test_sat_solver.py`
- `techne/inventory.json` entry for `TOOL_SAT_SOLVER`
- `techne/queue/requests.jsonl` status changed to `fulfilled`

Interface:

```python
solve_cnf(clauses: list[list[int]], solver: str = "kissat", timeout: float | None = None) -> dict
```

Behavior:

- Accepts DIMACS-style integer-literal CNF as `list[list[int]]`.
- Returns `{'satisfiable': True|False|None, 'model': list[int] | None, 'stats': dict}`.
- `None` is used only for timeout/interrupted solves, with `stats['timed_out'] == True`.
- Records requested solver, realized backend, clause count, variable count, elapsed seconds, timeout, and PySAT accumulator stats where exposed.

Backend note:

- `python-sat` / PySAT was already installed.
- PySAT exposes `kissat404`, `glucose3`, and other solvers.
- On this Windows harness, `kissat404` segfaulted on the small Caccetta-Haggkvist UNSAT certificate during testing. The wrapper therefore treats `solver='kissat'` as a stable alias that falls back to `glucose3` on Windows and records `requested_solver='kissat'`.
- No solver binaries were downloaded or committed.

Validation:

- Focused SAT tests: `4 passed`.
- Full Techne suite: `123 passed, 1 warning`.
- Calibration anchors:
  - 3-SAT satisfiable instance with returned model verified against all clauses.
  - 3-SAT unsatisfiable instance.
  - Small Caccetta-Haggkvist certificate: no digraph on 5 vertices with min outdegree 2 and no directed cycles of length <= 3.
  - Timeout behavior via immediate interruption.

## Handoff

Completed:

- REQ-026 forged and locally fulfilled.
- Tests pass.

In flight:

- Agora status post remains pending because Redis connection timed out from this harness.

Next unblock:

- Restore network path to `192.168.1.176:6379`, then post `HARMONIA_E_STATUS` to `agora:harmonia_sync` and rerun `tail_sync(20)` / `queue_preview(15)`.

## Forging: REQ-027 / TOOL_TT_SPLICE

Delivered:

- `techne/lib/tt_splice.py`
- `techne/tests/test_tt_splice.py`
- `techne/inventory.json` entry for `TOOL_TT_SPLICE`
- `techne/queue/requests.jsonl` status changed to `fulfilled`
- `scripts/harmonia_e_status_post.py` with the intended `HARMONIA_E_STATUS` payload for a network-connected shell

Interface:

```python
tt_splice_compatibility(
    region_a_npz: Path,
    region_b_npz: Path,
    prime_detrend: bool = True,
    null_perms: int = 300,
    seed: int = 20260417,
) -> dict
```

Behavior:

- Loads NPZ tensors using key `data` when present, otherwise the first numeric array with `ndim >= 2`.
- Computes independent and joint TT bond ranks via deterministic dense SVD unfoldings.
- Applies leading-axis log-prime-density residual detrending by default.
- Emits a `PATTERN_PRIME_GRAVITATIONAL_OVERFIT` warning when `prime_detrend=False`; no silent skip.
- Runs a permutation null by shuffling region B along the splice axis and reports empirical `audit['null_p_value']`.
- Returns `bond_ranks`, `compatibility_score` in `[0, 1]`, inferred `bridge_operators`, and the required audit fields.

Validation:

- Focused TT splice tests: `5 passed, 1 skipped`.
- Full Techne suite: `128 passed, 1 skipped, 1 warning`.
- Full-suite note: Hypothesis exposed an existing `TOOL_MAHLER_MEASURE` tiny-batch precision edge (`companion_batch` differed from scalar by ~1.6e-8). Fixed narrowly by routing tiny companion batches through the scalar-equivalent path; scan-scale batch path remains unchanged.
- Synthetic anchors:
  - Known low-rank shared factor scores high and emits `LOW_RANK_SHARED_FACTOR`.
  - Random Gaussian tensor pair scores low with null p-value > 0.05.
  - Self-splice scores exactly `1.0`.
  - Same seed gives identical bond ranks and null p-value.
  - Prime detrend warning fires when disabled.

Real-data smoke note:

- `ergon/tensor.npz` exists and has key `data` with shape `(4755770, 208)`.
- It is a large object-feature matrix, not a pair of extracted per-region tensors. The smoke test inspects and documents the schema, then skips to avoid materializing the full matrix. Next user of the tool should extract per-region slices before calling `tt_splice_compatibility`.

Handoff:

- REQ-027 forged and locally fulfilled.
- Redis remains unreachable from this harness. Run `python scripts/harmonia_e_status_post.py` from a network-connected shell to post the status payload.
- Next queue pick per conductor instruction: REQ-031 `TAIL_VS_BULK_DECOMPOSITION`.

## Forging: REQ-031 / TAIL_VS_BULK_DECOMPOSITION

Delivered:

- `techne/lib/tail_vs_bulk.py`
- `techne/tests/test_tail_vs_bulk.py`
- `techne/inventory.json` entry for `TAIL_VS_BULK_DECOMPOSITION`
- `techne/queue/requests.jsonl` status changed to `fulfilled`
- `scripts/harmonia_e_status_post.py` updated with the REQ-031 status payload

Interface:

```python
decompose_spectral(
    spectral_signal: np.ndarray,
    tail_threshold: float | str = "auto",
    null_model: callable | None = None,
    n_perms: int = 300,
    seed: int = 20260417,
) -> dict
```

Behavior:

- Splits by spectral coordinate tail, not magnitude tail. Default `"auto"` uses threshold `0.95`.
- Returns `tail_signal`, `bulk_signal`, independent `tail_battery_scores` / `bulk_battery_scores`, `agreement_score`, and provenance audit fields.
- Built-in battery is a documented placeholder until a substrate `battery_apply` callable exists. It returns `effect_size`, `p_value`, and `pattern_flags`.
- `null_model` callable hook is supported with contract `callable(signal, mask, rng, n_perms) -> {effect_size, p_value, pattern_flags}`.

Validation:

- Focused tail-vs-bulk tests: `6 passed`.
- Full Techne suite: `134 passed, 1 skipped, 1 warning`.
- Synthetic anchors:
  - Strong tail / flat bulk: low agreement, tail promotes, bulk fails.
  - Strong bulk / flat tail: low agreement, bulk promotes, tail fails.
  - Strong tail and bulk: high agreement, both promote.
  - Pure noise: both fail.
  - Same seed: bit-identical decomposition and scores.

Known issue:

- The tail/bulk threshold is a calibration parameter. It still needs calibration against F011's actual spectral structure before being treated as a durable battery threshold.

Handoff:

- REQ-031 forged and locally fulfilled.
- Redis remains unreachable from this harness; run `python scripts/harmonia_e_status_post.py` from a network-connected shell to post the REQ-031 status payload.
- Next queue pick if continuing: REQ-029 `TOOL_SDP_RELAX`.
