"""ledger_v2.py — append-only ledger for v2 operators (same contract as v1's ledger)."""
from __future__ import annotations

import json
import os

ENTRY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ledger")
REQUIRED = ("id", "derivation", "dependencies", "creation_event", "admission_test",
            "effect_size", "ablation_result", "transfer_results",
            "observed_failure_region", "revisions", "status", "events")
STATUSES = ("candidate", "admitted", "bounded", "superseded", "rejected")


def new_entry(cid, derivation, dependencies, creation_event):
    return {"id": cid, "derivation": derivation, "dependencies": dependencies,
            "creation_event": creation_event, "admission_test": None,
            "effect_size": None, "ablation_result": None, "transfer_results": {},
            "observed_failure_region": None, "revisions": [],
            "status": "candidate", "events": [dict(creation_event, kind="created")]}


def append_event(entry, kind, **payload):
    entry["events"].append({"kind": kind, **payload})


def set_status(entry, status, reason):
    assert status in STATUSES, status
    append_event(entry, "status_change", frm=entry["status"], to=status, reason=reason)
    entry["status"] = status


def save(entry):
    for key in REQUIRED:
        assert key in entry, f"ledger entry missing {key}"
    os.makedirs(ENTRY_DIR, exist_ok=True)
    path = os.path.join(ENTRY_DIR, f"{entry['id']}.json")
    with open(path, "w") as f:
        json.dump(entry, f, indent=1, default=str)
    return path
