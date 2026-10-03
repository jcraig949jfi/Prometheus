"""Round 3: closure probes for N4, N7-N10, N12, N19, N24-N28, M22, M27, M29-M31 on the third version."""
import copy
import json

from drv import *

R = retain1
P = meta.PAIRS
p_ok = dict(R.PANEL)
G1, G2, G3, KEYS = audits.G1, audits.G2, audits.G3, audits.KEYS
REP, B = meta.REPORTED, meta.BUDGET

print("################ N4 / M29: G10.ruler")
keys = json.loads((CF / KEYS).read_text())
print("   RUNS rows: %d; per receipt: %s" % (len(audits.RUNS), {n: sum(1 for r in audits.RUNS if r[2][0] == n) for n in (G1, G2, G3, KEYS)}))
for c in keys["cells"]:
    used = [(m, a) for m, s, src, a in audits.RUNS if src[0] == KEYS and src[2] == c]
    print("     %-62s label %-24s bits %6.2f  registry %s  returned %s"
          % (c, keys["verdicts"][c], keys["cells"][c]["certified_bits_carried"], used, audits.returned(CF, (KEYS, "keys", c))))
for claim, setting in (("BITS", "BITS@KEYS"), ("STRONG", "V01@RUN1"), ("STRONG", "S19@RUN2"), ("STRONG", "S19@RUN3"),
                       ("REUSE", "S19@RUN2"), ("REUSE", "BITS@PAIRS"), ("COMBINATION", "BITS@PAIRS"),
                       ("BITS_TWO_BOUNDARIES", "BITS@TWO"), ("STRONG", "BITS@KEYS"), ("BITS", "S19@RUN2")):
    r = audits.ruler_status(claim, setting, CF)
    show("  %s at %s  answered=%s" % (claim, setting, r.detail["answered"]), r)
g1 = json.loads((CF / G1).read_text())
g2 = json.loads((CF / G2).read_text())
g3 = json.loads((CF / G3).read_text())
print("   run1 members:", sorted(g1["result"]["v01_verdict"]), "| run2 cells:", sorted(g2["cells"]), "| run3 cells:", sorted(g3["cells"]))
print("   cells in receipts: %d" % (len(g1["result"]["v01_verdict"]) + len(g2["cells"]) + len(g3["cells"]) + len(keys["cells"])))
# sensitivity: one positive flipped by hand; and a ruler with one negative only
bits = [r for r in audits.RUNS if "BITS" in r[3]]
show("N a BITS kit of one positive and one negative only (two cells of nine)",
     audits.ruler_status("BITS", "BITS@KEYS", CF, [bits[3], bits[4]], {}))
show("N STRONG at run 2 with only the four cells the steps rejected (no positive answered, none exists)",
     audits.ruler_status("STRONG", "S19@RUN2", CF, [r for r in audits.RUNS if r[1] == "S19@RUN2" and audits.returned(CF, r[2]) == "NEGATIVE"], {}))
# a guard label dropped from the receipt copy: does the gate depend on labels?
print("   GUARDS:", audits.GUARDS, "| labels in receipt:", sorted(set(keys["verdicts"].values())))

print("################ N7 / M22: G8 demand closure")
for gap in (6, 8, 10, 12, 16, 20):
    r = torture.demand_closure(meta.DEMAND, meta.TRAIN, gap=gap, cue_from_distractors="last2")
    print("   xor of the last two, gap %2d -> %-13s %s" % (gap, r.verdict, r.reason[:110]))
for gap in (6, 8, 10, 12, 20):
    r = torture.demand_closure(meta.DEMAND, meta.TRAIN, gap=gap)
    print("   CLEAN world, gap %2d -> %-13s %s" % (gap, r.verdict, r.reason[:110]))
for gap in (6, 8, 12):
    r = torture.demand_closure(meta.DEMAND, meta.TRAIN, gap=gap, cue_from_distractors="all")
    print("   parity of all, gap %2d -> %-13s %s" % (gap, r.verdict, r.reason[:110]))
for leak in ("parity", "bit1", "bit3"):
    r = torture.demand_closure(meta.DEMAND, meta.TRAIN, leak_clock=leak)
    print("   clock leak %-7s -> %-13s %s" % (leak, r.verdict, r.reason[:110]))


_BaseWorld = R.World


class MidXorWorld(_BaseWorld):
    """Fault of my own: the cue is the xor of distractors 6 and 7 of a gap of 12 (neither early nor recent)."""

    def episode(self, org, seed, observer=None, cue=True, force_bit=None, interrupt=None):
        if force_bit is None:
            # with force_bit set the world draws no cue, so distractor i is draw i of the episode
            planned = [khash(seed, i) & 1 for i in range(1, self.gap + 1)]
            force_bit = planned[5] ^ planned[6]
        return _BaseWorld.episode(self, org, seed, observer=observer, cue=cue, force_bit=force_bit, interrupt=interrupt)


_orig = torture.World
torture.World = MidXorWorld
R_score_world = R.World
R.World = MidXorWorld
try:
    r = torture.demand_closure(meta.DEMAND, meta.TRAIN, gap=12)
    print("   N cue = xor of distractors 6 and 7 of a gap of 12 -> %-13s %s" % (r.verdict, r.reason[:140]))

    class MidReader(R.Register):
        def __init__(self):
            self.w, self.seen = None, []

        def reset(self):
            self.w, self.seen = None, []

        def step(self, obs):
            if obs.kind == "DISTRACT":
                self.seen.append(obs.value)
            if obs.kind == "PROBE":
                return self.seen[5] ^ self.seen[6]

    print("     a policy that reads those two distractors scores %d of 64" % R.score(MidReader, meta.SEEDS, gap=12))
finally:
    torture.World = _orig
    R.World = R_score_world

print("################ N8 / M27: G7.report")
picked = meta.missers()
show("  null on NEEDLE, the report's own cherry-picked founders, registered = REPORTED",
     meta.checked(meta.null("NEEDLE", seeds=picked)))
show("  the same when the registration itself holds the cherry-picked founders",
     meta.checked(meta.null("NEEDLE", seeds=picked), picked))
hitpool = [s for s in range(50000, 56000) if search.sample_reach("NEEDLE", "NEUTRAL", 100, "COLD", [s]) == 1][:128]
rep = {"claim": "COLD_DISCOVERY", "landscape": "NEEDLE", "budget": 100, "start_law": "COLD", "distance": 0,
       "policies": {"NEUTRAL": {"seeds": hitpool, "hits": len(hitpool)}}}
show("N discovery, 128 of 128, founders REGISTERED because they hit (exact reach %.3f at budget 100)"
     % search.exact_reach("NEEDLE", "NEUTRAL", 100, "COLD"), search.check_report(rep, hitpool))
show("  repair claim at distance 0", meta.checked(meta.report("REPAIR_REACH", "VALLEY", "REPAIR", 0, ("STRICT",))))
rev = meta.report()
rev["policies"]["NEUTRAL"]["seeds"] = list(reversed(REP))
show("S sound: the registered founders reported in another order (same set, same hits)", meta.checked(rev))
show("N null with founders = registered, but only 2 registered founders, bound 0.7764",
     search.check_report(meta.null(seeds=[1, 2], upper_bound=stats.zero_hit_upper(2)), [1, 2]))
show("N a REPAIR_REACH claim that reports 0 hits of 128 (nothing repaired) on VALLEY/NEUTRAL distance 3",
     meta.checked(meta.report("REPAIR_REACH", "VALLEY", "REPAIR", 3, ("NEUTRAL",))))
print("     hits there:", meta.hits("VALLEY", "NEUTRAL", "REPAIR", 3))
show("N null whose stated bound is 1.0 (says nothing) on NEEDLE/STRICT+ELITIST... two ascent-only -> BLOCKED expected",
     meta.checked(meta.null("NEEDLE", ("STRICT", "ELITIST"), upper_bound=1.0)))
show("N null on VALLEY with bound 1.0", meta.checked(meta.null(upper_bound=1.0)))

print("################ N9: G6.observer")
show("  healing observer", meta.all_positives(lambda m: torture.observer_equivalence(m, P, torture.healing_observer)))
show("  hidden-field observer (pinned)", meta.all_positives(lambda m: torture.observer_equivalence(m, P, torture.hidden_observer)))
show("  later-episodes observer", meta.all_positives(lambda m: torture.observer_equivalence(m, P, torture.later_episodes_observer)))


def swap_and_restore(log):
    """Mine: flips the stored word and flips it back inside one observer call. Nothing recorded differs."""
    def observe(world, seed, t, org):
        if hasattr(org, "w") and org.w is not None:
            org.w ^= 1
            org.w ^= 1
    return observe


def last_step_only(log):
    """Mine: rewrites the organism at the last step of the LAST checked seed only."""
    def observe(world, seed, t, org):
        if seed == P[-1] and t == world.gap + 1 and hasattr(org, "w"):
            org.w = 1 - (org.w or 0)
    return observe


show("  observer that rewrites the word at the last step of the last seed only",
     meta.all_positives(lambda m: torture.observer_equivalence(m, P, last_step_only)))


def slow_observer(log):
    """Mine: the observer costs host time (a busy loop). The gate has no notion of host cost or timing."""
    def observe(world, seed, t, org):
        sum(range(2000))
    return observe


show("N observer that burns host time at every step (timing/cost is not compared)",
     meta.all_positives(lambda m: torture.observer_equivalence(m, P, slow_observer)))

print("################ N10: G3 thresholds")
print("   bracket:", {k: v for k, v in meta.bracket().items()})
ok_alpha = [a for a in (1e-9, 1e-8, 3e-7, 5e-7, 8e-7, 9e-7, 9.4e-7, 9.5e-7, 1e-6, 1.5e-6, 2e-6, 3e-6, 5e-6, 1e-5, 1e-4, 1e-3, 1e-2)
            if meta.exclusion(rulers.make_exclusion_ruler(alpha=a)).verdict == PASS]
print("   alphas in the ruler that still PASS G3:", ok_alpha)
ok_weak = [w for w in (0.80, 0.85, 0.90, 0.92, 0.93, 0.935, 0.9375, 0.94, 0.945, 0.95, 0.96, 0.97, 0.99)
           if meta.exclusion(rulers.make_exclusion_ruler(weakest=w)).verdict == PASS]
print("   weakest-positive rates in the ruler that still PASS G3:", ok_weak)
ok_bound = [b / 1000 for b in range(480, 521) if meta.exclusion(rulers.make_exclusion_ruler(b / 1000)).verdict == PASS]
print("   bounds (grid 0.001) that still PASS G3 with the registered EDGES:", ok_bound)
show("  G3 with no weak positive", meta.exclusion(weak=None))
show("N G3 with the weak positive replaced by a PERFECT positive (the 'weak' one is not weak)", meta.exclusion(weak=R.Register))
show("N G3 with EDGES that hold only two thresholds {51: POSITIVE, 13: INVERTED}", meta.exclusion(edges={51: "POSITIVE", 13: "INVERTED"}))
show("N G3 with one further block only", meta.exclusion(blocks=[meta.BLOCKS[0]]))

print("################ N12: attainability and what is declared")
show("  rates declared", registration.check_cell(meta.cell(known_answers={"HOLDS": 1.0, "FAILS": 0.0})))
show("  design counts typed (pinned)", registration.check_cell(meta.cell(known_answers={"HOLDS": meta.runs(480, 480), "FAILS": meta.runs(0, 480)})))
show("N design counts typed with design_seeds = [] (no design runs were made, by the cell's own statement)",
     registration.check_cell(meta.cell(design_seeds=[], known_answers={"HOLDS": meta.runs(480, 480), "FAILS": meta.runs(0, 480)})))
show("N design_n = 480 while the cell lists three design seeds", registration.check_cell(meta.cell(design_seeds=[1, 2, 3])))
show("  power typed 0.99 on run 3 (pinned)", audits.audit_setting(dict(audits.RUN3, power=0.99, amortization_horizon=3)))

print("################ N19: who computes INDETERMINATE")
r = meta.neutral("CLASS_EXCLUSION", "SHARED", dict(p_ok, REGISTER=(R.scripted(49), R.RegisterImpostor)))
show("  G5.neutrality with a positive that scores 49 of 64", r)
r = search.calibration_panel(B, meta.FOUNDERS)
print("   G7.calibration verdicts possible: PASS/FAIL/BLOCKED only" )
r = audits.audit_clauses(meta.toy_cells(**meta.CATCH_ALL), meta.toy_clauses)
show("  G9.clauses catch-all", r)

print("################ N24: keeper")
for lives in (300, 1000, 4000):
    rows = ladder.run(ladder.Keeper, lives, "ROTATION")
    c = ladder.certificate([r[2] for r in rows])
    print("   KEEPER, ROTATION, %4d lives: mean %.3f threshold %.3f -> %s" % (lives, c["mean"], c["threshold"], c["answer"]))

print("################ N25 / N26 / N27 / N28")
show("  design seeds repeated", registration.check_cell(meta.cell(design_seeds=[1, 1, 2])))
show("  power = 1 (int), horizon 3.0", audits.audit_setting(dict(meta.SETTING_OK, power=1, amortization_horizon=3.0)))
show("  power = True", audits.audit_setting(dict(meta.SETTING_OK, power=True)))
show("  a cell that registers every episode seed of 24 replicates (1,536 seeds)",
     registration.check_cell(meta.cell(registered_seeds=list(range(5000, 5000 + 24 * 64)))))
try:
    show("  render of an unregistered kind", claims.render(dict(meta.claim(), kind="STRUCTURE")))
except Exception as e:
    print("   render of an unregistered kind raises", type(e).__name__)
show("  reset that leaks every third call (pinned)", torture.reset_closure(R.EveryThirdReset, P))
show("  weak carrier as impostor (pinned)", meta.entry("REGISTER", dict(R.PANEL, REGISTER=(R.Register, R.weak_carrier()))))
show("  restart, capture wrong after the last step only", torture.restart_equivalence(R.LatticeEndBadCapture, P))
tick = [m for m in meta.qualify()["G1.receipt"]["mutant_verdicts"] if "clock tick" in m["mutant"]]
print("   clock-tick case in the registry:", tick)
ind = [(g, m["mutant"]) for g, row in meta.qualify().items() for m in row["mutant_verdicts"] if m["verdict"] == INDETERMINATE]
print("   the %d INDETERMINATE 'broken' cases:" % len(ind))
for g, m in ind:
    print("      %-12s %s" % (g, m))

print("################ M30 / M31")
r3 = meta.run3()
for k in (1, 2, 3, 4):
    show("  run 3 arms nudged in %d replicate(s)" % k, audits.audit_arms(meta.nudged(r3["STRATEGIST"]["replicates"], k), meta.ARMS3))
show("  two custodian names for one person", claims.check_custody(meta.custody(discovery_custodian="J. Craig", confirmation_custodian="James Craig")))
show("  custodians differing in case only", claims.check_custody(meta.custody(discovery_custodian="keeper", confirmation_custodian="Keeper")))
other = {"note": "see the paper"}
show("  render: setting and hash replaced together (pinned)", claims.render(dict(meta.claim(), setting=other, setting_sha256=claims.setting_hash(other))))
show("  a TRANSFER claim with exact_null UNQUALIFIED asks L2", claims.promote(meta.claim("TRANSFER", exact_null=UNQUALIFIED), 2))
show("N a claim about structure entered as EFFECT, exact_null typed PASS, asks L2", claims.promote(meta.claim("EFFECT"), 2))
c = meta.claim("NESTED")
print("   level of a NESTED claim with all facets typed PASS:", claims.level(c), "| render:", claims.render(c).reason[:90])
c2 = meta.claim("EFFECT", level=4)
c2["facets"].pop("exact_null")
print("   a claim with L1, L3, L4 facets and no exact_null stands at level:", claims.level(c2))
show("N L3 asked for a claim lacking an L2 facet (custody) but holding 'reproduced'",
     claims.promote(meta.claim(level=3, drop="custody"), 3))
show("N excluded_class is any non-empty string ('n/a')", claims.render(dict(meta.claim(), excluded_class="n/a")))
