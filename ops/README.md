# ops/

> **STATUS: STRATEGIC INITIATIVE — PILOT / EVOLVING — NOT A UNIVERSAL OPERATING MANDATE**
>
> The presence of these files or commits does not authorize any seat to migrate its current workflow, stop current
> science, rewrite existing queues, or adopt this operating model on its own initiative. Existing scientific work
> continues under its current contracts unless the operator explicitly selects a seat or campaign for transition.

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
