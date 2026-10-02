"""G1. Registration: a run exists only as a registered cell, and a receipt must belong to its registration.

Nothing a cell declares about its own power is believed. The cell registers a verdict table and,
for each answer it expects from a known case, the per-unit rate of that case. The gate computes
the probability of the answer from the table.
"""
import hashlib

from . import stats
from .verdict import BLOCKED, FAIL, INDETERMINATE, PASS, Result, combine

# The first eight are the cell of the hardening design. The rest are what a gate needs in order to
# refuse. design_seeds is required too and may be an empty list: no design runs were made.
REQUIRED = ("physics", "search", "world", "development", "boundary", "resources", "measurement", "exposure",
            "adapter", "independent_unit", "registered_seeds", "verdict_table", "known_answers", "source_sha256",
            "registered_at")


def check_verdict_table(table):
    """Every count 0..n maps to exactly one registered outcome, and every registered outcome is reachable.

    table = {"n": 24, "rule": [(lo, hi, outcome), ...], "outcomes": ["HOLDS", "FAILS", "INDETERMINATE"]}
    """
    gate = "G1.verdict_table"
    n, rule, outcomes = table.get("n"), table.get("rule"), table.get("outcomes")
    if not isinstance(n, int) or n <= 0 or not rule or not outcomes:
        return Result(gate, BLOCKED, "verdict table incomplete")
    stray = sorted({o for _, _, o in rule} - set(outcomes))
    if stray:
        return Result(gate, FAIL, "the table emits an outcome it does not register: %s" % ", ".join(stray))
    hits = set()
    for count in range(n + 1):
        got = [o for lo, hi, o in rule if lo <= count <= hi]
        if len(got) != 1:
            return Result(gate, FAIL, "count %d maps to %d outcomes: the table is not total and single-valued"
                          % (count, len(got)))
        hits.add(got[0])
    unreachable = [o for o in outcomes if o not in hits]
    if unreachable:
        return Result(gate, FAIL, "the ruler cannot emit %s" % ", ".join(unreachable))
    return Result(gate, PASS)


def attainability(table, known_answers, floor=stats.POWER_FLOOR):
    """Each answer expected from a known case must come out with probability >= floor."""
    gate = "G1.attainability"
    if not isinstance(known_answers, dict) or len(known_answers) < 2:
        return Result(gate, BLOCKED, "register at least two known answers (a yes and a no), each with its per-unit rate")
    low = []
    for outcome, rate in sorted(known_answers.items()):
        if outcome not in table["outcomes"] or isinstance(rate, bool) or not isinstance(rate, (int, float)) \
                or not 0 <= rate <= 1:
            return Result(gate, BLOCKED, "known answer %s needs a registered outcome and a rate in [0, 1]" % outcome)
        p = stats.outcome_probability(table, rate).get(outcome, 0.0)
        if p < floor:
            low.append("%s at rate %.3g comes out with probability %.3f" % (outcome, rate, p))
    if low:
        return Result(gate, BLOCKED, "; ".join(low) + "; the floor is %.2f" % floor)
    return Result(gate, PASS)


def check_cell(cell):
    """May this cell run? Every problem is reported; the verdict is the worst of them."""
    gate, found = "G1.cell", []
    missing = [k for k in REQUIRED if cell.get(k) in (None, "", [], {})]
    if not isinstance(cell.get("design_seeds"), list):
        missing.append("design_seeds")
    if missing:
        found.append(Result("fields", BLOCKED, "missing: %s" % ", ".join(missing)))
    exposure = cell.get("exposure")
    if exposure not in (None, "", [], {}) and not (
            isinstance(exposure, dict) and isinstance(exposure.get("tuning_evaluations"), int)
            and not isinstance(exposure["tuning_evaluations"], bool) and exposure["tuning_evaluations"] >= 0):
        found.append(Result("exposure", BLOCKED, "exposure must record tuning_evaluations as a count"))
    seeds, design = cell.get("registered_seeds") or [], cell.get("design_seeds") or []
    if len(set(seeds)) != len(seeds):
        found.append(Result("seeds", FAIL, "registered seeds repeat: the units are not independent"))
    shared = sorted(set(design) & set(seeds))
    if shared:
        found.append(Result("seeds", FAIL, "seeds used in design runs are registered for confirmation: %s" % shared[:5]))
    table = cell.get("verdict_table")
    if isinstance(table, dict):
        t = check_verdict_table(table)
        found.append(t)
        if t.verdict == PASS:
            if seeds and table["n"] != len(seeds):
                found.append(Result("units", FAIL, "the table counts %d units and %d seeds are registered"
                                    % (table["n"], len(seeds))))
            if cell.get("known_answers") not in (None, "", [], {}):
                found.append(attainability(table, cell["known_answers"]))
    out = combine(gate, found or [Result("fields", BLOCKED, "empty cell")])
    return Result(gate, out.verdict, out.reason)


def sha(source):
    return hashlib.sha256(source.replace(b"\r\n", b"\n")).hexdigest()


def check_receipt(cell, receipt, source=None):
    """Does this receipt belong to this registration?

    source is the code on hand, as bytes. The gate hashes it itself: a hash a receipt reports about
    its own code is a statement, and is checked against the code.
    """
    gate = "G1.receipt"
    missing = [k for k in ("source_sha256", "seeds", "ran_at") if receipt.get(k) in (None, "", [])]
    if missing:
        return Result(gate, BLOCKED, "receipt lacks: %s" % ", ".join(missing))
    if source is None:
        return Result(gate, BLOCKED, "the code the receipt names is not on hand: its hash cannot be checked")
    found = []
    if sha(source) != cell["source_sha256"]:
        found.append(Result("code", FAIL, "the code on hand is not the registered code"))
    if receipt["source_sha256"] != cell["source_sha256"]:
        found.append(Result("code", FAIL, "the receipt was produced by code other than the registered code"))
    if len(set(receipt["seeds"])) != len(receipt["seeds"]) or sorted(receipt["seeds"]) != sorted(cell["registered_seeds"]):
        found.append(Result("seeds", FAIL, "the receipt's seeds are not the registered seeds, each once"))
    if receipt["ran_at"] < cell["registered_at"]:
        found.append(Result("clock", FAIL, "the run is earlier than its registration"))
    elif receipt["ran_at"] == cell["registered_at"]:
        found.append(Result("clock", INDETERMINATE, "the clock cannot order the run and its registration"))
    out = combine(gate, found or [Result("all", PASS)])
    return Result(gate, out.verdict, out.reason)
