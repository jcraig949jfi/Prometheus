"""Generator determinism and structural invariants (v2)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import interp_a as A                  # noqa: E402
import generator as G                 # noqa: E402
from _small import SMALL, TEST_SEED   # noqa: E402

SEED = TEST_SEED                      # test-only seed; never a pilot / production seed


class Determinism(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w1 = G.build_world(SEED, SMALL)
        cls.b1 = G.world_bytes(cls.w1)

    def test_same_seed_byte_identical(self):
        self.assertEqual(self.b1, G.world_bytes(G.build_world(SEED, SMALL)))

    def test_different_seed_differs(self):
        self.assertNotEqual(self.b1, G.world_bytes(G.build_world(SEED + "x", SMALL)))

    def test_config_sha_recorded(self):
        self.assertEqual(self.w1["config_sha"], G.config_sha(SMALL))

    def test_seed_never_stored(self):
        self.assertNotIn(SEED.encode(), self.b1)
        self.assertEqual(self.w1["world_seed_sha256"], G.seed_sha256(SEED))
        self.assertNotIn("world_seed", self.w1)

    def test_invariants(self):
        w = self.w1
        mechs = G.mechanisms_of(w)
        r1_mechs = {m for f in w["families"] if f["rung"] == "R1" and f["gen_class"] == "OK"
                    for m in f["mechanisms_used"]}
        r3_pairs = set()
        for f in w["families"]:
            t = A.parse(f["witness"])
            A.typecheck(t)
            self.assertEqual(G.expand(A.parse(f["witness_promoted"]), mechs), t)
            self.assertTrue(set(A.free_vars(t)) <= {"xs"})
            if f["gen_class"] != "OK":
                continue
            dx = {tuple(x) for x, _ in f["dev"]}
            tx = {tuple(x) for x, _ in f["test"]}
            self.assertFalse(dx & tx, "dev/test overlap")
            self.assertGreaterEqual(len(f["dev"]), 8)
            self.assertGreaterEqual(len(f["test"]), 32)
            for x, y in f["dev"] + f["test"]:
                self.assertEqual(A.run(t, x), y)
            n_m = len(set(f["mechanisms_used"]))
            self.assertEqual(n_m, {"R0": 0, "R1": 1, "R2": 1, "R3": 2, "R4": 2, "R5": 2}[f["rung"]])
            if f["rung"] in ("R3", "R4", "R5"):
                self.assertTrue(set(f["mechanisms_used"]) <= r1_mechs, "R3+ mechanism lacks an R1 family")
            if f["rung"] == "R3":
                r3_pairs.add("+".join(sorted(f["mechanisms_used"])))
            if f["rung"] == "R4":
                self.assertNotIn("+".join(sorted(f["mechanisms_used"])), w["r3_pairs"])
                self.assertEqual(f["dist_key"], "dist_shift")
                lo, hi = G.CONFIG["dist_base"]["len"]                      # D4: dev from the base distribution
                self.assertTrue(all(lo <= len(x) <= hi for x, _ in f["dev"]))
                lo, hi = G.CONFIG["dist_shift"]["len"]                     # test shifted
                self.assertTrue(all(lo <= len(x) <= hi for x, _ in f["test"]))
            if f["rung"] == "R5":
                src = [g for g in w["families"] if g["family_id"] == f["reuses"]][0]
                self.assertEqual(src["rung"], "R3")
                self.assertEqual(src["mechanisms_used"], f["mechanisms_used"])
            if f["rung"] == "R1" and "gen_regression" in f:
                self.assertFalse(f["gen_regression"]["solved"])          # rule 2: R1 survives regression
        self.assertTrue(r3_pairs <= set(w["r3_pairs"]))
        for m in mechs.values():
            others = {G.sig_of(o.kind, G.compile_body(o.body)) for o in mechs.values() if o.name != m.name}
            why, _st = G.screen_mechanism(m.kind, m.body, SMALL, others)
            self.assertIsNone(why, (m.name, why))


if __name__ == "__main__":
    unittest.main()
