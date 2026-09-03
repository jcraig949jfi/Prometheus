"""Replay tests: same seed + same runtime => byte-identical population, transcripts, children."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from proteus.foundry import generate, probes, lineage, identity, signatures  # noqa: E402
from proteus.foundry.prng import SplitMix64  # noqa: E402
from proteus.foundry.vm import Player, Meter  # noqa: E402


def _fm(seed, n):
    fm = dict(generate.DEFAULT_FOUNDRY_MANIFEST)
    fm["seed"] = seed
    fm["n"] = n
    return fm


class Replay(unittest.TestCase):
    def test_population_is_bit_identical_under_same_seed(self):
        a = generate.generate(_fm(11, 300))
        b = generate.generate(_fm(11, 300))
        self.assertEqual([o["manifest"] for o in a], [o["manifest"] for o in b])
        self.assertEqual([o["organism_id"] for o in a], [o["organism_id"] for o in b])

    def test_different_seed_differs(self):
        a = generate.generate(_fm(11, 50))
        b = generate.generate(_fm(12, 50))
        self.assertNotEqual([o["organism_id"] for o in a], [o["organism_id"] for o in b])

    def test_transcript_replays_exactly(self):
        pop = generate.generate(_fm(3, 40))
        pr = probes.build_probes()
        for o in pop:
            _, h1 = probes.run_ensemble(o["manifest"], pr)
            _, h2 = probes.run_ensemble(o["manifest"], pr)
            self.assertEqual(h1, h2)

    def test_knockout_signature_replays_exactly(self):
        pop = generate.generate(_fm(5, 10))
        pr = probes.build_probes()
        for o in pop:
            s1 = signatures.signatures(o["manifest"], pr, probes.DEFAULT_ENSEMBLE)
            s2 = signatures.signatures(o["manifest"], pr, probes.DEFAULT_ENSEMBLE)
            self.assertEqual(s1["knockout_vector"], s2["knockout_vector"])
            self.assertEqual(s1["transcript_class"], s2["transcript_class"])

    def test_descent_replays_exactly(self):
        pop = generate.generate(_fm(9, 20))
        for i, o in enumerate(pop):
            c1, r1 = lineage.descend(o, 1000 + i, mate=pop[(i + 1) % 20])
            c2, r2 = lineage.descend(o, 1000 + i, mate=pop[(i + 1) % 20])
            self.assertEqual(c1["organism_id"], c2["organism_id"])
            self.assertEqual(r1["record_id"], r2["record_id"])

    def test_checkpoint_restore_continues_identically(self):
        pop = generate.generate(_fm(21, 30))
        pr = probes.build_probes()
        probe = pr[0]
        for o in pop:
            p = Player(o["manifest"])
            st = p.fresh_state()
            rng = SplitMix64(probe["rnd_seed"])
            first = [p.run_tick(st, probe["inputs"][t], probe["n_out"], rng, None, 128) for t in range(2)]
            snap = lineage.checkpoint(o["organism_id"], st, "enc-test", 2)
            rng_state = rng.state
            rest = [p.run_tick(st, probe["inputs"][t], probe["n_out"], rng, None, 128) for t in range(2, probe["ticks"])]
            st2 = lineage.restore(snap)
            rng2 = SplitMix64(0)
            rng2.state = rng_state
            rest2 = [p.run_tick(st2, probe["inputs"][t], probe["n_out"], rng2, None, 128) for t in range(2, probe["ticks"])]
            self.assertEqual(rest, rest2)
            self.assertEqual(st, st2)
            del first

    def test_runtime_mismatch_refused(self):
        pop = generate.generate(_fm(2, 1))
        p = Player(pop[0]["manifest"])
        snap = lineage.checkpoint(pop[0]["organism_id"], p.fresh_state(), None, 0)
        snap["runtime_hash"] = "0" * 64
        with self.assertRaises(ValueError):
            lineage.restore(snap)

    def test_runtime_identity_is_platform_independent(self):
        rid = identity.runtime_identity()
        self.assertEqual(rid["runtime_hash"], identity.RUNTIME_HASH)
        self.assertEqual(len(rid["runtime_hash"]), 64)

    def test_meter_is_a_vector_without_fitness(self):
        pop = generate.generate(_fm(4, 5))
        pr = probes.build_probes()
        m = Meter()
        probes.run_ensemble(pop[0]["manifest"], pr, probes.DEFAULT_ENSEMBLE, m)
        d = m.as_dict(pop[0]["manifest"])
        self.assertNotIn("fitness", d)
        for k in ("ops", "wall_s", "cpu_s", "footprint_words", "persistent_state_words",
                  "proxy_search_expenditure", "proxy_adaptation_expenditure", "gpu"):
            self.assertIn(k, d)


if __name__ == "__main__":
    unittest.main()
