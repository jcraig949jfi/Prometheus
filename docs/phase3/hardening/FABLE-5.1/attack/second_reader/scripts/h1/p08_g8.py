"""G8.demand and the fitted table baseline."""
from drv import *
R, DEMAND, TRAIN, SEEDS = retain1, meta.DEMAND, meta.TRAIN, meta.SEEDS
dc = torture.demand_closure


def show(name, thunk):
    try:
        r = thunk()
        print("%-100s -> %s %s" % (name, r.verdict, ("| " + r.reason[:160]) if r.reason else ""))
        return r
    except Exception as e:
        print("%-100s -> RAISES %s: %s" % (name, type(e).__name__, str(e)[:100]))


print("--- the sound world: what each baseline scored (2,048 episodes)")
clean = dc(DEMAND, TRAIN)
print("    ", clean.verdict, clean.detail)
w = R.World()
same = sum(1 for s in DEMAND[:256] if len({R.World().episode(c(), s)["answer"] for c in (R.Constant, R.KeyReader, R.WorldParker)}) == 1)
print("     CONSTANT, KEY_READER and WORLD_PARKER give the same answer in %d of 256 episodes; CLOCK answers %s every time"
      % (same, {R.World().episode(R.ClockReader(), s)["answer"] for s in DEMAND[:256]}))


class XorLastTwo(R.Register):
    """Carries nothing across the gap: answers the xor of the last two distractors."""

    def __init__(self):
        self.w, self.last = None, [0, 0]

    def reset(self):
        self.w, self.last = None, [0, 0]

    def step(self, obs):
        if obs.kind == "DISTRACT":
            self.last = [self.last[1], obs.value]
        if obs.kind == "PROBE":
            return self.last[0] ^ self.last[1]


print("--- the registered leak (cue = xor of the last two distractors) at other gaps")
for gap in (6, 8, 10, 12, 13, 14, 15, 16, 18, 20):
    r = dc(DEMAND, TRAIN, gap=gap, cue_from_distractors=True)
    print("     gap %2d: %-13s TABLE %4d of 2048; a policy that xors the last two distractors: %d of 64"
          % (gap, r.verdict, r.detail["TABLE"], R.score(XorLastTwo, SEEDS, gap=gap, cue_from_distractors=True)))
print("     sound world at gap 16:", dc(DEMAND, TRAIN, gap=16).verdict, "; at gap 1:", dc(DEMAND, TRAIN, gap=1).verdict,
      "; at gap 0:", dc(DEMAND, TRAIN, gap=0).verdict)

print("--- the table fitted on little or nothing")
show("D1 xor leak at gap 6, table fitted on NO seeds", lambda: dc(DEMAND, [], cue_from_distractors=True))
show("D2 xor leak at gap 6, table fitted on 8 seeds", lambda: dc(DEMAND, TRAIN[:8], cue_from_distractors=True))
show("D3 xor leak at gap 6, table fitted on 16 seeds", lambda: dc(DEMAND, TRAIN[:16], cue_from_distractors=True))
show("D4 xor leak at gap 6, table fitted on 2,048 seeds (the registered mutant)", lambda: dc(DEMAND, TRAIN, cue_from_distractors=True))

print("--- baselines are required by name")
fake = {"CONSTANT": R.Constant, "CLOCK": R.Constant, "KEY_READER": R.Constant, "WORLD_PARKER": R.Constant, "TABLE": None}
show("D5 the environment keeps what is written; the baseline NAMED WORLD_PARKER is a constant", lambda: dc(DEMAND, TRAIN, baselines=fake, writable_mark=True))
show("D6 the environment keeps what is written, the real list (registered mutant)", lambda: dc(DEMAND, TRAIN, writable_mark=True))
show("D7 no seeds to score on", lambda: dc([], TRAIN))

print("--- what the recorder keeps of the clock")
show("D8 the listed escape (cue follows bit 1 of the counter)", lambda: dc(DEMAND, TRAIN, leak_clock="bit1"))
r = dc(DEMAND, TRAIN, leak_clock="bit1")
print("     TABLE scored", r.detail["TABLE"], "; the recorder stores obs.clock & 1 only (retain1.py line 378)")

print("--- how large a leak the margin admits")
from exactbin import tge, tle
hi = stats.critical_k(2048, 0.5, 1e-6)
for rate_num, rate_den in ((13, 24), (27, 50), (11, 20)):
    rate = rate_num / rate_den
    exp = round(2048 * rate)
    print("     a baseline at true rate %.4f: expected %d of 2048 -> %s; P(score in the PASS range 929..1119) = %.3f; "
          "P(an exclusion ruler at n=2048, alpha 1e-6 says yes, needs >= %d) = %.3f"
          % (rate, exp, stats.equivalence(exp, 2048, 0.5, 0.1, 1e-6),
             float(tle(2048, 1119, (rate_num, rate_den)) - tle(2048, 928, (rate_num, rate_den))), hi,
             float(tge(2048, hi, (rate_num, rate_den)))))

print("--- helper: every_missing_baseline_blocks")
print("    ", meta.every_missing_baseline_blocks().verdict, "| registered expected verdict BLOCKED")
