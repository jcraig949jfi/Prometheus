"""Engine interface contract: init / step / save_state / load_state / digest (C-013-T022)."""
import unittest

from rso.scale.runner import engine as E
from rso.scale.runner.tests._util import AETHER, TOY, aether_params, toy_params


class EngineContract:
    runtime = None

    def params(self):
        raise NotImplementedError

    def setUp(self):
        self.eng = E.get_engine(self.runtime)
        self.p = self.params()

    def test_round_trip_bytes(self):
        s = self.eng.step(self.eng.init(self.p), 7)
        b = self.eng.save_state(s)
        self.assertIsInstance(b, bytes)
        self.assertEqual(self.eng.save_state(self.eng.load_state(self.p, b)), b)

    def test_split_run_equality(self):
        whole = self.eng.step(self.eng.init(self.p), 12)
        a = self.eng.step(self.eng.init(self.p), 5)
        a = self.eng.load_state(self.p, self.eng.save_state(a))       # through bytes, as a resume does
        split = self.eng.step(a, 7)
        self.assertEqual(self.eng.digest(whole), self.eng.digest(split))
        self.assertEqual(self.eng.save_state(whole), self.eng.save_state(split))

    def test_deterministic_and_seed_sensitive(self):
        d1 = self.eng.digest(self.eng.step(self.eng.init(self.p), 6))
        d2 = self.eng.digest(self.eng.step(self.eng.init(self.p), 6))
        self.assertEqual(d1, d2)
        q = dict(self.p, seed=self.p["seed"] + 1)
        self.assertNotEqual(d1, self.eng.digest(self.eng.step(self.eng.init(q), 6)))

    def test_digest_moves_with_steps(self):
        s0 = self.eng.init(self.p)
        self.assertNotEqual(self.eng.digest(s0), self.eng.digest(self.eng.step(s0, 3)))

    def test_load_refuses_garbage(self):
        b = self.eng.save_state(self.eng.init(self.p))
        with self.assertRaises(ValueError):
            self.eng.load_state(self.p, b[:-1])
        with self.assertRaises(ValueError):
            self.eng.load_state(self.p, b"XXXX" + b[4:])

    def test_probe_names_code(self):
        pr = self.eng.probe()
        self.assertIn("engine_files", pr)
        self.assertTrue(all(len(h) == 64 for h in pr["engine_files"].values()))


class TestToyEngine(EngineContract, unittest.TestCase):
    runtime = TOY

    def params(self):
        return toy_params()


class TestAetherEngine(EngineContract, unittest.TestCase):
    runtime = AETHER

    def params(self):
        return aether_params()

    def test_matches_kernel_run_world(self):
        """The adapter steps exactly what Aether's own driver steps (aeth01_run.run_world) -- read only."""
        from rso.scale.runner import aether as A
        R, G = A.aether_modules()
        p = self.p
        fields, _ = R.build_initial(p["regime"], p["h"], p["w"], p["rng_seed"], energy_mode=p["energy_mode"])
        params = {k: p[k] for k in ("h", "w", "seed", "write_cost", "maintenance_cost", "replenish_numer",
                                    "replenish_amount", "mut_numer")}
        import numpy as np
        _, _, _, meta = R.run_world(np, G.gpu_step, fields, params, 9, sample_every=10 ** 9,
                                    deep_every=10 ** 9, map_every=10 ** 9)
        s = self.eng.step(self.eng.init(p), 9)
        self.assertEqual(A.fields_digest(s), meta["final_state_digest"])

    def test_unknown_runtime(self):
        self.assertIsNone(E.lookup({"name": "nope", "version": 1}))
        with self.assertRaises(LookupError):
            E.get_engine({"name": "nope", "version": 1})


if __name__ == "__main__":
    unittest.main()
