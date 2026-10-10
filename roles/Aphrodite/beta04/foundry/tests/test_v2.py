"""E1 v2 specific tests: regression bank provenance, affine-in-accumulator screen, primitive extraction, arm-view
redaction, nearest-input lookup, order-free rank."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fastc                 # noqa: E402
import generator as G        # noqa: E402
import interp_a as A         # noqa: E402
import nulls as N            # noqa: E402
import qualify2 as Q         # noqa: E402
import regress               # noqa: E402
import tenum                 # noqa: E402


class Bank(unittest.TestCase):
    def test_bank_uses_only_config_ops(self):
        b = regress.bank_summary(G.CONFIG)
        ops = set(G.CONFIG["mech_pcfg"]["ops"]) | set(G.CONFIG["mech_pcfg"]["cmp_ops"])
        names = b["phi"] + [k.split(":", 1)[1] for k in b["single_keys"] if ":" in k]
        for name in names:
            for tok in name.replace("(", " ").replace(")", " ").split():
                self.assertTrue(tok in ops or tok == "x" or tok.lstrip("-").isdigit(), (name, tok))
        self.assertEqual(b["stats"], G.CONFIG["readouts_int"])

    def test_bank_deterministic(self):
        self.assertEqual(regress.bank_summary(G.CONFIG)["sha256"], regress.bank_summary(G.CONFIG)["sha256"])


class Screen(unittest.TestCase):
    def test_affine_in_acc(self):
        aff = fastc.compile_term(A.parse("(add (sub 6 a) (mul b b))"))
        mul = fastc.compile_term(A.parse("(sub (mul a b) 1)"))
        self.assertTrue(G.affine_in_acc(aff))
        self.assertFalse(G.affine_in_acc(mul))


class Extraction(unittest.TestCase):
    def test_extract(self):
        cases = [("(map (lam x (add (mul x x) 3)) xs)", "f", "(lam x (add (mul x x) 3))"),
                 ("(sub (pow (max xs) 3) (max xs))", "f", "(lam x (sub (pow x 3) x))"),
                 ("(foldl (lam a (lam b (sub (mul a b) 1))) 0 xs)", "s", "(lam a (lam b (sub (mul a b) 1)))"),
                 ("(len (filter (lam x (gt x 2)) xs))", "p", "(lam x (gt x 2))"),
                 ("(add (max xs) (min xs))", "f", None)]
        for src, k, want in cases:
            lam, _how = Q.extract_primitive(A.parse(src), k)
            self.assertEqual(A.show(lam) if lam else None, want, src)


class Redaction(unittest.TestCase):
    def test_arm_view_fields(self):
        r = {"family_id": "Wx-F001-R3", "rung": "R3", "dev": [[[1, 2], 3]], "test": [[[4], 5]], "witness": "w",
             "tribunal": [], "index": 1}
        a = Q.arm_json(Q.opaque("secret-seed", r["family_id"]), r)
        self.assertEqual(set(a), {"id", "dev"})
        s = json.dumps(a)
        for leak in ("R3", "secret-seed", "Wx-F001", "witness", "test", "tribunal"):
            self.assertNotIn(leak, s)

    def test_opaque_depends_on_secret(self):
        self.assertNotEqual(Q.opaque("s1", "F"), Q.opaque("s2", "F"))
        self.assertEqual(len(Q.opaque("s1", "F")), 16)


class Misc(unittest.TestCase):
    def test_nearest_lookup(self):
        dev = [[[1, 2, 3], 10], [[9, 9], 20], [[0], 30]]
        test = [[[1, 2, 4], 10], [[9, 8], 20], [[1], 30]] * 11
        res = N.run_closed_form(dev, test)
        self.assertTrue(res["lookup"]["solved"])

    def test_order_free_rank(self):
        self.assertEqual(tenum.order_free_rank({1: 4, 2: 10}, 3, est_next=100), (14 + 50.5, True))
        self.assertEqual(tenum.order_free_rank({1: 4, 2: 10}, 2), (4 + 5.5, False))


if __name__ == "__main__":
    unittest.main()
