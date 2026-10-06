"""The D4 instrument against known answers (design S17 layer 2: an instrument passes its controls before it
judges data). Short in-process runs on temporary local remotes; none of this is D4 data."""
import os
import threading
import unittest

from moonshot.epoch import bench
from moonshot.epoch import store as S
from moonshot.epoch import worker as W
from moonshot.epoch.tests.harness import APPROVED_SHA, Harness


class TestBenchInstrument(unittest.TestCase):
    def _run(self, layout, workers, duration_s):
        h = Harness(layout)
        self.addCleanup(h.cleanup)
        chains = bench.make_chains(h.coordinator, "B", 3, iterations=2000, checkpoint_bytes=256, epochs=100000,
                                   approved_code_sha=APPROVED_SHA)
        out = []

        def one(i):
            st = h.store("bw%d" % i)
            out.append(bench.bench_worker(st, "bw%d" % i, chains, code_sha=APPROVED_SHA, approved={APPROVED_SHA},
                                          spool_dir=os.path.join(h.dir, "spool-bw%d" % i), leases=True,
                                          duration_s=duration_s, start=i))

        ts = [threading.Thread(target=one, args=(i,)) for i in range(workers)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        bench.validate_all(h.validator(), "B", replay_every=3)
        return h, out, bench.report(h.coordinator, "B", wall_s=duration_s, repo_bytes=1000)

    def test_single_worker_known_answers(self):
        h, sums, rep = self._run(S.PER_CHAIN, 1, 3)
        self.assertGreater(rep["published"], 0)
        self.assertEqual((rep["published"], rep["validated"], rep["attempts"], rep["executed"]),
                         (rep["published"],) * 4)
        self.assertEqual((rep["retries_counted"], rep["disagreements"], rep["pending_at_end"]), (0, 0, 0))
        self.assertEqual(rep["outcomes"], {"PUBLISHED": rep["published"]})
        self.assertEqual(rep["workers"], 1)
        self.assertTrue(rep["checks"]["B2"] and rep["checks"]["B4"] and rep["checks"]["B5"])
        self.assertAlmostEqual(rep["metrics"]["M6_repo_bytes_per_published"], 1000 / rep["published"])

    def test_single_ref_contention_is_counted_and_summed(self):
        # Deterministic collision (fixed after ubu002 showed two free-running threads need not collide in 4 s):
        # alpha pauses after staging C000 while bravo publishes C001 on the same index, as D3 case 4 does.
        h = Harness(S.SINGLE_REF)
        self.addCleanup(h.cleanup)
        bench.make_chains(h.coordinator, "C", 2, iterations=500, checkpoint_bytes=64, epochs=5,
                          approved_code_sha=APPROVED_SHA)
        b = h.worker("bravo")

        def bravo_publishes(worker, ctx):
            b.run_attempt("C001")

        a = h.worker("alpha", faults=W.FaultPlan({"after_stage": bravo_publishes}))
        ra = a.run_attempt("C000")
        self.assertGreaterEqual(ra.receipt["contention_retries"], 1)
        sums = []
        for w in (a, b):
            w.flush_receipts()
            sums.append(bench.summarize(w, t_start=0, attempts=1))
            w.store.append_receipts(w.worker_id, {sums[-1]["attempt_id"]: sums[-1]})
        bench.validate_all(h.validator(), "C")
        rep = bench.report(h.coordinator, "C", wall_s=10, repo_bytes=1000)
        records = h.coordinator.read_receipts()
        expect = sum(max(0, r.get("push_attempts_cas", 0) - 1) for r in records if r.get("kind") != "WORKER_SUMMARY") \
            + sum(s["contention_retries_total"] for s in sums)
        self.assertEqual(rep["retries_counted"], expect)
        self.assertGreaterEqual(rep["retries_counted"], 1)
        self.assertEqual((rep["published"], rep["validated"]), (2, 2))

    def test_abandonment_and_coordination_arithmetic(self):
        h = Harness(S.PER_CHAIN)
        self.addCleanup(h.cleanup)
        bench.make_chains(h.coordinator, "A", 1, iterations=10, checkpoint_bytes=8, epochs=10,
                          approved_code_sha=APPROVED_SHA)
        w = h.store("crafted")
        base = {"timings": {"execute_s": 3.0, "claim_s": 0.1}, "push_attempts_cas": 1, "contention_retries": 0}
        w.append_receipts("crafted", {
            "r1": dict(base, attempt_id="r1", outcome="PUBLISHED"),
            "r2": dict(base, attempt_id="r2", outcome="ABANDONED_RECOVERED"),
            "r3": dict(base, attempt_id="r3", outcome="DUPLICATE", push_attempts_cas=3),
            "s1": {"kind": "WORKER_SUMMARY", "attempt_id": "s1", "pending_attempts": 1,
                   "coordination_wall_total_s": 1.0, "contention_retries_total": 2,
                   "bytes_pushed_total": 10, "bytes_fetched_total": 5, "flags": []},
        })
        rep = bench.report(h.coordinator, "A", wall_s=60)
        m = rep["metrics"]
        self.assertAlmostEqual(m["M1_coordination_fraction"], 1.0 / (1.0 + 9.0))
        self.assertAlmostEqual(m["M4_abandonment_rate"], (1 + 1) / (3 + 1))  # ABANDONED + pending over started + pending
        self.assertEqual(rep["retries_counted"], 2 + 2)                       # (3 - 1) CAS resends + 2 contention
        self.assertIsNone(m["M2_retries_per_published"])                      # nothing is on the lineage
        self.assertEqual(rep["verdict"], "RECONSIDER")


if __name__ == "__main__":
    unittest.main()
