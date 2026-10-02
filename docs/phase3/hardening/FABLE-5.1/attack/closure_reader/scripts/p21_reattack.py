"""The reader's 71 broken cases and 12 sound cases of the first attack, ported to the second version's API."""
import copy
import json

from drv import *

R = retain1
seq = registration
P = meta.PAIRS
p_ok = dict(R.PANEL)
G1, G2, G3, KEYS = audits.G1, audits.G2, audits.G3, audits.KEYS
r2, r3 = meta.run2(), meta.run3()
t3 = audits.clause_table(r3, audits.clauses_run3)
REP = meta.REPORTED
F = meta.FOUNDERS
B = meta.BUDGET
pinned = {e["gate"]: e["fault"] for e in meta.known_escapes()}


def nan_cell():
    return seq.check_cell(meta.cell(known_answers={"HOLDS": float("nan"), "FAILS": float("nan")}))


class WordAttractor(R.Register):
    physics = "ATTRACTOR"


class WordPacket(R.Register):
    physics = "PACKET"


class WordAttractorImp(R.RegisterImpostor):
    physics = "ATTRACTOR"


class WordPacketImp(R.RegisterImpostor):
    physics = "PACKET"


def phantom_cal(extra):
    return search.calibration("NEEDLE", "NEUTRAL", B, "COLD", F, 0, meta.phantom(extra))


def short_cal(frac):
    return search.calibration("NEEDLE", "NEUTRAL", B, "COLD", F, 0, meta.short_budget(frac))


def rigged_registry():
    """The registry is a declaration: call the organism that passed a positive for the strong claim."""
    runs = [("GENUINE", "S19@RUN2", (G2, "cell", "BUILDER"), {"STRONG": "POSITIVE"}),
            ("A_SELECTOR", "S19@RUN2", (G2, "cell", "SELECTOR"), {"STRONG": "NEGATIVE"})]
    return audits.ruler_status("STRONG", "S19@RUN2", CF, runs, {})


def swapped_setting():
    other = {"note": "see the paper"}
    c = dict(meta.claim(), setting=other, setting_sha256=claims.setting_hash(other))
    return claims.render(c)


# (old id, what it was, port on the new API, which pinned escape it is if it still passes)
E = [
    ("E01", "G1.cell: power declared for one answer only", lambda: seq.check_cell(meta.cell(known_answers={"HOLDS": 0.999})), None),
    ("E02", "G1.cell: power is NaN", nan_cell, None),
    ("E03", "G1.cell: power 99 (percent)", lambda: seq.check_cell(meta.cell(known_answers={"HOLDS": 99, "FAILS": 99})), None),
    ("E04", "G1.cell: registered seeds repeated", lambda: seq.check_cell(meta.cell(registered_seeds=[5000] * 24)), None),
    ("E05", "G1.cell: table emits an unregistered outcome", lambda: seq.check_cell(meta.cell(verdict_table=meta.table(
        [(22, 24, "HOLDS"), (0, 12, "FAILS"), (13, 20, "INDETERMINATE"), (21, 21, "BANANA")]))), None),
    ("E06", "G1.cell: exposure = 'unknown'", lambda: seq.check_cell(meta.cell(exposure="unknown")), None),
    ("E07", "G1.cell: attainability rests on a declared number (now: per-unit rates declared 1.0 and 0.0, nothing behind them)",
     lambda: seq.check_cell(meta.cell(known_answers={"HOLDS": 1.0, "FAILS": 0.0})), None),
    ("E08", "G1.receipt: the receipt copies the registered hash (now: the code on hand is other code)",
     lambda: seq.check_receipt(meta.cell(), meta.run_receipt(ran_at=101), b"other code\n"), None),
    ("E09", "G1.receipt: duplicate-padded seeds", lambda: seq.check_receipt(
        meta.cell(registered_seeds=[5000, 5000] + list(range(5001, 5023))),
        meta.run_receipt(seeds=[5000, 5000] + list(range(5001, 5023))), meta.SOURCE), None),
    ("E10", "G10.ruler: receipts are unrelated files that exist", lambda: audits.ruler_status(
        "BITS", "BITS@KEYS", CF, [(m, s, ("README.md",) + src[1:], a) for m, s, src, a in audits.RUNS]), None),
    ("E11", "G10.ruler: the strong claim made to pass by declaration (now: the registry calls the fixed builder a positive)",
     rigged_registry, None),
    ("E12", "G10.ruler: called without the receipts folder", None, None),
    ("E13", "G10.setting: power registered as 0.2", lambda: audits.audit_setting(dict(meta.SETTING_OK, power=0.2)), None),
    ("E14", "G10.setting: power 'not computed', horizon 'n/a'",
     lambda: audits.audit_setting(dict(meta.SETTING_OK, power="not computed", amortization_horizon="n/a")), None),
    ("E15", "G10.setting: every field 'tbd'", lambda: audits.audit_setting({k: "tbd" for k in audits.SETTING}), None),
    ("E16", "G10.contrast: two things change, one of them not written down",
     lambda: audits.audit_contrast("parts_shared", audits.RUN3, dict(audits.RUN3, parts_shared=True)), None),
    ("E17", "G11: the same generator renamed (now: same code hash)", lambda: claims.check_custody(
        meta.custody(confirmation=meta.side(generator_sha256="1" * 64))), None),
    ("E18", "G11: confirmation with no seeds", lambda: claims.check_custody(meta.custody(confirmation=meta.side(seeds=[]))), None),
    ("E19", "G11: acceptance rule fixed after the data was seen", lambda: claims.check_custody(meta.custody(rule_fixed_at=30)), None),
    ("E20", "G11: one custodian for both sets", lambda: claims.check_custody(meta.custody(confirmation_custodian="tuner")), None),
    ("E21", "G11: negative tuning count", lambda: claims.check_custody(meta.custody(tuning_evaluations=-5)), None),
    ("E22", "G12: a structure claim whose exact_null facet is simply asserted PASS",
     lambda: claims.promote(meta.claim("TRANSFER"), 2), "G12.promote"),
    ("E23", "G12: L3 with 'reproduced' asserted", lambda: claims.promote(meta.claim(reproduced=PASS), 3), "G12.promote"),
    ("E24", "G12.render: conditions that are not the registered setting",
     lambda: claims.render(dict(meta.claim(), setting={"note": "see the paper"})), None),
    ("E25", "G12.render: a claim whose facets all failed is rendered like a logged run",
     lambda: Result("render", FAIL if "withheld: " in claims.render(meta.claim(**{f: FAIL for f in claims.L1})).reason
                    else PASS, claims.render(meta.claim(**{f: FAIL for f in claims.L1})).reason[:60]), None),
    ("E26", "G2: positive declared at 1.0, n = 20", lambda: stats.preflight(20, 0.5, 1e-6, 1.0), None),
    ("E27", "G2: alpha = 0.5", lambda: stats.preflight(64, 0.5, 0.5, 1.0), None),
    ("E28", "G2: alpha = 0.011", lambda: stats.preflight(64, 0.5, 0.011, 1.0), None),
    ("E29", "G3: always-POSITIVE ruler on a panel with no impostors",
     lambda: meta.exclusion(lambda make, seeds: "POSITIVE", {k: (v[0], None) for k, v in p_ok.items()}), None),
    ("E30", "G3: always-POSITIVE ruler on an empty panel", lambda: meta.exclusion(lambda make, seeds: "POSITIVE", {}), None),
    ("E31", "G4: impostor = Inverter", lambda: meta.entry("REGISTER", dict(p_ok, REGISTER=(R.Register, R.Inverter))), None),
    ("E32", "G4: impostor not matched (PACKET impostor = Constant)",
     lambda: meta.entry("PACKET", dict(p_ok, PACKET=(R.PacketRing, R.Constant))), None),
    ("E33", "G4: CHEMISTRY admitted on register organisms",
     lambda: meta.entry("CHEMISTRY", {"CHEMISTRY": (R.Register, R.RegisterImpostor)}), None),
    ("E34", "G5: REGISTER_SWAP declared SHARED on three look-alike physics", lambda: meta.neutral(
        "REGISTER_SWAP", "SHARED", {p: (meta.relabel(R.Register, p), meta.relabel(R.RegisterImpostor, p))
                                    for p in ("REGISTER", "ATTRACTOR", "PACKET")}), "G5.neutrality"),
    ("E35", "G5: REGISTER_SWAP SHARED, three physics that all keep an attribute w", lambda: meta.neutral(
        "REGISTER_SWAP", "SHARED", {"REGISTER": R.PANEL["REGISTER"], "ATTRACTOR": (WordAttractor, WordAttractorImp),
                                    "PACKET": (WordPacket, WordPacketImp)}), "G5.neutrality"),
    ("E36", "G5: declared valid nowhere", lambda: meta.neutral("REGISTER_SWAP", []), None),
    ("E37", "G5: always-NEGATIVE ruler declared valid nowhere",
     lambda: meta.neutral("X", [], ruler=lambda m, s: "NEGATIVE"), None),
    ("E38", "G5: interchange ruler, impostor = Inverter",
     lambda: meta.neutral("INTERCHANGE", "SHARED", dict(p_ok, REGISTER=(R.Register, R.Inverter))), None),
    ("E39", "G5: class exclusion, impostor = Inverter",
     lambda: meta.neutral("CLASS_EXCLUSION", "SHARED", dict(p_ok, REGISTER=(R.Register, R.Inverter))), None),
    ("E40", "G6.observer: rewrites the register after the probe",
     lambda: meta.all_positives(lambda m: torture.observer_equivalence(m, P, torture.writing_observer)), None),
    ("E41", "G6.observer: disturbs the world only on unchecked seeds",
     lambda: meta.all_positives(lambda m: torture.observer_equivalence(m, P, torture.rare_observer(P))), "G6.observer"),
    ("E42", "G6.observer: bumps the world's episode counter",
     lambda: meta.all_positives(lambda m: torture.observer_equivalence(m, P, torture.counter_observer)), None),
    ("E43", "G6.observer: draws from the world's stream after the last distractor",
     lambda: meta.all_positives(lambda m: torture.observer_equivalence(m, P, torture.late_observer)), None),
    ("E44", "G6.reset: state survives reset, shown only in cued episodes", lambda: torture.reset_closure(R.SneakyRegister, P), None),
    ("E45", "G6.restart: restore that merges with stale state", lambda: torture.restart_equivalence(R.PacketAppendRestore, P), None),
    ("E46", "G6.restart: restore that leaves a stale word", lambda: torture.restart_equivalence(R.RegisterKeepIfSet, P), None),
    ("E47", "G6.restart: capture wrong only after step 5", lambda: torture.restart_equivalence(R.LatticeLateBadCapture, P), None),
    ("E48", "G7.cal: estimator ran 90% of the budget", lambda: short_cal(0.9), "G7.calibration"),
    ("E49", "G7.cal: 80% of the budget", lambda: short_cal(0.8), "G7.calibration"),
    ("E50", "G7.cal: 70% of the budget", lambda: short_cal(0.7), "G7.calibration"),
    ("E51", "G7.cal: 60% of the budget", lambda: short_cal(0.6), "G7.calibration"),
    ("E52", "G7.cal: 50% of the budget", lambda: short_cal(0.5), "G7.calibration"),
    ("E53", "G7.cal: 40% of the budget", lambda: short_cal(0.4), "G7.calibration"),
    ("E54", "G7.cal: phantom hits, same bias as 2 of 48 (11 of 256)", lambda: phantom_cal(11), "G7.calibration"),
    ("E55", "G7.cal: phantom hits, same bias as 4 of 48 (21 of 256)", lambda: phantom_cal(21), "G7.calibration"),
    ("E56", "G7.cal: phantom hits, same bias as 6 of 48 (32 of 256)", lambda: phantom_cal(32), "G7.calibration"),
    ("E57", "G7.cal: phantom hits, same bias as 8 of 48 (43 of 256)", lambda: phantom_cal(43), "G7.calibration"),
    ("E58", "G7.report: cold discovery with zero hits",
     lambda: search.check_report(meta.report("COLD_DISCOVERY", "VALLEY", policies=("STRICT",))), None),
    ("E59", "G7.report: more hits than founders", lambda: search.check_report(meta.recount(
        meta.report(), NEUTRAL={"seeds": list(REP), "hits": 10 * len(REP)})), None),
    ("E60", "G7.report: a null from two policies, neither able to cross a neutral step",
     lambda: search.check_report(meta.null("NEEDLE", ("STRICT", "ELITIST"))), None),
    ("E61", "G7.report: prose label 'the substrate cannot do it'",
     lambda: search.check_report(meta.null(label="the substrate cannot do it")), None),
    ("E62", "G7.report: prose label 'no capacity in this physics'",
     lambda: search.check_report(meta.null(label="no capacity in this physics")), None),
    ("E63", "G7.report: positive control from another policy and landscape (now: computed by the gate; budget 5)",
     lambda: search.check_report(meta.null(budget=5)), None),
    ("E64", "G7.report: start says COLD, the runs were repair", lambda: search.check_report(meta.recount(
        meta.report("COLD_DISCOVERY", "VALLEY", policies=("STRICT",)),
        STRICT={"seeds": list(REP), "hits": meta.hits("VALLEY", "STRICT", "REPAIR", 1)})), None),
    ("E65", "G7.report: invented hit count on seeds that were never run",
     lambda: search.check_report(meta.recount(meta.report(), NEUTRAL={"seeds": list(range(48)), "hits": 5})), None),
    ("E66", "G8: the probe carries the complement of the answer",
     lambda: torture.demand_closure(meta.DEMAND, meta.TRAIN, leak_key="inverted"), None),
    ("E67", "G8: the probe carries the answer in 40% of episodes",
     lambda: torture.demand_closure(meta.DEMAND, meta.TRAIN, leak_key="partial"), None),
    ("E68", "G8: the cue is the xor of the last two distractors",
     lambda: torture.demand_closure(meta.DEMAND, meta.TRAIN, cue_from_distractors=True), None),
    ("E69", "G9.arms: one replicate of 24 nudged", lambda: audits.audit_arms(meta.nudged(r3["STRATEGIST"]["replicates"]), meta.ARMS3), None),
    ("E70", "G9.clauses: one catch-all cell", lambda: audits.audit_clauses(meta.toy_cells(**meta.CATCH_ALL), meta.toy_clauses), None),
    ("E71", "G9.sham: idle sham plus a cell where another operation is called sham", lambda: audits.audit_sham(
        r3["STRATEGIST"]["replicates"], dict(t3["NESTING.sham_harmless"], ANOTHER=0)), "G9.sham"),
]

S = [
    ("S01", "G1.cell: no design runs were made, design_seeds = []", lambda: seq.check_cell(meta.cell(design_seeds=[]))),
    ("S02", "G1.cell: zero exposure declared as {}", lambda: seq.check_cell(meta.cell(exposure={}))),
    ("S03", "G1.receipt: run at the clock tick of its registration",
     lambda: seq.check_receipt(meta.cell(), meta.run_receipt(ran_at=100), meta.SOURCE)),
    ("S04", "G10.contrast: the same setting worded differently", lambda: audits.audit_contrast(
        "parts_shared", audits.RUN3, dict(audits.RUN3, parts_shared=True, cost="tasks to an accepted procedure, no cut-off"))),
    ("S05", "G4: sound positive, 16 seeds", lambda: meta.entry("REGISTER", seeds=meta.SEEDS[:16])),
    ("S06", "G4: sound positive, 19 seeds", lambda: meta.entry("REGISTER", seeds=meta.SEEDS[:19])),
    ("S07", "G5: right on four physics, a fifth registered with no organism",
     lambda: meta.neutral("CLASS_EXCLUSION", "SHARED", dict(p_ok, CHEMISTRY=(None, None)))),
    ("S08", "G7.report: prose 'not a claim that the target is impossible'",
     lambda: search.check_report(meta.null(label="a bound on reach; not a claim that the target is impossible"))),
    ("S09", "G7.report: bound rounded to four places",
     lambda: search.check_report(meta.null(upper_bound=round(stats.zero_hit_upper(len(REP)), 4)))),
    ("S10", "G7.report: a more cautious bound (99%)",
     lambda: search.check_report(meta.null(upper_bound=stats.zero_hit_upper(len(REP), 0.99)))),
    ("S11", "G9.arms: two separate computations that both hit a 400-task cap", lambda: audits.audit_arms(
        [{"naive_B": 400, "dev_B": 40, "lesion_B": 400, "sham_B": 41 + i % 2} for i in range(24)],
        ("naive_B", "dev_B", "lesion_B", "sham_B"))),
    ("S12", "G9.sham: a neutral sham at small counts (3 against 4)", lambda: audits.audit_sham(
        [{"dev_B": 3, "sham_B": 4} for _ in range(24)], {"GOOD": 24, "BAD": 0})),
]

print("%-4s %-13s %-9s %s" % ("id", "verdict", "", "case"))
still, known, new, na = [], [], [], []
for cid, what, thunk, pin in E:
    if thunk is None:
        na.append(cid)
        print("%-4s %-13s %-9s %s" % (cid, "n/a", "", what + "  (the argument is now required)"))
        continue
    r = thunk()
    tag = ""
    if r.verdict == PASS:
        still.append(cid)
        if pin and pin in pinned:
            known.append(cid)
            tag = "pinned"
        else:
            new.append(cid)
            tag = "NOT pinned"
    print("%-4s %-13s %-9s %s%s" % (cid, r.verdict, tag, what, ("   | " + r.reason[:110]) if r.reason else ""))
print()
print("broken cases: %d ported, %d no longer expressible; still PASS: %d (%d are instances of a pinned escape, %d are not)"
      % (len(E) - len(na), len(na), len(still), len(known), len(new)))
print("  pinned:", known)
print("  not pinned:", new)
print()
rej = []
for cid, what, thunk in S:
    r = thunk()
    if r.verdict != PASS:
        rej.append((cid, r.verdict))
    print("%-4s %-13s %s%s" % (cid, r.verdict, what, ("   | " + r.reason[:110]) if r.reason else ""))
print("sound cases: %d; not PASS: %d %s" % (len(S), len(rej), rej))
