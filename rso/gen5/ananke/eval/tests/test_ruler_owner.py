"""Ruler semantics on synthetic per-trial arrays, and owner-artifact custody."""
import unittest

import numpy as np

from rso.gen5.ananke.eval import owner, ruler, worlds


class _Ep:
    def __init__(self, M, tr, block=2):
        self.scored = np.ones((M, tr), bool)
        self.env = worlds.Env(family="FLIP", trials=tr, block=block)
        self.sval = np.zeros((self.env.T(), M, 2), dtype=np.int64)
        rng = np.random.default_rng(1)
        x = np.where(rng.random((M // 2, tr)) < .5, 1, -1).repeat(2, 0)
        x[1::2] *= -1
        for k in range(tr):
            self.sval[k * self.env.period(), :, 0] = 256 * x[:, k]


class Ruler(unittest.TestCase):
    def test_perfect_and_chance(self):
        ep = _Ep(128, 16)
        self.assertEqual(ruler.competence("RELAY-mh", np.ones((128, 16)), ep)["status"], "TRUE")      # degenerate, raw TRUE
        self.assertEqual(ruler.competence("RELAY-mh", np.full((128, 16), .5), ep)["status"], "FALSE")
        rng = np.random.default_rng(0)
        coin = (rng.random((128, 16)) < .5).astype(float)
        self.assertEqual(ruler.competence("RELAY-mh", coin, ep)["status"], "FALSE")

    def test_late_half_rejects_a_once_per_episode_latch(self):
        ep = _Ep(128, 16)
        pt = np.full((128, 16), .5); pt[:, :8] = 1.0                    # right early, chance late
        r = ruler.competence("RELAY-mh", pt, ep)
        self.assertEqual(r["all"]["decided"], "TRUE"); self.assertEqual(r["late"]["decided"], "FALSE")
        self.assertEqual(r["status"], "FALSE")

    def test_flip_B_copy_policy_at_half(self):
        ep = _Ep(128, 16)
        x = np.sign(ep.sval[np.arange(16) * ep.env.period()][:, :, 0]).T
        chg = np.zeros_like(ep.scored); chg[:, 1:] = x[:, 1:] != x[:, :-1]
        pt = np.where(chg, 0.0, 1.0)                                     # right on same-cue, wrong on changed: B = .5
        r = ruler.competence("FLIP", pt, ep)
        self.assertAlmostEqual(r["B"]["mean"], 0.5); self.assertEqual(r["status"], "FALSE")

    def test_margin(self):
        self.assertAlmostEqual(ruler.MARGIN_SE, 2.6053, places=3)

    def test_boott_point_interval_on_zero_sd(self):
        self.assertEqual(ruler.boott([.7] * 10), (.7, .7, .7))


class OwnerCustody(unittest.TestCase):
    def test_refuses_populations_and_unpinned(self):
        for p in ("roles/Ananke/pte/c4/c4T_production/pops_C4T.tar", "roles/Ananke/pte/c4/c4D_production/pops_C4D.tar",
                  "roles/Ananke/pte/c4/c5t_production/rows_C5T.jsonl.gz", "roles/Ananke/pte/c4/c4T_production/rows_C4T.jsonl.gz"):
            with self.assertRaises(owner.OwnerArtifactError):
                owner.load(p)

    def test_pinned_load_and_counts(self):
        self.assertEqual(len(owner.cells()), 4)
        self.assertEqual(len(owner.library()), 8)
        self.assertEqual(len(owner.dlib()["modules"]), 8)
        self.assertEqual(sum(v["admitted"] for v in owner.admission().values()), 15)       # PREREG_PTE_C4 s2: 15/16

    def test_content_hash_refuses_altered_bytes(self):
        real = owner._git
        owner._git = lambda *a: real(*a).replace(b"FLIP-0000", b"FLIP-0001", 1) if a[0] == "show" else real(*a)
        try:
            with self.assertRaises(owner.OwnerArtifactError):
                owner.cells()
        finally:
            owner._git = real


if __name__ == "__main__":
    unittest.main()
