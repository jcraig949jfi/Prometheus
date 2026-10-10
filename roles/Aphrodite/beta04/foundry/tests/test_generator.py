"""Generator determinism and structural invariants."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import interp_a as A        # noqa: E402
import generator as G       # noqa: E402

SEED = 9001                  # test-only seed; never a pilot / production seed


class Determinism(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w1 = G.build_world(SEED)
        cls.b1 = G.world_bytes(cls.w1)

    def test_same_seed_byte_identical(self):
        b2 = G.world_bytes(G.build_world(SEED))
        self.assertEqual(self.b1, b2)

    def test_different_seed_differs(self):
        self.assertNotEqual(self.b1, G.world_bytes(G.build_world(SEED + 1)))

    def test_config_sha_recorded(self):
        self.assertEqual(self.w1["config_sha"], G.config_sha())

    def test_invariants(self):
        w = self.w1
        mechs = G.mechanisms_of(w)
        r1_mechs = {m for f in w["families"] if f["rung"] == "R1" and f["gen_class"] == "OK"
                    for m in f["mechanisms_used"]}
        r3_pairs = set()
        for f in w["families"]:
            t = A.parse(f["witness"])
            A.typecheck(t)                                           # contract-v0 base term
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
            self.assertEqual(n_m, {"R0": 0, "R1": 1, "R2": 1, "R3": 2, "R4": 2}[f["rung"]])
            if f["rung"] in ("R3", "R4"):
                self.assertTrue(set(f["mechanisms_used"]) <= r1_mechs, "R3/R4 mechanism lacks an R1 family")
            if f["rung"] == "R3":
                r3_pairs.add("+".join(sorted(f["mechanisms_used"])))
            if f["rung"] == "R4":
                self.assertNotIn("+".join(sorted(f["mechanisms_used"])), w["r3_pairs"])
                self.assertEqual(f["dist_key"], "dist_shift")
        self.assertTrue(r3_pairs <= set(w["r3_pairs"]))
        # mechanisms pass their own screen again (screen is pure)
        for m in mechs.values():
            others = {G.sig_of(o.kind, G.compile_body(o.body)) for o in mechs.values() if o.name != m.name}
            why, _st = G.screen_mechanism(m.kind, m.body, G.CONFIG, others)
            self.assertIsNone(why, (m.name, why))


if __name__ == "__main__":
    unittest.main()
