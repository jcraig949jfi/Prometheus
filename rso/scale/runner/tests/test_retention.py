"""Checkpoint retention policy (C-013-T024; architecture s3.6/s3.8): keep every Kth + last M + contest-referenced."""
import json
import os
import unittest

from rso.scale.runner import account as A
from rso.scale.runner import control as CTL
from rso.scale.runner import engine as E
from rso.scale.runner import lease as L
from rso.scale.runner import resume as RS
from rso.scale.runner import retention as RET
from rso.scale.runner import run as RUN
from rso.scale.runner import store as S
from rso.scale.runner import worker as W
from rso.scale.runner.tests._util import TempRun

POLICY = {"keep_every": 4, "keep_last": 2}


def out_sha(rd, c, k):
    return RUN.publications(rd, c)[k]["output_checkpoint_sha256"]


def present(rd, c, k):
    return os.path.exists(RUN.object_store(rd).path(out_sha(rd, c, k)))


class TestPolicyDeclared(unittest.TestCase):
    def test_policy_in_manifest(self):
        t = TempRun(epochs=3, retention=POLICY)
        try:
            self.assertEqual(t.manifest["checkpoint_retention"], POLICY)
            self.assertEqual(RUN.load_manifest(t.run_dir)[0]["checkpoint_retention"], POLICY)
        finally:
            t.cleanup()

    def test_no_policy_means_keep_everything(self):
        t = TempRun(epochs=6)
        try:
            self.assertIsNone(t.manifest["checkpoint_retention"])
            for c in RUN.chain_ids(t.manifest):
                W.work(t.run_dir, c)
            self.assertEqual(RET.prune(t.run_dir)["pruned"], [])
        finally:
            t.cleanup()

    def test_bad_policy_refused(self):
        for bad in ({"keep_every": 0, "keep_last": 2}, {"keep_every": 4, "keep_last": 1}, {"keep_every": 4}):
            with self.assertRaises(ValueError, msg=bad):
                TempRun(epochs=2, retention=bad).cleanup()


class TestPrune(unittest.TestCase):
    def setUp(self):
        self.t = TempRun(epochs=12, retention=POLICY, replay_every=1)
        self.rd = self.t.run_dir
        self.chains = RUN.chain_ids(self.t.manifest)
        self.m = self.t.manifest

    def tearDown(self):
        self.t.cleanup()

    def run_all(self, **kw):
        for c in self.chains:
            W.work(self.rd, c, **kw)

    def test_keeps_genesis_every_kth_last_m_and_head(self):
        self.run_all()
        for c in self.chains:
            self.assertEqual(RET.keep_epochs(self.rd, c), {0, 4, 8, 11, 12})
            for k in range(1, 13):
                self.assertEqual(present(self.rd, c, k), k in {4, 8, 11, 12}, (c, k))
            self.assertTrue(os.path.exists(RUN.object_store(self.rd).path(
                RUN.genesis(self.rd, c).obj["initial_checkpoint_sha256"])))

    def test_worker_prunes_as_it_goes_storage_is_bounded(self):
        c = self.chains[0]
        W.work(self.rd, c, max_epochs=9)
        # at head 9: genesis, 4, 8 (every 4th), 8, 9 (last 2) -> epochs 1-3, 5-7 are gone already
        for k in (1, 2, 3, 5, 6, 7):
            self.assertFalse(present(self.rd, c, k), k)
        for k in (4, 8, 9):
            self.assertTrue(present(self.rd, c, k), k)

    def test_contest_referenced_epochs_are_kept(self):
        c = self.chains[0]
        W.work(self.rd, c, max_epochs=3)                           # head 3: the contest is on a kept epoch
        S.append_jsonl(os.path.join(RUN.pdir(self.rd, c), "contests.jsonl"),
                       {"kind": "DISAGREEMENT", "epoch_index": 3, "work_id": "x"})
        W.work(self.rd, c)
        self.assertEqual(RET.keep_epochs(self.rd, c), {0, 2, 3, 4, 8, 11, 12})
        for k in (2, 3):
            self.assertTrue(present(self.rd, c, k), k)
        self.assertFalse(present(self.rd, c, 5))

    def test_object_shared_with_a_kept_epoch_is_not_deleted(self):
        c0, c1 = self.chains
        W.work(self.rd, c0, max_epochs=3)                           # head 3: nothing prunable yet beyond epoch 1
        W.work(self.rd, c1, max_epochs=5)
        # make c0's epoch-1 checkpoint (prunable) the same object c1 keeps at its epoch 4
        pubs = os.path.join(RUN.pdir(self.rd, c0), "publications.jsonl")
        rows, _ = S.read_jsonl(pubs)
        shared = out_sha(self.rd, c1, 4)
        for r in rows:
            if r["epoch_index"] == 1:
                r["output_checkpoint_sha256"] = shared
        with open(pubs, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(r, sort_keys=True) + "\n" for r in rows)
        RET.prune(self.rd)
        self.assertTrue(os.path.exists(RUN.object_store(self.rd).path(shared)))

    def test_dry_run_deletes_nothing_and_idempotent(self):
        u = TempRun(epochs=12)                                      # no policy declared: the worker prunes nothing
        try:
            for c in RUN.chain_ids(u.manifest):
                W.work(u.run_dir, c)
            before = RUN.object_store(u.run_dir).total_bytes()
            r = RET.prune(u.run_dir, policy=POLICY, dry_run=True)   # an explicit policy overrides the manifest's
            self.assertEqual(len(r["pruned"]), 2 * 8)
            self.assertEqual(RUN.object_store(u.run_dir).total_bytes(), before)
            self.assertEqual(len(RET.prune(u.run_dir, policy=POLICY)["pruned"]), 2 * 8)
            self.assertLess(RUN.object_store(u.run_dir).total_bytes(), before)
            self.assertEqual(RET.prune(u.run_dir, policy=POLICY)["pruned"], [])
        finally:
            u.cleanup()

    def test_prune_is_recorded(self):
        c = self.chains[0]
        W.work(self.rd, c, max_epochs=9)
        rows, _ = S.read_jsonl(os.path.join(RUN.pdir(self.rd, c), "retention.jsonl"))
        self.assertTrue(rows)
        self.assertEqual(rows[0]["policy"], POLICY)
        self.assertEqual(sorted(p["epoch_index"] for r in rows for p in r["pruned"]), [1, 2, 3, 5, 6, 7])
        self.assertTrue(all(p["bytes"] > 0 for r in rows for p in r["pruned"]))


class TestFireAfterPruning(unittest.TestCase):
    """The packet's evidence: prune, then resume and s3.8 replay still VALID, digest == control."""

    def setUp(self):
        self.t = TempRun(epochs=12, retention=POLICY, replay_every=1)
        self.rd = self.t.run_dir
        self.chains = RUN.chain_ids(self.t.manifest)
        self.engine = E.get_engine(self.t.manifest["engine"]["runtime"])

    def tearDown(self):
        self.t.cleanup()

    def test_resume_and_replay_valid_after_prune_digest_equals_control(self):
        c0, c1 = self.chains
        with self.assertRaises(W.SimulatedCrash):
            W.work(self.rd, c0, crash_after_ticks=40 * 9 + 15)      # dies in epoch 10, head 9, 1-3 and 5-7 pruned
        self.assertEqual(RUN.head(self.rd, c0)["head_index"], 9)
        self.assertFalse(present(self.rd, c0, 6))
        L.force_expire(self.rd, c0)
        v = RS.verify_resume(self.rd, c0, self.engine, force_replay=True, record=False)
        self.assertEqual(v["verdict"], "VALID", v)
        self.assertTrue(v["replayed"])
        r = W.work(self.rd, c0)
        self.assertEqual(r["status"], "COMPLETE")
        self.assertEqual(r["resume"]["verdict"], "VALID")
        W.work(self.rd, c1)
        v = RS.verify_resume(self.rd, c0, self.engine, force_replay=True, record=False)
        self.assertEqual((v["verdict"], v["head_index"]), ("VALID", 12))
        acct = A.final_account(self.rd)
        self.assertEqual(acct["run_digest"], CTL.control(self.rd)["run_digest"])

    def test_pruned_run_stores_fewer_bytes_than_unpruned(self):
        u = TempRun(epochs=12, replay_every=1)
        try:
            for r in (self.t, u):
                for c in RUN.chain_ids(r.manifest):
                    W.work(r.run_dir, c)
            self.assertLess(RUN.object_store(self.rd).total_bytes(), RUN.object_store(u.run_dir).total_bytes())
        finally:
            u.cleanup()


if __name__ == "__main__":
    unittest.main()
