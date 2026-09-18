"""proteus.behavior_fingerprint.v1 -- the T0 row every evaluation emits (Campaign 6 Axis T, organism side).

Consumers fixed the envelope before this was written (Daedalus SFE_C6_INTERFACE_DELTA s3; Vivarium
#455; Mnemosyne #459): one row per evaluation, <= 1 KiB canonical JSON, carrying at least
{eval, lt, organism_id, parent_id, digest}; the engine sees only digests, PEW anchors segments of
rows. The FIELDS are Proteus's, and the rule for them is the 09-05 lesson: nothing that varies
between two runs of the same organism on the same inputs (no timings), and nothing the world
scores with. A fingerprint is a description of WHAT THE ORGANISM DID, never of how well.

Two substrates, one row shape:
    v0  (proteus.foundry.vm.Meter.as_dict minus wall_s/cpu_s/gpu)   ops, ops_by_category, ticks,
        budget_exhausted_ticks, branches, code writes, in/out counts, rnd draws, footprint
    graph (proteus.graph.vm.GraphMeter.as_dict)                      ops, ops_by_category, ticks,
        budget_exhausted_ticks, nodes_executed, node_exec (digested + top-k), routes, call depth,
        in/out counts, rnd draws, state writes + addresses (digested), dormant count
plus the OUTPUT summary (per channel: count, distinct, digest of the sequence) and the STATE
summary the substrate exposes. Long vectors are digested (sha256 over canonical JSON) with a
bounded top-k kept, so the row never exceeds the cap however large the genome.

Known limit, measured (test_fingerprint.py::test_sensitivity): the frozen v0 Meter exposes no set of
written tape addresses, so on v0 two PUTs to different keys yield the same T0 row; the graph meter
carries state_addrs_digest and separates them. Widening v0's meter is a runtime transition
(PROTEUS-19) and is not done here.

Cheat control (schema): any key or nested key matching FORBIDDEN (reward, fitness, score, payoff,
held-out, world_id, cell, target ...) is REFUSED. The dictionary must not be able to become an
invisible fitness function through this row (directive s3 / Amendment 1 s2).
"""
from __future__ import annotations

import re

from proteus.foundry.identity import canonical_json, hash_obj, sha256_hex

SCHEMA = "proteus.behavior_fingerprint.v1"
ROW_BYTES_MAX = 1024
TOPK = 8
FORBIDDEN = re.compile(r"(reward|fitness|score|payoff|heldout|held_out|world_id|cell|target|solved|competence|rank|elite)", re.I)
V0_TIMING_KEYS = ("wall_s", "cpu_s", "gpu")


def _digest_seq(seq) -> str:
    return sha256_hex(canonical_json(list(seq)))[:16]


def _topk(counts: list, k: int = TOPK) -> list:
    idx = sorted(range(len(counts)), key=lambda i: (-counts[i], i))[:k]
    return [[i, counts[i]] for i in idx if counts[i]]


def output_summary(outputs: list) -> list:
    out = []
    for ch in outputs:
        out.append({"n": len(ch), "distinct": len(set(ch)), "digest": _digest_seq(ch) if ch else None})
    return out


def _check_forbidden(obj, path="") -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if FORBIDDEN.search(str(k)):
                raise ValueError("forbidden field in fingerprint: %s%s" % (path, k))
            _check_forbidden(v, path + str(k) + ".")
    elif isinstance(obj, list):
        for v in obj:
            _check_forbidden(v, path)


def from_v0_meter(md: dict) -> dict:
    """Meter.as_dict() of the frozen VM, minus the timing keys (T2 rule: 40/40 reproducible)."""
    body = {k: v for k, v in md.items() if k not in V0_TIMING_KEYS}
    return {"substrate": "v0", "runtime": "proteus.runtime.v0", **body}


def from_graph_meter(md: dict, n_dormant: int) -> dict:
    node_exec = md["node_exec"]
    addrs = md["state_addresses_written"]
    return {
        "substrate": "graph", "runtime": "proteus.runtime.graph.v1",
        "ops": md["ops"], "ops_by_category": md["ops_by_category"],
        "ticks": md["ticks"], "budget_exhausted_ticks": md["budget_exhausted_ticks"], "statuses": md["statuses"],
        "nodes_total": len(node_exec), "nodes_executed": md["nodes_executed"], "nodes_dormant": n_dormant,
        "node_exec_digest": _digest_seq(node_exec), "node_exec_topk": _topk(node_exec),
        "routes": {k: v for k, v in list(md["route_taken"].items())[:TOPK]}, "routes_n": len(md["route_taken"]),
        "call_depth_max_reached": md["call_depth_max_reached"], "call_depth_refused": md["call_depth_refused"],
        "in_reads": md["in_reads"], "out_writes": md["out_writes"], "out_dropped": md["out_dropped"],
        "rnd_draws": md["rnd_draws"],
        "state_writes": md["state_writes"], "state_addrs_n": len(addrs), "state_addrs_digest": _digest_seq(addrs) if addrs else None,
    }


def fingerprint(*, organism_id: str, parent_id: str | None, eval_ordinal: int, logical_time: int,
                behaviour: dict, outputs: list, extra: dict | None = None) -> dict:
    """Assemble the row. `behaviour` is from_v0_meter(...) or from_graph_meter(...). `extra` is a
    producer's own small block (e.g. lineage delta refs); it is checked against FORBIDDEN too."""
    row = {
        "schema_version": SCHEMA,
        "eval": int(eval_ordinal), "lt": int(logical_time),
        "organism_id": organism_id, "parent_id": parent_id,
        "behaviour": behaviour,
        "outputs": output_summary(outputs),
    }
    if extra:
        row["extra"] = extra
    _check_forbidden(row)
    body = {k: v for k, v in row.items()}
    row["digest"] = "sha256:" + hash_obj(body)
    enc = canonical_json(row).encode("utf-8")
    if len(enc) > ROW_BYTES_MAX:
        raise ValueError("fingerprint row %d bytes exceeds %d" % (len(enc), ROW_BYTES_MAX))
    return row


def verify(row: dict) -> None:
    if row.get("schema_version") != SCHEMA:
        raise ValueError("schema mismatch")
    for k in ("eval", "lt", "organism_id", "parent_id", "digest"):
        if k not in row:
            raise ValueError("missing " + k)
    body = {k: v for k, v in row.items() if k != "digest"}
    if row["digest"] != "sha256:" + hash_obj(body):
        raise ValueError("digest does not recompute")
    _check_forbidden(row)
    if len(canonical_json(row).encode("utf-8")) > ROW_BYTES_MAX:
        raise ValueError("row exceeds cap")
