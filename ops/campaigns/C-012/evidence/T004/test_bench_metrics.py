"""Tests of the frozen T004 analysis code on hand-built rows (no database).
    python -m unittest ops/campaigns/C-012/evidence/T004/test_bench_metrics.py   (from the repo root)"""
import importlib.util
import unittest
from pathlib import Path

_s = importlib.util.spec_from_file_location("bench_metrics", Path(__file__).with_name("bench_metrics.py"))
BM = importlib.util.module_from_spec(_s)
_s.loader.exec_module(BM)


def row(i, inst, created, started, execute=1.0, transfer=0.1, finish=0.05, publish=0.2, status="succeeded",
        outcome="PUBLISHED", task=None, nbytes=1000):
    first = started + execute
    last = first + transfer
    ended = last + finish
    return {"task_id": task or "t%d" % i, "attempt_id": "a%d" % i, "instance": inst, "host": "h",
            "status": status, "created": created, "started": started, "ended": ended, "first_artifact": first,
            "last_artifact": last, "artifact_bytes": nbytes, "params_bytes": 100,
            "classified": ended + publish if outcome else None, "outcome": outcome}


class TestStats(unittest.TestCase):
    def test_median_and_nearest_rank_p95(self):
        self.assertEqual(BM.median([3, 1, 2]), 2)
        self.assertEqual(BM.median([4, 1, 2, 3]), 2.5)
        self.assertEqual(BM.p95(list(range(1, 101))), 95)
        self.assertEqual(BM.p95([7]), 7)
        self.assertIsNone(BM.median([]))


class TestPoint(unittest.TestCase):
    def two_workers(self):
        rows = []
        for w in ("w1", "w2"):
            t = 0.0
            for k in range(5):
                rows.append(row(len(rows), w, created=t - 0.5, started=t))
                t = rows[-1]["ended"] + 0.2                      # a 0.2 s claim gap between attempts
        return rows

    def test_stage_decomposition_and_gaps(self):
        rows = self.two_workers()
        s = BM.stages(rows[0])
        self.assertAlmostEqual(s["execute"], 1.0)
        self.assertAlmostEqual(s["transfer"], 0.1)
        self.assertAlmostEqual(s["finish"], 0.05)
        self.assertAlmostEqual(s["queue"], 0.5)
        self.assertAlmostEqual(s["publish"], 0.2)
        g = BM.gaps(rows)
        self.assertEqual(len(g), 8)                              # 4 gaps per worker
        self.assertTrue(all(abs(x - 0.2) < 1e-9 for x in g))

    def test_metrics_follow_their_definitions(self):
        rows = self.two_workers()
        m = BM.point_metrics(rows, wall_s=10.0, published=10, db_bytes=50000)
        coord = 8 * 0.2 + 10 * (0.1 + 0.05)
        self.assertAlmostEqual(m["M1_coordination_wall_fraction"], coord / (coord + 10 * 1.0))
        self.assertEqual(m["M2_retries_per_published"], 0)
        self.assertAlmostEqual(m["M3_p95_gap_over_median_execute"], 0.2 / 1.0)
        self.assertEqual(m["M4_abandonment_rate"], 0)
        self.assertAlmostEqual(m["M5_bytes_moved_per_published"], 1100)
        self.assertAlmostEqual(m["M6_db_bytes_per_published"], 5000)
        self.assertAlmostEqual(m["throughput_per_s"], 1.0)

    def test_retries_and_abandonment_count_what_the_prereg_says(self):
        rows = self.two_workers()
        rows.append(row(99, "w3", created=0, started=1, status="abandoned", outcome=None, task="t0"))   # a retry of t0
        rows.append(row(98, "w3", created=0, started=9, outcome="STALE"))
        rows.append(row(97, "w3", created=0, started=12, outcome="DUPLICATE"))
        m = BM.point_metrics(rows, wall_s=10.0, published=10, db_bytes=0)
        # fabric retries: 13 executed attempts over 12 tasks = 1; contention: STALE + DUPLICATE = 2
        self.assertAlmostEqual(m["M2_retries_per_published"], 0.3)
        self.assertAlmostEqual(m["M4_abandonment_rate"], 2 / 13)   # the abandoned attempt + the STALE one

    def test_verdict_and_envelope(self):
        ok = {"M1_coordination_wall_fraction": 0.01, "M2_retries_per_published": 0.0,
              "M3_p95_gap_over_median_execute": 0.05, "M4_abandonment_rate": 0.0, "db_errors": 0}
        self.assertEqual(BM.verdict(ok), ("ADEQUATE", []))
        bad = dict(ok, M1_coordination_wall_fraction=0.2, db_errors=1)
        self.assertEqual(BM.verdict(bad), ("RECONSIDER", ["B1", "B5"]))
        self.assertEqual(BM.verdict(dict(ok, M3_p95_gap_over_median_execute=None)), ("RECONSIDER", ["B3"]))
        self.assertEqual(BM.envelope({60: "ADEQUATE", 30: "ADEQUATE", 10: "ADEQUATE", 3: "RECONSIDER",
                                      1: "RECONSIDER"}), 10)
        self.assertEqual(BM.envelope({60: "ADEQUATE", 30: "RECONSIDER", 10: "ADEQUATE"}), 60)
        self.assertIsNone(BM.envelope({60: "RECONSIDER", 30: "ADEQUATE"}))


if __name__ == "__main__":
    unittest.main()
