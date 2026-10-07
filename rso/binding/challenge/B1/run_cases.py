"""C-009-T030 CC3: run the sound / broken cases and the probe against the frozen binding surface (one ledgered
launch on the C-009 ledger).

    python -B rso/binding/challenge/B1/run_cases.py --ledger rso/binding/LEDGER.jsonl --contract rso/binding/contract.json

Consumer-only: the r1 base is the committed rso/binding/R1/G0; nothing is built. Reuses the S3 driver's check
machinery (rso/slice001/challenge/S3/attack_set/run_cases.py: run_checks, emit_case, Rows, decide_case) as the
S4 and R2 drivers did, adding two check types (witness_binding, custody_why_contains). Output: results_cases.jsonl
beside this file (a new file; never overwritten). Expected values are read from expected.json and never written.

    --dry   controls only, no ledger row, no case or probe (an import/dry check of the drivers; disclosed in
            CHALLENGE_SET.md if used)
"""
import argparse
import base64
import hashlib
import importlib
import json
import os
import subprocess
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.dont_write_bytecode = True

from rso.slice001 import checker as C                      # noqa: E402
from rso.slice001 import ledger as L                       # noqa: E402
from rso.slice001 import s2_bundle as SB                   # noqa: E402
from rso.slice001 import s2_run as SR                      # noqa: E402
from rso.slice001.fixtures import evidence_cases as F      # noqa: E402

S3 = importlib.import_module("rso.slice001.challenge.S3.attack_set.run_cases")
CS = importlib.import_module("rso.binding.challenge.B1.cases")

BASES = ("synthetic", "r1")


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load_r1_g0():
    d = os.path.join(ROOT, "rso", "binding", "R1", "G0")

    def j(f):
        with open(os.path.join(d, f), "rb") as fh:
            return json.loads(fh.read())
    tr = {nid: {role: base64.b64decode(s) for role, s in t.items()} for nid, t in j("traces.json")["traces"].items()}
    with open(os.path.join(d, "MANIFEST.json"), "rb") as fh:
        manifest = fh.read()
    return SB.G0(j("receipts.json")["receipts"], tr, j("inventory.json")["rows"], manifest, j("run.json")["run_id"])


def gate_versions_for(base_name, recs):
    """The consumer gates' versions: the committed stage records for the real base; the fixture's for the
    synthetic base (its stage records and store are the fixture's, so the real versions would read
    NO_STAGE_RECORD there)."""
    if base_name == "synthetic":
        return {g: F.gate_code(g) for g in C.GATES}
    return {r["instrument"]: r["version"] for r in recs if r["instrument"] in C.GATES}


def decide(case, gate_versions):
    cons = C.Consumer(case.bundle, case.anchors, case.store, case.config, gate_versions, case.first_check)
    return cons.decide_all(case.claims), cons.custody


SYNTHETIC_NOTE = ("synthetic base: G-RECOMP fails on the fixture traces for every CL-RET claim, baseline included "
                  "(found by the --dry controls check, dry_controls_2026-10-07T034302Z.jsonl), so a claim-level "
                  "check there measures G-RECOMP, not the binding; recorded, not scored. The r1 base (real "
                  "executions) is fully scored.")


def split_unscored(rows, case_id, kind, results, bname):
    """On the synthetic base, claim-type checks are written as unscored check rows and removed from scoring."""
    if bname != "synthetic":
        return results
    keep = []
    for ck, good, actual in results:
        if ck["type"] == "claim":
            rows.write({"row": "check", "id": case_id, "kind": kind, "check": ck, "ok": good, "scored": False,
                        "actual": actual, "note": SYNTHETIC_NOTE})
        else:
            keep.append((ck, good, actual))
    return keep


def run_checks(checks, decisions, custody, refs):
    """S3.run_checks plus witness_binding and custody_why_contains."""
    mine, theirs = [], []
    for ck in checks:
        (mine if ck["type"] in ("witness_binding", "custody_why_contains") else theirs).append(ck)
    out = S3.run_checks(theirs, decisions, custody, refs) if theirs else []
    for ck in mine:
        try:
            if ck["type"] == "witness_binding":
                ln = S3.lines_of(decisions[ck["claim"]]).get(ck["line"])
                w = (ln or {}).get("witness")
                got = w.get("binding") if isinstance(w, dict) else None
                out.append((ck, got == ck["binding"], {"binding": got, "witness": w}))
            else:
                why = list(custody.get("why", []))
                out.append((ck, ck["text"] in why, {"status": custody["status"], "why": why}))
        except Exception as e:
            out.append((ck, False, {"exception": "%s: %s" % (type(e).__name__, e)}))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--contract", default=L.DEFAULT_CONTRACT)
    ap.add_argument("--out", default=os.path.join(HERE, "results_cases.jsonl"))
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    with open(os.path.join(HERE, "expected.json"), "rb") as f:
        raw = f.read()
    expected = json.loads(raw.decode("utf-8"))
    out_path = a.out if not a.dry else os.path.join(HERE, "dry_controls_%s.jsonl" % utc().replace(":", ""))
    rows = S3.Rows(out_path)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, stdout=subprocess.PIPE,
                            universal_newlines=True, timeout=120).stdout.strip()
    stamp = utc()
    run_id = "B1-CASES-%s-%d" % (stamp.replace(":", "").replace("-", ""), os.getpid())
    code = {p: hashlib.sha256(open(os.path.join(ROOT, *p.split("/")), "rb").read().replace(b"\r\n", b"\n"))
            .hexdigest() for p in ("rso/binding/binding.py", "rso/slice001/evidence.py", "rso/slice001/checker.py",
                                   "rso/slice001/receipt.py", "rso/slice001/s2_run.py")}
    rows.write({"row": "header", "schema": "pallas.c009.t030.case_rows.v1", "commit": commit, "dry": a.dry,
                "expected_sha256": hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest(), "run_id": run_id,
                "code_lf_sha256": code, "python": sys.version.split()[0], "started_at_utc": stamp})
    led = att = None
    if not a.dry:
        led = L.Ledger.from_contract(a.ledger, a.contract)
        att = led.begin(run_id, "B1-CASES", L.TOP_LEVEL, supplied_by="pallas C-009-T030 run_cases.py")
    c0 = time.process_time()
    summary = {b: {"sound": [0, 0], "broken": [0, 0], "controls": [0, 0]} for b in BASES}
    by_id = {c["id"]: c for c in expected["cases"]}
    try:
        recs, blobs = SR.stage_records()
        g1 = load_r1_g0()
        for bname in BASES:
            base = None if bname == "synthetic" else F.real_base(g1, stage_records=recs, blobs=blobs)
            gv = gate_versions_for(bname, recs)
            refs, custs = {}, {}
            refs["BASELINE"], custs["BASELINE"] = decide(F.g0(base), gv)
            refs["KEEPER"], custs["KEEPER"] = decide(F.keeper(base), gv)
            rows.write({"row": "controls", "base": bname, "launch": F._base(base).launch,
                        "inventory_rows": len(refs and F.g0(base).bundle.inventory),
                        "baseline": {k: S3.claim_summary(v) for k, v in sorted(refs["BASELINE"].items())},
                        "baseline_custody": custs["BASELINE"], "keeper_custody": custs["KEEPER"]})
            for ctrl in expected["controls"]:
                res = run_checks(ctrl["checks"], refs[ctrl["bundle"]], custs[ctrl["bundle"]], refs)
                res = split_unscored(rows, "%s@%s" % (ctrl["id"], bname), "control", res, bname)
                ok = S3.emit_case(rows, dict(ctrl, id="%s@%s" % (ctrl["id"], bname)), "control", res)
                summary[bname]["controls"][1] += 1
                summary[bname]["controls"][0] += int(ok)
            if a.dry:
                continue
            for cid, build in list(CS.SOUND.items()) + list(CS.BROKEN.items()):
                case, err, res = by_id[cid], None, []
                try:
                    c = build(base)
                    dec, cust = decide(c, gv)
                    res = run_checks(case["checks"], dec, cust, refs)
                    res = split_unscored(rows, "%s@%s" % (cid, bname), "case", res, bname)
                    rec = {"row": "case_claims", "id": cid, "base": bname, "custody": cust,
                           "claims": {k: S3.claim_summary(v) for k, v in sorted(dec.items())},
                           "g_inv_lines": {k: v for k, v in S3.lines_of(dec["CL-RET(REG)"]).items()
                                           if k.startswith("G-INV")}}
                    if hasattr(c, "hidden"):
                        rec["hidden_sibling"] = c.hidden
                    rows.write(rec)
                except Exception as e:
                    err = "%s: %s" % (type(e).__name__, e)
                    rows.write({"row": "case_error", "id": cid, "base": bname, "error": err,
                                "traceback": traceback.format_exc()})
                ok = S3.emit_case(rows, dict(case, id="%s@%s" % (cid, bname)), "case", res, err)
                summary[bname][case["polarity"]][1] += 1
                summary[bname][case["polarity"]][0] += int(ok)
            if bname == "r1":
                pid = "B1.PROBE.PRODUCTION_RUNJSON"
                row = {"row": "probe", "id": pid, "base": bname, "scored": False}
                try:
                    dec_a, cust_a, rid_a, dec_b, cust_b = CS.probe_production_runjson(g1, recs, blobs,
                                                                                      F.FIRST_CHECK)
                    row["production_path"] = {
                        "bundle_run_id": rid_a, "custody": cust_a,
                        "claims": {k: S3.claim_summary(v) for k, v in sorted(dec_a.items())},
                        "g_inv_CL-RET(REG)": S3.lines_of(dec_a["CL-RET(REG)"]).get("G-INV@CL-RET(REG)")}
                    row["fixture_path"] = {
                        "bundle_run_id": CS.SUBSTITUTE, "custody": cust_b,
                        "claims": {k: S3.claim_summary(v) for k, v in sorted(dec_b.items())},
                        "g_inv_CL-RET(REG)": S3.lines_of(dec_b["CL-RET(REG)"]).get("G-INV@CL-RET(REG)")}
                    row["paths_agree"] = all(C.decision_bytes(dec_a[k]) == C.decision_bytes(dec_b[k]) for k in dec_a)
                except Exception as e:
                    row["error"] = "%s: %s" % (type(e).__name__, e)
                    row["traceback"] = traceback.format_exc()
                rows.write(row)
    finally:
        if att is not None:
            att.finish("COMPLETED", cpu_s=time.process_time() - c0)
    rows.write({"row": "terminal", "summary": {b: {k: {"correct": v[0], "total": v[1]} for k, v in s.items()}
                                               for b, s in summary.items()},
                "ledger_usage": led.usage() if led is not None else None, "cpu_s": round(time.process_time() - c0, 3),
                "ended_at_utc": utc()})
    print(json.dumps({"summary": summary, "out": out_path}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
