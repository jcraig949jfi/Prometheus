from dataclasses import FrozenInstanceError, fields
from fractions import Fraction as F
from itertools import product
import unittest

import finite as f


class FiniteTests(unittest.TestCase):
    def test_retention_no_carry_and_donor(self):
        self.assertEqual(f.bit_answers("carry"), (0, 1))
        self.assertEqual(f.bit_answers("reset"), (0, 0))
        self.assertEqual(f.bit_answers("flip"), (1, 0))
        self.assertEqual(f.detector_counts(), (2, 1, 0))
        self.assertEqual(f.recovery((0, 0), (0,)), F(1, 2))
        self.assertEqual(f.recovery((0, 0), (1,)), F(1, 2))
        donor_hits = sum(donor == key for key, donor in product((0, 1), repeat=2))
        self.assertEqual(F(donor_hits, 4), F(1, 2))
        # A post-boundary cue exposes the key and voids the no-carry premise.
        self.assertEqual(sum(key == cue for key, cue in ((0, 0), (1, 1))), 2)

    def test_exact_channel_class(self):
        self.assertEqual(f.channel_optimum(4, 1), F(1, 4))
        self.assertEqual(f.channel_optimum(4, 2), F(1, 2))
        self.assertEqual(f.recovery((0, 1, 2, 3), (0, 1, 2, 3)), 1)
        # Separately enumerate the successful-key set, without calling recovery.
        counts = [sum(k in {d[e[k]]} for k in range(4))
                  for e in product(range(2), repeat=4) for d in product(range(4), repeat=2)]
        self.assertEqual(len(counts), 256)
        self.assertEqual(max(counts), 2)
        for channels, expected in ((1, F(1, 4)), (2, F(1, 2)), (4, F(1))):
            self.assertEqual(f.channel_bound(4, channels), expected)

    def test_plateau_valley_and_repair(self):
        for policy in ("strict", "nondecreasing"):
            self.assertEqual(f.search((0, 1, 2), 0, policy).hit_step, 2)
            self.assertIsNone(f.search((0, -1, 1), 0, policy).hit_step)
        strict = f.search((0, 0, 1), 0, "strict")
        self.assertEqual((strict.proposals, strict.states), ((1, 1), (0, 0, 0)))
        self.assertEqual(f.search((0, 0, 1), 0, "nondecreasing").hit_step, 2)
        self.assertEqual(f.search((0, -1, 1), 0, "enumerate").states, (0, 1, 2))
        self.assertEqual(f.search((0, -1, 1), 1, "strict").hit_step, 1)
        self.assertIsNone(f.search((0, -1, 1), 0, "enumerate", 1).hit_step)

    def test_continuation_missing_checkpoint_bit(self):
        states = ((0, 0), (1, 0), (0, 1), (1, 1))
        expected = ((0, 1), (1, 1), (1, 0), (0, 0))
        self.assertEqual(tuple(f.continuation(tuple(s)) for s in states), expected)
        broken = tuple(f.continuation((0, c)) for q, c in states)
        self.assertEqual(tuple(i for i in range(4) if broken[i] != expected[i]), (1, 3))

    def test_reset_clean_twin_and_reachable_leak(self):
        for allowed in (0, 1):
            twins = [f.BoundaryState(allowed, secret, (secret,)) for secret in (0, 1)]
            clean = [s.clean_reset().tick().observe() for s in twins]
            leaky = [s.leaky_reset().tick().observe() for s in twins]
            self.assertEqual(clean, [(allowed, 0), (allowed, 0)])
            self.assertEqual(leaky, [(allowed, 0), (allowed, 1)])
            # Perfect checkpoint continuation still preserves the forbidden packet.
            self.assertEqual([f.BoundaryState(s.allowed, s.displayed, s.pending).tick().observe()
                              for s in twins], leaky)
        erased = f.BoundaryState(0, 0, ()).tick().observe()
        self.assertNotEqual(erased, f.BoundaryState(1, 1, (1,)).clean_reset().tick().observe())

    def test_reencoding_witness_not_cross_physics(self):
        for encoding in ("plain", "one_hot"):
            self.assertEqual(tuple(f.read_bit(f.encode_bit(b, encoding), encoding) for b in (0, 1)), (0, 1))
        self.assertEqual(tuple(f.biased_ruler(f.encode_bit(b, "plain")) for b in (0, 1)), (0, 1))
        self.assertEqual(tuple(f.biased_ruler(f.encode_bit(b, "one_hot")) for b in (0, 1)), (1, 0))

    def test_updater_fresh_targets_freeze_flatten_and_r0(self):
        hits = r0_hits = 0
        for beta, x in product((1, 2), repeat=2):
            v = f.History.learn(((1, beta), (2, 2 * beta)))
            u = v.build(x)
            self.assertEqual(tuple(field.name for field in fields(u)), ("eta",))
            self.assertEqual(u.eta, F(1, beta * x))
            with self.assertRaises(FrozenInstanceError):
                u.eta = F(1)
            del v
            answers = []
            for y in (-1, 1):
                g = f.task_gradient(beta * x, y)
                answer = u.step(0, g)
                answers.append(answer)
                self.assertEqual(answer, y)
                self.assertEqual(f.flattened(beta, x, g), answer)
                self.assertEqual(u.step(0, 0), 0)
                self.assertEqual(u.eta, F(1, beta * x))
                hits += answer == y
                r0_hits += f.sign_gradient_r0(g) == y
            self.assertEqual(answers, [-1, 1])
        self.assertEqual((hits, r0_hits, hits - r0_hits), (8, 8, 0))

    def test_clamp_swap_and_disconnection_mediation(self):
        histories = [f.History.learn(((1, beta),)) for beta in (1, 2)]
        updaters = [v.build(1) for v in histories]
        self.assertEqual([u.step(0, -2) for u in updaters], [2, 1])
        self.assertEqual([u.step(0, -2) for u in reversed(updaters)], [1, 2])
        clamp = f.Updater(F(1, 2))
        self.assertEqual([clamp.step(0, -2) for _ in histories], [1, 1])
        # A deliberate open V bypass destroys that fixed-U invariance.
        bypass = [clamp.step(0, -2) + v.beta for v in histories]
        self.assertEqual(bypass, [2, 3])
        del histories
        self.assertEqual([u.step(0, -2) for u in updaters], [2, 1])

    def test_finite_input_validation(self):
        for bad in (True, 0, 5, 1.0):
            with self.assertRaises(ValueError):
                f.channel_bound(bad, 1)
        with self.assertRaises(ValueError):
            f.History.learn(((1, 1), (2, 3)))
        with self.assertRaises(ValueError):
            f.task_gradient(1, True)


if __name__ == "__main__":
    unittest.main()