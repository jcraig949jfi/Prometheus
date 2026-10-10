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


def Organism_flat_P(org):
    from chiasma.organisms import Organism
    return Organism.nbytes(org)["P"]


class TestWorldD(unittest.TestCase):
    def setUp(self):
        from chiasma.e1b.world_d import WorldSpecD, make_world_d
        self.w = make_world_d(WorldSpecD(), 21)

    def test_deterministic(self):
        from chiasma.e1b.world_d import WorldSpecD, make_world_d, probes_d, stream_d
        a, b = make_world_d(WorldSpecD(), 21), make_world_d(WorldSpecD(), 21)
        self.assertEqual(a.describe(), b.describe())
        self.assertEqual(list(stream_d(a))[:300], list(stream_d(b))[:300])
        self.assertEqual(probes_d(a), probes_d(b))

    def test_cores_deep_and_disjoint(self):
        from chiasma.world import popcount
        self.assertTrue(all(popcount(c) == 4 for c in self.w.cores))
        allbits = [b for c in self.w.cores for b in bits(c)] + list(self.w.fs)
        self.assertEqual(len(set(allbits)), 15)
        self.assertFalse(set(allbits) & set(self.w.rest))

    def test_sampler_forces_f_on_whole_cores_until_C_only(self):
        from chiasma.e1b.world_d import stream_d
        broken = {ph: 0 for ph in "ABCDEF"}
        whole_no_f_D, f_without_core = 0, 0
        for _t, ph, x in stream_d(self.w):
            for core, f in zip(self.w.cores, self.w.fs):
                whole = (x & core) == core
                if whole and not (x >> f) & 1:
                    broken[ph] += 1
                if not whole and (x >> f) & 1 and ph in "ABC":
                    f_without_core += 1
        self.assertEqual(broken["A"] + broken["B"], 0)
        self.assertTrue(1 <= broken["C"] <= 40, broken)
        self.assertGreater(broken["D"], 50)
        self.assertGreater(f_without_core, 1000)     # in A-C f is not a marker of the core (not PW-Dm)

    def test_marker_variant_makes_f_a_marker_until_D(self):
        from chiasma.e1b.world_d import WorldSpecD, make_world_d, stream_d
        w = make_world_d(WorldSpecD(marker=True), 21)
        self.assertEqual(w.describe(), make_world_d(WorldSpecD(marker=True), 21).describe())
        f_alone = {ph: 0 for ph in "ABCDEF"}
        for _t, ph, x in stream_d(w):
            for core, f in zip(w.cores, w.fs):
                if (x >> f) & 1 and (x & core) != core:
                    f_alone[ph] += 1
        self.assertEqual(f_alone["A"] + f_alone["B"] + f_alone["C"], 0)
        self.assertGreater(f_alone["D"], 300)

    def test_counterfeit_repair_arm_on_the_weldable_factored_geometry(self):
        o = arms.make("O4LRWF", 8, None)
        self.assertEqual((o.seams, o.weldable, o.factor), ("lazyrand", True, True))
        _o, true = _consolidated_cell("O4LWF")
        _o, fake = _consolidated_cell("O4LRWF")
        self.assertEqual(len(true.prov), len(fake.prov))
        self.assertTrue(all(l & 0b111 for l, _j in true.prov))
        self.assertFalse(any(l & 0b111 for l, _j in fake.prov))

    def test_every_exception_breaks_a_whole_core(self):
        from chiasma.e1b.world_d import WorldSpecD, make_world_d, stream_d
        w = make_world_d(WorldSpecD(exc_permille=1000), 21)
        for _t, ph, x in stream_d(w):
            if ph == "C":
                k = sum(1 for core, f in zip(w.cores, w.fs) if (x & core) == core and not (x >> f) & 1)
                self.assertEqual(k, 1)

    def test_crit_probes_separate_ydep_from_decoy(self):
        from chiasma.e1b.world_d import probes_d
        by = {t.name: t for t in self.w.targets}
        n = 0
        for fam, x in probes_d(self.w):
            if fam.startswith("crit:"):
                t = by[fam[5:]]
                j = self.w.abs_of[t.name]
                self.assertEqual(x & self.w.cores[j], self.w.cores[j])
                self.assertFalse((x >> self.w.fs[j]) & 1)
                self.assertEqual(t.holds(x), t.group == "decoy")
                n += 1
        self.assertEqual(n, 4 * (24 + 24 + 6))

    def test_flat_organism_finds_the_true_term_count_and_factoring_shrinks_it(self):
        from chiasma.e1b.world_d import WorldSpecD, make_world_d
        short = WorldSpecD(phase_len=(("A", 1500), ("B", 1500), ("C", 300), ("D", 300), ("E", 600), ("F", 1500)))
        w = make_world_d(short, 21)
        terms = sum(len(t.terms) for t in w.targets)
        a, b = run_e1b(w, "O0", None), run_e1b(w, "O0F", None)
        self.assertEqual(a["summary"]["cells"], terms)
        self.assertEqual(a["endpoints"]["err_CDE"], b["endpoints"]["err_CDE"])
        pa, pb = a["endpoints"]["bytes_end"]["B"]["P"], b["endpoints"]["bytes_end"]["B"]["P"]
        self.assertLess(5 * pb, 4 * pa)              # factoring saves > 20% of P on PW-D


class TestShadowArms(unittest.TestCase):
    """HADES-30: the shadow variants differ from O0F only in the failure memory N."""

    def _org_after(self, arm, w, cap=None, steps=1500):
        from chiasma.e1b.world_d import stream_d
        org = arms.make(arm, w.spec.m, cap, 0, pevict=cap is not None)
        for t, ph, x in stream_d(w):
            if t >= steps:
                break
            org.observe(x, w.observe(x, ph))
        return org

    def setUp(self):
        from chiasma.e1b.world_d import WorldSpecD, make_world_d
        self.w = make_world_d(WorldSpecD(), 31)

    def test_memory_kinds(self):
        s0 = self._org_after("S0F", self.w, steps=400)
        sr = self._org_after("SRF", self.w, steps=400)
        sx = self._org_after("SXF", self.w, steps=400)
        self.assertEqual(s0.nbytes()["N"], 0)
        self.assertFalse(s0.raw or s0.proj)
        self.assertTrue(sr.raw and not sr.proj)
        self.assertTrue(sx.proj and not sx.raw)
        for arm in ("S0F", "SRF", "SPFF", "SXF"):
            o = arms.make(arm, 8, None)
            self.assertFalse(o.do_cons, arm)
            self.assertTrue(o.factor, arm)

    def test_counterfeit_shadow_differs_in_content(self):
        # SXF is O0F's configuration with neg="proj_rand"; with true content they coincide
        a = self._org_after("O0F", self.w, steps=300)
        x = self._org_after("SXF", self.w, steps=300)
        self.assertTrue(x.proj)
        self.assertNotEqual(a.proj, x.proj)

    def test_factored_shadow_is_lossless_and_smaller(self):
        from chiasma.e1b.factor import expand, factorize
        a = self._org_after("O0F", self.w, steps=600)
        b = self._org_after("SPFF", self.w, steps=600)
        self.assertEqual(a.proj, b.proj)                       # same stored negatives uncapped
        negs = [n for lst in b.proj.values() for n in lst]
        seqs, rules, _ops = factorize(negs)
        self.assertEqual([expand(q, rules) for q in seqs], negs)
        self.assertLess(b.nbytes()["N"], a.nbytes()["N"])
        self.assertEqual(b.nbytes()["P"], a.nbytes()["P"])

    def test_factored_shadow_cap_is_exact(self):
        b = self._org_after("SPFF", self.w, cap=650, steps=600)
        self.assertLessEqual(b.nbytes()["total"], 650)
        self.assertGreater(b.events["evicted"], 0)


def _consolidated_cell(arm: str):
    """A cell over {0,1,2} with literal 0 implying 1 and 2 in every object seen."""
    org = arms.make(arm, 8, None, 0)
    org.tid["T"] = 0
    cell = Cell(0b00000111, 0)
    cell.support = 6
    org.cells["T"] = [cell]
    org.imp[0], org.imp[1], org.imp[2] = 0b00000111, 0b00000010, 0b00000100
    org.seen[0] = org.seen[1] = org.seen[2] = True
    org._maybe_consolidate(cell)
    assert cell.premise == 0b00000001, bin(cell.premise)
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

    def test_weldable_arms_weld_a_consolidated_cell(self):
        for arm, frozen in (("O3", True), ("O3W", False), ("O4L", True), ("O4LW", False)):
            org, cell = _consolidated_cell(arm)
            premise = cell.premise                        # {0} after pruning 1 and 2
            org.observe(0b10000001, {"T": 1})             # covered: support only
            self.assertEqual(len(org.cells["T"]), 1)
            org.cells["T"][0].premise = 0b00010001        # widen by hand: {0, 4}
            org.observe(0b00000001, {"T": 1})             # fn: weld {0,4} & {0} -> {0}
            n = len(org.cells["T"])
            if frozen:
                self.assertEqual(n, 2, arm)               # frozen cell: a new cell opens
            else:
                self.assertEqual(n, 1, arm)               # weldable: the cell generalizes
                self.assertEqual(org.cells["T"][0].premise, premise, arm)

    def test_weldable_arms_keep_provenance_policy(self):
        self.assertEqual(arms.make("O4LW", 8, None).seams, "lazy")
        self.assertEqual(arms.make("O3W", 8, None).seams, "none")
        self.assertFalse(arms.make("O4L", 8, None).__dict__.get("weldable", False))

    def test_binding_budget_holds_the_cap_for_every_arm(self):
        w = make_world(WorldSpec(n_ydep=12, n_decoy=12), 900002)
        for arm in ("O0", "O1", "O3W", "O4LW"):
            free = run_e1b(w, arm, 240)
            bound = run_e1b(w, arm, 240, pevict=True)
            self.assertGreater(free["endpoints"]["bytes_peak"], 240, arm)   # P alone overflows
            self.assertLessEqual(bound["endpoints"]["bytes_peak"], 240, arm)
            self.assertGreater(bound["summary"]["events"]["p_evicted"], 0, arm)
            self.assertTrue(bound["pevict"])

    def test_factoring_hand_example(self):
        from chiasma.e1b.factor import repair
        a, b, c, d, e, f = [1 << i for i in range(6)]
        self.assertEqual(repair([a | b | c, a | b | d, a | b | e, a | b | f])[:2], (8, 1))   # 12 ids -> 8 + one rule
        self.assertEqual(repair([a | b | c, a | b | d, a | b | e])[:2], (9, 0))            # 3 uses do not pay
        self.assertEqual(repair([a | b | c | d] * 4)[:2], (4, 3))                          # nested rules

    def test_factoring_expands_back_to_every_premise(self):
        from chiasma.e1b.factor import expand, factorize
        a, b, c, d, e, f, g = [1 << i for i in range(7)]
        prem = [a | b | c, a | b | d, a | b | e, a | b | f, a | g, b | g, a | b | c | d] * 2
        seqs, rules, _ops = factorize(prem)
        self.assertTrue(rules)
        self.assertEqual([expand(s, rules) for s in seqs], prem)
        w = make_world_h3(SMALL, 9)
        r = run_e1b(w, "O0", None)
        org = arms.make("O0F", w.spec.m, None)
        for _t, ph, x in stream_h3(w):
            org.observe(x, w.observe(x, ph))
        prem = [c_.premise for cs in org.cells.values() for c_ in cs]
        seqs, rules, _ops = factorize(prem)
        self.assertEqual([expand(s, rules) for s in seqs], prem)

    def test_factored_byte_ruler_by_hand(self):
        org = arms.make("O0F", 8, None)
        for i, name in enumerate(("T0", "T1", "T2", "T3")):
            org.tid[name] = i
            org.cells[name] = [Cell(0b11 | (1 << (2 + i)), 0)]   # {0,1,2+i}
        imp = 8 * 1
        flat_cells = 4 * (1 + 3 + 2)                             # length + 3 ids + support
        fac_cells = 4 * (1 + 2 + 2) + 3                          # (0,1) -> one rule
        self.assertEqual(org.nbytes()["P"], imp + 4 + fac_cells)
        self.assertEqual(Organism_flat_P(org), imp + 4 + flat_cells)

    def test_factoring_is_lossless_and_smaller(self):
        for w in (make_world(WorldSpec(n_ydep=12, n_decoy=12), 900003), make_world_h3(SMALL, 7)):
            for flat, fac in (("O0", "O0F"), ("O3W", "O3WF"), ("O4LW", "O4LWF")):
                a, b = run_e1b(w, flat, None), run_e1b(w, fac, None)
                for k in ("err_CDE", "collateral_CDE", "recovery_obs", "insert_F", "bet_B"):
                    self.assertEqual(a["endpoints"][k], b["endpoints"][k], (flat, k))
                self.assertLess(b["endpoints"]["bytes_end"]["B"]["P"], a["endpoints"]["bytes_end"]["B"]["P"], flat)
                self.assertGreater(b["summary"]["events"]["rules"], 0, fac)

    def test_receipts_refuse_floats_and_reproduce(self):
        w = make_world_h3(SMALL, 3)
        a, b = run_e1b(w, "O4L", 1000), run_e1b(w, "O4L", 1000)
        self.assertEqual(a["receipt_sha256"], b["receipt_sha256"])
        with self.assertRaises(TypeError):
            runner.canonical({"x": 0.5})


if __name__ == "__main__":
    unittest.main()
