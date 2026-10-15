"""C-019-T011: the measurement table is computed from runner rows, and its catalog names only variants that exist.
(Written after the first implementation pass; the RED run in RED_OUTPUT.txt covers the attacks / targets / mutants tests.)"""
import unittest

from rso.adversary import measurement as MS, targets as T


def row(target, attack, variant, verdict, limitation=None):
    return dict(target=target, attack=attack, variant=variant, verdict=verdict, limitation=limitation, detail="", fired=True)


class Classify(unittest.TestCase):
    def test_rejected_is_yes_limitation_and_survived_are_no(self):
        rows = [row("t", "DROP", "a", "REJECTED"), row("t", "REWRITE_DERIVED", "b", "LIMITATION", "C018-R1c"),
                row("t", "DUPLICATE", "c", "SURVIVED")]
        self.assertEqual(MS.classify(rows, ("t", "DROP", "a"))[0], "yes")
        self.assertEqual(MS.classify(rows, ("t", "REWRITE_DERIVED", "b")), ("no", "LIMITATION C018-R1c"))
        self.assertEqual(MS.classify(rows, ("t", "DUPLICATE", "c"))[0], "no")

    def test_a_prefix_group_is_yes_only_if_every_member_is_rejected(self):
        rows = [row("t", "DROP", "shard-0", "REJECTED"), row("t", "DROP", "shard-1", "SURVIVED")]
        self.assertEqual(MS.classify(rows, ("t", "DROP", "shard-"))[0], "no")

    def test_no_variant_is_not_covered_and_a_missing_variant_is_an_error(self):
        self.assertEqual(MS.classify([], None)[0], "not covered")
        with self.assertRaises(KeyError):
            MS.classify([row("t", "DROP", "a", "REJECTED")], ("t", "DROP", "zzz"))


class Catalog(unittest.TestCase):
    def test_every_mapped_defect_names_a_registered_variant(self):
        for hid, _c, _d, _s, key, _n in MS.CATALOG:
            if key is None:
                continue
            target, attack, prefix = key
            self.assertTrue(any(a == attack and v.startswith(prefix) for a, v, _f in T.TARGETS[target]["variants"]), hid)

    def test_ids_are_unique_and_unmapped_defects_say_why(self):
        ids = [c[0] for c in MS.CATALOG]
        self.assertEqual(len(ids), len(set(ids)))
        for c in MS.CATALOG:
            if c[4] is None:
                self.assertTrue(c[5], c[0])

    def test_catalog_spans_at_least_three_previous_generations(self):
        self.assertGreaterEqual(len({c[1] for c in MS.CATALOG}), 3)

    def test_render_contains_the_reviewer_template(self):
        text, t = MS.render([row(k[0], k[1], k[2], "REJECTED") for *_x, k, _n in MS.CATALOG if k])
        self.assertIn("Reviewer template", text)
        self.assertIn("cost per new defect class", text)


if __name__ == "__main__":
    unittest.main()
