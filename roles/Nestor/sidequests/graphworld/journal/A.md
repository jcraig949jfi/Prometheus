# Lane A journal (conductor + fabric)

## 2026-09-14 iteration 1 -- Nestor-A[m1-918ab2b0] (reconstructed by successor)
- Kit, bus, substrate and contract at a901ba0c9 (see roles/Nestor/journal/2026-09-14.md).
- A2: FalkorDB built from source on WSL ext4, BUILD_DONE 07:29, ~/lab/falkor-out/libfalkordb.so
  sha256 c495cae39faeb85a9b1674ee07940bb34e662142a051cbe0fc535e352495e0d9. No baseline bench yet.
- A3 quick (2000 x 4): lost 0 in all faults, cheat lost 400. Session ended 07:29 before commit.

## 2026-09-14 iteration 2 -- Nestor-A[m1-449a9e76]
- Post mortem of A and D: POSTMORTEM_2026-09-14_A_D.md. BOOT_CLONE step 1 + liveness fixed.
- Committed the predecessor's A3 code and quick rows as found. Added crash_after_commit_4p to the plan.
- Bounty audit: B-bounty-C1-cpu-d64r64 NOT scored. It is a PASS, not a KILL, and C1b (04ee00aa6)
  measured nb_bucket/numba_par = 1.01 idle in one interleaved process. B3g refutes B's own B2:
  a self-correction, not a bounty.
- A3 full run (10k x 4): lost 0 and chains verified 8/8, crash_after_commit dedups 200, cheat lost 400.
  Receipt PASS (rows 4cce561b5); no board metric fits; speed INDETERMINATE (shared host).
- Board audit 2: C7d's kill point removed (C retracted it: the target was the charge channel). Bounty open to B.
- A2: artifact recorded and smoke-tested (A2_BUILD.md). Baseline bench is the next A item, then A4.
- Liveness: D's new session is checking out its worktree (locked) at 11:45; no hello yet.

## 2026-09-14 quiesce (operator request), ~12:15 -- Nestor-A[m1-449a9e76]
- B: stopped, clean, pushed (tip 5cc6c19e4); substrate 6391 left running.
- C: stopped, clean, pushed (C7 line closed after C7e KILL); 6392 left running.
- D: rebooted as m1-5ab220e6 at ~11:48, D1 KILL (ea659043e), D1b KILL (c277e6e8b), paused; 6393 running.
  Next D item: D1c symbol-split move.
- E: E10 still RUNNING (pid 26576, started 11:16; 10/24 rows at 12:11), rows + e10_run.py
  uncommitted in gw-e. E owns the landing.
- Boards at quiesce: kills B 9 / C 6 / D 2; bounties B:B-bounty-C7d-charge-index 1 (audited, scored);
  steps_per_s_verified B1; branch_points_per_cpu_h E2b.
- A open items: A2 baseline bench, A4 CHIMERA-0 harness; Daedalus packet committed but not sent.

## 2026-09-14 ~14:10 -- landed profile fixes 1, 2, 6 (operator authorization 06)
- 18 Redis clients -> 127.0.0.1 (16 lane D/E files); test suite 39.8 s -> 25.1 s, 97 passed.
- cache=True on static njit kernels (B6 fused/probes, C row kernels); fused first call in a fresh process 6.21 s -> 0.32 s, fitness 517,984 unchanged.
- primordial/ops/warmup.py (0.55 s warm); tests/test_fabric_hygiene.py guards both. Dual-flag runtime kernels left uncached (cache collision risk).
- ROUND2_PREP_BACKLOG_2026-09-14.md: Phase 1 gate F1-F6, then F7-F15; open decisions D1-D4.

## 2026-09-14 ~16:05 -- round 2 gate F1-F6 and cohort layer (operator decisions 07)
- F1-F5 landed at 2d3122a5c: launcher log, liveness + reaper, heartbeat, bus to/inbox/tail/tag guard/burst/ANOMALY queue, receipt guard + host_load, RowWriter.
- F6: prepare_worktrees built nestor-r2-b sparse (588 files, checkout 0.3 s, warmup 6.8 s cold); the first verify caught the pre-commit probes needing ergon/probe (added).
- QD ledger seeded (21 round 1 baseline cells); 10 round 1 anomalies seeded OPEN on the live bus; draw_cell for the anti-prior cohort.
- SWARM_R2.md (cohorts, clause A binding, rules) and BOOT_R2.md (operator launch order + 4 paste blocks). Suite 112 passed.

## 2026-09-14 16:19-17:36 -- round 2 test launch 1 (2 epochs), conductor record
- Launch: operator on mobile; the Bash tool kills child processes, so wt.exe/Start-Process failed. One-shot /IT scheduled tasks worked (B 16:19, C 16:21, D 16:22, E 16:22), each task disabled after /Run. B's comms boot needed evidence_wiki (+archaeon); sparse set fixed before C-E.
- 37 receipts in pm:results (B 27, C 7 incl. C-R2-09 at 17:26, E 3 + E-T1 refile); D resolved 4 anomalies (0 receipts, 636 rows) and filed 3 children; anomaly queue 18 (14 OPEN).
- Liveness: 0 deaths; D and E flagged STALE once each while idle/paused.
- Quiesce posted 17:26; all four paused 17:29-17:36 with nothing unpushed.
- Carry-forward: w4 clause A near-degenerate (12 B abstain/fixed-action brain 97.2 vs 98.76); LuaArchive sampler unseeded (D4; E seeded sampler 33038855e); round 1 baselines need >=8 runs + IQR (B); my qd_ledger check front contamination fixed by E (edb064317).

## 2026-09-15 00:53 -- round 4 launch gate GREEN; cohorts launching (operator messages 13, 14)

- Rulings: Q1 gate IN the floor, Q2 HOLD (active gate_in|HOLD). Operator asleep with the standing order "loop and kick it off when it ready".
- P0: G-R4-1..5 PASS (G P0 DONE 1789447406457-0), H-R4-1..3 PASS (H P0 DONE 1789447874149-0, replay 0 mismatches).
- Screen (worlds_r4.json ee86620f4, sha256 f007f4e2...): 74 cells.
  - SURVIVED 1: w13 train128_held64 (floor 166.47; baseline 182.72, ci95 [173.41, 188.11], 200 B).
  - HELD 5: w7 t8, w1 t8, w1 t128, w34 t8, w13 t8. Filed as anomalies 1789447409534..541 for D (discriminator: seed the linear archive with the gate genome).
  - PENDING 4, non-survivable: w7, w34, w26, w10 t128. Their ~7.8 h of learners run after test launch 1.
  - CULLED 64.
- Conductor scheduling calls overnight:
  - w13 t128 learner cleared;
  - learners <= 1 h that decide a survivor are pre-cleared;
  - PENDING status (SWARM_R4 s7);
  - no 4-epoch cap in P0.
- Fabric defects fixed with repro tests before launch:
  - 519d081c8 (G): idle worker socket timeout;
  - 7fa40eec9: rows commit on a Windows \?\ long path killed the worker;
  - 54c2d95fc: pm:worker expired during long jobs (confirmed live in G's run).
- Gate at 35d8ef0b5:
  - suite 419 passed rc 0;
  - SHARES_R4 default;
  - worktrees nestor-r4-{b,c,d,e} ff'd and clean;
  - idle worker smoke PASS;
  - draw_cell world axis = survivors (w13) + non-graphworld.
- Launch: B at 00:53 (schtask PM_B_20260915_005323). C, D and E follow, each after the previous hello.
- Framework writeup for operator/NotebookLM: FRAMEWORK_WRITEUP_2026-09-14.txt (54c2d95fc).
