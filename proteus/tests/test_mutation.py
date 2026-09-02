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
                           "grammar_hash", "record_id"}


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

    def test_grammar_hash_frozen_in_prereg(self):
        path = os.path.join(ROOT, "proteus", "v0", "NEUTRALITY_PREREG.json")
        if not os.path.exists(path):
            self.skipTest("neutrality prereg not yet written")
        with open(path, encoding="utf-8") as f:
            prereg = json.load(f)
        self.assertEqual(prereg["grammar_hash"], grammar.GRAMMAR_HASH)

    def test_static_reachability_basic(self):
        # HALT at instruction 0: only instruction 0 reachable
        g = [1, 0, 0, 0] + [7, 0, 0, 0] * 3
        self.assertEqual(grammar.static_reachable(g, 64), {0})
        # JMP +2 from 0 skips instruction 1
        g = [18, 0, 2, 0] + [7, 0, 0, 0] + [7, 0, 0, 0] + [1, 0, 0, 0]
        self.assertEqual(grammar.static_reachable(g, 64), {0, 2, 3})


if __name__ == "__main__":
    unittest.main()
