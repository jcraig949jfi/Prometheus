---
name: Cron discipline for Harmonia session loops
purpose: Factor out of session transcripts the procedural how-to for using CronCreate/CronDelete to run collaborative multi-session loops. Addresses axis-6 sprawl observation #7 (cron-discipline tribal knowledge).
audience: Any Harmonia session (or sibling role) on a collaborative day where James has asked for a recurring loop
status: v1.0 — first-draft by sessionA 2026-04-23 axis-6 strawman; update as cadence patterns evolve
---

# Cron discipline

## When to create a cron

James or the user asks you to loop at a specific interval (e.g., "every 4 minutes", "work together today and check in every 10m"). Memory `feedback_4min_cron_collaboration.md` captures the general pattern. Three concrete cadence classes have been validated:

| Class | Interval | Use case | Cron expression |
|---|---|---|---|
| Collaborative sprint | 4m | Team coordination day with multiple sessions active, short feedback cycles | `*/4 * * * *` |
| Sustained work | 6-10m | Team day where each session has more to do per tick; less cross-session back-pressure | `*/6 * * * *` or `*/10 * * * *` |
| Drifted check-ins | 20-30m | Solo session with external waits (auditor, peer review), longer reasoning per tick | `*/20 * * * *` or `*/30 * * * *` |

## Interval rounding (critical)

Cron divides a 60-minute hour cleanly only by integer divisors of 60: `1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30`. If James asks for a non-clean interval (7m, 8m, 9m, 11m, 13m, 14m), **round to the nearest clean divisor and tell the user** — don't ship an uneven cron.

Worked examples from this project:
- James 2026-04-22: "every 4 minutes" → `*/4` clean, no rounding.
- James 2026-04-22 later: "every 7 minutes" → `*/7` would fire at :00, :07, :14, ..., :56, :00 (4-min gap, uneven). Rounded down to `*/6` to respect the slowdown direction while keeping clean divisibility. sessionA cron `28f962f7`.
- James 2026-04-23: "every 8 minutes" → `*/8` same issue as 7. Rounded up to `*/10` to respect slowdown direction while clean. sessionA cron `20a85d59`.

Rounding direction: if the ask is a slowdown from the previous cadence, round toward the slower clean divisor. If a speedup, round toward the faster. Communicate the rounding explicitly in the message that schedules the new cron.

## How to create a cron

Via `CronCreate` tool:

```
CronCreate(
    cron='*/N * * * *',
    prompt='<the full task prompt to fire each tick>',
    recurring=true
)
```

The prompt should be self-contained — it is the message Claude will receive each tick, with no persistent session memory beyond what is written to disk / Redis / the cron prompt text itself. Include:

- The instance identity (`You are Harmonia_M2_sessionA...`)
- The interval + rationale (`on a 10-min loop, rounded from James's 8m ask for clean divisibility`)
- Team composition + coordination conventions
- Substrate credentials env vars (PYTHONPATH / PYTHONIOENCODING / AGORA_REDIS_HOST / AGORA_REDIS_PASSWORD)
- Message-format discipline (flat-key xadd; not nested under a `msg` key — `tail_sync` reads top-level)
- Active directives (what James asked for this session)
- Work types to rotate across ticks
- Standing open items
- Role-specific wave mechanics (dissent-by-design for wave-N dissent-holder)
- Wind-down trigger (`Kill cron on wind-down per 4min_cron_collaboration memory`)
- Security reminders (never read .env / credential / key files; use `from keys import get_key` if needed)

## How to swap a cron (cadence change)

When James asks for a new cadence mid-session:

1. Identify the running cron's job ID from the prior schedule message.
2. `CronDelete(id=<old_id>)` to cancel.
3. `CronCreate(cron='*/N * * * *', prompt='<updated prompt>', recurring=true)` with the new interval + updated prompt text reflecting the new cadence rationale.
4. Post `CRON_SWAP` or similar on `agora:harmonia_sync` so sibling sessions see the cadence change.
5. Continue the tick's work — don't wait for the cron to fire; it fires on its own schedule.

Worked example: sessionA 2026-04-23 iter-49 — James shifted 4m→8m directive via sessionC DIRECTIVE_AND_RECRUITMENT. sessionA was on `28f962f7` (6m, prior cron-swap from 4m→7m-asked). Deleted `28f962f7`, created `20a85d59` (10m, rounded from 8m), posted CLAIM naming both cron IDs.

## How to kill a cron on wind-down

Per `feedback_4min_cron_collaboration.md`: "Kill cron on wind-down."

Triggers for wind-down:
- User explicitly says "wind down" / "we're done" / "end session"
- All standing open items are closed AND no new directives from James
- Claude session is about to exit (final post-processing)

Wind-down procedure:
1. Post a final `SESSION_CLOSE` or `WIND_DOWN` on `agora:harmonia_sync` with status summary (what landed this session, what remains open).
2. `CronDelete(id=<current_cron_id>)` to stop future fires.
3. (Optional) Update a handoff entry in `decisions_for_james.md` or a memory file if session-level state is worth persisting for cross-session continuity.
4. Exit.

Do NOT leave a cron running past session close — it will fire into a dead session and waste James's compute budget. Explicit deletion is the discipline.

## Rounding summary (cheat sheet)

| James asks | Round to | Cron | Why |
|---|---|---|---|
| 1m | 1m | `*/1 * * * *` | Already clean |
| 2m | 2m | `*/2 * * * *` | Clean |
| 3m | 3m | `*/3 * * * *` | Clean |
| 4m | 4m | `*/4 * * * *` | Clean |
| 5m | 5m | `*/5 * * * *` | Clean |
| 6m | 6m | `*/6 * * * *` | Clean |
| 7m | 6m (down if slowing, else 10m up) | `*/6` or `*/10` | Not clean; depends on direction |
| 8m | 6m (down if slowing) or 10m (up if accelerating context) | `*/6` or `*/10` | Not clean |
| 9m | 10m | `*/10 * * * *` | Round up; 10 is nearest clean |
| 10m | 10m | `*/10 * * * *` | Clean |
| 11m | 10m or 12m | `*/10` or `*/12` | Not clean |
| 12m | 12m | `*/12 * * * *` | Clean |
| 15m | 15m | `*/15 * * * *` | Clean |
| 20m | 20m | `*/20 * * * *` | Clean |
| 30m | 30m | `*/30 * * * *` | Clean |
| 60m | 60m (hourly) | `0 * * * *` | Use on-the-hour form |

## Version history

- **v1.0** 2026-04-23 (sessionA axis-6 strawman) — factor out of session transcripts per axis-6 consolidation #2. Three cadence classes, interval rounding rules, creation/swap/kill procedures, rounding cheat-sheet.
