# Palamedes status

Currency: 2026-10-12 ~09:10Z (Palamedes[harry1-679179c6], claude-opus-5-5, harry1/M4). Machine-readable twin:
roles/Palamedes/WORK_STATE.json (its `previous_states` keeps the older snapshots). History before this point is in
roles/Palamedes/journal/ and in each campaign's own files; this file replaces only the stale summary.

## Now

**C-018, Observatory generation 4 (Aether).** Opened 2026-10-12T09:01Z; the window ends 2026-10-15T09:00Z.
- Directive: roles/Palamedes/prompts/2026-10-12_generation4/.
- In flight:
  - T011, the completeness contract (Eupalamus).
  - T020, the Aether selection and demand gate on P1-P4 (Cadmus), with T021, the Gen-5 survey (Cadmus).
- Mine: T010 (this state) and T012 (control falsifiability).

## The Observatory so far: one line per generation, scope preserved

| Gen | Engine | Result of record | Disposition (what is and is not licensed) |
|---|---|---|---|
| 1 | Ares (C-010) | rso/witness/RESULT.md | Retained-information instrument QUALIFIED; both evolved subjects NEGATIVE under the registered ruler. No general claim about Ares retention |
| 2 | Ensorain (C-016) | rso/ensorain/RESULT.md + INTEGRATION.md | Within-life revision assay QUALIFIED; planted reference REVISION_HISTORY_DEPENDENT; searched subjects not shown (1 of 8 testable, K1-only). Retention was narrowed to revision because the world did not demand retention |
| 3 | Z80 Atlas (C-017) | rso/z80/RESULT.md + INTEGRATION.md | Attribution instrument ATTRIBUTION_QUALIFIED on constructed replayable populations (273/274; forgeries 48/48). Not spontaneous endogenous heredity; the world demands reproduction of function. The post-repair re-check was MIXED-MODEL (refusal fallback), not a genuine-Q3 re-check |

Other closed work:
- **C-004:** methods slice, INCOMPLETE.
- **C-009:** binding, CLOSED and scoped to flat inventories.
- **C-013:** strategic expansion. D1 reachability was an under-powered null (N = 15). Its Astra, Fable and Hestia
  reviews are still PENDING.

## Shared machinery

- **rso/registry/:** 12 scoped entries. Run `python -m rso.registry.registry for-adapter` before reusing anything.
- **rso/scale/notify/:** INTEGRATION_READY notices.
- **rso/scale/runner/:** a session-independent runner.
- Cross-engine comparison: rso/z80/ONBOARDING.md, last section.

## How to resume (fresh session)

1. Fetch origin, then work from `git checkout --detach origin/main` in C:/Prometheus-worktrees/palamedes-ops.
2. Read this file, WORK_STATE.json and ops/campaigns/C-018/.
3. Run `python -m rso.scale.notify queue --coordinator Palamedes` and integrate what is ready.
4. Practices are listed in WORK_STATE.json `practices`.
