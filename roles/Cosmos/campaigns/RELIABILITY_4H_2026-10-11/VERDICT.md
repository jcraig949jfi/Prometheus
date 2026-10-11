# RELIABILITY TEST VERDICT -- 4 h window 2026-10-11T06:09:58Z -> 10:09:58Z (prereg PREREG.md, before start)

VERDICT: **FAIL** by the preregistered rule (one clause missed: P1 hour 1). The science and supervision parts held; the
independent-wake mechanism did not meet its own timing.

| clause | result | evidence |
|---|---|---|
| P1 four hourly entries, each committed within 20 min of 07:13 / 08:13 / 09:13 / 10:13 | **MISS (h1)**: h1 07:35:38 (+22.6 min); h2 08:32:09 (+19.2); h3 09:32:07 (+19.1); h4 ~10:01 (-12) | STATUS_LOG.md, commit times |
| P2 every job terminal; no live job without results beyond its stall limit unflagged | MET: 16 supervised runs, all DONE, 0 restarts in the window (the earlier EXP-04 relaunch stall at 05:55 was caught and recovered by the watchdog) | ~/cosmos_runs/*/EVENTS.jsonl; sweep |
| P3 no gap > 30 min with no job and no logged reason | MET (narrowly): idle gaps 21, 22.6, 28.6 min, each logged | STATUS_LOG.md |
| P4 lease renewed at each wake, never expired | MET: 06:09, 07:35, 08:32, 09:32, 10:00; smallest margin 4 min (07:35) | LEASE.json renewals |
| P5 >= 2 preregistered results committed | MET: EXP-05, -06, -07, -08, -09; NS-01 F15 tests; NS-02 | cosmos/c4-v03, cosmos/ns01-2026-10-11 |
| P6 zero constraint violations | MET. One disclosed PROCESS slip (EXP-08 one-system smoke-test output seen before its prereg commit; rules unchanged) | EXP-08 prereg disclosure |

## What the test established about the mechanism
- The progress watchdog works in production: no job ever sat silently; every run reached a terminal verdict.
- The session scheduler is NOT a reliable independent wake: every cron fired ~20-30 min after its minute (it fires
  only when the session is idle, plus jitter). Moving the cron 10 min earlier (07:36) bought just enough margin for
  h2/h3; h4 was driven by a job-completion notification instead. Idle gaps were spent WAITING for the scheduler.
- Unattended progress was real: ~4 h produced 11 preregistered experiments, 2 campaigns' deliverables, 3 full suites.
- Known limitation stated before the test still stands: everything wakes only while this Claude session lives.

## Recommendation
Do not authorise a multi-day window yet. Before the next attempt: (1) an OS-level timer (systemd user timer or cron)
running `python -m prometheus.cosmos.supervise sweep` every 10 min, writing an alert and posting to comms on
STALLED / DEAD / running-without-lease (needs operator approval for automatic posting); (2) keep at least one
supervised job queued at all times so job completions, not the scheduler, pace the agent; (3) re-run this 4 h test
with P1 unchanged.
