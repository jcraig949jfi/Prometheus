"""C-009-T034 CC3 re-check: run the sound / broken cases against FREEZE_B2 (one ledgered launch on the C-009 ledger).

    python -B rso/binding/challenge/B2/run_cases.py --ledger rso/binding/LEDGER.jsonl --contract rso/binding/contract.json

Consumer-only: the r1 base is the committed rso/binding/R1/G0; nothing is built. The B1 driver (rso/binding/
challenge/B1/run_cases.py) is re-used: the S3 check machinery (run_checks, emit_case, Rows, claim_summary,
lines_of) plus B1's witness_binding / custody_why_contains checks and its synthetic-base unscored rule. Output:
results_cases.jsonl beside this file (a new file; never overwritten). Expected values are read from expected.json
and never written.

    --dry          controls only, no ledger row, no case (as B1)
    --check-build  construct every case on both bases and record its inventory shape (row counts, the inserted
                   row); NO consumer call, NO verdict observed, no ledger row. Disclosed in REPORT.md if used.
"""
import argparse
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

from rso.slice001 import ledger as L                       # noqa: E402
from rso.slice001 import s2_run as SR                      # noqa: E402
from rso.slice001.fixtures import evidence_cases as F      # noqa: E402

S3 = importlib.import_module("rso.slice001.challenge.S3.attack_set.run_cases")
B1 = importlib.import_module("rso.binding.challenge.B1.run_cases")
CS = importlib.import_module("rso.binding.challenge.B2.cases")

BASES = ("synthetic", "r1")
SUPPLIED_BY = "pallas C-009-T034 run_cases.py"


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--contract", default=L.DEFAULT_CONTRACT)
    ap.add_argument("--out", default=os.path.join(HERE, "results_cases.jsonl"))
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--check-build", action="store_true")
    a = ap.parse_args(argv)
    with open(os.path.join(HERE, "expected.json"), "rb") as f:
        raw = f.read()
    expected = json.loads(raw.decode("utf-8"))
    stamp = utc()
    if a.check_build:
        out_path = os.path.join(HERE, "check_build_%s.jsonl" % stamp.replace(":", ""))
    elif a.dry:
        out_path = os.path.join(HERE, "dry_controls_%s.jsonl" % stamp.replace(":", ""))
    else:
        out_path = a.out
    rows = S3.Rows(out_path)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, stdout=subprocess.PIPE,
                            universal_newlines=True, timeout=120).stdout.strip()
    run_id = "B2-CASES-%s-%d" % (stamp.replace(":", "").replace("-", ""), os.getpid())
    code = {p: hashlib.sha256(open(os.path.join(ROOT, *p.split("/")), "rb").read().replace(b"\r\n", b"\n"))
            .hexdigest() for p in ("rso/binding/binding.py", "rso/slice001/evidence.py", "rso/slice001/checker.py",
                                   "rso/slice001/receipt.py", "rso/slice001/s2_run.py")}
    rows.write({"row": "header", "schema": "pallas.c009.t034.case_rows.v1", "commit": commit, "dry": a.dry,
                "check_build": a.check_build,
                "expected_sha256": hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest(), "run_id": run_id,
                "code_lf_sha256": code, "python": sys.version.split()[0], "started_at_utc": stamp})
    recs, blobs = SR.stage_records()
    g1 = B1.load_r1_g0()
    if a.check_build:
        for bname in BASES:
            base = None if bname == "synthetic" else F.real_base(g1, stage_records=recs, blobs=blobs)
            for cid, build in list(CS.SOUND.items()) + list(CS.BROKEN.items()):
                try:
                    c = build(base)
                    inv = c.bundle.inventory
                    rec = {"row": "build_check", "id": cid, "base": bname, "inventory_rows": len(inv),
                           "terminal_ok": inv[-1].get("kind") == "TERMINAL" and inv[-1].get("row_count") == len(inv) - 1,
                           "receipts": len(c.bundle.receipts)}
                    for k in ("hidden", "extra_row"):
                        if hasattr(c, k):
                            rec[k] = getattr(c, k)
                    rows.write(rec)
                except Exception as e:
                    rows.write({"row": "build_error", "id": cid, "base": bname,
                                "error": "%s: %s" % (type(e).__name__, e), "traceback": traceback.format_exc()})
        rows.write({"row": "terminal", "check_build": True, "ended_at_utc": utc()})
        print(json.dumps({"check_build": out_path}))
        return 0
    led = att = None
    if not a.dry:
        led = L.Ledger.from_contract(a.ledger, a.contract)
        att = led.begin(run_id, "B2-CASES", L.TOP_LEVEL, supplied_by=SUPPLIED_BY)
    c0 = time.process_time()
    summary = {b: {"sound": [0, 0], "broken": [0, 0], "controls": [0, 0]} for b in BASES}
    by_id = {c["id"]: c for c in expected["cases"]}
    try:
        for bname in BASES:
            base = None if bname == "synthetic" else F.real_base(g1, stage_records=recs, blobs=blobs)
            gv = B1.gate_versions_for(bname, recs)
            refs, custs = {}, {}
            refs["BASELINE"], custs["BASELINE"] = B1.decide(F.g0(base), gv)
            refs["KEEPER"], custs["KEEPER"] = B1.decide(F.keeper(base), gv)
            rows.write({"row": "controls", "base": bname, "launch": F._base(base).launch,
                        "inventory_rows": len(F.g0(base).bundle.inventory),
                        "baseline": {k: S3.claim_summary(v) for k, v in sorted(refs["BASELINE"].items())},
                        "baseline_custody": custs["BASELINE"], "keeper_custody": custs["KEEPER"]})
            for ctrl in expected["controls"]:
                res = B1.run_checks(ctrl["checks"], refs[ctrl["bundle"]], custs[ctrl["bundle"]], refs)
                res = B1.split_unscored(rows, "%s@%s" % (ctrl["id"], bname), "control", res, bname)
                ok = S3.emit_case(rows, dict(ctrl, id="%s@%s" % (ctrl["id"], bname)), "control", res)
                summary[bname]["controls"][1] += 1
                summary[bname]["controls"][0] += int(ok)
            if a.dry:
                continue
            for cid, build in list(CS.SOUND.items()) + list(CS.BROKEN.items()):
                case, err, res = by_id[cid], None, []
                try:
                    c = build(base)
                    dec, cust = B1.decide(c, gv)
                    res = B1.run_checks(case["checks"], dec, cust, refs)
                    res = B1.split_unscored(rows, "%s@%s" % (cid, bname), "case", res, bname)
                    rec = {"row": "case_claims", "id": cid, "base": bname, "custody": cust,
                           "claims": {k: S3.claim_summary(v) for k, v in sorted(dec.items())},
                           "g_inv_lines": {k: v for k, v in S3.lines_of(dec["CL-RET(REG)"]).items()
                                           if k.startswith("G-INV")}}
                    for k in ("hidden", "extra_row"):
                        if hasattr(c, k):
                            rec[k] = getattr(c, k)
                    rows.write(rec)
                except Exception as e:
                    err = "%s: %s" % (type(e).__name__, e)
                    rows.write({"row": "case_error", "id": cid, "base": bname, "error": err,
                                "traceback": traceback.format_exc()})
                ok = S3.emit_case(rows, dict(case, id="%s@%s" % (cid, bname)), "case", res, err)
                summary[bname][case["polarity"]][1] += 1
                summary[bname][case["polarity"]][0] += int(ok)
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
