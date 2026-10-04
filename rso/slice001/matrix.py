"""S2 acceptance matrix: implementation verdicts against the independent expected-answer table (C-004-T020).

The comparison target is rso/slice001/expected/EXPECTED_ANSWERS.json (Pallas, T005; CONTRACT.md R4). This module
only COMPARES. It never decides which side is wrong: every mismatch leaves here UNCLASSIFIED, with the
disagreement-register items (ops/campaigns/C-004/DISAGREEMENTS.md) that already name its case, and the coordinator
classifies it as IMPLEMENTATION, CONTRACT or TABLE defect with evidence.

Rules (each one is a test in tests/test_matrix.py):
- A field the table marks UNDETERMINED, or does not state, is NOT_COMPARED, never MATCH.
- An implementation that answers UNDETERMINED where the table determines the value is a MISMATCH (otherwise
  "UNDETERMINED everywhere" would compare as nothing and pass).
- A reason containing <placeholders> is compared as a pattern: the literal text must match, a placeholder matches
  any non-empty text. "UNDETERMINED among A | B" matches either alternative and is reported as such.
- A registered case with no implementation row is MISSING. MISSING is a failure, never a pass.
- An implementation row for an unregistered case is EXTRA (reported; it cannot hide a MISSING one).
- Reasons are compared only for FAIL outcomes: the contract registers FAIL reason forms (draft A A5, V4) and no
  PASS or ruler reason forms, so those texts are NOT_APPLICABLE (register X17). NOT_APPLICABLE is a rule of the
  contract and does not downgrade agreement; NOT_COMPARED (the table could not decide) does.
- Cases whose contract entry has exit_criterion false (E06) are compared and reported but never gate.
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXPECTED = REPO / "rso" / "slice001" / "expected" / "EXPECTED_ANSWERS.json"
CONTRACT = REPO / "rso" / "slice001" / "contract" / "contract.json"

MATCH, MISMATCH, NOT_COMPARED, NOT_APPLICABLE = "MATCH", "MISMATCH", "NOT_COMPARED", "NOT_APPLICABLE"
AGREE, DISAGREE, PARTIAL, MISSING, EXTRA = "AGREE", "DISAGREE", "PARTIAL", "MISSING", "EXTRA"
VERDICT_FIELDS = ("execution", "authority", "outcome")
COUNT_FIELDS = ("statistic", "successes", "trials", "eligible_count", "applicable_count")
CLAIM_FIELDS = ("eligibility", "standing")

# Register items that name a case directly (DISAGREEMENTS.md X01-X16). General items (X10-X14, X16) are attached
# by the coordinator when a mismatch touches them; they are listed so a report can cite them.
REGISTER = {
    "T02.CLOCKED": ["X01"], "E02.RELABEL": ["X02"], "E03.REANCHOR": ["X03"], "E06.LOSSY": ["X04"],
    "T02.AMNESIAC": ["X05"], "E02.MISSING": ["X06"], "E04.W_RESTART": ["X07"], "E04.W_UNRELATED": ["X08"],
    "T06.PKTD_NOQ": ["X09"], "T06.HCOUNT": ["X09", "X15"],
}
GENERAL_REGISTER = ("X10", "X11", "X12", "X13", "X14", "X16")

_PLACEHOLDER = re.compile(r"<[^<>]+>")


def _undetermined(v):
    return isinstance(v, str) and v.strip().upper().startswith("UNDETERMINED")


def reason_matches(expected, actual):
    """Pattern match of a reason. Returns (status, note)."""
    if expected is None or expected == "":
        return NOT_COMPARED, "reason not stated in the table"
    if actual is None:
        return MISMATCH, "implementation gave no reason"
    if _undetermined(actual):
        if _undetermined(expected):
            return NOT_COMPARED, "both sides undetermined"
        return MISMATCH, "implementation reports UNDETERMINED where the table determines the reason"
    m = re.match(r"\s*UNDETERMINED among (.+?)(\s*\(G\d+\))?\s*$", expected)
    if m:
        alts = [a.strip() for a in m.group(1).split("|")]
        hit = [a for a in alts if reason_matches(a, actual)[0] == MATCH]
        if hit:
            return NOT_COMPARED, "table undetermined; implementation chose %r" % hit[0]
        return MISMATCH, "implementation reason matches none of the table's alternatives %r" % alts
    if _undetermined(expected):
        return NOT_COMPARED, "table: " + expected
    parts = _PLACEHOLDER.split(expected)
    rx = "^" + "(.+?)".join(re.escape(p) for p in parts) + "$"
    return (MATCH, "") if re.match(rx, actual.strip(), re.DOTALL) else (MISMATCH, "reason differs")


def _cmp(expected, actual):
    if expected is None:
        return NOT_COMPARED, "not stated in the table"
    if _undetermined(expected):
        return NOT_COMPARED, "table: " + str(expected)
    if actual is None:
        return MISMATCH, "implementation did not report it"
    if _undetermined(actual):
        return MISMATCH, "implementation reports UNDETERMINED where the table determines %r" % (expected,)
    return (MATCH, "") if expected == actual else (MISMATCH, "%r != %r" % (expected, actual))


def compare_verdict(exp, act, where):
    """Field-by-field comparison of one verdict (primary or other)."""
    rows = []
    act = act or {}
    for f in VERDICT_FIELDS + COUNT_FIELDS:
        if f in exp:
            st, note = _cmp(exp.get(f), act.get(f))
            rows.append({"where": where, "field": f, "expected": exp.get(f), "actual": act.get(f),
                         "status": st, "note": note})
    if "per_boundary" in exp:
        st, note = _cmp(exp["per_boundary"], act.get("per_boundary"))
        rows.append({"where": where, "field": "per_boundary", "expected": exp["per_boundary"],
                     "actual": act.get("per_boundary"), "status": st, "note": note})
    if exp.get("outcome") == "FAIL":
        st, note = reason_matches(exp.get("reason"), act.get("reason"))
    else:
        st, note = NOT_APPLICABLE, "no registered reason form for a %s outcome (X17)" % exp.get("outcome")
    rows.append({"where": where, "field": "reason", "expected": exp.get("reason"), "actual": act.get("reason"),
                 "status": st, "note": note})
    return rows


def _key(v):
    return (v.get("predicate"), v.get("scope"))


def compare_row(exp, act):
    """Compare one registered case. `act` is the implementation's row in the table's shape, or None."""
    cid = exp["id"]
    if act is None:
        return {"id": cid, "status": MISSING, "fields": [], "register": REGISTER.get(cid, [])}
    fields = compare_verdict(exp["primary"], act.get("primary"), "primary")
    by_key = {_key(v): v for v in act.get("other_verdicts", [])}
    for v in exp.get("other_verdicts", []):
        fields += compare_verdict(v, by_key.get(_key(v)), "other:%s/%s" % _key(v))
    claims = {c["claim"]: c for c in act.get("claims", [])}
    for c in exp.get("claims", []):
        got = claims.get(c["claim"], {})
        for f in CLAIM_FIELDS:
            st, note = _cmp(c.get(f), got.get(f))
            fields.append({"where": "claim:" + c["claim"], "field": f, "expected": c.get(f), "actual": got.get(f),
                           "status": st, "note": note})
    statuses = {f["status"] for f in fields}
    if MISMATCH in statuses:
        status = DISAGREE
    elif MATCH in statuses and NOT_COMPARED in statuses:
        status = PARTIAL
    elif MATCH in statuses:
        status = AGREE
    else:
        status = PARTIAL
    return {"id": cid, "status": status, "fields": fields, "register": REGISTER.get(cid, [])}


def load_expected(path=EXPECTED):
    t = json.loads(Path(path).read_text(encoding="utf-8"))
    return {r["id"]: r for r in t["rows"]}


def exit_flags(path=CONTRACT):
    c = json.loads(Path(path).read_text(encoding="utf-8"))
    return {x["id"]: bool(x.get("exit_criterion", True)) for x in c["cases"]}


def compare(expected, actual, exit_criteria):
    """expected: {id: row}; actual: {id: row}; exit_criteria: {id: bool}. Returns the matrix report."""
    results = [compare_row(expected[cid], actual.get(cid)) for cid in sorted(expected)]
    extra = sorted(set(actual) - set(expected))
    gating = [r for r in results if exit_criteria.get(r["id"], True)]
    unresolved = [r["id"] for r in gating if r["status"] in (DISAGREE, MISSING)]
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    return {"results": results, "extra": extra, "counts": counts, "registered": len(expected),
            "gating": len(gating), "unresolved_gating": unresolved,
            "exit_ok": not unresolved and not extra,
            "classification": {cid: "UNCLASSIFIED" for cid in unresolved}}


def render(report):
    """Plain-ASCII summary for the T020 receipt and the S5 report."""
    out = ["S2 matrix vs independent table: %d registered, %d gating" % (report["registered"], report["gating"]),
           "counts: " + ", ".join("%s %d" % kv for kv in sorted(report["counts"].items())),
           "extra rows: %s" % (", ".join(report["extra"]) or "none"),
           "unresolved gating: %s" % (", ".join(report["unresolved_gating"]) or "none"),
           "exit: %s" % ("OK" if report["exit_ok"] else "NOT OK")]
    for r in report["results"]:
        if r["status"] in (DISAGREE, MISSING):
            out.append("  %-20s %-8s register %s" % (r["id"], r["status"], ",".join(r["register"]) or "-"))
            for f in r["fields"]:
                if f["status"] == MISMATCH:
                    out.append("      %s.%s: expected %r, got %r" % (f["where"], f["field"], f["expected"], f["actual"]))
    return "\n".join(out)
