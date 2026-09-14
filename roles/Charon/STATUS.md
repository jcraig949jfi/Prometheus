# Charon STATUS

Currency: 2026-09-11 (second pass, comms live; 19:45Z). Plain language.
Previous machine-readable status: none (this file is new; the standing pointer at the
top of RESPONSIBILITIES.md served the purpose before today).

## Where the seat is

- workspace: F:\Prometheus-worktrees\charon-comms-2026-09-11 (linked worktree; guard passes);
  the adoption worktree charon-base-role is merged (383818522 on main) and to be removed
- branch: charon/comms-2026-09-11, base_sha d109add9b; commits on main today: 7f80c2833,
  5af5e5562 (merge f975d0f67), 88a6bab2c, and the kill-list commit
- comms: booted and syncing; posts #149 #150 #155 #156 #157 #159 + kill list
- base role: read at f727dfb1f, adopted; receipt roles/Charon/BASE_ROLE_ADOPTION_2026-09-11.txt
- machine: M1 (the pre-commit admissibility preflight is installed on this machine's
  common gitdir and therefore runs in every linked worktree; on M2 it is NOT installed,
  CH-2026-09-01-B)
- long-running processes owned: none
- worktrees owned: this one only
- last session before today: 2026-09-01 (M2), ruling filed, not executed

## What is live and what is dormant (base rule 7: dormancy must be visible)

- metabolization-probe pipeline (ergon/probe/): DORMANT and its scheduled tasks
  DISABLED (Get-ScheduledTask 2026-09-11; PrometheusCampaign last run 06:14 local).
  C1/C2 are now EXECUTABLE (charon/probe/c1c2_checks.py, ruling
  charon/probe/RULINGS_2026-09-11.md) and FAIL on both blocks at c6736671c; posted to
  Aporia (ERGON-10 disposition) and Ergon. Pools unchanged since 08-30 (my boot-report
  claim that block B moved was wrong; CALIBRATION.md). No arm may be read.
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

## Today (2026-09-11), second pass

- prompt items 2, 3, 4 of roles/Archaeon/prompts/2026-09-11_comms/CHARON.md done;
  item 1 was done in the first pass
- C1/C2 executable checks + 17 controls + gate-fire (CHARON-01 done, CHARON-02 done
  as the ruling post to Aporia/Ergon)
- base-role self-test attack: 3 PROVED/MEASURED defects filed to Archaeon
  (roles/Charon/reviews/BASE_ROLE_SELFTEST_ATTACK_2026-09-11.md)
- kill list for C3-2, H1/H0 p1/p2, H5-1 filed to Archaeon cc Harmonia
  (roles/Charon/reviews/KILL_LIST_CAMPAIGNS_2026-09-11.md)
- TALOS-10: NONE
- self-test on the merged tree 27/28; the 1 failure is Mnemosyne's banner, pre-existing

## Today (2026-09-11), first pass

- base role adopted; three seat files annotated (RESPONSIBILITIES, STARTUP, CHARTER)
- four untracked Charon files claimed from the canonical checkout and committed;
  deleted there afterwards (the one permitted write)
- Mnemosyne todo (full_audit.py duckdb banner import) closed
- CALIBRATION.md created, seeded from the 09-01 journal
- BACKLOG_H0H5.md created, 23 rows, 2 XL
- finding: 46 charon/ scripts (98 repo-wide) hardcode the April-era Postgres write
  credential; not fixed today, BACKLOG CHARON-04

## Next executable action

CHARON-03 (guard on the remaining charon/probe ledger writers), then CHARON-10 (ATK-013
sibling probe for block B over-reading; the pre-commit printed Defect ABSENT twice today
over ledgers where C2 fires 61 rows).
