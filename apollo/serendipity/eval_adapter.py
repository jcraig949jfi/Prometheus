"""eval_adapter.py -- Apollo's EvaluationAdapter boundary (charter S4).

Wraps the budget-consuming /v0/search and /v0/evaluate with the transport doctrine
from remote.py: a TransportIndeterminate is NEVER a result -- reconcile the trace
against the host ledger before assuming anything, and never silently re-spend budget.
"""
from __future__ import annotations

from remote import TransportIndeterminate


def burst(client, driver, engine_id, task_id, seed, budget, config=None,
          trace_id=None) -> dict:
    """One bounded search burst. driver in {random,objective,novelty,map_elites}.
    Returns the driver report. On indeterminate transport, reconciles and raises
    (a budget-consuming op is not blindly retried here)."""
    body = {"driver": driver, "engine_id": engine_id, "task_id": task_id,
            "seed": seed, "budget": budget}
    if config:
        body["config"] = config
    try:
        return client.post("/v0/search", body, trace_id=trace_id)
    except TransportIndeterminate as e:
        outcome = client.reconcile(e.trace_id)
        raise RuntimeError(f"search indeterminate trace={e.trace_id}; "
                           f"ledger committed={outcome.get('committed')} "
                           f"-- inspect before re-spending budget") from e


def evaluate(client, artifact_id, task_id, seed, trace_id=None) -> dict:
    """Evaluate one artifact on a task. Content-addressed/idempotent -> a single
    same-trace retry is safe on indeterminate transport."""
    body = {"artifact_id": artifact_id, "task_id": task_id, "seed": seed}
    try:
        return client.post("/v0/evaluate", body, trace_id=trace_id)
    except TransportIndeterminate:
        return client.post("/v0/evaluate", body, trace_id=trace_id)
