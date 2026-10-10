"""Run manifest, Moonshot-aligned epochs, generation-CAS publication, verified resume, accounting (C-013-T022)."""
import hashlib
import json
import unittest

from moonshot.epoch import canonical as C
from moonshot.epoch import model as M
from rso.scale.runner import account as A
from rso.scale.runner import control as CTL
from rso.scale.runner import engine as E
from rso.scale.runner import lease as L
from rso.scale.runner import resume as RS
from rso.scale.runner import run as RUN
from rso.scale.runner import worker as W
from rso.scale.runner.tests._util import AETHER, TempRun, aether_params


class Base(unittest.TestCase):
    kw = {}

    def setUp(self):
        self.t = TempRun(**self.kw)
        self.rd = self.t.run_dir
        self.m, self.mid = RUN.load_manifest(self.rd)
        self.chains = RUN.chain_ids(self.m)

    def tearDown(self):
        self.t.cleanup()


class TestManifest(Base):
    def test_manifest_identity(self):
        self.assertEqual(len(self.mid), 64)
        self.assertEqual(self.m["schema"], "rso.runner.run_manifest.v1")
        self.assertEqual(self.chains, ["t-p0", "t-p1"])
        for k in ("engine", "environment", "partitions", "epochs", "caps", "replay_every", "canonical_digest"):
            self.assertIn(k, self.m)

    def test_create_refuses_existing(self):
        with self.assertRaises(FileExistsError):
            RUN.create_run(self.rd, name="t", runtime=self.m["engine"]["runtime"], params={}, partitions=[],
                           epochs=1)

    def test_genesis_is_moonshot_genesis(self):
        g = RUN.genesis(self.rd, self.chains[0])
        self.assertEqual(g.obj["schema"], M.GENESIS_SCHEMA)
        self.assertEqual(g.obj["params"]["seed"], 100)
        h = RUN.head(self.rd, self.chains[0])
        self.assertEqual((h["head_index"], h["generation"], h["state"]), (0, 0, "OPEN"))
        self.assertEqual(h["head_checkpoint_sha256"], g.obj["initial_checkpoint_sha256"])


class TestWorkerAndControl(Base):
    def test_run_to_completion_equals_control(self):
        for c in self.chains:
            r = W.work(self.rd, c)
            self.assertEqual(r["status"], "COMPLETE")
        acct = A.final_account(self.rd)
        self.assertEqual(acct["state"], "COMPLETE")
        self.assertEqual(acct["run_digest"], CTL.control(self.rd)["run_digest"])
        self.assertEqual(acct["outcomes"]["PUBLISHED"], 8)
        self.assertEqual(acct["wasted"]["interrupted_attempts"], 0)

    def test_epochs_verify_under_moonshot(self):
        c = self.chains[0]
        W.work(self.rd, c)
        prev = RUN.genesis(self.rd, c).obj["initial_checkpoint_sha256"]
        for k in range(1, 5):
            files = RUN.epoch_files(self.rd, c, k)
            self.assertEqual(M.verify_epoch(files, prev), [])
            prev = json.loads(files["manifest"])["output_checkpoint_sha256"]
        # the same chain computed by Moonshot's own replay_chain with the same runtime has the same identity
        g = RUN.genesis(self.rd, c)
        ref = M.replay_chain(g, 4, runner=W.moonshot_runtime(E.get_engine(self.m["engine"]["runtime"])))
        self.assertEqual(ref[-1].epoch_digest, RUN.head(self.rd, c)["head_epoch_digest"])

    def test_crash_mid_epoch_then_resume(self):
        c = self.chains[1]
        with self.assertRaises(W.SimulatedCrash):
            W.work(self.rd, c, crash_after_ticks=40 * 2 + 15)       # dies 15 ticks into epoch 3
        self.assertEqual(RUN.head(self.rd, c)["head_index"], 2)
        L.force_expire(self.rd, c)                                  # a killed holder's lease, as the TTL would
        r = W.work(self.rd, c)
        self.assertEqual(r["status"], "COMPLETE")
        self.assertEqual(r["resume"]["verdict"], "VALID")
        self.assertTrue(r["resume"]["replayed"])                    # the first resumption is always replayed
        W.work(self.rd, self.chains[0])
        acct = A.final_account(self.rd)
        self.assertEqual(acct["run_digest"], CTL.control(self.rd)["run_digest"])
        self.assertEqual(acct["wasted"]["interrupted_attempts"], 1)
        self.assertGreaterEqual(acct["wasted"]["ticks_lower_bound"], 10)
        self.assertEqual(acct["outcomes"]["PUBLISHED"], 8)


class TestPublishCAS(Base):
    def _epoch(self, c, k, inp):
        g = RUN.genesis(self.rd, c)
        return M.execute(g.obj, k, inp, runner=W.moonshot_runtime(E.get_engine(self.m["engine"]["runtime"])))

    def test_outcomes(self):
        c = self.chains[0]
        tok = L.acquire(self.rd, c)
        g = RUN.genesis(self.rd, c)
        e1 = self._epoch(c, 1, g.initial_checkpoint)
        pub = RUN.publish
        self.assertEqual(pub(self.rd, c, e1, expected_generation=0, lease_token=tok, attempt_id="a1"), "PUBLISHED")
        self.assertEqual(pub(self.rd, c, e1, expected_generation=0, lease_token=tok, attempt_id="a2"), "DUPLICATE")
        e2 = self._epoch(c, 2, e1.checkpoint)
        # generation moved: a zombie's view
        self.assertEqual(pub(self.rd, c, e2, expected_generation=0, lease_token=tok, attempt_id="a3"), "STALE")
        # fenced: not the lease holder
        self.assertEqual(pub(self.rd, c, e2, expected_generation=1, lease_token="not-the-lease", attempt_id="a4"),
                         "STALE")
        self.assertEqual(pub(self.rd, c, e2, expected_generation=1, lease_token=tok, attempt_id="a5"), "PUBLISHED")
        # a self-consistent but different result for an already-published work identity halts the chain
        trace = e1.trace + b"x\n"
        t_sha = hashlib.sha256(trace).hexdigest()
        dig = M.epoch_digest(e1.work_id, t_sha, e1.manifest["output_checkpoint_sha256"])
        man = dict(e1.manifest, trace_sha256=t_sha, trace_bytes=len(trace), epoch_digest=dig)
        forged = M.EpochResult(e1.chain_id, 1, e1.spec, e1.spec_bytes, trace, e1.checkpoint, man,
                               C.canonical_bytes(man), e1.work_id, dig)
        self.assertEqual(pub(self.rd, c, forged, expected_generation=2, lease_token=tok, attempt_id="a6"),
                         "DISAGREEMENT")
        self.assertEqual(RUN.head(self.rd, c)["state"], "HALTED")
        self.assertEqual(pub(self.rd, c, e2, expected_generation=2, lease_token=tok, attempt_id="a7"), "HALTED")

    def test_invalid_bytes_refused(self):
        c = self.chains[0]
        tok = L.acquire(self.rd, c)
        g = RUN.genesis(self.rd, c)
        e1 = self._epoch(c, 1, g.initial_checkpoint)
        broken = M.EpochResult(e1.chain_id, 1, e1.spec, e1.spec_bytes, e1.trace, e1.checkpoint + b"!",
                               e1.manifest, e1.manifest_bytes, e1.work_id, e1.epoch_digest)
        self.assertEqual(RUN.publish(self.rd, c, broken, expected_generation=0, lease_token=tok, attempt_id="b1"),
                         "INVALID")
        self.assertEqual(RUN.head(self.rd, c)["head_index"], 0)


class TestVerifiedResume(Base):
    def setUp(self):
        super().setUp()
        self.c = self.chains[0]
        W.work(self.rd, self.c, max_epochs=2)
        self.eng = E.get_engine(self.m["engine"]["runtime"])

    def test_valid(self):
        v = RS.verify_resume(self.rd, self.c, self.eng, force_replay=True)
        self.assertEqual(v["verdict"], "VALID", v)
        self.assertTrue(all(v["checks"].values()), v)

    def test_corrupt_checkpoint_invalid(self):
        sha = RUN.head(self.rd, self.c)["head_checkpoint_sha256"]
        with open(RUN.object_store(self.rd).path(sha), "r+b") as f:
            f.write(b"\x00\x00\x00\x00")
        v = RS.verify_resume(self.rd, self.c, self.eng)
        self.assertEqual(v["verdict"], "INVALID")
        self.assertFalse(v["checks"]["bytes"])

    def test_environment_mismatch_invalid(self):
        class Other(type(self.eng)):
            def probe(self):
                p = dict(super().probe())
                p["engine_files"] = {"x.py": "0" * 64}
                return p
        v = RS.verify_resume(self.rd, self.c, Other())
        self.assertEqual(v["verdict"], "INVALID")
        self.assertFalse(v["checks"]["environment"])

    def test_replay_mismatch_contested_and_halts(self):
        class Drifted(type(self.eng)):
            def step(self, state, n):
                return super().step(super().step(state, n), 1)     # one tick too many: a nondeterministic host
        v = RS.verify_resume(self.rd, self.c, Drifted(), force_replay=True)
        self.assertEqual(v["verdict"], "CONTESTED")
        self.assertEqual(RUN.head(self.rd, self.c)["state"], "HALTED")


class TestLease(Base):
    def test_exclusive_and_dead_holder(self):
        c = self.chains[0]
        tok = L.acquire(self.rd, c)
        self.assertIsNotNone(tok)
        self.assertIsNone(L.acquire(self.rd, c))                    # held by a live process (this one)
        L.release(self.rd, c, tok)
        self.assertIsNotNone(L.acquire(self.rd, c))
        L.force_dead_holder(self.rd, c)                             # the holder pid no longer exists
        self.assertIsNotNone(L.acquire(self.rd, c))


class TestAetherRun(Base):
    kw = {"runtime": AETHER, "params": aether_params(), "partitions": 1, "epochs": 3}

    def test_aether_chain_equals_control(self):
        c = self.chains[0]
        with self.assertRaises(W.SimulatedCrash):
            W.work(self.rd, c, crash_after_ticks=25)
        L.force_expire(self.rd, c)
        self.assertEqual(W.work(self.rd, c)["status"], "COMPLETE")
        acct = A.final_account(self.rd)
        ctl = CTL.control(self.rd)
        self.assertEqual(acct["run_digest"], ctl["run_digest"])
        self.assertEqual(acct["chains"][c]["final_state_digest"], ctl["chains"][c]["final_state_digest"])


if __name__ == "__main__":
    unittest.main()
