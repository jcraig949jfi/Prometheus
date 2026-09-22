"""Executable integrity invariants (operator directive s6). Each is a function that returns None or raises
IntegrityHalt(invariant, receipt, invalidated). The scheduler calls them at the points where the evidence
is produced; a raise stops the scheduler globally and writes GLOBAL_HALT.json with the three named things.
Nothing here depends on interpretation.
"""
from __future__ import annotations

import json
from typing import List

from archaeon.campaign6 import schemas as S


class IntegrityHalt(RuntimeError):
    def __init__(self, invariant: str, receipt: dict, invalidated: str):
        super().__init__("%s: %s" % (invariant, invalidated))
        self.invariant, self.receipt, self.invalidated = invariant, receipt, invalidated


def check_checkpoint_ancestry(chunks: List[dict]) -> None:
    """chunk[i].checkpoint_in digest must equal chunk[i-1].checkpoint_out digest."""
    for i in range(1, len(chunks)):
        prev_out = chunks[i - 1]["out"]["checkpoint_out"]["digest"]; this_in = chunks[i]["checkpoint_in_digest"]
        if prev_out != this_in:
            raise IntegrityHalt("checkpoint_ancestry", {"chunk": i, "prev_out": prev_out, "this_in": this_in}, "every chunk after %d of this run" % (i - 1))


def check_replay_A(spec_hash: str, out_digest_first: str, out_digest_replay: str, chunk: int) -> None:
    if out_digest_first != out_digest_replay:
        raise IntegrityHalt("deterministic_replay", {"spec_hash": spec_hash, "chunk": chunk, "first": out_digest_first, "replay": out_digest_replay},
                            "every result produced from this spec (replay A required by the spec)")


def check_evidence_writes(out: dict) -> None:
    """Every event, freeze and anchor carries a known schema; anchors cover the evaluations and chain."""
    for e in out["events"]:
        S.validate(e)
        if e.get("interpretation") is not None:
            raise IntegrityHalt("observation_interpretation_separation", {"event_id": e["event_id"]}, "this segment's events")
    for f in out["freezes"]:
        if f.get("schema") != "sfe.freeze.v1" or f.get("interpretation") is not None:
            raise IntegrityHalt("observation_interpretation_separation", {"event_id": f.get("event_id")}, "this segment's freezes")
    n = sum(a["n"] for a in out["anchors"])
    if n != out["evaluations"]:
        raise IntegrityHalt("evidence_write_anchor_coverage", {"anchored": n, "evaluations": out["evaluations"]}, "this segment's T0 sidecar")
    for i in range(1, len(out["anchors"])):
        if out["anchors"][i]["prev_segment_hash"] != out["anchors"][i - 1]["segment_hash"]:
            raise IntegrityHalt("evidence_write_anchor_chain", {"anchor": i}, "this segment's T0 sidecar")


def check_provenance(spec: dict, seg_spec: dict) -> None:
    pv = seg_spec.get("provenance", {})
    if pv.get("schema") != "archaeon.c6.provenance.v1" or pv.get("lane") not in ("HUMAN_DIRECTED", "LLM_PROPOSED", "PROCEDURAL", "EVOLUTION_GENERATED", "MIXED"):
        raise IntegrityHalt("provenance", {"experiment_id": spec["experiment_id"]}, "this run")
    if not seg_spec.get("spec_hash"):
        raise IntegrityHalt("provenance", {"experiment_id": spec["experiment_id"], "reason": "no spec_hash"}, "this run")


def check_registry_write(path, before_lines: int) -> None:
    """An append-only file must only grow."""
    after = sum(1 for _ in open(path, encoding="utf-8"))
    if after < before_lines:
        raise IntegrityHalt("unrecoverable_runtime_state", {"path": str(path), "before": before_lines, "after": after}, "the registry")
