"""C-019-T011 RED-first: the kit has teeth. rso.slice001.mutation (registry entry mutation-runner) applies single-line mutants to
rso/completeness/verify.py; the Z80 attack suite (SuiteZ80Attacks below) must FAIL on each, i.e. the kit would have flagged the
regression. A kit whose attacks pass against a broken verifier is the vacuous test the directive warns about.
    python -m unittest rso.adversary.tests.test_mutants -v"""
import os
import tempfile
import unittest

from rso.adversary import core as K, mutants as MU
from rso.slice001 import mutation


class SuiteZ80Attacks(unittest.TestCase):
    """The suite the mutation runner executes against each mutant: DROP and DUPLICATE on the Z80 fixture must be REJECTED."""
    def test_z80_drop_and_duplicate_rejected(self):
        rows = K.run_target("z80_completeness")
        bad = [(r["attack"], r["variant"], r["verdict"]) for r in rows
               if r["attack"] in ("DROP", "DUPLICATE") and r["verdict"] != K.REJECTED]
        self.assertEqual(bad, [])


class MutantsAreKilled(unittest.TestCase):
    def test_edits_file_is_valid_and_every_find_text_occurs_once(self):
        edits, _ = mutation.load_edits(MU.EDITS_PATH)
        self.assertGreaterEqual(len(edits), 4)
        src = {}
        for e in edits:
            text = src.setdefault(e["path"], open(os.path.join(MU.ROOT, e["path"]), encoding="utf-8").read())
            self.assertEqual(text.count(e["find"]), 1, e["edit_id"])

    def test_the_kit_kills_the_verifier_mutants(self):
        with tempfile.TemporaryDirectory() as d:
            out = MU.run_mutants(os.path.join(d, "rows.jsonl"), require_committed=False)
        s = out["summary"]
        self.assertEqual(out["baseline"][0]["status"], "PASSED")
        self.assertEqual(s["survived"], 0, out["edits"])
        self.assertEqual(s["killed"], s["executed"])
        self.assertGreaterEqual(s["killed"], 4)


if __name__ == "__main__":
    unittest.main()
