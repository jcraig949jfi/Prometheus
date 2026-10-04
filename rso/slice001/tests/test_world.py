"""Tests for rso/slice001/world.py (C-004-T010): world W-S1 of CONTRACT.md draft A A2-A4.

The expected values here come from the frozen contract (contract.json reset_model, draft A A2, A4), not from
running world.py. The checker's history convention (rso/slice001/checker.py u_of / f_of) is cross-checked
because the T016 adapter emits traces in that order.
Python >= 3.8, standard library only.
"""
import json
import os
import unittest
from fractions import Fraction

from rso.slice001 import checker as CK
from rso.slice001 import world as W

CONTRACT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "contract", "contract.json")


def _reset_model():
    with open(CONTRACT, "r", encoding="utf-8") as f:
        return json.load(f)["reset_model"]


class Reg(W.Runtime):
    """Sound reference (draft A A6 REG): a := u, d := f; reset clears d and the channel, keeps a."""

    def on_cue(self, u, f):
        self.a, self.d = u, f

    def reset(self):
        self.d = 0
        self.chan = []


class Pktd(Reg):
    """Sound reference with a non-empty channel mid-episode (draft A A6 PKTD): display sent with k = 0."""

    def on_cue(self, u, f):
        self.a = u
        self.send(f, 0)


class Lagd(Reg):
    """Display-only erase (draft A A6 LAGD): sends (f, 1), reset clears d only."""

    def on_cue(self, u, f):
        self.a, self.d = u, f
        self.send(f, 1)

    def reset(self):
        self.d = 0


class CountingResets(Reg):
    def __init__(self):
        Reg.__init__(self)
        self.calls = 0

    def reset(self):
        Reg.reset(self)
        self.calls += 1


class TestRegisteredModel(unittest.TestCase):
    def test_constants_equal_contract_reset_model(self):
        rm = _reset_model()
        self.assertEqual(W.EPISODES, rm["episodes_per_life"])
        self.assertEqual(W.RESET_CALLS, rm["reset_calls_per_life"])
        self.assertEqual(list(W.BOUNDARIES), rm["evaluated_boundaries"])
        self.assertEqual(W.R, rm["repeat_count_R"])
        self.assertEqual(W.H, rm["delay_horizon_H_episodes"])
        self.assertEqual(W.K, rm["max_channel_delay_K_episodes"])
        self.assertEqual(W.S, rm["sends_per_cue_S"])
        self.assertEqual(W.Q, rm["channel_capacity_Q"])
        self.assertEqual(list(W.TICKS), rm["ticks"])
        self.assertEqual(W.HISTORIES, rm["histories"])
        self.assertEqual(len(W.SCHEDULE_POINTS), rm["restart_cut_points"])
        self.assertEqual(list(W.RESTORE_TARGETS), rm["restore_targets"])

    def test_registered_model_does_not_block_closure(self):
        self.assertEqual(W.closure_blockers(_reset_model()), [])

    def test_delay_longer_than_horizon_blocks_closure(self):
        rm = dict(_reset_model(), max_channel_delay_K_episodes=4)
        blockers = W.closure_blockers(rm)
        self.assertEqual(len(blockers), 1)
        self.assertIn("delay K=4 exceeds horizon H=3", blockers[0])

    def test_four_episode_life_truncates_the_horizon(self):
        # FD-A1: with L = 4 the horizon after boundary 3 is one episode, shorter than K = 3.
        rm = dict(_reset_model(), episodes_per_life=4, reset_calls_per_life=3)
        blockers = W.closure_blockers(rm)
        self.assertTrue(any("boundary 2" in b for b in blockers))
        self.assertTrue(any("boundary 3" in b for b in blockers))
        self.assertFalse(any("boundary 1" in b for b in blockers))


class TestDomain(unittest.TestCase):
    def test_history_count_and_distinct_inputs(self):
        seen = {W.inputs(h) for h in W.histories()}
        self.assertEqual(len(list(W.histories())), 4096)
        self.assertEqual(len(seen), 4096)
        self.assertEqual(W.domain_summary()["histories"], 4096)

    def test_history_order_matches_checker(self):
        for h in W.histories():
            for e in range(1, 7):
                self.assertEqual(W.u_of(h, e), CK.u_of(h, e))
                self.assertEqual(W.f_of(h, e), CK.f_of(h, e))
                self.assertEqual(W.u_of(h, e, "CLOCKED"), CK.u_of(h, e, "CLOCKED"))

    def test_canonical_order_is_lexicographic_in_u1_f1_to_u6_f6(self):
        self.assertEqual(W.inputs(0), ((0, 0),) * 6)
        self.assertEqual(W.inputs(1), ((0, 0),) * 5 + ((0, 1),))
        self.assertEqual(W.inputs(2048), ((1, 0),) + ((0, 0),) * 5)
        self.assertEqual(W.inputs(4095), ((1, 1),) * 6)
        ordered = [W.inputs(h) for h in W.histories()]
        self.assertEqual(ordered, sorted(ordered))

    def test_complement(self):
        for h in (0, 1, 1234, 4095):
            self.assertEqual(W.inputs(W.complement(h)),
                             tuple((1 - u, 1 - f) for u, f in W.inputs(h)))

    def test_unknown_variant_refused(self):
        with self.assertRaises(ValueError):
            W.inputs(0, "WARPED")


class TestTruthModel(unittest.TestCase):
    def test_retained_truth_is_u_j_and_display_truth_is_f_e(self):
        for h in (0, 77, 2730, 4095):
            t = W.truth(h)
            self.assertEqual(t["retained"], {j: W.u_of(h, j) for j in (1, 2, 3)})
            self.assertEqual(t["display"], {e: W.f_of(h, e) for e in range(1, 7)})

    def test_u_j_balanced(self):
        for j in (1, 2, 3):
            self.assertEqual(W.ones(j), 2048)
        self.assertEqual(sum(W.ones(j) for j in (1, 2, 3)), 6144)

    def test_clocked_overrides_u_at_evaluated_boundaries_only(self):
        for h in (0, 4095, 1365):
            t = W.truth(h, "CLOCKED")
            self.assertEqual(t["retained"], {1: 1, 2: 0, 3: 1})
            self.assertEqual(W.u_of(h, 4, "CLOCKED"), W.u_of(h, 4))

    def test_no_carry_class_has_eight_policies_each_exactly_one_half(self):
        pols = W.no_carry_policies()
        self.assertEqual(len(pols), 8)
        self.assertEqual(len(set(pols)), 8)
        for p in pols:
            self.assertEqual(W.no_carry_success(p), Fraction(1, 2))

    def test_clocked_world_lets_a_no_carry_policy_answer_perfectly(self):
        best = max(W.no_carry_success(p, "CLOCKED") for p in W.no_carry_policies())
        self.assertEqual(best, Fraction(1))


class TestScheduleAndChannel(unittest.TestCase):
    def test_schedule_points(self):
        pts = W.SCHEDULE_POINTS
        self.assertEqual(len(pts), 29)
        self.assertEqual(pts[0], ("TICK", 1, "DELIVER"))
        self.assertEqual(pts[4], ("RESET", 1))
        self.assertEqual(pts[-1], ("TICK", 6, "PROBE_D"))
        self.assertEqual(sum(1 for p in pts if p[0] == "RESET"), 5)

    def test_reset_called_five_times_per_life(self):
        made = []

        def make():
            made.append(CountingResets())
            return made[-1]
        W.run_life(make, 0)
        self.assertEqual(made[0].calls, 5)

    def test_reset_at_controls_which_boundaries_reset(self):
        made = []

        def make():
            made.append(CountingResets())
            return made[-1]
        W.run_life(make, 0, reset_at=frozenset({1, 3}))
        self.assertEqual(made[0].calls, 2)

    def test_outputs_of_the_sound_register(self):
        h = 0b10_01_11_00_01_10     # (1,0) (0,1) (1,1) (0,0) (0,1) (1,0)
        rec = W.run_life(Reg, h)
        self.assertEqual([rec.probe_a(e) for e in range(1, 7)],
                         [(0, 0), (1, 0), (0, 0), (1, 0), (0, 0), (0, 0)])
        self.assertEqual([rec.probe_d(e) for e in range(1, 7)], [0, 1, 1, 0, 1, 0])
        self.assertEqual(len(rec.outputs), 24)

    def test_delay_zero_arrives_at_probe_d_of_the_same_episode(self):
        h = 0b01_00_01_00_01_00
        rec = W.run_life(Pktd, h)
        self.assertEqual([rec.probe_d(e) for e in range(1, 7)], [1, 0, 1, 0, 1, 0])
        self.assertEqual(rec.deliveries(3), ((), (1,)))
        self.assertEqual(rec.sends(3), ((1, 0),))

    def test_delay_one_arrives_at_deliver_of_the_next_episode(self):
        h = 0b01_00_00_00_00_00     # f_1 = 1
        rec = W.run_life(Lagd, h)
        self.assertEqual(rec.deliveries(2), ((1,), ()))
        self.assertEqual(rec.probe_a(2), (0, 1))         # display after the reset shows the forbidden bit
        self.assertEqual(rec.deliveries(1), ((), ()))

    def test_delay_three_and_undelivered_sends(self):
        class Lag3(Reg):
            def on_cue(self, u, f):
                Reg.on_cue(self, u, f)
                self.send(self.ep % 2, 3)

            def reset(self):
                self.d = 0            # leaves the channel, so delayed packets survive the resets
        made = []

        def make():
            made.append(Lag3())
            return made[-1]
        rec = W.run_life(make, 0)
        self.assertEqual(rec.deliveries(4), ((1,), ()))   # sent in episode 1 (ep % 2 = 1)
        self.assertEqual(rec.deliveries(6), ((1,), ()))   # sent in episode 3
        self.assertEqual(len(made[0].chan), 3)            # sent in 4, 5, 6: due after the life

    def test_reachable_channel_maximum_is_six_not_q(self):
        # Correction to draft A A2 "Q = S x (K + 1), the reachable maximum": with S = 2 and K = 3 at most 6
        # packets are ever in flight, so Q = 8 never binds from send() alone.
        class Flood(Reg):
            peak = 0

            def on_cue(self, u, f):
                self.send(u, 3)
                self.send(f, 3 if self.ep % 2 else 2)
                Flood.peak = max(Flood.peak, len(self.chan))

            def reset(self):
                pass
        W.run_life(Flood, 4095)
        self.assertEqual(Flood.peak, 6)


class TestBounds(unittest.TestCase):
    def test_delay_outside_range(self):
        class Over(Reg):
            def on_cue(self, u, f):
                self.send(f, 4)
        with self.assertRaises(W.BoundsViolation) as cm:
            W.run_life(Over, 0)
        self.assertEqual(cm.exception.bound, "DELAY_RANGE")
        self.assertEqual(str(cm.exception), "runtime outside the registered model: DELAY_RANGE at (1, CUE)")

    def test_too_many_sends(self):
        class Chatty(Reg):
            def on_cue(self, u, f):
                for _ in range(3):
                    self.send(f, 0)
        with self.assertRaises(W.BoundsViolation) as cm:
            W.run_life(Chatty, 0)
        self.assertEqual(cm.exception.bound, "SENDS_PER_CUE")

    def test_capacity_through_restore(self):
        r = Reg()
        c = r.capture()
        c["chan"] = tuple((9, "DELIVER", 0) for _ in range(9))
        with self.assertRaises(W.BoundsViolation) as cm:
            r.restore(c)
        self.assertEqual(cm.exception.bound, "CHANNEL_CAPACITY")

    def test_output_alphabet(self):
        class Two(Reg):
            def answer(self):
                return 2
        with self.assertRaises(W.BoundsViolation) as cm:
            W.run_life(Two, 0)
        self.assertEqual(cm.exception.bound, "OUTPUT_ALPHABET")
        self.assertEqual(str(cm.exception), "runtime outside the registered model: OUTPUT_ALPHABET at (1, PROBE_A)")

    def test_registered_runtimes_stay_inside_the_bounds(self):
        for M in (Reg, Pktd, Lagd):
            for h in (0, 1365, 2730, 4095):
                W.run_life(M, h)


class TestInterface(unittest.TestCase):
    def test_declared_components(self):
        d = Reg().declare()
        self.assertEqual({k: v["class"] for k, v in d.items()},
                         {"a": "ALLOWED", "d": "FORBIDDEN", "chan": "FORBIDDEN", "ep": "SCHEDULE",
                          "log_n": "BOOKKEEPING"})
        self.assertEqual(d["a"]["initial"], 0)
        self.assertEqual(d["chan"]["initial"], ())

    def test_capture_contains_every_declared_component_and_round_trips(self):
        r = Pktd()
        r.step("DELIVER")
        r.step("PROBE_A")
        r.step("CUE", (1, 1))
        c = r.capture()
        self.assertTrue(set(r.declare()) <= set(c))
        t = Pktd()
        t.restore(c)
        self.assertEqual(t.capture(), c)
        self.assertEqual(t.step("PROBE_D"), r.step("PROBE_D"))

    def test_capture_is_a_copy(self):
        r = Lagd()
        r.step("DELIVER")
        r.step("PROBE_A")
        r.step("CUE", (0, 1))
        c = r.capture()
        r.chan.clear()
        self.assertEqual(len(c["chan"]), 1)

    def test_hook_sees_every_schedule_point_and_may_replace_the_runtime(self):
        seen = []

        def hook(rt, point):
            seen.append(point)
            if point == ("RESET", 2):
                fresh = Pktd()
                fresh.restore(rt.capture())
                return fresh
            return rt
        a = W.run_life(Pktd, 1234)
        b = W.run_life(Pktd, 1234, hook=hook)
        self.assertEqual(tuple(seen), W.SCHEDULE_POINTS)
        self.assertEqual(a.outputs, b.outputs)

    def test_skipped_reset_still_reports_its_schedule_point(self):
        seen = []
        W.run_life(Reg, 0, reset_at=frozenset({2}), hook=lambda rt, p: seen.append(p) or rt)
        self.assertEqual(tuple(seen), W.SCHEDULE_POINTS)


if __name__ == "__main__":
    unittest.main()
