"""GM. The gates are rulers too: each must pass a sound case and reject a case that must not pass.

A gate with no such case is UNQUALIFIED: it has never been shown able to fail. A gate that passes a
broken case has an escape. A gate that rejects a sound case makes false accusations. qualify() runs
every gate against its registered sound cases and mutants and returns one row per gate.

Where the cases come from. The first version of this registry held only cases written by the author
of the gates. Three adversarial reads followed. Each found faults the gates passed; most are now
registered here beside the author's cases. What the gates still cannot catch is in known_escapes(),
each run and pinned by a test, so that a passing harness is not read as covering it. Every gate has
at least one, and the list is not complete: each read so far has found more.

Several mutants are not invented. They are this reviewer's own runs 1 to 4, read from their receipts.
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
PAIRS = list(range(2000, 2012))                                        # 12 seeds for torture
FOUNDERS = list(range(3000, 3256))                                     # 256 independent founders for calibration
REPORTED = list(range(4000, 4128))                                     # 128 founders registered for a search report
DEMAND = list(range(10000, 12048))                                     # 2,048 episodes for demand closure
TRAIN = list(range(20000, 22048))                                      # 2,048 others to fit the tables
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
FACETS = {1: ("registration", "power", "detection", "demand", "independence", "exposure", "resources"),
          2: ("exact_null", "attack_round", "custody", "second_implementation"), 3: ("reproduced",), 4: ("predicted",)}
KIND_FACETS = {"EFFECT": (), "TRANSFER": ("new_family",), "MECHANISM": ("intervention",),
               "ORIGIN": ("cold_start", "class_bound"), "ECONOMY": ("lifecycle_cost", "frozen_comparators"),
               "NESTED": ("retention_at_boundary", "mediation", "cargo_control", "flattened_twin"),
               "LAW": ("prediction_registered",)}


def receipt(name):
    return json.loads((COUNTERFEIT / name).read_text(encoding="ascii"))


# ---------------------------------------------------------------- fixtures: registration

def table(rule=None, outcomes=("HOLDS", "FAILS", "INDETERMINATE")):
    return {"n": 24, "outcomes": list(outcomes),
            "rule": rule or [(22, 24, "HOLDS"), (0, 12, "FAILS"), (13, 21, "INDETERMINATE")]}


def runs(hits, n):
    return {"design_hits": hits, "design_n": n}


def cell(**change):
    c = {"physics": "REGISTER", "search": "none (designed)", "world": "RETAIN-1, gap 6", "development": "none",
         "boundary": "internal; environment writes certified zero", "resources": {"steps": 8},
         "measurement": "a replicate passes if its organism excludes the class", "exposure": {"tuning_evaluations": 0},
         "adapter": "symbolic", "independent_unit": "replicate", "design_seeds": [1, 2, 3],
         "registered_seeds": list(range(5000, 5024)), "verdict_table": table(),
         "known_answers": {"HOLDS": runs(480, 480), "FAILS": runs(96, 480)},
         "source_sha256": registration.sha(SOURCE), "registered_at": 100}
    c.update(change)
    return c


def run_receipt(**change):
    r = {"source_sha256": registration.sha(SOURCE), "seeds": list(range(5000, 5024)), "ran_at": 200,
         "outcome": "HOLDS"}
    r.update(change)
    return r


def every_missing_field_blocks(check, make, fields):
    """One mutant for many: BLOCKED only if removing any single required field is BLOCKED."""
    open_ = [f for f in fields if check(make(**{f: None})).verdict != BLOCKED]
    return Result("fields", PASS if open_ else BLOCKED, "not required after all: %s" % ", ".join(open_))


# ---------------------------------------------------------------- fixtures: rulers and panel

def exclusion(ruler=rulers.exclusion_ruler, panel=None, seeds=None, weak=retain1.FadingRegister, blocks=None,
              edges=rulers.EDGES):
    return rulers.exclusion_gate(ruler, retain1.PANEL if panel is None else panel, SEEDS if seeds is None else seeds,
                                 weak, BLOCKS if blocks is None else blocks, edges)


def entry(physics, panel=None, seeds=None):
    return rulers.entry_gate(physics, retain1.PANEL if panel is None else panel, SEEDS if seeds is None else seeds)


def neutral(name, declared, panel=None, ruler=None, seeds=None):
    return rulers.neutrality_gate(name, ruler or rulers.RULERS[name], declared,
                                  retain1.PANEL if panel is None else panel, SEEDS if seeds is None else seeds)


def relabel(cls, physics):
    """The same machine under another physics name. The gates read the name; they cannot read the machine."""
    return type(cls.__name__ + "As" + physics.title(), (cls,), {"physics": physics})


def organism_scores():
    """Scores of 64: the four positives, the weak positive, and each impostor on nine blocks of seeds."""
    pos = [retain1.score(p, SEEDS) for _, (p, _) in sorted(retain1.PANEL.items())]
    imp = {name: [retain1.score(i, block) for block in [SEEDS] + BLOCKS]
           for name, (_, i) in sorted(retain1.PANEL.items())}
    return pos, retain1.score(retain1.FadingRegister, SEEDS), imp


def edges_for(bound, n=64, alpha=rulers.ALPHA, weakest=rulers.P_WEAKEST):
    """The thresholds a registration would hold if its bound were `bound`: every count next to a change of
    answer, with the answer it must get."""
    names = {"EXCLUDES": "POSITIVE", "AT_BOUND": "NEGATIVE"}
    answer = [names.get(a, a) for a in (stats.classify(k, n, bound, alpha, weakest) for k in range(n + 1))]
    return {k: answer[k] for k in range(n + 1)
            if (k > 0 and answer[k] != answer[k - 1]) or (k < n and answer[k] != answer[k + 1])}


def bracket():
    """Which bounds still return the known answers: from the organisms alone (grid of 0.001), and at the
    registered thresholds (grid of 0.00001)."""
    pos, weak, imp = organism_scores()
    flat = [s for v in imp.values() for s in v]

    def at(k, b):
        return stats.classify(k, 64, b, rulers.ALPHA, rulers.P_WEAKEST)

    def organisms_ok(b):
        return all(at(s, b) == "EXCLUDES" for s in pos + [weak]) and all(at(s, b) == "AT_BOUND" for s in flat)

    def edges_ok(b):
        return all({"EXCLUDES": "POSITIVE", "AT_BOUND": "NEGATIVE"}.get(at(k, b), at(k, b)) == want
                   for k, want in rulers.EDGES.items())

    by_organisms = [b / 1000 for b in range(1, 1000) if organisms_ok(b / 1000)]
    with_edges = [b / 100000 for b in range(49000, 51001) if edges_ok(b / 100000)]
    return {"by_organisms": [min(by_organisms), max(by_organisms)],
            "at_registered_thresholds": [min(with_edges), max(with_edges)],
            "impostor_scores": [min(flat), max(flat)], "impostor_series": len({tuple(v) for v in imp.values()}),
            "positive_scores": pos, "weak_positive_score": weak}


def all_positives(check):
    """Run one torture check on every positive of the panel; the first failure wins."""
    for physics, (positive, _) in sorted(retain1.PANEL.items()):
        r = check(positive)
        if r.verdict != PASS:
            return Result(r.gate, r.verdict, "%s: %s" % (physics, r.reason))
    return Result("panel", PASS)


def all_but_first_observer(log):
    """Fault: draws from the world's stream on every seed but the first one checked."""
    def observe(world, seed, t, org):
        if seed != PAIRS[0]:
            world.draw(seed)
    return observe


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
           seeds=None, **change):
    seeds = REPORTED if seeds is None else seeds
    r = {"claim": claim, "landscape": landscape, "budget": budget, "start_law": law, "distance": distance,
         "policies": {p: {"seeds": list(seeds), "hits": hits(landscape, p, law, distance, seeds, budget)}
                      for p in policies}}
    r.update(change)
    return r


def recount(r, **policies):
    """A report with its counts replaced."""
    return dict(r, policies=policies)


def null(landscape="VALLEY", policies=("STRICT", "NEUTRAL"), seeds=None, **change):
    fields = {"scope": "POLICIES_AND_BUDGET", "upper_bound": stats.zero_hit_upper(len(REPORTED))}
    fields.update(change)
    return report("REACH_BOUNDED", landscape, policies=policies, seeds=seeds, **fields)


def checked(r, registered=None):
    return search.check_report(r, REPORTED if registered is None else registered)


def missers(n=128):
    """Founders picked, after the fact, because the neutral search missed the needle from them."""
    out, s = [], 50000
    while len(out) < n:
        if search.sample_reach("NEEDLE", "NEUTRAL", BUDGET, "COLD", [s]) == 0:
            out.append(s)
        s += 1
    return out


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


def never_searches(landscape, policy, budget, kind, seeds, distance=0):
    """Fault: an estimator that reports no hit, whatever it is asked."""
    return 0


def always_hits(landscape, policy, budget, kind, seeds, distance=0):
    """Fault: an estimator that reports a hit for every founder."""
    return len(seeds)


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


def nudged(reps, replicates=1):
    """Fault: arms that are one series, made to differ in a few replicates of 24."""
    reps = copy.deepcopy(reps)
    for i in range(replicates):
        for arm, d in (("lesion_B", 1), ("sham_B", 1), ("rescue_B", 2), ("v_donor_B", 3),
                       ("irrelevant_history_B", 2)):
            reps[i][arm] += d
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


def claim(kind="EFFECT", drop=None, level=2, **facets):
    """A claim holding every facet its kind needs up to `level`, each with a source."""
    names = tuple(f for lv in range(1, level + 1) for f in FACETS[lv]) + KIND_FACETS.get(kind, ())
    f = {k: {"verdict": PASS, "source": "RECEIPT_harness_v0.json"} for k in names}
    for k, v in facets.items():
        f[k] = v if isinstance(v, dict) or v is None else {"verdict": v, "source": "RECEIPT_harness_v0.json"}
    for k in ([drop] if isinstance(drop, str) else list(drop or [])):
        f.pop(k)
    return {"kind": kind, "cell": "REGISTER/RETAIN-1/designed", "facets": f, "setting": dict(SETTING),
            "excluded_class": "policies that carry nothing across the gap",
            "setting_sha256": claims.setting_hash(SETTING)}


def every_facet_blocks(level):
    """One mutant for several: BLOCKED only if a claim holding every facet up to that level stands there and
    dropping any single facet of that level is BLOCKED."""
    whole = claims.promote(claim(level=level), level).verdict
    open_ = [f for f in FACETS[level] if claims.promote(claim(level=level, drop=f), level).verdict != BLOCKED]
    return Result("facets", PASS if open_ or whole != PASS else BLOCKED,
                  "not required after all: %s" % ", ".join(open_))


def every_kind_facet_blocks():
    """One mutant for eleven: BLOCKED only if dropping any facet a kind needs is BLOCKED for that kind."""
    open_ = ["%s.%s" % (k, f) for k, fs in sorted(KIND_FACETS.items()) for f in fs
             if claims.promote(claim(k, drop=f), 1).verdict != BLOCKED]
    return Result("facets", PASS if open_ else BLOCKED, "not required after all: %s" % ", ".join(open_))


# ---------------------------------------------------------------- the registry

def gates():
    """Gate id -> (what it guards, sound cases, mutants). A mutant is (name, thunk, registered verdict)."""
    R = retain1
    p_ok = dict(R.PANEL)
    r2, r3 = run2(), run3()
    t2, t3 = audits.clause_table(r2, audits.clauses_run2), audits.clause_table(r3, audits.clauses_run3)
    toy_row = audits.clause_table(toy_cells(**ISOLATING), toy_clauses)["NESTING.sham_harmless"]
    seq, obs_eq, design = registration, torture.observer_equivalence, stats.preflight_from_design
    hitter = next(s for s in REPORTED if hits("NEEDLE", "NEUTRAL", seeds=[s]))
    picked = missers()
    bits = [r for r in audits.RUNS if "BITS" in r[3]]
    return {
        "G1.cell": ("a run exists only as a complete registered cell whose answers are attainable", [
            lambda: seq.check_cell(cell()),
            lambda: seq.check_cell(cell(design_seeds=[]))], [
            ("a required field is missing (each of the sixteen, in turn)",
             lambda: every_missing_field_blocks(seq.check_cell, cell, CELL_FIELDS), BLOCKED),
            ("exposure given as a word", lambda: seq.check_cell(cell(exposure="unknown")), BLOCKED),
            ("a negative count of tuning evaluations",
             lambda: seq.check_cell(cell(exposure={"tuning_evaluations": -5})), BLOCKED),
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
            ("a design seed is repeated", lambda: seq.check_cell(cell(design_seeds=[1, 1, 2])), FAIL),
            ("the table counts 24 units and three seeds are registered",
             lambda: seq.check_cell(cell(registered_seeds=[5000, 5001, 5002])), FAIL),
            ("the table counts 24 units and 48 seeds are registered",
             lambda: seq.check_cell(cell(registered_seeds=list(range(5000, 5048)))), FAIL),
            ("a positive right in 466 of 480 design units: its answer comes out 87 times in 100",
             lambda: seq.check_cell(cell(known_answers={"HOLDS": runs(466, 480), "FAILS": runs(96, 480)})), BLOCKED),
            ("a positive perfect in 240 design units: its answer is attainable at 0.9897, under the floor",
             lambda: seq.check_cell(cell(known_answers={"HOLDS": runs(240, 240), "FAILS": runs(96, 480)})), BLOCKED),
            ("design runs registered for one answer only",
             lambda: seq.check_cell(cell(known_answers={"HOLDS": runs(480, 480)})), BLOCKED),
            ("a rate declared, with no design runs behind it",
             lambda: seq.check_cell(cell(known_answers={"HOLDS": 1.0, "FAILS": 0.0})), BLOCKED),
            ("a negative count of design hits",
             lambda: seq.check_cell(cell(known_answers={"HOLDS": runs(480, 480), "FAILS": runs(-5, 480)})), BLOCKED),
            ("design counts given as true and false",
             lambda: seq.check_cell(cell(known_answers={"HOLDS": runs(True, True), "FAILS": runs(False, True)})),
             BLOCKED),
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
            ("a run on 23 of the 24 registered seeds",
             lambda: seq.check_receipt(cell(), run_receipt(seeds=list(range(5000, 5023))), SOURCE), FAIL),
            ("run earlier than its registration", lambda: seq.check_receipt(cell(), run_receipt(ran_at=99), SOURCE),
             FAIL),
            ("run at the clock tick of its registration: the order cannot be decided",
             lambda: seq.check_receipt(cell(), run_receipt(ran_at=100), SOURCE), INDETERMINATE),
            ("receipt without a source hash",
             lambda: seq.check_receipt(cell(), run_receipt(source_sha256=""), SOURCE), BLOCKED),
            ("receipt without the time it ran", lambda: seq.check_receipt(cell(), run_receipt(ran_at=None), SOURCE),
             BLOCKED),
            ("clock readings given as text",
             lambda: seq.check_receipt(cell(registered_at="100"), run_receipt(ran_at="99"), SOURCE), BLOCKED),
            ("the code is not on hand", lambda: seq.check_receipt(cell(), run_receipt()), BLOCKED)]),
        "G2.preflight": ("no run starts unless both answers of the ruler are attainable", [
            lambda: design(len(SEEDS), rulers.BOUND, rulers.ALPHA, 256, 256)], [
            ("16 episodes cannot reach alpha 1e-6", lambda: design(16, 0.5, 1e-6, 256, 256), BLOCKED),
            ("a positive right in 192 of 256 design runs", lambda: design(64, 0.5, 1e-6, 192, 256), BLOCKED),
            ("alpha 0.05: a class member is called positive too often", lambda: design(64, 0.5, 0.05, 256, 256),
             BLOCKED),
            ("a positive seen perfect in 20 design runs, registered at 20 episodes",
             lambda: design(20, 0.5, 1e-6, 20, 20), BLOCKED),
            ("a rate with no design runs behind it", lambda: design(64, 0.5, 1e-6, 0, 0), BLOCKED),
            ("design counts given as true and true", lambda: design(64, 0.5, 1e-6, True, True), BLOCKED),
            ("a class member that would be called negative 70 times in 100",
             lambda: stats.preflight(18, 0.02, 1e-6, 0.6), BLOCKED),
            ("a rate given as 99", lambda: stats.preflight(64, 0.5, 1e-6, 99), BLOCKED)]),
        "G3.exclusion": ("class exclusion returns the known answers on organisms and at its registered thresholds", [
            lambda: exclusion()], [
            ("a bound of 0.10 where the class reaches 0.5", lambda: exclusion(rulers.make_exclusion_ruler(0.10)), FAIL),
            ("a bound of 0.25", lambda: exclusion(rulers.make_exclusion_ruler(0.25)), FAIL),
            ("a bound of 0.45", lambda: exclusion(rulers.make_exclusion_ruler(0.45)), FAIL),
            ("a bound of 0.70", lambda: exclusion(rulers.make_exclusion_ruler(0.70)), FAIL),
            ("alpha 0.01 in the ruler", lambda: exclusion(rulers.make_exclusion_ruler(alpha=1e-2)), FAIL),
            ("alpha 1e-9 in the ruler", lambda: exclusion(rulers.make_exclusion_ruler(alpha=1e-9)), FAIL),
            ("a weakest positive of 0.99 in the ruler", lambda: exclusion(rulers.make_exclusion_ruler(weakest=0.99)),
             FAIL),
            ("a ruler that always says yes, on a panel with no impostors",
             lambda: exclusion(lambda make, seeds: "POSITIVE", {k: (v[0], None) for k, v in p_ok.items()}), UNQUALIFIED),
            ("a panel with no weak positive", lambda: exclusion(weak=None), UNQUALIFIED),
            ("no registered thresholds", lambda: exclusion(edges=None), UNQUALIFIED),
            ("no further blocks of seeds for the impostors", lambda: exclusion(blocks=[]), UNQUALIFIED),
            ("a bound of 0.33, registered together with thresholds computed from it: one impostor block beats it",
             lambda: exclusion(rulers.make_exclusion_ruler(0.33), edges=edges_for(0.33)), FAIL),
            ("a bound of 0.70, registered together with thresholds computed from it: one impostor block is too low "
             "for it", lambda: exclusion(rulers.make_exclusion_ruler(0.70), edges=edges_for(0.70)), FAIL),
            ("the same block of seeds used eight times", lambda: exclusion(blocks=[BLOCKS[0]] * 8), BLOCKED),
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
            ("30 episodes: a yes is reachable and the weakest positive seldom earns it",
             lambda: entry("REGISTER", seeds=SEEDS[:30]), BLOCKED),
            ("a positive that scores 49 of 64",
             lambda: entry("REGISTER", dict(p_ok, REGISTER=(R.scripted(49), R.RegisterImpostor))), INDETERMINATE)]),
        "G5.neutrality": ("a ruler is shared only where it has returned the known answers", [
            lambda: neutral("CLASS_EXCLUSION", "SHARED"), lambda: neutral("INTERCHANGE", "SHARED"),
            lambda: neutral("INTERCHANGE", "SHARED", dict(p_ok, REGISTER=(R.FadingRegister, R.RegisterImpostor))),
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
            ("interchange on 8 seeds: 16 pairs cannot reach alpha 1e-6",
             lambda: neutral("INTERCHANGE", "SHARED", seeds=PAIRS[:8]), BLOCKED),
            ("class exclusion on 16 episodes", lambda: neutral("CLASS_EXCLUSION", "SHARED", seeds=SEEDS[:16]), BLOCKED)]),
        "G6.observer": ("observing a run does not change it", [
            lambda: all_positives(lambda m: obs_eq(m, PAIRS, torture.quiet_observer)),
            lambda: all_positives(lambda m: obs_eq(m, PAIRS, torture.own_stream_observer))], [
            ("an observer that draws from the world's random stream",
             lambda: all_positives(lambda m: obs_eq(m, PAIRS, torture.greedy_observer)), FAIL),
            ("an observer that draws from it after the last distractor",
             lambda: all_positives(lambda m: obs_eq(m, PAIRS, torture.late_observer)), FAIL),
            ("an observer that rewrites the organism after it has answered",
             lambda: all_positives(lambda m: obs_eq(m, PAIRS, torture.writing_observer)), FAIL),
            ("an observer that advances the world's episode counter",
             lambda: all_positives(lambda m: obs_eq(m, PAIRS, torture.counter_observer)), FAIL),
            ("an observer that writes on the environment",
             lambda: all_positives(lambda m: obs_eq(m, PAIRS, torture.marking_observer)), FAIL),
            ("an observer whose damage the organism repairs before its next step",
             lambda: all_positives(lambda m: obs_eq(m, PAIRS, torture.healing_observer)), FAIL),
            ("an observer that disturbs every episode of a world but its first",
             lambda: all_positives(lambda m: obs_eq(m, PAIRS, torture.later_episodes_observer)), FAIL),
            ("an observer that disturbs every seed but the first",
             lambda: all_positives(lambda m: obs_eq(m, PAIRS, all_but_first_observer)), FAIL),
            ("no seeds", lambda: obs_eq(R.Register, [], torture.quiet_observer), BLOCKED)]),
        "G6.reset": ("after a reset a runtime behaves as one that never ran", [
            lambda: all_positives(lambda m: torture.reset_closure(m, PAIRS)),
            lambda: torture.reset_closure(R.WorldParker, PAIRS, writable_mark=True)], [
            ("a runtime whose reset keeps its word", lambda: torture.reset_closure(R.LeakyResetRegister, PAIRS), FAIL),
            ("a harness that forgets to reset", lambda: torture.reset_closure(R.Register, PAIRS, skip_reset=True), FAIL),
            ("a carry that native() hides and that shows only when a cue arrives",
             lambda: torture.reset_closure(R.SneakyRegister, PAIRS), FAIL),
            ("a carry left by an episode with no cue", lambda: torture.reset_closure(R.BlankCarry, PAIRS), FAIL),
            ("a reset that keeps a step counter", lambda: torture.reset_closure(R.LatticeKeepsClock, PAIRS), FAIL),
            ("an environment that keeps its mark across episodes",
             lambda: torture.reset_closure(R.WorldParker, PAIRS, writable_mark=True, keep_mark=True), FAIL),
            ("a reset that is sound on the first seed and leaks afterwards",
             lambda: torture.reset_closure(R.faulty_from(13, R.Register, R.LeakyResetRegister), PAIRS), FAIL),
            ("no seeds", lambda: torture.reset_closure(R.Register, []), BLOCKED)]),
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
             lambda: torture.restart_equivalence(R.LatticeLateBadCapture, PAIRS), FAIL),
            ("a capture that is wrong after the last step only",
             lambda: torture.restart_equivalence(R.LatticeEndBadCapture, PAIRS), FAIL),
            ("a capture that is sound on the first seed and wrong afterwards",
             lambda: torture.restart_equivalence(R.faulty_from(18, R.PacketRing, R.PacketRingBadCapture), PAIRS), FAIL),
            ("no seeds", lambda: torture.restart_equivalence(R.Register, []), BLOCKED)]),
        "G7.calibration": ("a reach estimator agrees with exact reach on a panel of five cells", [
            lambda: search.calibration_panel(BUDGET, FOUNDERS)], [
            ("repair runs counted as cold reach", lambda: search.calibration_panel(BUDGET, FOUNDERS, repair_as_cold),
             FAIL),
            ("an estimator that ran half the registered budget",
             lambda: search.calibration_panel(BUDGET, FOUNDERS, short_budget(0.5)), FAIL),
            ("an estimator that reports 40 hits it did not have",
             lambda: search.calibration_panel(BUDGET, FOUNDERS, phantom(40)), FAIL),
            ("an estimator that never searches", lambda: search.calibration_panel(BUDGET, FOUNDERS, never_searches),
             FAIL),
            ("an estimator that always reports a hit",
             lambda: search.calibration_panel(BUDGET, FOUNDERS, always_hits), FAIL),
            ("no founders", lambda: search.calibration_panel(BUDGET, []), BLOCKED)]),
        "G7.report": ("a search result is what it says it is", [
            lambda: checked(report()),
            lambda: checked(null()),
            lambda: checked(report("REPAIR_REACH", "VALLEY", "REPAIR", 1, ("STRICT",))),
            lambda: checked(null(upper_bound=round(stats.zero_hit_upper(len(REPORTED)), 4))),
            lambda: checked(null(upper_bound=stats.zero_hit_upper(len(REPORTED), 0.99))),
            lambda: checked(report(budget=24))], [
            ("a repair start declared under a cold-discovery claim",
             lambda: checked(report("COLD_DISCOVERY", "VALLEY", "REPAIR", 1, ("STRICT",))), FAIL),
            ("repair counts reported under a cold start", lambda: checked(recount(
                report("COLD_DISCOVERY", "VALLEY", policies=("STRICT",)),
                STRICT={"seeds": list(REPORTED), "hits": hits("VALLEY", "STRICT", "REPAIR", 1)})), FAIL),
            ("a repair claim made from a cold start", lambda: checked(report("REPAIR_REACH", "ASCENT")), FAIL),
            ("a repair start at distance 0", lambda: checked(report("REPAIR_REACH", "VALLEY", "REPAIR", 0, ("STRICT",))),
             FAIL),
            ("a discovery claimed with nothing found",
             lambda: checked(report("COLD_DISCOVERY", "VALLEY", policies=("STRICT",))), FAIL),
            ("more hits reported than the search had", lambda: checked(recount(
                report(), NEUTRAL={"seeds": list(REPORTED), "hits": hits("NEEDLE", "NEUTRAL") + 9})), FAIL),
            ("a null whose scope is the substrate", lambda: checked(null(scope="SUBSTRATE")), FAIL),
            ("a null that states no scope", lambda: checked(null(scope=None)), BLOCKED),
            ("a null from one policy on a plateau", lambda: checked(null("NEEDLE", ("STRICT",))), BLOCKED),
            ("a null from two policies, neither able to cross a neutral step",
             lambda: checked(null("NEEDLE", ("STRICT", "ELITIST"))), BLOCKED),
            ("a null although the second policy reached the target", lambda: checked(null("NEEDLE")), FAIL),
            ("a null with one hit", lambda: checked(null("NEEDLE", budget=8)), FAIL),
            ("founders chosen by the report because the search missed from them",
             lambda: checked(null("NEEDLE", seeds=picked)), FAIL),
            ("a null on founders that are not the registered ones, with no hit on either set",
             lambda: checked(null(seeds=list(range(7000, 7128)))), FAIL),
            ("founders registered because the search missed from them: the exact count shows it",
             lambda: checked(null("NEEDLE", seeds=picked), picked), FAIL),
            ("one founder that hit, counted 128 times", lambda: checked(recount(
                report(), NEUTRAL={"seeds": [hitter] * len(REPORTED), "hits": len(REPORTED)})), FAIL),
            ("a null with no bound attached", lambda: checked(null(upper_bound=None)), FAIL),
            ("a null with a bound smaller than the founders warrant", lambda: checked(null(upper_bound=0.001)), FAIL),
            ("a null at a budget too small for the positive control", lambda: checked(null(budget=5)), UNQUALIFIED),
            ("a null at a budget where the control is reached 81 times in 100", lambda: checked(null(budget=24)),
             UNQUALIFIED),
            ("a policy that is not registered", lambda: checked(recount(
                report(), STRICT_AGAIN={"seeds": list(REPORTED), "hits": 0})), BLOCKED),
            ("a landscape that is not registered", lambda: checked(dict(report(), landscape="NEEDEL")), BLOCKED),
            ("a claim that is not one of the three", lambda: checked(dict(report(), claim="SUBSTRATE_INCAPABLE")),
             BLOCKED),
            ("a start law that is not one of the two", lambda: checked(dict(report(), start_law="WARM")), BLOCKED),
            ("a report with no budget", lambda: checked(dict(report(), budget=None)), BLOCKED),
            ("the registered founders repeat", lambda: checked(report(), [REPORTED[0]] * len(REPORTED)), BLOCKED),
            ("the registered founders are not on hand", lambda: search.check_report(report(), None), BLOCKED)]),
        "G8.demand": ("every baseline on the list is shown to sit at the bound", [
            lambda: torture.demand_closure(DEMAND, TRAIN)], [
            ("the cue follows a counter the organism can read",
             lambda: torture.demand_closure(DEMAND, TRAIN, leak_clock="parity"), FAIL),
            ("the cue follows the second bit of that counter",
             lambda: torture.demand_closure(DEMAND, TRAIN, leak_clock="bit1"), FAIL),
            ("the probe carries the answer", lambda: torture.demand_closure(DEMAND, TRAIN, leak_key="plain"), FAIL),
            ("the probe carries the complement of the answer",
             lambda: torture.demand_closure(DEMAND, TRAIN, leak_key="inverted"), FAIL),
            ("the probe carries the answer in two episodes of five",
             lambda: torture.demand_closure(DEMAND, TRAIN, leak_key="partial"), FAIL),
            ("the cue is the xor of the last two distractors",
             lambda: torture.demand_closure(DEMAND, TRAIN, cue_from_distractors="last2"), FAIL),
            ("the same, with a gap of 20",
             lambda: torture.demand_closure(DEMAND, TRAIN, gap=20, cue_from_distractors="last2"), FAIL),
            ("the cue is the parity of all six distractors",
             lambda: torture.demand_closure(DEMAND, TRAIN, cue_from_distractors="all"), FAIL),
            ("the same, with a gap of 20: the table that could see it cannot be fitted",
             lambda: torture.demand_closure(DEMAND, TRAIN, gap=20, cue_from_distractors="all"), INDETERMINATE),
            ("the environment keeps what the organism writes",
             lambda: torture.demand_closure(DEMAND, TRAIN, writable_mark=True), FAIL),
            ("a required baseline was not run (each of the five, in turn)",
             lambda: every_missing_baseline_blocks(), BLOCKED),
            ("closure claimed from 64 episodes", lambda: torture.demand_closure(SEEDS, TRAIN), INDETERMINATE),
            ("the tables scored on the seeds they were fitted on", lambda: torture.demand_closure(DEMAND, DEMAND),
             BLOCKED)]),
        "G9.arms": ("arms registered as separate controls give separate series", [
            lambda: audits.audit_arms(toy_cells()["GOOD"]["replicates"], ("naive_B", "dev_B", "sham_B", "lesion_B")),
            lambda: audits.audit_arms(r2["BUILDER"]["replicates"], ARMS2)], [
            ("run 3, STRATEGIST: eight arms", lambda: audits.audit_arms(r3["STRATEGIST"]["replicates"], ARMS3), FAIL),
            ("the same arms nudged apart in one replicate of 24",
             lambda: audits.audit_arms(nudged(r3["STRATEGIST"]["replicates"]), ARMS3), FAIL),
            ("the same arms nudged apart in two replicates of 24",
             lambda: audits.audit_arms(nudged(r3["STRATEGIST"]["replicates"], 2), ARMS3), FAIL)]),
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
            lambda: audits.audit_setting(SETTING_OK),
            lambda: audits.audit_setting(dict(SETTING_OK, power=1, amortization_horizon=3.0))], [
            ("run 2 as it was registered", lambda: audits.audit_setting(audits.RUN2), BLOCKED),
            ("run 3 as it was registered", lambda: audits.audit_setting(audits.RUN3), BLOCKED),
            ("power registered as 0.2", lambda: audits.audit_setting(dict(SETTING_OK, power=0.2)), BLOCKED),
            ("power registered as a sentence",
             lambda: audits.audit_setting(dict(SETTING_OK, power="high enough")), BLOCKED),
            ("a horizon of no later family", lambda: audits.audit_setting(dict(SETTING_OK, amortization_horizon=0)),
             BLOCKED),
            ("a horizon registered as a sentence",
             lambda: audits.audit_setting(dict(SETTING_OK, amortization_horizon="a few families")), BLOCKED),
            ("an effect threshold of zero", lambda: audits.audit_setting(dict(SETTING_OK, effect_threshold=0)), BLOCKED),
            ("an effect threshold registered as a word",
             lambda: audits.audit_setting(dict(SETTING_OK, effect_threshold="large")), BLOCKED),
            ("a choice registered as n/a", lambda: audits.audit_setting(dict(SETTING_OK, sham="n/a")), BLOCKED),
            ("a choice registered as unknown", lambda: audits.audit_setting(dict(SETTING_OK, cost="unknown")), BLOCKED),
            ("every field registered as tbd", lambda: audits.audit_setting({k: "tbd" for k in audits.SETTING}),
             BLOCKED)]),
        "G10.contrast": ("a contrast named after one variable changes that variable only", [
            lambda: audits.audit_contrast("parts_shared", audits.RUN3, dict(audits.RUN3, parts_shared=True))], [
            ("run 2 against run 3, named after shared parts",
             lambda: audits.audit_contrast("parts_shared", audits.RUN2, audits.RUN3), FAIL),
            ("one further difference besides the named one", lambda: audits.audit_contrast(
                "parts_shared", audits.RUN3, dict(audits.RUN3, parts_shared=True, effect_threshold=4)), FAIL),
            ("two cells that do not differ in the named variable",
             lambda: audits.audit_contrast("parts_shared", audits.RUN3, audits.RUN3), FAIL)]),
        "G10.ruler": ("a ruler is used for a claim only after it has answered the kit correctly", [
            lambda: audits.ruler_status("BITS", "BITS@KEYS", COUNTERFEIT)], [
            ("the strong claim, run 1: the v0.1 criterion said yes to a selector and to a fixed builder",
             lambda: audits.ruler_status("STRONG", "V01@RUN1", COUNTERFEIT), FAIL),
            ("the strong claim, run 2: the strict steps said yes to a fixed builder",
             lambda: audits.ruler_status("STRONG", "S19@RUN2", COUNTERFEIT), FAIL),
            ("the strong claim, run 3: the steps said yes to a selector over search orders",
             lambda: audits.ruler_status("STRONG", "S19@RUN3", COUNTERFEIT), FAIL),
            ("bits across two nested boundaries: nothing registered has been built",
             lambda: audits.ruler_status("BITS_TWO_BOUNDARIES", "BITS@TWO", COUNTERFEIT), UNQUALIFIED),
            ("combination on an unseen pair: nothing registered has been built",
             lambda: audits.ruler_status("COMBINATION", "BITS@PAIRS", COUNTERFEIT), UNQUALIFIED),
            ("a registered answer that the receipt contradicts", lambda: audits.ruler_status(
                "BITS", "BITS@KEYS", COUNTERFEIT, [(m, s, src, {"BITS": "NEGATIVE"}) if m == "KEY_ACQUIRER_16" else
                                                   (m, s, src, a) for m, s, src, a in audits.RUNS]), FAIL),
            ("a receipt replaced by an unrelated file that exists", lambda: audits.ruler_status(
                "BITS", "BITS@KEYS", COUNTERFEIT, [(m, s, ("README.md",) + src[1:], a) for m, s, src, a in audits.RUNS]),
             BLOCKED),
            ("a kit with positives and no negative", lambda: audits.ruler_status(
                "BITS", "BITS@KEYS", COUNTERFEIT, [r for r in bits if r[3]["BITS"] == "POSITIVE"]), UNQUALIFIED),
            ("a kit with negatives and no positive", lambda: audits.ruler_status(
                "BITS", "BITS@KEYS", COUNTERFEIT, [r for r in bits if r[3]["BITS"] == "NEGATIVE"]), UNQUALIFIED),
            ("a kit answered correctly, with one registered member never built", lambda: audits.ruler_status(
                "BITS", "BITS@KEYS", COUNTERFEIT, bits, {"KEY_HIDER": {"BITS": "NEGATIVE"}}), UNQUALIFIED),
            ("a kit answered correctly, with one member run only at another setting", lambda: audits.ruler_status(
                "BITS", "BITS@KEYS", COUNTERFEIT, bits + [("KEY_HIDER", "BITS@ELSEWHERE", bits[0][2],
                                                           {"BITS": "NEGATIVE"})], {}), UNQUALIFIED)]),
        "G11.custody": ("confirmation data is not discovery data, and the rule was fixed first", [
            lambda: claims.check_custody(custody()),
            lambda: claims.check_custody(custody(claim="NEW_SEEDS", confirmation=side(generator_sha256="1" * 64)))], [
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
            ("a discovery with no seeds", lambda: claims.check_custody(custody(
                discovery={"seeds": [], "panel_sha256": "d" * 64, "generator_sha256": "1" * 64})), BLOCKED),
            ("a negative count of tuning evaluations", lambda: claims.check_custody(custody(tuning_evaluations=-5)),
             BLOCKED),
            ("a count given as true", lambda: claims.check_custody(custody(tuning_evaluations=True)), BLOCKED),
            ("a claim that is not one of the two registered", lambda: claims.check_custody(custody(claim="BETTER")),
             BLOCKED),
            ("selection data described in other words", lambda: claims.check_custody(custody(selection_data="holdout")),
             BLOCKED)]),
        "G12.promote": ("a claim stands only on facets that passed, each with a source", [
            lambda: claims.promote(claim(), 1), lambda: claims.promote(claim(), 2),
            lambda: claims.promote(claim(level=4), 4)] + [
            (lambda k=k: claims.promote(claim(k), 1)) for k in sorted(KIND_FACETS) if k != "EFFECT"], [
            ("a facet of the first level is absent (each of the seven, in turn)", lambda: every_facet_blocks(1), BLOCKED),
            ("a facet of the second level is absent (each of the four, in turn)", lambda: every_facet_blocks(2), BLOCKED),
            ("the third level asked with nothing reproduced", lambda: every_facet_blocks(3), BLOCKED),
            ("the fourth level asked with nothing predicted", lambda: every_facet_blocks(4), BLOCKED),
            ("a facet of its kind is absent (each kind and facet, in turn)", lambda: every_kind_facet_blocks(), BLOCKED),
            ("the demand facet failed", lambda: claims.promote(claim(demand=FAIL), 1), FAIL),
            ("the ruler is unqualified in this physics", lambda: claims.promote(claim(detection=UNQUALIFIED), 1),
             UNQUALIFIED),
            ("the evidence was indeterminate", lambda: claims.promote(claim(independence=INDETERMINATE), 1),
             INDETERMINATE),
            ("no exact bound, and the second level is asked",
             lambda: claims.promote(claim("TRANSFER", exact_null=UNQUALIFIED), 2), UNQUALIFIED),
            ("a nested claim resting on a retention certificate alone", lambda: claims.promote(claim(
                "NESTED", drop=["mediation", "cargo_control", "flattened_twin"]), 1), BLOCKED),
            ("one facet absent and another failed", lambda: claims.promote(claim(drop="detection", demand=FAIL), 1),
             FAIL),
            ("a facet typed PASS with no source", lambda: claims.promote(claim(demand={"verdict": PASS}), 1), BLOCKED),
            ("a facet whose source is a blank",
             lambda: claims.promote(claim(demand={"verdict": PASS, "source": " "}), 1), BLOCKED),
            ("a facet with a verdict that is not one of the five",
             lambda: claims.promote(claim(demand={"verdict": "passed", "source": "x"}), 1), BLOCKED),
            ("a kind of claim that is not registered", lambda: claims.promote(dict(claim(), kind="STRUCTURE"), 1),
             BLOCKED),
            ("the second level asked with a failed second implementation",
             lambda: claims.promote(claim(second_implementation=FAIL), 2), FAIL)]),
        "G12.render": ("a claim is quoted with its cell, its excluded class and its registered setting or not at all", [
            lambda: claims.render(claim())], [
            ("a claim stripped of its setting", lambda: claims.render(dict(claim(), setting={})), BLOCKED),
            ("a claim with no cell", lambda: claims.render(dict(claim(), cell="")), BLOCKED),
            ("a claim that does not name the class it excludes",
             lambda: claims.render(dict(claim(), excluded_class="")), BLOCKED),
            ("a claim with no hash of its registered setting", lambda: claims.render(dict(claim(), setting_sha256="")),
             BLOCKED),
            ("a kind of claim that is not registered", lambda: claims.render(dict(claim(), kind="STRUCTURE")), BLOCKED),
            ("a setting that is not the one registered",
             lambda: claims.render(dict(claim(), setting={"note": "see the paper"})), FAIL)]),
    }


WRONG_BOUND = 0.48          # a wrong bound, registered together with thresholds computed from it


def known_escapes():
    """Faults this harness is known NOT to catch. Each is run; the test suite pins every one.

    They are listed so that nobody reads a passing harness as covering them. `shown` is evidence that
    the fault is real where the harness can produce it. Every gate has at least one, and the list is
    not complete.
    """
    R = retain1
    r3 = run3()
    row = dict(audits.clause_table(r3, audits.clauses_run3)["NESTING.sham_harmless"], ANOTHER_OPERATION_CALLED_SHAM=0)
    words = {p: (relabel(R.Register, p), relabel(R.RegisterImpostor, p)) for p in ("REGISTER", "ATTRACTOR", "PACKET")}
    chem = {"CHEMISTRY": (relabel(R.Register, "CHEMISTRY"), relabel(R.RegisterImpostor, "CHEMISTRY"))}
    other = {"note": "see the paper"}
    builder_called_positive = [(m, s, src, {"STRONG": "POSITIVE"} if m == "LIBRARY_FIXED_BUILDER" else a)
                               for m, s, src, a in audits.RUNS if s == "S19@RUN2"]
    return [
        {"gate": "G1.cell", "fault": "design counts that were typed and never run",
         "verdict": registration.check_cell(cell(known_answers={"HOLDS": runs(480, 480),
                                                                "FAILS": runs(0, 480)})).verdict,
         "why": "the gate computes each answer's probability from design counts. It cannot see whether the design "
                "runs were made."},
        {"gate": "G1.receipt", "fault": "a receipt whose reported outcome was changed after the run",
         "verdict": registration.check_receipt(cell(), run_receipt(outcome="FAILS"), SOURCE).verdict,
         "why": "the gate checks that a receipt belongs to its registration. It does not read what the receipt says "
                "the run found."},
        {"gate": "G2.preflight", "fault": "a positive declared perfect in 256 design runs that were never made",
         "verdict": stats.preflight_from_design(64, 0.5, 1e-6, 256, 256).verdict,
         "why": "the same: the counts are a declaration."},
        {"gate": "G3.exclusion", "fault": "a bound of %.2f where the class reaches 0.5, registered together with "
                                          "thresholds computed from it" % WRONG_BOUND,
         "verdict": exclusion(rulers.make_exclusion_ruler(WRONG_BOUND), edges=edges_for(WRONG_BOUND)).verdict,
         "shown": dict(bracket(), thresholds_at_the_wrong_bound={str(k): v for k, v in
                                                                 sorted(edges_for(WRONG_BOUND).items())}),
         "why": "the registered thresholds hold the ruler's arithmetic to the registered bound, within 0.001. The "
                "organisms hold the registered bound itself only loosely. That the bound is the true one has to be "
                "derived, and derived again by a second author."},
        {"gate": "G4.entry", "fault": "stored-word machines relabelled as another physics",
         "verdict": entry("CHEMISTRY", chem).verdict,
         "why": "the gate reads the physics an organism declares. It cannot read what the organism is."},
        {"gate": "G4.entry", "fault": "an impostor that carries the cue in one episode of five",
         "verdict": entry("REGISTER", dict(R.PANEL, REGISTER=(R.Register, R.weak_carrier()))).verdict,
         "shown": {"it_scores": R.score(R.weak_carrier(), SEEDS), "of": len(SEEDS)},
         "why": "a carrier too weak to exclude the class is called a negative. The ruler has a weakest positive it "
                "is registered to detect, and says nothing below it."},
        {"gate": "G5.neutrality", "fault": "the register-swap ruler declared shared on three relabelled stored-word "
                                           "machines",
         "verdict": neutral("REGISTER_SWAP", "SHARED", words).verdict,
         "why": "the gate counts physics by name. Whether three physics are unlike is a judgment, registered in "
                "advance and attacked by a second author's isomer."},
        {"gate": "G6.observer", "fault": "an observer that disturbs the world only on seeds outside those checked",
         "verdict": all_positives(lambda m: torture.observer_equivalence(m, PAIRS, torture.rare_observer(PAIRS))).verdict,
         "why": "equivalence is shown on the seeds checked and on no others. A run has to be checked on its own seeds."},
        {"gate": "G6.observer", "fault": "an observer that writes a field of the organism its reported state omits",
         "verdict": all_positives(lambda m: torture.observer_equivalence(m, PAIRS, torture.hidden_observer)).verdict,
         "why": "the gate compares what a runtime reports as its state."},
        {"gate": "G6.reset", "fault": "a carry that native() hides and that is used two episodes later",
         "verdict": torture.reset_closure(R.SleeperRegister, PAIRS).verdict,
         "why": "the gate looks one episode ahead and at the state a runtime reports. State hidden from both passes."},
        {"gate": "G6.reset", "fault": "a reset that leaks on every third call",
         "verdict": torture.reset_closure(R.EveryThirdReset, PAIRS).verdict,
         "why": "the gate calls reset twice on each runtime."},
        {"gate": "G6.restart", "fault": "a count of episodes that capture omits and native() hides, used from the "
                                        "second episode on",
         "verdict": torture.restart_equivalence(R.HiddenCounter, PAIRS).verdict,
         "why": "the gate restarts within one episode."},
        {"gate": "G7.calibration", "fault": "an estimator that ran 95% of the registered budget",
         "verdict": search.calibration_panel(BUDGET, FOUNDERS, short_budget(0.95)).verdict,
         "shown": {"exact_at_budget": search.exact_reach("NEEDLE", "NEUTRAL", BUDGET, "COLD"),
                   "exact_at_95_percent": search.exact_reach("NEEDLE", "NEUTRAL", int(BUDGET * 0.95), "COLD")},
         "why": "256 founders resolve an error in reach of a few standard errors and nothing smaller."},
        {"gate": "G7.report", "fault": "a null whose prose says the substrate cannot do it, with the scope field right",
         "verdict": checked(dict(null(), label="the substrate cannot do it")).verdict,
         "why": "prose is not read. And outside these toy landscapes there is no exact reach to hold a null against, "
                "so founders registered because the search missed from them would pass."},
        {"gate": "G8.demand", "fault": "the cue follows the fourth bit of a counter the organism can read",
         "verdict": torture.demand_closure(DEMAND, TRAIN, leak_clock="bit3").verdict,
         "shown": {"a_policy_that_reads_that_bit_scores": R.score(R.ClockBit3Reader, SEEDS, leak_clock="bit3"),
                   "of": len(SEEDS)},
         "why": "the gate runs a list of baselines and small fitted tables, not the class. Nothing on the list "
                "reads that bit."},
        {"gate": "G9.arms", "fault": "run 3's arms nudged apart in three replicates of 24",
         "verdict": audits.audit_arms(nudged(r3["STRATEGIST"]["replicates"], 3), ARMS3).verdict,
         "why": "arms are one series if equal in 22 of 24 replicates. Three nudged replicates leave 21."},
        {"gate": "G9.clauses", "fault": "cells that were typed, not run, so that every clause fails by itself",
         "verdict": audits.audit_clauses(toy_cells(**ISOLATING), toy_clauses).verdict,
         "why": "an audit of numbers cannot see where the numbers came from."},
        {"gate": "G9.sham", "fault": "run 3's idle sham, with a cell added in which another, harmful operation is "
                                     "called the sham",
         "verdict": audits.audit_sham(r3["STRATEGIST"]["replicates"], row).verdict,
         "why": "an audit of numbers cannot see what an operation was. The fire test of a sham must use that sham."},
        {"gate": "G10.setting", "fault": "a power of 0.99 typed onto run 3, with nothing computed",
         "verdict": audits.audit_setting(dict(audits.RUN3, power=0.99, amortization_horizon=3)).verdict,
         "why": "presence and type are checked, not meaning and not provenance."},
        {"gate": "G10.contrast", "fault": "two runs that differ in a choice nobody wrote down",
         "verdict": audits.audit_contrast("parts_shared", {"parts_shared": True}, {"parts_shared": False}).verdict,
         "why": "the gate compares the fields that were written down."},
        {"gate": "G10.ruler", "fault": "a registry that calls the fixed builder a positive for the strong claim",
         "verdict": audits.ruler_status("STRONG", "S19@RUN2", COUNTERFEIT, builder_called_positive, {}).verdict,
         "why": "the registered answers are a declaration. Who registers them, and when, is outside the gate."},
        {"gate": "G11.custody", "fault": "an edited copy of the discovery generator presented as a new family",
         "verdict": claims.check_custody(custody(confirmation=side(generator_sha256="3" * 64))).verdict,
         "why": "generators are compared by the hash of their code, and custodians by name. Whether two generators "
                "are one family, or two names one person, is a judgment."},
        {"gate": "G12.promote", "fault": "a facet typed PASS whose named source was never run",
         "verdict": claims.promote(claim(demand={"verdict": PASS, "source": "RECEIPT_that_does_not_exist.json"}),
                                   1).verdict,
         "why": "the gate requires a source and does not open it. A claim about structure entered as an effect "
                "passes the same way."},
        {"gate": "G12.render", "fault": "a claim whose setting and its hash were replaced together",
         "verdict": claims.render(dict(claim(), setting=other, setting_sha256=claims.setting_hash(other))).verdict,
         "why": "the hash is carried by the claim. It should come from the registration."},
    ]


def qualify(registry=None):
    """Run every gate on its sound cases and mutants. One row per gate."""
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
