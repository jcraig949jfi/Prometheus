# C-019-T020 Aether post-confirmation replay audit

Cadmus[harry1-c619844e], claude-sonnet-5-5 (Q2). This is a POST-CONFIRMATION audit, separate from C-018's frozen confirmation. It modifies nothing
under `rso/aether/` outside `rso/aether/audit/`: `runs/`, `RESULT.md`, `FROZEN.json`, every pinned file and the decision rule are untouched. It does not replace the result.

## 1. Outcome (directive s1, D1)

**All 57 re-executed units MATCH.** For every one of the 57 units not previously fully replayed, the natively regenerated arrays reproduce the committed `arrays_sha256`
digest, each of the first-divergence arrays `ftick_cutB` and `ftick_cutN` is element-for-element equal, the meta fields `tree / B / N / origin / B_tick` and the warm digest
are equal, and the meta digest equals the shard row's `meta_sha256`. Together with the 6 preregistered sample replays and the integrator's RX 8201 replay, **all 64 units
(and all 8 CONFIRMED units) are now fully replayed**.

> The committed clamp evidence is reproducible under the pinned native execution implementation. This closes the R1c missing-replay exposure within that trust boundary
> and does NOT prove the native transition physics correct.

No MISMATCH, so no QUALIFICATION WARNING is issued. Recomputed classes: 0 of 57 changed. The RX and V1 dispositions recomputed from replayed evidence equal the committed ones (s5).

## 2. Erratum to the C-018 report (record; provenance preserved)

The original report (`rso/aether/RESULT.md` / challenge R2 REPORT) says that one of the eight CONFIRMED units was fully replayed. The correct count after the integrator's additional work is **two**:
RX 8228 (the preregistered RX.3 sample, `rso/aether/runs/meta/analyse_full.out`, `full_replay_verified: 6`) and RX 8201 (the integrator's re-execution recorded in the
`INTEGRATED` history entry of `ops/campaigns/C-018/tasks/C-018-T050/TASK.json`, 2026-10-12T19:36:55Z, repository commit 85e0cd7fb; `arrays_sha256`
`567d483e33d6b847f8d33049d557ee4d5afc988f208e09c4ecc4b2d5845c5fce`, equal to the committed digest of `native_RX_8201`; B and N equal). The original text is not edited; this erratum supersedes the count only.
After this audit the count is **eight of eight**.

## 3. Pins

- Production source revision: the confirmatory run commit `fa0347fd22a85f6baf5413bb3a000bf4c7039a3f` (C-018-T050); the release `rso/aether/RELEASE.json` names `frozen_json_commit` `1f2d2444f52a8c2411ee2b1d1032b1b4a7da0be3`.
- `rso/aether/FROZEN.json` at `1f2d2444f`: git blob `69b1a66c237f0b32761454d55902d80fdf6ad7da`; sha256 of its LF bytes `9fe0fcb4e2ab59f1547d36652141d90380d81771495180b970a3802e8382d306`
  (= `RELEASE.json frozen_json_sha256_lf`; the packet's "9fe0fcb4" is this sha256). The same blob is on origin/main efe7bddc7.
- Aether source pin: the `Aether/...` entries of `FROZEN.json` (`Aether/V2B/PROP01/prop01_run.py`, `prop01_tree.py`, `REACH01/R1/r1_reduce.py`, `r1_test4.py`, `Aether/observatory/*`, `Aether/test/reference/gpu_aeth01.py`),
  and `rso/aether/adapter.py` sha256 `2427a6132b87113bdc57f0a93bcafbffc6a22759196b372c9f568edf45f83474`.
  `rso.aether.freeze.mismatches()` returned `[]` on the audit worktree (origin/main efe7bddc7): every pinned file is byte-identical to its frozen hash.
- Design manifest sha256 `d9e8f885c8d43a237854359c7a8ef7394485bc69483600c43d220821314c8d47`. Python 3.12.10, numpy 2.4.3, Windows (harry1), CPU reference path.

## 4. Method

- Script: `rso/aether/audit/replay_audit.py` (`run`, `aggregate`). Inputs per unit are its committed meta: law, seed, n, warm, H (128 / 300 / 400 throughout). The call is `rso.aether.adapter.native_unit(law, seed, n, warm, H)`, which calls Aether's own
  `law_step` / `run_unit` and is the same call `confirm analyse` makes for its sample (`confirm.py:214`). **No new seeds**; committed evidence is only read; nothing is repaired.
- Per unit the record (`rso/aether/audit/replay/<law>_<seed>.json`) holds both `arrays_sha256`, equality of every array in the file (snap, imp, ftick_impulse, ftick_cutB, ftick_cutN, H, D), equality of `ftick_cutB` / `ftick_cutN` separately (with the count of differing sites),
  the meta fields `tree / B / N / origin / B_tick`, the warm digest, the meta digest, and CPU. A unit is MATCH only if all of those hold.
- Classes: `rso.aether.evaluate.evaluate_unit` (the frozen evaluator, imported read-only) on the REPLAYED arrays and meta, tabulated beside the committed class; law summaries via `evaluate.law_summary` / `disposition` (the code `confirm analyse` uses). The 7 already-replayed units use
  their committed arrays (their replay digests already equalled the committed ones). Replayed arrays are local scratch (`audit/replay_arrays/`, git-ignored, 23 MB); the digests and per-unit records are committed.
- Execution: one DETACHED process (PowerShell `Start-Process`, PID 8916, logs `replay_run.out` / `replay_run.err`), command line `python -B -m rso.aether.audit.replay_audit run` with `EW_DB_HOST=192.168.1.202`, working directory the audit worktree; restartable (units with a record are skipped).
  The first unit (RX 8193) ran in the foreground as a timing check. Tables: `python -B -m rso.aether.audit.replay_audit aggregate`, then `python -B -m rso.aether.audit.render_audit`.
- CPU: 4671 s process CPU over the 57 replays (mean 82 s/unit, one process; the second harry1 slot ran T021's small jobs). No M2, no paid compute.

## 5. Law-level dispositions recomputed from replayed evidence (POST-CONFIRMATION; separate from the C-018 result)

| law | source | CONFIRMED / CONTROL_VACUOUS / INSUFFICIENT / NOT_INTERVENTIONAL / NO_CUT / NONSPECIFIC / MULTI_SOURCE | evaluable | confirmed r>=2 | reach band | content excess | pooled agreement | disposition |
|---|---|---|---|---|---|---|---|---|
| RX | committed (C-018) | 8 / 8 / 3 / 5 / 24 / 0 / 0 | 13 of 48 | 8 | 6 | 0.0135 | 0.7475 | CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT |
| RX | replayed (post-confirmation) | 8 / 8 / 3 / 5 / 24 / 0 / 0 | 13 of 48 | 8 | 6 | 0.0135 | 0.7475 | CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT |
| V1 | committed (C-018) | 0 / 0 / 3 / 0 / 13 / 0 / 0 | 0 of 16 | 0 | 0 | -- | -- | ANCESTRY_UNEVALUABLE |
| V1 | replayed (post-confirmation) | 0 / 0 / 3 / 0 / 13 / 0 / 0 | 0 of 16 | 0 | 0 | -- | -- | ANCESTRY_UNEVALUABLE |

Class and disposition changes: none. Full structure in `rso/aether/audit/TABLES.json`.

## 6. Per-unit table (64 units; arrays_sha256 prefixes of 12 hex; full digests in the per-unit records and `runs/`)

MATCH = arrays_sha256 equal AND ftick_cutB / ftick_cutN equal AND tree / B / N / origin / B_tick, warm digest and meta digest equal.

| law | seed | committed arrays_sha256 | replayed arrays_sha256 | result | committed class | class from replayed arrays |
|---|---|---|---|---|---|---|
@@UNIT_ROWS@@

## 7. What this does and does not establish

- Establishes: the committed `ftick_cutB`, `ftick_cutN`, trees, B/N selections and warm digests for all 64 units are what Aether's pinned native path produces again from the recorded inputs, on this host, under the stated pins; the eight CONFIRMED classes (and so the RX disposition) do not depend on an unreplayed unit.
- Does NOT establish: that the native transition law (`law_step`) is correct; independence from the adapter (the replay uses the same `native_unit` call); cross-platform or GPU equivalence (CPU reference path only); anything about content or discovery.
- Limitations: replay of a deterministic function is a reproducibility check, not a second implementation; N is the adapter's non-ancestor rule on the same tree (challenge R2 limitation unchanged); the challenge R2 REPORT s5 text items are not re-adjudicated here.
