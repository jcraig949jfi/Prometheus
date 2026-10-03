"""G9 and G10. Audits of a finished run from its receipt, and the registry of the nested-improvement kit.

These gates read numbers that a run already wrote. They exist because the review of this
reviewer's own runs found these faults by hand: arms that gave one series, clauses that no fixture
could make false, a sham that could not fail, a contrast that changed several things, and settings
that were never registered.

Two limits. The settings of runs 2 and 3 below were written down by the reviewer after the fact;
only the effect threshold is read from a receipt. And an audit of numbers cannot see what an
operation was: a cell in which some other, harmful operation is called the sham makes a sham look
able to fail. meta.known_escapes pins that case.
"""
import json

from .verdict import BLOCKED, FAIL, INDETERMINATE, PASS, UNQUALIFIED, Result, combine

N, HOLDS_AT, FAILS_AT = 24, 22, 12
GOOD_MAX, BAD_MIN = 3.5, 6.0


# ---------------------------------------------------------------- arms

def coincident(reps, arms, same_at=HOLDS_AT):
    """Groups of arms whose values are equal in at least `same_at` of the replicates."""
    groups = []
    for arm in arms:
        for group in groups:
            if sum(1 for o in reps if o[arm] == o[group[0]]) >= min(same_at, len(reps)):
                group.append(arm)
                break
        else:
            groups.append([arm])
    return groups


def audit_arms(reps, arms):
    """Arms registered as separate controls must give separate series.

    Two arms with one series give one piece of evidence, whether they are one computation or two
    that both hit a cap. The gate cannot tell which and does not need to.
    """
    groups = coincident(reps, arms)
    merged = [g for g in groups if len(g) > 1]
    if merged:
        return Result("G9.arms", FAIL, "%d arms give %d distinct series: %s"
                      % (len(arms), len(groups), "; ".join(" = ".join(g) for g in merged)), groups)
    return Result("G9.arms", PASS, "", groups)


# ---------------------------------------------------------------- clauses

def clauses_run2(o, factor=4):
    """The six conjuncts of gauntlet2.py as their thirteen clauses."""
    slack = 2 * o["dev_B"] + 4
    return {
        "SAVINGS": factor * o["dev_B"] <= o["naive_B"],
        "LIFECYCLE": o["lifecycle_developed"] < o["lifecycle_naive"],
        "U_TRANSFER.frozen_U_good_on_C": o["q_C_same_kind"] <= GOOD_MAX,
        "U_TRANSFER.frozen_U_good_on_narrower_C": o["q_C_narrower"] <= GOOD_MAX,
        "U_TRANSFER.lesioned_line_bad_on_C": o["q_C_lesioned_line"] >= BAD_MIN,
        "NESTING.lesion_hurts": 2 * o["lesion_B"] >= o["naive_B"],
        "NESTING.sham_harmless": o["sham_B"] <= slack,
        "NESTING.rescue_restores": o["rescue_B"] <= slack,
        "NESTING.donor_V_helps": factor * o["v_donor_B"] <= o["naive_B"],
        "PROVENANCE.wrong_history_no_help": 2 * o["wrong_history_B"] >= o["naive_B"],
        "PROVENANCE.random_store_no_help": 2 * o["random_library_B"] >= o["naive_B"],
        "REPEAT.D": factor * o["dev_D"] <= o["naive_D"],
        "REPEAT.E": factor * o["dev_E"] <= o["naive_E"],
    }


def clauses_run3(o, factor=2):
    """The same thirteen clauses with gauntlet3.py's arm names."""
    renamed = dict(o, wrong_history_B=o["irrelevant_history_B"], random_library_B=o["random_V_B"])
    return clauses_run2(renamed, factor)


def clause_table(cells, clauses):
    """For every clause, in how many replicates of every cell it is true."""
    names = list(clauses(next(iter(cells.values()))["replicates"][0]))
    return {c: {cell: sum(1 for o in v["replicates"] if clauses(o)[c]) for cell, v in cells.items()} for c in names}


def audit_clauses(cells, clauses):
    """Every clause needs a cell in which it holds and a cell in which it fails while the others hold.

    UNQUALIFIED: some clause fails in no cell, or holds in none. INDETERMINATE: every clause fails
    somewhere, and some fail only where other clauses fail too, so their own work is not shown.
    """
    table = clause_table(cells, clauses)
    names = list(table)
    cannot_fail = sorted(c for c in names if min(table[c].values()) > FAILS_AT)
    cannot_hold = sorted(c for c in names if max(table[c].values()) < HOLDS_AT)
    cell_names = list(next(iter(table.values())))
    not_isolated = sorted(c for c in names if c not in cannot_fail and not any(
        table[c][cell] <= FAILS_AT and all(table[d][cell] >= HOLDS_AT for d in names if d != c) for cell in cell_names))
    detail = {"cannot_fail": cannot_fail, "cannot_hold": cannot_hold, "not_isolated": not_isolated, "table": table}
    if cannot_fail or cannot_hold:
        return Result("G9.clauses", UNQUALIFIED,
                      "%d of %d clauses have no fixture that makes them false%s" % (
                          len(cannot_fail), len(table),
                          ("; %d have none that makes them true" % len(cannot_hold)) if cannot_hold else ""), detail)
    if not_isolated:
        return Result("G9.clauses", INDETERMINATE, "%d of %d clauses fail only where another clause fails too"
                      % (len(not_isolated), len(table)), detail)
    return Result("G9.clauses", PASS, "", detail)


# ---------------------------------------------------------------- sham

def audit_sham(reps, clause_row, margin=0.25, slack=1):
    """A sham must be able to fail, and must leave the organism where it was.

    clause_row is the sham clause's row of the clause table. Equivalence, not absence of a difference:
    the sham arm must lie within `margin` of the intact arm (or within `slack` tasks, if that is
    more) in at least HOLDS_AT replicates.
    """
    if min(clause_row.values()) > FAILS_AT:
        return Result("G9.sham", UNQUALIFIED, "no fixture makes the sham clause false: it cannot fail")
    near = sum(1 for o in reps if abs(o["sham_B"] - o["dev_B"]) <= max(margin * o["dev_B"], slack))
    faster = sum(1 for o in reps if o["sham_B"] < o["dev_B"])
    detail = {"within_margin": near, "sham_faster": faster, "n": len(reps)}
    if near >= HOLDS_AT:
        return Result("G9.sham", PASS, "", detail)
    return Result("G9.sham", FAIL, "the sham is within %d%% of intact in %d of %d replicates (faster in %d): it is "
                  "not neutral" % (round(100 * margin), near, len(reps), faster), detail)


# ---------------------------------------------------------------- settings and contrasts

SETTING = ("cost", "later_families", "content_reset", "sham", "family_A", "wrong_history", "effect_threshold",
           "power", "amortization_horizon")
PLACEHOLDERS = ("", "tbd", "todo", "n/a", "na", "none", "unknown", "not computed", "?")


def _number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def audit_setting(setting):
    """The nine choices section 19 leaves open must each be registered before the run.

    Presence and type are checked, not meaning: a sentence that says nothing passes, and so does a
    power that was typed and never computed. Power is a number of at least 0.99; the horizon is a
    count of later families; the threshold is a positive number.
    """
    bad = []
    for k in SETTING:
        v = setting.get(k)
        if v is None or (isinstance(v, str) and v.strip().lower() in PLACEHOLDERS):
            bad.append("%s not registered" % k)
        elif k == "power" and not (_number(v) and 0.99 <= v <= 1.0):
            bad.append("power must be a probability of at least 0.99")
        elif k == "amortization_horizon" and not (_number(v) and v == int(v) and v >= 1):
            bad.append("amortization_horizon must be a count of later families")
        elif k == "effect_threshold" and not (_number(v) and v > 0):
            bad.append("effect_threshold must be a positive number")
    if bad:
        return Result("G10.setting", BLOCKED, "; ".join(bad))
    return Result("G10.setting", PASS)


def audit_contrast(named, a, b):
    """A contrast named after one variable may differ in that variable only.

    It compares the fields that were written down. A difference in something nobody wrote down is
    not seen, and the same choice worded two ways counts as a difference.
    """
    differ = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    if differ == [named]:
        return Result("G10.contrast", PASS, "", differ)
    if named not in differ:
        return Result("G10.contrast", FAIL, "the two cells do not differ in %s" % named, differ)
    return Result("G10.contrast", FAIL, "named after %s; of %d fields written down %d differ, also: %s"
                  % (named, len(set(a) | set(b)), len(differ), ", ".join(d for d in differ if d != named)), differ)


# The settings of this reviewer's runs 2 and 3, written down after the fact from PREREG_gauntlet2.md
# and PREREG_gauntlet3.md. None marks a choice those files do not make: neither states a power or
# an amortization horizon (check_hardening.py checks that against the files).
RUN2 = {"cost": "TASKS_TO_ACCEPTED_PROCEDURE_NO_CUTOFF",
        "later_families": "B_D_E_NEW_KINDS__C_NEW_SEED_OF_B",
        "content_reset": "DECLARED_STORES_CLEARED_AT_STEPS_2_AND_5",
        "sham": "REMOVE_AS_MANY_UNUSED_LIBRARY_ENTRIES",
        "family_A": "FOUR_PART_FAMILIES",
        "wrong_history": "FOUR_PARTS_THAT_DO_NOT_COMPOSE_B",
        "effect_threshold": 4, "parts_shared": True, "power": None, "amortization_horizon": None}
RUN3 = {"cost": "TASKS_TO_ACCEPTED_PROCEDURE_NO_CUTOFF",
        "later_families": "B_D_E_NEW_KINDS__C_NEW_SEED_OF_B",
        "content_reset": "NONE_CALLED",
        "sham": "SWAP_TWO_IDLE_INHERITED_ORDERS",
        "family_A": "ONE_COMPOSITE_FAMILY",
        "wrong_history": "ONE_PART_FAMILY",
        "effect_threshold": 2, "parts_shared": False, "power": None, "amortization_horizon": None}


# ---------------------------------------------------------------- the kit

# Every cell of the four receipts of the review, with the ruler it was run under and the registered
# answer for the claim that ruler was offered for. 26 rows: none is left out.
#
# STRONG is the claim v0.1 calls the recursive extension: that what was built improves the process
# that builds later learning machinery. Every organism in runs 1 to 3 has fixed inherited
# machinery, so every one is a registered NEGATIVE for it. That is the reviewer's judgment of what
# was built, made before these gates existed; it is a declaration, and meta.known_escapes pins what
# follows if it is declared otherwise.
#
# BITS is the claim of run 4: information acquired in this life was carried across the family
# boundary. The answer is read from the numbers (certified bits above zero) and from the two guards
# of that run (a world check and a history of other keys), not from the label CONSTRUCTED, which
# the review withdrew.
#
# No row carries an answer for reuse of built parts. The runs do not settle one: the fire-test
# cells of run 2 are builders the steps reject for other reasons, and the result of run 3 follows
# its curriculum. KIT_ANSWERS below records what a ruler for reuse would have to return.
G1, G2, G3, KEYS = "RECEIPT_gauntlet.json", "RECEIPT_gauntlet2.json", "RECEIPT_gauntlet3.json", "RECEIPT_keys.json"
NO, YES = {"STRONG": "NEGATIVE"}, {"BITS": "POSITIVE"}
RUNS = [
    # member                              setting      receipt, kind, key
    ("LIBRARY_FIXED_BUILDER",             "V01@RUN1", (G1, "v01", "BUILDER"), NO),
    ("PROCEDURE_SELECTOR",                "V01@RUN1", (G1, "v01", "GEARBOX"), NO),
    ("MATURATION_UNLOCK",                 "V01@RUN1", (G1, "v01", "MATURATION"), NO),
    ("NO_DEVELOPMENT",                    "V01@RUN1", (G1, "v01", "STATIC"), NO),
    ("LIBRARY_FIXED_BUILDER",             "S19@RUN2", (G2, "cell", "BUILDER"), NO),
    ("PROCEDURE_SELECTOR",                "S19@RUN2", (G2, "cell", "SELECTOR"), NO),
    ("NO_DEVELOPMENT",                    "S19@RUN2", (G2, "cell", "STATIC"), NO),
    ("BUILDER_COSTLY_DEVELOPMENT",        "S19@RUN2", (G2, "cell", "WASTEFUL"), NO),
    ("BUILDER_HIDDEN_COPY",               "S19@RUN2", (G2, "cell", "HIDDEN"), NO),
    ("BUILDER_UNDER_A_HARMFUL_SHAM",      "S19@RUN2", (G2, "cell", "BADSHAM"), NO),
    ("MATURATION_UNLOCK",                 "S19@RUN2", (G2, "cell", "MATURATION"), NO),
    ("MEMORIZER",                         "S19@RUN2", (G2, "cell", "MEMORISER"), NO),
    ("BUILDER_OFF_ITS_HISTORY",           "S19@RUN2", (G2, "cell", "OFFHISTORY"), NO),
    ("LIBRARY_FIXED_BUILDER",             "S19@RUN3", (G3, "cell", "BUILDER"), NO),
    ("SEARCH_ORDER_SELECTOR",             "S19@RUN3", (G3, "cell", "STRATEGIST"), NO),
    ("SEARCH_ORDER_SELECTOR_EAGER",       "S19@RUN3", (G3, "cell", "EAGER"), NO),
    ("NO_DEVELOPMENT",                    "S19@RUN3", (G3, "cell", "STATIC"), NO),
    ("KEY_ACQUIRER_4",                    "BITS@KEYS", (KEYS, "keys", "ACQUIRER(4)"), YES),
    ("KEY_ACQUIRER_8",                    "BITS@KEYS", (KEYS, "keys", "ACQUIRER(8)"), YES),
    ("KEY_ACQUIRER_12",                   "BITS@KEYS", (KEYS, "keys", "ACQUIRER(12)"), YES),
    ("KEY_ACQUIRER_16",                   "BITS@KEYS", (KEYS, "keys", "ACQUIRER(16)"), YES),
    ("KEY_ELIMINATOR",                    "BITS@KEYS", (KEYS, "keys", "ELIM"), {"BITS": "NEGATIVE"}),
    ("KEY_SELECTOR",                      "BITS@KEYS", (KEYS, "keys", "SELECTOR(64)"), {"BITS": "NEGATIVE"}),
    ("KEY_SELECTOR_ON_ITS_OWN_LIST",      "BITS@KEYS",
     (KEYS, "keys", "fire test A: SELECTOR(64), key drawn from its own list"), {"BITS": "NEGATIVE"}),
    ("KEY_HARDWIRED",                     "BITS@KEYS",
     (KEYS, "keys", "fire test B: HARDWIRED, harness reuses one key"), {"BITS": "NEGATIVE"}),
    ("KEY_SANDBAGGER",                    "BITS@KEYS",
     (KEYS, "keys", "fire test D: SANDBAGGER, harness reuses one key"), {"BITS": "NEGATIVE"}),
]
# Registered and never built under any registered ruler. The first four are the package's; the fifth
# is the genuine positive both the package and ASTRA's review ask for. The rest exist only as
# exploratory fixtures in ladder.py, with no registered verdict.
UNBUILT = {
    "WORLD_PARKING":            {"STRONG": "NEGATIVE"},
    "NESTED_COMPILER_CARGO":    {"STRONG": "NEGATIVE"},
    "HIERARCHICAL_SELECTOR":    {"STRONG": "NEGATIVE"},
    "FLATTENED_EQUIVALENT":     {"STRONG": "AS_ITS_SOURCE"},
    "GENUINE_LEARNED_UPDATER":  {"STRONG": "POSITIVE"},
    "KEY_CACHE_TWO_BOUNDARIES": {"BITS_TWO_BOUNDARIES": "POSITIVE"},
    "KEY_ELIMINATOR_TWO_BOUNDARIES": {"BITS_TWO_BOUNDARIES": "NEGATIVE"},
    "PAIR_COMPOSER":            {"COMBINATION": "POSITIVE"},
    "PAIR_SCHEMA_CACHE":        {"COMBINATION": "POSITIVE"},
    "PAIR_TABLE_CACHE":         {"COMBINATION": "NEGATIVE"},
    "PAIR_HIDER":               {"COMBINATION": "NEGATIVE"},
}
# What a ruler would have to return on each member of the package's kit, per claim. For reuse of
# built parts no ruler has been checked against this column.
KIT_ANSWERS = {
    "PROCEDURE_SELECTOR":      {"reuse": "NEGATIVE", "strong": "NEGATIVE"},
    "LIBRARY_FIXED_BUILDER":   {"reuse": "POSITIVE", "strong": "NEGATIVE"},
    "SEARCH_ORDER_SELECTOR":   {"reuse": "NEGATIVE", "strong": "NEGATIVE"},
    "MATURATION_UNLOCK":       {"reuse": "NEGATIVE", "strong": "NEGATIVE"},
    "MEMORIZER":               {"reuse": "NEGATIVE", "strong": "NEGATIVE"},
    "WORLD_PARKING":           {"reuse": "NEGATIVE", "strong": "NEGATIVE"},
    "NESTED_COMPILER_CARGO":   {"reuse": "NEGATIVE", "strong": "NEGATIVE"},
    "HIERARCHICAL_SELECTOR":   {"reuse": "NEGATIVE", "strong": "NEGATIVE"},
    "FLATTENED_EQUIVALENT":    {"reuse": "AS_ITS_SOURCE", "strong": "AS_ITS_SOURCE"},
    "GENUINE_LEARNED_UPDATER": {"reuse": None, "strong": "POSITIVE"},
}
SETTINGS = ("V01@RUN1", "S19@RUN2", "S19@RUN3", "BITS@KEYS")
GUARDS = ("INHERITED_OR_LEAK", "RULER_NOT_APPLICABLE")


def returned(receipts, source):
    """What the ruler returned on a kit member, read from the receipt. None if it cannot be read."""
    name, kind, key = source
    try:
        data = json.loads((receipts / name).read_text(encoding="ascii"))
        if kind == "v01":
            answers = set(data["result"]["v01_verdict"][key].values())
            return {("PASS",): "POSITIVE", ("FAIL",): "NEGATIVE"}.get(tuple(sorted(answers)), "MIXED")
        if kind == "cell":
            return {"PASS": "POSITIVE", "FAIL": "NEGATIVE"}[data["cells"][key]["verdict"]]
        if kind == "keys":
            bits, guard = data["cells"][key]["certified_bits_carried"], data["verdicts"][key] in GUARDS
            return "POSITIVE" if bits > 0 and not guard else "NEGATIVE"
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None
    return None


def ruler_status(claim, setting, receipts, runs=None, unbuilt=None):
    """G10. May the ruler used at this setting be used for this claim?

    It must have returned the registered answer on every kit member run at this setting, on at least
    one positive and one negative, and no member registered for the claim may be unbuilt or not yet
    run at this setting. A wrong answer is a FAIL of the ruler. Gaps leave it UNQUALIFIED.
    """
    runs, unbuilt = (RUNS if runs is None else runs), (UNBUILT if unbuilt is None else unbuilt)
    gate, found, seen = "G10.ruler[%s at %s]" % (claim, setting), [], {"POSITIVE": 0, "NEGATIVE": 0}
    here = [r for r in runs if r[1] == setting and claim in r[3]]
    for member, _, source, answers in here:
        got = returned(receipts, source)
        if got is None:
            found.append(Result(member, BLOCKED, "no readable verdict for %s in %s" % (source[2], source[0])))
        elif got != answers[claim]:
            found.append(Result(member, FAIL, "registered %s, the ruler returned %s" % (answers[claim], got)))
        else:
            seen[got] = seen.get(got, 0) + 1
    if not seen["POSITIVE"]:
        found.append(Result("positive", UNQUALIFIED, "no known positive has been answered correctly at this setting"))
    if not seen["NEGATIVE"]:
        found.append(Result("negative", UNQUALIFIED, "no known negative has been answered correctly at this setting"))
    never = sorted(m for m, answers in unbuilt.items() if claim in answers)
    if never:
        found.append(Result("unbuilt", UNQUALIFIED, "registered and not built: %s" % ", ".join(never)))
    elsewhere = sorted({r[0] for r in runs if claim in r[3] and r[1] != setting} - {r[0] for r in here})
    if elsewhere:
        found.append(Result("not run here", UNQUALIFIED, "built, and not run at this setting: %s" % ", ".join(elsewhere)))
    out = combine(gate, found or [Result("all", PASS)])
    return Result(gate, out.verdict, out.reason, {"answered": seen})
