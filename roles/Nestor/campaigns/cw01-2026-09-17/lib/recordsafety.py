"""Durable campaign records must open for any reader, and must agree with each other.

TWO GATES, BOTH PROMOTED FROM DEFECTS I CREATED.

CW01-D050 - PORTABILITY. CAMPAIGN_STATE.json is how this campaign survives the loss
of a session; requirement XI forbids leaning on Redis to interpret a finished attempt.
So the recovery file has one job: open. My e05 closeout scripts wrote it with
`json.dumps(..., ensure_ascii=False)`, emitting raw UTF-8 instead of escapes. At e04
close it held 0 non-ascii bytes; afterwards 3. On Windows (cp1252),
`json.load(open(path))` raised UnicodeDecodeError. Found by accident when an unrelated
one-liner crashed.

CW01-D051 - AGREEMENT. CAMPAIGN_STATE records a defect tally. D049 was raised when a
HAND-MAINTAINED tally drifted from DEFECTS.jsonl and put a false headline into
PACKAGE.md. I "fixed" it by DERIVING the tally at write time. That fix was
structurally wrong: a derivation performed once holds only until the next append.
`repair_state_encoding.py` appended D050 and the state went stale within minutes -
ledger 51, state 50.

The general lesson, and the reason both of these live here as gates rather than as
rules: a one-shot correction cannot hold an invariant. Twice in one session I repaired
an instance where an enforceable check was needed. This campaign's clearest evidence
is that gates transfer and memos do not - Q10, promoted from D010, caught D019 in
brand new code within the hour.

WHAT IS ACTUALLY ASSERTED (portability)

ASCII-cleanliness: no byte above 127. That is a property of the FILE and guarantees it
decodes under every ascii-superset encoding. What is NOT asserted is that
`open(path)` without an encoding works HERE - that test is platform-dependent, since
the broken file failed on cp1252 but would have opened fine on a UTF-8 host, so a
green result would have meant nothing. Naive readability is a diagnostic, never the
criterion (CW01-D034 family: a condition satisfiable in the absence of the defect).
"""
from __future__ import annotations

import collections
import json
import pathlib


class UnsafeRecord(AssertionError):
    """Raised when a durable record is not portable to an arbitrary reader."""


class TallyDrift(AssertionError):
    """Raised when a recorded tally disagrees with the ledger it summarises."""


# ----------------------------------------------------------------- portability

def scan(path):
    """Measure a record. Missing file yields NOT_VERIFIED, never a pass."""
    p = pathlib.Path(path)
    if not p.exists():
        return {"path": str(p), "outcome": "NOT_VERIFIED", "reason": "file does not exist",
                "non_ascii_bytes": None, "first_offset": None, "naive_readable": None}
    data = p.read_bytes()
    offsets = [i for i, b in enumerate(data) if b > 127]

    naive = None                                   # DIAGNOSTIC ONLY - platform dependent
    try:
        with open(p) as fh:
            fh.read()
        naive = True
    except Exception:                              # noqa: BLE001
        naive = False

    return {"path": str(p), "bytes": len(data),
            "non_ascii_bytes": len(offsets),
            "first_offset": offsets[0] if offsets else None,
            "naive_readable": naive,
            "outcome": "PASS" if not offsets else "FAIL",
            "reason": ("ascii-clean; decodes under any ascii-superset encoding" if not offsets
                       else "%d non-ascii byte(s), first at offset %d; a reader whose default "
                            "encoding is not utf-8 may fail" % (len(offsets), offsets[0]))}


def require_ascii_safe(path):
    """Fail closed rather than commit a record a recovering executor cannot open."""
    v = scan(path)
    if v["outcome"] == "FAIL":
        raise UnsafeRecord("%s: %s" % (v["path"], v["reason"]))
    return v


def check_records(paths):
    """Gate a set of durable records. NOT_VERIFIED is never counted as a pass."""
    checks = [scan(p) for p in paths]
    n_pass = sum(1 for c in checks if c["outcome"] == "PASS")
    n_fail = sum(1 for c in checks if c["outcome"] == "FAIL")
    n_nv = sum(1 for c in checks if c["outcome"] == "NOT_VERIFIED")
    return {"checks": checks, "n_pass": n_pass, "n_fail": n_fail, "n_not_verified": n_nv,
            "safe": n_fail == 0 and n_nv == 0,
            "verdict": ("all records portable" if n_fail == 0 and n_nv == 0 else
                        "UNPORTABLE RECORDS PRESENT" if n_fail else
                        "some records could not be checked")}


# -------------------------------------------------------------------- agreement

def derive_tally(ledger_path):
    """The truth: counts computed from the ledger itself."""
    p = pathlib.Path(ledger_path)
    entries = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    per = collections.Counter(d.get("experiment_id") for d in entries)
    return {"total": len(entries),
            "per_experiment": {str(k).replace("cw01-", ""): v for k, v in sorted(per.items())}}


def check_tally(state_path, ledger_path):
    """A recorded tally must equal what the ledger actually contains, NOW.

    Deriving once is not enough: the next append re-introduces drift (CW01-D051).
    """
    sp, lp = pathlib.Path(state_path), pathlib.Path(ledger_path)
    if not sp.exists() or not lp.exists():
        return {"outcome": "NOT_VERIFIED", "reason": "state or ledger missing",
                "recorded": None, "derived": None}
    truth = derive_tally(lp)
    st = json.loads(sp.read_text(encoding="utf-8"))
    t = st.get("campaign_totals", {})
    rec_total = t.get("defects_logged")
    rec_per = t.get("defects_per_experiment")

    problems = []
    if rec_total != truth["total"]:
        problems.append("defects_logged recorded %s, ledger holds %s" % (rec_total, truth["total"]))
    if rec_per != truth["per_experiment"]:
        problems.append("per-experiment recorded %s, derived %s" % (rec_per, truth["per_experiment"]))

    return {"outcome": "PASS" if not problems else "FAIL",
            "recorded": {"total": rec_total, "per_experiment": rec_per},
            "derived": truth,
            "reason": ("tally agrees with the ledger" if not problems else "; ".join(problems))}


def require_tally_consistent(state_path, ledger_path):
    """Fail closed rather than publish a summary its own source contradicts."""
    v = check_tally(state_path, ledger_path)
    if v["outcome"] == "FAIL":
        raise TallyDrift(v["reason"])
    return v


if __name__ == "__main__":
    import sys
    import tempfile

    ok = True

    def ck(label, cond, detail=""):
        global ok
        ok &= bool(cond)
        print("   %-46s %s %s" % (label, "PASS" if cond else "FAIL", detail))

    tmp = pathlib.Path(tempfile.mkdtemp())

    print("  -- portability gate (CW01-D050) --")
    bad = tmp / "bad.json"
    bad.write_text(json.dumps({"note": "something每 caller"}, ensure_ascii=False),
                   encoding="utf-8")
    v = scan(bad)
    ck("refuses a record with non-ascii bytes", v["outcome"] == "FAIL",
       "%d byte(s) at %s" % (v["non_ascii_bytes"], v["first_offset"]))
    raised = False
    try:
        require_ascii_safe(bad)
    except UnsafeRecord:
        raised = True
    ck("require_ascii_safe fails closed", raised)

    good = tmp / "good.json"
    good.write_text(json.dumps({"note": "something每 caller"}, ensure_ascii=True),
                    encoding="utf-8")
    ck("admits the same content, ascii-escaped", scan(good)["outcome"] == "PASS")
    ck("escaped file round-trips to the same object",
       json.loads(good.read_text(encoding="utf-8")) == json.loads(bad.read_text(encoding="utf-8")))
    ck("missing file is NOT_VERIFIED", scan(tmp / "nope.json")["outcome"] == "NOT_VERIFIED")
    ck("NOT_VERIFIED is not counted as safe", check_records([tmp / "nope.json"])["safe"] is False)

    print("  -- agreement gate (CW01-D051) --")
    led = tmp / "L.jsonl"
    led.write_text("".join(json.dumps({"id": "X%d" % i, "experiment_id": "cw01-e01"}) + "\n"
                           for i in range(3)), encoding="utf-8")

    def mkstate(total, per):
        s = tmp / ("S%s.json" % total)      # parens required: / binds tighter than %
        s.write_text(json.dumps({"campaign_totals": {"defects_logged": total,
                                                     "defects_per_experiment": per}}),
                     encoding="utf-8")
        return s

    drift = mkstate(2, {"e01": 2})          # ledger has 3 - exactly the D051 shape
    v = check_tally(drift, led)
    ck("refuses a drifted tally", v["outcome"] == "FAIL", v["reason"][:52])
    raised = False
    try:
        require_tally_consistent(drift, led)
    except TallyDrift:
        raised = True
    ck("require_tally_consistent fails closed", raised)

    agree = mkstate(3, {"e01": 3})
    ck("admits a consistent tally", check_tally(agree, led)["outcome"] == "PASS")
    ck("missing ledger is NOT_VERIFIED",
       check_tally(agree, tmp / "absent.jsonl")["outcome"] == "NOT_VERIFIED")

    print("  -- live campaign records --")
    base = pathlib.Path(__file__).resolve().parents[1]
    real = check_records([base / "CAMPAIGN_STATE.json", base / "DEFECTS.jsonl"])
    for c in real["checks"]:
        print("   %-46s %s %s" % ("portability: " + pathlib.Path(c["path"]).name,
                                  c["outcome"], "naive_readable=%s" % c["naive_readable"]))
    ck("live records are portable", real["safe"], real["verdict"])
    lt = check_tally(base / "CAMPAIGN_STATE.json", base / "DEFECTS.jsonl")
    print("   %-46s %s %s" % ("agreement: live tally", lt["outcome"], lt["reason"][:60]))

    print("\n   gate proven: %s | live tally: %s" %
          ("yes" if ok else "NO", lt["outcome"]))
    sys.exit(0 if ok else 1)
