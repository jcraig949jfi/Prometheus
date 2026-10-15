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
| RX | 8192 | c768c674a205 | (prior full replay, not re-run) | MATCH (prior) | NO_CUT | NO_CUT |
| RX | 8193 | 385239de7b4f | 385239de7b4f | MATCH | NO_CUT | NO_CUT |
| RX | 8194 | 33affdd97770 | 33affdd97770 | MATCH | NO_CUT | NO_CUT |
| RX | 8195 | 46301a64be8c | 46301a64be8c | MATCH | CONTROL_VACUOUS | CONTROL_VACUOUS |
| RX | 8196 | d6e6b1493177 | d6e6b1493177 | MATCH | NO_CUT | NO_CUT |
| RX | 8197 | f6bfe2c96816 | f6bfe2c96816 | MATCH | NO_CUT | NO_CUT |
| RX | 8198 | 6a52a567a81d | 6a52a567a81d | MATCH | NO_CUT | NO_CUT |
| RX | 8199 | e81d7ab93dcf | e81d7ab93dcf | MATCH | NOT_INTERVENTIONAL | NOT_INTERVENTIONAL |
| RX | 8200 | 92792ae0ab36 | 92792ae0ab36 | MATCH | NOT_INTERVENTIONAL | NOT_INTERVENTIONAL |
| RX | 8201 | 567d483e33d6 | (prior full replay, not re-run) | MATCH (prior) | CONFIRMED | CONFIRMED |
| RX | 8202 | 020a7f35a8fb | 020a7f35a8fb | MATCH | NOT_INTERVENTIONAL | NOT_INTERVENTIONAL |
| RX | 8203 | ecb8788c1cb5 | ecb8788c1cb5 | MATCH | NOT_INTERVENTIONAL | NOT_INTERVENTIONAL |
| RX | 8204 | dd744dd02b5b | (prior full replay, not re-run) | MATCH (prior) | NO_CUT | NO_CUT |
| RX | 8205 | ad6b818ab113 | ad6b818ab113 | MATCH | NO_CUT | NO_CUT |
| RX | 8206 | cdf5ec1ea574 | cdf5ec1ea574 | MATCH | NO_CUT | NO_CUT |
| RX | 8207 | 33829bbe0a31 | 33829bbe0a31 | MATCH | CONFIRMED | CONFIRMED |
| RX | 8208 | aad8a0b0defd | aad8a0b0defd | MATCH | CONTROL_VACUOUS | CONTROL_VACUOUS |
| RX | 8209 | 8f2ab4c7c6b9 | 8f2ab4c7c6b9 | MATCH | NO_CUT | NO_CUT |
| RX | 8210 | 30ae1c64ca0d | 30ae1c64ca0d | MATCH | CONTROL_VACUOUS | CONTROL_VACUOUS |
| RX | 8211 | e6ea6e9b47b2 | e6ea6e9b47b2 | MATCH | CONTROL_VACUOUS | CONTROL_VACUOUS |
| RX | 8212 | c59ffd691309 | c59ffd691309 | MATCH | NO_CUT | NO_CUT |
| RX | 8213 | 6cb9114e4770 | 6cb9114e4770 | MATCH | NO_CUT | NO_CUT |
| RX | 8214 | e7cfa4173db6 | e7cfa4173db6 | MATCH | INSUFFICIENT | INSUFFICIENT |
| RX | 8215 | 5a03c86d9160 | 5a03c86d9160 | MATCH | NO_CUT | NO_CUT |
| RX | 8216 | 794f0388bed0 | (prior full replay, not re-run) | MATCH (prior) | CONTROL_VACUOUS | CONTROL_VACUOUS |
| RX | 8217 | c40fbe51dfc5 | c40fbe51dfc5 | MATCH | NO_CUT | NO_CUT |
| RX | 8218 | 94485042f806 | 94485042f806 | MATCH | NO_CUT | NO_CUT |
| RX | 8219 | f3bd675802e7 | f3bd675802e7 | MATCH | CONFIRMED | CONFIRMED |
| RX | 8220 | a483e53ef551 | a483e53ef551 | MATCH | INSUFFICIENT | INSUFFICIENT |
| RX | 8221 | 4216c50ff758 | 4216c50ff758 | MATCH | NO_CUT | NO_CUT |
| RX | 8222 | caa28e84aa4e | caa28e84aa4e | MATCH | CONTROL_VACUOUS | CONTROL_VACUOUS |
| RX | 8223 | e1e716b3f39a | e1e716b3f39a | MATCH | CONFIRMED | CONFIRMED |
| RX | 8224 | c1aef456ce52 | c1aef456ce52 | MATCH | NOT_INTERVENTIONAL | NOT_INTERVENTIONAL |
| RX | 8225 | 77cddff601d7 | 77cddff601d7 | MATCH | NO_CUT | NO_CUT |
| RX | 8226 | 66b5d4e8c1a7 | 66b5d4e8c1a7 | MATCH | CONFIRMED | CONFIRMED |
| RX | 8227 | 9f74ce2e2049 | 9f74ce2e2049 | MATCH | NO_CUT | NO_CUT |
| RX | 8228 | bf58e0eb1414 | (prior full replay, not re-run) | MATCH (prior) | CONFIRMED | CONFIRMED |
| RX | 8229 | 16766f53f50f | 16766f53f50f | MATCH | NO_CUT | NO_CUT |
| RX | 8230 | 7eea019f29f3 | 7eea019f29f3 | MATCH | NO_CUT | NO_CUT |
| RX | 8231 | 8ec7b5f3453c | 8ec7b5f3453c | MATCH | CONFIRMED | CONFIRMED |
| RX | 8232 | 9da8045ae27c | 9da8045ae27c | MATCH | NO_CUT | NO_CUT |
| RX | 8233 | 17b5406ab7b5 | 17b5406ab7b5 | MATCH | CONTROL_VACUOUS | CONTROL_VACUOUS |
| RX | 8234 | bf2c416e4b00 | bf2c416e4b00 | MATCH | NO_CUT | NO_CUT |
| RX | 8235 | efa793221027 | efa793221027 | MATCH | INSUFFICIENT | INSUFFICIENT |
| RX | 8236 | fa22fa337edb | fa22fa337edb | MATCH | CONTROL_VACUOUS | CONTROL_VACUOUS |
| RX | 8237 | e5f9efcf5a37 | e5f9efcf5a37 | MATCH | CONFIRMED | CONFIRMED |
| RX | 8238 | 145df92bf928 | 145df92bf928 | MATCH | NO_CUT | NO_CUT |
| RX | 8239 | a6ebb34d4812 | a6ebb34d4812 | MATCH | NO_CUT | NO_CUT |
| V1 | 8192 | 6a841d7a4ec5 | (prior full replay, not re-run) | MATCH (prior) | INSUFFICIENT | INSUFFICIENT |
| V1 | 8193 | 12559787d07f | 12559787d07f | MATCH | NO_CUT | NO_CUT |
| V1 | 8194 | d18bbe7ba6cc | d18bbe7ba6cc | MATCH | INSUFFICIENT | INSUFFICIENT |
| V1 | 8195 | cf3947ac950e | cf3947ac950e | MATCH | NO_CUT | NO_CUT |
| V1 | 8196 | ee07813f5dae | ee07813f5dae | MATCH | NO_CUT | NO_CUT |
| V1 | 8197 | 6a3f34697256 | 6a3f34697256 | MATCH | NO_CUT | NO_CUT |
| V1 | 8198 | 40d72dc3dd85 | 40d72dc3dd85 | MATCH | NO_CUT | NO_CUT |
| V1 | 8199 | be9f5c16a1a6 | be9f5c16a1a6 | MATCH | INSUFFICIENT | INSUFFICIENT |
| V1 | 8200 | 6a985c9c20fd | (prior full replay, not re-run) | MATCH (prior) | NO_CUT | NO_CUT |
| V1 | 8201 | 7e6b7e966dfa | 7e6b7e966dfa | MATCH | NO_CUT | NO_CUT |
| V1 | 8202 | f20d2c4b7426 | f20d2c4b7426 | MATCH | NO_CUT | NO_CUT |
| V1 | 8203 | 2fadbfdeaf29 | 2fadbfdeaf29 | MATCH | NO_CUT | NO_CUT |
| V1 | 8204 | 6f2e984d28c2 | 6f2e984d28c2 | MATCH | NO_CUT | NO_CUT |
| V1 | 8205 | 3ba83c29b4c2 | 3ba83c29b4c2 | MATCH | NO_CUT | NO_CUT |
| V1 | 8206 | ac0fb9df7d1f | ac0fb9df7d1f | MATCH | NO_CUT | NO_CUT |
| V1 | 8207 | d3bab517f606 | d3bab517f606 | MATCH | NO_CUT | NO_CUT |

## 7. What this does and does not establish

- Establishes: the committed `ftick_cutB`, `ftick_cutN`, trees, B/N selections and warm digests for all 64 units are what Aether's pinned native path produces again from the recorded inputs, on this host, under the stated pins; the eight CONFIRMED classes (and so the RX disposition) do not depend on an unreplayed unit.
- Does NOT establish: that the native transition law (`law_step`) is correct; independence from the adapter (the replay uses the same `native_unit` call); cross-platform or GPU equivalence (CPU reference path only); anything about content or discovery.
- Limitations: replay of a deterministic function is a reproducibility check, not a second implementation; N is the adapter's non-ancestor rule on the same tree (challenge R2 limitation unchanged); the challenge R2 REPORT s5 text items are not re-adjudicated here.
