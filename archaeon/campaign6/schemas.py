"""Campaign 6 record schemas (v0.1). Plain dicts with validators; every record carries its schema
id so a reader can refuse what it does not know. Nothing here interprets; these are the shapes
the observatory writes and the adjudicator reads.

  provenance.v1   who/what generated a run: lane label, generator id+version, seed, parameters,
                  parent run (branch), trigger receipt (if deepened), thresholds live.
  fingerprint.v1  T0: one fixed-shape behavioural summary per evaluation.
  detector.v1     one ruler's verdict on one event neighbourhood.
  event.v1        an event neighbourhood: which rulers fired, disagreement flag, tier reached.
  freeze.v1       T2 packet: organism, parent, ancestors, siblings, world state, pressure
                  history, mutation chain, T1 window, replay packet id.
  replay.v1       one replay attempt A-G with its receipt.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List

from .c6base import LANES, DETECTORS, DETECTOR_OUTCOMES, TIERS, REPLAYS, PRESSURE_KINDS


def digest(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


class SchemaError(ValueError):
    pass


def _req(d: dict, keys, schema: str) -> None:
    missing = [k for k in keys if k not in d]
    if missing:
        raise SchemaError("%s missing %s" % (schema, missing))


def provenance(lane: str, generator: str, version: str, seed: int, params: dict, *, parent_run: str | None = None,
               trigger: dict | None = None, thresholds_digest: str | None = None, note: str = "") -> dict:
    if lane not in LANES:
        raise SchemaError("lane %r" % lane)
    rec = {"schema": "archaeon.c6.provenance.v1", "lane": lane, "generator": generator, "generator_version": version, "seed": seed,
           "params": params, "parent_run": parent_run, "trigger": trigger, "thresholds_digest": thresholds_digest, "note": note}
    rec["run_id"] = digest({k: v for k, v in rec.items() if k != "note"})[:24]
    return rec


FINGERPRINT_FIELDS = (
    "action_hist",            # list[int] per action channel
    "state_transitions",      # int: organism internal-state transitions observed
    "resources_touched",      # list[str]: resource types read or consumed
    "objects_changed",        # int
    "internal_state_usage",   # int: memory cells / node states written
    "node_exec_counts",       # dict node_id -> int (or bucketed)
    "module_exec_counts",     # dict module_id -> int
    "routing_decisions",      # int
    "memory_reads", "memory_writes",
    "interaction_partners",   # int distinct
    "communication_events",   # int
    "survival_transitions",   # list[str]
    "env_dependencies",       # list[str]: world features whose state was read
    "reward",                 # float (present, never the only field)
    "genotype_digest", "phenotype_digest",
)


def fingerprint(**fields) -> dict:
    _req(fields, FINGERPRINT_FIELDS, "fingerprint.v1")
    rec = {"schema": "archaeon.c6.fingerprint.v1", **{k: fields[k] for k in FINGERPRINT_FIELDS}}
    rec["fp_digest"] = digest({k: rec[k] for k in FINGERPRINT_FIELDS if k not in ("reward",)})
    return rec


def detector_verdict(name: str, outcome: str, score: float | None, threshold: float | None, evidence: dict) -> dict:
    if name not in DETECTORS:
        raise SchemaError("detector %r" % name)
    if outcome not in DETECTOR_OUTCOMES:
        raise SchemaError("outcome %r" % outcome)
    return {"schema": "archaeon.c6.detector.v1", "detector": name, "outcome": outcome, "score": score, "threshold": threshold, "evidence": evidence}


def event(run_id: str, organism_id: str, generation: int, verdicts: List[dict], tier: str) -> dict:
    if tier not in TIERS:
        raise SchemaError("tier %r" % tier)
    fired = [v["detector"] for v in verdicts if v["outcome"] == "FIRE"]
    quiet = [v["detector"] for v in verdicts if v["outcome"] == "QUIET"]
    unable = [v["detector"] for v in verdicts if v["outcome"] == "UNABLE"]
    rec = {"schema": "archaeon.c6.event.v1", "run_id": run_id, "organism_id": organism_id, "generation": generation, "verdicts": verdicts,
           "fired": fired, "quiet": quiet, "unable": unable, "disagreement": bool(fired) and bool(quiet), "classifier_failure": bool(unable),
           "tier": tier, "interpretation": None}          # interpretation stays None until adjudication (directive: preserve before explaining)
    rec["event_id"] = digest({k: v for k, v in rec.items() if k not in ("interpretation",)})[:24]
    return rec


def freeze_packet(event_id: str, organism: dict, parent: dict | None, ancestors: List[dict], siblings: List[dict], world_state: dict,
                  pressure_history: List[dict], mutation_chain: List[dict], t1_window: List[dict]) -> dict:
    for p in pressure_history:
        if p.get("kind") not in PRESSURE_KINDS:
            raise SchemaError("pressure kind %r" % p.get("kind"))
    rec = {"schema": "archaeon.c6.freeze.v1", "event_id": event_id, "organism": organism, "parent": parent, "ancestors": ancestors, "siblings": siblings,
           "world_state": world_state, "pressure_history": pressure_history, "mutation_chain": mutation_chain, "t1_window": t1_window}
    rec["packet_digest"] = digest(rec)
    return rec


def replay_receipt(event_id: str, kind: str, reproduced: bool | None, details: dict) -> dict:
    if kind not in REPLAYS:
        raise SchemaError("replay %r" % kind)
    return {"schema": "archaeon.c6.replay.v1", "event_id": event_id, "kind": kind, "reproduced": reproduced, "details": details}


def validate(rec: dict) -> str:
    """Return the schema id or raise. Readers call this before trusting a record."""
    s = rec.get("schema", "")
    if not s.startswith("archaeon.c6."):
        raise SchemaError("not a campaign-6 record: %r" % s)
    return s
