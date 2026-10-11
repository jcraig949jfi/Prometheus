"""wforge F09 -- the affordability regression (Astra's review F09, operator ACCEPT "immediate stop condition";
design v0.3 s12 Lane B: Themis writes the red regression, the substrate owner fixes wforge).

Run from the repo root:  python -m unittest roles/Themis/handoffs/wforge_F09/test_wforge_affordability.py

The defect (SerendipityFoundry/worldfoundry/wforge/world.py, Encounter.step): when an action costs more than the slot's
charge, step() sets `mag, cost = 0, 0` ("forced abstain") but then queues writes from the ORIGINAL action vector, so
an unpaid action moves the world. The contract these tests encode (Astra: "an unaffordable action has the defined
abstention effect and cannot queue unpaid writes"; repair: "exercise over-budget, exactly affordable, delayed and
multi-channel actions against charged work"):

  RED now (define the fix):   an over-budget action -- single channel, delayed, multi-channel, and across a grid of
                              costs and charges -- leaves registers, charge and actions_used exactly as its
                              zero-action twin's, and queues nothing.
  GREEN now (guard the fix):  an affordable or EXACTLY affordable action is paid and its writes land.

Deliberately NOT asserted (the owner's semantics; see HANDOFF.md): whether a forced abstain increments `abstained`
(it does not today, a true abstain does), whether an exactly-affordable action may kill its slot that tick (it does
today: charge reaches 0), and that `mag` sums the whole action list while writes use only a[:act_width].
"""
import itertools
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "SerendipityFoundry" / "worldfoundry"))

from wforge.world import Encounter, Mechanics  # noqa: E402

M = 65536


def mech(*, act_cost=3, start_charge=1, delay=0, act_width=1, act_targets=(0,), n_regs=1, horizon=8, step_cost=0):
    """Astra's probe world: no transitions, no regime, no noise, no yield -- registers move only by actions."""
    return Mechanics(n_regs=n_regs, n_slots=1, horizon=horizon, lin_ops=[], regime_period=0, stoch_rate=0,
                     delay=delay, act_width=act_width, act_targets=list(act_targets), act_cost=act_cost,
                     step_cost=step_cost, yield_reg=0, yield_lo=0, yield_hi=1, yield_amt=0,
                     start_charge=start_charge, obs_perm=list(range(n_regs + 1)), obs_regs=list(range(n_regs)),
                     corrupt_rate=0, obs_delay=0, horizon_class="MICRO")


def twin_run(m, action, steps=1, world_id="review-underfunded", seed=0):
    """Step an actor with `action` once (then zero actions) and its zero-action twin for `steps` ticks."""
    zero = [0] * m.act_width
    a, b = Encounter(m, world_id, seed), Encounter(m, world_id, seed)
    for t in range(steps):
        a.step([action if t == 0 else zero])
        b.step([zero])
    return a, b


class TestUnpaidWritesAreImpossible(unittest.TestCase):
    """RED until F09 is fixed."""

    def assert_no_effect(self, a, b, what):
        self.assertEqual(a.regs, b.regs, "{}: an UNPAID action moved the registers (delta {} mod 65536)".format(
            what, [(x - y) % M for x, y in zip(a.regs, b.regs)]))
        self.assertEqual(a.charge, b.charge, what + ": charge differs from the zero-action twin")
        self.assertEqual(a.actions_used, b.actions_used, what + ": an unaffordable action was counted as used")
        self.assertEqual(a.pending, [], what + ": an unaffordable action left a queued write")

    def test_astras_probe(self):
        # charge 1, one action of magnitude 1 at cost 3 per unit: unaffordable
        a, b = twin_run(mech(), [1])
        self.assertEqual((a.charge, a.actions_used), ([1], [0]))       # what wforge already gets right
        self.assert_no_effect(a, b, "Astra's probe (cost 3 > charge 1)")

    def test_a_delayed_unpaid_write_never_lands(self):
        a, b = twin_run(mech(delay=2, horizon=8), [1], steps=4)          # past the landing tick
        self.assert_no_effect(a, b, "delayed (delay 2)")

    def test_multi_channel_unpaid_writes(self):
        m = mech(act_width=2, act_targets=(0, 1), n_regs=2, act_cost=1, start_charge=5)
        a, b = twin_run(m, [3, 4])                                       # magnitude 7 > charge 5
        self.assert_no_effect(a, b, "multi-channel (7 > 5)")

    def test_no_unaffordable_action_moves_the_world_across_a_grid(self):
        bad = []
        for cost, charge, amp, delay, width in itertools.product((1, 2, 3), (1, 2, 4, 6), range(1, 8), (0, 2),
                                                                 (1, 2)):
            m = mech(act_cost=cost, start_charge=charge, delay=delay, act_width=width,
                     act_targets=tuple(range(width)), n_regs=2)
            action = [amp] + [0] * (width - 1)
            if amp * cost <= charge:
                continue                                                 # affordable: the guards below
            a, b = twin_run(m, action, steps=delay + 2)
            if a.regs != b.regs or a.charge != b.charge or a.actions_used != b.actions_used:
                bad.append((cost, charge, amp, delay, width))
        self.assertEqual(bad, [], "{} unaffordable (cost, charge, magnitude, delay, width) cases moved the world; "
                                  "first {}".format(len(bad), bad[:5]))


class TestPaidActionsStillWork(unittest.TestCase):
    """GREEN now: guards against over-correcting the fix."""

    def test_an_affordable_action_is_paid_and_lands(self):
        a, b = twin_run(mech(act_cost=1, start_charge=10), [2])
        self.assertEqual((a.charge, a.actions_used), ([8], [2]))
        self.assertEqual([(x - y) % M for x, y in zip(a.regs, b.regs)], [2 * 251])

    def test_an_exactly_affordable_action_is_paid_and_lands(self):
        a, b = twin_run(mech(act_cost=3, start_charge=3), [1])            # cost == charge: affordable
        self.assertEqual((a.charge, a.actions_used), ([0], [1]))
        self.assertEqual([(x - y) % M for x, y in zip(a.regs, b.regs)], [251])

    def test_a_paid_delayed_write_lands_on_time(self):
        m = mech(act_cost=1, start_charge=10, delay=2)
        a, b = twin_run(m, [1], steps=2)
        self.assertEqual(a.regs, b.regs)                                 # not yet (lands at tick 2)
        a.step([[0]]); b.step([[0]])
        self.assertEqual([(x - y) % M for x, y in zip(a.regs, b.regs)], [251])

    def test_every_affordable_action_moves_the_world_by_its_paid_writes(self):
        for cost, charge, amp in itertools.product((1, 2, 3), (1, 2, 4, 6, 21), range(1, 8)):
            if amp * cost > charge:
                continue
            a, b = twin_run(mech(act_cost=cost, start_charge=charge), [amp])
            with self.subTest(cost=cost, charge=charge, amp=amp):
                self.assertEqual(a.charge, [charge - amp * cost])
                self.assertEqual([(x - y) % M for x, y in zip(a.regs, b.regs)], [amp * 251 % M])


if __name__ == "__main__":
    unittest.main()
