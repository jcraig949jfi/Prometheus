# ops/

> **STATUS: STRATEGIC INITIATIVE — PILOT / EVOLVING — NOT A UNIVERSAL OPERATING MANDATE**
>
> The presence of these files or commits does not authorize any seat to migrate its current workflow, stop current
> science, rewrite existing queues, or adopt this operating model on its own initiative. Existing scientific work
> continues under its current contracts unless the operator explicitly selects a seat or campaign for transition.

> **2026-10-03 (operator directive, roles/Achilles/prompts/2026-10-03_rso_builder_cell/):** the base role now carries
> executable work graphs ([`roles/base-role/DISTRIBUTED_WORK.md`](../roles/base-role/DISTRIBUTED_WORK.md)) built on this
> initiative's s4-s5 layout: `ops/campaigns/<C-id>/CAMPAIGN.json` + `tasks/<TASK_ID>/TASK.json` / `LEASE.json` /
> `attempts/<A-id>/RECEIPT.json`, checked by `python -m workgraph`. It is a capability, not a migration: the transition
> policy below still holds for existing work. First operator-selected campaign: C-004 (RSO Builder Cell). 2026-10-03: optional Epic level above Thread
> (`ops/epics/<EP-id>/EPIC.json`; Epic -> Thread -> Campaign -> [Experiment] -> Task -> Attempt); first epic EP-PHASE3.

This directory holds the **Git-native lab control plane** initiative, a *proposed* future operating model for Prometheus.
It was captured on 2026-09-27 by Harmonia at the operator's request, as information for the fleet, **not as an instruction to it.**

| File | What |
|---|---|
| `initiatives/GIT_NATIVE_LAB_CONTROL_PLANE.md` | The initiative: Thread → Campaign → Experiment → Task → Attempt; Git as durable authority; claim and resource leases; CWO; Atlas boundary; evidence maturity; cleanup contract; transition policy; the recorded first-pilot intent |
| `initiatives/GIT_NATIVE_OPEN_QUESTIONS.md` | Design questions deliberately left open for the pilot to answer |
| `initiatives/GIT_NATIVE_EXISTING_MACHINERY.md` | Queue, lease, GPU-reservation, fleet and forensic machinery already in Prometheus: to be mined, not replaced |

**If you are an agent reading this:** keep working under your current contracts. Do not create `ops/tasks/`,
`ops/campaigns/`, leases, CWOs or resource files, and do not convert your queue or journals. Transition happens only
for a seat or campaign the operator explicitly selects, by a separate directive. The first candidate (Archaeon on M2)
is recorded as *intent* only; it has not been directed.
