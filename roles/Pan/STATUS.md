# Pan status

Currency: 2026-10-09T11:05Z.

seat state: ACTIVE (charter adopted 2026-10-09; window to 2026-10-12).
  WORK_STATE.json: ACTIVE, MWO-0004; fleet order CWO-2026-09-30C.
what it asserts: PRESENT (comms Pan[m2-f20b5eac] on the M1 store), ACTIVE
  (charter adopted, environment built), NOT YET PRODUCTIVE (no index
  rows yet), VALID not applicable until the first controls run.
host: SPECTREX5; worktree pan-base-role-adopt-2026-10-09, branch
  pan/base-role-adopt-2026-10-09, base 970399844.
environment: seat venv on M2 NVMe with pyarrow 26.0.0, pyiceberg 0.12.0,
  sentence-transformers 6.1.0, torch 2.11.0+cu128 (CUDA available).
measured facts: M1 cluster PostgreSQL 17.9 (Windows); pgvector absent
  (Q-001); databases lmfdb 365 GB, prometheus_fire 3477 MB,
  prometheus_sci 320 MB; 33 schemas in prometheus_fire.
monitors owned or fed: none yet.
running: deep research on the adjacent frontier (5 notes).
blockers: none for the seat. Q-001 (pgvector) is a hard gate on one
  item only; its default is running.
next executable action: PAN-01 inventory v0.
questions for the operator: roles/Pan/QUESTIONS.md (6 open).
