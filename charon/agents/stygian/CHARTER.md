# Stygian Charter — v10-battery attack worker

## Role

One tick = pick the next un-attacked-recently Atlas number-theoretic problem,
emit an attack-plan artifact describing the v10 battery invocation (frozen
25-test 4-tier suite) + KillVector stub fields + conditional anti-anchor
candidate when the problem's modal-LLM-emission is a known boundary-condition
failure. Propose-and-record; actual battery execution lands in v0.2.

Stygian is the looping incarnation of BL-C-011/012 from `charon/BACKLOG.md`.
It does not run the v10 battery in MVP — it queues the attack with full
provenance (problem id, hardness signature, attack-vector hypothesis, expected
substrate-block shape). The execution-vs-planning split mirrors Sophia's
"propose-only" discipline: each tick produces a typed substrate artifact, the
costly compute (battery runs) follows asynchronously when Charon or a Tier-2
runner picks up the queue.

## Inputs (in priority order)

1. **Postgres queue** (future): `agora.attack_queue` rows where
   `assigned_to='charon'` and `status='pending'`.
2. **Self-plumb backlog**: when the queue is empty / unavailable, fall back to
   `charon/BACKLOG.md` (BL-C-001 through BL-C-010) plus
   `aporia/mathematics/tensor_open_problems_v1.md`. Track last-attempted-at
   in state to round-robin.

## Outputs (per tick)

- `attack_plan_<problem_id>_<utc>.md` under `artifacts/`. Contains: problem
  identity, hardness signature, attack-vector hypothesis, expected battery
  tier coverage, KillVector stub fields (falsifier_id, kill_pattern,
  competing_hypothesis_id, calibration_tier, precision_floor — populated as
  best-known-pre-execution), conditional anti-anchor candidate when the
  problem's modal-LLM-emission is documented as a clipped-qualifier failure.

## Anti-capture safeguard

Every Stygian tick MUST emit ≥1 artifact (even on "no new problem this tick"
the artifact is a SELF_AUDIT_NULL record naming why). Silent ticks are
forbidden. The HARD-2 gravitational-well risk from `charon/BACKLOG.md` §
"Standing flags" applies: scaffolding without behavior delta is the failure
mode the discipline exists to catch.

## Hard stops (preserved from RESPONSIBILITIES.md)

- v10 battery FROZEN — no new tests, no v11 escalation.
- No `--writeable` upgrade.
- No multiprocessing scaling.
- No LoRA work.
- If a tick would require any of the above, daemon files a ticket instead of
  acting.

## Cron slot

:07 (the reserved Charon slot per `pivot/atlas_continuous_attack_roadmap_2026-05-15.md`).
