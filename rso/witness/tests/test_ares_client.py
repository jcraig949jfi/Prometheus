"""Plumbing tests for rso/witness/ares_client.py (C-009-T013).

SELECTION.md gate: no subject evolution, no witness predicate on Ares output, no accuracy or retention number for any
arm or control. These tests check mechanics only -- runner fidelity, determinism, that each arm wrapper is applied
(on internal state), observer neutrality, receipts and binding rows. Predicate count functions are exercised on
SYNTHETIC arrays only. Python >= 3.8; numpy.
"""
import unittest

import numpy as np

from ares import search as AR
from ares import substrate as S
from rso.binding import binding as B
from rso.witness import ares_client as AC

SEEDS = [101, 102, 103, 104]


def _random_pop(P=6, seed=7):
    return S.random_population(S.Config(), P, np.random.default_rng(seed))


class TestRunner(unittest.TestCase):
    def test_runner_reproduces_ares_rollout_actions(self):
        # random organisms plus both carriers: an activation carrier's actions depend on W15's interrupts, so a
        # runner that skipped them would differ (a random population alone did not expose that; author mutant)
        for pop in (_random_pop(), AC.recur_carrier(), AC.pos_carrier()):
            _, traces = AR.rollout(pop, AR.make_world("W15", "present"), SEEDS, record=True)
            mine = AC.run_episodes(pop, AC.world("W15", "present"), SEEDS)
            self.assertTrue(np.array_equal(mine["actions"], np.stack(traces["actions"])))

    def test_interrupts_reach_the_runtime(self):
        # internal state, not accuracy: right after an interrupt step the hidden activations are zero
        zero_after = []
        out = AC.run_episodes(AC.recur_carrier(), AC.world("W15", "present"), SEEDS[:1],
                              observer=lambda t, rt: zero_after.append((t, not np.any(rt.v[:, S.OBS_DIM:]))))
        hits = [z for t, z in zero_after if t in set(out["reset_steps"][0])]
        self.assertEqual(hits, [True] * 4)

    def test_deterministic_under_fixed_seeds(self):
        pop = _random_pop()
        a = AC.run_episodes(pop, AC.world("W15", "present"), SEEDS)
        b = AC.run_episodes(pop, AC.world("W15", "present"), SEEDS)
        for k in ("actions", "regimes", "shown"):
            self.assertTrue(np.array_equal(a[k], b[k]), k)
        self.assertEqual(a["reset_steps"], b["reset_steps"])

    def test_runner_returns_no_reward_or_fitness(self):
        out = AC.run_episodes(_random_pop(), AC.world("W15", "present"), SEEDS)
        self.assertEqual(sorted(out), ["actions", "regimes", "reset_steps", "shown"])

    def test_observer_does_not_change_actions(self):
        pop = AC.pos_carrier()
        seen = []
        quiet = AC.run_episodes(pop, AC.world("W15", "present"), SEEDS)
        watched = AC.run_episodes(pop, AC.world("W15", "present"), SEEDS, observer=lambda t, rt: seen.append(
            (rt.v.copy(), rt.W1.copy())))
        self.assertTrue(np.array_equal(quiet["actions"], watched["actions"]))
        self.assertEqual(len(seen), len(SEEDS) * AC.world("W15", "present").T)


class TestArmsApplied(unittest.TestCase):
    """Each wrapper checked on internal state, never on accuracy."""

    def test_arm_table(self):
        self.assertEqual(AC.ARMS, ("S", "S-NOPL", "S-LEAK", "POS", "RECUR", "NULL", "SHUF"))
        for name in AC.ARMS:
            pop, mode, rt_cls = AC.arm(name, _random_pop(P=1))
            self.assertIn(mode, ("present", "shuffled"))
            self.assertTrue(issubclass(rt_cls, S.Runtime))

    def test_s_leak_leaves_plastic_w1_unrestored(self):
        pop = AC.pos_carrier()
        for rt_cls, restored in ((S.Runtime, True), (AC.LeakyResetRuntime, False)):
            rt = rt_cls(pop)
            AC.run_episodes(pop, AC.world("W15", "present"), SEEDS[:1], runtime=rt)
            self.assertFalse(np.array_equal(rt.W1, pop.W1))          # plasticity wrote during the life
            rt.reset()
            self.assertEqual(np.array_equal(rt.W1, pop.W1), restored, rt_cls.__name__)
            self.assertFalse(np.any(rt.v))                           # both zero activations

    def test_s_nopl_has_no_plastic_update(self):
        pop, _, rt_cls = AC.arm("S-NOPL", AC.pos_carrier())
        self.assertFalse(np.any(pop.R))
        rt = rt_cls(pop)
        self.assertFalse(rt.plastic)
        AC.run_episodes(pop, AC.world("W15", "present"), SEEDS[:1], runtime=rt)
        self.assertTrue(np.array_equal(rt.W1, pop.W1))

    def test_null_resets_activations_every_step(self):
        pop, _, _ = AC.arm("NULL", _random_pop(P=1))
        self.assertTrue(pop.cfg.reset_each_step)

    def test_shuf_decouples_shown_cue_from_regime(self):
        _, mode, _ = AC.arm("SHUF", _random_pop(P=1))
        out = AC.run_episodes(_random_pop(P=1), AC.world("W15", mode), list(range(200, 240)))
        self.assertTrue(np.any(out["shown"] != out["regimes"]))
        present = AC.run_episodes(_random_pop(P=1), AC.world("W15", "present"), list(range(200, 240)))
        self.assertTrue(np.array_equal(present["shown"], present["regimes"]))

    def test_hand_wired_carriers_are_wired_as_declared(self):
        pos = AC.pos_carrier()
        self.assertTrue(np.any(pos.R))                                # a plastic edge
        rec = AC.recur_carrier()
        h = S.OBS_DIM
        self.assertNotEqual(rec.W1[0, h, h], 0.0)                     # the activation self-loop
        self.assertFalse(np.any(rec.R))

    def test_w15_interrupts_exist_and_are_recorded(self):
        out = AC.run_episodes(_random_pop(P=1), AC.world("W15", "present"), SEEDS)
        self.assertTrue(all(len(s) == 4 for s in out["reset_steps"]))


class TestReceiptsAndBinding(unittest.TestCase):
    def setUp(self):
        self.pop = _random_pop(P=1)
        self.launch = AC.Launch("launch-test-1", code_commit="0" * 40)
        self.produced = [self.launch.produce(arm, "P-OBS", self.pop, SEEDS) for arm in AC.ARMS]

    def test_every_produced_receipt_binds(self):
        rows = self.launch.rows()
        for node_id, run_id, data in self.produced:
            self.assertEqual(B.binding_reasons(node_id, run_id, data, rows, "launch-test-1"), [], node_id)

    def test_a_tampered_receipt_does_not_bind(self):
        node_id, run_id, data = self.produced[0]
        bad = data.replace(b'"seeds"', b'"seedz"')
        self.assertIn(B.DIGEST_MISMATCH, B.binding_reasons(node_id, run_id, bad, self.launch.rows(), "launch-test-1"))

    def test_a_receipt_presented_under_another_launch_does_not_bind(self):
        node_id, run_id, data = self.produced[0]
        rows = self.launch.rows() + [{"kind": "RUN", "run_id": "launch-B", "launch_kind": "TOP_LEVEL",
                                      "node_id": "G0", "status": "COMPLETED"}]
        self.assertIn(B.FOREIGN_LAUNCH, B.binding_reasons(node_id, run_id, data, rows, "launch-B"))

    def test_receipts_are_canonical_float_free_and_deterministic(self):
        again = AC.Launch("launch-test-1", code_commit="0" * 40).produce("S", "P-OBS", self.pop, SEEDS)
        self.assertEqual(again[2], self.produced[0][2])
        import json
        from rso.slice001 import receipt as R
        obj = json.loads(again[2])
        self.assertEqual(R.canonical_bytes(obj), again[2])               # canonical (refuses floats)
        self.assertEqual(len({p[0] for p in self.produced}), len(AC.ARMS))   # one opaque node id per arm

    def test_receipt_records_subject_world_seeds_observer_outputs_oracle(self):
        rec = AC.receipt_dict(self.launch, "S", "P-OBS", self.pop, SEEDS)
        for k in ("node_id", "subject", "arm", "predicate", "world", "seeds", "observer", "outputs", "oracle",
                  "execution", "code"):
            self.assertIn(k, rec)
        self.assertEqual(rec["subject"]["genome_sha256"], AC.genome_digest(self.pop))
        self.assertEqual([o["role"] for o in rec["outputs"]], ["trace:actions"])
        self.assertEqual([o["role"] for o in rec["oracle"]], ["oracle:regimes", "oracle:reset_steps"])


class TestPredicateCountsOnSyntheticArrays(unittest.TestCase):
    """Count functions only; no thresholds (Argus, C-009-T014) and never on Ares arm output here."""

    def test_post_interrupt_counts(self):
        # 2 episodes, T = 6, P = 2; regime 1 means good action 2; last interrupt at step 3
        actions = np.array([[[2, 0]] * 6, [[1, 2]] * 6], dtype=np.int8)
        regimes = np.array([1, 0])
        correct, total = AC.post_interrupt_counts(actions, regimes, [{1, 3}, {2, 3}])
        self.assertEqual(total.tolist(), [4, 4])
        self.assertEqual(correct.tolist(), [2 + 2, 0 + 0])

    def test_paired_carryover_diffs(self):
        # the same probe episode after two different preceding episodes; any difference is carry-over
        after_a = np.zeros((5, 2), dtype=np.int8)
        after_b = after_a.copy(); after_b[0, 1] = 2; after_b[3, 1] = 1
        self.assertEqual(AC.paired_carryover_diffs(after_a, after_a.copy()), 0)
        self.assertEqual(AC.paired_carryover_diffs(after_a, after_b), 2)

    def test_actions_equal(self):
        a = np.ones((2, 3, 1), dtype=np.int8)
        self.assertTrue(AC.actions_equal(a, a.copy()))
        b = a.copy(); b[1, 2, 0] = 0
        self.assertFalse(AC.actions_equal(a, b))


if __name__ == "__main__":
    unittest.main()
