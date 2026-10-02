"""G9 and G10. Audits of a finished run from its receipt, and the registry of the nested-improvement kit.

These gates read numbers that a run already wrote. They exist because three rounds of review of this
reviewer's own runs found the same faults by hand: arms that were one computation, clauses that no
fixture could make false, a sham that could not fail, a contrast that changed two things, and
settings that were never registered. Each is now a function that returns a verdict.
"""
from .verdict import BLOCKED, FAIL, PASS, UNQUALIFIED, Result

N, HOLDS_AT, FAILS_AT = 24, 22, 12
GOOD_MAX, BAD_MIN = 3.5, 6.0


# ---------------------------------------------------------------- arms

def coincident(reps, arms):
    """Groups of arms whose values are equal in every replicate."""
    groups = []
    for arm in arms:
        for group in groups:
            if all(o[arm] == o[group[0]] for o in reps):
                group.append(arm)
                break
        else:
            groups.append([arm])
    return groups


def audit_arms(reps, arms):
    """Arms registered as separate controls must be separate computations."""
    groups = coincident(reps, arms)
    merged = [g for g in groups if len(g) > 1]
    if merged:
        return Result("G9.arms", FAIL, "%d arms are %d computations: %s"
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
    """Every clause needs a cell in which it fails and a cell in which it holds."""
    table = clause_table(cells, clauses)
    cannot_fail = sorted(c for c, row in table.items() if min(row.values()) > FAILS_AT)
    cannot_hold = sorted(c for c, row in table.items() if max(row.values()) < HOLDS_AT)
    detail = {"cannot_fail": cannot_fail, "cannot_hold": cannot_hold, "table": table}
    if cannot_fail or cannot_hold:
        return Result("G9.clauses", UNQUALIFIED,
                      "%d of %d clauses have no fixture that makes them false%s" % (
                          len(cannot_fail), len(table),
                          ("; %d have none that makes them true" % len(cannot_hold)) if cannot_hold else ""), detail)
    return Result("G9.clauses", PASS, "", detail)


# ---------------------------------------------------------------- sham

def audit_sham(reps, clause_row, margin=0.25):
    """A sham must be able to fail, and must leave the organism where it was.

    clause_row is the sham clause's row of the clause table. Equivalence, not absence of a difference:
    the sham arm must lie within `margin` of the intact arm in at least HOLDS_AT replicates.
    """
    if min(clause_row.values()) > FAILS_AT:
        return Result("G9.sham", UNQUALIFIED, "no fixture makes the sham clause false: it cannot fail")
    near = sum(1 for o in reps if abs(o["sham_B"] - o["dev_B"]) <= margin * o["dev_B"])
    faster = sum(1 for o in reps if o["sham_B"] < o["dev_B"])
    detail = {"within_margin": near, "sham_faster": faster, "n": len(reps)}
    if near >= HOLDS_AT:
        return Result("G9.sham", PASS, "", detail)
    return Result("G9.sham", FAIL, "the sham is within %d%% of intact in %d of %d replicates (faster in %d): it controls "
                  "for size, not for neutrality" % (round(100 * margin), near, len(reps), faster), detail)


# ---------------------------------------------------------------- settings and contrasts

SETTING = ("cost", "later_families", "content_reset", "sham", "family_A", "wrong_history", "effect_threshold",
           "power", "amortization_horizon")


def audit_setting(setting):
    """The nine choices section 19 leaves open must each be registered before the run."""
    missing = [k for k in SETTING if setting.get(k) in (None, "")]
    if missing:
        return Result("G10.setting", BLOCKED, "not registered: %s" % ", ".join(missing))
    return Result("G10.setting", PASS)


def audit_contrast(named, a, b):
    """A contrast named after one variable may differ in that variable only."""
    differ = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    if differ == [named]:
        return Result("G10.contrast", PASS)
    if named not in differ:
        return Result("G10.contrast", FAIL, "the two cells do not differ in %s" % named, differ)
    return Result("G10.contrast", FAIL, "named after %s, and also changes: %s"
                  % (named, ", ".join(d for d in differ if d != named)), differ)


# The settings of this reviewer's runs 2 and 3, written down after the fact. None marks a choice
# that was never registered.
RUN2 = {"cost": "tasks to an accepted procedure, no cut-off; accepted after 8 passed tasks",
        "later_families": "B, D, E kinds never met; C a new seed of B's kind",
        "content_reset": "declared stores cleared at steps 2 and 5",
        "sham": "as many unused library entries as the lesion removes",
        "family_A": "four part families",
        "wrong_history": "four parts that do not compose B",
        "effect_threshold": 4, "parts_shared": True, "power": None, "amortization_horizon": None}
RUN3 = {"cost": "tasks to an accepted procedure, no cut-off; accepted after 8 passed tasks",
        "later_families": "B, D, E kinds never met; C a new seed of B's kind",
        "content_reset": "none called",
        "sham": "two idle inherited orders swapped",
        "family_A": "one composite family",
        "wrong_history": "one part family",
        "effect_threshold": 2, "parts_shared": False, "power": None, "amortization_horizon": None}


# ---------------------------------------------------------------- the kit

# Expected answer of each kit member for each claim. A member's answer is specific to the claim: a
# library learner is a legitimate positive for reuse of built parts and a negative for the strong
# claim. `built` says whether the member has run anywhere in this repository.
KIT = {
    "PROCEDURE_SELECTOR":     {"built": True,  "ORDER3_REUSE": "NEGATIVE", "STRONG_RECURSION": "NEGATIVE",
                               "receipt": "RECEIPT_gauntlet.json"},
    "LIBRARY_FIXED_BUILDER":  {"built": True,  "ORDER3_REUSE": "POSITIVE", "STRONG_RECURSION": "NEGATIVE",
                               "receipt": "RECEIPT_gauntlet2.json"},
    "SEARCH_ORDER_SELECTOR":  {"built": True,  "ORDER3_REUSE": "NEGATIVE", "STRONG_RECURSION": "NEGATIVE",
                               "receipt": "RECEIPT_gauntlet3.json"},
    "MATURATION_UNLOCK":      {"built": True,  "ORDER3_REUSE": "NEGATIVE", "STRONG_RECURSION": "NEGATIVE",
                               "receipt": "RECEIPT_gauntlet2.json"},
    "MEMORIZER":              {"built": True,  "ORDER3_REUSE": "NEGATIVE", "STRONG_RECURSION": "NEGATIVE",
                               "receipt": "RECEIPT_gauntlet2.json"},
    "WORLD_PARKING":          {"built": False, "ORDER3_REUSE": "NEGATIVE", "STRONG_RECURSION": "NEGATIVE"},
    "NESTED_COMPILER_CARGO":  {"built": False, "ORDER3_REUSE": "NEGATIVE", "STRONG_RECURSION": "NEGATIVE"},
    "HIERARCHICAL_SELECTOR":  {"built": False, "ORDER3_REUSE": "NEGATIVE", "STRONG_RECURSION": "NEGATIVE"},
    "FLATTENED_EQUIVALENT":   {"built": False, "ORDER3_REUSE": "POSITIVE", "STRONG_RECURSION": "NEGATIVE"},
    "KEY_ACQUIRER":           {"built": True,  "ORDER3_BITS": "POSITIVE", "receipt": "RECEIPT_keys.json"},
    "KEY_SELECTOR":           {"built": True,  "ORDER3_BITS": "NEGATIVE", "receipt": "RECEIPT_keys.json"},
    "KEY_SANDBAGGER":         {"built": True,  "ORDER3_BITS": "NEGATIVE", "receipt": "RECEIPT_keys.json"},
    "KEY_ACQUIRER_DEPTH4":    {"built": False, "ORDER4_BITS": "POSITIVE"},
    "KEY_ACQUIRER_DEPTH3":    {"built": False, "ORDER4_BITS": "NEGATIVE"},
}


def ruler_status(claim, kit=None, receipts=None):
    """G10. May a ruler for this claim be used? It needs a built positive, a built negative, and no gaps.

    receipts, if given, is the folder in which every built member's receipt must exist.
    """
    kit = KIT if kit is None else kit
    gate = "G10.ruler[%s]" % claim
    members = {m: v for m, v in kit.items() if claim in v}
    if receipts is not None:
        lost = sorted(m for m, v in members.items() if v["built"] and not (receipts / v.get("receipt", "?")).is_file())
        if lost:
            return Result(gate, BLOCKED, "called built, and no receipt on disk: %s" % ", ".join(lost))
    positives = sorted(m for m, v in members.items() if v[claim] == "POSITIVE")
    negatives = sorted(m for m, v in members.items() if v[claim] == "NEGATIVE")
    if not positives:
        return Result(gate, UNQUALIFIED, "no known positive is registered: the ruler cannot be shown to say yes")
    if not negatives:
        return Result(gate, UNQUALIFIED, "no known negative is registered: the ruler cannot be shown to say no")
    unbuilt = sorted(m for m, v in members.items() if not v["built"])
    if unbuilt:
        return Result(gate, UNQUALIFIED, "registered and not built: %s" % ", ".join(unbuilt),
                      {"positives": positives, "negatives": negatives})
    return Result(gate, PASS, "", {"positives": positives, "negatives": negatives})
