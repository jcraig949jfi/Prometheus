"""GM. The gates are rulers too: each must pass a clean case and reject a case broken on purpose.

A gate with no broken case is UNQUALIFIED: it has never been shown able to fail. A gate that passes a
broken case has an escape. A gate that rejects a clean case makes false accusations. qualify() runs
every gate against its registered clean cases and mutants and returns one row per gate.

Several mutants are not invented. They are this reviewer's own runs 2 and 3, read from their
receipts, and the faults are the ones three rounds of review found by hand.
"""
import json
import pathlib

from . import audits, claims, registration, retain1, rulers, search, stats, torture
from .verdict import BLOCKED, FAIL, INDETERMINATE, PASS, UNQUALIFIED, Result

HERE = pathlib.Path(__file__).resolve().parent
COUNTERFEIT = HERE.parents[2].parent / "review" / "FABLE-5.1" / "counterfeit"
SEEDS = list(range(1000, 1064))          # 64 episodes for class exclusion
PAIRS = list(range(2000, 2012))          # 12 seeds for interchange and torture
FOUNDERS = list(range(3000, 3048))       # 48 independent founders for search
BUDGET = 400


def receipt(name):
    return json.loads((COUNTERFEIT / name).read_text(encoding="ascii"))


# ---------------------------------------------------------------- fixtures

def cell(**change):
    c = {"physics": "REGISTER", "search": "none (designed)", "world": "RETAIN-1 gap 6", "development": "none",
         "boundary": "internal; environment writes certified zero", "resources": {"steps": 8},
         "measurement": "class exclusion at alpha 1e-6", "exposure": {"tuning_evaluations": 0},
         "adapter": "symbolic", "independent_unit": "episode", "design_seeds": [1, 2, 3],
         "registered_seeds": [1000, 1001, 1002],
         "verdict_table": {"n": 24, "outcomes": ["HOLDS", "FAILS", "INDETERMINATE"],
                           "rule": [(22, 24, "HOLDS"), (0, 12, "FAILS"), (13, 21, "INDETERMINATE")]},
         "power": {"positive": 1.0, "impostor": 0.999999}, "source_sha256": "a" * 64, "registered_at": 100}
    c.update(change)
    return c


def run_receipt(**change):
    r = {"source_sha256": "a" * 64, "seeds": [1000, 1001, 1002], "ran_at": 200}
    r.update(change)
    return r


def table(rule):
    return {"n": 24, "outcomes": ["HOLDS", "FAILS", "INDETERMINATE"], "rule": rule}


def scope(ruler, panel=None):
    panel = retain1.PANEL if panel is None else panel
    t = rulers.measured_scope(ruler, panel, SEEDS)
    wrong = sorted(p for p, row in t.items() if row and not row["agrees"])
    return Result("G3.exclusion", FAIL if wrong else PASS, "wrong on: %s" % ", ".join(wrong) if wrong else "", t)


def loose_exclusion(bound):
    """Fault: a ruler whose bound is not the exact one."""
    def ruler(make, seeds):
        got = stats.class_exclusion(retain1.score(make, seeds), len(seeds), bound, rulers.ALPHA)
        return "POSITIVE" if got == "EXCLUDES" else "NEGATIVE"
    return ruler


def entry(physics, panel=None):
    return rulers.entry_gate(physics, retain1.PANEL if panel is None else panel, SEEDS)


def neutral(name, declared, panel=None):
    panel = retain1.PANEL if panel is None else panel
    seeds = SEEDS if name == "CLASS_EXCLUSION" else PAIRS
    return rulers.neutrality_gate(name, rulers.RULERS[name], declared, panel, seeds)


def all_positives(check):
    """Run one torture check on every positive of the panel; the first failure wins."""
    for physics, (positive, _) in sorted(retain1.PANEL.items()):
        r = check(positive)
        if r.verdict != PASS:
            return Result(r.gate, r.verdict, "%s: %s" % (physics, r.reason))
    return Result("panel", PASS)


def search_report(**change):
    control = search.exact_reach("ASCENT", "NEUTRAL", BUDGET, "COLD")
    r = {"claim": "COLD_DISCOVERY", "start_law": "COLD", "label": "",
         "policies": {"NEUTRAL": {"n": len(FOUNDERS), "seeds": list(FOUNDERS),
                                  "hits": search.sample_reach("NEEDLE", "NEUTRAL", BUDGET, "COLD", FOUNDERS)}},
         "positive_control": {"exact_reach": control}, "upper_bound": None}
    r.update(change)
    return r


def null_report(landscape="VALLEY", **change):
    policies = {p: {"n": len(FOUNDERS), "seeds": list(FOUNDERS),
                    "hits": search.sample_reach(landscape, p, BUDGET, "COLD", FOUNDERS)} for p in ("STRICT", "NEUTRAL")}
    fields = {"claim": "REACH_BOUNDED", "policies": policies, "upper_bound": stats.zero_hit_upper(len(FOUNDERS))}
    fields.update(change)
    return search_report(**fields)


def repair_as_cold(landscape, policy, budget, kind, seeds, distance=0):
    """Fault: an estimator that starts one flip from the target and reports the result as cold reach."""
    return search.sample_reach(landscape, policy, budget, "REPAIR", seeds, 1)


def toy_cells():
    """Two cells for a three-clause toy rule: one where every clause holds, one where every clause fails."""
    good = {"naive_B": 100, "dev_B": 10, "sham_B": 11, "lesion_B": 90}
    bad = {"naive_B": 100, "dev_B": 90, "sham_B": 400, "lesion_B": 10}
    return {"GOOD": {"replicates": [dict(good) for _ in range(24)]}, "BAD": {"replicates": [dict(bad) for _ in range(24)]}}


def toy_clauses(o):
    return {"SAVINGS": 4 * o["dev_B"] <= o["naive_B"], "NESTING.lesion_hurts": 2 * o["lesion_B"] >= o["naive_B"],
            "NESTING.sham_harmless": o["sham_B"] <= 2 * o["dev_B"] + 4}


def custody(**change):
    r = {"discovery": {"seeds": [1, 2, 3], "panel_sha256": "d" * 64, "generator": "renewal-v1"},
         "confirmation": {"seeds": [7, 8, 9], "panel_sha256": "c" * 64, "generator": "renewal-v2"},
         "selection_data": "discovery", "claim": "NEW_FAMILY", "tuning_evaluations": 40, "tuning_budget": 50}
    r.update(change)
    return r


def claim(kind="EFFECT", drop=None, **facets):
    f = {k: PASS for k in claims.L1 + claims.L2}
    f.update(facets)
    if drop:
        f.pop(drop)
    return {"kind": kind, "cell": "REGISTER/RETAIN-1/designed", "facets": f,
            "conditions": {"gap": 6, "alpha": "1e-6", "episodes": 64}}


def run2():
    return receipt("RECEIPT_gauntlet2.json")["cells"]


def run3():
    return receipt("RECEIPT_gauntlet3.json")["cells"]


ARMS2 = ("naive_B", "dev_B", "lesion_B", "sham_B", "rescue_B", "v_donor_B", "wrong_history_B", "random_library_B")
ARMS3 = ("naive_B", "dev_B", "lesion_B", "sham_B", "rescue_B", "v_donor_B", "irrelevant_history_B", "random_V_B")
SETTING_OK = dict(audits.RUN2, power="0.99 at the registered factor, by simulation on design seeds",
                  amortization_horizon="three later families")


# ---------------------------------------------------------------- the registry

def gates():
    """Gate id -> (what it guards, clean cases, mutants). A mutant is (name, thunk, expected verdict)."""
    p_ok = dict(retain1.PANEL)
    two = {k: p_ok[k] for k in ("REGISTER", "ATTRACTOR")}
    no_impostor = dict(p_ok, LATTICE=(retain1.Lattice, None))
    no_constant = {k: v for k, v in retain1.BASELINES.items() if k != "CONSTANT"}
    r2, r3 = run2(), run3()
    t2, t3 = audits.clause_table(r2, audits.clauses_run2), audits.clause_table(r3, audits.clauses_run3)
    return {
        "G1.cell": ("a run exists only as a complete registered cell", [lambda: registration.check_cell(cell())], [
            ("exposure not declared", lambda: registration.check_cell(cell(exposure=None)), BLOCKED),
            ("verdict table leaves counts 13 to 21 unmapped",
             lambda: registration.check_cell(cell(verdict_table=table([(22, 24, "HOLDS"), (0, 12, "FAILS")]))), FAIL),
            ("the ruler cannot emit INDETERMINATE",
             lambda: registration.check_cell(cell(verdict_table=table([(13, 24, "HOLDS"), (0, 12, "FAILS")]))), FAIL),
            ("a design seed is registered for confirmation",
             lambda: registration.check_cell(cell(design_seeds=[1, 2, 1000])), FAIL),
            ("power 0.865 for a registered answer",
             lambda: registration.check_cell(cell(power={"positive": 0.865, "impostor": 0.999})), BLOCKED)]),
        "G1.receipt": ("a receipt belongs to its registration", [
            lambda: registration.check_receipt(cell(), run_receipt())], [
            ("receipt from other code", lambda: registration.check_receipt(cell(), run_receipt(source_sha256="b" * 64)),
             FAIL),
            ("receipt on other seeds", lambda: registration.check_receipt(cell(), run_receipt(seeds=[1, 2, 3])), FAIL),
            ("run earlier than its registration", lambda: registration.check_receipt(cell(), run_receipt(ran_at=50)),
             FAIL),
            ("receipt without a source hash", lambda: registration.check_receipt(cell(), run_receipt(source_sha256="")),
             BLOCKED)]),
        "G2.preflight": ("no run starts unless both registered answers are attainable", [
            lambda: stats.preflight(len(SEEDS), 0.5, 1e-6, 1.0)], [
            ("16 episodes cannot reach alpha 1e-6", lambda: stats.preflight(16, 0.5, 1e-6, 1.0), BLOCKED),
            ("a positive expected at 0.75 has too little power", lambda: stats.preflight(64, 0.5, 1e-6, 0.75), BLOCKED)]),
        "G3.exclusion": ("class exclusion against the exact bound gives the known answer in every physics", [
            lambda: scope(rulers.exclusion_ruler)], [
            ("a bound of 0.10 where the class reaches 0.5", lambda: scope(loose_exclusion(0.10)), FAIL)]),
        "G4.entry": ("a physics is read only after it has returned a known answer", [
            lambda: entry("REGISTER"), lambda: entry("ATTRACTOR"), lambda: entry("PACKET"), lambda: entry("LATTICE")], [
            ("a physics with no designed organism", lambda: entry("CHEMISTRY"), UNQUALIFIED),
            ("a physics with a positive and no impostor", lambda: entry("LATTICE", no_impostor), UNQUALIFIED),
            ("a designed positive that does not work",
             lambda: entry("PACKET", dict(p_ok, PACKET=(retain1.PacketImpostor, retain1.PacketImpostor))), FAIL),
            ("an impostor that is in fact a positive",
             lambda: entry("PACKET", dict(p_ok, PACKET=(retain1.PacketRing, retain1.PacketRing))), FAIL)]),
        "G5.neutrality": ("a ruler is shared only where it has returned the known answers", [
            lambda: neutral("CLASS_EXCLUSION", "SHARED"), lambda: neutral("INTERCHANGE", "SHARED"),
            lambda: neutral("REGISTER_SWAP", ["REGISTER"])], [
            ("the register-swap ruler declared shared", lambda: neutral("REGISTER_SWAP", "SHARED"), FAIL),
            ("the register-swap ruler declared valid for packets",
             lambda: neutral("REGISTER_SWAP", ["REGISTER", "PACKET"]), FAIL),
            ("a shared claim on a panel of two physics", lambda: neutral("CLASS_EXCLUSION", "SHARED", two), UNQUALIFIED),
            ("a shared claim where one physics has no impostor",
             lambda: neutral("CLASS_EXCLUSION", "SHARED", no_impostor), UNQUALIFIED)]),
        "G6.observer": ("observing a run does not change it", [
            lambda: all_positives(lambda m: torture.observer_equivalence(m, PAIRS, torture.quiet_observer))], [
            ("an observer that draws from the world's random stream",
             lambda: all_positives(lambda m: torture.observer_equivalence(m, PAIRS, torture.greedy_observer)), FAIL)]),
        "G6.reset": ("nothing survives a reset", [lambda: all_positives(lambda m: torture.reset_closure(m, PAIRS))], [
            ("a runtime whose reset keeps its word", lambda: torture.reset_closure(retain1.LeakyResetRegister, PAIRS),
             FAIL),
            ("a harness that forgets to reset", lambda: torture.reset_closure(retain1.Register, PAIRS, skip_reset=True),
             FAIL)]),
        "G6.restart": ("capture and restore lose nothing", [
            lambda: all_positives(lambda m: torture.restart_equivalence(m, PAIRS))], [
            ("a capture that omits packets in flight",
             lambda: torture.restart_equivalence(retain1.PacketRingBadCapture, PAIRS), FAIL),
            ("a restore that leaves stale state", lambda: torture.restart_equivalence(retain1.AttractorStaleRestore, PAIRS),
             FAIL)]),
        "G7.calibration": ("sampled reach agrees with exact reach", [
            lambda: search.calibration("ASCENT", "NEUTRAL", BUDGET, "COLD", FOUNDERS),
            lambda: search.calibration("NEEDLE", "NEUTRAL", BUDGET, "COLD", FOUNDERS),
            lambda: search.calibration("NEEDLE", "STRICT", BUDGET, "COLD", FOUNDERS),
            lambda: search.calibration("VALLEY", "NEUTRAL", BUDGET, "COLD", FOUNDERS),
            lambda: search.calibration("VALLEY", "STRICT", BUDGET, "REPAIR", FOUNDERS, 1)], [
            ("repair runs counted as cold reach",
             lambda: search.calibration("VALLEY", "STRICT", BUDGET, "COLD", FOUNDERS, 0, repair_as_cold), FAIL)]),
        "G7.report": ("a search result is labelled as what it is", [
            lambda: search.check_report(search_report()), lambda: search.check_report(null_report()),
            lambda: search.check_report(search_report(claim="REPAIR_REACH", start_law="REPAIR"))], [
            ("repair reported as cold discovery", lambda: search.check_report(search_report(start_law="REPAIR")), FAIL),
            ("zero hits called substrate incapable",
             lambda: search.check_report(null_report(label="substrate incapable")), FAIL),
            ("a null from one policy on a plateau", lambda: search.check_report(search_report(
                claim="REACH_BOUNDED", upper_bound=stats.zero_hit_upper(len(FOUNDERS)),
                policies={"STRICT": {"n": len(FOUNDERS), "seeds": list(FOUNDERS),
                                     "hits": search.sample_reach("NEEDLE", "STRICT", BUDGET, "COLD", FOUNDERS)}})),
             BLOCKED),
            ("a null although the second policy reached the target",
             lambda: search.check_report(null_report("NEEDLE")), FAIL),
            ("the same founder counted twice", lambda: search.check_report(search_report(policies={"NEUTRAL": {
                "n": len(FOUNDERS), "seeds": [FOUNDERS[0]] * len(FOUNDERS), "hits": 0}})), FAIL),
            ("a null with no bound attached", lambda: search.check_report(null_report(upper_bound=None)), FAIL),
            ("a search with no positive control", lambda: search.check_report(search_report(positive_control=None)),
             UNQUALIFIED)]),
        "G8.demand": ("the world cannot be solved without the capability", [lambda: torture.demand_closure(SEEDS)], [
            ("the cue follows a counter the organism can read", lambda: torture.demand_closure(SEEDS, leak_clock=True),
             FAIL),
            ("the probe carries the answer", lambda: torture.demand_closure(SEEDS, leak_key=True), FAIL),
            ("the environment keeps what the organism writes", lambda: torture.demand_closure(SEEDS, writable_mark=True),
             FAIL),
            ("the constant baseline was not run", lambda: torture.demand_closure(SEEDS, baselines=no_constant), BLOCKED)]),
        "G9.arms": ("arms registered as separate controls are separate computations", [
            lambda: audits.audit_arms(toy_cells()["GOOD"]["replicates"], ("naive_B", "dev_B", "sham_B", "lesion_B")),
            lambda: audits.audit_arms(r2["BUILDER"]["replicates"], ARMS2)], [
            ("run 3, STRATEGIST: eight arms", lambda: audits.audit_arms(r3["STRATEGIST"]["replicates"], ARMS3), FAIL)]),
        "G9.clauses": ("every clause has a fixture that makes it false and one that makes it true", [
            lambda: audits.audit_clauses(toy_cells(), toy_clauses)], [
            ("run 2: nine cells, thirteen clauses", lambda: audits.audit_clauses(r2, audits.clauses_run2), UNQUALIFIED),
            ("run 3: four cells, thirteen clauses", lambda: audits.audit_clauses(r3, audits.clauses_run3), UNQUALIFIED)]),
        "G9.sham": ("a sham can fail and leaves the organism where it was", [
            lambda: audits.audit_sham(toy_cells()["GOOD"]["replicates"],
                                      audits.clause_table(toy_cells(), toy_clauses)["NESTING.sham_harmless"])], [
            ("run 2, BUILDER: the sham removes unused entries",
             lambda: audits.audit_sham(r2["BUILDER"]["replicates"], t2["NESTING.sham_harmless"]), FAIL),
            ("run 3, STRATEGIST: the sham swaps two idle orders",
             lambda: audits.audit_sham(r3["STRATEGIST"]["replicates"], t3["NESTING.sham_harmless"]), UNQUALIFIED)]),
        "G10.setting": ("the nine open choices are registered before the run", [
            lambda: audits.audit_setting(SETTING_OK)], [
            ("run 2 as it was registered", lambda: audits.audit_setting(audits.RUN2), BLOCKED),
            ("run 3 as it was registered", lambda: audits.audit_setting(audits.RUN3), BLOCKED)]),
        "G10.contrast": ("a contrast named after one variable changes that variable only", [
            lambda: audits.audit_contrast("parts_shared", audits.RUN3, dict(audits.RUN3, parts_shared=True))], [
            ("run 2 against run 3, named after shared parts",
             lambda: audits.audit_contrast("parts_shared", audits.RUN2, audits.RUN3), FAIL)]),
        "G10.ruler": ("a ruler is used only with a built positive, a built negative and no gaps", [
            lambda: audits.ruler_status("ORDER3_BITS", receipts=COUNTERFEIT)], [
            ("the strong recursive claim: no positive exists",
             lambda: audits.ruler_status("STRONG_RECURSION", receipts=COUNTERFEIT), UNQUALIFIED),
            ("reuse of built parts: four kit members not built",
             lambda: audits.ruler_status("ORDER3_REUSE", receipts=COUNTERFEIT), UNQUALIFIED),
            ("acquisition at order 4: nothing built",
             lambda: audits.ruler_status("ORDER4_BITS", receipts=COUNTERFEIT), UNQUALIFIED),
            ("a positive called built with no receipt", lambda: audits.ruler_status("STRONG_RECURSION", dict(
                audits.KIT, GENUINE={"built": True, "STRONG_RECURSION": "POSITIVE", "receipt": "RECEIPT_none.json"}),
                receipts=COUNTERFEIT), BLOCKED)]),
        "G11.custody": ("confirmation data is not discovery data", [lambda: claims.check_custody(custody())], [
            ("confirmation seeds reused from discovery", lambda: claims.check_custody(custody(
                confirmation={"seeds": [3, 8, 9], "panel_sha256": "c" * 64, "generator": "renewal-v2"})), FAIL),
            ("the confirmation panel is the discovery panel", lambda: claims.check_custody(custody(
                confirmation={"seeds": [7, 8, 9], "panel_sha256": "d" * 64, "generator": "renewal-v2"})), FAIL),
            ("the champion was chosen on confirmation data",
             lambda: claims.check_custody(custody(selection_data="confirmation")), FAIL),
            ("new seeds of one generator presented as a new family", lambda: claims.check_custody(custody(
                confirmation={"seeds": [7, 8, 9], "panel_sha256": "c" * 64, "generator": "renewal-v1"})), FAIL),
            ("tuning beyond the registered budget", lambda: claims.check_custody(custody(tuning_evaluations=80)), FAIL),
            ("no record of what selection used", lambda: claims.check_custody(custody(selection_data=None)), BLOCKED)]),
        "G12.promote": ("a claim stands only on facets that passed", [
            lambda: claims.promote(claim(), 1), lambda: claims.promote(claim(), 2)], [
            ("the detection facet is absent", lambda: claims.promote(claim(drop="detection"), 1), BLOCKED),
            ("the demand facet failed", lambda: claims.promote(claim(demand=FAIL), 1), FAIL),
            ("the ruler is unqualified in this physics", lambda: claims.promote(claim(detection=UNQUALIFIED), 1),
             UNQUALIFIED),
            ("the evidence was indeterminate", lambda: claims.promote(claim(independence=INDETERMINATE), 1),
             INDETERMINATE),
            ("a structure claim with no exact bound asks for L2",
             lambda: claims.promote(claim(kind="TRANSFER", exact_null=UNQUALIFIED), 2), UNQUALIFIED),
            ("a mechanism claim with no intervention facet", lambda: claims.promote(claim(kind="MECHANISM"), 1),
             BLOCKED)]),
        "G12.render": ("a claim is quoted with its conditions or not at all", [lambda: claims.render(claim())], [
            ("a claim stripped of its conditions", lambda: claims.render(dict(claim(), conditions={})), BLOCKED)]),
    }


def known_escapes():
    """Faults this harness is known NOT to catch. Each is run, and the test suite pins the escape.

    They are listed so that nobody reads a passing harness as covering them.
    """
    return [
        {"gate": "G3.exclusion",
         "fault": "a bound of 0.25 where the class reaches 0.5",
         "verdict": scope(loose_exclusion(0.25)).verdict,
         "why": "64 episodes cannot tell an impostor at 0.5 from a bound of 0.25 at alpha 1e-6. A bound that is "
                "wrong by less than the panel can resolve passes. An exact bound has to be derived and "
                "re-derived by a second author; it cannot be tested into existence."},
        {"gate": "G6.observer",
         "fault": "an observer that draws from the world's random stream, checked on scores only",
         "verdict": all_positives(lambda m: torture.observer_equivalence(
             m, PAIRS, torture.greedy_observer, compare="score")).verdict,
         "why": "the positives hold their bit robustly, so their answers do not change when the distractors do. "
                "Comparing scores passes a broken observer; the gate compares whole trajectories."},
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
