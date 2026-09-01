"""world_adapter.py -- Apollo's WorldAdapter boundary (charter S4).

Authors Apollo-OWNED tasks (worlds) in an isolated namespace. Tasks are content-
addressed; admin_metadata carries client_id/campaign/run_id so provenance is Apollo's.
Apollo never mutates or deletes another seat's world -- it only CREATES its own.

Foundry task = integer function-induction: train_cases are [[inputs...], output].
"""
from __future__ import annotations

CLIENT_ID = "apollo"


def affine_cases(a: int, b: int, xs):
    """f(x) = a*x + b as Foundry train_cases: [[x], a*x+b]."""
    return [[[x], a * x + b] for x in xs]


def ensure_task(client, train_cases, test_cases=None, campaign="slice_pilot",
                run_id="", rule="", trace_id=None) -> str:
    """Create (or content-address to) an Apollo-owned task. Returns task_id."""
    body = {
        "train_cases": train_cases,
        "admin_metadata": {"client_id": CLIENT_ID, "campaign": campaign,
                           "run_id": run_id, "rule": rule},
        "provenance": {"author": CLIENT_ID, "kind": "affine_induction"},
    }
    if test_cases:
        body["test_cases"] = test_cases
    return client.post("/v0/tasks", body, trace_id=trace_id)["task_id"]
