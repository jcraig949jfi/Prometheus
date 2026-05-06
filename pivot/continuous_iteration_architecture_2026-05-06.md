# Continuous Iteration Architecture — Producers + Watchers + Queue

**Date:** 2026-05-06
**Owner:** Aporia (design); James (operational decision)
**Purpose:** structure both Techne (substrate) and Ergon (Learner) into a continuous iteration loop driving toward production-grade MVPs.
**Status:** plan; awaits James greenlight before infrastructure setup

## The problem

Both agents have been mostly idle with short bursts of work. The pattern:
- James gives a directive
- The agent does ~2-7 hours of focused work
- Output ships
- Agent sleeps until next directive

This is fine for one-shot tasks. It's the wrong shape for MVP-grade iteration where the agent needs to: code → test → review own output → identify gap → code again → test → cycle.

The fix isn't asking the agent to "loop more." AI agents don't run continuously; they run when invoked. The fix is **infrastructure**: scheduled invocation + watcher agents + persistent queue.

## Architecture: Producers + Watchers + Queue

```
                    ┌─────────────────────────┐
                    │   Persistent Queues     │
                    │   (git-tracked JSONL)   │
                    └──────────┬──────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
   ┌────────┐             ┌────────┐             ┌────────┐
   │ Techne │             │ Ergon  │             │ Charon │
   │(produce)             │(produce)             │(watch) │
   └───┬────┘             └───┬────┘             └───┬────┘
       │                      │                      │
       ▼                      ▼                      ▼
   ┌────────────────────────────────────────────────────┐
   │              git-tracked artifacts                 │
   │       (code, tests, session journals, results)     │
   └──────────────────┬─────────────────────────────────┘
                      │
                      ▼
                ┌──────────┐
                │  Aporia  │
                │ (watch)  │
                └──────────┘
```

Three roles, four agents:

### Producers (do the work)
- **Techne** — substrate v2.x → v3.x trajectory. Iteration unit: kernel opcode, primitive, pipeline component.
- **Ergon** — Learner v0.5 → v1.0 → v2.0. Iteration unit: training run, evaluation, corpus update.

### Watchers (continuously test producer outputs and file findings)
- **Charon** — substrate-grade test runner. Runs the falsification battery against itself; runs the testing-plan tests (G4, ExclusionCertificate adversarial, TriangulationProtocol independence, cross-domain gauntlet, substrate-layer synthetic-null) against new substrate commits.
- **Aporia** (me) — calibration reviewer. Checks new outputs against v2.x specs, watchlist trigger conditions, discipline rules (no narrative inflation, no scope drift, no hidden failures).

### Queue (persistent work items)
Git-tracked JSONL files at `agora/queue/`:
- `techne_inbox.jsonl` — tickets for Techne
- `ergon_inbox.jsonl` — tickets for Ergon
- `charon_inbox.jsonl` — tickets for Charon (specific tests to run)
- `aporia_inbox.jsonl` — tickets for Aporia (specific reviews to file)

Each ticket has the same schema (see below). Ticket lifecycle: `OPEN → IN_PROGRESS → DONE` (or `BLOCKED`, `WONTFIX`).

## Ticket schema

```json
{
  "id": "T-2026-05-06-0001",
  "source": "charon-watcher | aporia-watcher | james | techne | ergon | frontier-review",
  "target": "techne | ergon | charon | aporia",
  "type": "bug | feature | test-run | review-request | calibration | escalation",
  "priority": "P0-blocker | P1-high | P2-normal | P3-low",
  "title": "short human-readable title",
  "payload": {
    "description": "what the ticket asks for, in detail",
    "acceptance_criteria": "what counts as done",
    "predecessors": ["T-..."],
    "context_files": ["paths to relevant existing artifacts"]
  },
  "created_at": "2026-05-06T10:00:00Z",
  "created_by": "agent_id",
  "deadline": "2026-05-08T10:00:00Z (optional)",
  "status": "OPEN | IN_PROGRESS | DONE | BLOCKED | WONTFIX",
  "status_history": [
    {"status": "OPEN", "at": "2026-05-06T10:00:00Z", "by": "charon-watcher"}
  ],
  "resolution": "filled when DONE: artifact paths, key findings, follow-up tickets"
}
```

## Cron schedule (initial proposal)

| Agent | Cadence | What it does on each fire |
|---|---|---|
| Techne (producer) | every 4 hours | Read `techne_inbox.jsonl`. Pick highest-priority OPEN ticket. Work it (code + test + commit). Mark DONE or escalate. Update inbox. |
| Ergon (producer) | every 4 hours | Same pattern; reads `ergon_inbox.jsonl`. |
| Charon (watcher) | every 2 hours | Run the substrate-grade test battery against `git log -10`. File any failures or anomalies as new tickets in `techne_inbox.jsonl`. Run any `charon_inbox.jsonl` tickets. |
| Aporia (watcher) | every 6 hours | Review recent commits + session journals. File calibration concerns into `techne_inbox.jsonl` or `ergon_inbox.jsonl`. Update watchlist. Run any `aporia_inbox.jsonl` tickets. |
| Frontier-second-pass | weekly | Dispatch K(c) / v2.3 / v0.5 results to Claude / Grok / DeepSeek for outside review. File contrarian-critique findings as tickets. |

Cadence is asymmetric on purpose:
- Watchers fire MORE OFTEN than producers, so the queue stays fed
- Aporia fires LESS OFTEN than Charon because calibration review is lower-frequency than test running
- Frontier review is weekly because the cost is high and the signal is slow-moving

## Producer iteration cycle (the loop you're asking for)

Every Techne or Ergon invocation runs the same 6-step cycle:

1. **Read inbox.** Read `<self>_inbox.jsonl`. Pick highest-priority OPEN ticket.
2. **Pre-test.** Run existing test suite. Verify clean baseline.
3. **Implement.** Code the ticket's acceptance criteria.
4. **Test.** Run test suite again. All must pass.
5. **Self-review.** Re-read own diff against the ticket's acceptance criteria. Honest assessment: does this solve it, or did I solve a different problem?
6. **Commit + log.** Commit the work. Update ticket status to DONE with resolution. Append session journal entry. Push.

If step 4 fails (tests break): roll back, mark ticket BLOCKED with reason, file bug ticket for follow-up.
If step 5 fails (self-review reveals scope mismatch): mark ticket BLOCKED with reason, file new ticket reframing.
If step 6 fails (push conflict): pull, resolve, retry. If still conflict, escalate.

This 6-step cycle is what the producer agents do EVERY 4 hours.

## Watcher iteration cycle

Every Charon or Aporia invocation runs:

1. **Read commit log since last run.** `git log --since=<last_run_ts>`.
2. **Run watcher-specific tests.**
   - Charon: F-gate orthogonality, ExclusionCertificate replay, TriangulationProtocol independence, cross-domain gauntlet, synthetic-null at substrate layer
   - Aporia: discipline check, watchlist trigger evaluation, calibration vs spec
3. **File findings.** Any failures, anomalies, or concerns become new tickets in the producer inboxes.
4. **Update watcher state.** Last-run timestamp, accumulated findings.

## MVP target conditions

### Techne MVP (substrate v3.0 candidate)

- All v2.3 primitives stable across 1000+ episodes (Charon-watcher tests pass for 100 consecutive runs)
- KillEmbedding A149 prototype passes the synthetic-null guard
- TriangulationProtocol catches at least 1 correlated-path attempt (caught by adversarial replay test)
- Cross-domain gauntlet test passes (Lehmer claim killed when submitted to BSD pipeline)
- F-gate orthogonality MI audit shows all pairs MI < 0.4 bits OR documented N-fold revision filed
- Watch-1 PARTIAL verdict resolved (CoC hybrid translation prototyped or formally deferred to v3.x)

When all 6 hold for ≥7 days: substrate v3.0 ready to ship. Cut a release tag.

### Ergon MVP (Learner v1.0 candidate)

- Phase 0 eval-protocol fix lands; W4.0 re-passes under new protocol
- Phase 1 corpus selection identifies LR-headroom corpus (LR baseline < 80%)
- Phase 2 LoRA training on LR-headroom corpus shows: LoRA > LR on standard held-out AND ≈ LR on reflection-pair held-out AND > LR on structurally-distinct held-out
- W4.0 synthetic-null gate fires correctly (label-shuffle detected)
- 1 calibrated negative finding shipped per week of training (substrate-grade discipline maintained under pressure)
- Aporia's standing constraint satisfied: ≥100 per-claim records in ≥2 domains

When all 6 hold for ≥7 days: Learner v1.0 ready to ship. Cut a release tag.

## What we need to build (priority order)

### This week

1. **Create `agora/queue/` directory structure with empty inboxes.** ~30 min.
2. **Seed each inbox with 3-5 starter tickets** based on existing watchlist + tire-kick findings + testing plan. Aporia owns this initial seeding; ~2 hours.
3. **Set up cron routines** via `RemoteTrigger` (or `CronCreate`) for the 5 agents on the cadence above. Same pattern as `aporia-batch-deep-research-daily`. ~1 hour per cron, 5 hours total.
4. **Write the agent startup prompts** — each agent's prompt loaded fresh on every cron fire, telling it to read inbox, work top ticket, follow the 6-step cycle. ~2 hours.

### Next week

5. **Charon-watcher implementation** — the test battery code itself (most of this exists; need a unified runner). ~1 day.
6. **Aporia-watcher implementation** — discipline-review template + automated trigger evaluation. ~1 day.
7. **First full week of continuous iteration.** Both producers + both watchers running. James reviews the iteration log at end of week.

### Week 3+

8. **Tune cadence** based on what worked / didn't.
9. **Add escalation paths** when an agent BLOCKS too many consecutive tickets.
10. **Add frontier-second-pass weekly cron** when artifact volume justifies it.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Watcher floods producer inbox with low-quality tickets → producer can't make progress | Watchers prioritize tickets P0–P3; producers always work P0/P1 first. Watchers self-throttle: max 5 new tickets per fire. |
| Producer skips self-review (step 5) under cadence pressure → discipline degrades | Self-review section is required in the session journal for each commit. Aporia-watcher fails any commit missing this section; files calibration ticket. |
| Two producers commit conflicting changes to shared file | Use file-level ownership: Techne owns `sigma_kernel/` + `prometheus_math/`; Ergon owns `ergon/learner/` + `ergon/pipeline_d/`. Anything else, locks via small-grained tickets. |
| Cron drift / agent doesn't actually fire on schedule | Each agent's startup prompt logs `last_fired_at` to a heartbeat file. James checks the heartbeat weekly; if stale, ping. |
| Agents thrash on the same ticket repeatedly | Tickets have a `consecutive_block_count`; after 3 consecutive blocks, ticket auto-escalates to James for human resolution. |
| MVP target conditions never hit (perpetual iteration) | Each MVP target has a 30-day sunset. If conditions aren't met by sunset, full retrospective + plan revision required. Avoid drift. |
| Watchers find nothing wrong → discipline erosion suspicion | Quarterly calibration: deliberately introduce a known bug, see if Charon-watcher catches it. If not, improve the watcher. (Substrate-grade self-test of the self-test.) |

## What this architecture does NOT do

- Replace human direction. James still owns priority, MVP target setting, and override authority.
- Run experiments autonomously without James's approval. Each cron-fired agent works tickets that EXIST in its inbox; it doesn't generate new substrate-grade questions on its own (those go through Aporia or James).
- Skip the synthetic-null discipline. W4.0-style commit-blocking gates remain in force; cadence pressure doesn't override discipline.
- Solve the open watchlist items (Watch-1 / Watch-2 / Watch-3 / Watch-4). Those need human-grade decisions; this architecture surfaces evidence faster but doesn't decide.

## Comparison to current state (what changes)

| Today | With architecture |
|---|---|
| Agents fire when James types a directive | Agents fire on cron + queue, James types directives less often |
| Tests run when an agent decides to | Tests run continuously via Charon-watcher every 2 hours |
| Calibration review happens after pitch deadline | Aporia-watcher reviews every 6 hours; deviations caught early |
| Inboxes don't exist; tickets are ad-hoc | Inboxes are git-tracked JSONL; tickets have lifecycle |
| Both producers idle for hours/days between bursts | Both producers iterate every 4 hours through queue |
| MVP target conditions implicit | MVP target conditions explicit; trackable per-week |
| Frontier-model review on demand | Frontier-second-pass weekly automatic |

## Decision request to James

Three concrete decisions:

1. **Greenlight the architecture as proposed** — yes / modify / reject?
2. **Initial cadence** — do you want producers every 4 hours (proposed) or different (every 2? every 6?)?
3. **Start scope** — do you want all 4 agents (Techne, Ergon, Charon, Aporia) on cron, or start with just the 2 producers and add watchers in week 2?

If yes, I'll seed the inboxes with starter tickets today (Aporia work; ~2 hours) and produce the cron-routine specs for `RemoteTrigger` setup. You'd then run the 5 setup commands once, and the architecture goes live.

Standing offer: if you want, I can also draft the first week's MVP-targeted ticket pack (≈25 tickets across both inboxes, prioritized) so the loop has real fuel at startup.

— Aporia, 2026-05-06
