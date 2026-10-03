# Phase 2-B operating cadence -- a refreshed CWO about every 48 hours

Operator directive 2026-10-03 (verbatim: roles/Achilles/prompts/2026-10-03_generic_workers/, s9-s11, s23). Phase 2-B is LOW-band, work-conserving
background science: it uses idle machines and yields to higher bands (roles/base-role/DISTRIBUTED_WORK.md s13).

## The cycle (per active, non-parked Phase 2-B engine/seat)
- BEGINNING: the seat reviews the previous ~48 hours and makes the epistemic decisions -- interpret results,
  triage defects, decide replays, choose the next experiments. Input: `python -m workgraph cwo-inputs EP-PHASE2B
  --hours 48 --previous <CWO-id>` (receipts, preemptions, unfinished work, escalations, anomalies, priority
  requests, cross-epic findings, resource use), plus forensic feedback and available resources.
- MIDDLE: execution, mostly deterministic and mostly by PrometheusWorkers: the seat writes complete
  GENERIC_WORKER packets (ATOMIC unless the engine registers otherwise) and does not watch them.
- END: results and receipts close. New work normally does not start if it cannot reasonably finish before the
  next CWO boundary; an exception is registered in the packet's notes (or as a priority request).

The refreshed CWO is published by Aporia under its charter (ops/work_orders/, ops/fleet/), assembled mostly from
the cwo-inputs JSON. It is a reasoning checkpoint, not a reason for constant inference.

## Close categories at the boundary
DONE | SCIENTIFIC_OUTCOME | ENGINEERING_FAIL | PREEMPTED_RESOURCE | DEFERRED | SUPERSEDED. PREEMPTED_RESOURCE keeps
the original registration: "replay unchanged when capacity becomes available" -- no scientific reconsideration
unless circumstances changed.

## Inference economy
Wake a seat for an unexpected result, an ambiguous defect, a comparator choice, a redesign, an interpretation,
or the next campaign. Do not wake it to watch jobs, poll, move files, rerun unchanged commands or summarize
deterministic status.

## Protection for a run worth finishing
Typical case: "this run can start on idle resources normally, but once started it is worth allowing it to
finish" -> a PREEMPTION_PROTECTION priority request for that experiment (LOW -> MEDIUM, with an expiry), decided
by the operator (DISTRIBUTED_WORK.md s14). Other experiments of the same seat stay LOW.
