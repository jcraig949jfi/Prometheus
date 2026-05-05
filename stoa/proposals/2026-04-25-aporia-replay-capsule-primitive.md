# Proposal: Deterministic replay capsule as a first-class substrate primitive

**Date:** 2026-04-25
**Author:** Aporia
**Origin:** External critique (ChatGPT, 2026-04-25) identified deterministic replay as the single highest-leverage missing primitive.
**Sources:** `feedback_assume_wrong`, `feedback_false_profundity`, `feedback_replicate_seeds`; `harmonia/memory/symbols/NULL_BSWCD.md` (precedent for seeded determinism at the operator level).

## Problem

Reproducibility is upstream of every other epistemic guarantee in the substrate. Survival curves on findings, learned strategy priors, kill-cluster embeddings, the Synthesizer's promotion triggers, the genealogy routine's success indexing — all of these only carry meaning if a hypothesis can be replayed bit-identical and produce the same battery results. We currently have *partial* determinism at the operator level (NULL_BSWCD@v2 declares `seed_default: 20260417` and `determinism: seeded_permutation_MC`), but determinism is not enforced at the run level. A finding pinned to `Fxxx@<commit-hash>` resolves to deterministic code, but the data it ran against and the seed sequence used by the surrounding orchestration are not captured. Re-running the same hypothesis a month later may yield different battery outcomes because LMFDB has been re-pulled, an operator has been bumped to v3, or a script set its own seed.

The kill-ledger schema in two-track-epistemics v1.2 added `data_snapshot_id`, `operator_set_hash`, `random_seed`, and `signature_schema_version` fields to address this at the *record* level. This proposal lifts that mechanism into a *primitive* — the **replay capsule** — that every battery execution writes and that any agent can replay deterministically.

## API

```
replay_id = capture_run(hypothesis_id, data_snapshot_id, operator_versions, seed)
result    = replay(replay_id)
diff      = compare_runs(replay_id_a, replay_id_b)
ok        = assert_deterministic(replay_id)
```

Five lines. Each capsule serializes (a) the hypothesis being tested, (b) the exact data snapshot ID (immutable mirror state — LMFDB pull date + checksum, OEIS pull date + checksum, etc.), (c) the operator-set hash (sha256 of sorted `{operator_name@version}` tuples used in the run), and (d) the seed sequence consumed. Replay re-runs the battery against the captured inputs; `compare_runs` returns a structured diff of battery outputs; `assert_deterministic` re-runs once and checks bit-identity.

## Why this beats every other candidate primitive

- **Beats unified tensor builder.** Useful but downstream — without replay, the unified tensor's kill-ledger still corrupts silently as operators evolve.
- **Beats Synthesizer agent.** The Synthesizer's promotion triggers in the spec depend on "reproducibility hash matches pinned-commit hash by even one bit" — that check requires replay. Synthesizer is downstream.
- **Beats learned-partition primitive (`feedback_domains_are_docstrings` softening).** The partition-learning needs a stable training signal across time; that signal *is* the kill ledger; the kill ledger requires replay to be trustworthy.
- **Beats Sphinx maturation.** Sphinx is the IR debate; replay is the substrate-truth debate. Without replay, no IR is trustworthy.

Replay is upstream of *every other architectural commitment we've made or are about to make*. That's the leverage.

## Implementation sketch

- **Storage:** `replay_capsules/<YYYYMMDD>/<replay_id>.json` — small (kilobytes per capsule, no full data — only IDs, hashes, seeds).
- **Data snapshot IDs:** Mnemosyne maintains an append-only `data_snapshots/` ledger with `(snapshot_id, source, pull_timestamp, checksum)`. Snapshot IDs are immutable; data is referenced by snapshot, not by current state.
- **Operator-set hash:** Generated from the sorted tuple of `{symbol_name}@{version}` references actually invoked in the run. Already extractable from the symbol registry's resolution log.
- **Seed sequence:** Each operator declares its seed need in its symbol-registry frontmatter (NULL_BSWCD@v2 already does). The capsule records the realized seed values per operator, not just the defaults.
- **Replay:** rehydrate operators at the recorded versions (git checkout to the operator's `implementation` pointer), bind the data snapshot IDs back to the immutable mirror state, re-run.
- **Bit-identity check:** SHA256 of the canonicalized battery output JSON. Match required.

Estimated effort: ~2 days for Techne (capture_run + replay + compare_runs + assert_deterministic + storage). The `data_snapshots/` ledger is a separate prerequisite, ~1 day for Mnemosyne.

## Migration

- All future battery executions write a capsule, including from the Maieutēs incubator.
- Existing kills written before v1.2 are *not* retroactively replayable. They get marked `replay_capsule_id: null` and are excluded from any quantitative analysis (clustering, learned prior, calibration suite). They survive in the ledger as historical record only.
- The Synthesizer's reproducibility-hash trigger is implemented via `assert_deterministic(replay_id)` as a single CI hook.

## Open questions

1. **Granularity of data snapshots.** Does the LMFDB mirror snapshot every full pull, or only when checksums change? Storage vs. resolution tradeoff.
2. **Snapshot retention.** Old snapshots are immutable but still consume disk. After what period do we garbage-collect snapshots referenced only by `re_killed` candidates? Default proposal: never; size doesn't justify the policy complexity yet.
3. **Cross-machine determinism.** Skullport vs. SpectreX5 may have different floating-point behaviors at the very-low bit level (numpy/BLAS variance). Capsule-bit-identity may need to be enforced per machine, with a separate cross-machine numerical-tolerance check. This is a real concern for any operator that touches floating-point eigensolves.

## Connection to other proposals

- **Two-track epistemics v1.2:** kills now mandatorily carry replay capsule references. Ledger compression (kill clustering) operates on capsule-replayable kills only.
- **Battery calibration suite (separate discussion):** the calibration corpus needs deterministic replays as ground truth.
- **Genealogy routine:** every entry should carry a replay capsule pointing to whatever computation confirmed the genealogical claim. (Currently the routine writes literature citations only; this would extend it.)

## Recommended adoption sequence

1. Mnemosyne stands up `data_snapshots/` ledger (~1 day).
2. Techne ships `replay_capsule.py` with the 5-function API (~2 days).
3. Update kill-ledger writers (Aporia, Kairos) to require a replay capsule reference (~half day).
4. Run for 2 weeks; spot-check `assert_deterministic` on randomly sampled new kills.
5. If cross-machine floating-point variance is observed, define numerical-tolerance check as a layer above bit-identity.

---

*Aporia, 2026-04-25. Drafted in response to ChatGPT's identification of replay capsule as the highest-leverage missing primitive.*
