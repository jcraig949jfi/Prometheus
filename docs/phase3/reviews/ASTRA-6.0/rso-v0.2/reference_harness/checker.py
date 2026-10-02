"""Immutable, scoped finite-contract checker. No filesystem artifact loader."""

from dataclasses import dataclass, replace
from enum import Enum
from hashlib import sha256
import json
from types import MappingProxyType

from finite import search_record


class Status(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    UNQUALIFIED = "UNQUALIFIED"


@dataclass(frozen=True)
class Decision:
    status: Status
    reasons: tuple = ()


def result(status, reason):
    return Decision(status, (reason,))


def text(value):
    if type(value) is not str or not value or not value.isascii():
        raise ValueError("nonempty ASCII text required")


def sequence(value):
    if type(value) not in (list, tuple):
        raise ValueError("list or tuple required")
    return tuple(value)


@dataclass(frozen=True)
class Artifact:
    key: str
    digest: str
    size: int

    def __post_init__(self):
        text(self.key)
        if (type(self.digest) is not str or len(self.digest) != 64
                or any(c not in "0123456789abcdef" for c in self.digest)):
            raise ValueError("SHA-256 required")
        if type(self.size) is not int or not 0 <= self.size <= 4096:
            raise ValueError("artifact size outside domain")


@dataclass(frozen=True)
class Node:
    id: str
    scope: tuple
    kind: str
    predicate: str
    deps: tuple = ()
    artifact: Artifact = None

    def __post_init__(self):
        for value in (self.id, self.kind, self.predicate):
            text(value)
        scope, deps = sequence(self.scope), sequence(self.deps)
        if len(scope) != 8 or len(set(deps)) != len(deps):
            raise ValueError("eight scope axes and unique dependencies required")
        for value in scope + deps:
            text(value)
        if self.kind not in ("evidence", "claim"):
            raise ValueError("unknown node kind")
        if self.artifact is not None and type(self.artifact) is not Artifact:
            raise ValueError("immutable artifact reference required")
        if self.kind == "claim" and self.artifact is not None:
            raise ValueError("claim cannot supply its own verdict artifact")
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "deps", deps)


@dataclass(frozen=True)
class Graph:
    nodes: tuple
    invalidated: tuple = ()

    def __post_init__(self):
        nodes, invalidated = sequence(self.nodes), sequence(self.invalidated)
        if len(nodes) > 64 or any(type(n) is not Node for n in nodes):
            raise ValueError("at most 64 immutable nodes")
        ids = {n.id for n in nodes}
        if len(ids) != len(nodes) or any(i not in ids for i in invalidated):
            raise ValueError("duplicate ID or unknown invalidation")
        object.__setattr__(self, "nodes", nodes)
        object.__setattr__(self, "invalidated", tuple(sorted(set(invalidated))))

    def invalidate(self, source):
        """Trusted caller action; append closure without changing old snapshots."""
        if source not in {n.id for n in self.nodes}:
            raise ValueError("unknown invalidation source")
        seeds = set(self.invalidated) | {source}
        bad = set(seeds)
        while True:
            grown = bad | {n.id for n in self.nodes if set(n.deps) & bad}
            if grown == bad:
                return replace(self, invalidated=tuple(sorted(bad)))
            bad = grown


# Checker-owned v1 fixture policies; callers cannot pass required_facets or PASS.
POLICY = MappingProxyType({
    "retention": ("retention", "channel", "detector"),
    "cold_reach": ("cold", "detector"),
    "repair_reach": ("repair", "detector"),
    "continuation": ("continuation",),
    "reset": ("reset",),
    "reencoding": ("encoding",),
    "updater": ("updater",),
})
EXPECTED = MappingProxyType({
    "source": (0, 1), "retention": (0, 1), "channel": (1, 2, 4),
    "detector": (2, 1, 0),
    "continuation": ((0, 1), (1, 1), (1, 0), (0, 0)),
    "reset": ((0, 0), (1, 0), (0, 0), (1, 0)),
    "encoding": ((0, 1), (0, 1)),
    "updater": (
        ("-1", "-1", "-1", "-1/2", "0", "-1"),
        ("1", "1", "1", "1/2", "0", "1"),
        ("-1", "-1", "-2", "-1/2", "0", "-1"),
        ("1", "1", "2", "1/2", "0", "1"),
        ("-1", "-1", "-2", "-2", "0", "-1"),
        ("1", "1", "2", "2", "0", "1"),
        ("-1", "-1", "-4", "-2", "0", "-1"),
        ("1", "1", "4", "2", "0", "1")),
})


def structure(graph):
    index = {n.id: n for n in graph.nodes}
    for parent in graph.nodes:
        for dep in parent.deps:
            if dep not in index:
                return result(Status.BLOCKED, "DANGLING:" + dep)
            node = index[dep]
            if node.scope != parent.scope:
                return result(Status.FAIL, "WRONG_SCOPE")
            if node.kind != "evidence":
                return result(Status.FAIL, "WRONG_ROLE")
    active, done = set(), set()

    def visit(key):
        if key in active:
            return False
        if key in done:
            return True
        active.add(key)
        if not all(visit(dep) for dep in index[key].deps):
            return False
        active.remove(key)
        done.add(key)
        return True

    return (Decision(Status.PASS) if all(visit(k) for k in index)
            else result(Status.FAIL, "CYCLE"))


def artifact_check(ref, blobs, anchors):
    """Anchors are caller-owned evidence Nodes, NOT taken from the graph."""
    if ref is None or ref.key not in blobs:
        return result(Status.BLOCKED, "MISSING_ARTIFACT")
    if ref.key not in anchors:
        return result(Status.BLOCKED, "MISSING_EXTERNAL_ANCHOR")
    anchor = anchors[ref.key]
    if type(anchor) is not Node or anchor.kind != "evidence" or anchor.artifact != ref:
        return result(Status.FAIL, "ANCHOR_MISMATCH")
    data = blobs[ref.key]
    if type(data) is not bytes or len(data) != ref.size:
        return result(Status.FAIL, "ARTIFACT_LENGTH")
    if sha256(data).hexdigest() != ref.digest:
        return result(Status.FAIL, "ARTIFACT_DIGEST")
    return Decision(Status.PASS)


def freeze_json(value, depth=0):
    if depth > 8:
        raise ValueError("JSON depth limit")
    if value is None or type(value) is int:
        return value
    if type(value) is str and value.isascii():
        return value
    if type(value) is list:
        return tuple(freeze_json(v, depth + 1) for v in value)
    if type(value) is dict:
        return {k: freeze_json(v, depth + 1) for k, v in value.items()}
    raise ValueError("booleans, floats and non-ASCII are not measurements")


def unique_object(pairs):
    if len(dict(pairs)) != len(pairs):
        raise ValueError("duplicate JSON key")
    return dict(pairs)


def evidence_check(node, blobs, anchors):
    integrity = artifact_check(node.artifact, blobs, anchors)
    if integrity.status != Status.PASS:
        return integrity
    if node != anchors[node.artifact.key]:
        return result(Status.FAIL, "EVIDENCE_BINDING")
    try:
        data = freeze_json(json.loads(blobs[node.artifact.key].decode("ascii"),
                                      object_pairs_hook=unique_object))
        facet = node.predicate
        if facet == "detector" and data is None:
            return result(Status.UNQUALIFIED, "DETECTOR_UNAVAILABLE")
        if facet in ("cold", "repair"):
            if type(data) is not dict or set(data) != {"lineage", "policy", "proposals", "states"}:
                raise ValueError("search record schema")
            lineage = data["lineage"]
            if lineage not in ((0,), (2, 1)):
                raise ValueError("founder construction")
            if facet == "cold" and lineage != (0,):
                return result(Status.FAIL, "SEARCH_REGIME_MISMATCH")
            if facet == "repair" and lineage != (2, 1):
                return result(Status.FAIL, "SEARCH_REGIME_MISMATCH")
            expected = freeze_json(search_record(lineage, data["policy"]))
            if data != expected or data["states"][-1] != 2:
                return result(Status.FAIL, "SEARCH_TRACE_OR_HIT")
        elif facet not in EXPECTED:
            return result(Status.BLOCKED, "UNIMPLEMENTED_FACET")
        elif data != EXPECTED[facet]:
            return result(Status.FAIL, "BAD_EVIDENCE:" + facet)
    except (ValueError, TypeError, KeyError, IndexError, RecursionError):
        return result(Status.FAIL, "BAD_EVIDENCE_SCHEMA")
    return Decision(Status.PASS)


def evaluate(graph, claim_id, blobs, anchors):
    index = {n.id: n for n in graph.nodes}
    claim = index.get(claim_id)
    if claim is None or claim.kind != "claim":
        return result(Status.BLOCKED, "UNKNOWN_CLAIM")
    if claim.predicate == "strong_recursion":
        return result(Status.UNQUALIFIED, "NO_STRONG_RECURSION_DETECTOR")
    if claim.predicate not in POLICY:
        return result(Status.BLOCKED, "UNIMPLEMENTED_CLAIM")
    integrity = structure(graph)
    if integrity.status != Status.PASS:
        return integrity
    reports = []
    facets = [index[key].predicate for key in claim.deps]
    if len(facets) != len(set(facets)):
        return result(Status.FAIL, "DUPLICATE_FACET")
    missing = set(POLICY[claim.predicate]) - set(facets)
    if missing:
        reports.append(result(Status.BLOCKED, "MISSING_FACET:" + ",".join(sorted(missing))))
    seen = set()
    blobs, anchors = dict(blobs), dict(anchors)

    def inspect(key):
        if key in seen:
            return
        seen.add(key)
        node = index[key]
        if key in graph.invalidated:
            reports.append(result(Status.BLOCKED, "INVALIDATED:" + key))
        if node.kind == "evidence":
            reports.append(evidence_check(node, blobs, anchors))
        for dep in node.deps:
            inspect(dep)

    inspect(claim_id)
    priority = (Status.PASS, Status.UNQUALIFIED, Status.BLOCKED, Status.FAIL)
    status = max((r.status for r in reports), key=priority.index, default=Status.PASS)
    return Decision(status, tuple(reason for r in reports for reason in r.reasons))