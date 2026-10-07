"""AUTHOR_TESTED stage records and fire tests: CALIBRATION, RETENTION, G-BIND, G-INV, G-RECOMP (C-004-T023B).

Draft B B4.1/B4.3 and rso-builder 2.4: every instrument version carries a stage record whose fire test names at
least one case the instrument must accept and one it must reject with the expected reason, executed at exactly
that version; a ruler's fire test has a known POSITIVE, NEGATIVE and NOT_SHOWN case.

    python -B -m rso.slice001.stages.evidence_plane fire [I ...]      # run the fire tests -> stages/fire/<I>.json
    python -B -m rso.slice001.stages.evidence_plane records <commit> <utc> [I ...]
                                      # stage records citing the fire receipts committed at <commit> -> stages/<I>.json

Fire receipts are deterministic (no clock): the same version reproduces the same bytes, which is how
tests/test_stages_evidence.py checks "fire tests reproduce". Cases come from the contract (draft A A6 runtimes
in fixtures/world_cases.py; draft B B9 bundle edits in fixtures/evidence_cases.py) with expected values stated
here, never read back from the instrument. Nothing is registered with the custody store here (AMENDMENT V8:
Palamedes requests registration from Aporia at T020).

Python >= 3.8, standard library only.
"""
import copy
import hashlib
import json
import os
import sys

from rso.slice001 import adapter as A
from rso.slice001 import checker as C
from rso.slice001 import evidence as EV
from rso.slice001 import receipt as R
from rso.slice001 import reset as RS
from rso.slice001 import rulers as P
from rso.slice001.fixtures import cc1_cases as CC
from rso.slice001.fixtures import evidence_cases as F
from rso.slice001.fixtures import world_cases as WC
from rso.slice001.stages import version as V

FIRE_SCHEMA = "rso.slice001.fire_test.v1"
INSTRUMENTS = ("CALIBRATION", "RETENTION", "G-BIND", "G-INV", "G-RECOMP")
# The id a stage record names (receipt.validate_stage_record; evidence.authority looks up predicate.id).
RECORD_ID = {"CALIBRATION": "P1", "RETENTION": "P2", "G-BIND": "G-BIND", "G-INV": "G-INV", "G-RECOMP": "G-RECOMP"}
# The commit each instrument's version is pinned to (version.py's convention, one commit per version). The rulers
# keep T023A/T023B's pin; the consumer gates are pinned to the C-009-T011 implementation commit (evidence.py on
# rso/binding; before it the C-004-T046 second repair at 78f4d1fdc and the C-004-T042 S4 repair at 22d270fb2),
# whose stage records were regenerated then (B4.1: a new version needs a new record).
GATE_PIN = "dc21c5d73005ddced7070247c5a47e6c5c467ce7"
PIN = {"CALIBRATION": V.PINNED, "RETENTION": V.PINNED, "G-BIND": GATE_PIN, "G-INV": GATE_PIN, "G-RECOMP": GATE_PIN}
STAGES_DIR = os.path.dirname(os.path.abspath(__file__))
FIRE_DIR = os.path.join(STAGES_DIR, "fire")
RECORDED_BY = "Argus[desktop-ruapvai-b08b36ac] under C-004-T023B"
# Who executed and recorded each instrument's CURRENT fire test and record (the rulers' are unchanged since T023B).
RECORDED_BY_OF = {"CALIBRATION": RECORDED_BY, "RETENTION": RECORDED_BY,
                  "G-BIND": "Argus[harry1-20749977] under C-009-T011", "G-INV": "Argus[harry1-20749977] under C-009-T011",
                  "G-RECOMP": "Argus[harry1-20749977] under C-009-T011"}


def fire_path(instrument):
    return "rso/slice001/stages/fire/%s.json" % instrument


def record_path(instrument):
    return "rso/slice001/stages/%s.json" % instrument


# --------------------------------------------------------------------------------------------------------
# Cases: (case_id, ACCEPT|REJECT, expected value, expected reason or None, thunk -> (value, reason))

def _gate_vr(g):
    """(value, reason) of a consumer-gate result; BLOCKED reads as (BLOCKED, first missing)."""
    if g["execution"]["status"] == "BLOCKED":
        return "BLOCKED", g["execution"]["missing"][0]
    o = g["outcome"]
    return o["value"], (o["reason"] if o["value"] == "FAIL" else None)


def _calibration_cases():
    def run(variant):
        o = P.calibration(variant)
        return o["value"], (o["reason"] if o["value"] == "FAIL" else None)
    return [("T02.AMNESIAC/world STANDARD", "ACCEPT", "PASS", None, lambda: run("STANDARD")),
            ("T02.CLOCKED", "REJECT", "FAIL", "no-carry class reaches 1/1 > 1/2 at boundary 1",
             lambda: run("CLOCKED"))]


def _retention_cases():
    def run(make):
        o = P.retention_of_runtime(make)
        return o["value"], o["statistic"]
    # For a ruler the "reason" column carries the exact statistic s (A5 P2).
    return [("T01.REG", "ACCEPT", "POSITIVE", "1/1", lambda: run(WC.REG)),
            ("T02.AMNESIAC", "ACCEPT", "NEGATIVE", "1/2", lambda: run(WC.AMNESIAC)),
            ("T02.FLIP", "REJECT", "NOT_SHOWN", "0/1", lambda: run(WC.FLIP))]


def _bind(case_id, claim_id="CL-RET(REG)"):
    case = F.CASES[case_id]()
    return _gate_vr(EV.g_bind(case.claims[claim_id], case.bundle, case.anchors, case.config))


def _inv(case_fn, claim_id="CL-RET(REG)"):
    case = case_fn()
    return _gate_vr(EV.g_inv(case.claims[claim_id], case.bundle, case.anchors))


def _without_erase_run():
    case = F.g0()
    inv = [r for r in case.bundle.inventory if r.get("node_id") != "rcpt:REG:ERASE:STANDARD"]
    inv[-1] = {"kind": "TERMINAL", "row_count": len(inv) - 1}
    case.bundle.inventory = inv
    return case


def _g_bind_cases():
    return [("E03.G0", "ACCEPT", "PASS", None, lambda: _bind("E03.G0")),
            ("E03.BYTEFLIP", "REJECT", "FAIL", "BYTES_MISMATCH:trace:probe_a", lambda: _bind("E03.BYTEFLIP")),
            ("E03.STRIP", "REJECT", "FAIL",
             "DEPENDENCY_MISMATCH:rcpt:REG:RETENTION:STANDARD->rcpt:WORLD:CALIBRATION:STANDARD",
             lambda: _bind("E03.STRIP")),
            ("E02.MALFORMED", "REJECT", "FAIL", "SCOPE_MALFORMED:boundary", lambda: _bind("E02.MALFORMED")),
            ("S3 probe MEASUREMENT_LIE (T042)", "REJECT", "FAIL", "SCOPE_MALFORMED:measurement",
             lambda: _bind_case(_measurement_lie)),
            ("S4.SOUND.REPRODUCED (T046 C1): two keeper manifests, one node set", "ACCEPT", "PASS", None,
             lambda: _bind_case(_reproduced))]


def _bind_case(case_fn, claim_id="CL-RET(REG)"):
    case = case_fn()
    return _gate_vr(EV.g_bind(case.claims[claim_id], case.bundle, case.anchors, case.config))


def _measurement_lie():
    d = F.g0_dicts()
    d["rcpt:REG:ERASE:STANDARD"]["cell"]["measurement"] = "f" * 64
    return F.Case("MEASUREMENT_LIE", F.make_bundle(d), F.retained(d), EV.FixtureStore(F.stage_rows()), F.claims())


def _reproduced():
    """S4.SOUND.REPRODUCED (T046 C1): the keeper holds an earlier production's manifest of the same 25 node ids
    (registered first) and this bundle's; the anchors are the keeper's AnchorChoice, resolved per bundle."""
    d1, d2 = F.g0_dicts(), F.g0_dicts()
    for x in d1.values():
        x["created_at_utc"] = "2026-10-03T21:00:00Z"
    b2 = F.make_bundle(d2)
    m1, m2 = F.manifest_of(d1), F.manifest_of(d2)
    rows = [F.row("EVIDENCE_MANIFEST", hashlib.sha256(m1).hexdigest(), at="2026-10-03T22:00:00Z",
                  path="fixtures/G0_S2/MANIFEST.json")] + F.keeper_rows(d2, b2)
    store = EV.FixtureStore(rows)
    anchors = EV.anchors_from_keeper(store, {"fixtures/G0_S2/MANIFEST.json": m1, "fixtures/G0/MANIFEST.json": m2})
    return F.Case("REPRODUCED", b2, anchors, store, F.claims())


def _inv_bind(case_fn, claim_id="CL-RET(REG)"):
    """G-INV (value, reason) with the BIND_* reasons beside the slice spelling: "<reason> [BIND_..., ...]"."""
    value, reason, bind = CC.g_inv_of(case_fn(), claim_id)
    return value, (reason if bind is None else "%s [%s]" % (reason, ", ".join(bind)))


def _g_inv_cases():
    """E02 and the C-009 CC1 set (fixtures/cc1_cases.py, synthetic base; C-009-T011). Each CC1 case's expected
    answer is cc1_cases' C-009 answer, stated there, never read back from the instrument."""
    run = F.g0_dicts()["rcpt:REG:PRESERVE:STANDARD"]["execution"]["run_id"]
    out = [("E02.G0", "ACCEPT", "PASS", None, lambda: _inv(F.CASES["E02.G0"])),
           ("E02.MISSING", "REJECT", "FAIL", "RUN_UNREPORTED:%s" % run, lambda: _inv(F.CASES["E02.MISSING"])),
           ("G0 without the REG ERASE run row", "REJECT", "FAIL",
            "RECEIPT_WITHOUT_RUN:rcpt:REG:ERASE:STANDARD [BIND_NO_ROW]", lambda: _inv_bind(_without_erase_run))]
    for cid, build, claim, (value, reason, bind) in CC.CASES:
        want = reason if bind is None else "%s [%s]" % (reason, ", ".join(bind))
        out.append(("CC1 %s" % cid, "ACCEPT" if value == "PASS" else "REJECT", value, want,
                    (lambda b=build, c=claim: _inv_bind(b, c))))
    return out


# G-RECOMP: a real REG bundle (world -> adapter) whose outcomes come from the real predicates (rulers.py,
# reset.py), then the edits the gate must catch.

_REG = {}


def _strip(outcome):
    return {k: v for k, v in outcome.items() if k != "execution"}


def _reg_bundle(edit=None):
    if "runs" not in _REG:
        _REG["runs"] = A.world_runs(WC.REG)
    runs = _REG["runs"]
    commit = "0" * 40
    code = [{"role": "code:rso/slice001/fixtures/world_cases.py", "sha256": "0" * 64, "length": 1,
             "commit": commit}]
    rref = {"path": "fire-test", "blob_sha256": "0" * 64, "commit": commit}

    def ident(s):
        return A.Identity(rref, rref, {"cell_id": "W-S1", "revision": "0" * 64, "physics": s, "world": "STANDARD",
                                       "boundary": "EPISODE_CONTENT_RESET j=1..3", "search": "NONE",
                                       "development": "NONE", "resources": "fire", "exposure": "fire"},
                          {"id": s, "code": code}, code, code,
                          {"base_sha": commit, "branch": "fire", "worktree_path": "fire", "dirty": False}, rref)

    evaluate = {"CALIBRATION": lambda r: P.calibration("STANDARD"), "RETENTION": P.retention_from_runs,
                "ERASE": lambda r: _strip(RS.erase(WC.REG)), "PRESERVE": lambda r: _strip(RS.preserve(WC.REG)),
                "CHANNEL": lambda r: _strip(RS.channel(WC.REG))}
    receipts, traces = {}, {}
    for name in C.RECOMPUTE_SET:
        s = EV.WORLD_SUBJECT if name == "CALIBRATION" else "REG"
        ev, extra = evaluate[name], None
        if edit == "outcome" and name == "RETENTION":
            ev = lambda r: dict(P.retention_from_runs(r), value="NEGATIVE")
        if edit == "layout" and name == "RETENTION":
            extra = {"trace:probe_a": b'{"not":"a trace"}'}
        rc, tr = A.make_receipt(ident(s), name, ev, code, run_id="fire-%s" % name, runs=runs, extra_traces=extra,
                                created_at_utc="2026-10-04T00:00:00Z")
        receipts[rc.node_id], traces[rc.node_id] = rc.canonical_bytes(), tr
    if edit == "bytes":
        n = "rcpt:REG:RETENTION:STANDARD"
        other = A.traces_from_runs({"trace:probe_a": A.world_runs(WC.AMNESIAC)["trace:probe_a"]})
        traces[n] = dict(traces[n], **other)
    return EV.Bundle(receipts, traces, inventory=[])


def _recomp(edit=None):
    return _gate_vr(C.g_recomp(EV.make_claim("CL-RET", subject="REG"), _reg_bundle(edit), None))


def _g_recomp_cases():
    return [("REG real traces, real predicates", "ACCEPT", "PASS", None, lambda: _recomp()),
            ("REG RETENTION outcome edited to NEGATIVE", "REJECT", "FAIL", "OUTCOME_MISMATCH:value",
             lambda: _recomp("outcome")),
            ("REG probe_a bytes swapped for AMNESIAC's", "REJECT", "FAIL", "BYTES_MISMATCH:trace:probe_a",
             lambda: _recomp("bytes")),
            ("REG probe_a bound but outside the layout", "REJECT", "FAIL", "TRACE_SCHEMA:trace:probe_a",
             lambda: _recomp("layout"))]


CASES = {"CALIBRATION": _calibration_cases, "RETENTION": _retention_cases, "G-BIND": _g_bind_cases,
         "G-INV": _g_inv_cases, "G-RECOMP": _g_recomp_cases}


# --------------------------------------------------------------------------------------------------------

def fire_receipt(instrument):
    """Run the instrument's fire cases at its current version; a deterministic receipt dict."""
    version = V.instrument_version(instrument, PIN[instrument])
    rows = []
    for case_id, polarity, want_v, want_r, thunk in CASES[instrument]():
        got_v, got_r = thunk()
        rows.append({"case_id": case_id, "polarity": polarity, "expected_value": want_v,
                     "expected_reason": want_r, "observed_value": got_v, "observed_reason": got_r,
                     "ok": (got_v, got_r) == (want_v, want_r)})
    return {"schema": FIRE_SCHEMA, "instrument": instrument, "version": version,
            "version_hash": EV.predicate_version(version), "cases": rows, "all_ok": all(r["ok"] for r in rows),
            "executed_by": RECORDED_BY_OF[instrument]}


def stage_record(instrument, receipt_bytes, receipt_commit, recorded_at_utc):
    rec = json.loads(receipt_bytes.decode("utf-8"))
    if not rec["all_ok"]:
        raise RuntimeError("fire test of %s did not pass; no stage record" % instrument)
    must_accept = [c["case_id"] for c in rec["cases"] if c["polarity"] == "ACCEPT"]
    must_reject = [{"case_id": c["case_id"], "expected_reason": c["expected_reason"] or c["expected_value"]}
                   for c in rec["cases"] if c["polarity"] == "REJECT"]
    out = {"instrument": RECORD_ID[instrument], "version": rec["version"], "stage": "AUTHOR_TESTED",
           "fire_test": {"must_accept": must_accept, "must_reject": must_reject,
                         "receipt": {"path": fire_path(instrument),
                                     "blob_sha256": __import__("hashlib").sha256(receipt_bytes).hexdigest(),
                                     "commit": receipt_commit}},
           "first_sight": None, "closure": None, "recorded_by": RECORDED_BY_OF[instrument],
           "recorded_at_utc": recorded_at_utc}
    return R.validate_stage_record(out)


def dump(obj):
    """Fire receipts only: stage records cite their file hash, so these bytes stay as they are. Stage records
    are written as receipt.canonical_bytes (C-004-T027)."""
    return (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["fire"]:
        os.makedirs(FIRE_DIR, exist_ok=True)
        ok = True
        for i in (argv[1:] or INSTRUMENTS):
            rec = fire_receipt(i)
            with open(os.path.join(FIRE_DIR, "%s.json" % i), "wb") as f:
                f.write(dump(rec))
            ok &= rec["all_ok"]
            print("%-12s %s %s" % (i, "OK  " if rec["all_ok"] else "FAIL", rec["version_hash"][:12]))
        return 0 if ok else 1
    if argv[:1] == ["records"] and len(argv) >= 3:
        commit, at = argv[1], argv[2]
        for i in (argv[3:] or INSTRUMENTS):
            data = V.committed_blob(fire_path(i), commit)
            with open(os.path.join(STAGES_DIR, "%s.json" % i), "wb") as f:
                f.write(R.canonical_bytes(stage_record(i, data, commit, at)))   # C-004-T027: file == record_blob
            print("%-12s stage record -> %s" % (i, record_path(i)))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
