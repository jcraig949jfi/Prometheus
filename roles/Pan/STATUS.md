# Pan status

Currency: 2026-10-09T11:50Z.

seat state: ACTIVE (charter 2026-10-09; window to 2026-10-12). WORK_STATE ACTIVE.
what it asserts: PRESENT (comms Pan[m2-f20b5eac]), ACTIVE, PRODUCTIVE (rows:
  73,037 artifacts, 13,128 commits, 394,952 chunks + embeddings, 4,702 arXiv,
  738 HF daily, 1,503 HF models), VALID: PARTIAL -- retrieval v1 FAILS its
  frozen positive thresholds on the held-out set (hybrid R@10 0.75 < 0.80);
  negative (vector) and cheat controls pass; Iceberg and fit controls pass.
host: SPECTREX5; worktree pan-base-role-adopt-2026-10-09, branch
  pan/base-role-adopt-2026-10-09.
latest report: reports/STATUS_20261009T1150Z.md (status report 1).
monitors owned or fed: none registered yet (refresh loop is PAN-17).
running: nothing. No lease held.
blockers: none for the seat; Q-001 (pgvector) gates one item.
next executable action: v2 retrieval design on a fresh held-out set.
questions for the operator: QUESTIONS.md (7 open).
