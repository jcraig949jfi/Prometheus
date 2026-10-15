# Palamedes status

Currency: 2026-10-15T14:54:21Z (Palamedes[harry1-679179c6], claude-opus-5-5, harry1/M4). Machine-readable twin:
roles/Palamedes/WORK_STATE.json (its `previous_states` keeps the older snapshots). History before this point is in
roles/Palamedes/journal/ and in each campaign's own files; this file replaces only the stale summary.

## Now

**IDLE.** C-019 (Generation 5) closed early on the selection gate, 2026-10-15. Record: ops/campaigns/C-019/CLOSEOUT.md;
external review packet: rso/scale/review/GEN5_EXTERNAL_REVIEW_PACKET.md. Waiting on Ananke (#2249, #2259) and the operator.

## The Observatory so far: one line per generation, scope preserved

| Gen | Engine | Result of record | Disposition (what is and is not licensed) |
|---|---|---|---|
| 1 | Ares (C-010) | rso/witness/RESULT.md | Retained-information instrument QUALIFIED; both evolved subjects NEGATIVE under the registered ruler. No general claim about Ares retention |
| 2 | Ensorain (C-016) | rso/ensorain/RESULT.md + INTEGRATION.md | Within-life revision assay QUALIFIED; planted reference REVISION_HISTORY_DEPENDENT; searched subjects not shown (1 of 8 testable, K1-only). Retention was narrowed to revision because the world did not demand retention |
| 3 | Z80 Atlas (C-017) | rso/z80/RESULT.md + INTEGRATION.md | Attribution instrument ATTRIBUTION_QUALIFIED on constructed replayable populations (273/274; forgeries 48/48). Not spontaneous endogenous heredity; the world demands reproduction of function. The post-repair re-check was MIXED-MODEL (refusal fallback), not a genuine-Q3 re-check |
| 4 | Aether (C-018) | rso/aether/RESULT.md | RX CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT (interventional ancestry r>=2 in 8 of 13 evaluable; content not recoverable above ~0.05-0.10); V1 not evaluated; P4 unsupported; TEST-4 preserved; genuine Q3 | Post-confirmation audit (C-019): all 64 units natively replayed, 57/57 MATCH |
| 5 | selection only (C-019) | rso/gen5/SELECTION.md | No substrate selected. Crius WORLD_DEMAND_NOT_QUALIFIED + DISCOVERY_INACCESSIBLE (constructed reuse real, leaks inert, undiscoverable); Ananke right substrate, owner already ran the ladder (C4 0/168; designed halves 2/32), owner unavailable, power unmet (107/arm). Parts-suitability ladder drafted for owner sign-off |

Other closed work:
- **C-004:** methods slice, INCOMPLETE.
- **C-009:** binding, CLOSED and scoped to flat inventories.
- **C-013:** strategic expansion. D1 reachability was an under-powered null (N = 15). Its Astra and Fable reviews are
  NOT PERFORMED -- SUPERSEDED BY LATER EXPERIMENTAL EVIDENCE (D4); Hestia's is still pending.

## Shared machinery

- **rso/registry/:** 17 scoped entries (incl. adversarial-kit, rso/adversary/). Run `python -m rso.registry.registry for-adapter` before reusing anything.
- **rso/scale/notify/:** INTEGRATION_READY notices.
- **rso/scale/runner/:** a session-independent runner.
- Cross-engine comparison: rso/z80/ONBOARDING.md, last section.

## How to resume (fresh session)

1. Fetch origin, then work from `git checkout --detach origin/main` in C:/Prometheus-worktrees/palamedes-ops.
2. Read this file, WORK_STATE.json and ops/campaigns/C-019/.
3. Run `python -m rso.scale.notify queue --coordinator Palamedes` and integrate what is ready.
4. Practices are listed in WORK_STATE.json `practices`.
