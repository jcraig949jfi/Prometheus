"""C-009-T030 CC3: run the five committed semantic edits with rso/slice001/mutation.py (one ledgered launch on the
C-009 ledger; every child a MUTATION_CHILD row parented to it).

    python -B rso/binding/challenge/B1/run_mutation.py --ledger rso/binding/LEDGER.jsonl --contract rso/binding/contract.json

As the S3/S4/R2 drivers: mutation._run_child is wrapped in memory so every child is a MUTATION_CHILD ledger row
charged its wall seconds (the child's own CPU is not visible to the parent; wall is the conservative charge).
Targeted suite: the binding unit tests and the slice test modules of evidence.py and of the modules T010/T011
touched (names from FREEZE_B1.md). A survivor is then run against the FULL frozen suite (both acceptance suites)
while this packet's CPU allowance permits. Rows: mutation_rows.jsonl (the runner's) and mutation_confirm.jsonl.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.dont_write_bytecode = True

from rso.slice001 import ledger as L                       # noqa: E402
from rso.slice001 import mutation as M                     # noqa: E402

T = "rso.slice001.tests."
B = "rso.binding.tests.test_binding"
SUITE = [B, T + "test_evidence", T + "test_checker_render", T + "test_stages_evidence", T + "test_ledger"]
FULL = [B] + [T + n for n in ("test_adapter", "test_checker_render", "test_ci", "test_encoding", "test_evidence",
                              "test_ledger", "test_matrix_engine", "test_mutation", "test_receipt",
                              "test_reset_observer", "test_rulers", "test_s2_bundle", "test_s2_run",
                              "test_stages_evidence", "test_stages_world", "test_world")]
B1_BUDGET_S = 30 * 60              # this packet's allowance inside the C-009 90 CPU-minute cap
FULL_CHILD_ESTIMATE_S = 6 * 60


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def b1_used(led):
    return sum((r["cpu_s"] or 0.0) for r in led._runs(led._read()).values() if r["run_id"].startswith("B1-"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--contract", default=L.DEFAULT_CONTRACT)
    a = ap.parse_args(argv)
    led = L.Ledger.from_contract(a.ledger, a.contract)
    run_id = "B1-MUTATION-%s-%d" % (utc().replace(":", "").replace("-", ""), os.getpid())
    top = led.begin(run_id, "B1-MUTATION", L.TOP_LEVEL, supplied_by="pallas C-009-T030 run_mutation.py")
    c0 = time.process_time()
    state = {"n": 0, "label": "targeted"}
    original = M._run_child

    def charged(job, timeout_s):
        state["n"] += 1
        att = led.begin("%s/child-%03d" % (run_id, state["n"]), "B1-MUTATION-CHILD:%s" % state["label"],
                        L.MUTATION_CHILD, supplied_by="pallas C-009-T030 run_mutation.py", parent_run_id=run_id)
        try:
            res, wall = original(job, timeout_s)
        except BaseException:
            att.finish("FAILED", cpu_s=0.0)
            raise
        timed_out = res.get("phase") == "timeout"
        att.finish("FAILED" if timed_out else "COMPLETED", cpu_s=float(timeout_s if timed_out else wall))
        return res, wall

    M._run_child = charged
    report, ok = {"run_id": run_id}, False
    try:
        path = os.path.join(HERE, "edits.json")
        out = M.run(path, ROOT, SUITE, os.path.join(HERE, "mutation_rows.jsonl"), timeout_s=900,
                    require_committed=True, max_child_seconds=B1_BUDGET_S)
        report["targeted"] = {"suite": SUITE, "baseline": out["baseline"], "summary": out["summary"]}
        edits, _ = M.load_edits(path)
        by_id = {e["edit_id"]: e for e in edits}
        survivors = [by_id[r["edit_id"]] for r in M.load_rows(out["rows_path"])
                     if r.get("row") == "edit" and r["status"] == "SURVIVED"]
        confirm = []
        if survivors:
            with open(os.path.join(HERE, "mutation_confirm.jsonl"), "x", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps({"row": "header", "suite": FULL, "started_at_utc": utc()}, sort_keys=True) + "\n")
                for e in survivors:
                    row = {"row": "confirm", "edit_id": e["edit_id"]}
                    used = b1_used(led)
                    if used + FULL_CHILD_ESTIMATE_S > B1_BUDGET_S:
                        row.update({"status": "NOT_RUN_BUDGET", "b1_cpu_used_s": round(used, 1)})
                    else:
                        with open(os.path.join(ROOT, e["path"]), "rb") as sf:
                            source = sf.read().decode("utf-8")
                        state["label"] = "CONFIRM:" + e["edit_id"]
                        job = {"sys_path": [ROOT], "module": e["module"], "source": M.apply_edit(source, e),
                               "filename": os.path.join(ROOT, e["path"]), "suite": FULL, "witness": [],
                               "mark": M._MARK}
                        res, wall = M._run_child(job, 1200)
                        row.update({"status": M._classify(res), "tests_run": res.get("tests_run"),
                                    "failures": res.get("failures"), "errors": res.get("errors"),
                                    "detail": res.get("detail"), "wall_seconds": round(wall, 3)})
                    confirm.append(row)
                    f.write(json.dumps(row, sort_keys=True) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
                f.write(json.dumps({"row": "terminal", "confirm_rows": len(confirm), "ended_at_utc": utc()},
                                   sort_keys=True) + "\n")
        report["confirm"] = confirm
        ok = True
    except L.CapExhausted as e:
        report["cap_exhausted"] = str(e)
    finally:
        M._run_child = original
        top.finish("COMPLETED" if ok else "FAILED", cpu_s=time.process_time() - c0)
    report["b1_cpu_used_s"] = round(b1_used(led), 1)
    report["ledger_usage"] = led.usage()
    print(json.dumps(report, sort_keys=True, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
