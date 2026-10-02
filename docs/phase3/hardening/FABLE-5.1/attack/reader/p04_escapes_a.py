exec(open(__file__.replace("p04_escapes_a.py", "drv.py")).read())
from rso_harness import stats, retain1, rulers, search, torture, audits, claims, registration
from rso_harness.verdict import *
def show(tag, r): print("%-78s -> %s %s" % (tag, r.verdict, ("| " + r.reason) if r.reason else ""))
print("################ G1.cell")
c = meta.cell
show("clean", registration.check_cell(c()))
show("E power declared for one answer only {'positive':1.0}", registration.check_cell(c(power={"positive": 1.0})))
show("E power is NaN", registration.check_cell(c(power={"positive": float("nan"), "impostor": float("nan")})))
show("E power 99 (percent)", registration.check_cell(c(power={"positive": 99, "impostor": 99})))
show("E registered seeds repeated [1000,1000,1000]", registration.check_cell(c(registered_seeds=[1000, 1000, 1000])))
show("E table emits unregistered outcome BANANA at count 21", registration.check_cell(c(verdict_table=meta.table([(22, 24, "HOLDS"), (0, 12, "FAILS"), (13, 20, "INDETERMINATE"), (21, 21, "BANANA")]))))
show("E exposure = 'unknown' (string)", registration.check_cell(c(exposure="unknown")))
show("E measurement alpha 1e-6 but table n=24, power self-declared 1.0 with 16 episodes", registration.check_cell(c(world="RETAIN-1 gap 6, 16 episodes")))
show("S sound: no design runs were made, design_seeds=[]", registration.check_cell(c(design_seeds=[])))
show("S sound: zero exposure declared as {}", registration.check_cell(c(exposure={})))
show("precedence: missing exposure AND shared seed (FAIL should outrank BLOCKED)", registration.check_cell(c(exposure=None, design_seeds=[1, 2, 1000])))
print("################ G1.receipt")
show("clean", registration.check_receipt(c(), meta.run_receipt()))
show("E receipt ran_at == registered_at + 1 but self-reported hash copied", registration.check_receipt(c(), meta.run_receipt(ran_at=101)))
show("S sound: same clock tick ran_at == registered_at", registration.check_receipt(c(), meta.run_receipt(ran_at=100)))
show("E receipt seeds duplicate-padded [1000,1001,1002] vs registered dupes", registration.check_receipt(c(registered_seeds=[1000, 1000, 1001]), meta.run_receipt(seeds=[1000, 1001, 1000])))
print("################ G2.preflight")
show("clean", stats.preflight(64, 0.5, 1e-6, 1.0))
show("E positive declared at 1.0 but n=20 (minimum reachable)", stats.preflight(20, 0.5, 1e-6, 1.0))
show("  positive at 0.89 n=64", stats.preflight(64, 0.5, 1e-6, 0.89))
show("  positive at 0.88 n=64", stats.preflight(64, 0.5, 1e-6, 0.88))
show("E alpha=0.5 (ruler says yes to half the class) p0=.5", stats.preflight(64, 0.5, 0.5, 1.0))
show("E alpha=0.011", stats.preflight(64, 0.5, 0.011, 1.0))
show("  alpha=0.0099", stats.preflight(64, 0.5, 0.0099, 1.0))
print("################ G3.exclusion (scope)")
show("clean", meta.scope(rulers.exclusion_ruler))
always = lambda make, seeds: "POSITIVE"
show("E always-POSITIVE ruler on a panel with no impostors", meta.scope(always, {k: (v[0], None) for k, v in retain1.PANEL.items()}))
show("E always-POSITIVE ruler on an empty panel", meta.scope(always, {}))
for b in (0.20, 0.22, 0.23, 0.24, 0.25, 0.30, 0.60, 0.75, 0.80, 0.805, 0.81, 0.82):
    show("  loose bound %.3f" % b, meta.scope(meta.loose_exclusion(b)))
for b in (0.25, 0.75, 0.80):
    k = stats.critical_k(64, b, 1e-6)
    print("     bound %.2f: critical k=%s; P(impostor at 0.5 reaches it)=%.4f ; power for a positive at 0.9 = %.4f" % (b, k, stats.tail_ge(64, k, 0.5), stats.tail_ge(64, k, 0.9)))
print("################ G4.entry")
class Inverter(retain1.Register):
    """Holds the cue perfectly and answers its complement."""
    def step(self, obs):
        if obs.kind == "CUE": self.w = obs.value
        if obs.kind == "PROBE": return 1 - (self.w or 0)
print("  Inverter score of 64:", retain1.score(Inverter, meta.SEEDS))
show("E impostor = Inverter (retains the bit perfectly, answers complement)", meta.entry("REGISTER", dict(retain1.PANEL, REGISTER=(retain1.Register, Inverter))))
show("E impostor not matched: PACKET impostor = Constant", meta.entry("PACKET", dict(retain1.PANEL, PACKET=(retain1.PacketRing, retain1.Constant))))
show("E CHEMISTRY admitted on register organisms", meta.entry("CHEMISTRY", {"CHEMISTRY": (retain1.Register, retain1.RegisterImpostor)}))
show("S sound positive, 16 seeds (verdict unreachable): FAIL instead of BLOCKED", rulers.entry_gate("REGISTER", retain1.PANEL, list(range(1000, 1016))))
show("S sound positive, 19 seeds", rulers.entry_gate("REGISTER", retain1.PANEL, list(range(1000, 1019))))
print("  exclusion_ruler on Register with 16 seeds:", rulers.exclusion_ruler(retain1.Register, list(range(1000, 1016))))
print("################ G5.neutrality")
three = {"A": (retain1.Register, retain1.RegisterImpostor), "B": (retain1.Register, retain1.RegisterImpostor), "C": (retain1.Register, retain1.RegisterImpostor)}
show("E REGISTER_SWAP declared SHARED on three look-alike physics", rulers.neutrality_gate("REGISTER_SWAP", rulers.register_swap_ruler, "SHARED", three, meta.PAIRS))
class WordAttractor(retain1.Register): physics = "ATTRACTOR-LIKE"
class WordPacket(retain1.Register): physics = "PACKET-LIKE"
three2 = {"REGISTER": retain1.PANEL["REGISTER"], "ATTRACTOR": (WordAttractor, retain1.RegisterImpostor), "PACKET": (WordPacket, retain1.RegisterImpostor)}
show("E REGISTER_SWAP SHARED, three physics that all keep an attribute w", rulers.neutrality_gate("REGISTER_SWAP", rulers.register_swap_ruler, "SHARED", three2, meta.PAIRS))
show("E declared valid nowhere []", rulers.neutrality_gate("REGISTER_SWAP", rulers.register_swap_ruler, [], retain1.PANEL, meta.PAIRS))
five = dict(retain1.PANEL, CHEMISTRY=(None, None))
show("S CLASS_EXCLUSION SHARED, right on 4 physics, a 5th registered with no organism", rulers.neutrality_gate("CLASS_EXCLUSION", rulers.exclusion_ruler, "SHARED", five, meta.SEEDS))
show("E always-NEGATIVE ruler declared valid in [] ", rulers.neutrality_gate("X", lambda m, s: "NEGATIVE", [], retain1.PANEL, meta.PAIRS))
inv_panel = dict(retain1.PANEL, REGISTER=(retain1.Register, Inverter))
show("E interchange ruler, impostor = Inverter", rulers.neutrality_gate("INTERCHANGE", rulers.interchange_ruler, "SHARED", inv_panel, meta.PAIRS))
show("E class exclusion, impostor = Inverter", rulers.neutrality_gate("CLASS_EXCLUSION", rulers.exclusion_ruler, "SHARED", inv_panel, meta.SEEDS))
