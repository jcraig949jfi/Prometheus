# TH-GLOBAL-CONTROL-PLANE -- shared control-plane infrastructure

epic: EP-GLOBAL

Status: OPEN, PERMANENT. Type: PROCESS / INFRASTRUCTURE. Opened 2026-10-03 under the operator directive
roles/Achilles/prompts/2026-10-03_generic_workers/ (s25: these mechanisms are GLOBAL infrastructure, not
Phase 2-B-specific). Set up by Achilles, which does not operate it as a scheduler or coordinator.

## What it holds (all reached through `python -m workgraph`; normative text in roles/base-role/DISTRIBUTED_WORK.md)
- the work graph itself: epics, threads, campaigns, task packets, leases, receipts (s1-s11)
- execution ownership NAMED_SEAT / GENERIC_WORKER and the PrometheusWorker architecture
  (s12; roles/generic-worker-role/; workgraph/worker.py)
- execution modes ATOMIC / NATIVE_PARALLEL / SHARDABLE (s12)
- the inherited epic priority bands, preemption and PREEMPTED_RESOURCE (s13)
- the operator priority-request queue, its Markdown view and its email-digest rendering, and the comms/A2A
  notification events (s14; ops/operator_queue/; achilles/census/render.py operator_queue_block)
- common resource-leasing rules (s10, s13) and CWO input assembly (s15; workgraph/cwo.py)

## Campaigns
None as work graphs yet; changes so far were made under operator directives (Achilles receipts in
roles/Achilles/reviews/).
