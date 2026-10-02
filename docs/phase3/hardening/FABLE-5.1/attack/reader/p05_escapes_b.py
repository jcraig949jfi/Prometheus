exec(open(__file__.replace("p05_escapes_b.py", "drv.py")).read())
from rso_harness import stats, retain1, rulers, search, torture, audits, claims, registration
from rso_harness.verdict import *
from rso_harness.stats import khash


def show(tag, r):
    print("%-86s -> %s %s" % (tag, r.verdict, ("| " + r.reason) if r.reason else ""))


P = meta.PAIRS
print("################ G6.observer")


def last_step_writer(log):
    """Fault: rewrites the organism state after the probe has been answered."""
    def observe(world, seed, t, org):
        if t == 7 and hasattr(org, "w"):
            org.w = 1
    return observe


def own_stream_observer(log):
    """Clean twin: draws random numbers, but from its own stream."""
    n = [0]

    def observe(world, seed, t, org):
        n[0] += 1
        log.append(khash(seed, 777, n[0]))
    return observe


def rare_observer(log):
    """Fault: draws from the world stream only on seeds outside the 12 checked."""
    def observe(world, seed, t, org):
        if seed not in P:
            world.draw(seed)
    return observe


def mark_writer(log):
    def observe(world, seed, t, org):
        world.mark = 1
    return observe


def clock_bump(log):
    def observe(world, seed, t, org):
        world.episodes += 5
    return observe


def late_draw(log):
    """Fault: draws from the world stream, but only after the last distractor has been drawn."""
    def observe(world, seed, t, org):
        if t >= 6:
            world.draw(seed)
    return observe


for name, obs in (("clean twin: observer with its own random stream", own_stream_observer),
                  ("E writes the register after the probe (t=7)", last_step_writer),
                  ("E disturbs the world only on unchecked seeds", rare_observer),
                  ("? writes the environment mark", mark_writer),
                  ("E bumps the world episode counter", clock_bump),
                  ("E draws from the world stream after the last distractor", late_draw)):
    show(name, meta.all_positives(lambda m: torture.observer_equivalence(m, P, obs)))

print("################ G6.reset")


class SneakyRegister(retain1.Register):
    """Reset clears the word and keeps a carry that native() does not show; the carry is used only when a cue arrives."""

    def __init__(self):
        self.w = None
        self.carry = 0

    def reset(self):
        self.w = None

    def step(self, obs):
        if obs.kind == "CUE":
            self.w = obs.value ^ self.carry
            self.seen = obs.value
        if obs.kind == "PROBE":
            out = self.w or 0
            if self.w is not None:
                self.carry = self.seen
            return out


show("E state survives reset, expressed only in cued episodes (SneakyRegister)", torture.reset_closure(SneakyRegister, P))
w = retain1.World()
o = SneakyRegister()
r1 = w.episode(o, 5, force_bit=1)
r2 = w.episode(o, 6, force_bit=1)
r3 = w.episode(o, 7, force_bit=1)
print("   demonstration: three cued episodes, cue 1 each; answers:", r1["answer"], r2["answer"], r3["answer"],
      "(the carry-over changes later answers)")
show("clean positives", meta.all_positives(lambda m: torture.reset_closure(m, P)))
for nm, m in (("Attractor", retain1.Attractor), ("PacketRing", retain1.PacketRing), ("Lattice", retain1.Lattice)):
    show("  harness forgets to reset: " + nm, torture.reset_closure(m, P, skip_reset=True))

print("################ G6.restart")


class PacketAppendRestore(retain1.PacketRing):
    """Fault: restore adds to whatever is already there (stale state is kept)."""

    def restore(self, state):
        self.queue = self.queue + [list(p) for p in state]


class RegisterKeepIfSet(retain1.Register):
    """Fault: restore only fills an empty word; a stale word is left in place."""

    def restore(self, state):
        if self.w is None:
            self.w = state[0]


class LateOnlyBadCapture(retain1.Lattice):
    """Fault: capture drops the clock, but only late in the gap (after step 5)."""

    def capture(self):
        return (tuple(self.cells), self.t if self.t <= 5 else 0)


show("E restore that merges with stale state (PacketAppendRestore)", torture.restart_equivalence(PacketAppendRestore, P))
show("E restore that leaves a stale word in place (RegisterKeepIfSet)", torture.restart_equivalence(RegisterKeepIfSet, P))
show("E capture that is wrong only after step 5 (checked at step 3 only)", torture.restart_equivalence(LateOnlyBadCapture, P))
show("  same fault, checked at step 6", torture.restart_equivalence(LateOnlyBadCapture, P, at=6))
a = PacketAppendRestore()
a.queue = [[1, 0]]
a.restore(((0, 1),))
print("   PacketAppendRestore into a used runtime ->", a.queue, "(stale packet kept)")
b = RegisterKeepIfSet()
b.w = 0
b.restore((1,))
print("   RegisterKeepIfSet into a used runtime -> w =", b.w, "(stale word kept; should be 1)")

print("################ G8.demand")
show("clean", torture.demand_closure(meta.SEEDS))
import rso_harness.retain1 as R
Base = R.World


def run_world(self, org, seed, cue_and_probe):
    self.draws, self.mark = 0, None
    org.reset()
    bit, kinds = cue_and_probe(self, seed)
    answer = None
    for t, (kind, value) in enumerate(kinds):
        if kind == "DISTRACT" and value is None:
            value = self.draw(seed)
        action = org.step(R.Obs(kind, value, t, self.mark))
        if kind == "PROBE":
            answer = action
    self.episodes += 1
    return {"bit": bit, "answer": answer, "trace": ()}


class InvertedKeyWorld(Base):
    """Fault: the probe carries the complement of the answer."""

    def episode(self, org, seed, **kw):
        def plan(self, seed):
            bit = self.draw(seed)
            return bit, [("CUE", bit)] + [("DISTRACT", None)] * self.gap + [("PROBE", 1 - bit)]
        return run_world(self, org, seed, plan)


class PartialLeakWorld(Base):
    """Fault: the probe carries the answer in 40% of episodes (a reader of the probe is right 70% of the time)."""

    def episode(self, org, seed, **kw):
        def plan(self, seed):
            bit = self.draw(seed)
            leak = (khash(seed, 4242) % 5) < 2
            return bit, [("CUE", bit)] + [("DISTRACT", None)] * self.gap + [("PROBE", bit if leak else None)]
        return run_world(self, org, seed, plan)


class XorWorld(Base):
    """Fault: the cue is the xor of the last two distractors."""

    def episode(self, org, seed, **kw):
        def plan(self, seed):
            d = [self.draw(seed) for _ in range(self.gap)]
            bit = d[-1] ^ d[-2]
            return bit, [("CUE", bit)] + [("DISTRACT", v) for v in d] + [("PROBE", None)]
        return run_world(self, org, seed, plan)


class XorLastTwo(R.Register):
    """Carries nothing across the gap: answers the xor of the last two distractors."""

    def __init__(self):
        self.w = None
        self.a = self.b = 0

    def reset(self):
        self.a = self.b = 0

    def step(self, obs):
        if obs.kind == "DISTRACT":
            self.a, self.b = self.b, obs.value
        if obs.kind == "PROBE":
            return self.a ^ self.b


class ProbeReader70(R.Register):
    """Carries nothing: answers what the probe carries when it carries something."""

    def step(self, obs):
        if obs.kind == "PROBE":
            return obs.value or 0


class Negator(R.Register):
    """Carries nothing: answers the complement of what the probe carries."""

    def step(self, obs):
        if obs.kind == "PROBE":
            return 1 - (obs.value or 0)


for name, W, cheat in (("E the probe carries the COMPLEMENT of the answer", InvertedKeyWorld, Negator),
                       ("E the probe carries the answer in 40% of episodes", PartialLeakWorld, ProbeReader70),
                       ("E the cue is the xor of the last two distractors", XorWorld, XorLastTwo)):
    R.World = W
    try:
        r = torture.demand_closure(meta.SEEDS)
        scores = {k: R.score(v, meta.SEEDS) for k, v in R.BASELINES.items()}
        show(name, r)
        print("      baseline scores of 64:", scores)
        print("      a policy that carries nothing (%s) scores %d of 64; the exclusion ruler calls it %s"
              % (cheat.__name__, R.score(cheat, meta.SEEDS), rulers.exclusion_ruler(cheat, meta.SEEDS)))
    finally:
        R.World = Base
print("   P(G8 flags a probe reader that is right 70%% of the time) = %.4f ; 75%% = %.4f ; 80%% = %.4f"
      % (stats.tail_ge(64, 51, 0.70), stats.tail_ge(64, 51, 0.75), stats.tail_ge(64, 51, 0.80)))
show("? required baselines present, LAST_DISTRACTOR dropped",
     torture.demand_closure(meta.SEEDS, baselines={k: v for k, v in R.BASELINES.items() if k != "LAST_DISTRACTOR"}))
