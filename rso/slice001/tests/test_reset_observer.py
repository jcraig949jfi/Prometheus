"""Tests for reset.py and observer.py (C-004-T011): ERASE, PRESERVE, CHANNEL, RESTART, OBSERVER on world W-S1.

Expected values come from CONTRACT.md draft A A5-A7 and the independent table
(rso/slice001/expected/EXPECTED_ANSWERS.json, rows T03-T08), not from running these predicates.
Three kinds of check:
  - case outcomes: every sound fixture accepted, every broken fixture rejected with the contract's reason;
  - fire tests (rso-builder-role s2.4): a deliberately naive predicate stub PASSES each broken fixture, so
    the real predicate's FAIL is not a property any check would have;
  - producer/consumer agreement: ERASE, PRESERVE and CHANNEL equal checker.recompute_* on traces built
    from the same runs (value, eligible_count, applicable_count, witness).
Expensive outcomes are computed once per module (RESTART is ~237568 continuations per runtime).
Python >= 3.8, standard library only.
"""
import unittest

from rso.slice001 import checker as CK
from rso.slice001 import observer as OB
from rso.slice001 import reset as RS
from rso.slice001 import world as W
from rso.slice001.fixtures import world_cases as WC

_cache = {}


def outcome(pred, name, obs=None):
    key = (pred, name, obs)
    if key not in _cache:
        make = WC.RUNTIMES[name]
        if pred == "OBSERVER":
            _cache[key] = OB.observer(make, WC.OBSERVERS[obs], obs)
        else:
            _cache[key] = getattr(RS, pred.lower())(make)
    return _cache[key]


def traces(make):
    """Trace runs in checker.TRACE_LAYOUT, built here from world.run_life (independent of reset.py)."""
    def bits(x):
        return "".join(str(b) for b in x)
    pa = {k: [] for k in ("RESET", "SKIP1", "SKIP2", "SKIP3")}
    pd, sd, cl = [], [], []
    for h in W.histories():
        rec = W.run_life(make, h)
        pa["RESET"].append("".join(bits(rec.probe_a(e)) for e in range(1, 7)))
        pd.append("".join(str(rec.probe_d(e)) for e in range(1, 7)))
        sd.append("".join("".join("%d%d" % s for s in rec.sends(e)) + "--" * (2 - len(rec.sends(e)))
                          for e in range(1, 7)))
        for j in (1, 2, 3):
            r = W.run_life(make, h, reset_at=set(range(1, 6)) - {j})
            pa["SKIP%d" % j].append("".join(bits(r.probe_a(e)) for e in range(1, 7)))
        row = []
        for j in (1, 2, 3):
            for v in (0, 1):
                def hook(rt, point, j=j, v=v):
                    if point == ("RESET", j):
                        c = rt.capture()
                        c["a"] = v
                        rt.restore(c)
                    return rt
                row.append(str(W.run_life(make, h, hook=hook).probe_a(j + 1)[0]))
        cl.append("".join(row))
    return {"trace:probe_a": {k: "".join(v) for k, v in pa.items()}, "trace:probe_d": {"RESET": "".join(pd)},
            "trace:sends": {"RESET": "".join(sd)}, "trace:clamp": {"CLAMP": "".join(cl)}}


# --------------------------------------------------------------------------------------------------------
# Naive stubs (fire tests). Each is a plausible-looking predicate that a broken fixture gets through.

def naive_erase_capture(make):
    """Right after each reset, the captured display is 0 and the channel is empty -> 'erased'."""
    ok = True
    for h in range(0, W.HISTORIES, 7):
        def hook(rt, point):
            nonlocal ok
            if point[0] == "RESET" and point[1] in W.BOUNDARIES and rt.capture()["d"] != 0:
                ok = False
            return rt
        W.run_life(make, h, hook=hook)
    return ok


def naive_erase_two_calls_one_episode(make):
    """ERASE checked at boundaries 1 and 2 only, one episode ahead (the reported state is not compared)."""
    masks = {1: RS.forbidden_mask(1), 2: RS.forbidden_mask(2)}
    outs = {h: W.run_life(make, h) for h in W.histories()}
    for j in (1, 2):
        for h in W.histories():
            r = h & ~masks[j]
            if outs[h].probe_a(j + 1) != outs[r].probe_a(j + 1):
                return False
    return True


def naive_erase_declared_state(make):
    """After each reset, the declared state (a, d) is a function of u_j alone -> 'erased'."""
    seen = {}
    for h in W.histories():
        def hook(rt, point):
            if point[0] == "RESET" and point[1] in W.BOUNDARIES:
                c = rt.capture()
                seen.setdefault((point[1], W.u_of(h, point[1])), set()).add((c["a"], c["d"]))
            return rt
        W.run_life(make, h, hook=hook)
    return all(len(v) == 1 for v in seen.values())


def naive_erase_packet_alone(make):
    """The packets in flight after each reset are, on their own, independent of f_j."""
    by_f = {}
    for h in W.histories():
        def hook(rt, point):
            if point[0] == "RESET" and point[1] in W.BOUNDARIES:
                key = (point[1], W.f_of(h, point[1]))
                payload = tuple(sorted(p[2] for p in rt.capture()["chan"]))
                by_f.setdefault(key, {}).setdefault(payload, 0)
                by_f[key][payload] += 1
            return rt
        W.run_life(make, h, hook=hook)
    return all(by_f[(j, 0)] == by_f[(j, 1)] for j in W.BOUNDARIES)


def naive_restart(make, cuts):
    """Restart compared at the given cut indexes only, FRESH target only."""
    for h in range(0, W.HISTORIES, 5):
        base = W.run_life(make, h).outputs
        for i in cuts:
            point = W.SCHEDULE_POINTS[i]

            def hook(rt, p, point=point):
                if p == point:
                    t = make()
                    t.restore(rt.capture())
                    return t
                return rt
            if W.run_life(make, h, hook=hook).outputs != base:
                return False
    return True


def naive_observer_final_score(make, obs):
    """Observer harmless if the retention answers (the 'final score') are unchanged."""
    for h in W.histories():
        a = W.run_life(make, h)
        b = W.run_life(make, h, hook=lambda rt, p, h=h: obs(rt, p, h) if p[0] == "TICK" else rt)
        if [a.probe_a(e)[0] for e in range(2, 5)] != [b.probe_a(e)[0] for e in range(2, 5)]:
            return False
    return True


RESET_POINTS = [i for i, p in enumerate(W.SCHEDULE_POINTS) if p[0] == "RESET"]
EPISODE1_POINTS = [i for i, p in enumerate(W.SCHEDULE_POINTS) if p[0] == "TICK" and p[1] == 1]


class TestFireStubs(unittest.TestCase):
    """Each broken fixture gets through a naive check; the real predicate must refuse it (next class)."""

    def test_T04_lagd_passes_a_captured_display_check(self):
        self.assertTrue(naive_erase_capture(WC.LAGD))

    def test_T05_wipe_passes_erasure_alone(self):
        self.assertEqual(outcome("ERASE", "WIPE")["value"], "PASS")

    def test_T06_pkdt_noq_passes_cuts_at_reset_points_only(self):
        self.assertTrue(naive_restart(WC.PKTD_NOQ, RESET_POINTS))

    def test_T06_hcount_passes_cuts_inside_one_episode(self):
        self.assertTrue(naive_restart(WC.HCOUNT, EPISODE1_POINTS))

    def test_T07_heal_passes_a_final_score_check(self):
        self.assertTrue(naive_observer_final_score(WC.REG, WC.HEAL))

    def test_T08_every3_and_sleeper_pass_two_calls_one_episode_ahead(self):
        self.assertTrue(naive_erase_two_calls_one_episode(WC.EVERY3))
        self.assertTrue(naive_erase_two_calls_one_episode(WC.SLEEPER))

    def test_T08_split1_passes_a_declared_state_check(self):
        self.assertTrue(naive_erase_declared_state(WC.SPLIT1))

    def test_T08_split2_passes_a_packet_alone_check(self):
        self.assertTrue(naive_erase_packet_alone(WC.SPLIT2))

    def test_stubs_are_not_vacuous(self):
        # each stub refuses something, so its PASS above is a fact about the fixture
        self.assertFalse(naive_erase_capture(WC.EVERY3))
        self.assertFalse(naive_restart(WC.PKTD_NOQ, [i for i, p in enumerate(W.SCHEDULE_POINTS)
                                                     if p == ("TICK", 1, "CUE")]))
        self.assertFalse(naive_restart(WC.HCOUNT, RESET_POINTS))
        self.assertFalse(naive_erase_two_calls_one_episode(WC.LAGD))
        self.assertFalse(naive_erase_declared_state(WC.EVERY3))
        self.assertFalse(naive_erase_packet_alone(WC.LAGD))


class TestCases(unittest.TestCase):
    """Draft A A6 rows T03-T08 (+P0) and the independent table rows T03-T08."""

    def assertGate(self, out, value, eligible, reason_prefix=None, applicable=None):
        self.assertEqual(out["value"], value, out["reason"])
        self.assertEqual(out["eligible_count"], eligible)
        if applicable is not None:
            self.assertEqual(out["applicable_count"], applicable)
        if reason_prefix is not None:
            self.assertTrue(out["reason"].startswith(reason_prefix), out["reason"])
        if value == "FAIL":
            self.assertIsNotNone(out["witness"])
        else:
            self.assertIsNone(out["witness"])

    def test_T03_reg(self):
        self.assertGate(outcome("ERASE", "REG"), "PASS", 9600)
        self.assertGate(outcome("PRESERVE", "REG"), "PASS", 6144, applicable=6144)

    def test_T04_lagd(self):
        out = outcome("ERASE", "LAGD")
        # canonical order is history first: h = 64 (f_3 = 1) is the smallest history with a forbidden bit
        self.assertGate(out, "FAIL", 9600, "forbidden influence across boundary 3, first visible at (4, PROBE_A)")
        self.assertEqual(out["witness"], {"history": 64, "partner": 0, "j": 3, "episode": 4, "tick": "PROBE_A"})
        self.assertGate(outcome("PRESERVE", "LAGD"), "PASS", 6144, applicable=6144)

    def test_T05_wipe(self):
        out = outcome("PRESERVE", "WIPE")
        self.assertGate(out, "FAIL", 6144, "reset at 3 destroys allowed content", applicable=6144)
        self.assertEqual(out["witness"], {"history": 128, "partner": 0, "j": 3})      # u_3 = 1 comes first
        self.assertGate(outcome("ERASE", "WIPE"), "PASS", 9600)

    def test_T05_amnesiac_preserve_is_vacuous(self):
        out = outcome("PRESERVE", "AMNESIAC")
        self.assertGate(out, "PASS", 6144, applicable=0)
        self.assertTrue(out["vacuous"])

    def test_T06_complete_restart(self):
        for name in ("REG", "PKTD"):
            self.assertGate(outcome("RESTART", name), "PASS", 237568)

    def test_T06_incomplete_restart(self):
        for name in ("PKTD_NOQ", "HCOUNT"):
            self.assertGate(outcome("RESTART", name), "FAIL", 237568,
                            "capture/restore loses future-influencing state at")

    def test_T06_coupling_restart_does_not_establish_reset(self):
        self.assertGate(outcome("RESTART", "LAGD"), "PASS", 237568)
        self.assertEqual(outcome("ERASE", "LAGD")["value"], "FAIL")

    def test_T06_hcount_erase_pass(self):
        self.assertGate(outcome("ERASE", "HCOUNT"), "PASS", 9600)

    def test_T07_observers_on_reg(self):
        self.assertGate(outcome("OBSERVER", "REG", "NULL"), "PASS", 196608)
        self.assertGate(outcome("OBSERVER", "REG", "BOOKKEEP"), "PASS", 196608)
        out = outcome("OBSERVER", "REG", "HEAL")
        self.assertGate(out, "FAIL", 196608, "observer HEAL changes state:d at (1, CUE)")
        self.assertEqual(out["witness"], {"history": 0, "episode": 1, "tick": "CUE", "what": "state:d"})

    def test_T07_heal_changes_an_output_but_not_the_final_score(self):
        self.assertTrue(naive_observer_final_score(WC.REG, WC.HEAL))
        self.assertEqual(OB.obs_eq(WC.REG, WC.HEAL, "HEAL", outputs_only=True)["witness"],
                         {"history": 0, "episode": 1, "tick": "PROBE_D", "what": "output"})

    def test_capture_pure(self):
        self.assertEqual(OB.capture_pure(WC.REG)["value"], "PASS")

        class Impure(WC.REG):
            def capture(self):
                self.a ^= 1
                return WC.REG.capture(self)
        out = OB.capture_pure(Impure)
        self.assertEqual(out["value"], "FAIL")
        self.assertTrue(out["reason"].startswith("capture() changes future output at"))
        self.assertEqual(OB.observer(Impure, WC.NULL, "NULL")["value"], "FAIL")

    def test_T08_every3(self):
        out = outcome("ERASE", "EVERY3")
        self.assertGate(out, "FAIL", 9600, "forbidden influence across boundary 3, first visible at (4, PROBE_A)")
        self.assertEqual(out["witness"]["j"], 3)
        self.assertGate(outcome("PRESERVE", "EVERY3"), "PASS", 6144, applicable=6144)

    def test_T08_sleeper_and_splits(self):
        for name in ("SLEEPER", "SPLIT1", "SPLIT2"):
            self.assertGate(outcome("ERASE", name), "FAIL", 9600, "forbidden influence across boundary")
        self.assertEqual(outcome("ERASE", "SLEEPER")["witness"],
                         {"history": 64, "partner": 0, "j": 3, "episode": 5, "tick": "PROBE_D"})

    def test_T08_reg(self):
        self.assertGate(outcome("ERASE", "REG"), "PASS", 9600)

    def test_T01_channel(self):
        self.assertGate(outcome("CHANNEL", "REG"), "PASS", 24576)
        out = outcome("CHANNEL", "QCARRY")
        self.assertGate(out, "FAIL", 24576, "retained answer does not follow the declared allowed channel at 1")
        self.assertEqual(out["witness"], {"history": 0, "j": 1, "v": 1})
        self.assertGate(outcome("CHANNEL", "AMNESIAC"), "PASS", 24576)     # X05: answers from a

    def test_P0_overdelay_is_blocked_with_bounds_fail(self):
        out = RS.bounds(WC.OVERDELAY)
        self.assertEqual(out["value"], "FAIL")
        self.assertEqual(out["reason"], "runtime outside the registered model: DELAY_RANGE at (1, CUE)")
        self.assertEqual(RS.bounds(WC.REG)["value"], "PASS")
        blocked = RS.erase(WC.OVERDELAY)
        self.assertEqual(blocked["execution"], {"status": "BLOCKED", "missing": ["runtime inside the registered model"]})


class TestEscapesAndLimits(unittest.TestCase):
    def test_every_in_model_escape_is_caught(self):
        for eid, source, runtime, obs, pred in WC.ESCAPES:
            if pred == "CALIBRATION":
                continue                                  # T012 (world CLOCKED)
            with self.subTest(escape=eid):
                self.assertEqual(outcome(pred, runtime, obs)["value"], "FAIL", (eid, source))

    def test_observer_qualification_is_per_runtime(self):
        self.assertEqual(outcome("OBSERVER", "REG", "IMPOSTOR_ONLY")["value"], "PASS")
        self.assertEqual(outcome("OBSERVER", "AMNESIAC", "IMPOSTOR_ONLY")["value"], "FAIL")

    def test_state_heal_changes_no_output(self):
        self.assertEqual(OB.obs_eq(WC.REG, WC.STATE_HEAL, "STATE_HEAL", outputs_only=True)["value"], "PASS")

    def test_stated_limits_pass_by_construction(self):
        for lid, runtime, pred, why in WC.STATED_LIMITS:
            with self.subTest(limit=lid):
                self.assertEqual(outcome(pred, runtime)["value"], "PASS", why)


class TestAgreementWithChecker(unittest.TestCase):
    """The producer's predicates equal the consumer's recomputation (G-RECOMP fields) on the same runs."""

    FIELDS = ("value", "eligible_count", "applicable_count", "witness")

    def test_erase_preserve_channel_agree(self):
        # PASS and FAIL of each predicate: ERASE (REG / LAGD), PRESERVE (REG / WIPE), CHANNEL (REG / QCARRY)
        for name in ("REG", "LAGD", "WIPE", "QCARRY"):
            runs = traces(WC.RUNTIMES[name])
            for pred, fn in (("ERASE", CK.recompute_erase), ("PRESERVE", CK.recompute_preserve),
                             ("CHANNEL", CK.recompute_channel)):
                with self.subTest(runtime=name, predicate=pred):
                    mine, theirs = outcome(pred, name), fn(runs)
                    for f in self.FIELDS:
                        self.assertEqual(mine[f], theirs[f], f)


class TestRunner(unittest.TestCase):
    def test_point_runner_equals_world_run_life(self):
        for name in ("REG", "PKTD", "LAGD", "HCOUNT", "SPLIT1"):
            for h in (0, 1, 2730, 4095):
                self.assertEqual(RS.run_points(WC.RUNTIMES[name](), h, 0, len(W.SCHEDULE_POINTS)),
                                 W.run_life(WC.RUNTIMES[name], h).outputs)


# --------------------------------------------------------------------------------------------------------
# S4 repair C-004-T043 (TRIAGE_S3.md rows E01, E02; S3 edits rso/slice001/challenge/S3/attack_set/edits_A.json).
# Fixtures live here, not in fixtures/world_cases.py, so no instrument version changes (P8 pins that file; #1543).

class LAG3_ONLY(WC.REG):
    """E01: the forbidden bit sent once, at the CUE of episode 3, with k = 3; the reset keeps the channel. It first
    shows at PROBE_A of episode 6: lag exactly H after boundary 3 (draft A A7), and nowhere earlier."""

    def on_cue(self, u, f):
        self.a, self.d = u, f
        if self.ep == 3:
            self.send(f, 3)

    def reset(self):
        self.d = 0


class SENDS_ONLY(WC.REG):
    """E02: re-sends the previous episode's forbidden bit (k = 3) at every CUE and ignores deliveries, so the
    forbidden content shows in no probe, only in the CUE output (A5 P3: identical outputs at EVERY tick)."""

    def __init__(self):
        WC.REG.__init__(self)
        self.prev = 0

    def on_cue(self, u, f):
        self.a, self.d = u, f
        self.send(self.prev, 3)
        self.prev = f

    def on_deliver(self, bits):
        pass


def _erase_with_edit(edit_id, make):
    """reset.erase with one S3 edit applied to an in-memory copy of reset.py (the frozen file is never written)."""
    import json
    import os
    import types
    edits = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "challenge", "S3", "attack_set", "edits_A.json")
    with open(edits, "r", encoding="utf-8") as f:
        doc = json.load(f)
    edit = next(e for e in (doc["edits"] if isinstance(doc, dict) else doc) if e["edit_id"] == edit_id)
    with open(RS.__file__, "r", encoding="utf-8") as f:
        src = f.read()
    assert src.count(edit["find"]) == 1, edit_id
    mod = types.ModuleType("rso.slice001.reset_" + edit_id.replace("-", "_"))
    exec(compile(src.replace(edit["find"], edit["replace"]), RS.__file__, "exec"), mod.__dict__)
    return mod.erase(make)


class TestS4RepairE01E02(unittest.TestCase):
    def test_E01_lag_exactly_H_is_caught(self):
        out = RS.erase(LAG3_ONLY)
        self.assertEqual(out["value"], "FAIL")
        self.assertEqual(out["witness"], {"history": 64, "partner": 0, "j": 3, "episode": 6, "tick": "PROBE_A"})
        self.assertEqual(out["reason"], "forbidden influence across boundary 3, first visible at (6, PROBE_A)")

    def test_E02_sends_only_leak_is_caught(self):
        out = RS.erase(SENDS_ONLY)
        self.assertEqual(out["value"], "FAIL")
        self.assertEqual(out["witness"], {"history": 64, "partner": 0, "j": 3, "episode": 4, "tick": "CUE"})
        self.assertEqual(out["reason"], "forbidden influence across boundary 3, first visible at (4, CUE)")

    def test_E01_fixture_kills_the_S3_horizon_edit(self):
        # fire half: the edited ERASE (horizon j+1..j+2) lets the lag-H leak through; the frozen one does not
        self.assertEqual(_erase_with_edit("E01-erase-horizon", LAG3_ONLY)["value"], "PASS")

    def test_E02_fixture_kills_the_S3_sends_edit(self):
        self.assertEqual(_erase_with_edit("E02-erase-ignores-sends", SENDS_ONLY)["value"], "PASS")

    def test_fixtures_stay_inside_the_registered_model(self):
        for make in (LAG3_ONLY, SENDS_ONLY):
            self.assertEqual(RS.bounds(make)["value"], "PASS")
            self.assertEqual(RS.preserve(make)["value"], "PASS")    # only the erase clause is under test


if __name__ == "__main__":
    unittest.main()
