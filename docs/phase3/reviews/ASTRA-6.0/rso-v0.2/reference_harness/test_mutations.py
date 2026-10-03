"""Five real single-source faults; only assertion failures count as kills."""

from pathlib import Path
import sys
from types import ModuleType
import unittest

import checker
import test_contracts as contracts


class SourceMutationTests(unittest.TestCase):
    def run_mutant(self, name, old, new, probe):
        baseline = unittest.TestResult()
        contracts.ContractTests(probe).run(baseline)
        self.assertEqual(baseline.testsRun, 1)
        self.assertEqual(baseline.errors, [])
        self.assertEqual(baseline.failures, [])
        self.assertEqual(baseline.skipped, [])
        source = Path(checker.__file__).read_text(encoding="ascii")
        self.assertEqual(source.count(old), 1, "mutation target must be unique")
        mutant_source = source.replace(old, new, 1)
        module_name = "_finite_contract_mutant_" + name
        module = ModuleType(module_name)
        self.assertNotIn(module_name, sys.modules)
        sys.modules[module_name] = module  # Required by dataclasses, not a disk import.
        try:
            exec(compile(mutant_source, "<" + module_name + ">", "exec"), module.__dict__)
            case = type("MutatedContractTests", (contracts.ContractTests,), {"api": module})
            outcome = unittest.TestResult()
            case(probe).run(outcome)
            self.assertEqual(outcome.testsRun, 1)
            self.assertEqual(outcome.errors, [], "crashes do not count as semantic kills")
            self.assertEqual(outcome.skipped, [])
            self.assertEqual(len(outcome.failures), 1, "mutant must fail a contract assertion")
        finally:
            del sys.modules[module_name]

    def test_missing_facet_passes(self):
        self.run_mutant("missing_facet", "if missing:", "if False and missing:",
                        "test_missing_facet")

    def test_ignores_external_binding(self):
        self.run_mutant("ignores_binding", "if node != anchors[node.artifact.key]:",
                        "if False and node != anchors[node.artifact.key]:", "test_whole_graph_relabel")

    def test_bypasses_repair_cold(self):
        self.run_mutant("repair_cold", 'if facet == "cold" and lineage != (0,):',
                        'if False and facet == "cold" and lineage != (0,):',
                        "test_repair_cannot_be_cold")

    def test_skips_digest_comparison(self):
        self.run_mutant("digest", "if sha256(data).hexdigest() != ref.digest:",
                        "if False and sha256(data).hexdigest() != ref.digest:",
                        "test_artifact_digest")

    def test_only_direct_invalidation(self):
        self.run_mutant("direct_invalidation", "if set(n.deps) & bad}",
                        "if set(n.deps) & seeds}", "test_transitive_invalidation")


if __name__ == "__main__":
    unittest.main()