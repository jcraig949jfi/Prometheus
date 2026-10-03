"""GM. The gates are rulers too: each must pass a clean case and reject a case broken on purpose.

A gate with no broken case is UNQUALIFIED: it has never been shown able to fail. A gate that passes a
broken case has an escape. A gate that rejects a clean case makes false accusations. qualify() runs
every gate against its registered clean cases and mutants and returns one row per gate.

Where the cases come from. The first version of this registry held only cases written by the author
of the gates. An adversarial reader then wrote its own and found escapes or false accusations in
most gates. Its cases are now registered here beside the author's. Faults it showed that the gates
still cannot catch are in known_escapes(), each run and pinned by a test, so that a passing harness
is not read as covering them.

Several mutants are not invented. They are this reviewer's own runs 1 to 3, read from their receipts.
"""
import copy
import json
import os
import pathlib

from . import audits, claims, registration, retain1, rulers, search, stats, torture
from .verdict import BLOCKED, FAIL, INDETERMINATE, PASS, UNQUALIFIED, Result

HERE = pathlib.Path(__file__).resolve().parent
# The receipts of the review. RSO_COUNTERFEIT lets a copy of the harness made elsewhere find them.
COUNTERFEIT = pathlib.Path(os.environ.get("RSO_COUNTERFEIT") or
                           HERE.parents[2].parent / "review" / "FABLE-5.1" / "counterfeit")
SEEDS = list(range(1000, 1064))                                        # 64 episodes for class exclusion
BLOCKS = [list(range(1100 + 64 * i, 1164 + 64 * i)) for i in range(8)]  # eight further blocks for the impostors
PAIRS = list(range(2000, 2012))                                        # 12 seeds for interchange and torture
FOUNDERS = list(range(3000, 3256))                                     # 256 independent founders for calibration
REPORTED = list(range(4000, 4128))                                     # 128 founders in a search report
DEMAND = list(range(10000, 12048))                                     # 2,048 episodes for demand closure
TRAIN = list(range(20000, 22048))                                      # 2,048 others to fit the table baseline
BUDGET = 400
SOURCE = b"the registered code of the run\n"
# What must be required, spelled out here and not read from the gates' own lists: a gate that
# drops a name from its list must be caught by these.
CELL_FIELDS = ("physics", "search", "world", "development", "boundary", "resources", "measurement", "exposure",
               "adapter", "independent_unit", "design_seeds", "registered_seeds", "verdict_table", "known_answers",
               "source_sha256", "registered_at")
CUSTODY_FIELDS = ("discovery", "confirmation", "selection_data", "claim", "tuning_evaluations", "tuning_budget",
                  "rule_fixed_at", "confirmation_opened_at", "discovery_custodian", "confirmation_custodian")
BASELINES_REQUIRED = ("CONSTANT", "CLOCK", "KEY_READER", "WORLD_PARKER", "TABLE")


def receipt(name):
    return json.loads((COUNTERFEIT / name).read_text(encoding="ascii"))


# ---------------------------------------------------------------- fixtures: registration

def table(rule=None, outcomes=("HOLDS", "FAILS", "INDETERMINATE")):
    return {"n": 24, "outcomes": list(outcomes),
            "rule": rule or [(22, 24, "HOLDS"), (0, 12, "FAILS"), (13, 21, "INDETERMINATE")]}


def cell(**change):
    c = {"physics": "REGISTER", "search": "none (designed)", "world": "RETAIN-1, gap 6", "development": "none",
         "boundary": "internal; environment writes certified zero", "resources": {"steps": 8},
         "measurement": "a replicate passes if its organism excludes the class", "exposure": {"tuning_evaluations": 0},
         "adapter": "symbolic", "independent_unit": "replicate", "design_seeds": [1, 2, 3],
         "registered_seeds": list(range(5000, 5024)), "verdict_table": table(),
         "known_answers": {"HOLDS": 0.999, "FAILS": 0.2},
         "source_sha256": registration.sha(SOURCE), "registered_at": 100}
    c.update(change)
    return c


def run_receipt(**change):
    r = {"source_sha256": registration.sha(SOURCE), "seeds": list(range(5000, 5024)), "ran_at": 200}
    r.update(change)
    return r


def every_missing_field_blocks(check, make, fields):
    """One mutant for many: BLOCKED only if removing any single required field is BLOCKED."""
    open_ = [f for f in fields if check(make(**{f: None})).verdict != BLOCKED]
    return Result("fields", PASS if open_ else BLOCKED, "not required after all: %s" % ", ".join(open_))


# ---------------------------------------------------------------- fixtures: rulers and panel

def exclusion(ruler=rulers.exclusion_ruler, panel=None, seeds=None, weak=retain1.FadingRegister, blocks=None):
    return rulers.exclusion_gate(ruler, retain1.PANEL if panel is None else panel, SEEDS if seeds is None else seeds,
                                 weak, BLOCKS if blocks is None else blocks)


def entry(physics, panel=None, seeds=None):
    return rulers.entry_gate(physics, retain1.PANEL if panel is None else panel, SEEDS if seeds is None else seeds)


def neutral(name, declared, panel=None, ruler=None, seeds=None):
    panel = retain1.PANEL if panel is None else panel
    if seeds is None:
        seeds = SEEDS if name == "CLASS_EXCLUSION" else PAIRS
    return rulers.neutrality_gate(name, ruler or rulers.RULERS[name], declared, panel, seeds)


def relabel(cls, physics):
    """The same machine under another physics name. The gates read the name; they cannot read the machine."""
    return type(cls.__name__ + "As" + physics.title(), (cls,), {"physics": physics})


def bracket():
    """The lowest and highest bound, on a grid of 0.01, for which the exclusion gate still passes this panel."""
    pos = [retain1.score(p, SEEDS) for p, _ in retain1.PANEL.values()] + [retain1.score(retain1.FadingRegister, SEEDS)]
    imp = [retain1.score(i, block) for _, i in retain1.PANEL.values() for block in [SEEDS] + BLOCKS]
    ok = [b / 100 for b in range(1, 100)
          if all(stats.classify(s, 64, b / 100, rulers.ALPHA, rulers.P_WEAKEST) == "EXCLUDES" for s in pos)
          and all(stats.classify(s, 64, b / 100, rulers.ALPHA, rulers.P_WEAKEST) == "AT_BOUND" for s in imp)]
    return {"lowest": min(ok), "highest": max(ok), "impostor_scores": [min(imp), max(imp)], "positive_scores": pos}


def all_positives(check):
    """Run one torture check on every positive of the panel; the first failure wins."""
    for physics, (positive, _) in sorted(retain1.PANEL.items()):
        r = check(positive)
        if r.verdict != PASS:
            return Result(r.gate, r.verdict, "%s: %s" % (physics, r.reason))
    return Result("panel", PASS)


def every_missing_baseline_blocks():
    """One mutant for five: BLOCKED only if leaving out any single required baseline is BLOCKED."""
    full = dict(retain1.BASELINES, TABLE=None)
    open_ = [b for b in BASELINES_REQUIRED if torture.demand_closure(
        DEMAND, TRAIN, baselines={k: v for k, v in full.items() if k != b}).verdict != BLOCKED]
    return Result("baselines", PASS if open_ else BLOCKED, "not required after all: %s" % ", ".join(open_))


# ---------------------------------------------------------------- fixtures: search

def hits(landscape, policy, law="COLD", distance=0, seeds=None, budget=BUDGET):
    return search.sample_reach(landscape, policy, budget, law, REPORTED if seeds is None else seeds, distance)


def report(claim="COLD_DISCOVERY", landscape="NEEDLE", law="COLD", distance=0, policies=("NEUTRAL",), budget=BUDGET,
           **change):
    r = {"claim": claim, "landscape": landscape, "budget": budget, "start_law": law, "distance": distance,
         "policies": {p: {"seeds": list(REPORTED), "hits": hits(landscape, p, law, distance, budget=budget)}
                      for p in policies}}
    r.update(change)
    return r


def recount(r, **policies):
    """A report with its counts replaced."""
    return dict(r, policies=policies)


def null(landscape="VALLEY", policies=("STRICT", "NEUTRAL"), **change):
    fields = {"scope": "POLICIES_AND_BUDGET", "upper_bound": stats.zero_hit_upper(len(REPORTED))}
    fields.update(change)
    return report("REACH_BOUNDED", landscape, policies=policies, **fields)


def repair_as_cold(landscape, policy, budget, kind, seeds, distance=0):
    """Fault: an estimator that starts one flip from the target and reports the result as cold reach."""
    return search.sample_reach(landscape, policy, budget, "REPAIR", seeds, 1)


def short_budget(fraction):
    """Fault: an estimator that ran a fraction of the registered budget."""
    def estimator(landscape, policy, budget, kind, seeds, distance=0):
        return search.sample_reach(landscape, policy, int(budget * fraction), kind, seeds, distance)
    return estimator


def phantom(extra):
    """Fault: an estimator that reports hits it did not have."""
    def estimator(landscape, policy, budget, kind, seeds, distance=0):
        return min(len(seeds), search.sample_reach(landscape, policy, budget, kind, seeds, distance) + extra)
    return estimator


# ---------------------------------------------------------------- fixtures: audits

TOY = {"naive_B": 100, "dev_B": 10, "sham_B": 11, "lesion_B": 90}


def toy_cells(**cells):
    """Cells for a three-clause toy rule. GOOD holds every clause; each named cell changes some arms."""
    out = {"GOOD": {"replicates": [dict(TOY) for _ in range(24)]}}
    for name, change in cells.items():
        out[name] = {"replicates": [dict(TOY, **change) for _ in range(24)]}
    return out


ISOLATING = {"NO_SAVINGS": {"dev_B": 60, "sham_B": 61}, "NO_LESION_EFFECT": {"lesion_B": 10},
             "HARMFUL_SHAM": {"sham_B": 400}}
CATCH_ALL = {"NOTHING_WORKS": {"dev_B": 90, "sham_B": 400, "lesion_B": 10}}


def toy_clauses(o):
    return {"SAVINGS": 4 * o["dev_B"] <= o["naive_B"], "NESTING.lesion_hurts": 2 * o["lesion_B"] >= o["naive_B"],
            "NESTING.sham_harmless": o["sham_B"] <= 2 * o["dev_B"] + 4}


def toy_clauses_with_an_impossible_one(o):
    return dict(toy_clauses(o), IMPOSSIBLE=o["dev_B"] < 0)


def run2():
    return receipt("RECEIPT_gauntlet2.json")["cells"]


def run3():
    return receipt("RECEIPT_gauntlet3.json")["cells"]


def nudged(reps):
    """Fault: arms that are one series, made to differ in one replicate of 24."""
    reps = copy.deepcopy(reps)
    for arm, d in (("lesion_B", 1), ("sham_B", 1), ("rescue_B", 2), ("v_donor_B", 3), ("irrelevant_history_B", 2)):
        reps[0][arm] += d
    return reps


ARMS2 = ("naive_B", "dev_B", "lesion_B", "sham_B", "rescue_B", "v_donor_B", "wrong_history_B", "random_library_B")
ARMS3 = ("naive_B", "dev_B", "lesion_B", "sham_B", "rescue_B", "v_donor_B", "irrelevant_history_B", "random_V_B")
SETTING_OK = dict(audits.RUN2, power=0.99, amortization_horizon=3)


# ---------------------------------------------------------------- fixtures: custody and claims

def custody(**change):
    r = {"discovery": {"seeds": [1, 2, 3], "panel_sha256": "d" * 64, "generator_sha256": "1" * 64},
         "confirmation": {"seeds": [7, 8, 9], "panel_sha256": "c" * 64, "generator_sha256": "2" * 64},
         "selection_data": "discovery", "claim": "NEW_FAMILY", "tuning_evaluations": 40, "tuning_budget": 50,
         "rule_fixed_at": 10, "confirmation_opened_at": 20, "discovery_custodian": "tuner",
         "confirmation_custodian": "keeper"}
    r.update(change)
    return r


def side(**change):
    s = {"seeds": [7, 8, 9], "panel_sha256": "c" * 64, "generator_sha256": "2" * 64}
    s.update(change)
    return s


SETTING = {"gap": 6, "alpha": "1e-6", "episodes": 64}


def claim(kind="EFFECT", drop=None, setting=None, **facets):
    names = claims.L1 + claims.L2 + claims.KIND[kind]
    f = {k: {"verdict": PASS, "source": "RECEIPT_harness_v0.json"} for k in names}
    for k, v in facets.items():
        f[k] = v if isinstance(v, dict) or v is None else {"verdict": v, "source": "RECEIPT_harness_v0.json"}
    for k in ([drop] if isinstance(drop, str) else list(drop or [])):
        f.pop(k)
    return {"kind": kind, "cell": "REGISTER/RETAIN-1/designed", "facets": f, "setting": dict(SETTING),
            "setting_sha256": claims.setting_hash(SETTING if setting is None else setting)}


# ---------------------------------------------------------------- the registry

def gates():
    """Gate id -> (what it guards, clean cases, mutants). A mutant is (name, thunk, registered verdict)."""
    R = retain1
    p_ok = dict(R.PANEL)
    r2, r3 = run2(), run3()
    t2, t3 = audits.clause_table(r2, audits.clauses_run2), audits.clause_table(r3, audits.clauses_run3)
    toy_row = audits.clause_table(toy_cells(**ISOLATING), toy_clauses)["NESTING.sham_harmless"]
    cal = search.calibration
    seq = registration
    hitter = next(s for s in REPORTED if hits("NEEDLE", "NEUTRAL", seeds=[s]))
    bits = [r for r in audits.RUNS if "BITS" in r[3]]
    return {
        "G1.cell": ("a run exists only as a complete registered cell whose answers are attainable", [
            lambda: seq.check_cell(cell()),
            lambda: seq.check_cell(cell(design_seeds=[]))], [
            ("a required field is missing (each of the sixteen, in turn)",
             lambda: every_missing_field_blocks(seq.check_cell, cell, CELL_FIELDS), BLOCKED),
            ("exposure given as a word", lambda: seq.check_cell(cell(exposure="unknown")), BLOCKED),
            ("verdict table leaves counts 13 to 21 unmapped",
             lambda: seq.check_cell(cell(verdict_table=table([(22, 24, "HOLDS"), (0, 12, "FAILS")]))), FAIL),
            ("the ruler cannot emit its third outcome",
             lambda: seq.check_cell(cell(verdict_table=table([(13, 24, "HOLDS"), (0, 12, "FAILS")]))), FAIL),
            ("a count mapped to two outcomes",
             lambda: seq.check_cell(cell(verdict_table=table([(22, 24, "HOLDS"), (0, 13, "FAILS"),
                                                               (13, 21, "INDETERMINATE")]))), FAIL),
            ("the table emits an outcome it does not register",
             lambda: seq.check_cell(cell(verdict_table=table([(22, 24, "HOLDS"), (0, 12, "FAILS"), (13, 20,
                                                               "INDETERMINATE"), (21, 21, "MAYBE")]))), FAIL),
            ("a design seed is registered for confirmation",
             lambda: seq.check_cell(cell(design_seeds=[1, 2, 5000])), FAIL),
            ("a registered seed is repeated",
             lambda: seq.check_cell(cell(registered_seeds=[5000] * 24)), FAIL),
            ("the table counts 24 units and three seeds are registered",
             lambda: seq.check_cell(cell(registered_seeds=[5000, 5001, 5002])), FAIL),
            ("a positive that reaches its answer with probability 0.96",
             lambda: seq.check_cell(cell(known_answers={"HOLDS": 0.97, "FAILS": 0.2})), BLOCKED),
            ("power declared for one answer only", lambda: seq.check_cell(cell(known_answers={"HOLDS": 0.999})), BLOCKED),
            ("power declared as a number, with no rate behind it",
             lambda: seq.check_cell(cell(known_answers={"HOLDS": "1.0", "FAILS": "0.999"})), BLOCKED),
            ("a missing field and a shared seed together",
             lambda: seq.check_cell(cell(exposure=None, design_seeds=[1, 2, 5000])), FAIL)]),
        "G1.receipt": ("a receipt belongs to its registration", [
            lambda: seq.check_receipt(cell(), run_receipt(), SOURCE)], [
            ("receipt from other code", lambda: seq.check_receipt(cell(), run_receipt(source_sha256="b" * 64), SOURCE),
             FAIL),
            ("the receipt copies the registered hash and the code on hand is other code",
             lambda: seq.check_receipt(cell(), run_receipt(), b"other code\n"), FAIL),
            ("receipt on other seeds", lambda: seq.check_receipt(cell(), run_receipt(seeds=[1, 2, 3]), SOURCE), FAIL),
            ("one registered seed run twice in place of another",
             lambda: seq.check_receipt(cell(), run_receipt(seeds=[5000] + list(range(5000, 5023))), SOURCE), FAIL),
            ("run earlier than its registration", lambda: seq.check_receipt(cell(), run_receipt(ran_at=99), SOURCE), FAIL),
            ("run at the clock tick of its registration",
             lambda: seq.check_receipt(cell(), run_receipt(ran_at=100), SOURCE), INDETERMINATE),
            ("receipt without a source hash",
             lambda: seq.check_receipt(cell(), run_receipt(source_sha256=""), SOURCE), BLOCKED),
            ("the code is not on hand", lambda: seq.check_receipt(cell(), run_receipt()), BLOCKED)]),
        "G2.preflight": ("no run starts unless both registered answers are attainable", [
            lambda: stats.preflight(len(SEEDS), rulers.BOUND, rulers.ALPHA, rulers.P_WEAKEST),
            lambda: stats.preflight_from_design(len(SEEDS), rulers.BOUND, rulers.ALPHA, 256, 256)], [
            ("16 episodes cannot reach alpha 1e-6", lambda: stats.preflight(16, 0.5, 1e-6, 1.0), BLOCKED),
            ("a positive expected at 0.75", lambda: stats.preflight(64, 0.5, 1e-6, 0.75), BLOCKED),
            ("a positive expected at 0.85: power 0.91", lambda: stats.preflight(64, 0.5, 1e-6, 0.85), BLOCKED),
            ("alpha 0.05: the negative's answer is below 0.99", lambda: stats.preflight(64, 0.5, 0.05, 1.0), BLOCKED),
            ("a positive seen perfect in 20 design runs, registered at 20 episodes",
             lambda: stats.preflight_from_design(20, 0.5, 1e-6, 20, 20), BLOCKED),
            ("a rate with no design runs behind it", lambda: stats.preflight_from_design(64, 0.5, 1e-6, 0, 0), BLOCKED),
            ("power given as 99", lambda: stats.preflight(64, 0.5, 1e-6, 99), BLOCKED)]),
        "G3.exclusion": ("class exclusion returns the known answers on a panel that brackets its bound", [
            lambda: exclusion()], [
            ("a bound of 0.10 where the class reaches 0.5", lambda: exclusion(rulers.make_exclusion_ruler(0.10)), FAIL),
            ("a bound of 0.25", lambda: exclusion(rulers.make_exclusion_ruler(0.25)), FAIL),
            ("a bound of 0.70", lambda: exclusion(rulers.make_exclusion_ruler(0.70)), FAIL),
            ("alpha 0.4 in the ruler", lambda: exclusion(rulers.make_exclusion_ruler(alpha=0.4)), FAIL),
            ("a ruler that always says yes, on a panel with no impostors",
             lambda: exclusion(lambda make, seeds: "POSITIVE", {k: (v[0], None) for k, v in p_ok.items()}), UNQUALIFIED),
            ("a panel with no weak positive: the bound is not bracketed", lambda: exclusion(weak=None), UNQUALIFIED),
            ("16 episodes", lambda: exclusion(seeds=SEEDS[:16], blocks=[b[:16] for b in BLOCKS]), BLOCKED),
            ("a weak positive that scores 49 of 64", lambda: exclusion(weak=R.scripted(49)), INDETERMINATE)]),
        "G4.entry": ("a physics is read only after it has returned a known answer", [
            lambda: entry("REGISTER"), lambda: entry("ATTRACTOR"), lambda: entry("PACKET"), lambda: entry("LATTICE")], [
            ("a physics with no designed organism", lambda: entry("CHEMISTRY"), UNQUALIFIED),
            ("a physics with a positive and no impostor", lambda: entry("LATTICE", dict(p_ok, LATTICE=(R.Lattice, None))),
             UNQUALIFIED),
            ("a designed positive that does not work",
             lambda: entry("PACKET", dict(p_ok, PACKET=(R.PacketImpostor, R.PacketImpostor))), FAIL),
            ("an impostor that is in fact a positive",
             lambda: entry("PACKET", dict(p_ok, PACKET=(R.PacketRing, R.PacketRing))), FAIL),
            ("an impostor that carries the cue and answers its complement",
             lambda: entry("REGISTER", dict(p_ok, REGISTER=(R.Register, R.Inverter))), FAIL),
            ("an impostor from another physics", lambda: entry("PACKET", dict(p_ok, PACKET=(R.PacketRing, R.Constant))),
             FAIL),
            ("stored-word machines entered under another physics",
             lambda: entry("CHEMISTRY", {"CHEMISTRY": (R.Register, R.RegisterImpostor)}), FAIL),
            ("16 episodes", lambda: entry("REGISTER", seeds=SEEDS[:16]), BLOCKED),
            ("a positive that scores 49 of 64",
             lambda: entry("REGISTER", dict(p_ok, REGISTER=(R.scripted(49), R.RegisterImpostor))), INDETERMINATE)]),
        "G5.neutrality": ("a ruler is shared only where it has returned the known answers", [
            lambda: neutral("CLASS_EXCLUSION", "SHARED"), lambda: neutral("INTERCHANGE", "SHARED"),
            lambda: neutral("REGISTER_SWAP", ["REGISTER"]),
            lambda: neutral("CLASS_EXCLUSION", "SHARED", dict(p_ok, CHEMISTRY=(None, None)))], [
            ("the register-swap ruler declared shared", lambda: neutral("REGISTER_SWAP", "SHARED"), FAIL),
            ("the register-swap ruler declared valid for packets",
             lambda: neutral("REGISTER_SWAP", ["REGISTER", "PACKET"]), FAIL),
            ("a shared claim on a panel of two physics",
             lambda: neutral("CLASS_EXCLUSION", "SHARED", {k: p_ok[k] for k in ("REGISTER", "ATTRACTOR")}), UNQUALIFIED),
            ("declared valid in a physics with no known answer",
             lambda: neutral("REGISTER_SWAP", ["REGISTER", "CHEMISTRY"], dict(p_ok, CHEMISTRY=(None, None))),
             UNQUALIFIED),
            ("declared valid nowhere", lambda: neutral("REGISTER_SWAP", []), BLOCKED),
            ("a ruler that always says no, declared shared",
             lambda: neutral("NEVER", "SHARED", ruler=lambda make, seeds: "NEGATIVE"), FAIL),
            ("interchange on a panel whose impostor carries the cue",
             lambda: neutral("INTERCHANGE", "SHARED", dict(p_ok, REGISTER=(R.Register, R.Inverter))), FAIL),
            ("class exclusion on 16 episodes", lambda: neutral("CLASS_EXCLUSION", "SHARED", seeds=SEEDS[:16]), BLOCKED)]),
        "G6.observer": ("observing a run does not change it", [
            lambda: all_positives(lambda m: torture.observer_equivalence(m, PAIRS, torture.quiet_observer)),
            lambda: all_positives(lambda m: torture.observer_equivalence(m, PAIRS, torture.own_stream_observer))], [
            ("an observer that draws from the world's random stream",
             lambda: all_positives(lambda m: torture.observer_equivalence(m, PAIRS, torture.greedy_observer)), FAIL),
            ("an observer that draws from it after the last distractor",
             lambda: all_positives(lambda m: torture.observer_equivalence(m, PAIRS, torture.late_observer)), FAIL),
            ("an observer that rewrites the organism after it has answered",
             lambda: all_positives(lambda m: torture.observer_equivalence(m, PAIRS, torture.writing_observer)), FAIL),
            ("an observer that advances the world's episode counter",
             lambda: all_positives(lambda m: torture.observer_equivalence(m, PAIRS, torture.counter_observer)), FAIL),
            ("an observer that writes on the environment",
             lambda: all_positives(lambda m: torture.observer_equivalence(m, PAIRS, torture.marking_observer)), FAIL)]),
        "G6.reset": ("after a reset a runtime behaves as one that never ran", [
            lambda: all_positives(lambda m: torture.reset_closure(m, PAIRS)),
            lambda: torture.reset_closure(R.WorldParker, PAIRS, writable_mark=True)], [
            ("a runtime whose reset keeps its word", lambda: torture.reset_closure(R.LeakyResetRegister, PAIRS), FAIL),
            ("a harness that forgets to reset", lambda: torture.reset_closure(R.Register, PAIRS, skip_reset=True), FAIL),
            ("a carry that native() hides and that shows only when a cue arrives",
             lambda: torture.reset_closure(R.SneakyRegister, PAIRS), FAIL),
            ("a reset that keeps a step counter", lambda: torture.reset_closure(R.LatticeKeepsClock, PAIRS), FAIL),
            ("an environment that keeps its mark across episodes",
             lambda: torture.reset_closure(R.WorldParker, PAIRS, writable_mark=True, keep_mark=True), FAIL)]),
        "G6.restart": ("capture and restore carry the whole state", [
            lambda: all_positives(lambda m: torture.restart_equivalence(m, PAIRS))], [
            ("a capture that omits packets in flight", lambda: torture.restart_equivalence(R.PacketRingBadCapture, PAIRS),
             FAIL),
            ("a restore that does nothing", lambda: torture.restart_equivalence(R.AttractorStaleRestore, PAIRS), FAIL),
            ("a restore that adds to what is there", lambda: torture.restart_equivalence(R.PacketAppendRestore, PAIRS),
             FAIL),
            ("a restore that leaves a stale word in place",
             lambda: torture.restart_equivalence(R.RegisterKeepIfSet, PAIRS), FAIL),
            ("a capture that is wrong late in the gap only",
             lambda: torture.restart_equivalence(R.LatticeLateBadCapture, PAIRS), FAIL)]),
        "G7.calibration": ("sampled reach agrees with exact reach", [
            lambda: cal("NEEDLE", "NEUTRAL", BUDGET, "COLD", FOUNDERS),
            lambda: cal("NEEDLE", "NEUTRAL", BUDGET, "REPAIR", FOUNDERS, 1),
            lambda: cal("VALLEY", "NEUTRAL", BUDGET, "REPAIR", FOUNDERS, 1),
            lambda: cal("ASCENT", "STRICT", BUDGET, "COLD", FOUNDERS),
            lambda: cal("VALLEY", "STRICT", BUDGET, "COLD", FOUNDERS)], [
            ("repair runs counted as cold reach",
             lambda: cal("VALLEY", "STRICT", BUDGET, "COLD", FOUNDERS, 0, repair_as_cold), FAIL),
            ("an estimator that ran half the registered budget",
             lambda: cal("NEEDLE", "NEUTRAL", BUDGET, "COLD", FOUNDERS, 0, short_budget(0.5)), FAIL),
            ("an estimator that reports 40 hits it did not have",
             lambda: cal("NEEDLE", "NEUTRAL", BUDGET, "COLD", FOUNDERS, 0, phantom(40)), FAIL)]),
        "G7.report": ("a search result is what it says it is", [
            lambda: search.check_report(report()),
            lambda: search.check_report(null()),
            lambda: search.check_report(report("REPAIR_REACH", "VALLEY", "REPAIR", 1, ("STRICT",))),
            lambda: search.check_report(null(upper_bound=round(stats.zero_hit_upper(len(REPORTED)), 4))),
            lambda: search.check_report(null(upper_bound=stats.zero_hit_upper(len(REPORTED), 0.99)))], [
            ("a repair start declared under a cold-discovery claim",
             lambda: search.check_report(report("COLD_DISCOVERY", "VALLEY", "REPAIR", 1, ("STRICT",))), FAIL),
            ("repair counts reported under a cold start", lambda: search.check_report(recount(
                report("COLD_DISCOVERY", "VALLEY", policies=("STRICT",)),
                STRICT={"seeds": list(REPORTED), "hits": hits("VALLEY", "STRICT", "REPAIR", 1)})), FAIL),
            ("a discovery claimed with nothing found",
             lambda: search.check_report(report("COLD_DISCOVERY", "VALLEY", policies=("STRICT",))), FAIL),
            ("more hits reported than the search had", lambda: search.check_report(recount(
                report(), NEUTRAL={"seeds": list(REPORTED), "hits": hits("NEEDLE", "NEUTRAL") + 9})), FAIL),
            ("a null whose scope is the substrate", lambda: search.check_report(null(scope="SUBSTRATE")), FAIL),
            ("a null that states no scope", lambda: search.check_report(null(scope=None)), BLOCKED),
            ("a null from one policy on a plateau", lambda: search.check_report(null("NEEDLE", ("STRICT",))), BLOCKED),
            ("a null from two policies, neither able to cross a neutral step",
             lambda: search.check_report(null("NEEDLE", ("STRICT", "ELITIST"))), BLOCKED),
            ("a null although the second policy reached the target", lambda: search.check_report(null("NEEDLE")), FAIL),
            ("one founder that hit, counted 128 times", lambda: search.check_report(recount(
                report(), NEUTRAL={"seeds": [hitter] * len(REPORTED), "hits": len(REPORTED)})), FAIL),
            ("a null with no bound attached", lambda: search.check_report(null(upper_bound=None)), FAIL),
            ("a null with a bound smaller than the founders warrant", lambda: search.check_report(null(upper_bound=0.001)),
             FAIL),
            ("a null at a budget too small for the positive control",
             lambda: search.check_report(null(budget=5)), UNQUALIFIED),
            ("a policy that is not registered", lambda: search.check_report(recount(
                report(), STRICT_AGAIN={"seeds": list(REPORTED), "hits": 0})), BLOCKED),
            ("no positive control and a repair start under a discovery claim",
             lambda: search.check_report(report("COLD_DISCOVERY", "VALLEY", "REPAIR", 1, ("STRICT",), budget=5)), FAIL)]),
        "G8.demand": ("every baseline on the list is shown to sit at the bound", [
            lambda: torture.demand_closure(DEMAND, TRAIN)], [
            ("the cue follows a counter the organism can read",
             lambda: torture.demand_closure(DEMAND, TRAIN, leak_clock="parity"), FAIL),
            ("the probe carries the answer", lambda: torture.demand_closure(DEMAND, TRAIN, leak_key="plain"), FAIL),
            ("the probe carries the complement of the answer",
             lambda: torture.demand_closure(DEMAND, TRAIN, leak_key="inverted"), FAIL),
            ("the probe carries the answer in two episodes of five",
             lambda: torture.demand_closure(DEMAND, TRAIN, leak_key="partial"), FAIL),
            ("the cue is the xor of the last two distractors",
             lambda: torture.demand_closure(DEMAND, TRAIN, cue_from_distractors=True), FAIL),
            ("the environment keeps what the organism writes",
             lambda: torture.demand_closure(DEMAND, TRAIN, writable_mark=True), FAIL),
            ("a required baseline was not run (each of the five, in turn)",
             lambda: every_missing_baseline_blocks(), BLOCKED),
            ("closure claimed from 64 episodes", lambda: torture.demand_closure(SEEDS, TRAIN), INDETERMINATE),
            ("the table scored on the seeds it was fitted on", lambda: torture.demand_closure(DEMAND, DEMAND), BLOCKED)]),
        "G9.arms": ("arms registered as separate controls give separate series", [
            lambda: audits.audit_arms(toy_cells()["GOOD"]["replicates"], ("naive_B", "dev_B", "sham_B", "lesion_B")),
            lambda: audits.audit_arms(r2["BUILDER"]["replicates"], ARMS2)], [
            ("run 3, STRATEGIST: eight arms", lambda: audits.audit_arms(r3["STRATEGIST"]["replicates"], ARMS3), FAIL),
            ("the same arms nudged apart in one replicate of 24",
             lambda: audits.audit_arms(nudged(r3["STRATEGIST"]["replicates"]), ARMS3), FAIL)]),
        "G9.clauses": ("every clause holds somewhere and fails somewhere by itself", [
            lambda: audits.audit_clauses(toy_cells(**ISOLATING), toy_clauses)], [
            ("run 2: nine cells, thirteen clauses", lambda: audits.audit_clauses(r2, audits.clauses_run2), UNQUALIFIED),
            ("run 3: four cells, thirteen clauses", lambda: audits.audit_clauses(r3, audits.clauses_run3), UNQUALIFIED),
            ("one catch-all cell in which nothing works",
             lambda: audits.audit_clauses(toy_cells(**CATCH_ALL), toy_clauses), INDETERMINATE),
            ("a clause that can never hold",
             lambda: audits.audit_clauses(toy_cells(**ISOLATING), toy_clauses_with_an_impossible_one), UNQUALIFIED)]),
        "G9.sham": ("a sham can fail and leaves the organism where it was", [
            lambda: audits.audit_sham(toy_cells()["GOOD"]["replicates"], toy_row),
            lambda: audits.audit_sham([{"dev_B": 3, "sham_B": 4} for _ in range(24)], toy_row)], [
            ("run 2, BUILDER: the sham removes unused entries",
             lambda: audits.audit_sham(r2["BUILDER"]["replicates"], t2["NESTING.sham_harmless"]), FAIL),
            ("run 3, STRATEGIST: the sham swaps two idle orders",
             lambda: audits.audit_sham(r3["STRATEGIST"]["replicates"], t3["NESTING.sham_harmless"]), UNQUALIFIED),
            ("a sham 40% slower in every replicate",
             lambda: audits.audit_sham([{"dev_B": 10, "sham_B": 14} for _ in range(24)], toy_row), FAIL)]),
        "G10.setting": ("the nine open choices are registered before the run", [
            lambda: audits.audit_setting(SETTING_OK)], [
            ("run 2 as it was registered", lambda: audits.audit_setting(audits.RUN2), BLOCKED),
            ("run 3 as it was registered", lambda: audits.audit_setting(audits.RUN3), BLOCKED),
            ("power registered as 0.2", lambda: audits.audit_setting(dict(SETTING_OK, power=0.2)), BLOCKED),
            ("power registered as a sentence",
             lambda: audits.audit_setting(dict(SETTING_OK, power="high enough")), BLOCKED),
            ("every field registered as tbd", lambda: audits.audit_setting({k: "tbd" for k in audits.SETTING}), BLOCKED)]),
        "G10.contrast": ("a contrast named after one variable changes that variable only", [
            lambda: audits.audit_contrast("parts_shared", audits.RUN3, dict(audits.RUN3, parts_shared=True))], [
            ("run 2 against run 3, named after shared parts",
             lambda: audits.audit_contrast("parts_shared", audits.RUN2, audits.RUN3), FAIL),
            ("two cells that do not differ in the named variable",
             lambda: audits.audit_contrast("parts_shared", audits.RUN3, audits.RUN3), FAIL)]),
        "G10.ruler": ("a ruler is used for a claim only after it has answered the kit correctly", [
            lambda: audits.ruler_status("BITS", "BITS@KEYS", COUNTERFEIT)], [
            ("the strong claim, run 1: the v0.1 criterion passed a selector and a fixed builder",
             lambda: audits.ruler_status("STRONG", "V01@RUN1", COUNTERFEIT), FAIL),
            ("the strong claim, run 2: the strict protocol passed a fixed builder",
             lambda: audits.ruler_status("STRONG", "S19@RUN2", COUNTERFEIT), FAIL),
            ("the strong claim, run 3: the strict protocol passed a selector over search orders",
             lambda: audits.ruler_status("STRONG", "S19@RUN3", COUNTERFEIT), FAIL),
            ("reuse of built parts, run 2: right on all it met; four members unbuilt, one not run here",
             lambda: audits.ruler_status("REUSE", "S19@RUN2", COUNTERFEIT), UNQUALIFIED),
            ("reuse of built parts, run 3: passed an organism that builds no parts",
             lambda: audits.ruler_status("REUSE", "S19@RUN3", COUNTERFEIT), FAIL),
            ("bits across two nested boundaries: nothing registered has been built",
             lambda: audits.ruler_status("BITS_TWO_LEVELS", "BITS@TWO", COUNTERFEIT), UNQUALIFIED),
            ("composition on an unseen pair: nothing registered has been built",
             lambda: audits.ruler_status("COMPOSITION", "BITS@PAIRS", COUNTERFEIT), UNQUALIFIED),
            ("a registered answer that the receipt contradicts", lambda: audits.ruler_status(
                "BITS", "BITS@KEYS", COUNTERFEIT, [(m, s, src, {"BITS": "NEGATIVE"}) if m == "KEY_ACQUIRER" else
                                                   (m, s, src, a) for m, s, src, a in audits.RUNS]), FAIL),
            ("a receipt replaced by an unrelated file that exists", lambda: audits.ruler_status(
                "BITS", "BITS@KEYS", COUNTERFEIT, [(m, s, ("README.md",) + src[1:], a) for m, s, src, a in audits.RUNS]),
             BLOCKED),
            ("a kit with a positive and no negative", lambda: audits.ruler_status(
                "BITS", "BITS@KEYS", COUNTERFEIT, [r for r in audits.RUNS if r[0] == "KEY_ACQUIRER"]), UNQUALIFIED),
            ("a kit answered correctly, with one registered member never built", lambda: audits.ruler_status(
                "BITS", "BITS@KEYS", COUNTERFEIT, bits, {"KEY_HIDER": {"BITS": "NEGATIVE"}}), UNQUALIFIED),
            ("a kit answered correctly, with one member run only at another setting", lambda: audits.ruler_status(
                "BITS", "BITS@KEYS", COUNTERFEIT, bits + [("KEY_HIDER", "BITS@ELSEWHERE", bits[0][2],
                                                           {"BITS": "NEGATIVE"})], {}), UNQUALIFIED)]),
        "G11.custody": ("confirmation data is not discovery data, and the rule was fixed first", [
            lambda: claims.check_custody(custody())], [
            ("a required field is missing (each of the ten, in turn)",
             lambda: every_missing_field_blocks(claims.check_custody, custody, CUSTODY_FIELDS), BLOCKED),
            ("confirmation seeds reused from discovery",
             lambda: claims.check_custody(custody(confirmation=side(seeds=[3, 8, 9]))), FAIL),
            ("the confirmation panel is the discovery panel",
             lambda: claims.check_custody(custody(confirmation=side(panel_sha256="d" * 64))), FAIL),
            ("the champion was chosen on confirmation data",
             lambda: claims.check_custody(custody(selection_data="confirmation")), FAIL),
            ("new seeds of one generator presented as a new family",
             lambda: claims.check_custody(custody(confirmation=side(generator_sha256="1" * 64))), FAIL),
            ("tuning beyond the registered budget", lambda: claims.check_custody(custody(tuning_evaluations=80)), FAIL),
            ("the acceptance rule fixed after the confirmation data was opened",
             lambda: claims.check_custody(custody(rule_fixed_at=30)), FAIL),
            ("one custodian for both sets", lambda: claims.check_custody(custody(confirmation_custodian="tuner")), FAIL),
            ("a confirmation with no seeds", lambda: claims.check_custody(custody(confirmation=side(seeds=[]))), BLOCKED),
            ("a negative count of tuning evaluations", lambda: claims.check_custody(custody(tuning_evaluations=-5)),
             BLOCKED)]),
        "G12.promote": ("a claim stands only on facets that passed, each with a source", [
            lambda: claims.promote(claim(), 1), lambda: claims.promote(claim(), 2),
            lambda: claims.promote(claim("NESTED"), 1), lambda: claims.promote(claim("MECHANISM"), 2)], [
            ("the detection facet is absent", lambda: claims.promote(claim(drop="detection"), 1), BLOCKED),
            ("the demand facet failed", lambda: claims.promote(claim(demand=FAIL), 1), FAIL),
            ("the ruler is unqualified in this physics", lambda: claims.promote(claim(detection=UNQUALIFIED), 1),
             UNQUALIFIED),
            ("the evidence was indeterminate", lambda: claims.promote(claim(independence=INDETERMINATE), 1),
             INDETERMINATE),
            ("a structure claim with no exact bound asks for L2",
             lambda: claims.promote(claim("TRANSFER", exact_null=UNQUALIFIED), 2), UNQUALIFIED),
            ("a mechanism claim with no intervention facet",
             lambda: claims.promote(claim("MECHANISM", drop="intervention"), 1), BLOCKED),
            ("a nested claim resting on a retention certificate alone", lambda: claims.promote(claim(
                "NESTED", drop=["mediation", "cargo_control", "flattened_twin"]), 1), BLOCKED),
            ("one facet absent and another failed", lambda: claims.promote(claim(drop="detection", demand=FAIL), 1),
             FAIL),
            ("a facet typed PASS with no source", lambda: claims.promote(claim(demand={"verdict": PASS}), 1), BLOCKED),
            ("a facet with a verdict that is not one of the five",
             lambda: claims.promote(claim(demand={"verdict": "passed", "source": "x"}), 1), BLOCKED),
            ("L2 asked with no custody facet", lambda: claims.promote(claim(drop="custody"), 2), BLOCKED),
            ("L2 asked with a failed second implementation",
             lambda: claims.promote(claim(second_implementation=FAIL), 2), FAIL)]),
        "G12.render": ("a claim is quoted with its cell and its registered setting or not at all", [
            lambda: claims.render(claim())], [
            ("a claim stripped of its setting", lambda: claims.render(dict(claim(), setting={})), BLOCKED),
            ("a claim with no cell", lambda: claims.render(dict(claim(), cell="")), BLOCKED),
            ("a setting that is not the one registered",
             lambda: claims.render(dict(claim(), setting={"note": "see the paper"})), FAIL)]),
    }


def known_escapes():
    """Faults this harness is known NOT to catch. Each is run; the test suite pins every one.

    They are listed so that nobody reads a passing harness as covering them. `shown` is evidence that
    the fault is real where the harness can produce it.
    """
    R = retain1
    r3 = run3()
    row = dict(audits.clause_table(r3, audits.clauses_run3)["NESTING.sham_harmless"], ANOTHER_OPERATION_CALLED_SHAM=0)
    words = {p: (relabel(R.Register, p), relabel(R.RegisterImpostor, p)) for p in ("REGISTER", "ATTRACTOR", "PACKET")}
    chem = {"CHEMISTRY": (relabel(R.Register, "CHEMISTRY"), relabel(R.RegisterImpostor, "CHEMISTRY"))}
    return [
        {"gate": "G3.exclusion", "fault": "a bound of 0.45 where the class reaches 0.5",
         "verdict": exclusion(rulers.make_exclusion_ruler(0.45)).verdict, "shown": bracket(),
         "why": "the panel brackets the bound and does not pin it: any bound inside the bracket returns the known "
                "answers. The exact bound has to be derived, and derived again by a second author."},
        {"gate": "G4.entry", "fault": "stored-word machines relabelled as another physics",
         "verdict": entry("CHEMISTRY", chem).verdict,
         "why": "the gate reads the physics an organism declares. It cannot read what the organism is."},
        {"gate": "G5.neutrality", "fault": "the register-swap ruler declared shared on three relabelled stored-word "
                                           "machines",
         "verdict": neutral("REGISTER_SWAP", "SHARED", words).verdict,
         "why": "the gate counts physics by name. Whether three physics are unlike is a judgment, registered in "
                "advance and attacked by a second author's isomer."},
        {"gate": "G6.observer", "fault": "an observer that disturbs the world only on seeds outside those checked",
         "verdict": all_positives(lambda m: torture.observer_equivalence(m, PAIRS, torture.rare_observer(PAIRS))).verdict,
         "why": "equivalence is shown on the seeds checked and on no others. A run has to be checked on its own seeds."},
        {"gate": "G6.reset", "fault": "a carry that native() hides and that is used two episodes later",
         "verdict": torture.reset_closure(R.SleeperRegister, PAIRS).verdict,
         "why": "the gate looks one episode ahead and at the state a runtime reports. State hidden from both passes."},
        {"gate": "G7.calibration", "fault": "an estimator that ran 95% of the registered budget",
         "verdict": search.calibration("NEEDLE", "NEUTRAL", BUDGET, "COLD", FOUNDERS, 0, short_budget(0.95)).verdict,
         "shown": {"exact_at_budget": search.exact_reach("NEEDLE", "NEUTRAL", BUDGET, "COLD"),
                   "exact_at_95_percent": search.exact_reach("NEEDLE", "NEUTRAL", int(BUDGET * 0.95), "COLD")},
         "why": "256 founders resolve an error in reach of a few standard errors and nothing smaller."},
        {"gate": "G8.demand", "fault": "the cue follows the second bit of a counter the organism can read",
         "verdict": torture.demand_closure(DEMAND, TRAIN, leak_clock="bit1").verdict,
         "shown": {"a_policy_that_reads_that_bit_scores": R.score(R.ClockBit1Reader, SEEDS, leak_clock="bit1"),
                   "of": len(SEEDS)},
         "why": "the gate runs a list of baselines, not the class. No baseline on the list reads that bit."},
        {"gate": "G9.sham", "fault": "run 3's idle sham, with a cell added in which another, harmful operation is "
                                     "called the sham",
         "verdict": audits.audit_sham(r3["STRATEGIST"]["replicates"], row).verdict,
         "why": "an audit of numbers cannot see what an operation was. The fire test of a sham must use that sham."},
        {"gate": "G10.setting", "fault": "the cost definition registered as a sentence that says nothing",
         "verdict": audits.audit_setting(dict(SETTING_OK, cost="as appropriate")).verdict,
         "why": "presence and type are checked, not meaning."},
        {"gate": "G11.custody", "fault": "an edited copy of the discovery generator presented as a new family",
         "verdict": claims.check_custody(custody(confirmation=side(generator_sha256="3" * 64))).verdict,
         "why": "generators are compared by the hash of their code. Whether two generators are one family is a "
                "judgment about their grammar."},
        {"gate": "G12.promote", "fault": "a facet typed PASS whose named source was never run",
         "verdict": claims.promote(claim(demand={"verdict": PASS, "source": "RECEIPT_that_does_not_exist.json"}),
                                   1).verdict,
         "why": "the gate requires a source and does not open it."},
    ]


def qualify(registry=None):
    """Run every gate on its clean cases and mutants. One row per gate."""
    rows = {}
    for gid, (guards, clean, mutants) in (gates() if registry is None else registry).items():
        clean_results = [thunk() for thunk in clean]
        mutant_results = [(name, thunk(), expected) for name, thunk, expected in mutants]
        false_alarms = [r.reason or r.verdict for r in clean_results if r.verdict != PASS]
        escapes = [name for name, r, _ in mutant_results if r.verdict == PASS]
        wrong_kind = ["%s: %s, expected %s" % (name, r.verdict, exp) for name, r, exp in mutant_results
                      if r.verdict not in (PASS, exp)]
        if not clean or not mutants:
            status = UNQUALIFIED
        elif false_alarms or escapes or wrong_kind:
            status = FAIL
        else:
            status = PASS
        rows[gid] = {"guards": guards, "status": status, "clean": len(clean), "mutants": len(mutants),
                     "false_alarms": false_alarms, "escapes": escapes, "wrong_kind": wrong_kind,
                     "mutant_verdicts": [{"mutant": name, "verdict": r.verdict, "reason": r.reason}
                                         for name, r, _ in mutant_results]}
    return rows
