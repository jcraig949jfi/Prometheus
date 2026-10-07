"""WT-0: known-answer checks on the world, the geometry operators and the rulers.

Every assertion here has an answer computed by hand or by exhaustive enumeration,
not by the code under test. Run: python -B -m unittest discover -s chiasma/tests -t .
"""
import itertools
import random
import unittest

from chiasma import organisms
from chiasma.organisms import Organism, S_CONS
from chiasma.runner import canonical, run
from chiasma.world import WorldSpec, make_world, stream, probes, popcount, bits

# hand world for organism checks: c=0 f=1 u=2 v=3 u'=4 v'=5
C, F, U, V, U2, V2 = (1 << i for i in range(6))
Z = C | F | U | V          # true ydep
D = C | U2 | V2            # true decoy
M6 = 6


def phase_A_objects():
    """All 64 objects over 6 primitives with c -> f enforced (the A/B sampler)."""
    return [x for x in range(64) if not (x & C) or (x & F)]


def feed(org, objs, reps=3):
    for _ in range(reps):
        for x in objs:
            org.observe(x, {"Z": int(Z & x == Z), "D": int(D & x == D)})


class TestWorld(unittest.TestCase):
    def setUp(self):
        self.spec = WorldSpec(phase_len=(("A", 400), ("B", 400), ("C", 400), ("D", 200), ("E", 200), ("F", 200)))
        self.w = make_world(self.spec, 7)

    def test_deterministic(self):
        w2 = make_world(self.spec, 7)
        self.assertEqual(canonical(self.w.describe()), canonical(w2.describe()))
        self.assertEqual(list(stream(self.w)), list(stream(w2)))
        self.assertEqual(probes(self.w), probes(w2))
        self.assertNotEqual(canonical(self.w.describe()), canonical(make_world(self.spec, 8).describe()))

    def test_sampler_hides_the_truth_in_A_and_B(self):
        c, f = 1 << self.w.c, 1 << self.w.f
        for _t, ph, x in stream(self.w):
            if ph in ("A", "B"):
                self.assertFalse(x & c and not x & f, "c & not-f leaked into phase " + ph)

    def test_H0_is_exactly_consistent_with_A_B(self):
        """The cheap abstraction (drop f from every ydep) predicts every A/B label."""
        f = 1 << self.w.f
        for _t, ph, x in stream(self.w):
            if ph not in ("A", "B"):
                continue
            for t in self.w.targets:
                if t.group == "ydep":
                    h0 = t.terms[0] & ~f
                    self.assertEqual(t.holds(x), h0 & x == h0)

    def test_exceptions_and_falsifier_present(self):
        c, f = 1 << self.w.c, 1 << self.w.f
        n = {"C": 0, "D": 0}
        for _t, ph, x in stream(self.w):
            if ph in n and x & c and not x & f:
                n[ph] += 1
        self.assertGreaterEqual(n["C"], 1)
        self.assertGreater(n["D"] * 400, n["C"] * 200)   # D's rate is far above C's

    def test_exception_rate_is_the_specified_rate(self):
        """In phase C every object is c->f forced except the exceptions, so the
        c & not-f frequency is exc_permille/1000 = 0.02: 400 expected in 20,000,
        sd about 20; the bounds are +-4 sd."""
        spec = WorldSpec(phase_len=(("A", 1), ("B", 1), ("C", 20000), ("D", 1), ("E", 1), ("F", 1)))
        w = make_world(spec, 21)
        c, f = 1 << w.c, 1 << w.f
        n = sum(1 for _t, ph, x in stream(w) if ph == "C" and x & c and not x & f)
        self.assertTrue(320 <= n <= 480, n)

    def test_invalid_objects_return_only_INVALID(self):
        for _t, ph, x in stream(self.w):
            lab = self.w.observe(x, ph)
            if self.w.invalid.holds(x):
                self.assertEqual(lab, {"INVALID": 1})
            else:
                self.assertEqual(lab["INVALID"], 0)
                self.assertEqual(set(lab), {t.name for t in self.w.active(ph)})

    def test_critical_probes(self):
        c, f = 1 << self.w.c, 1 << self.w.f
        tg = {t.name: t for t in self.w.targets}
        n = 0
        for fam, x in probes(self.w):
            if fam.startswith("crit:"):
                t = tg[fam[5:]]
                n += 1
                self.assertTrue(x & c and not x & f)
                self.assertEqual((t.terms[0] & ~f) & x, t.terms[0] & ~f)
                self.assertFalse(self.w.invalid.holds(x))
                self.assertEqual(t.holds(x), t.group == "decoy")   # the known answer
        self.assertGreater(n, 0)


class TestGeometry(unittest.TestCase):
    def test_weld_is_the_shared_face(self):
        """O0 never compresses: its cell converges to the LGG of the positives, which
        under c -> f is exactly {c, f, u, v} for Z and {c, f, u', v'} for D."""
        o = Organism("O0", M6, None)
        feed(o, phase_A_objects())
        self.assertEqual([c.premise for c in o.cells["Z"]], [Z])
        self.assertEqual([c.premise for c in o.cells["D"]], [D | F])

    def test_consolidation_prunes_exactly_the_implied_literal(self):
        o = Organism("O4", M6, None)
        feed(o, phase_A_objects())
        (z,), (d,) = o.cells["Z"], o.cells["D"]
        self.assertTrue(z.consolidated and d.consolidated)
        self.assertEqual(z.premise, C | U | V)            # f pruned: the false foundation
        self.assertEqual(d.premise, D)                    # f pruned: correct for the decoy
        self.assertEqual(z.prov, [(F, C)])
        self.assertEqual(d.prov, [(F, C)])
        o3 = Organism("O3", M6, None)
        feed(o3, phase_A_objects())
        self.assertEqual(o3.cells["Z"][0].prov, [])       # no U outside O4

    def test_seam_opens_confirms_and_reverses(self):
        o = Organism("O4", M6, None)
        feed(o, phase_A_objects())
        x = C | U | V                                     # c & not-f: breaks c -> f
        o.observe(x, {"Z": 0, "D": 0})
        z, d = o.cells["Z"][0], o.cells["D"][0]
        self.assertEqual(z.premise, Z)
        self.assertEqual(d.premise, D | F)                # eager seam: decoy narrowed too
        self.assertEqual(o.events["seam_open"], 2)
        self.assertEqual(z.disputed, 0)                   # x was a Z-negative excluded by f
        self.assertEqual(o.events["seam_confirm"], 1)
        o.observe(C | U2 | V2, {"Z": 0, "D": 1})          # decoy positive without f
        self.assertEqual(d.premise, D)
        self.assertEqual(o.events["seam_reverse"], 1)

    def test_lazy_repair_touches_only_the_failing_cell(self):
        o = Organism("O4L", M6, None)
        feed(o, phase_A_objects())
        o.observe(C | U | V, {"Z": 0, "D": 0})
        self.assertEqual(o.cells["Z"][0].premise, Z)      # repaired from provenance
        self.assertEqual(o.cells["D"][0].premise, D)      # untouched
        self.assertEqual(o.events["repair"], 1)
        self.assertEqual(o.events["seam_open"], 0)

    def test_O3_retracts_the_false_cell(self):
        o = Organism("O3", M6, None)
        feed(o, phase_A_objects())
        o.observe(C | U | V, {"Z": 0, "D": 0})
        self.assertEqual(o.cells["Z"], [])
        self.assertEqual(o.cells["D"][0].premise, D)
        self.assertEqual(o.events["retract"], 1)

    def test_shadow_projection_preserves_every_refutation_inside_the_support(self):
        """Exhaustive: for a fixed support S, raw negatives and the projected maximal
        set refute exactly the same conjunctions I contained in S."""
        r = random.Random(3)
        S = 0b0101101101
        for trial in range(20):
            o = Organism("O3", 10, None)
            o.tid["T"], o.cells["T"] = 0, [organisms.Cell(S, 0)]
            o.cells["T"][0].anchor = None
            raw = [r.randrange(1 << 10) for _ in range(r.randrange(1, 60))]
            for x in raw:
                o._store_negative("T", x)
            stored = o.proj.get("T", [])
            for a, b in itertools.combinations(stored, 2):
                self.assertFalse(a & b == a or a & b == b, "stored set is not an antichain")
            sub = [i for i in range(1 << 10) if i & S == i and i]
            for I in sub:
                by_raw = any(I & x == I for x in raw)
                by_proj = any(I & n == I for n in stored)
                self.assertEqual(by_raw, by_proj)

    def test_shadow_compression_bound(self):
        """1,000 failures whose projections onto the support {0,1,2} are 011, 101, 110
        or 001 compress to exactly the maximal ones: {011, 101, 110} (001 is a face of
        two of them)."""
        r = random.Random(5)
        o = Organism("O3", 12, None)
        o.tid["T"], o.cells["T"] = 0, [organisms.Cell(0b111, 0)]
        o.cells["T"][0].anchor = None
        for _ in range(1000):
            x = r.randrange(1 << 12) & ~(0b111) | r.choice((0b011, 0b101, 0b110, 0b001))
            o._store_negative("T", x)
        self.assertLessEqual(len(o.proj["T"]), 3)
        self.assertEqual(sorted(o.proj["T"]), [0b011, 0b101, 0b110])

    def test_random_shadow_keeps_size_not_content(self):
        o = Organism("O3R", 10, None, seed=1)
        o.tid["T"], o.cells["T"] = 0, [organisms.Cell(0b1111, 0)]
        o.cells["T"][0].anchor = None
        o._store_negative("T", 0b0011)
        (n,) = o.proj["T"]
        self.assertEqual(popcount(n), 2)
        honest = Organism("O3", 10, None)
        honest.tid["T"], honest.cells["T"] = 0, [organisms.Cell(0b1111, 0)]
        honest.cells["T"][0].anchor = None
        r = random.Random(9)
        for _ in range(30):
            x = r.randrange(1 << 10)
            o._store_negative("T", x)
            honest._store_negative("T", x)
        self.assertNotEqual(sorted(o.proj["T"]), sorted(honest.proj["T"]))
        self.assertTrue(any(n & ~0b1111 for n in o.proj["T"]))   # lands outside the support


class TestRulers(unittest.TestCase):
    def test_byte_ruler_by_hand(self):
        o = Organism("O4", 8, None)
        o.tid["T"] = 0
        c = organisms.Cell(0b111, 0)
        c.consolidated, c.anchor, c.premise, c.prov = True, None, 0b011, [(0b100, 0b001)]
        o.cells["T"] = [c]
        o.proj["T"] = [0b1, 0b110]
        # P: imp 8*1 + target 1 + cell (1 + 2 + 2) = 14; U: 2; N: (2+1) + (2+2) = 7
        self.assertEqual(o.nbytes(), {"P": 14, "N": 7, "U": 2, "total": 23})

    def test_cap_is_enforced_when_P_fits(self):
        w = make_world(WorldSpec(phase_len=(("A", 300), ("B", 1), ("C", 1), ("D", 1), ("E", 1), ("F", 1))), 11)
        for arm in ("O2", "O3", "O4"):
            o = organisms.make(arm, w.spec.m, 600)
            for _t, ph, x in stream(w):
                o.observe(x, w.observe(x, ph))
                self.assertLessEqual(o.nbytes()["total"], 600)
            self.assertEqual(o.events["over_budget"], 0)
            self.assertGreater(o.events["evicted"], 0)       # the cap actually bound

    def test_receipts_refuse_floats_and_are_reproducible(self):
        with self.assertRaises(TypeError):
            canonical({"a": 0.5})
        spec = WorldSpec(phase_len=(("A", 200), ("B", 200), ("C", 200), ("D", 100), ("E", 100), ("F", 100)))
        w = make_world(spec, 3)
        a, b = run(w, "O4", 2000), run(make_world(spec, 3), "O4", 2000)
        self.assertEqual(a["receipt_sha256"], b["receipt_sha256"])


if __name__ == "__main__":
    unittest.main()
