# Palamedes status

Currency: 2026-10-12 ~09:10Z (Palamedes[harry1-679179c6], claude-opus-5-5, harry1/M4). Machine-readable twin:
roles/Palamedes/WORK_STATE.json (its `previous_states` keeps the older snapshots). History before this point is in
roles/Palamedes/journal/ and in each campaign's own files; this file replaces only the stale summary.

## Now

**IDLE.** C-018 (Generation 4, Aether) closed 2026-10-12 ~20:00Z. Review packet: rso/scale/review/GEN4_REVIEW_PACKET.md.
Generation 5 (Crius, contract rso/gen5/CANDIDATE_CONTRACT.md) needs operator authority and a named engine steward.

## The Observatory so far: one line per generation, scope preserved

| Gen | Engine | Result of record | Disposition (what is and is not licensed) |
|---|---|---|---|
| 1 | Ares (C-010) | rso/witness/RESULT.md | Retained-information instrument QUALIFIED; both evolved subjects NEGATIVE under the registered ruler. No general claim about Ares retention |
| 2 | Ensorain (C-016) | rso/ensorain/RESULT.md + INTEGRATION.md | Within-life revision assay QUALIFIED; planted reference REVISION_HISTORY_DEPENDENT; searched subjects not shown (1 of 8 testable, K1-only). Retention was narrowed to revision because the world did not demand retention |
| 4 | Aether (C-018) | rso/aether/RESULT.md | RX CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT (interventional ancestry r>=2 in 8 of 13 evaluable; content not recoverable above ~0.05-0.10); V1 not evaluated; P4 unsupported; TEST-4 preserved; genuine Q3 |
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
