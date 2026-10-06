"""D1: canonical bytes, the synthetic.v1 runtime, and semantic identity independent of git (CONTRACT s1-s2).

The known-answer vectors come from an independent reference (straight hashlib, below), not from the
package, so they pin the CONTRACT's formulas; running this file on Windows and on Linux is D3 case 7's
cross-host evidence."""
import hashlib
import json
import unittest

from moonshot.epoch import canonical as C
from moonshot.epoch import model, runtime
from moonshot.epoch import store as S
from moonshot.epoch.tests.harness import Harness

KAT_INITIAL = b"moonshot kat genesis\n"
KAT_PARAMS = {"work_iterations": 1000, "trace_every": 250, "checkpoint_bytes": 64}
KAT = {  # epoch_index: (work_id, epoch_digest, trace_sha256, checkpoint_sha256)
    1: ("f16fc9195859f2bb969511aa312ba1979d039ecddcd4ab34759183711baa1f72",
        "02af8ac6ad9e920d5b3ac6c9343713b5d0ff9eb83b0a55338942141178ee6385",
        "263f9463969688376c4cb05a8b626892645ef353f23a2428e35ef38e6bc7c7e3",
        "fd5efd3dc95c25b393f6c347bd2538d9e44869e73ce03add6a60b696076ae166"),
    2: ("6b874346b5827719178730ca1d4192d96a9a2b4cfd6967873fad6dfe8848ff38",
        "92fc3372845d984e8dca40c93fd81a6ec46b64dcfc222b16ded79e7c6cc93acf",
        "1ab3f93fda37674d4b924e078db7a7c3bcc9aa0a7e531ba08622596356121844",
        "c48155c470dff799417089919a5c79cea31660d77128aedeab82b89c843cce93"),
}


# ------------------------------------------------------------------------------------- independent reference

def _canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _H(tag, o):
    return hashlib.sha256(tag.encode("ascii") + b"\x00" + _canon(o)).hexdigest()


def _ref_run(inp, spec):
    p = spec["params"]
    st = hashlib.sha256(b"moonshot.synthetic.v1\x00" + hashlib.sha256(inp).digest()
                        + hashlib.sha256(_canon(spec)).digest()).digest()
    lines = []
    for i in range(1, p["work_iterations"] + 1):
        st = hashlib.sha256(st).digest()
        if i % p["trace_every"] == 0 or i == p["work_iterations"]:
            lines.append(_canon({"i": i, "s": st.hex()}) + b"\n")
    out, c = b"", 0
    while len(out) < p["checkpoint_bytes"]:
        out += hashlib.sha256(b"moonshot.synthetic.v1.ckpt\x00" + st + c.to_bytes(8, "big")).digest()
        c += 1
    return b"".join(lines), out[:p["checkpoint_bytes"]]


def _kat_genesis():
    return model.make_genesis("KAT", epochs=2, params=dict(KAT_PARAMS), approved_code_sha="0" * 40,
                              initial_checkpoint=KAT_INITIAL)


class TestCanonical(unittest.TestCase):
    def test_sorted_compact_ascii(self):
        self.assertEqual(C.canonical_bytes({"b": 1, "a": [True, None, "\u00e9"]}),
                         b'{"a":[true,null,"\\u00e9"],"b":1}')

    def test_floats_are_refused(self):
        for bad in (1.5, {"x": 0.0}, [float("nan")]):
            with self.assertRaises(C.CanonicalError):
                C.canonical_bytes(bad)

    def test_parse_refuses_non_canonical_bytes(self):
        self.assertEqual(C.parse_canonical(b'{"a":1}'), {"a": 1})
        for bad in (b'{"a": 1}', b'{"b":1,"a":2}', b'{"a":1}\n'):
            with self.assertRaises(C.CanonicalError):
                C.parse_canonical(bad)

    def test_digests(self):
        self.assertEqual(C.sha256_hex(b"abc"), _sha(b"abc"))
        self.assertEqual(C.tagged_digest("t.v1", {"x": 1}), _H("t.v1", {"x": 1}))
        self.assertNotEqual(C.tagged_digest("t.v1", {"x": 1}), C.tagged_digest("t.v2", {"x": 1}))


class TestSyntheticRuntime(unittest.TestCase):
    def test_matches_independent_reference(self):
        g = _kat_genesis()
        spec = model.derive_spec(g.obj, 1)
        self.assertEqual(runtime.run_synthetic_v1(KAT_INITIAL, spec), _ref_run(KAT_INITIAL, spec))

    def test_registry(self):
        self.assertIs(runtime.lookup(runtime.SYNTHETIC_V1), runtime.run_synthetic_v1)
        self.assertIsNone(runtime.lookup({"name": "moonshot.synthetic", "version": 99}))
        self.assertIsNone(runtime.lookup({"name": "something.else", "version": 1}))

    def test_params_are_validated(self):
        g = _kat_genesis()
        for bad in ({"work_iterations": 0, "trace_every": 1, "checkpoint_bytes": 8},
                    {"work_iterations": 10, "trace_every": 0, "checkpoint_bytes": 8},
                    {"work_iterations": 10, "trace_every": 1, "checkpoint_bytes": -1},
                    {"work_iterations": 10, "trace_every": 1, "checkpoint_bytes": 8, "extra": 1}):
            spec = dict(model.derive_spec(g.obj, 1), params=bad)
            with self.assertRaises(ValueError):
                runtime.run_synthetic_v1(KAT_INITIAL, spec)


class TestSemanticIdentity(unittest.TestCase):
    def test_known_answer_vectors(self):
        g = _kat_genesis()
        inp = KAT_INITIAL
        for k in (1, 2):
            r = model.execute(g.obj, k, inp)
            self.assertEqual((r.work_id, r.epoch_digest, _sha(r.trace), _sha(r.checkpoint)), KAT[k], k)
            inp = r.checkpoint

    def test_formulas_match_contract(self):
        g = _kat_genesis()
        r = model.execute(g.obj, 1, KAT_INITIAL)
        self.assertEqual(r.spec_bytes, _canon(r.spec))
        self.assertEqual(r.work_id, _H("moonshot.epoch.work.v1", {
            "input_checkpoint_sha256": _sha(KAT_INITIAL), "spec_sha256": _sha(r.spec_bytes),
            "runtime": runtime.SYNTHETIC_V1}))
        self.assertEqual(r.epoch_digest, _H("moonshot.epoch.result.v1", {
            "work_id": r.work_id, "trace_sha256": _sha(r.trace), "output_checkpoint_sha256": _sha(r.checkpoint)}))
        self.assertEqual(model.work_id(_sha(KAT_INITIAL), _sha(r.spec_bytes), runtime.SYNTHETIC_V1), r.work_id)
        self.assertEqual(model.epoch_digest(r.work_id, _sha(r.trace), _sha(r.checkpoint)), r.epoch_digest)

    def test_manifest_has_no_attempt_metadata(self):
        r = model.execute(_kat_genesis().obj, 1, KAT_INITIAL)
        self.assertEqual(set(r.manifest), set(model.MANIFEST_KEYS))
        self.assertEqual(r.manifest_bytes, C.canonical_bytes(r.manifest))
        for key in ("host", "worker", "attempt", "time", "clock", "retry", "commit", "git"):
            self.assertFalse([k for k in r.manifest if key in k], key)

    def test_verify_epoch_detects_each_tampered_blob(self):
        r = model.execute(_kat_genesis().obj, 1, KAT_INITIAL)
        files = {"manifest": r.manifest_bytes, "spec": r.spec_bytes, "trace": r.trace, "checkpoint": r.checkpoint}
        self.assertEqual(model.verify_epoch(files, _sha(KAT_INITIAL)), [])
        for name in files:
            bad = dict(files, **{name: files[name] + b"x"})
            self.assertTrue(model.verify_epoch(bad, _sha(KAT_INITIAL)), name)
        self.assertTrue(model.verify_epoch(files, _sha(b"some other input")))

    def test_spec_binds_chain_and_index(self):
        g = _kat_genesis()
        self.assertNotEqual(model.execute(g.obj, 1, KAT_INITIAL).work_id,
                            model.execute(g.obj, 2, KAT_INITIAL).work_id)
        g2 = model.make_genesis("KAT2", epochs=2, params=dict(KAT_PARAMS), approved_code_sha="0" * 40,
                                initial_checkpoint=KAT_INITIAL)
        self.assertNotEqual(model.execute(g.obj, 1, KAT_INITIAL).work_id,
                            model.execute(g2.obj, 1, KAT_INITIAL).work_id)

    def test_code_sha_is_not_identity(self):
        a = model.make_genesis("KAT", epochs=2, params=dict(KAT_PARAMS), approved_code_sha="a" * 40,
                               initial_checkpoint=KAT_INITIAL)
        b = model.make_genesis("KAT", epochs=2, params=dict(KAT_PARAMS), approved_code_sha="b" * 40,
                               initial_checkpoint=KAT_INITIAL)
        self.assertEqual(model.execute(a.obj, 1, KAT_INITIAL).epoch_digest,
                         model.execute(b.obj, 1, KAT_INITIAL).epoch_digest)

    def test_replay_chain(self):
        rs = model.replay_chain(_kat_genesis(), 2)
        self.assertEqual([(r.work_id, r.epoch_digest) for r in rs], [KAT[1][:2], KAT[2][:2]])


class TestTransportIndependence(unittest.TestCase):
    """OP-LC1 change 1: git SHAs locate bytes; the same epochs on two layouts have different commits and
    identical semantic identity and canonical bytes."""

    def test_same_digests_different_commits_across_layouts(self):
        seen = {}
        for layout in S.LAYOUTS:
            h = Harness(layout)
            self.addCleanup(h.cleanup)
            h.chain("T", epochs=2)
            h.worker("w").run_chain("T")
            lin = h.coordinator.lineage("T")
            seen[layout] = [(e.epoch_digest, e.commit, h.coordinator.epoch_bytes(e.commit)) for e in lin]
        a, b = seen[S.PER_CHAIN], seen[S.SINGLE_REF]
        self.assertEqual([x[0] for x in a], [x[0] for x in b])
        self.assertEqual([x[2] for x in a], [x[2] for x in b])
        self.assertNotEqual([x[1] for x in a], [x[1] for x in b])

    def test_denylisted_remotes_are_refused(self):
        for url in ("https://github.com/jcraig949jfi/Prometheus.git", "git@github.com:jcraig949jfi/Prometheus.git",
                    "D:\\Prometheus", "/home/jcraig/Prometheus/"):
            with self.assertRaises(S.ForbiddenRemote, msg=url):
                S.Store(url, namespace="t", layout=S.PER_CHAIN, local_dir="unused")


if __name__ == "__main__":
    unittest.main()
