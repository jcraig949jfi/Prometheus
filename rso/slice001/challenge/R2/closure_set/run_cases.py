"""C-004-T048 R2: run the closure re-check cases and the two probes against the frozen second-repair code (one
ledgered launch).

    python -B rso/slice001/challenge/R2/closure_set/run_cases.py --ledger rso/slice001/s2/LEDGER.jsonl

Consumer-only: the bundles are the committed s4/G0 and s2/G0; nothing is built. Reuses the S3 driver's check
machinery (challenge/S3/attack_set/run_cases.py: run_checks, emit_case, Rows) as the S4 driver did. Output:
../results_cases.jsonl.
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
R2_DIR = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.dont_write_bytecode = True

from rso.slice001 import checker as C                      # noqa: E402
from rso.slice001 import ledger as L                       # noqa: E402
from rso.slice001 import s2_run as SR                      # noqa: E402
from rso.slice001.fixtures import evidence_cases as F      # noqa: E402

S3 = importlib.import_module("rso.slice001.challenge.S3.attack_set.run_cases")
CS = importlib.import_module("rso.slice001.challenge.R2.closure_set.cases")


def load_bundle(window, name):
    d = os.path.join(ROOT, "rso", "slice001", window, name)

    def j(f):
        with open(os.path.join(d, f), "rb") as fh:
            return json.loads(fh.read())
    import base64
    tr = {nid: {role: base64.b64decode(s) for role, s in t.items()} for nid, t in j("traces.json")["traces"].items()}
    with open(os.path.join(d, "MANIFEST.json"), "rb") as fh:
        manifest = fh.read()
    from rso.slice001 import s2_bundle as SB
    return SB.G0(j("receipts.json")["receipts"], tr, j("inventory.json")["rows"], manifest, j("run.json")["run_id"])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--out", default=os.path.join(R2_DIR, "results_cases.jsonl"))
    a = ap.parse_args(argv)
    with open(os.path.join(HERE, "expected.json"), "rb") as f:
        raw = f.read()
    expected = json.loads(raw.decode("utf-8"))
    rows = S3.Rows(a.out)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, stdout=subprocess.PIPE,
                            universal_newlines=True, timeout=120).stdout.strip()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    run_id = "R2-CASES-%s-%d" % (stamp.replace(":", "").replace("-", ""), os.getpid())
    rows.write({"row": "header", "schema": "pallas.c004.t048.case_rows.v1", "commit": commit,
                "expected_sha256": hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest(), "run_id": run_id,
                "python": sys.version.split()[0], "started_at_utc": stamp})
    led = L.Ledger.from_contract(a.ledger)
    att = led.begin(run_id, "R2-CASES", L.TOP_LEVEL, supplied_by="pallas R2 run_cases.py")
    c0 = time.process_time()
    summary = {"sound": [0, 0], "broken": [0, 0], "controls": [0, 0]}
    by_id = {c["id"]: c for c in expected["cases"]}
    try:
        recs, blobs = SR.stage_records()
        g4, g2 = load_bundle("s4", "G0"), load_bundle("s2", "G0")
        base = F.real_base(g4, stage_records=recs, blobs=blobs)
        refs, custs = {}, {}
        refs["R2_BASELINE"], custs["R2_BASELINE"] = S3.decide_case(F.g0(base), recs)
        refs["R2_KEEPER"], custs["R2_KEEPER"] = S3.decide_case(F.keeper(base), recs)
        for ctrl in expected["controls"]:
            res = S3.run_checks(ctrl["checks"], refs[ctrl["bundle"]], custs[ctrl["bundle"]], refs)
            ok = S3.emit_case(rows, ctrl, "control", res)
            summary["controls"][1] += 1
            summary["controls"][0] += int(ok)
        builders = {
            "R2.SOUND.SUPERSET_MANIFEST": lambda: CS.sound_superset_manifest(base, g2.manifest),
            "R2.BROKEN.LATER_WINDOW_RUN": lambda: CS.broken_later_window_run(base),
        }
        for cid, build in builders.items():
            case, err, res = by_id[cid], None, []
            try:
                dec, cust = S3.decide_case(build(), recs)
                res = S3.run_checks(case["checks"], dec, cust, refs)
                rows.write({"row": "case_claims", "id": cid, "custody": cust,
                            "claims": {k: S3.claim_summary(v) for k, v in sorted(dec.items())}})
            except Exception as e:
                err = "%s: %s" % (type(e).__name__, e)
                rows.write({"row": "case_error", "id": cid, "error": err, "traceback": traceback.format_exc()})
            ok = S3.emit_case(rows, case, "case", res, err)
            summary[case["polarity"]][1] += 1
            summary[case["polarity"]][0] += int(ok)
        probes = {"R2.PROBE.OVERLAP_RUN": lambda: CS.probe_overlap_run(base),
                  "R2.PROBE.FAILED_ROW_CITED": lambda: CS.probe_failed_row_cited(base)}
        for pid, build in probes.items():
            row = {"row": "probe", "id": pid, "scored": False}
            try:
                dec, cust = S3.decide_case(build(), recs)
                row["claims"] = {"CL-RET(REG)": S3.claim_summary(dec["CL-RET(REG)"])}
                row["lines"] = {k: v for k, v in S3.lines_of(dec["CL-RET(REG)"]).items() if k.startswith("G-")}
                row["identical_to_baseline"] = C.decision_bytes(dec["CL-RET(REG)"]) == C.decision_bytes(
                    refs["R2_BASELINE"]["CL-RET(REG)"])
            except Exception as e:
                row["error"] = "%s: %s" % (type(e).__name__, e)
            rows.write(row)
    finally:
        att.finish("COMPLETED", cpu_s=time.process_time() - c0)
    rows.write({"row": "terminal", "summary": {k: {"correct": v[0], "total": v[1]} for k, v in summary.items()},
                "ledger_usage": led.usage(), "ended_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    print(json.dumps({"summary": summary, "out": a.out}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
