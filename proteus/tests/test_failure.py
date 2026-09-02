"""Failure tests: invalid manifests die cheaply and loudly; budgets bind; deaths are recorded, not dropped."""
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from proteus.foundry import generate, probes  # noqa: E402
from proteus.foundry.prng import SplitMix64  # noqa: E402
from proteus.foundry.vm import Player, Meter, ManifestError, validate_manifest, SCHEMA  # noqa: E402
from proteus.foundry.qualify import qualify, FailureLedger  # noqa: E402


def _good():
    return {"schema_version": SCHEMA, "n_regs": 4, "tape_words": 32, "genome": [0] * 8,
            "code_writable": False, "persist": "none", "tick_budget": 64, "out_cap": 4}


class Failure(unittest.TestCase):
    def test_bad_manifests_fail_closed(self):
        bad = []
        m = _good(); m["genome"] = [0] * 7; bad.append(m)                 # not multiple of 4
        m = _good(); m["genome"] = [0] * 64; bad.append(m)                # longer than tape
        m = _good(); m["tape_words"] = 30; bad.append(m)                  # not multiple of 4
        m = _good(); m["n_regs"] = 1; bad.append(m)                       # below bound
        m = _good(); m["genome"] = [1 << 32] * 8; bad.append(m)           # word out of range
        m = _good(); m["genome"] = ["x"] * 8; bad.append(m)               # not integers
        m = _good(); m["persist"] = "forever"; bad.append(m)              # unknown policy
        m = _good(); m["extra"] = 1; bad.append(m)                        # unknown field
        m = _good(); del m["out_cap"]; bad.append(m)                      # missing field
        m = _good(); m["code_writable"] = 1; bad.append(m)                # bool as int
        m = _good(); m["schema_version"] = "other"; bad.append(m)
        for m in bad:
            with self.assertRaises(ManifestError):
                validate_manifest(m)

    def test_budget_binds_on_infinite_loop(self):
        m = _good()
        m["genome"] = [18, 0, 0, 0] * 2   # JMP +0: spin forever
        p = Player(m)
        st = p.fresh_state()
        meter = Meter()
        t0 = time.perf_counter()
        outs, status = p.run_tick(st, [], 1, SplitMix64(1), meter)
        self.assertEqual(status, "budget")
        self.assertEqual(meter.ops, 64)
        self.assertLess(time.perf_counter() - t0, 0.05)

    def test_budget_never_exceeds_manifest(self):
        m = _good()
        m["genome"] = [18, 0, 0, 0] * 2
        p = Player(m)
        meter = Meter()
        p.run_tick(p.fresh_state(), [], 1, SplitMix64(1), meter, budget=10 ** 6)
        self.assertEqual(meter.ops, 64)

    def test_protected_genome_ignores_writes(self):
        m = _good()
        # LDC r0 = 5 ; LDC r1 = 0 ; ST tape[r1] = r0 ; HALT  -> tries to overwrite instruction 0
        m["genome"] = [3, 0, 5, 0, 3, 1, 0, 0, 6, 1, 0, 0, 1, 0, 0, 0]
        p = Player(m)
        st = p.fresh_state()
        p.run_tick(st, [], 1, SplitMix64(1))
        self.assertEqual(st["tape"][0], 3)
        m["code_writable"] = True
        p = Player(m)
        st = p.fresh_state()
        p.run_tick(st, [], 1, SplitMix64(1))
        self.assertEqual(st["tape"][0], 5)

    def test_output_cap_drops_and_counts(self):
        m = _good()
        m["out_cap"] = 2
        m["genome"] = [23, 0, 0, 0] * 2   # OUT r0 -> ch r0 ; wraps forever
        p = Player(m)
        meter = Meter()
        outs, status = p.run_tick(p.fresh_state(), [], 1, SplitMix64(1), meter)
        self.assertEqual(len(outs[0]), 2)
        self.assertEqual(meter.out_writes, 2)
        self.assertGreater(meter.out_dropped, 0)

    def test_qualification_deaths_are_recorded_and_cheap(self):
        fm = dict(generate.DEFAULT_FOUNDRY_MANIFEST)
        fm["seed"] = 77
        fm["n"] = 30
        pop = generate.generate(fm)
        # corrupt two manifests after generation: they must die at qualification, not crash it
        pop[3] = dict(pop[3]); pop[3]["manifest"] = dict(pop[3]["manifest"]); pop[3]["manifest"]["n_regs"] = 99
        pop[9] = dict(pop[9]); pop[9]["manifest"] = dict(pop[9]["manifest"]); pop[9]["manifest"]["genome"] = [1, 2, 3]
        ledger = FailureLedger()
        pr = probes.build_probes()
        alive = qualify(pop, pr, probes.DEFAULT_ENSEMBLE, ledger)
        self.assertEqual(len(alive), 28)
        self.assertEqual(len(ledger.rows), 2)
        self.assertEqual({r["organism_index"] for r in ledger.rows}, {3, 9})
        for r in ledger.rows:
            self.assertEqual(r["failure_class"], "MANIFEST_INVALID")
            self.assertLess(r["cost"]["wall_s"], 0.01)
        # ledger is append-only: rows carry a running hash chain
        self.assertEqual(ledger.rows[1]["prev_hash"], ledger.rows[0]["row_hash"])

    def test_runtime_mismatch_dies_at_qualification(self):
        fm = dict(generate.DEFAULT_FOUNDRY_MANIFEST)
        fm["seed"] = 78
        fm["n"] = 3
        pop = generate.generate(fm)
        pop[1] = dict(pop[1]); pop[1]["runtime_hash"] = "f" * 64
        ledger = FailureLedger()
        alive = qualify(pop, probes.build_probes(), probes.DEFAULT_ENSEMBLE, ledger)
        self.assertEqual(len(alive), 2)
        self.assertEqual(ledger.rows[0]["failure_class"], "RUNTIME_MISMATCH")


if __name__ == "__main__":
    unittest.main()
