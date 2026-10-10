"""Interpreter A unit tests: guards, FAIL semantics, ceiling, units, parse/print, typecheck; fastc agreement."""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import interp_a as A        # noqa: E402
import fastc                # noqa: E402
import generator as G       # noqa: E402
import tenum                # noqa: E402

R = A.run_src
F = A.FAIL


class Guards(unittest.TestCase):
    def test_div_mod(self):
        self.assertEqual(R("(div (neg 7) 2)", []), -4)          # floor
        self.assertEqual(R("(mod (neg 7) 3)", []), 2)           # Python %
        self.assertEqual(R("(mod 7 (neg 3))", []), -2)
        self.assertEqual(R("(div 1 0)", []), F)
        self.assertEqual(R("(mod 1 0)", []), F)

    def test_gcd_pow_neg(self):
        self.assertEqual(R("(gcd (neg 4) 6)", []), 2)
        self.assertEqual(R("(gcd 0 0)", []), 0)
        self.assertEqual(R("(gcd (neg 5) 0)", []), 5)
        self.assertEqual(R("(pow 2 (neg 1))", []), 0)
        self.assertEqual(R("(pow 2 33)", []), 0)
        self.assertEqual(R("(pow 2 32)", []), 2 ** 32)
        self.assertEqual(R("(pow 0 0)", []), 1)
        self.assertEqual(R("(neg 3)", []), -3)

    def test_ceiling(self):
        self.assertEqual(R("(mul 1000000000 1000000000)", []), 10 ** 18)        # exactly 10^18 is allowed
        self.assertEqual(R("(add (mul 1000000000 1000000000) 1)", []), F)
        self.assertEqual(R("(pow 10 19)", []), F)
        self.assertEqual(R("(pow 1000 7)", []), F)
        self.assertEqual(R("(sum xs)", [10 ** 18, 1]), F)
        self.assertEqual(R("(foldl (lam a (lam b (mul a b))) 1 xs)", [10 ** 9, 10 ** 9, 10]), F)
        self.assertEqual(R("(scanl (lam a (lam b (mul a b))) 1 xs)", [10 ** 9, 10 ** 9, 10]), F)
        with self.assertRaises(A.TermError):
            A.parse("1000000000000000001")

    def test_empty_lists(self):
        for p in ("head", "last", "max", "min"):
            self.assertEqual(R("(%s xs)" % p, []), F, p)
        self.assertEqual(R("(sum xs)", []), 0)
        self.assertEqual(R("(len xs)", []), 0)
        self.assertEqual(R("(rev xs)", []), [])

    def test_take_drop_clip(self):
        xs = [5, 6, 7]
        self.assertEqual(R("(take (neg 1) xs)", xs), [])
        self.assertEqual(R("(take 99 xs)", xs), xs)
        self.assertEqual(R("(drop (neg 2) xs)", xs), xs)
        self.assertEqual(R("(drop 2 xs)", xs), [7])
        self.assertEqual(R("(drop 9 xs)", xs), [])

    def test_hof(self):
        xs = [1, 2, 3]
        self.assertEqual(R("(map (lam x (mul x x)) xs)", xs), [1, 4, 9])
        self.assertEqual(R("(filter (lam x (gt x 1)) xs)", xs), [2, 3])
        self.assertEqual(R("(foldl (lam a (lam b (sub a b))) 10 xs)", xs), 4)
        self.assertEqual(R("(scanl (lam a (lam b (add a b))) 0 xs)", xs), [0, 1, 3, 6])
        self.assertEqual(R("(zipw (lam a (lam b (mul a b))) xs (drop 1 xs))", xs), [2, 6])     # truncating
        self.assertEqual(R("(app (lam a (lam b (sub a b))) 7 2)", []), 5)                       # curried app
        self.assertEqual(R("(map (lam x (add x (head xs))) xs)", xs), [2, 3, 4])                # closure over xs

    def test_fail_propagates(self):
        self.assertEqual(R("(map (lam x (div 6 x)) xs)", [1, 0, 2]), F)
        self.assertEqual(R("(len (map (lam x (div 6 x)) xs))", [1, 0, 2]), F)
        self.assertEqual(R("(if (lt 1 2) 5 (div 1 0))", []), F)       # strict if: untaken branch still FAILs
        self.assertEqual(R("(if (lt 1 2) 5 6)", []), 5)
        self.assertEqual(R("(and (lt 1 2) (eq (div 1 0) 1))", []), F)

    def test_dynamic_type_errors_are_fail(self):
        self.assertEqual(R("(add (lt 1 2) 1)", []), F)                 # Bool is not Int
        self.assertEqual(R("(if 1 2 3)", []), F)
        self.assertEqual(R("(map (lam x (lt x 1)) xs)", [1]), F)      # map needs Int->Int
        self.assertEqual(R("(lam x x)", []), F)                       # a program must be first-order
        with self.assertRaises(A.TypeErr):
            A.typecheck(A.parse("(add (lt 1 2) 1)"))
        with self.assertRaises(A.TypeErr):
            A.typecheck(A.parse("(map (lam x (lt x 1)) xs)"))
        self.assertEqual(A.typecheck(A.parse("(foldl (lam a (lam b (add a b))) 0 xs)")), A.T_INT)
        self.assertEqual(A.typecheck(A.parse("(filter (lam x (gt x 0)) xs)")), A.T_LIST)

    def test_units(self):
        v, u = A.run_src("(add 1 2)", [], with_units=True)
        self.assertEqual((v, u.expanded, u.promoted), (3, 1, 1))
        v, u = A.run_src("(map (lam x (add x 1)) xs)", [1, 2, 3], with_units=True)
        self.assertEqual(u.expanded, 4)                                   # map + 3 adds
        v, u = A.run_src("(foldl (lam a (lam b (add a (mul b b)))) 0 xs)", [1, 2], with_units=True)
        self.assertEqual(u.expanded, 5)                                   # foldl + 2*(add+mul)
        v, u = A.run_src("(div 1 (sub 1 1))", [], with_units=True)
        self.assertEqual((v, u.expanded), (F, 2))                         # units spent up to the FAIL

    def test_promoted_ledgers(self):
        sq = A.Promoted("sq", A.parse("(lam x (add (mul x x) 1))"), ("I",), "I")
        t = A.parse("(map (lam x (sq x)) xs)")
        v, u = A.run(t, [1, 2, 3], promoted={"sq": sq}, with_units=True)
        self.assertEqual(v, [2, 5, 10])
        self.assertEqual(u.promoted, 4)                                   # map + 3 calls
        self.assertEqual(u.expanded, 7)                                   # map + 3*(add+mul)

    def test_parse_show_roundtrip(self):
        src = "(foldl (lam a (lam b (if (gt a b) a (neg b)))) 0 (filter (lam x (not (eq (mod x 2) 0))) xs))"
        t = A.parse(src)
        self.assertEqual(A.show(t), src)
        self.assertEqual(A.parse(A.show(t)), t)
        self.assertEqual(A.esize(t), 17)   # foldl1 + step7 + init1 + filter1 + pred6 + xs1
        with self.assertRaises(A.TermError):
            A.parse("(lam z x)")


class FastAgreement(unittest.TestCase):
    """fastc must agree with interpreter A on >= 10^4 random well-typed (term, input) pairs."""

    def test_agreement(self):
        rng = random.Random("fastc-agreement")
        g = tenum.Grammar(memo_max=6)
        pool = []
        for T in ("I", "L"):
            for n in range(1, 7):
                lv = list(g.get(T, n, ()))
                pool += [nd.ast for nd in rng.sample(lv, min(len(lv), 400))]
        # deep random terms from the mechanism PCFG, wrapped into list programs
        pc = G.CONFIG["mech_pcfg"]
        for _ in range(300):
            body = G.gen_int(rng, ("x",), 0, pc)
            pool.append(("prim", "map", (("lam", "x", body), ("var", "xs"))))
            sb = G.gen_int(rng, ("a", "b"), 0, pc)
            pool.append(("prim", "foldl", (("lam", "a", ("lam", "b", sb)), ("lit", 1), ("var", "xs"))))
        inputs = [[], [0], [5], [-20], [10 ** 6, -10 ** 6], [3, -1, 4, 1, -5, 9, 2, 6]]
        n = 0
        mism = []
        while n < 10000:
            t = rng.choice(pool)
            xs = rng.choice(inputs) if rng.random() < 0.3 else \
                [rng.randint(-25, 25) for _ in range(rng.randint(0, 10))]
            a = A.run(t, xs)
            b = fastc.runf(fastc.compile_term(t), xs)
            if a != b or type(a) is not type(b):
                mism.append((A.show(t), xs, a, b))
            n += 1
        self.assertEqual(mism[:5], [])


if __name__ == "__main__":
    unittest.main()
