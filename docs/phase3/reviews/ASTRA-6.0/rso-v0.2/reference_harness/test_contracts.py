from dataclasses import FrozenInstanceError, replace
from hashlib import sha256
import json
import unittest

import checker
import finite


SCOPE = ("toy-v1", "chain-v1", "key-v1", "fixed-v1", "boundary-v1",
         "budget-v1", "readout-v1", "exposure-v1")
REQUIRES = {"retention": ("retention", "channel", "detector"),
            "cold_reach": ("cold", "detector"), "repair_reach": ("repair", "detector"),
            "continuation": ("continuation",), "reset": ("reset",),
            "reencoding": ("encoding",), "updater": ("updater",)}


def bundle(api, claim="retention", extra=None):
    values = {"source": [0, 1], "retention": finite.bit_answers("carry"),
              "channel": [1, 2, 4], "detector": finite.detector_counts()}
    values.update(extra or {})
    blobs = {k: json.dumps(v).encode("ascii") for k, v in values.items()}
    refs = {k: api.Artifact(k, sha256(v).hexdigest(), len(v)) for k, v in blobs.items()}
    nodes = [api.Node(k, SCOPE, "evidence", k,
                      {"detector": ("source",), "retention": ("detector",)}.get(k, ()), ref)
             for k, ref in refs.items()]
    anchors = {n.artifact.key: n for n in nodes}  # Synthetic trusted input, not independent custody.
    nodes.append(api.Node("claim", SCOPE, "claim", claim, REQUIRES.get(claim, ())))
    return api.Graph(nodes), blobs, anchors


def change(graph, key, **updates):
    return replace(graph, nodes=tuple(replace(n, **updates) if n.id == key else n
                                      for n in graph.nodes))


class ContractTests(unittest.TestCase):
    api = checker

    def check(self, graph, blobs, anchors, status, reason=None, claim="claim"):
        result = self.api.evaluate(graph, claim, blobs, anchors)
        self.assertEqual(result.status.value, status)
        if reason is not None:
            self.assertIn(reason, result.reasons)
        return result

    def test_clean_claims_and_strong_limit(self):
        examples = {"retention": {}, "cold_reach": {"cold": finite.search_record((0,), "enumerate")},
                    "repair_reach": {"repair": finite.search_record((2, 1), "strict")},
                    "continuation": {"continuation": [finite.continuation(s) for s in
                                                       ((0, 0), (1, 0), (0, 1), (1, 1))]},
                    "reset": {"reset": [finite.BoundaryState(a, b, (b,)).clean_reset().tick().observe()
                                        for b in (0, 1) for a in (0, 1)]},
                    "reencoding": {"encoding": [[finite.read_bit(finite.encode_bit(b, e), e)
                                                  for b in (0, 1)] for e in ("plain", "one_hot")]},
                    "updater": {"updater": finite.updater_rows()}}
        for claim, extra in examples.items():
            with self.subTest(claim=claim):
                graph, blobs, anchors = bundle(self.api, claim, extra)
                self.check(graph, blobs, anchors, "PASS")
                strong = change(graph, "claim", predicate="strong_recursion")
                self.check(strong, blobs, anchors, "UNQUALIFIED", "NO_STRONG_RECURSION_DETECTOR")
                self.check(strong, {}, {}, "UNQUALIFIED")

    def test_missing_facet(self):
        graph, blobs, anchors = bundle(self.api)
        for removed in ("retention", "channel", "detector"):
            deps = tuple(f for f in REQUIRES["retention"] if f != removed)
            self.check(change(graph, "claim", deps=deps), blobs, anchors,
                       "BLOCKED", "MISSING_FACET:" + removed)

    def test_wrong_scope(self):
        graph, blobs, anchors = bundle(self.api)
        for axis in range(8):
            scope = list(SCOPE)
            scope[axis] += "-changed"
            self.check(change(graph, "retention", scope=scope), blobs, anchors, "FAIL", "WRONG_SCOPE")

    def test_whole_graph_relabel(self):
        graph, blobs, anchors = bundle(self.api)
        revised = replace(graph, nodes=tuple(replace(n, scope=("new-physics",) + n.scope[1:])
                                             for n in graph.nodes))
        self.check(revised, blobs, anchors, "FAIL", "EVIDENCE_BINDING")

    def test_stripped_dependency_binding(self):
        graph, blobs, anchors = bundle(self.api)
        self.check(change(graph, "detector", deps=()), blobs, anchors, "FAIL", "EVIDENCE_BINDING")

    def test_repair_cannot_be_cold(self):
        graph, blobs, anchors = bundle(self.api, "cold_reach",
                                      {"cold": finite.search_record((2, 1), "strict")})
        self.check(graph, blobs, anchors, "FAIL", "SEARCH_REGIME_MISMATCH")

    def test_artifact_digest(self):
        graph, blobs, anchors = bundle(self.api)
        self.assertEqual(blobs["retention"], b"[0, 1]")
        blobs["retention"] = b"[ 0,1]"  # Same parsed observation AND length; different anchored bytes.
        self.check(graph, blobs, anchors, "FAIL", "ARTIFACT_DIGEST")

    def test_transitive_invalidation(self):
        graph, blobs, anchors = bundle(self.api)
        # Truly unrelated reset evidence, not renamed dependent receipts with stripped deps.
        raw = b"[[0,0],[1,0],[0,0],[1,0]]"
        ref = self.api.Artifact("reset", sha256(raw).hexdigest(), len(raw))
        node = self.api.Node("reset", SCOPE, "evidence", "reset", (), ref)
        blobs["reset"], anchors["reset"] = raw, node
        unrelated = self.api.Node("other", SCOPE, "claim", "reset", ("reset",))
        graph = replace(graph, nodes=graph.nodes + (node, unrelated))
        revised = graph.invalidate("source")
        self.assertEqual(set(revised.invalidated), {"source", "detector", "retention", "claim"})
        self.assertEqual(graph.invalidated, ())
        self.assertEqual(revised.invalidate("source"), revised)
        self.check(graph, blobs, anchors, "PASS")
        self.check(revised, blobs, anchors, "BLOCKED", "INVALIDATED:claim")
        self.check(revised, blobs, anchors, "PASS", claim="other")

    def test_four_statuses_and_non_boolean_evidence(self):
        self.assertEqual({s.value for s in self.api.Status}, {"PASS", "FAIL", "BLOCKED", "UNQUALIFIED"})
        graph, blobs, anchors = bundle(self.api, extra={"detector": None})
        self.check(graph, blobs, anchors, "UNQUALIFIED", "DETECTOR_UNAVAILABLE")
        for bad in ([1, 0], [False, True], {"PASS": True}, "PASS", [0.0, 1.0]):
            self.check(*bundle(self.api, extra={"retention": bad}), "FAIL")
        self.check(*bundle(self.api, "not_implemented"), "BLOCKED", "UNIMPLEMENTED_CLAIM")

    def test_immutable_graph_policy_and_permutation(self):
        graph, blobs, anchors = bundle(self.api)
        scope, deps = list(SCOPE), ["source"]
        node = self.api.Node("new", scope, "evidence", "source", deps, anchors["source"].artifact)
        scope[0], deps[0] = "changed", "changed"
        self.assertEqual(node.scope, SCOPE)
        self.assertEqual(node.deps, ("source",))
        with self.assertRaises(FrozenInstanceError):
            node.predicate = "PASS"
        with self.assertRaises(TypeError):
            self.api.POLICY["retention"] = ()
        with self.assertRaises(TypeError):
            self.api.evaluate(graph, "claim", blobs, anchors, required_facets=[])
        self.check(replace(graph, nodes=tuple(reversed(graph.nodes))), blobs, anchors, "PASS")

    def test_cycles_dangling_and_self_support(self):
        graph, blobs, anchors = bundle(self.api)
        self.check(change(graph, "source", deps=("retention",)), blobs, anchors, "FAIL", "CYCLE")
        self.check(change(graph, "source", deps=("absent",)), blobs, anchors, "BLOCKED", "DANGLING:absent")
        self.check(change(graph, "source", deps=("claim",)), blobs, anchors, "FAIL", "WRONG_ROLE")
        with self.assertRaises(ValueError):
            self.api.Graph(graph.nodes + (graph.nodes[0],))

    def test_anchor_and_length_requirements(self):
        graph, blobs, anchors = bundle(self.api)
        self.check(graph, blobs, {}, "BLOCKED", "MISSING_EXTERNAL_ANCHOR")
        self.check(graph, {}, anchors, "BLOCKED", "MISSING_ARTIFACT")
        altered = dict(blobs, retention=b"[0,1]")
        self.check(graph, altered, anchors, "FAIL", "ARTIFACT_LENGTH")
        ref = self.api.Artifact("retention", sha256(altered["retention"]).hexdigest(), 5)
        self.check(change(graph, "retention", artifact=ref), altered, anchors, "FAIL", "ANCHOR_MISMATCH")

    def test_schema_limits_and_duplicate_keys(self):
        graph, blobs, anchors = bundle(self.api)
        for raw in (b'{"x":0,"x":1}', b'NaN', b'[' * 10 + b'0' + b']' * 10):
            ref = self.api.Artifact("retention", sha256(raw).hexdigest(), len(raw))
            anchor = replace(anchors["retention"], artifact=ref)
            self.check(change(graph, "retention", artifact=ref), dict(blobs, retention=raw),
                       dict(anchors, retention=anchor), "FAIL", "BAD_EVIDENCE_SCHEMA")
        with self.assertRaises(ValueError):
            self.api.Artifact("huge", "0" * 64, 4097)
        with self.assertRaises(ValueError):
            self.api.Node("x", SCOPE[:-1], "claim", "retention")

    def test_semantic_trace_defects(self):
        for claim, extra in (
                ("retention", {"retention": finite.bit_answers("flip")}),
                ("cold_reach", {"cold": finite.search_record((0,), "strict")}),
                ("reset", {"reset": [finite.BoundaryState(a, b, (b,)).leaky_reset().tick().observe()
                                     for b in (0, 1) for a in (0, 1)]}),
                ("continuation", {"continuation": [finite.continuation((0, c)) for q, c in
                                                    ((0, 0), (1, 0), (0, 1), (1, 1))]}),
                ("reencoding", {"encoding": [[finite.biased_ruler(finite.encode_bit(b, e))
                                               for b in (0, 1)] for e in ("plain", "one_hot")]})):
            with self.subTest(claim=claim):
                self.check(*bundle(self.api, claim, extra), "FAIL")


if __name__ == "__main__":
    unittest.main()