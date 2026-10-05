"""C-004-T030 S3: run the ten committed semantic edits with rso/slice001/mutation.py, charging every child.

    python -B rso/slice001/challenge/S3/attack_set/run_mutation.py --ledger rso/slice001/s2/LEDGER.jsonl

Attack tooling (Pallas); no file of the frozen implementation is changed. mutation.run() does not charge the
slice ledger (T019 receipt; packet notes), so this driver wraps mutation._run_child IN MEMORY: every child
(baselines included) gets its own MUTATION_CHILD ledger row, charged its WALL seconds (>= its CPU for a
single-threaded child; a timeout is charged the timeout). The driver itself is one TOP_LEVEL launch.

Phase 1 (targeted): edits_A.json against SUITE_A, edits_B.json against SUITE_B (the test modules that exercise
            the edited modules; a full-suite child costs about 7 CPU-minutes and the caps do not allow ten).
Phase 2 (confirmation): each edit that SURVIVED phase 1 is run once more against the FULL frozen suite, in edit
            order, while the S3 CPU budget allows; the unchanged full suite is the ci launch made before this
            driver. A phase-1 survivor not confirmed here is reported as "survived the targeted suite only".

Rows: ../mutation_rows_A.jsonl, ../mutation_rows_B.jsonl (the runner's own rows files) and
../mutation_confirm.jsonl (this driver's rows for phase 2). None is ever overwritten.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
S3_DIR = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.dont_write_bytecode = True

from rso.slice001 import ledger as L                       # noqa: E402
from rso.slice001 import mutation as M                     # noqa: E402

T = "rso.slice001.tests."
SUITE_A = [T + "test_reset_observer", T + "test_encoding", T + "test_stages_world"]
SUITE_B = [T + "test_evidence", T + "test_checker_render", T + "test_stages_evidence", T + "test_receipt"]
FULL = [T + n for n in ("test_adapter", "test_checker_render", "test_ci", "test_encoding", "test_evidence",
                        "test_ledger", "test_matrix_engine", "test_mutation", "test_receipt",
                        "test_reset_observer", "test_rulers", "test_s2_bundle", "test_s2_run",
                        "test_stages_evidence", "test_stages_world", "test_world")]
S3_BUDGET_S = 40 * 60          # CPU seconds this reviewer allows S3 in total (S4 needs the rest of the cap)
FULL_CHILD_ESTIMATE_S = 8 * 60


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def s3_used(led):
    """CPU seconds already charged to S3 rows (run ids starting 'S3-')."""
    return sum((r["cpu_s"] or 0.0) for r in led._runs(led._read()).values() if r["run_id"].startswith("S3-"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--skip-confirm", action="store_true")
    a = ap.parse_args(argv)
    led = L.Ledger.from_contract(a.ledger)
    run_id = "S3-MUTATION-%s-%d" % (utc().replace(":", "").replace("-", ""), os.getpid())
    top = led.begin(run_id, "S3-MUTATION", L.TOP_LEVEL, supplied_by="pallas S3 run_mutation.py")
    c0 = time.process_time()
    state = {"n": 0, "label": "?"}
    original = M._run_child

    def charged(job, timeout_s):
        state["n"] += 1
        rid = "%s/child-%03d" % (run_id, state["n"])
        att = led.begin(rid, "S3-MUTATION-CHILD:%s" % state["label"], L.MUTATION_CHILD,
                        supplied_by="pallas S3 run_mutation.py")
        try:
            res, wall = original(job, timeout_s)
        except BaseException:
            att.finish("FAILED", cpu_s=0.0)
            raise
        timed_out = res.get("phase") == "timeout"
        att.finish("FAILED" if timed_out else "COMPLETED", cpu_s=float(timeout_s if timed_out else wall))
        return res, wall

    M._run_child = charged
    report = {"run_id": run_id, "phases": []}
    ok = False
    try:
        survivors = []
        for label, edits, suite, rows, timeout_s, cap in (
                ("A", "edits_A.json", SUITE_A, "mutation_rows_A.jsonl", 900, 1500),
                ("B", "edits_B.json", SUITE_B, "mutation_rows_B.jsonl", 300, 600)):
            state["label"] = label
            path = os.path.join(HERE, edits)
            out = M.run(path, ROOT, suite, os.path.join(S3_DIR, rows), timeout_s=timeout_s,
                        require_committed=True, max_child_seconds=cap)
            report["phases"].append({"phase": label, "suite": suite, "baseline": out["baseline"],
                                     "summary": out["summary"]})
            all_edits, _ = M.load_edits(path)
            by_id = {e["edit_id"]: e for e in all_edits}
            for r in M.load_rows(out["rows_path"]):
                if r.get("row") == "edit" and r["status"] == "SURVIVED":
                    survivors.append(by_id[r["edit_id"]])

        confirm = []
        if survivors and not a.skip_confirm:
            cpath = os.path.join(S3_DIR, "mutation_confirm.jsonl")
            with open(cpath, "x", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps({"row": "header", "suite": FULL, "started_at_utc": utc(),
                                    "note": "phase-1 survivors against the full frozen suite; the unchanged "
                                            "full suite is the ci launch made before this driver"},
                                   sort_keys=True) + "\n")
                for e in survivors:
                    row = {"row": "confirm", "edit_id": e["edit_id"]}
                    used = s3_used(led)
                    if used + FULL_CHILD_ESTIMATE_S > S3_BUDGET_S:
                        row.update({"status": "NOT_RUN_BUDGET", "s3_cpu_used_s": round(used, 1)})
                    else:
                        with open(os.path.join(ROOT, e["path"]), "rb") as sf:
                            source = sf.read().decode("utf-8")
                        edited = M.apply_edit(source, e)
                        state["label"] = "CONFIRM:" + e["edit_id"]
                        job = {"sys_path": [ROOT], "module": e["module"], "source": edited,
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
    report["s3_cpu_used_s"] = round(s3_used(led), 1)
    report["ledger_usage"] = led.usage()
    print(json.dumps(report, sort_keys=True, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
