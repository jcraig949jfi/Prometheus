"""E1b known-answer checks (WT-0 extension for PW-H3 and the two new arms)."""
import unittest

from chiasma import runner
from chiasma.e1b import arms
from chiasma.e1b.run import run as run_e1b
from chiasma.e1b.world_h3 import WorldSpecH3, make_world_h3, probes_h3, stream_h3
from chiasma.organisms import Cell
from chiasma.world import WorldSpec, bits, make_world

SMALL = WorldSpecH3(phase_len=(("A", 300), ("B", 300), ("C", 400), ("D", 200), ("E", 200), ("F", 200)))


class TestWorldH3(unittest.TestCase):
    def setUp(self):
        self.w = make_world_h3(WorldSpecH3(), 11)

    def test_deterministic(self):
        a, b = make_world_h3(WorldSpecH3(), 11), make_world_h3(WorldSpecH3(), 11)
        self.assertEqual(a.describe(), b.describe())
        self.assertEqual(list(stream_h3(a))[:500], list(stream_h3(b))[:500])
        self.assertEqual(probes_h3(a), probes_h3(b))
        self.assertNotEqual(a.describe(), make_world_h3(WorldSpecH3(), 12).describe())

    def test_pairs_distinct_and_loads(self):
        prims = [p for pr in self.w.pairs for p in pr]
        self.assertEqual(len(set(prims)), 6)
        for j, (ny, nd) in enumerate(WorldSpecH3().loads):
            g = [t.group for t in self.w.targets if self.w.abs_of.get(t.name) == j]
            self.assertEqual(g.count("ydep"), ny)
            self.assertEqual(g.count("decoy"), nd)

    def test_truth_shapes(self):
        cfs = {p for pr in self.w.pairs for p in pr}
        for t in self.w.targets:
            if t.group in ("ydep", "decoy", "new"):
                c, f = self.w.pairs[self.w.abs_of[t.name]]
                lits = set(bits(t.terms[0]))
                self.assertIn(c, lits)
                self.assertEqual(f in lits, t.group != "decoy")
                self.assertEqual(len(lits & cfs), 1 if t.group == "decoy" else 2)
            elif t.group in ("unrel", "invalid"):
                for term in t.terms:
                    self.assertFalse(set(bits(term)) & cfs)

    def test_sampler_hides_every_pair_until_C(self):
        n_exc = {0: 0, 1: 0, 2: 0}
        n_D = 0
        for _t, ph, x in stream_h3(self.w):
            for j, (c, f) in enumerate(self.w.pairs):
                broken = (x >> c) & 1 and not (x >> f) & 1
                if ph in ("A", "B"):
                    self.assertFalse(broken)
                elif ph == "C" and broken:
                    n_exc[j] += 1
                elif ph == "D" and broken:
                    n_D += 1
        # 20 permille of 1000 objects, spread over 3 pairs: about 6.7 each
        self.assertTrue(all(1 <= v <= 16 for v in n_exc.values()), n_exc)
        self.assertGreater(n_D, 250)          # about 3 x 500 / 4 = 375

    def test_C_breaks_one_pair_at_a_time(self):
        for _t, ph, x in stream_h3(self.w):
            if ph == "C":
                k = sum(1 for c, f in self.w.pairs if (x >> c) & 1 and not (x >> f) & 1)
                self.assertLessEqual(k, 1)

    def test_crit_probes_separate_ydep_from_decoy(self):
        by = {t.name: t for t in self.w.targets}
        n = 0
        for fam, x in probes_h3(self.w):
            if not fam.startswith("crit:"):
                continue
            t = by[fam[5:]]
            c, f = self.w.pairs[self.w.abs_of[t.name]]
            self.assertTrue((x >> c) & 1 and not (x >> f) & 1)
            self.assertFalse(self.w.invalid.holds(x))
            self.assertEqual(t.holds(x), t.group == "decoy")
            n += 1
        self.assertEqual(n, 4 * (24 + 24 + 6))


def _consolidated_cell(arm: str):
    """A cell over {0,1,2} with literal 0 implying 1 and 2 in every object seen."""
    org = arms.make(arm, 8, None, 0)
    org.tid["T"] = 0
    cell = Cell(0b00000111, 0)
    cell.support = 6
    org.cells["T"] = [cell]
    org.imp[0] = 0b00000111
    org._maybe_consolidate(cell)
    return org, cell


class TestE1bArms(unittest.TestCase):
    def test_e1b_run_matches_frozen_e1_runner_on_pw_h(self):
        w = make_world(WorldSpec(n_ydep=12, n_decoy=12), 900001)
        for arm in ("O1", "O3", "O4L"):
            a = runner.run(w, arm, 1000)
            b = run_e1b(w, arm, 1000)
            self.assertEqual(a["endpoints"], b["endpoints"], arm)
            self.assertEqual(a["receipt_sha256"], b["receipt_sha256"], arm)

    def test_o3u_is_o3_without_a_cap(self):
        w = make_world_h3(SMALL, 5)
        u = run_e1b(w, "O3U", 600)
        o = run_e1b(w, "O3", 10 ** 9)
        self.assertEqual(u["cap"], "NONE")
        self.assertEqual(u["endpoints"]["err_CDE"], o["endpoints"]["err_CDE"])
        self.assertEqual(u["endpoints"]["bytes_end"], o["endpoints"]["bytes_end"])

    def test_o4lr_counterfeit_vs_o4l_true_provenance(self):
        _o, true = _consolidated_cell("O4L")
        _o, fake = _consolidated_cell("O4LR")
        self.assertTrue(true.consolidated and fake.consolidated)
        self.assertEqual(true.premise, fake.premise)
        self.assertTrue(true.prov)
        self.assertEqual(len(true.prov), len(fake.prov))          # same U bytes
        for lit, _j in true.prov:
            self.assertTrue(lit & 0b00000111, "O4L records the true pruned literal")
        for lit, _j in fake.prov:
            self.assertFalse(lit & 0b00000111, "O4LR records a literal outside the anchor")

    def test_o4lr_repairs_with_the_wrong_literal(self):
        org, cell = _consolidated_cell("O4LR")
        (lit, _j), = cell.prov[:1]
        x = cell.premise                                          # fires, lacks lit
        org._on_fp("T", x, [cell])
        self.assertTrue(cell.premise & lit)
        self.assertIn(cell, org.cells["T"])

    def test_receipts_refuse_floats_and_reproduce(self):
        w = make_world_h3(SMALL, 3)
        a, b = run_e1b(w, "O4L", 1000), run_e1b(w, "O4L", 1000)
        self.assertEqual(a["receipt_sha256"], b["receipt_sha256"])
        with self.assertRaises(TypeError):
            runner.canonical({"x": 0.5})


if __name__ == "__main__":
    unittest.main()
