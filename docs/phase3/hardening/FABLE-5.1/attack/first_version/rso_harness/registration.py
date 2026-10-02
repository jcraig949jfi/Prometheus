"""G1. Registration: a run exists only as a registered cell, and a receipt must belong to its registration."""
from .verdict import BLOCKED, FAIL, PASS, Result

# The registered developmental cell. The first eight are the cell of the hardening design; the rest
# are what a gate needs in order to refuse.
REQUIRED = ("physics", "search", "world", "development", "boundary", "resources", "measurement", "exposure",
            "adapter", "independent_unit", "design_seeds", "registered_seeds", "verdict_table", "power",
            "source_sha256", "registered_at")


def check_verdict_table(table):
    """A verdict table maps every count 0..n to exactly one outcome, and every registered outcome is reachable.

    table = {"n": 24, "rule": [(lo, hi, outcome), ...], "outcomes": ["HOLDS", "FAILS", "INDETERMINATE"]}
    """
    n, rule, outcomes = table.get("n"), table.get("rule"), table.get("outcomes")
    if n is None or not rule or not outcomes:
        return Result("G1.verdict_table", BLOCKED, "verdict table incomplete")
    hits = {}
    for count in range(n + 1):
        got = [o for lo, hi, o in rule if lo <= count <= hi]
        if len(got) != 1:
            return Result("G1.verdict_table", FAIL,
                          "count %d maps to %d outcomes: the table is not total and single-valued" % (count, len(got)))
        hits[got[0]] = hits.get(got[0], 0) + 1
    unreachable = [o for o in outcomes if o not in hits]
    if unreachable:
        return Result("G1.verdict_table", FAIL, "the ruler cannot emit %s" % ", ".join(unreachable))
    return Result("G1.verdict_table", PASS)


def check_cell(cell):
    """May this cell run? Missing fields block. A broken table or a seed shared with design runs fails."""
    missing = [k for k in REQUIRED if cell.get(k) in (None, "", [], {})]
    if missing:
        return Result("G1.cell", BLOCKED, "missing: %s" % ", ".join(missing))
    shared = sorted(set(cell["design_seeds"]) & set(cell["registered_seeds"]))
    if shared:
        return Result("G1.cell", FAIL, "seeds used in design runs are registered for confirmation: %s" % shared[:5])
    table = check_verdict_table(cell["verdict_table"])
    if table.verdict != PASS:
        return Result("G1.cell", table.verdict, table.reason)
    low = sorted(k for k, v in cell["power"].items() if v < 0.99)
    if low:
        return Result("G1.cell", BLOCKED, "registered answers not attainable at 0.99: %s" % ", ".join(low))
    return Result("G1.cell", PASS)


def check_receipt(cell, receipt):
    """Does this receipt belong to this registration? Other code, other seeds or an earlier clock fail."""
    need = ("source_sha256", "seeds", "ran_at")
    missing = [k for k in need if receipt.get(k) in (None, "", [])]
    if missing:
        return Result("G1.receipt", BLOCKED, "receipt lacks: %s" % ", ".join(missing))
    if receipt["source_sha256"] != cell["source_sha256"]:
        return Result("G1.receipt", FAIL, "the receipt was produced by code other than the registered code")
    if sorted(receipt["seeds"]) != sorted(cell["registered_seeds"]):
        return Result("G1.receipt", FAIL, "the receipt's seeds are not the registered seeds")
    if receipt["ran_at"] <= cell["registered_at"]:
        return Result("G1.receipt", FAIL, "the run is not later than its registration")
    return Result("G1.receipt", PASS)
