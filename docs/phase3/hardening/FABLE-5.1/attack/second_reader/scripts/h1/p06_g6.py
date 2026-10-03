"""G6.observer, G6.reset, G6.restart."""
from drv import *
R, PAIRS, SEEDS = retain1, meta.PAIRS, meta.SEEDS
allp = meta.all_positives


def show(name, thunk):
    try:
        r = thunk()
        print("%-92s -> %s %s" % (name, r.verdict, ("| " + r.reason[:150]) if r.reason else ""))
    except Exception as e:
        print("%-92s -> RAISES %s: %s" % (name, type(e).__name__, str(e)[:100]))


print("--- G6.observer: broken observers")


def second_episode_observer(log):          # disturbs only a world that has run before
    def observe(world, seed, t, org):
        if world.episodes > 0:
            world.draw(seed)
    return observe


show("O1 draws from the world stream in every episode but a world's first",
     lambda: allp(lambda m: torture.observer_equivalence(m, PAIRS, second_episode_observer)))
w0, w1 = R.World(), R.World()
a = [w0.episode(R.Register(), s) for s in PAIRS]
b = [w1.episode(R.Register(), s, observer=second_episode_observer([])) for s in PAIRS]
print("     same 12 seeds run as ONE run of 12 episodes: episodes that differ with the observer on: %d of 12"
      % sum(x != y for x, y in zip(a, b)))


def leak_switch_observer(log):             # after the probe, turns on the probe leak for every later episode
    def observe(world, seed, t, org):
        if t == world.gap + 1:
            world.leak_key = "plain"
    return observe


show("O2 after the probe, sets world.leak_key=plain (every later probe carries the answer)",
     lambda: allp(lambda m: torture.observer_equivalence(m, PAIRS, leak_switch_observer)))
w = R.World()
sc = 0
for s in SEEDS:
    r = w.episode(R.KeyReader(), s, observer=leak_switch_observer([]))
    sc += r["answer"] == r["bit"]
print("     a probe reader in one 64-episode run under that observer scores %d of 64 (class exclusion: %s)"
      % (sc, stats.classify(sc, 64, 0.5, 1e-6, 15 / 16)))


def no_reset_observer(log):                # switches the harness reset off
    def observe(world, seed, t, org):
        world.skip_reset = True
    return observe


show("O3 sets world.skip_reset=True (the harness stops resetting)",
     lambda: allp(lambda m: torture.observer_equivalence(m, PAIRS, no_reset_observer)))


def impostor_only_observer(log):           # rewrites only organisms that are not on the list checked
    def observe(world, seed, t, org):
        if type(org).__name__ in ("RegisterImpostor", "FadingRegister", "Constant", "KeyReader", "WorldParker",
                                  "Recorder"):
            org.w = world.draw(seed)
    return observe


show("O4 disturbs only impostors, the weak positive and the baselines",
     lambda: allp(lambda m: torture.observer_equivalence(m, PAIRS, impostor_only_observer)))
show("     the same observer checked on an impostor directly",
     lambda: torture.observer_equivalence(R.RegisterImpostor, PAIRS, impostor_only_observer))


def class_patch_observer(log):             # after the probe, shortens every Lattice made afterwards
    def observe(world, seed, t, org):
        if t == world.gap + 1 and isinstance(org, R.Lattice):
            R.Lattice.N = 4
    return observe


show("O5 after the first observed episode, changes the lattice physics for good (class attribute)",
     lambda: allp(lambda m: torture.observer_equivalence(m, PAIRS, class_patch_observer)))
print("     Lattice.N is now", R.Lattice.N)
R.Lattice.N = 8

show("O6 weak mode: greedy observer with compare=score returns a gate PASS",
     lambda: allp(lambda m: torture.observer_equivalence(m, PAIRS, torture.greedy_observer, compare="score")))
show("O7 no seeds at all", lambda: allp(lambda m: torture.observer_equivalence(m, [], torture.greedy_observer)))

print("--- G6.reset")
show("T0 no seeds at all, on a runtime whose reset keeps its word", lambda: torture.reset_closure(R.LeakyResetRegister, []))


class ThirdResetFails(R.Register):
    """Reset works twice and then stops clearing."""

    def __init__(self):
        self.w, self.resets = None, 0

    def reset(self):
        self.resets += 1
        if self.resets <= 2:
            self.w = None


show("T1 a reset that works twice and not the third time", lambda: torture.reset_closure(ThirdResetFails, PAIRS))
w, org = R.World(), ThirdResetFails()
ans = [w.episode(org, s, cue=(i < 2), force_bit=1)["answer"] for i, s in enumerate((1, 2, 3))]
print("     cue 1, cue 1, then a blank episode: answers", ans, "(a fresh runtime answers 0 to a blank episode)")


class CarryAfterBlank(R.Register):
    """Hidden carry set only by an episode with no cue, used in the next episode."""

    def __init__(self):
        self.w, self.pending = None, 0

    def reset(self):
        self.w = None

    def step(self, obs):
        if obs.kind == "BLANK":
            self.pending = 1
        if obs.kind == "CUE":
            self.w = obs.value ^ self.pending
            self.pending = 0
        if obs.kind == "PROBE":
            return self.w or 0


show("T2 a carry set only by an episode with no cue (the earlier episode in the check always has one)",
     lambda: torture.reset_closure(CarryAfterBlank, PAIRS))
w, org = R.World(), CarryAfterBlank()
w.episode(org, 1, cue=False)
print("     blank episode, then cue 1: answer", w.episode(org, 2, force_bit=1)["answer"])
show("T5 reset closure on the weak positive and on an impostor (never checked by the registry)",
     lambda: combine("x", [torture.reset_closure(R.FadingRegister, PAIRS), torture.reset_closure(R.RegisterImpostor, PAIRS)]))

print("--- G6.restart")
show("T3 SneakyRegister under the restart gate (hidden carry is not captured)",
     lambda: torture.restart_equivalence(R.SneakyRegister, PAIRS))
whole_org, cut_src, used = R.SneakyRegister(), R.SneakyRegister(), R.SneakyRegister()
R.World().episode(whole_org, 2000, force_bit=1)
R.World().episode(used, 2000, force_bit=0)
R.World().episode(cut_src, 2000, force_bit=1)
used.restore(cut_src.capture())
print("     uncut runtime hidden carry:", whole_org.carry, "; restored runtime hidden carry:", used.carry,
      "; reported state equal:", whole_org.native() == used.native())
show("T4 SleeperRegister under the restart gate", lambda: torture.restart_equivalence(R.SleeperRegister, PAIRS))


class RestoreNeedsWarm(R.Register):
    """Restore is ignored by a runtime that has never stepped."""

    def __init__(self):
        self.w, self.warm = None, False

    def step(self, obs):
        self.warm = True
        return super().step(obs)

    def restore(self, state):
        if self.warm:
            self.w = state[0]


show("K1 a restore that a never-used runtime ignores", lambda: torture.restart_equivalence(RestoreNeedsWarm, PAIRS))
src, dst = RestoreNeedsWarm(), RestoreNeedsWarm()
R.World().episode(src, 1, force_bit=1)
dst.restore(src.capture())
print("     captured word", src.capture(), "restored into a new runtime:", dst.native())


class LastStepBadCapture(R.Lattice):
    """Capture is wrong only after the probe (the last step)."""

    def capture(self):
        return (tuple(self.cells), self.t if self.t < 8 else 0)


show("K2 a capture that is wrong at the last step only", lambda: torture.restart_equivalence(LastStepBadCapture, PAIRS))
whole = R.World().episode(R.Lattice(), 2000)
print("     steps in an episode:", len(whole["trace"]), "; cuts tried: 0..%d" % (len(whole["trace"]) - 2))


class SameCueStale(R.Register):
    """Restore corrupts when the target already holds the same word. The check always supplies the opposite cue."""

    def restore(self, state):
        if self.w is None or self.w != state[0]:
            self.w = state[0]
        else:
            self.w = None


show("K3 a restore that corrupts when the target already holds the SAME word",
     lambda: torture.restart_equivalence(SameCueStale, PAIRS))
a, b = SameCueStale(), SameCueStale()
a.w = 1
b.w = 1
b.restore(a.capture())
print("     word 1 restored over a runtime holding 1 ->", b.native())
show("K4 no seeds at all, restore does nothing", lambda: torture.restart_equivalence(R.AttractorStaleRestore, []))
show("K5 restart on the weak positive (never checked by the registry)", lambda: torture.restart_equivalence(R.FadingRegister, PAIRS))


class FadingBadCapture(R.FadingRegister):
    def capture(self):
        return (self.w, 0)


show("K5b weak positive with a capture that drops its counter", lambda: torture.restart_equivalence(FadingBadCapture, PAIRS))
print("--- interchange ruler on registered positives outside the G5 panel")
print("     interchange on the weak positive (PAIRS):", rulers.interchange_ruler(R.FadingRegister, PAIRS),
      "; class exclusion on it:", rulers.exclusion_ruler(R.FadingRegister, SEEDS))
print("     interchange on a positive whose restore does nothing:", rulers.interchange_ruler(R.AttractorStaleRestore, PAIRS),
      "; class exclusion:", rulers.exclusion_ruler(R.AttractorStaleRestore, SEEDS))
print("     interchange on a positive whose capture omits the packet:", rulers.interchange_ruler(R.PacketRingBadCapture, PAIRS),
      "; class exclusion:", rulers.exclusion_ruler(R.PacketRingBadCapture, SEEDS))
