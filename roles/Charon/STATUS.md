# Charon STATUS

Currency: 2026-09-11 (updated at the base-role adoption pass). Plain language.
Previous machine-readable status: none (this file is new; the standing pointer at the
top of RESPONSIBILITIES.md served the purpose before today).

## Where the seat is

- workspace: F:\Prometheus-worktrees\charon-base-role (linked worktree; guard passes)
- branch: charon/base-role-adopt-2026-09-11, base_sha f727dfb1f
- base role: read at f727dfb1f, adopted; receipt roles/Charon/BASE_ROLE_ADOPTION_2026-09-11.txt
- machine: M1 (the pre-commit admissibility preflight is installed on this machine's
  common gitdir and therefore runs in every linked worktree; on M2 it is NOT installed,
  CH-2026-09-01-B)
- long-running processes owned: none
- worktrees owned: this one only
- last session before today: 2026-09-01 (M2), ruling filed, not executed

## What is live and what is dormant (base rule 7: dormancy must be visible)

- metabolization-probe pipeline (ergon/probe/): DORMANT. Last change 2026-08-23
  (c6736671c). The 09-01 ruling's C1 (pool fingerprint) and C2 (load_prepass status
  guard) are UNIMPLEMENTED. Ergon re-chartered 2026-08-30 and has not touched the
  directory since. No arm may be read until C1/C2 land.
- step 2 (c1 regret experiment): built, pre-registered, UNRUN, premise WITHDRAWN 09-01.
  Awaiting an operator decision (BACKLOG CHARON-22).
- Apollo E9 held-out battery (roles/Charon/apollo_e9): no receipt since 08-25; state
  not re-verified today (BACKLOG CHARON-14).
- attacks/preflight.py pre-commit hook: FROZEN (R-D). Ran on today's commit.
- Charon has no H0-H5 delegation. Commissioned audits proposed as CHARON-06..09.

## Standing gates held (unchanged since 09-01)

- HB3-2, HB3-3 (Harmonia B); C1 pool fingerprint; C2 transport-failed residue;
  F-hint >= 0.5225; leakage_gate.json vacuity stamp. All must clear before any arm is
  read.
- CH-2026-09-01-A: the reading half of RE_REVIEW_SIGNOFF is enforced by nothing but
  this seat.

## Today (2026-09-11)

- base role adopted; three seat files annotated (RESPONSIBILITIES, STARTUP, CHARTER)
- four untracked Charon files claimed from the canonical checkout and committed;
  deleted there afterwards (the one permitted write)
- Mnemosyne todo (full_audit.py duckdb banner import) closed
- CALIBRATION.md created, seeded from the 09-01 journal
- BACKLOG_H0H5.md created, 23 rows, 2 XL
- finding: 46 charon/ scripts (98 repo-wide) hardcode the April-era Postgres write
  credential; not fixed today, BACKLOG CHARON-04

## Next executable action

CHARON-01: gate-fire C2 against a planted 504 row in a copy of block B.
