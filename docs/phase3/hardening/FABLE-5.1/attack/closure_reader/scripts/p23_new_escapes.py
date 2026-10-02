"""New attacks on the gates that changed most in the second version: G3, G6, G7.report, G8, G10.ruler, G11, G12."""
import json

from drv import *

R = retain1
P = meta.PAIRS
p_ok = dict(R.PANEL)
G1, G2, G3, KEYS = audits.G1, audits.G2, audits.G3, audits.KEYS
REP, B = meta.REPORTED, meta.BUDGET


def show(tag, r):
    print("%-100s -> %s%s" % (tag, r.verdict, (" | " + r.reason[:150]) if r.reason else ""))


print("################ G3: what the bracketing panel does and does not pin")
blocks = [meta.SEEDS] + meta.BLOCKS
imp = {p: [R.score(i, b) for b in blocks] for p, (_, i) in R.PANEL.items()}
for p, s in imp.items():
    print("   impostor scores on nine blocks, %-9s %s" % (p, s))
print("   distinct impostor score series: %d of 4 (36 impostor trials are %d independent ones)"
      % (len({tuple(v) for v in imp.values()}), 9 * len({tuple(v) for v in imp.values()})))
for b in (0.34, 0.35, 0.40, 0.45, 0.60, 0.68, 0.69):
    show("N bound %.2f" % b, meta.exclusion(rulers.make_exclusion_ruler(b)))
for a in (1e-9, 1e-4, 1e-3, 1e-2, 0.05):
    show("N alpha %g in the ruler (registered 1e-6)" % a, meta.exclusion(rulers.make_exclusion_ruler(alpha=a)))
for w in (0.99, 0.999, 0.8, 0.7):
    show("N weakest registered positive %.3f in the ruler (registered 15/16)" % w,
         meta.exclusion(rulers.make_exclusion_ruler(weakest=w)))
r99 = rulers.make_exclusion_ruler(weakest=0.99)
print("   with weakest=0.99 a true positive at 15/16 that scores 50 of 64 is called:",
      stats.classify(50, 64, 0.5, 1e-6, 0.99), "(registered ruler: %s)" % stats.classify(50, 64, 0.5, 1e-6, 15 / 16))
print("   P(a 15/16 positive scores 50 or less in 64) = %.2e" % stats.tail_le(64, 50, 15 / 16))

print("################ G4 / G5")


class Leaky60(R.Register):
    """Holds the cue in one episode of five and guesses otherwise: rate 0.6. It carries the cue, weakly."""
    physics = "REGISTER"
    n = [0]

    def step(self, obs):
        if obs.kind == "CUE":
            self.w = obs.value
            Leaky60.n[0] += 1
        if obs.kind == "PROBE":
            return (self.w or 0) if Leaky60.n[0] % 5 == 0 else 0


print("   Leaky60 score:", R.score(Leaky60, meta.SEEDS))
show("N G4: an 'impostor' that carries the cue in one episode of five", meta.entry("REGISTER", dict(p_ok, REGISTER=(R.Register, Leaky60))))

print("################ G6.observer: a disturbance the organism repairs before its next reported state")


def healing_observer(log):
    """Fault: flips one lattice cell between steps, away from where the next distractor acts. Local majority
    repairs it before the next state is recorded, so no recorded state differs."""
    def observe(world, seed, t, org):
        if hasattr(org, "cells") and t < world.gap:
            org.cells[(t + 5) % org.N] ^= 1
    return observe


def hidden_observer(log):
    """Fault: writes a field of the organism that native() does not report."""
    def observe(world, seed, t, org):
        org.touched = getattr(org, "touched", 0) + 1
    return observe


show("N observer flips a lattice cell between steps; majority repairs it (all positives)",
     meta.all_positives(lambda m: torture.observer_equivalence(m, P, healing_observer)))
flips = []


def counting(log):
    def observe(world, seed, t, org):
        if hasattr(org, "cells") and t < world.gap:
            org.cells[(t + 5) % org.N] ^= 1
            flips.append(1)
    return observe


torture.observer_equivalence(R.Lattice, P, counting)
print("   cells flipped by that observer on the lattice over 12 seeds:", len(flips))
show("N observer writes a field native() does not report", meta.all_positives(lambda m: torture.observer_equivalence(m, P, hidden_observer)))

print("################ G6.reset / G6.restart")


class DistractorCarry(R.Register):
    """Reset clears the word; a hidden field keeps the previous episode's LAST DISTRACTOR and flips the next cue with it."""

    def __init__(self):
        self.w, self.h, self.last = None, 0, 0

    def reset(self):
        self.w, self.h = None, self.last

    def step(self, obs):
        if obs.kind == "CUE":
            self.w = obs.value ^ self.h
        if obs.kind == "DISTRACT":
            self.last = obs.value
        if obs.kind == "PROBE":
            return self.w or 0


show("  a hidden carry of the previous episode's last distractor", torture.reset_closure(DistractorCarry, P))


class EveryThird(R.Register):
    """Reset is sound twice and leaks on every third call."""

    def __init__(self):
        self.w, self.calls = None, 0

    def reset(self):
        self.calls += 1
        if self.calls % 3:
            self.w = None


show("N a reset that fails on every third call only", torture.reset_closure(EveryThird, P))
w, o = R.World(), EveryThird()
ans = []
for s in range(5):
    ans.append(w.episode(o, 100 + s, cue=(s % 3 != 2), force_bit=1 if s % 3 != 2 else None)["answer"])
print("   EveryThird: cue 1, cue 1, blank, cue 1, cue 1 ->", ans, "(a blank episode answers the earlier cue)")


class HiddenLag(R.Register):
    """Capture and native() report the word; a hidden lag field is neither captured nor reported, and is not used
    until two steps after a restore."""

    def __init__(self):
        self.w, self.age = None, 0

    def reset(self):
        self.w, self.age = None, 0

    def step(self, obs):
        self.age += 1
        if obs.kind == "CUE":
            self.w = obs.value
        if obs.kind == "PROBE":
            return self.w or 0


show("  restart: a hidden step counter that capture omits and nothing uses", torture.restart_equivalence(HiddenLag, P))

print("################ G7.report: replay")
pool = [s for s in range(50000, 53000) if search.sample_reach("NEEDLE", "NEUTRAL", B, "COLD", [s]) == 0][:128]
print("   founders picked for having missed: %d found among %d tried; exact reach of NEEDLE/NEUTRAL is %.4f"
      % (len(pool), pool[-1] - 50000 + 1, search.exact_reach("NEEDLE", "NEUTRAL", B, "COLD")))
picked = {"claim": "REACH_BOUNDED", "landscape": "NEEDLE", "budget": B, "start_law": "COLD", "distance": 0,
          "scope": "POLICIES_AND_BUDGET", "upper_bound": stats.zero_hit_upper(128),
          "policies": {"STRICT": {"seeds": list(pool), "hits": 0}, "NEUTRAL": {"seeds": list(pool), "hits": 0}}}
show("N a null on the NEEDLE from 128 founders chosen after the fact because they missed", search.check_report(picked))
hitpool = [s for s in range(50000, 53000) if search.sample_reach("NEEDLE", "NEUTRAL", 100, "COLD", [s]) == 1][:128]
show("N a cold discovery from 128 founders chosen because they hit (budget 100; exact reach %.3f)"
     % search.exact_reach("NEEDLE", "NEUTRAL", 100, "COLD"),
     search.check_report({"claim": "COLD_DISCOVERY", "landscape": "NEEDLE", "budget": 100, "start_law": "COLD", "distance": 0,
                          "policies": {"NEUTRAL": {"seeds": hitpool, "hits": len(hitpool)}}}))
show("N a repair claim that declares distance 1 and states no distance travelled is fine; distance 0 (starts ON the target)",
     search.check_report(meta.report("REPAIR_REACH", "VALLEY", "REPAIR", 0, ("STRICT",))))
show("N a null whose two policies ran on different founders (64 and 128); bound stated for 128",
     search.check_report({"claim": "REACH_BOUNDED", "landscape": "VALLEY", "budget": B, "start_law": "COLD", "distance": 0,
                          "scope": "POLICIES_AND_BUDGET", "upper_bound": stats.zero_hit_upper(128),
                          "policies": {"STRICT": {"seeds": list(REP), "hits": 0}, "NEUTRAL": {"seeds": list(REP)[:64], "hits": 0}}}))
show("N a null with one founder per policy and the bound that warrants (0.95)",
     search.check_report({"claim": "REACH_BOUNDED", "landscape": "VALLEY", "budget": B, "start_law": "COLD", "distance": 0,
                          "scope": "POLICIES_AND_BUDGET", "upper_bound": 0.95,
                          "policies": {"STRICT": {"seeds": [1], "hits": 0}, "NEUTRAL": {"seeds": [1], "hits": 0}}}))
try:
    show("  a report on a landscape with a typo", search.check_report(dict(meta.report(), landscape="NEEDEL")))
    show("  a claim that is not one of the three", search.check_report(dict(meta.report(), claim="SUBSTRATE_INCAPABLE")))
except Exception as e:
    print("   raised", type(e).__name__, e)

print("################ G8: the fitted table and the margin")
for gap in (6, 8, 10, 12, 16, 20):
    r = torture.demand_closure(meta.DEMAND, meta.TRAIN, gap=gap, cue_from_distractors=True)
    print("   the cue is the xor of the last two distractors, gap %2d -> %-13s table %4d of 2048   (a two-step reader scores 2048)"
          % (gap, r.verdict, r.detail["TABLE"]))


class XorLastTwo(R.Register):
    def __init__(self):
        self.w, self.a, self.b = None, 0, 0

    def reset(self):
        self.a = self.b = 0

    def step(self, obs):
        if obs.kind == "DISTRACT":
            self.a, self.b = self.b, obs.value
        if obs.kind == "PROBE":
            return self.a ^ self.b


print("   at gap 20 a policy that reads the last two distractors scores %d of 64 and the world-side ruler calls it %s"
      % (R.score(XorLastTwo, meta.SEEDS, gap=20, cue_from_distractors=True),
         stats.classify(R.score(XorLastTwo, meta.SEEDS, gap=20, cue_from_distractors=True), 64, 0.5, 1e-6, 15 / 16)))
show("  clean world at gap 20", torture.demand_closure(meta.DEMAND, meta.TRAIN, gap=20))
for k in (1024 + 60, 1024 + 80, 1024 + 95, 1024 + 96, 1024 + 111, 1024 + 112):
    print("   a baseline right in %d of 2048 (%.3f): %s" % (k, k / 2048, stats.equivalence(k, 2048, 0.5, 0.1, 1e-6)))

print("################ G10.ruler: the registry and what is read from the receipts")
keys = json.loads((CF / KEYS).read_text())
print("   cells of RECEIPT_keys.json and the label the gate reads:")
for c in keys["cells"]:
    used = [m for m, s, src, a in audits.RUNS if src[0] == KEYS and src[2] == c]
    print("     %-62s label %-22s certified bits %6.2f  in the registry: %s"
          % (c, keys["verdicts"][c], keys["cells"][c]["certified_bits_carried"], used or "NO"))
bits = [r for r in audits.RUNS if "BITS" in r[3]]
for name in ("ACQUIRER(4)", "ACQUIRER(8)", "ACQUIRER(12)"):
    show("N BITS, with %s registered as the positive it is" % name,
         audits.ruler_status("BITS", "BITS@KEYS", CF, bits + [("KEY_" + name, "BITS@KEYS", (KEYS, "keys", name), {"BITS": "POSITIVE"})], {}))
g1 = json.loads((CF / G1).read_text())
print("   members of RECEIPT_gauntlet.json under v01_verdict:", {k: sorted(set(v.values())) for k, v in g1["result"]["v01_verdict"].items()})
g2 = json.loads((CF / G2).read_text())
g3 = json.loads((CF / G3).read_text())
print("   cells of run 2:", {k: v["verdict"] for k, v in g2["cells"].items()})
print("   cells of run 3:", {k: v["verdict"] for k, v in g3["cells"].items()})
print("   registry rows:", [(m, s, src[2]) for m, s, src, _ in audits.RUNS])
show("N the strong claim at run 2 with the builder REGISTERED as a positive and the selector as the negative",
     audits.ruler_status("STRONG", "S19@RUN2", CF, [("GENUINE", "S19@RUN2", (G2, "cell", "BUILDER"), {"STRONG": "POSITIVE"}),
                                                    ("SEL", "S19@RUN2", (G2, "cell", "SELECTOR"), {"STRONG": "NEGATIVE"})], {}))
for claim, setting in (("REUSE", "V01@RUN1"), ("REUSE", "S19@RUN2"), ("REUSE", "S19@RUN3"), ("STRONG", "S19@RUN3")):
    show("  %s at %s" % (claim, setting), audits.ruler_status(claim, setting, CF))

print("################ G9.arms / G10.setting / G10.contrast")
r3 = meta.run3()
import copy
reps = copy.deepcopy(r3["STRATEGIST"]["replicates"])
for i in range(3):
    for arm, d in (("lesion_B", 1), ("sham_B", 1), ("rescue_B", 2), ("v_donor_B", 3), ("irrelevant_history_B", 2)):
        reps[i][arm] += d
show("N run 3 arms nudged apart in three replicates of 24 (registered mutant: one)", audits.audit_arms(reps, meta.ARMS3))
show("S power registered as the integer 1", audits.audit_setting(dict(meta.SETTING_OK, power=1)))
show("N power registered as 0.99 with nothing computed", audits.audit_setting(dict(meta.SETTING_OK, power=0.99)))
show("S horizon registered as 3.0", audits.audit_setting(dict(meta.SETTING_OK, amortization_horizon=3.0)))
show("S a cell that registers every episode seed of 24 replicates (1,536 seeds)",
     registration.check_cell(meta.cell(registered_seeds=list(range(5000, 5000 + 24 * 64)))))
show("N design seeds repeated [1, 1, 2]", registration.check_cell(meta.cell(design_seeds=[1, 1, 2])))

print("################ G11 / G12")
show("N two custodian names for one person", claims.check_custody(meta.custody(discovery_custodian="J. Craig", confirmation_custodian="James Craig")))
show("N the acceptance rule fixed after discovery output was seen, before confirmation was opened (the fault document 1 confesses)",
     claims.check_custody(meta.custody(rule_fixed_at=15, confirmation_opened_at=20)))
show("N the filter on which worlds are used chosen after design runs (no field)", claims.check_custody(meta.custody(world_filter="chosen after design runs")))
show("N confirmation opened before discovery ended (no field for the end of discovery)", claims.check_custody(meta.custody(rule_fixed_at=0, confirmation_opened_at=1)))
other = {"note": "see the paper"}
show("N render: the setting AND its hash replaced together", claims.render(dict(meta.claim(), setting=other, setting_sha256=claims.setting_hash(other))))
show("N a NESTED claim: four facets typed PASS, each naming a file", claims.promote(meta.claim("NESTED"), 2))
show("N a 'structure' claim entered as kind EFFECT, exact_null typed PASS, asks for L2", claims.promote(meta.claim("EFFECT"), 2))
show("N a facet whose source is one space", claims.promote(meta.claim(demand={"verdict": PASS, "source": " "}), 1))
try:
    show("  a claim of a kind that is not registered", claims.render(dict(meta.claim(), kind="STRUCTURE")))
except Exception as e:
    print("   render of an unregistered kind raises", type(e).__name__, "instead of returning a verdict")
for kind in claims.KIND:
    print("   kind %-10s needs %s" % (kind, claims.KIND[kind]))
