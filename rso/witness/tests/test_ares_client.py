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


def _zero_reward_world(name, mode):
    """An Ares world whose step reports reward 0 (observations, oracle and interrupts untouched)."""
    w = AR.make_world(name, mode)
    step = w.step

    def zero_step(a):
        obs, r, alive, info = step(a)
        return obs, np.zeros_like(r), alive, info
    w.step = zero_step
    return w


class TestRunner(unittest.TestCase):
    def test_runner_reproduces_ares_rollout_actions(self):
        # random organisms plus both carriers: an activation carrier's actions depend on W15's interrupts, so a
        # runner that skipped them would differ (a random population alone did not expose that; author mutant).
        # ACTION-ONLY reference (Palamedes #1746): rollout runs on a world whose reported rewards are zeroed, so
        # no accuracy or reward statistic is computed for any arm or control; the organism never observes reward
        # in W4/W15, so actions are unchanged. The fitness rollout returns is asserted to be exactly zero.
        for pop in (_random_pop(), AC.recur_carrier(), AC.pos_carrier()):
            fit, traces = AR.rollout(pop, _zero_reward_world("W15", "present"), SEEDS, record=True)
            self.assertFalse(np.any(fit))
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
        rec, arts = AC.receipt_dict(self.launch, "S", "P-RET", self.pop, SEEDS)
        for k in ("node_id", "subject", "arm", "predicate", "world", "seeds", "observer", "outputs", "oracle",
                  "execution", "code"):
            self.assertIn(k, rec)
        self.assertEqual(rec["subject"]["genome_sha256"], AC.genome_digest(self.pop))
        self.assertEqual([o["role"] for o in rec["outputs"]], ["trace:actions"])
        self.assertEqual([o["role"] for o in rec["oracle"]], ["oracle:regimes", "oracle:reset_steps"])


# --------------------------------------------------------------------------------------------------------
# C-010-T010: predicate-specific node executions returning artifact BYTES with layout (PREREGISTRATION s7).
# Plumbing on random / hand-wired organisms only; no count, accuracy or outcome on any registered arm.

def _decode(rec, arts, role):
    a = next(x for x in rec["outputs"] + rec["oracle"] if x["role"] == role)
    data = arts[a["sha256"]]
    if a["dtype"] == "json":
        return json.loads(data)
    return np.frombuffer(data, dtype=a["dtype"]).reshape(a["shape"])


import json  # noqa: E402  (used by _decode)


class TestNodeExecutionsWithArtifacts(unittest.TestCase):
    def setUp(self):
        self.launch = AC.Launch("launch-c010-test", code_commit="0" * 40)
        self.pop = _random_pop(P=1)

    def _check_listing(self, rec, arts):
        from rso.witness import run_witness as RW
        listed = RW.verify_artifacts(rec, arts)                      # the driver's own check: all named, nothing extra
        self.assertEqual(len(listed), len(rec["outputs"]) + len(rec["oracle"]))
        for a in rec["outputs"] + rec["oracle"]:
            self.assertIn("dtype", a)
            self.assertIn("shape", a)

    def test_roles_per_predicate_match_the_preregistration(self):
        roles = {"P-RET": (["trace:actions"], ["oracle:regimes", "oracle:reset_steps"]),
                 "P-CAL": (["trace:actions"], ["oracle:regimes", "oracle:reset_steps"]),
                 "P-CHAN": (["trace:actions"], ["oracle:regimes", "oracle:reset_steps"]),
                 "P-OBS": (["trace:actions_record", "trace:actions_norecord"], ["oracle:regimes", "oracle:reset_steps"]),
                 "P-ERASE": (["trace:probe_after_a", "trace:probe_after_b"], ["oracle:regimes"]),
                 "P-PRES": (["trace:pres_warm", "trace:pres_fresh"], ["oracle:regimes"])}
        seeds = {"P-ERASE": [s for t in AC.erase_probe_set()[:4] for s in t],
                 "P-PRES": [s for p in AC.pres_seed_set()[:4] for s in p]}
        for pred, (outs, orc) in roles.items():
            with self.subTest(predicate=pred):
                rec, arts = AC.receipt_dict(self.launch, "S", pred, self.pop, seeds.get(pred, SEEDS))
                self.assertEqual([o["role"] for o in rec["outputs"]], outs)
                self.assertEqual([o["role"] for o in rec["oracle"]], orc)
                self._check_listing(rec, arts)

    def test_episode_node_bytes_decode_to_the_run(self):
        rec, arts = AC.receipt_dict(self.launch, "S", "P-RET", self.pop, SEEDS)
        out = AC.run_episodes(self.pop, AC.world("W15", "present"), SEEDS)
        self.assertTrue(np.array_equal(_decode(rec, arts, "trace:actions"), out["actions"]))
        self.assertTrue(np.array_equal(_decode(rec, arts, "oracle:regimes"), out["regimes"]))
        self.assertEqual(_decode(rec, arts, "oracle:reset_steps"), out["reset_steps"])
        self.assertEqual(list(_decode(rec, arts, "trace:actions").shape), [len(SEEDS), 40, 1])

    def test_p_obs_node_runs_with_and_without_the_observer(self):
        rec, arts = AC.receipt_dict(self.launch, "POS", "P-OBS", self.pop, SEEDS)
        a, b = _decode(rec, arts, "trace:actions_record"), _decode(rec, arts, "trace:actions_norecord")
        self.assertEqual(a.shape, b.shape)
        self.assertEqual(rec["observer"], AC.OBSERVER_ID)

    def test_p_erase_node_on_a_leak_construction(self):
        from rso.witness.tests.test_ares_client import _leak_construction
        probes = AC.erase_probe_set()[:8]
        flat = [s for t in probes for s in t]
        sub = _leak_construction()
        rec_s, arts_s = AC.receipt_dict(self.launch, "S", "P-ERASE", sub, flat)
        rec_l, arts_l = AC.receipt_dict(self.launch, "S-LEAK", "P-ERASE", sub, flat)
        for rec, arts in ((rec_s, arts_s), (rec_l, arts_l)):
            self.assertEqual(list(_decode(rec, arts, "trace:probe_after_a").shape), [8, 40, 1])
            self.assertEqual(list(_decode(rec, arts, "oracle:regimes").shape), [8, 3])
        self.assertEqual(AC.paired_carryover_diffs(_decode(rec_s, arts_s, "trace:probe_after_a"),
                                                   _decode(rec_s, arts_s, "trace:probe_after_b")), 0)
        self.assertGreater(AC.paired_carryover_diffs(_decode(rec_l, arts_l, "trace:probe_after_a"),
                                                     _decode(rec_l, arts_l, "trace:probe_after_b")), 0)
        self.assertEqual(_decode(rec_s, arts_s, "oracle:regimes")[:, :2].tolist(), [[0, 1]] * 8)

    def test_p_pres_node_on_a_leak_construction(self):
        from rso.witness.tests.test_ares_client import _leak_construction
        flat = [s for p in AC.pres_seed_set()[:8] for s in p]
        sub = _leak_construction()
        rec_s, arts_s = AC.receipt_dict(self.launch, "S", "P-PRES", sub, flat)
        rec_l, arts_l = AC.receipt_dict(self.launch, "S-LEAK", "P-PRES", sub, flat)
        self.assertEqual(AC.paired_carryover_diffs(_decode(rec_s, arts_s, "trace:pres_warm"),
                                                   _decode(rec_s, arts_s, "trace:pres_fresh")), 0)
        self.assertGreater(AC.paired_carryover_diffs(_decode(rec_l, arts_l, "trace:pres_warm"),
                                                     _decode(rec_l, arts_l, "trace:pres_fresh")), 0)

    def test_malformed_probe_lists_are_refused(self):
        with self.assertRaises(ValueError):
            AC.receipt_dict(self.launch, "S", "P-ERASE", self.pop, [800000, 800003])      # not triples
        with self.assertRaises(ValueError):
            AC.receipt_dict(self.launch, "S", "P-PRES", self.pop, [850001])               # not pairs

    def test_driver_seam_takes_the_tuple(self):
        from rso.witness import run_witness as RW
        rec, arts = RW.node_artifacts(AC.receipt_dict, self.launch, "S", "P-RET", self.pop, SEEDS)
        self.assertEqual(len(RW.verify_artifacts(rec, arts)), 3)

    def test_produce_still_binds(self):
        node_id, run_id, data = self.launch.produce("S", "P-ERASE", self.pop,
                                                    [s for t in AC.erase_probe_set()[:2] for s in t])
        self.assertEqual(B.binding_reasons(node_id, run_id, data, self.launch.rows(), "launch-c010-test"), [])


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


# --------------------------------------------------------------------------------------------------------
# C-009-T018: P-ERASE probe set and P-PRES seed set. Plumbing on a hand-wired CONSTRUCTION only (not the subject,
# not a registered arm): it must register a difference when leaky and 0 when not. No accuracy statistic.

def _leak_construction():
    """Hand-wired test organism (not POS): h reads the cue (ch1) and the noise channel (ch0); a plastic edge from
    the constant channel (ch5) into h with rate 0.3; outputs read h with opposite signs."""
    cfg = S.Config()
    pop = S.Population(cfg, 1)
    n, h = cfg.n, S.OBS_DIM
    pop.alive[0, h] = True
    pop.op[0, h] = S.OPS.index("ADD")
    pop.W1[0, h, 1] = 1.0
    pop.W1[0, h, 0] = 0.5
    pop.R[0, h, 5] = 0.3
    pop.op[0, n - 2] = S.OPS.index("ADD"); pop.W1[0, n - 2, h] = -1.0
    pop.op[0, n - 1] = S.OPS.index("ADD"); pop.W1[0, n - 1, h] = 1.0
    return pop


class TestEraseProbesAndPresSeeds(unittest.TestCase):
    def test_probe_set_shape_balance_and_determinism(self):
        probes = AC.erase_probe_set()
        self.assertEqual(len(probes), AC.ERASE_N_PROBES)
        self.assertEqual(probes, AC.erase_probe_set())
        regime = AC.regime_of
        self.assertTrue(all(regime(a) == 0 and regime(b) == 1 for a, b, _ in probes))
        self.assertEqual(sorted(regime(p) for _, _, p in probes), [0] * 32 + [1] * 32)
        seeds = [s for t in probes for s in t]
        self.assertEqual(len(seeds), len(set(seeds)))                  # no seed reused within the set

    def test_seed_sets_are_disjoint_from_registered_ranges(self):
        used = set(s for t in AC.erase_probe_set() for s in t) | set(s for p in AC.pres_seed_set() for s in p)
        self.assertFalse(used & set(AR.EVAL_SEEDS))
        self.assertTrue(all(AC.ERASE_START <= s < AC.WITNESS_SEED_FLOOR for s in used))
        self.assertTrue(all(s >= 25_000 for s in used))                 # above balanced_seeds_for's scan range

    def test_exclusion_list_is_honoured(self):
        first = AC.erase_probe_set()
        banned = {first[0][0], first[3][2]}
        again = AC.erase_probe_set(exclude=banned)
        self.assertFalse(banned & set(s for t in again for s in t))
        self.assertEqual(len(again), AC.ERASE_N_PROBES)

    def test_erase_probe_registers_a_leak_and_zero_without_one(self):
        pop, probes = _leak_construction(), AC.erase_probe_set()
        self.assertEqual(AC.p_erase_count(pop, S.Runtime, probes), 0)
        self.assertGreater(AC.p_erase_count(pop, AC.LeakyResetRuntime, probes), 0)

    def test_erase_probe_is_zero_for_a_runtime_with_no_plasticity_even_when_leaky(self):
        pop = _leak_construction()
        pop.R[:] = 0.0                                                  # nothing to leak: the fire case cannot fire
        self.assertEqual(AC.p_erase_count(pop, AC.LeakyResetRuntime, AC.erase_probe_set()), 0)

    def test_pres_seed_set_and_diffs(self):
        pairs = AC.pres_seed_set()
        self.assertEqual(len(pairs), AC.PRES_N_SEEDS)
        self.assertEqual(pairs, AC.pres_seed_set())
        pop = _leak_construction()
        self.assertEqual(AC.p_pres_diffs(pop, S.Runtime, pairs), 0)
        self.assertGreater(AC.p_pres_diffs(pop, AC.LeakyResetRuntime, pairs), 0)


if __name__ == "__main__":
    unittest.main()
