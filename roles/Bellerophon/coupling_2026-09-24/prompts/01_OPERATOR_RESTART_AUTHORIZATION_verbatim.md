# Operator restart authorization (verbatim, received 2026-09-25 by Bellerophon[m2-9e74888e])

Here are some thoughts for post reset as well:

Bellerophon: restart and finish the full campaign.

Choose the cap-extension / active-runtime amendment, not the original absolute wall-clock caps.

The overnight idle period after the OOM is an infrastructure suspension and must not determine which scientific lanes receive observations.

Authorization

1. Resume the same frozen campaign.
    * Preserve all 959 completed observations exactly once.
    * Resume only missing frozen run IDs.
    * Do not restart from zero.
    * Do not alter hypotheses, treatments, lane allocations, detector definitions, statistical tests, readiness criteria, or the frozen decision tree.
2. Amend the time rule before restarting.
    Record that:
    * original launch was 2026-09-24 20:07Z;
    * execution stopped at approximately 21:23Z from host OOM;
    * nothing scientific ran during the suspension;
    * scientific results remained blinded;
    * the wall-clock caps are therefore replaced by an active campaign runtime limit.
    Count the approximately 1 h 16 min already executed before the OOM toward the campaign runtime.
    The campaign remains subject to the original directive's:
    * minimum intended extended-run scale: ~12 active hours where useful;
    * hard maximum: 25 active campaign hours total.
    The forced suspension does not count toward those hours.
    Do not enlarge the run/sample plan merely because additional wall-clock time is now available.
3. Finish all frozen lanes if they fit within the active-runtime maximum.
    Do not intentionally truncate B-rand, B-cop, J, or other later-priority lanes merely because the host sat idle overnight.
    Complete:
    * Phase 1;
    * automatic Phase 2;
    * preregistered follow-ups;
    * extension rules;
    * replay checks;
    * analysis;
    * final adjudication.
4. The machine is authorized for dedicated Bellerophon use until this campaign finishes.
    Before restarting, cleanly checkpoint/stop other Prometheus workloads using substantial CPU/RAM if that can be done without losing their evidence.
    Do not destroy another seat's uncheckpointed work.
    Once the competing workloads are safely quiescent, treat Bellerophon as the priority workload until the campaign and analysis finish.
5. Do not blindly assume 20 workers are safe.
    First establish actual available RAM and measured worker RSS.
    If the host is effectively dedicated and the measured reserve supports 20 workers safely, use 20.
    Otherwise use the highest safe concurrency.
    Maintain a meaningful memory reserve rather than driving the 32 GB machine to the edge again.
    Prefer automatic worker recycling if RSS grows over repeated jobs.
6. Standing operational restart authority remains in force.
    After this restart, do not return for human approval because of another ordinary:
    * worker crash;
    * executor crash;
    * memory-pressure shutdown;
    * checkpoint restart;
    * transient infrastructure interruption.
    If evidence integrity verifies and the frozen scientific design is unchanged, recover autonomously and continue.
    Only stop for operator involvement if:
    * evidence integrity cannot be established;
    * treatment/seed identity is corrupted;
    * already completed observations become scientifically uninterpretable;
    * continuing requires altering the scientific experiment;
    * unrecoverable repository/data loss occurs.
7. Maintain scientific blindness.
    Operational metadata is allowed:
    * run counts;
    * voids;
    * worker health;
    * memory;
    * throughput;
    * completion state.
    Do not inspect scientific outcomes until the frozen analysis point.
8. No further HITL.
    Once this restart begins, finish autonomously.
    Do not send progress updates or ask for scheduling decisions.
    Return only after:
    * execution is finished;
    * all permitted causal follow-ups are finished;
    * analysis is finished;
    * reports/ledgers are written;
    * commits are pushed;
    * readiness is adjudicated.

Final accounting

The final report must separately state:

* total wall-clock elapsed time;
* active campaign runtime;
* duration of the OOM suspension;
* number of pre-OOM observations retained;
* number of post-restart observations;
* concurrency used over time;
* peak memory behavior;
* any worker recycling/recovery;
* NOT_RUN count, if any;
* whether any execution amendment changed scientific content (expected: no).

This amendment repairs an operational stopping-rule problem. It does not reopen the scientific preregistration.

Proceed now, use the machine as the dedicated Bellerophon host once other workloads are safely quiesced, and complete the campaign without further human involvement.
