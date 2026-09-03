"""Mutation tests: every operator yields a valid manifest, lineage records are complete,
subtraction exists with more mass than addition, and the neutrality gate is wired to its prereg."""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from proteus.foundry import generate, grammar, lineage  # noqa: E402
from proteus.foundry.prng import SplitMix64  # noqa: E402
from proteus.foundry.vm import validate_manifest  # noqa: E402

REQUIRED_LINEAGE_FIELDS = {"schema_version", "organism_id", "lineage_id", "generation", "parent_ids",
                           "mutation_seed", "operators", "pre_hash", "post_hash",
                           "state_inheritance_policy", "resource_budget", "runtime_hash",
                           "grammar_hash", "grammar_version", "record_id"}


def _pop(seed, n):
    fm = dict(generate.DEFAULT_FOUNDRY_MANIFEST)
    fm["seed"] = seed
    fm["n"] = n
    return generate.generate(fm)


class Mutation(unittest.TestCase):
    def test_every_operator_yields_valid_manifest(self):
        pop = _pop(31, 60)
        for i, o in enumerate(pop):
            for name in grammar.NAMES:
                child, rec = grammar.mutate(o["manifest"], SplitMix64(i * 131 + hash(name) % 997),
                                            pop[(i + 7) % 60]["manifest"], name)
                validate_manifest(child)
                self.assertEqual(rec["operator"], name)

    def test_operators_at_bounds_stay_in_bounds(self):
        fm = dict(generate.DEFAULT_FOUNDRY_MANIFEST)
        fm["seed"] = 1
        fm["n"] = 10
        fm["genome_instr_range"] = [1, 1]
        tiny = generate.generate(fm)
        fm["genome_instr_range"] = [256, 256]
        fm["tape_words_choices"] = [1024]
        full = generate.generate(fm)
        for pop in (tiny, full):
            for i, o in enumerate(pop):
                for name in grammar.NAMES:
                    child, _ = grammar.mutate(o["manifest"], SplitMix64(i), pop[(i + 1) % 10]["manifest"], name)
                    validate_manifest(child)

    def test_lineage_record_complete(self):
        pop = _pop(8, 5)
        child, rec = lineage.descend(pop[0], 42, mate=pop[1])
        self.assertEqual(set(rec.keys()), REQUIRED_LINEAGE_FIELDS)
        self.assertEqual(rec["parent_ids"], [pop[0]["organism_id"], pop[1]["organism_id"]])
        self.assertEqual(rec["pre_hash"], pop[0]["organism_id"])
        self.assertEqual(rec["post_hash"], child["organism_id"])
        self.assertEqual(child["lineage_id"], pop[0]["lineage_id"])
        self.assertEqual(child["generation"], 1)
        validate_manifest(child["manifest"])

    def test_subtraction_mass_exceeds_addition_mass(self):
        w = dict(zip(grammar.NAMES, grammar.WEIGHTS))
        adds = w["insertion"] + w["duplication"]
        subs = w["deletion"] + w["unreachable_removal"]
        self.assertGreater(subs, adds)

    def test_operator_descriptions_free_of_cognition_language(self):
        banned = ("search", "plan", "match", "attention", "analog", "strateg", "hierarch",
                  "special", "communicat", "goal", "learn", "reason", "memory")
        for name, _, desc in grammar.OPERATORS:
            low = (name + " " + desc).lower()
            for b in banned:
                self.assertNotIn(b, low, f"operator {name} description contains '{b}'")

    def test_active_grammar_hash_frozen_in_prereg(self):
        path = os.path.join(ROOT, "proteus", "v0_4", "PREREG_V0_4.json")
        if not os.path.exists(path):
            self.skipTest("v0.3 prereg not yet written")
        with open(path, encoding="utf-8") as f:
            prereg = json.load(f)
        self.assertEqual(prereg["grammar_hash"], grammar.GRAMMAR_HASH)
        self.assertEqual(prereg["grammar_version"], grammar.GRAMMAR_VERSION)

    def test_frozen_evidence_pins_are_intact(self):
        """The v0/v0.1/v0.2 preregs and results must keep pointing at the grammars that made them."""
        v0 = os.path.join(ROOT, "proteus", "v0")
        for fn, expect in (("NEUTRALITY_PREREG_grammar_v0_2.json", grammar.GRAMMAR_HASH_V0_2),
                           ("NEUTRALITY_RESULT_grammar_v0_2_FAIL.json", grammar.GRAMMAR_HASH_V0_2)):
            with open(os.path.join(v0, fn), encoding="utf-8") as f:
                self.assertEqual(json.load(f)["grammar_hash"], expect, fn)
        for fn in ("NEUTRALITY_RESULT_grammar_v0_FAIL.json", "NEUTRALITY_RESULT_grammar_v0_1_FAIL.json"):
            with open(os.path.join(v0, fn), encoding="utf-8") as f:
                self.assertNotEqual(json.load(f)["grammar_hash"], grammar.GRAMMAR_HASH, fn)
        # the V0.3 preregistration and adjudication must still pin the v0.3 grammar
        p3 = os.path.join(ROOT, "proteus", "v0_3", "PREREG_V0_3.json")
        with open(p3, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["grammar_hash"], grammar.GRAMMAR_HASH_V0_3)
        a3 = os.path.join(ROOT, "proteus", "v0_3", "ADJUDICATION_V0_3.json")
        with open(a3, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["grammar_hash"], grammar.GRAMMAR_HASH_V0_3)

    def test_zeroing_removed_and_renormalization_is_mechanical(self):
        self.assertEqual(len(grammar.OPERATORS), 12)
        self.assertNotIn("zeroing", grammar.NAMES)
        self.assertNotIn("zeroing", grammar.IMPL)
        self.assertIn("reference_redirection", grammar.NAMES)
        self.assertAlmostEqual(sum(grammar.WEIGHTS), 1.0, places=12)
        survivors = [o for o in grammar.OPERATORS_V0_2 if o[0] != "zeroing"]
        self.assertEqual([o[0] for o in survivors], list(grammar.NAMES))
        for (n, w, d), (n2, w2, d2) in zip(survivors, grammar.OPERATORS):
            self.assertEqual(n, n2)
            self.assertEqual(d, d2)
            self.assertAlmostEqual(w2, w / 0.96, places=12)
        with self.assertRaises(KeyError):
            grammar.mutate(_pop(1, 1)[0]["manifest"], SplitMix64(1), None, "zeroing")

    def test_v0_2_grammar_still_executable_for_evidence(self):
        pop = _pop(3, 3)
        child, rec = lineage.descend(pop[0], 1, mate=pop[1],
                                     grammar_version=grammar.GRAMMAR_VERSION_V0_2)
        self.assertEqual(rec["grammar_hash"], grammar.GRAMMAR_HASH_V0_2)
        c2, r2 = lineage.descend(pop[0], 1, mate=pop[1],
                                 grammar_version=grammar.GRAMMAR_VERSION_V0_2)
        self.assertEqual(child["organism_id"], c2["organism_id"])

    def test_static_reachability_basic(self):
        # HALT at instruction 0: only instruction 0 reachable
        g = [1, 0, 0, 0] + [7, 0, 0, 0] * 3
        self.assertEqual(grammar.static_reachable(g, 64), {0})
        # JMP +2 from 0 skips instruction 1
        g = [18, 0, 2, 0] + [7, 0, 0, 0] + [7, 0, 0, 0] + [1, 0, 0, 0]
        self.assertEqual(grammar.static_reachable(g, 64), {0, 2, 3})


if __name__ == "__main__":
    unittest.main()
