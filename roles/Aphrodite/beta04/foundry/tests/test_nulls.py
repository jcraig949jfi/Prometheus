"""Baseline sanity: R0 families solved by a trivial rung; planted lookup-only family solved by lookup; planted
reactive family solved by the reactive null; planted regression positives solved by the REGRESSION rung; planted
structureless family and multiplicative fold solved by nothing."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import generator as G                 # noqa: E402
import nulls as N                     # noqa: E402
import qualify2 as Q                  # noqa: E402
import regress                        # noqa: E402
import tenum                          # noqa: E402
from _small import SMALL, TEST_SEED   # noqa: E402


class Linear(unittest.TestCase):
    def test_solve_linear(self):
        rows = [((1, 1), 5), ((2, 1), 7), ((5, 1), 13)]
        self.assertEqual([int(c) for c in N.solve_linear(rows)], [2, 3])
        self.assertIsNone(N.solve_linear([((1, 1), 5), ((2, 1), 7), ((3, 1), 10)]))
        self.assertIsNotNone(N.solve_linear([((1, 2, 1), 9), ((0, 1, 1), 4), ((3, 0, 1), 7)]))


class Ladder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = G.build_world(TEST_SEED, SMALL)
        cls.g = tenum.Grammar(memo_max=7)

    def test_r0_trivial(self):
        n = 0
        for f in self.world["families"]:
            if f["rung"] != "R0" or f["gen_class"] != "OK":
                continue
            res = N.run_closed_form(f["dev"], f["test"])
            small = N.run_small_search(self.g, f["output_type"], f["dev"], f["test"], 100_000)
            reg = regress.run(f["dev"], f["test"], G.CONFIG)
            solved = [k for k, v in res.items() if v["solved"]] + (["small"] if small["solved"] else []) + \
                (["regression"] if reg["solved"] else [])
            self.assertTrue(solved, f["witness"])
            n += 1
        self.assertGreater(n, 0)

    def test_planted(self):
        fams = {f["family_id"]: f for f in Q.planted_families()}
        lk = fams["PLANTED-LOOKUP"]
        res = N.run_closed_form(lk["dev"], lk["test"])
        self.assertTrue(res["lookup"]["solved"])
        self.assertFalse(res["constant"]["solved"])
        rnd = fams["PLANTED-RANDOM"]
        res = N.run_closed_form(rnd["dev"], rnd["test"])
        self.assertFalse(any(v["solved"] for v in res.values()))
        self.assertFalse(regress.run(rnd["dev"], rnd["test"], G.CONFIG)["solved"])
        self.assertFalse(N.run_small_search(self.g, "I", rnd["dev"], rnd["test"], 20_000)["solved"])
        rc = fams["PLANTED-REACTIVE"]
        res = N.run_closed_form(rc["dev"], rc["test"])
        self.assertTrue(res["reactive"]["solved"])
        self.assertFalse(res["constant"]["solved"])
        for fid, expect in (("PLANTED-REGRESSION-W", True), ("PLANTED-REGRESSION-E", True),
                            ("PLANTED-NONLINEAR-FOLD", False)):
            f = fams[fid]
            self.assertEqual(regress.run(f["dev"], f["test"], G.CONFIG)["solved"], expect, fid)

    def test_known_answers(self):
        dev = [[[1, 2, 3], [3, 5, 7]], [[-4, 0], [-7, 1]], [[9], [19]]] + [[[i, i + 1], [2 * i + 1, 2 * i + 3]]
                                                                           for i in range(5)]
        test = [[[10, -3, 8], [21, -5, 17]], [[40], [81]]] * 16
        self.assertTrue(N.run_closed_form(dev, test)["reactive"]["solved"])
        dev = [[[1, 2, 3], 6], [[4, 5], 20], [[2, 2, 2], 8], [[3], 3], [[1, 1], 1], [[2, 3], 6], [[5, 1, 1], 5],
               [[7, 2], 14]]
        test = [[[2, 5, 3], 30], [[6, 6], 36]] * 16
        res = N.run_closed_form(dev, test)
        self.assertFalse(res["reactive"]["solved"])
        self.assertTrue(res["library"]["solved"])


if __name__ == "__main__":
    unittest.main()
