"""C-010-T013: the witness config generator. Plumbing only: two TINY subject runs (P=4, G=1) stand in for the
registered ones; no count, accuracy or outcome is computed."""
import json
import os
import shutil
import tempfile
import unittest

from rso.witness import ares_client as AC
from rso.witness import make_configs as MC
from rso.witness import run_witness as RW


class TestMakeConfigs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="mkcfg-")
        cls.s4 = os.path.join(cls.tmp, "S4")
        cls.s15 = os.path.join(cls.tmp, "S15")
        RW.run_subject("W4", "present", {}, 4, 1, 2, 11, cls.s4)
        RW.run_subject("W15", "present", {}, 4, 1, 2, 12, cls.s15)
        cls.out = os.path.join(cls.tmp, "configs")
        cls.summary = MC.build(cls.s4, cls.s15, cls.out)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_three_configs_pass_the_driver_validation(self):
        for label in ("CONTROLS", "S4", "S15"):
            plan = RW.load_config(os.path.join(self.out, self.summary["configs"][label]))
            self.assertEqual(plan["label"], label)
        self.assertEqual(len(RW.load_config(os.path.join(self.out, "config_S4.json"))["plan"]), 6)
        self.assertEqual(len(RW.load_config(os.path.join(self.out, "config_CONTROLS.json"))["plan"]), 4)

    def test_witness_seeds_balanced_and_above_floor(self):
        w = self.summary["seeds"]["witness"]
        self.assertEqual(len(w), 2048)
        self.assertEqual(len(set(w)), 2048)
        self.assertEqual(self.summary["witness_r1"], 1024)
        self.assertTrue(all(s >= AC.WITNESS_SEED_FLOOR for s in w))

    def test_every_ga_episode_seed_and_eval_seed_is_excluded(self):
        used = set(self.summary["seeds"]["witness"]) | set(self.summary["seeds"]["erase"]) | set(self.summary["seeds"]["pres"])
        for d in (self.s4, self.s15):
            rec = json.load(open(os.path.join(d, "subject_record.json")))
            self.assertFalse(used & set(rec["episode_seeds"]))
        self.assertFalse(used & set(int(s) for s in RW.AR.EVAL_SEEDS))

    def test_exclusion_is_honoured_when_a_ga_seed_falls_in_the_witness_range(self):
        first = MC.seed_lists({})["witness"][0]
        again = MC.seed_lists({first: "test"})["witness"]
        self.assertNotIn(first, again)
        self.assertEqual(len(again), 2048)

    def test_s_and_s_nopl_share_seeds_in_order(self):
        cfg = json.load(open(os.path.join(self.out, "config_S15.json")))
        by = {(e["arm"], e["predicate"]): e["seeds"] for e in cfg["entries"]}
        self.assertEqual(by[("S", "P-RET")], by[("S-NOPL", "P-CHAN")])
        self.assertEqual(len(by[("S", "P-ERASE")]) % 3, 0)
        self.assertEqual(len(by[("S", "P-PRES")]) % 2, 0)

    def test_deterministic(self):
        out2 = os.path.join(self.tmp, "configs2")
        MC.build(self.s4, self.s15, out2)
        self.assertEqual(json.load(open(os.path.join(self.out, "WITNESS_SEEDS.json"))), self.summary["seeds"]["witness"])
        for name in ("SEED_LISTS.json", "WITNESS_SEEDS.json", "config_CONTROLS.json", "config_S4.json", "config_S15.json"):
            self.assertEqual(open(os.path.join(self.out, name), "rb").read(), open(os.path.join(out2, name), "rb").read(), name)



class TestPairingByPredicate(unittest.TestCase):
    """C-010-T013 integration fix in run_witness.load_config: S-NOPL pairs with S's P-RET node even when S also
    runs other predicates on other seeds (the registered S4/S15 configs)."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="pair-")
        RW.run_subject("W4", "present", {}, 4, 1, 2, 13, os.path.join(self.tmp, "S"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _cfg(self, entries):
        p = os.path.join(self.tmp, "c.json")
        json.dump({"schema": RW.CONFIG_SCHEMA, "label": "pair", "world": "W15", "entries": [
            {"subject": "S/genome.json", "arm": a, "predicate": pr, "seeds": s} for a, pr, s in entries]}, open(p, "w"))
        return p

    def test_other_s_predicates_do_not_break_the_pairing(self):
        RW.load_config(self._cfg([("S", "P-RET", [901, 902]), ("S-NOPL", "P-CHAN", [901, 902]),
                                  ("S", "P-PRES", [850001, 850002])]))

    def test_s_nopl_must_match_s_p_ret_even_if_another_s_entry_matches(self):
        with self.assertRaises(RW.WitnessError):
            RW.load_config(self._cfg([("S", "P-RET", [901, 902]), ("S-NOPL", "P-CHAN", [903, 904]),
                                      ("S", "P-PRES", [903, 904])]))


if __name__ == "__main__":
    unittest.main()
