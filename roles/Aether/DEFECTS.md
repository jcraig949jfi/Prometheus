# Aether -- recorded defects (MWO-0001 s12)

## DEF-AETH-001 (2026-09-29) -- ubu001 Fabric workers cannot create worktrees ("No space left on device")

- Observed: 16 of 20 E-009 script Tasks failed at worktree creation on ubu001, between 08:15 and 08:40 EDT, both
  attempts each, within seconds. Example: tsk-8fb852d1bab3, error_summary "worktree add failed: ... error: unable
  to write file prometheus_math/... fatal: cannot create directory at 'prometheus_math/benchmarks': No ..." (the
  message is truncated, and consistent with "No space left on device"). The checkout is 58,805 files.
- Scope: Cosmos Tasks also failed on ubu001 in the same hour, so this is not specific to Aether.
  worker.ubu001.sci / sci2 / sci3 / .a / .b were online at 08:39; each worker keeps its own checkout per base SHA.
- Side effects:
  - the failed attempt's env_receipt.json artifact (art-5d37d0c67b36) returns NotFound from `fabric get`;
  - both of a Task's attempts are spent on a host condition, so the Task goes to failed rather than waiting.
- Not fixed by Aether (host change; MWO-0001 s6 / s7.5). Reported to Odysseus (Fabric principal).
- Workaround used: MWO-0004 R3 native fallback on BUCKKEEP for the 16 affected E-009 units, under a canonical Fabric
  lease, same pinned code, same inputs (see ops/campaigns/C-002/E-009/RESULT.md).
