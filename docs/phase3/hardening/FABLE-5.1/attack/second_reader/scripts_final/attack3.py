"""One more attack on the version-three gates (unchanged copy). Broken cases that PASS and are not in known_escapes(),
sound cases that are refused, and a few numbers the documents state."""
import copy
import functools
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, "harness")
from rso_harness import audits, claims, meta, registration as reg, retain1 as R, rulers, search, stats, torture  # noqa: E402
from rso_harness.verdict import BLOCKED, FAIL, PASS, Result  # noqa: E402

CF, P, SEEDS = meta.COUNTERFEIT, meta.PAIRS, meta.SEEDS


def show(tag, r):
    v = r if isinstance(r, str) else r.verdict
    why = "" if isinstance(r, str) or not r.reason else " | " + r.reason[:110]
    print("  %-104s -> %s%s" % (tag[:104], v, why))


print("known escapes listed:", len(meta.known_escapes()))
for e in meta.known_escapes():
    print("   ", e["gate"], "|", e["fault"][:95])

print("\nBROKEN CASES")
# G1.cell
show("G1.cell  no registered seed at all: registered_seeds=()", reg.check_cell(meta.cell(registered_seeds=())))
show("G1.cell  design seed '5000' (text) beside registered seed 5000", reg.check_cell(meta.cell(design_seeds=[1, 2, "5000"])))
show("G1.cell  every descriptive field a placeholder (tbd / ? / n/a)", reg.check_cell(meta.cell(
    physics="tbd", search="?", world="n/a", development="tbd", boundary="unknown", measurement="todo", adapter="tbd",
    independent_unit="?", resources="tbd")))
# G1.receipt
bad_cell = meta.cell(verdict_table={"n": 24, "outcomes": ["HOLDS"], "rule": [(0, 24, "HOLDS")]}, known_answers={})
show("G1.cell  (control) a cell whose table can only say HOLDS and that registers no known answer", reg.check_cell(bad_cell))
show("G1.receipt  a receipt checked against that cell", reg.check_receipt(bad_cell, meta.run_receipt(), meta.SOURCE))
# G4.entry
show("G4.entry  a 'positive' that is right in its first 64 episodes and wrong ever after",
     meta.entry("REGISTER", dict(R.PANEL, REGISTER=(type("Short", (R.scripted(64),), {"physics": "REGISTER"}), R.RegisterImpostor))))
# G6.observer
def impostor_only(log):
    def observe(world, seed, t, org):
        if "Impostor" in type(org).__name__ or isinstance(org, R.FadingRegister):
            world.draw(seed)
    return observe
show("G6.observer  an observer that draws from the world's stream only when the organism is an impostor or the weak positive",
     meta.all_positives(lambda m: torture.observer_equivalence(m, P, impostor_only)))
show("    (the same observer, run on an impostor)", torture.observer_equivalence(R.RegisterImpostor, P, impostor_only))
# G7.calibration
def panel_only(landscape, policy, budget, kind, seeds, distance=0):
    on_panel = (landscape, policy, kind, distance) in search.CELLS and budget == meta.BUDGET
    return search.sample_reach(landscape, policy, budget, kind, seeds, distance) if on_panel else 0
show("G7.calibration  an estimator that searches on the five panel cells at budget 400 and reports 0 anywhere else",
     search.calibration_panel(meta.BUDGET, meta.FOUNDERS, panel_only))
show("    (what it reports for NEEDLE/STRICT/REPAIR(1), exact reach %.4f)" % search.exact_reach("NEEDLE", "STRICT", 400, "REPAIR", 1),
     str(panel_only("NEEDLE", "STRICT", 400, "REPAIR", meta.FOUNDERS, 1)) + " of 256")
# G7.report
show("G7.report  a discovery whose budget (2,000 proposals) is the report's own choice: nothing registers a budget",
     meta.checked(meta.report(budget=2000)))
show("G7.report  a null whose stated bound is 1.0 (it bounds nothing)", meta.checked(meta.null(upper_bound=1.0)))
show("G7.report  a null whose stated bound is True", meta.checked(meta.null(upper_bound=True)))
# G8.demand
show("G8.demand  the environment keeps what is written; a constant is entered under the name WORLD_PARKER",
     torture.demand_closure(meta.DEMAND, meta.TRAIN, baselines=dict(R.BASELINES, WORLD_PARKER=R.Constant, TABLE=None), writable_mark=True))
# G9.arms
r3 = meta.run3()["STRATEGIST"]["replicates"]
off = copy.deepcopy(r3)
for o in off:
    for i, arm in enumerate(meta.ARMS3):
        o[arm] += 7 * i
show("G9.arms  run 3's eight arms (three computations) reported with a constant offset per arm", audits.audit_arms(off, meta.ARMS3))
# G9.clauses
def big(change=None):
    return {"replicates": [dict(meta.TOY) for _ in range(22)] + [dict(meta.TOY, dev_B=90, sham_B=400, lesion_B=10) for _ in range(218)]
            if change is None else
            [dict(meta.TOY, **change) for _ in range(12)] * 0 + [dict(meta.TOY) for _ in range(22)]
            + [dict(meta.TOY, **change) for _ in range(218)]}
cells240 = {"GOOD": {"replicates": [dict(meta.TOY) for _ in range(22)] + [dict(meta.TOY, dev_B=90, sham_B=400, lesion_B=10) for _ in range(218)]}}
for name, change in meta.ISOLATING.items():
    # in each isolating cell: the named clause true in 12 of 240, the other clauses true in 22 of 240
    reps = [dict(meta.TOY) for _ in range(12)] + [dict(meta.TOY, **change) for _ in range(10)] + \
           [dict(meta.TOY, dev_B=90, sham_B=400, lesion_B=10) for _ in range(218)]
    cells240[name] = {"replicates": reps}
r = audits.audit_clauses(cells240, meta.toy_clauses)
show("G9.clauses  240 replicates per cell; every clause 'holds' where it is true in 22 of 240 (9%)", r)
print("       clause table:", {c: dict(v) for c, v in r.detail["table"].items()})
# G10.ruler
K = audits.KEYS
show("G10.ruler  STRONG 'qualified' at a new setting from two rows that point at run 4's key cells",
     audits.ruler_status("STRONG", "S19@NEW", CF, [("GENUINE_LEARNED_UPDATER", "S19@NEW", (K, "keys", "ACQUIRER(16)"), {"STRONG": "POSITIVE"}),
                                                  ("PROCEDURE_SELECTOR", "S19@NEW", (K, "keys", "ELIM"), {"STRONG": "NEGATIVE"})], {}))
# G11.custody
show("G11.custody  confirmation seeds '1','2','3' (text) against discovery seeds 1, 2, 3",
     claims.check_custody(meta.custody(confirmation=meta.side(seeds=["1", "2", "3"]))))
# G12.render
show("G12.render  the class excluded is one space", claims.render(dict(meta.claim(), excluded_class=" ")))
show("G12.render  the cell is one space", claims.render(dict(meta.claim(), cell=" ")))
# G5
class RegisterNoRestore(R.Register):
    def restore(self, state):
        pass
show("G5 (control) interchange, with a positive whose restore does nothing entered as the REGISTER impostor",
     meta.neutral("INTERCHANGE", ["REGISTER"], dict(R.PANEL, REGISTER=(R.Register, RegisterNoRestore))))
# G6.restart
class PatternBadCapture(R.Lattice):
    """Capture drops the step counter only in episodes whose first three distractors were all ones."""
    def __init__(self):
        R.Lattice.__init__(self); self.ones = 0
    def reset(self):
        R.Lattice.reset(self); self.ones = 0
    def perturb(self, obs):
        if obs.kind == "DISTRACT" and self.t <= 3 and obs.value:
            self.ones += 1
        R.Lattice.perturb(self, obs)
    def capture(self):
        return (tuple(self.cells), 0 if self.ones == 3 else self.t)
print("     (seeds in PAIRS whose first three distractors are all ones:",
      [s for s in P if all(R.World().episode(R.Recorder(), s)["trace"][i][1] for i in (1, 2, 3))], ")")
show("G6.restart  a capture that is wrong only when the first three distractors are all ones", torture.restart_equivalence(PatternBadCapture, P))
more = [s for s in range(2012, 2200) if all(R.World().episode(R.Recorder(), s)["trace"][i][1] for i in (1, 2, 3))][:3]
show("    (the same runtime on three seeds that have that pattern: %s)" % more, torture.restart_equivalence(PatternBadCapture, more))

print("\nSOUND CASES")
toy = [dict(meta.TOY, sham_B=meta.TOY["dev_B"]) for _ in range(24)]
row = audits.clause_table(meta.toy_cells(**meta.ISOLATING), meta.toy_clauses)["NESTING.sham_harmless"]
show("G9.sham   a sham that changes nothing: sham_B == dev_B in 24 of 24 replicates", audits.audit_sham(toy, row))
show("G9.arms   the same replicates", audits.audit_arms(toy, ("naive_B", "dev_B", "sham_B", "lesion_B")))
half = {k: {"replicates": v["replicates"][:12]} for k, v in meta.toy_cells(**meta.ISOLATING).items()}
show("G9.clauses  the registered sound toy with 12 replicates per cell", audits.audit_clauses(half, meta.toy_clauses))
show("G1.cell   design seeds given as a tuple", reg.check_cell(meta.cell(design_seeds=(1, 2, 3))))
show("G4.entry  a sound pair supplied through functools.partial",
     meta.entry("REGISTER", dict(R.PANEL, REGISTER=(functools.partial(R.Register), functools.partial(R.RegisterImpostor)))))
show("G7.report a null whose bound is rounded to three places (0.023)", meta.checked(meta.null(upper_bound=0.023)))
show("G12.render a registered setting quoted with a number where the registration has a string ('1e-6' vs 1e-06)",
     claims.render(dict(meta.claim(), setting=dict(meta.SETTING, alpha=1e-6))))

print("\nNUMBERS THE DOCUMENTS STATE")
t = meta.table()
for h, n in ((480, 480), (240, 240), (466, 480)):
    p = min(stats.outcome_probability(t, rate)["HOLDS"] for rate in (stats.lower_bound(h, n), stats.upper_bound(h, n)))
    print("  attainability of HOLDS with %d of %d design units: %.4f" % (h, n, p))
print("  positive control (ASCENT, cold) at budgets 5, 24, 46, 47:", ["%.4f" % search.exact_reach("ASCENT", "STRICT", b, "COLD") for b in (5, 24, 46, 47)])
b = meta.bracket()
print("  bracket by organisms:", b["by_organisms"], "| at registered thresholds:", b["at_registered_thresholds"], "| impostor series:", b["impostor_series"],
      "| impostor scores:", b["impostor_scores"], "| weak:", b["weak_positive_score"])
rows = meta.qualify()
print("  gates %d, sound %d, mutants %d, status all PASS: %s" % (len(rows), sum(r["clean"] for r in rows.values()),
      sum(r["mutants"] for r in rows.values()), all(r["status"] == PASS for r in rows.values())))
import collections
print("  mutant verdicts:", dict(collections.Counter(m["verdict"] for r in rows.values() for m in r["mutant_verdicts"])))
print("  gates whose mutants include INDETERMINATE:", sorted(g for g, r in rows.items() if any(m["verdict"] == "INDETERMINATE" for m in r["mutant_verdicts"])))
